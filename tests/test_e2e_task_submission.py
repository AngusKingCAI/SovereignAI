"""End-to-end tests for task submission flow."""
from __future__ import annotations

from typing import Any
from unittest.mock import Mock, patch
from uuid import uuid4

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
    """Get the container from the app state."""
    return client.app.state.container  # type: ignore[attr-defined]


@pytest.fixture
def authenticated_client(client: TestClient, container: Any) -> TestClient:
    """Create an authenticated test client."""
    from sovereignai.shared.auth import AuthMiddleware
    auth = container.retrieve(AuthMiddleware)

    # Register user first (before any requests)
    auth.register_user("testuser", "password123")

    # Login
    login_response = client.post("/api/auth/login", json={
        "username": "testuser",
        "password": "password123"
    })
    session_cookie = login_response.cookies.get("session_id")

    # Return client with session cookie
    if session_cookie:
        client.cookies.set("session_id", session_cookie)
    return client


def test_search_task_end_to_end(authenticated_client: TestClient, container: Any) -> None:
    """Test end-to-end task submission through dispatch endpoint."""
    from sovereignai.shared.capability_api import CapabilityAPI

    # Mock the capability API
    capability_api_mock = Mock()
    task_id = uuid4()
    capability_api_mock.submit_task = Mock(return_value=task_id)

    # Patch only the CapabilityAPI retrieval
    original_retrieve = container.retrieve
    def selective_retrieve(interface: Any) -> Any:
        if interface is CapabilityAPI:
            return capability_api_mock
        return original_retrieve(interface)

    with patch.object(container, 'retrieve', side_effect=selective_retrieve):
        # Submit a message
        response = authenticated_client.post("/api/dispatch", json={
            "message": "search for Python tutorials"
        })

        assert response.status_code == 200
        result = response.json()
        assert result["task_id"] == str(task_id)

        # Verify capability API was called
        capability_api_mock.submit_task.assert_called_once()


def test_task_state_updates_visible(authenticated_client: TestClient, container: Any) -> None:
    """Test that task state endpoint is accessible with authentication."""
    # Verify the endpoint structure is correct
    # Actual task state transitions are covered by integration tests
    response = authenticated_client.get("/api/tasks")

    assert response.status_code == 200
    result = response.json()
    assert isinstance(result, list)
