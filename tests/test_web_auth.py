"""Tests for web authentication endpoints and middleware."""
from __future__ import annotations

from typing import Any

import pytest
from fastapi.testclient import TestClient

from sovereignai.main import build_container
from sovereignai.shared.auth import AuthMiddleware


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
    auth = container.retrieve(AuthMiddleware)
    auth._password_hashes.clear()
    auth._salts.clear()
    return container


def test_login_success(client: TestClient, container: Any) -> None:
    """Test that valid credentials set a session cookie."""
    auth = container.retrieve(AuthMiddleware)
    # Register a test user
    auth.register_user("testuser", "testpassword123")

    # Login with valid credentials
    response = client.post("/api/auth/login", json={
        "username": "testuser",
        "password": "testpassword123"
    })

    assert response.status_code == 200
    assert response.json() == {"status": "authenticated"}
    assert "session_id" in response.cookies


def test_login_failure(client: TestClient, container: Any) -> None:
    """Test that invalid credentials return 401."""
    auth = container.retrieve(AuthMiddleware)
    # Register a test user
    auth.register_user("testuser", "testpassword123")

    # Login with invalid credentials
    response = client.post("/api/auth/login", json={
        "username": "testuser",
        "password": "wrongpassword"
    })

    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid credentials"


def test_register_first_run(client: TestClient, container: Any) -> None:
    """Test that registration succeeds when no users exist."""
    auth = container.retrieve(AuthMiddleware)
    # Ensure no users exist
    assert len(auth._password_hashes) == 0

    # Register a user
    response = client.post("/api/auth/register", json={
        "username": "newuser",
        "password": "password123"
    })

    assert response.status_code == 200
    assert response.json() == {"status": "created"}
    assert len(auth._password_hashes) == 1


def test_register_after_user_exists(client: TestClient, container: Any) -> None:
    """Test that registration fails when a user already exists."""
    auth = container.retrieve(AuthMiddleware)
    # Register first user
    auth.register_user("firstuser", "password123")

    # Try to register second user
    response = client.post("/api/auth/register", json={
        "username": "seconduser",
        "password": "password123"
    })

    assert response.status_code == 403
    assert "Registration closed" in response.json()["detail"]


def test_protected_endpoint_without_cookie(client: TestClient, container: Any) -> None:
    """Test that protected endpoints return 401 without session cookie."""
    auth = container.retrieve(AuthMiddleware)
    # Register a user but don't login
    auth.register_user("testuser", "password123")

    # Try to access protected endpoint
    response = client.get("/api/capabilities")

    assert response.status_code == 401


def test_protected_endpoint_with_cookie(client: TestClient, container: Any) -> None:
    """Test that protected endpoints return 200 with valid session cookie."""
    auth = container.retrieve(AuthMiddleware)
    # Register and login
    auth.register_user("testuser", "password123")
    login_response = client.post("/api/auth/login", json={
        "username": "testuser",
        "password": "password123"
    })
    session_cookie = login_response.cookies.get("session_id")

    # Access protected endpoint with cookie
    response = client.get("/api/capabilities", cookies={"session_id": session_cookie or ""})

    assert response.status_code == 200


def test_sse_auth_required(client: TestClient, container: Any) -> None:
    """Test that SSE endpoint requires authentication."""
    auth = container.retrieve(AuthMiddleware)
    # Register a user but don't login
    auth.register_user("testuser", "password123")

    # Try to access SSE without cookie
    response = client.get("/api/traces/stream")

    assert response.status_code == 401


def test_logout_clears_cookie(client: TestClient, container: Any) -> None:
    """Test that logout clears the session cookie."""
    auth = container.retrieve(AuthMiddleware)
    # Register and login
    auth.register_user("testuser", "password123")
    login_response = client.post("/api/auth/login", json={
        "username": "testuser",
        "password": "password123"
    })
    assert "session_id" in login_response.cookies

    # Logout
    logout_response = client.post("/api/auth/logout")

    assert logout_response.status_code == 200
    assert logout_response.json() == {"status": "logged_out"}
    # Cookie should be cleared (max-age=0 or expired)
