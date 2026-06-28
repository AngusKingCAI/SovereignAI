"""Tests for first-run registration flow."""
from __future__ import annotations

import pytest
from fastapi.testclient import TestClient
from sovereignai.main import build_container


@pytest.fixture
def client():
    """Create a test client for the FastAPI application."""
    from web.main import app
    
    # Initialize the container in app.state
    container = build_container()
    app.state.container = container
    
    return TestClient(app)


@pytest.fixture
def container(client):
    """Get the container from the app state."""
    return client.app.state.container


def test_no_users_redirects_to_register(client, container):
    """Test that accessing root with no users redirects to register."""
    from sovereignai.shared.auth import AuthMiddleware
    auth = container.retrieve(AuthMiddleware)
    
    # Ensure no users exist
    auth._password_hashes.clear()
    
    # Access root
    response = client.get("/", follow_redirects=False)
    
    assert response.status_code == 307  # Redirect
    assert response.headers["location"] == "/register"


def test_after_register_redirects_to_login(client, container):
    """Test that accessing register after user exists redirects to login."""
    from sovereignai.shared.auth import AuthMiddleware
    auth = container.retrieve(AuthMiddleware)
    
    # Register a user
    auth.register_user("testuser", "password123")
    
    # Try to access register page
    response = client.get("/register", follow_redirects=False)
    
    assert response.status_code == 307  # Redirect
    assert response.headers["location"] == "/login"


def test_static_files_not_redirected(client, container):
    """Test that static files are accessible without auth on first run."""
    from sovereignai.shared.auth import AuthMiddleware
    auth = container.retrieve(AuthMiddleware)
    
    # Ensure no users exist
    auth._password_hashes.clear()
    
    # Access static file
    response = client.get("/static/styles.css")
    
    # Should return 200 (static files are always allowed)
    assert response.status_code == 200


def test_api_returns_401_on_first_run(client, container):
    """Test that API endpoints return 401 on first run (not redirect)."""
    from sovereignai.shared.auth import AuthMiddleware
    auth = container.retrieve(AuthMiddleware)
    
    # Ensure no users exist
    auth._password_hashes.clear()
    
    # Access API endpoint - should raise HTTPException 401
    with pytest.raises(Exception) as exc_info:
        client.get("/api/capabilities")
    
    # Verify it's a 401 error
    assert "401" in str(exc_info.value)


def test_auth_endpoints_allowed_on_first_run(client, container):
    """Test that auth endpoints are accessible on first run."""
    from sovereignai.shared.auth import AuthMiddleware
    auth = container.retrieve(AuthMiddleware)
    
    # Ensure no users exist
    auth._password_hashes.clear()
    
    # Register endpoint should work
    response = client.post("/api/auth/register", json={
        "username": "newuser",
        "password": "password123"
    })
    
    assert response.status_code == 200
    assert response.json() == {"status": "created"}
