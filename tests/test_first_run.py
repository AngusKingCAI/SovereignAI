"""Tests for first-run registration flow."""
from __future__ import annotations

from typing import Any

import pytest
from fastapi.testclient import TestClient

from sovereignai.main import build_container


@pytest.fixture
def client() -> TestClient:
    """Create a test client for the FastAPI application."""
    from web.main import app

    # Initialize the container in app.state
    container = build_container()
    app.state.container = container

    return TestClient(app)


@pytest.fixture
def container(client: TestClient) -> Any:  # type: ignore[misc]
    """Get the container from the app state and clear auth users for fresh test state."""
    container = client.app.state.container  # type: ignore[attr-defined]
    # Clear persisted users to ensure fresh test state
    from sovereignai.shared.auth import AuthMiddleware
    auth = container.retrieve(AuthMiddleware)
    auth._password_hashes.clear()
    auth._salts.clear()
    return container


def test_no_users_redirects_to_register(client: TestClient, container: Any) -> None:
    """Test that accessing root with no users redirects to register."""
    from sovereignai.shared.auth import AuthMiddleware
    auth = container.retrieve(AuthMiddleware)
    # Ensure no users exist
    auth._password_hashes.clear()

    # Access root
    response = client.get("/", follow_redirects=False)

    assert response.status_code == 307  # Redirect
    assert response.headers["location"] == "/register"


def test_after_register_redirects_to_login(client: TestClient, container: Any) -> None:
    """Test that accessing register after user exists redirects to login."""
    from sovereignai.shared.auth import AuthMiddleware
    auth = container.retrieve(AuthMiddleware)
    # Register a user
    auth.register_user("testuser", "password123")

    # Try to access register page
    response = client.get("/register", follow_redirects=False)

    assert response.status_code == 307  # Redirect
    assert response.headers["location"] == "/login"


def test_static_files_not_redirected(client: TestClient, container: Any) -> None:
    """Test that static files are accessible without auth on first run."""
    from sovereignai.shared.auth import AuthMiddleware
    auth = container.retrieve(AuthMiddleware)
    # Ensure no users exist
    auth._password_hashes.clear()

    # Access static file
    response = client.get("/static/styles.css")

    # Should return 200 (static files are always allowed)
    assert response.status_code == 200


def test_api_returns_401_on_first_run(client: TestClient, container: Any) -> None:
    """Test that API endpoints return 401 on first run (not redirect)."""
    from sovereignai.shared.auth import AuthMiddleware
    auth = container.retrieve(AuthMiddleware)
    # Ensure no users exist
    auth._password_hashes.clear()

    # Access API endpoint - should return JSONResponse 401 (not raise exception)
    response = client.get("/api/capabilities")

    # Verify it's a 401 error
    assert response.status_code == 401
    assert "detail" in response.json()


def test_auth_endpoints_allowed_on_first_run(client: TestClient, container: Any) -> None:
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
