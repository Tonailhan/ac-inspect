# API Reference

The Anode Cover Inspector backend exposes a robust RESTful API built with FastAPI. All endpoints are accessible relative to the base URL `http://<host>:5001/api`. 

> [!NOTE]
> An interactive OpenAPI (Swagger) documentation page is automatically generated and accessible by visiting `http://localhost:5001/api/docs` while the backend is running.

---

## 1. Predict Image
Performs an AI analysis on a provided image to detect defects.

- **Endpoint**: `/predict`
- **Method**: `POST`
- **Content-Type**: `application/json`

### Request Body
```json
{
  "image": "data:image/jpeg;base64,/9j/4AAQSkZJRgABAQ..." 
}
```
*Note: The `image` string must be a valid base64-encoded image. The `data:image/...;base64,` prefix is optional and will be stripped automatically if present.*

### Success Response
```json
{
  "status": "OK",
  "confidence": 0.923,
  "processing_time_ms": 145.2,
  "timestamp": "2026-06-22T13:26:08.336794",
  "model_version": "real-3.0.0"
}
```
*Status will return either `"OK"` (acceptable powder coverage) or `"NG"` (defect/no good).*

---

## 2. Health Check
Retrieves the system's operational status and basic resource usage. Used by the frontend to display the API connection status.

- **Endpoint**: `/health`
- **Method**: `GET`

### Success Response
```json
{
  "status": "healthy",
  "model_loaded": true,
  "timestamp": "2026-06-22T13:25:08.575157",
  "version": "1.1.0",
  "model_version": "1.1.0",
  "uptime_seconds": 7678.12,
  "memory_usage_mb": 87.58,
  "cpu_percent": 1.2
}
```

---

## 3. Model Information
Returns metadata about the active ML model loaded into memory, including its classification threshold and architecture details.

- **Endpoint**: `/info`
- **Method**: `GET`

### Success Response
```json
{
  "status": "success",
  "model_name": "anode_cover_mobilenetv2",
  "model_version": "3.0.0",
  "model_description": "MobileNetV2 transfer learning model...",
  "input_shape": [224, 224, 3],
  "classes": ["OK", "NG"],
  "training_date": "2026-07-27",
  "accuracy": 0.817,
  "field_accuracy": 0.559,
  "field_ng_recall": 0.375,
  "classification_threshold": 0.525,
  "cache_enabled": true,
  "cache_size": 0,
  "cache_limit": 1000,
  "lazy_loading": true
}
```

> **Reading the accuracy fields.** `accuracy` is held-out test-set accuracy from
> the training run. `field_accuracy` and `field_ng_recall` come from the
> expert validation study on real plant photographs
> (see [expert-validation.md](expert-validation.md)) and are the figures that
> reflect operational performance. Cite the field figures in reports and
> presentations.
>
> `classification_threshold` is specific to the loaded model and must be
> re-derived whenever the weights are replaced.

---

## 4. System Metrics
Provides deep insights into the host machine's hardware usage. Useful for long-term server monitoring.

- **Endpoint**: `/metrics`
- **Method**: `GET`

### Success Response
```json
{
  "status": "success",
  "timestamp": "2026-06-22T13:28:10.000000",
  "system": {
    "cpu_percent": 15.5,
    "memory_percent": 45.2,
    "disk_usage": 60.1
  },
  "process": {
    "memory_mb": 110.5,
    "cpu_percent": 2.1,
    "threads": 12,
    "open_files": 4
  },
  "api": {
    "model_loaded": true,
    "cache_size": 15,
    "cache_hits": 0,
    "cache_misses": 0
  }
}
```
