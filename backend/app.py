"""Anode Cover Inspector API - Universal Inspection Interface

A FastAPI-based AI API for visual inspection and classification tasks.
Provides endpoints for automated image analysis.

Version: 1.1.0
"""

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request as StarletteRequest
from starlette.responses import Response
from pydantic import BaseModel, Field
from typing import Optional
import os
import io
import base64
import logging
from datetime import datetime
import time
import psutil
import asyncio
from typing import Dict, Any
import hashlib

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# ML Imports (for real model)
import numpy as np
from PIL import Image
try:
    from tensorflow.keras.models import load_model
    from tensorflow.keras.preprocessing.image import img_to_array
    TF_AVAILABLE = True
except ImportError:
    TF_AVAILABLE = False
    logger.warning("TensorFlow not available. Real model loading will fail.")

# Toggle between mock and real model
USE_MOCK = False

# Sigmoid threshold optimized on validation set (default 0.5 was too aggressive)
CLASSIFICATION_THRESHOLD = 0.25

# UI enforces a 10MB image limit; base64 adds ~33% overhead, so allow 14MB encoded
MAX_IMAGE_B64_BYTES = 14 * 1024 * 1024


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Add security headers to all responses"""
    
    async def dispatch(self, request: StarletteRequest, call_next):
        response = await call_next(request)
        
        # Don't add CSP for docs endpoints (Swagger UI needs CDN)
        if not request.url.path.startswith("/api/docs") and not request.url.path.startswith("/api/redoc"):
            # Security headers
            response.headers["X-Content-Type-Options"] = "nosniff"
            response.headers["X-Frame-Options"] = "DENY"
            response.headers["X-XSS-Protection"] = "1; mode=block"
            response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
            response.headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=()"
            
            # CSP - Content Security Policy
            csp = (
                "default-src 'self'; "
                "script-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; "
                "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; "
                "font-src 'self' https://fonts.gstatic.com; "
                "img-src 'self' data: https:; "
                "connect-src 'self' http://localhost:3000 http://localhost:5001 http://10.20.112.240:3000 http://10.20.112.240:5001"
            )
            response.headers["Content-Security-Policy"] = csp
        
        return response

# Initialize FastAPI app with metadata
app = FastAPI(
    title="Anode Cover Inspection API",
    description="""## AI-powered Visual Inspection
    
Anode Cover Inspector is an AI-powered API that analyzes images for automated inspection and quality control.
The system is designed for high-performance visual classification tasks.
""",
    version="1.1.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
    openapi_tags=[
        {
            "name": "Health",
            "description": "Health check and system monitoring endpoints"
        },
        {
            "name": "Inspection", 
            "description": "Image analysis and inspection endpoints"
        },
        {
            "name": "Info",
            "description": "Model information and metadata"
        },
        {
            "name": "Monitoring",
            "description": "System metrics and performance monitoring"
        }
    ],
    contact={
        "name": "Anode Cover Inspector",
        "url": "https://github.com/Tonailhan/ac-inspect"
    },
    license_info={
        "name": "MIT License",
        "url": "https://github.com/Tonailhan/ac-inspect/blob/main/LICENSE"
    }
)

# Add security headers middleware
app.add_middleware(SecurityHeadersMiddleware)

# Add CORS middleware. Browsers normally reach this API through the Next.js
# rewrite proxy (same-origin), so wildcard origins without credentials is safe
# for direct LAN access to the docs/API.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"]
)

# Response models
class HealthResponse(BaseModel):
    """Health check response model"""
    status: str = Field(..., example="healthy")
    model_loaded: bool = Field(..., example=True)
    timestamp: str = Field(..., example="2024-01-01T12:00:00.000000")
    version: str = Field(..., example="1.0.0")
    model_version: str = Field(..., example="1.0.0")
    uptime_seconds: float = Field(..., example=3600.5)
    memory_usage_mb: float = Field(..., example=1024.5)
    cpu_percent: float = Field(..., example=25.5)

class PredictRequest(BaseModel):
    """Prediction request model"""
    image: str = Field(..., description="Base64-encoded image data (PNG or JPEG format)")

class PredictResponse(BaseModel):
    """Inspection response model"""
    status: str = Field(..., description="Inspection result: 'OK' or 'NG'", example="OK")
    confidence: float = Field(..., description="Confidence score (0.0 to 1.0)", example=0.92)
    processing_time_ms: float = Field(..., example=150.5)
    timestamp: str = Field(..., example="2024-01-01T12:00:00.000000")
    model_version: str = Field(..., example="mock-1.1.0")

class ModelInfoResponse(BaseModel):
    """Model information response model"""
    status: str = Field(..., example="success")
    model_name: str = Field(..., example="standard_inspection_model")
    model_version: str = Field(..., example="1.1.0")
    model_description: str = Field(..., example="Mock inspection model for development testing")
    input_shape: list = Field(..., example=[224, 224, 3])
    classes: list = Field(..., example=["OK", "NG"])
    training_date: str = Field(..., example="2024-04-01")
    accuracy: float = Field(..., example=0.90)
    classification_threshold: float = Field(..., example=0.50)
    cache_enabled: bool = Field(..., example=True)
    cache_size: int = Field(..., example=0)
    cache_limit: int = Field(..., example=1000)
    lazy_loading: bool = Field(..., example=True)

# Global variables
model = None
model_loaded_time = None
startup_time = time.time()
prediction_cache = {}
CACHE_LIMIT = 1000
MODEL_VERSION = '3.0.0'

def get_model_info_data():
    """Get model information data"""
    return {
        'model_name': 'anode_cover_mobilenetv2',
        'model_version': MODEL_VERSION,
        'model_description': 'MobileNetV2 transfer learning model for anode cover powder level inspection (class-weighted, threshold-optimized)',
        'input_shape': [224, 224, 3],
        'classes': ['OK', 'NG'],
        'training_date': '2026-06-22',
        'accuracy': 0.91,
        'classification_threshold': CLASSIFICATION_THRESHOLD,
        'cache_size': len(prediction_cache),
        'cache_limit': CACHE_LIMIT
    }

def get_cache_key(image_data: str) -> str:
    """Generate cache key from image data"""
    return hashlib.md5(image_data.encode()).hexdigest()

@app.on_event("startup")
async def startup_event():
    """Initialize system on startup"""
    global model, model_loaded_time
    logger.info("Initializing Anode Cover Inspector Inspection API...")
    
    if USE_MOCK:
        model = None
        logger.info("System operational (Running with mock analyzer)")
    else:
        if not TF_AVAILABLE:
            logger.error("Cannot load real model: TensorFlow is not installed.")
            model = None
        else:
            try:
                # Load the newly placed model
                # Try models in order: .keras (new) → .h5 (legacy)
                weights_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'weights')
                model_candidates = [
                    os.path.join(weights_dir, 'anode_mobilenet_v2.keras'),
                    os.path.join(weights_dir, 'anode_mobilenet_v2.h5'),
                    os.path.join(weights_dir, 'anode_classifier_v1.h5'),
                ]
                
                model_path = None
                for candidate in model_candidates:
                    if os.path.exists(candidate):
                        model_path = candidate
                        break
                
                if model_path is None:
                    raise FileNotFoundError(f"No model file found in {weights_dir}")
                
                logger.info(f"Loading model from {model_path}...")
                model = load_model(model_path)
                logger.info(f"Model loaded successfully: {os.path.basename(model_path)}")
            except Exception as e:
                logger.error(f"Failed to load real model: {e}")
                model = None
    
    model_loaded_time = time.time()

def preprocess_image(image_data: str) -> np.ndarray:
    """Preprocess base64 image for model prediction.
    
    IMPORTANT: The MobileNetV2 model has a Rescaling layer baked in that
    converts [0, 255] -> [-1, 1]. So we must NOT normalize here.
    Just resize to 224x224 and pass raw pixel values [0, 255].
    """
    try:
        # Remove data URL prefix if present
        if 'base64,' in image_data:
            image_data = image_data.split('base64,')[1]
        
        # Decode base64
        image_bytes = base64.b64decode(image_data)
        
        # Open image
        image = Image.open(io.BytesIO(image_bytes))
        
        # Convert to RGB if needed
        if image.mode != 'RGB':
            image = image.convert('RGB')
        
        # Resize to model input size
        image = image.resize((224, 224))
        
        # Convert to array — DO NOT normalize (model has built-in Rescaling layer)
        image_array = img_to_array(image)  # Raw pixels [0, 255]
        
        # Add batch dimension
        image_array = np.expand_dims(image_array, axis=0)
        
        return image_array
        
    except Exception as e:
        logger.error(f"Error preprocessing image: {e}")
        raise HTTPException(status_code=400, detail=f"Invalid image data: {str(e)}")

@app.get("/api/health", response_model=HealthResponse, tags=["Health"])
async def health_check():
    """Health check endpoint"""
    process = psutil.Process()

    model_available = USE_MOCK or model is not None
    return HealthResponse(
        status="healthy" if model_available else "degraded",
        model_loaded=model is not None,
        timestamp=datetime.now().isoformat(),
        version="1.1.0",
        model_version=MODEL_VERSION,
        uptime_seconds=time.time() - startup_time,
        memory_usage_mb=process.memory_info().rss / 1024 / 1024,
        cpu_percent=process.cpu_percent()
    )

@app.get("/api/metrics", tags=["Monitoring"])
async def get_metrics():
    """Get system metrics"""
    process = psutil.Process()
    
    return {
        "status": "success",
        "timestamp": datetime.now().isoformat(),
        "system": {
            "cpu_percent": psutil.cpu_percent(),
            "memory_percent": psutil.virtual_memory().percent,
            "disk_usage": psutil.disk_usage('/').percent
        },
        "process": {
            "memory_mb": process.memory_info().rss / 1024 / 1024,
            "cpu_percent": process.cpu_percent(),
            "threads": process.num_threads(),
            "open_files": len(process.open_files())
        },
        "api": {
            "model_loaded": model is not None,
            "cache_size": len(prediction_cache),
            "cache_hits": 0,  # Would need to track this
            "cache_misses": 0  # Would need to track this
        }
    }

@app.post("/api/predict", response_model=PredictResponse, tags=["Inspection"])
async def predict(request: PredictRequest):
    """Analyze image and return inspection results"""
    import random
    start_time = time.time()

    if len(request.image) > MAX_IMAGE_B64_BYTES:
        raise HTTPException(status_code=413, detail="Image too large (max 10MB)")

    if USE_MOCK:
        # --- MOCK IMPLEMENTATION (explicit dev toggle only) ---
        # Mock behavior: randomly returns {"status": "OK", "confidence": 0.92} or {"status": "NG", "confidence": 0.88}
        if random.random() > 0.5:
            result_status = "OK"
            confidence_score = 0.92
        else:
            result_status = "NG"
            confidence_score = 0.88

        logger.info(f"Mock inspection performed. Result: {result_status}")
    elif model is None:
        # Never fabricate results when the real model is unavailable
        raise HTTPException(
            status_code=503,
            detail="Inspection model is not loaded. Check server logs and the weights/ directory."
        )
    else:
        # --- REAL MODEL IMPLEMENTATION ---
        try:
            # Preprocess the image
            img_array = preprocess_image(request.image)

            cache_key = get_cache_key(request.image)
            cached = prediction_cache.get(cache_key)
            if cached is not None:
                result_status, confidence_score = cached
                logger.info(f"Cache hit. Result: {result_status} (Conf: {confidence_score:.2f})")
            else:
                # Run blocking TF inference off the event loop so concurrent
                # requests aren't serialized
                loop = asyncio.get_event_loop()
                prediction = await loop.run_in_executor(None, model.predict, img_array)
                # Keras assigns labels alphabetically: NG=0, OK=1
                # Sigmoid output: higher = more likely OK
                is_ok = prediction[0][0] > CLASSIFICATION_THRESHOLD

                if is_ok:
                    result_status = "OK"
                    confidence_score = float(prediction[0][0])
                else:
                    result_status = "NG"
                    confidence_score = float(1 - prediction[0][0])

                if len(prediction_cache) >= CACHE_LIMIT:
                    prediction_cache.pop(next(iter(prediction_cache)))
                prediction_cache[cache_key] = (result_status, confidence_score)

                logger.info(f"Real inspection performed. Result: {result_status} (Conf: {confidence_score:.2f}, raw={prediction[0][0]:.3f}, threshold={CLASSIFICATION_THRESHOLD})")
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error during prediction: {e}")
            raise HTTPException(status_code=500, detail=f"Prediction error: {str(e)}")

    processing_time = (time.time() - start_time) * 1000
    if USE_MOCK:
        processing_time += 50  # Add artificial delay for mock

    return PredictResponse(
        status=result_status,
        confidence=confidence_score,
        processing_time_ms=processing_time,
        timestamp=datetime.now().isoformat(),
        model_version=f"mock-{MODEL_VERSION}" if USE_MOCK else MODEL_VERSION
    )

@app.get("/api/info", response_model=ModelInfoResponse, tags=["Info"])
async def model_info():
    """Get model information"""
    model_info_data = get_model_info_data()
    
    info = {
        "status": "success",
        "model_name": model_info_data['model_name'],
        "model_version": model_info_data['model_version'],
        "model_description": model_info_data['model_description'],
        "input_shape": model_info_data['input_shape'],
        "classes": model_info_data['classes'],
        "training_date": model_info_data['training_date'],
        "accuracy": model_info_data['accuracy'],
        "classification_threshold": model_info_data.get('classification_threshold', 0.5)
    }
    
    # Add caching information
    info['cache_enabled'] = True
    info['cache_size'] = model_info_data['cache_size']
    info['cache_limit'] = model_info_data['cache_limit']
    info['lazy_loading'] = True
    
    return ModelInfoResponse(**info)

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler"""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
        'error': 'Internal server error',
        'status': 'error'
        }
    )

if __name__ == '__main__':
    import uvicorn
    # Use 5001 instead of 5000 to avoid macOS AirPlay conflict
    port = int(os.environ.get('PORT', 5001))
    debug = os.environ.get('FASTAPI_DEBUG', 'False').lower() == 'true'
    
    logger.info(f"Starting FastAPI application on port {port}")
    logger.info(f"Debug mode: {debug}")
    logger.info(f"Model loaded: {model is not None}")
    
    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=port,
        reload=debug,
        log_level="info"
    )