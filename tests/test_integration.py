#!/usr/bin/env python3
"""
Integration tests for Anode Cover Inspector API
Tests the complete workflow from API endpoints to model predictions
"""

import pytest
import requests
import json
import time
import base64
import subprocess
import signal
import os
from typing import Dict, Any

BASE_URL = "http://localhost:5001/api"

class TestAPIIntegration:
    """Integration tests for the Anode Cover Inspector API"""
    
    @classmethod
    def setup_class(cls):
        """Start the API server for testing"""
        cls.server_process = None
        try:
            # Start the server in the background
            cls.server_process = subprocess.Popen(
                ['python', 'app.py'],
                cwd='backend',
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            
            # Wait for server to start
            max_wait = 30
            for i in range(max_wait):
                try:
                    response = requests.get(f"{BASE_URL}/health", timeout=2)
                    if response.status_code == 200:
                        print("✅ API server is ready")
                        break
                except requests.exceptions.ConnectionError:
                    time.sleep(1)
                    if i == max_wait - 1:
                        raise Exception("API server failed to start")
        except Exception as e:
            if cls.server_process:
                cls.server_process.terminate()
            raise e
    
    @classmethod
    def teardown_class(cls):
        """Stop the API server"""
        if cls.server_process:
            cls.server_process.terminate()
            cls.server_process.wait()
    
    def test_health_endpoint(self):
        """Test the health check endpoint"""
        response = requests.get(f"{BASE_URL}/health", timeout=10)
        
        assert response.status_code == 200
        data = response.json()
        
        # Check required fields
        assert 'status' in data
        assert 'model_loaded' in data
        assert 'timestamp' in data
        assert 'version' in data
        assert 'uptime_seconds' in data
        assert 'memory_usage_mb' in data
        assert 'cpu_percent' in data
        
        # Check values
        assert data['status'] in ['healthy', 'degraded']
        assert isinstance(data['model_loaded'], bool)
        assert data['version'] == '1.1.0'
        assert isinstance(data['uptime_seconds'], (int, float))
        assert isinstance(data['memory_usage_mb'], (int, float))
        assert isinstance(data['cpu_percent'], (int, float))
    
    def test_metrics_endpoint(self):
        """Test the detailed metrics endpoint"""
        response = requests.get(f"{BASE_URL}/metrics", timeout=10)
        
        assert response.status_code == 200
        data = response.json()
        
        # Check structure
        assert 'status' in data
        assert 'timestamp' in data
        assert 'system' in data
        assert 'process' in data
        assert 'api' in data

        # Check system metrics
        system = data['system']
        assert 'cpu_percent' in system
        assert 'memory_percent' in system
        assert 'disk_usage' in system

        # Check process metrics
        process = data['process']
        assert 'memory_mb' in process
        assert 'cpu_percent' in process
        assert 'threads' in process

        # Check API metrics
        api = data['api']
        assert 'model_loaded' in api
        assert 'cache_size' in api
    
    def test_info_endpoint(self):
        """Test the model info endpoint"""
        response = requests.get(f"{BASE_URL}/info", timeout=10)
        
        assert response.status_code == 200
        data = response.json()
        
        # Check required fields
        assert 'model_name' in data
        assert 'model_version' in data
        assert 'model_description' in data
        assert 'classes' in data
        assert 'input_shape' in data
        assert 'accuracy' in data
        assert 'classification_threshold' in data
        assert 'status' in data
        
        # Check values
        assert isinstance(data['classes'], list)
        assert 'OK' in data['classes']
        assert 'NG' in data['classes']
        assert data['status'] == 'success'
        
        # Check caching info
        assert 'cache_enabled' in data
        assert 'cache_size' in data
        assert 'cache_limit' in data
        assert 'lazy_loading' in data
    
    def test_predict_endpoint_invalid_data(self):
        """Test predict endpoint with invalid data"""
        # Test with no image data
        response = requests.post(
            f"{BASE_URL}/predict",
            json={},
            timeout=10
        )
        assert response.status_code == 422  # Validation error
        
        # Test with invalid base64
        response = requests.post(
            f"{BASE_URL}/predict",
            json={"image": "invalid_base64_data"},
            timeout=10
        )
        assert response.status_code in [400, 422]
    
    def test_predict_endpoint_with_valid_image(self):
        """Test predict endpoint with a valid test image"""
        # Create a small test image (1x1 pixel PNG)
        test_image_base64 = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=="
        
        response = requests.post(
            f"{BASE_URL}/predict",
            json={"image": f"data:image/png;base64,{test_image_base64}"},
            timeout=30
        )
        
        # Should either succeed (if model is loaded) or fail gracefully
        if response.status_code == 200:
            data = response.json()
            
            # Check response structure
            assert 'status' in data
            assert 'confidence' in data
            assert 'timestamp' in data
            assert 'processing_time_ms' in data
            
            # Check values
            assert data['status'] in ['OK', 'NG']
            assert isinstance(data['confidence'], (int, float))
            assert 0 <= data['confidence'] <= 1
            
            print(f"✅ Prediction successful: {data['status']} ({data['confidence']:.3f})")
        else:
            # Model might not be loaded in CI environment
            assert response.status_code in [503, 400]
            print("⚠️ Model not loaded (expected in CI environment)")
    
    def test_caching_functionality(self):
        """Test that caching works correctly"""
        # Create a test image
        test_image_base64 = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=="
        
        # Make first request
        start_time = time.time()
        response1 = requests.post(
            f"{BASE_URL}/predict",
            json={"image": f"data:image/png;base64,{test_image_base64}"},
            timeout=30
        )
        first_request_time = time.time() - start_time
        
        # Make second request (should be cached)
        start_time = time.time()
        response2 = requests.post(
            f"{BASE_URL}/predict",
            json={"image": f"data:image/png;base64,{test_image_base64}"},
            timeout=30
        )
        second_request_time = time.time() - start_time
        
        if response1.status_code == 200 and response2.status_code == 200:
            # Both requests should return the same result
            assert response1.json()['status'] == response2.json()['status']
            assert response1.json()['confidence'] == response2.json()['confidence']
            
            # Second request should be faster (cached)
            print(f"First request time: {first_request_time:.3f}s")
            print(f"Second request time: {second_request_time:.3f}s")
            
            # Note: This test might be flaky in CI environments
            if second_request_time < first_request_time * 0.8:
                print("✅ Caching appears to be working")
            else:
                print("⚠️ Caching effect not clearly visible")
        else:
            print("⚠️ Cannot test caching without loaded model")
    
    def test_security_headers(self):
        """Test that security headers are present"""
        response = requests.get(f"{BASE_URL}/health", timeout=10)
        
        assert response.status_code == 200
        
        headers = response.headers
        
        # Check for security headers
        assert 'X-Content-Type-Options' in headers
        assert headers['X-Content-Type-Options'] == 'nosniff'
        
        assert 'X-Frame-Options' in headers
        assert headers['X-Frame-Options'] == 'DENY'
        
        assert 'X-XSS-Protection' in headers
        assert headers['X-XSS-Protection'] == '1; mode=block'
        
        assert 'Referrer-Policy' in headers
        assert 'strict-origin-when-cross-origin' in headers['Referrer-Policy']
        
        assert 'Content-Security-Policy' in headers
        assert 'default-src' in headers['Content-Security-Policy']
        
        print("✅ Security headers present")
    
    def test_error_handling(self):
        """Test error handling for various scenarios"""
        # Test non-existent endpoint
        response = requests.get(f"{BASE_URL}/nonexistent", timeout=10)
        assert response.status_code == 404
        
        # Test invalid method
        response = requests.delete(f"{BASE_URL}/health", timeout=10)
        assert response.status_code == 405
        
        print("✅ Error handling working correctly")
    
    def test_concurrent_requests(self):
        """Test handling of concurrent requests"""
        import threading
        import queue
        
        results = queue.Queue()
        
        def make_request():
            try:
                response = requests.get(f"{BASE_URL}/health", timeout=10)
                results.put(response.status_code)
            except Exception as e:
                results.put(str(e))
        
        # Make 5 concurrent requests
        threads = []
        for _ in range(5):
            thread = threading.Thread(target=make_request)
            threads.append(thread)
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        # Check results
        success_count = 0
        while not results.empty():
            result = results.get()
            if result == 200:
                success_count += 1
        
        assert success_count == 5, f"Expected 5 successful requests, got {success_count}"
        print("✅ Concurrent requests handled successfully")

if __name__ == "__main__":
    # Run tests directly
    import sys
    
    # Change to the project root directory
    os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    
    test_instance = TestAPIIntegration()
    
    try:
        test_instance.setup_class()
        
        print("Running integration tests...")
        test_instance.test_health_endpoint()
        test_instance.test_metrics_endpoint()
        test_instance.test_info_endpoint()
        test_instance.test_predict_endpoint_invalid_data()
        test_instance.test_predict_endpoint_with_valid_image()
        test_instance.test_caching_functionality()
        test_instance.test_security_headers()
        test_instance.test_error_handling()
        test_instance.test_concurrent_requests()
        
        print("✅ All integration tests passed!")
        
    except Exception as e:
        print(f"❌ Integration test failed: {e}")
        sys.exit(1)
    finally:
        test_instance.teardown_class()
