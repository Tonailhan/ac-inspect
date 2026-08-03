# Anode Cover Inspector API

FastAPI-based AI API for visual inspection of anode covers.

## Endpoints

### `GET /api/health`
Health check endpoint for monitoring.

**Response:**
```json
{
  "status": "healthy",
  "model_loaded": true,
  "timestamp": "2025-01-13T12:00:00",
  "version": "1.1.0"
}
```

### `POST /api/predict`
Inspect an uploaded anode cover image.

**Request:**
```json
{
  "image": "data:image/jpeg;base64,/9j/4AAQSkZJRg..."
}
```

**Response:**
```json
{
  "status": "OK",
  "confidence": 0.92,
  "processing_time_ms": 150.5,
  "timestamp": "2026-07-27T12:00:00",
  "model_version": "3.0.0"
}
```

### `GET /api/info`
Get model information.

**Response:**
```json
{
  "status": "success",
  "model_name": "anode_cover_mobilenetv2",
  "model_version": "3.0.0",
  "model_description": "MobileNetV2 transfer learning model...",
  "classes": ["OK", "NG"],
  "input_shape": [224, 224, 3],
  "accuracy": 0.817,
  "field_accuracy": 0.559,
  "field_ng_recall": 0.375,
  "classification_threshold": 0.525
}
```

## API Documentation

FastAPI automatically generates interactive API documentation:

- **Swagger UI**: `/api/docs` - Interactive API documentation
- **ReDoc**: `/api/redoc` - Alternative API documentation

## Local Development

1. **Activate virtual environment:**
   ```bash
   .\venv312\Scripts\activate
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the API:**
   ```bash
   python app.py
   ```
   
   Or use uvicorn directly:
   ```bash
   uvicorn app:app --reload --host 0.0.0.0 --port 5001
   ```

4. **Access the API:**
   - API: http://localhost:5001
   - Docs: http://localhost:5001/api/docs
   - Health: http://localhost:5001/api/health

5. **Test the API:**
   ```bash
   curl http://localhost:5001/api/health
   ```

## Production Deployment

The API can be run with Uvicorn:

```bash
uvicorn app:app --host 0.0.0.0 --port $PORT --workers 4
```

### Environment Variables

- `PORT`: Server port (default: 5001)
- `FASTAPI_DEBUG`: Enable auto-reload debug mode (default: False)

## Features

- Production-ready with Uvicorn
- Comprehensive error handling
- Automatic request/response validation (Pydantic)
- Image size validation (max 10MB)
- Structured logging
- CORS configuration
- Health check endpoint
- Processing time tracking
- Automatic API documentation

## Error Handling

The API returns appropriate HTTP status codes:
- `200`: Success
- `400`: Bad request (invalid input)
- `404`: Endpoint not found
- `500`: Internal server error
- `503`: Service unavailable (model not loaded)

All errors follow the standard format:
```json
{
  "error": "Error message",
  "status": "error"
}
```

## Technology Stack

- **FastAPI**: Modern web framework
- **Uvicorn**: ASGI server
- **Pydantic**: Data validation
- **TensorFlow / Keras**: Model inference (MobileNetV2)
- **Pillow**: Image processing
