#!/usr/bin/env python3
"""
Unit tests for Anode Cover Inspector API
These tests don't require a running API server
"""

import pytest
import json
import sys
import os

# Add backend to path to import app modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

def test_openapi_schema_structure():
    """Test OpenAPI schema structure without requiring API"""
    with open('backend/app.py', 'r') as f:
        content = f.read()
    
    assert 'openapi_url="/api/openapi.json"' in content, "OpenAPI URL should be configured"
    assert 'docs_url="/api/docs"' in content, "Docs URL should be configured"
    
    # Check no false rate limiting claims
    assert '10 requests per minute' not in content.lower(), "Should not claim rate limiting"



def test_test_structure():
    """Test that test files have correct structure"""
    with open('tests/test_api.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    assert 'STANDALONE TEST SCRIPT' in content, "Should be marked as standalone"
    assert 'def test_' not in content, "Should not have test_* functions (use check_*)"
    assert 'def check_' in content, "Should have check_* functions"
    
    with open('tests/test_integration.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    assert 'class TestAPIIntegration' in content, "Should be a pytest class"
    assert 'import pytest' in content, "Should import pytest"

def test_api_response_format():
    """Test API response format in code"""
    with open('backend/app.py', 'r') as f:
        content = f.read()
    
    # Check that the predict endpoint uses OK/NG labels
    assert 'result_status = "OK"' in content, "Should return 'OK' status"
    assert 'result_status = "NG"' in content, "Should return 'NG' status"

def test_requirements_file():
    """Test that requirements.txt exists and has necessary packages"""
    assert os.path.exists('backend/requirements.txt'), "requirements.txt should exist"
    
    with open('backend/requirements.txt', 'r') as f:
        content = f.read()
    
    # Check for essential packages
    assert 'fastapi' in content.lower(), "Should have FastAPI"
    assert 'uvicorn' in content.lower(), "Should have uvicorn"

def test_documentation_files():
    """Test that documentation files exist"""
    assert os.path.exists('README.md'), "README.md should exist"

def test_frontend_structure():
    """Test frontend basic structure"""
    assert os.path.exists('frontend/package.json'), "frontend/package.json should exist"
    assert os.path.exists('frontend/app/layout.tsx'), "frontend app structure should exist"

if __name__ == "__main__":
    # Allow running as standalone script
    pytest.main([__file__, '-v'])
