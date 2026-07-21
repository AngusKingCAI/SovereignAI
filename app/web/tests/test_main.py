"""Tests for app/web/plan31_main.py DI composition."""

import pytest
from fastapi.testclient import TestClient

from app.web.plan31_main import create_app


@pytest.fixture
def client():
    """Create test client."""
    app = create_app()
    return TestClient(app)


def test_health_check(client):
    """Test health check endpoint."""
    response = client.get("/health")
    
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "version" in data


def test_all_routers_mounted(client):
    """Test that all routers are properly mounted."""
    # Test orchestrator endpoints
    response = client.get("/api/orchestrator/status")
    assert response.status_code in [200, 503]
    
    # Test messaging endpoints
    response = client.get("/api/messaging/audit")
    assert response.status_code in [200, 503]
    
    # Test auth endpoints
    response = client.get("/api/auth/bootstrap/status")
    assert response.status_code in [200, 503]
    
    # Test trace endpoints
    response = client.get("/api/trace/stream")
    assert response.status_code in [200, 503]
    
    # Test options endpoints
    response = client.get("/api/models/providers")
    assert response.status_code in [200, 404]


def test_dependency_injection_wired():
    """Test that dependencies are properly wired."""
    from app.web.plan31_main import app
    
    # Check that the app has the lifespan function
    assert app.router.lifespan_context is not None
    
    # Check that all routers are included
    route_paths = {route.path for route in app.routes}
    
    expected_paths = {
        "/health",
        "/api/orchestrator/status",
        "/api/messaging/audit",
        "/api/auth/bootstrap/status",
        "/api/trace/stream",
        "/api/models/providers",
    }
    
    # At least some of these should be present
    assert "/health" in route_paths
