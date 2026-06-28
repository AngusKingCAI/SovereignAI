"""End-to-end tests for task submission flow."""
from __future__ import annotations

from datetime import UTC, datetime
from unittest.mock import AsyncMock, MagicMock, patch
import pytest
from fastapi.testclient import TestClient
from sovereignai.main import build_container
from uuid import uuid4


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


@pytest.fixture
def authenticated_client(client, container):
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
    client.cookies.set("session_id", session_cookie)
    return client


def test_search_task_end_to_end(authenticated_client, container):
    """Test end-to-end task submission through dispatch endpoint."""
    from sovereignai.orchestrator.dispatcher import MessageDispatcher
    from sovereignai.shared.types import Task, CapabilityDeclaration, CapabilityCategory
    
    # Mock the dispatcher
    dispatcher_mock = AsyncMock()
    task_id = uuid4()
    capability = CapabilityDeclaration(
        category=CapabilityCategory.TOOL,
        name="websearch",
        version="1.0.0",
        priority=0
    )
    mock_task = Task(
        task_id=task_id,
        capability=capability,
        payload="search for Python tutorials",
        submitted_at=datetime.now(UTC)
    )
    dispatcher_mock.dispatch.return_value = mock_task
    
    # Patch only the MessageDispatcher retrieval
    original_retrieve = container.retrieve
    def selective_retrieve(interface):
        if interface is MessageDispatcher:
            return dispatcher_mock
        return original_retrieve(interface)
    
    with patch.object(container, 'retrieve', side_effect=selective_retrieve):
        # Submit a message
        response = authenticated_client.post("/api/dispatch", json={
            "message": "search for Python tutorials"
        })
        
        assert response.status_code == 200
        result = response.json()
        assert result["task_id"] == str(task_id)
        
        # Verify dispatcher was called
        dispatcher_mock.dispatch.assert_called_once()


def test_task_state_updates_visible(authenticated_client, container):
    """Test that task state endpoint is accessible with authentication."""
    # Verify the endpoint structure is correct
    # Actual task state transitions are covered by integration tests
    response = authenticated_client.get("/api/tasks")
    
    assert response.status_code == 200
    result = response.json()
    assert isinstance(result, list)
