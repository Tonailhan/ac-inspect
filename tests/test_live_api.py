#!/usr/bin/env python3
"""Live API integration test - tests all endpoints against running server."""

import requests
import json
import base64
import numpy as np
import io
import time
from PIL import Image

BASE = "http://localhost:5001/api"

def test_health():
    print("=== Health Check ===")
    r = requests.get(f"{BASE}/health", timeout=10)
    assert r.status_code == 200, f"Health check failed: {r.status_code}"
    data = r.json()
    print(f"  status: {data['status']}")
    print(f"  model_loaded: {data['model_loaded']}")
    print(f"  version: {data['version']}")
    assert data["status"] == "healthy"
    assert data["model_loaded"] is True
    print("  PASS")

def test_info():
    print("\n=== Model Info ===")
    r = requests.get(f"{BASE}/info", timeout=10)
    assert r.status_code == 200, f"Info check failed: {r.status_code}"
    data = r.json()
    print(f"  model_name: {data['model_name']}")
    print(f"  model_version: {data['model_version']}")
    print(f"  classes: {data['classes']}")
    print(f"  input_shape: {data['input_shape']}")
    assert data["classes"] == ["OK", "NG"]
    assert data["input_shape"] == [224, 224, 3]
    print("  PASS")

def test_metrics():
    print("\n=== Metrics ===")
    r = requests.get(f"{BASE}/metrics", timeout=10)
    assert r.status_code == 200, f"Metrics failed: {r.status_code}"
    data = r.json()
    print(f"  model_loaded: {data['api']['model_loaded']}")
    assert data["api"]["model_loaded"] is True
    print("  PASS")

def test_predict():
    print("\n=== Prediction (real model) ===")
    # Create a random test image
    test_img = Image.fromarray(
        np.random.randint(0, 256, (300, 300, 3), dtype=np.uint8)
    )
    buf = io.BytesIO()
    test_img.save(buf, format="PNG")
    b64 = base64.b64encode(buf.getvalue()).decode()

    start = time.time()
    r = requests.post(
        f"{BASE}/predict",
        json={"image": f"data:image/png;base64,{b64}"},
        timeout=60,
    )
    elapsed = time.time() - start

    assert r.status_code == 200, f"Predict failed: {r.status_code} - {r.text}"
    data = r.json()
    print(f"  result: {data['status']}")
    print(f"  confidence: {data['confidence']:.4f}")
    print(f"  model_version: {data['model_version']}")
    print(f"  processing_time_ms: {data['processing_time_ms']:.1f}")
    print(f"  total_request_time: {elapsed:.2f}s")

    assert data["status"] in ("OK", "NG")
    assert 0.0 <= data["confidence"] <= 1.0
    assert data["model_version"] == "3.0.0"
    print("  PASS")

def test_security_headers():
    print("\n=== Security Headers ===")
    r = requests.get(f"{BASE}/health", timeout=10)
    required = [
        "X-Content-Type-Options",
        "X-Frame-Options",
        "X-XSS-Protection",
        "Content-Security-Policy",
        "Referrer-Policy",
    ]
    for h in required:
        val = r.headers.get(h)
        assert val is not None, f"Missing header: {h}"
        print(f"  [OK] {h}: {val[:60]}")
    print("  PASS")

def test_error_handling():
    print("\n=== Error Handling ===")
    r = requests.post(f"{BASE}/predict", json={}, timeout=10)
    assert r.status_code == 422, f"Expected 422, got {r.status_code}"
    print(f"  Empty request: {r.status_code} (correct)")

    r = requests.get(f"{BASE}/nonexistent", timeout=10)
    assert r.status_code == 404, f"Expected 404, got {r.status_code}"
    print(f"  Bad endpoint: {r.status_code} (correct)")
    print("  PASS")


if __name__ == "__main__":
    print("=" * 60)
    print("Live API Integration Tests (new .keras model)")
    print("=" * 60)
    print()

    tests = [
        test_health,
        test_info,
        test_metrics,
        test_predict,
        test_security_headers,
        test_error_handling,
    ]

    passed = 0
    failed = 0
    for t in tests:
        try:
            t()
            passed += 1
        except Exception as e:
            print(f"  FAIL: {e}")
            failed += 1

    print()
    print("=" * 60)
    print(f"Results: {passed} passed, {failed} failed out of {len(tests)}")
    if failed == 0:
        print("ALL TESTS PASSED")
    else:
        print("SOME TESTS FAILED")
    print("=" * 60)
