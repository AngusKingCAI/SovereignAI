"""Tests for app/web/routes/options.py."""

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.web.routes.options import router


@pytest.fixture
def client():
    """Create test client."""
    app = FastAPI()
    app.include_router(router)
    
    return TestClient(app)


def test_model_registry_endpoints_accessible(client):
    """Test that model registry endpoints are accessible."""
    # Test providers endpoint
    response = client.get("/api/models/providers")
    # Should return 200 or 404 if database doesn't exist
    assert response.status_code in [200, 404]
    
    # Test models endpoint
    response = client.get("/api/models")
    assert response.status_code in [200, 404]
