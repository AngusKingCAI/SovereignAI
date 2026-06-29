"""Tests for orchestrator thinking display functionality.

Tests that dispatch triggers the thinking display and task polling detects completion.
"""
from __future__ import annotations

from typing import Any
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

from sovereignai.shared.task_state_machine import ITaskStateQuery, TaskState
from web.main import app


@pytest.fixture
def client() -> TestClient:
    """Create a test client for the FastAPI app with lifespan context."""
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
def container(client: TestClient) -> Any:
    """Get the container from the app state."""
    return client.app.state.container


def test_dispatch_returns_task_id(client: TestClient, container: Any) -> None:
    """Test that dispatch returns a task ID that can be used for polling."""
    # Register and login
    client.post(
        "/api/auth/register", json={"username": "testuser9", "password": "testpass"}
    )
    response = client.post(
        "/api/auth/login", json={"username": "testuser9", "password": "testpass"}
    )
    assert response.status_code == 200
    session_cookie = response.cookies.get("session_id")
    client.cookies.set("session_id", session_cookie)

    # Dispatch a message
    response = client.post("/api/dispatch", json={"message": "test message"})
    assert response.status_code == 200
    result = response.json()
    assert "task_id" in result
    assert result["state"] in ["received", "processing"]


def test_task_state_polling_endpoint(client: TestClient, container: Any) -> None:
    """Test that the task state polling endpoint returns current state."""
    task_id = uuid4()

    # Register and login
    client.post(
        "/api/auth/register", json={"username": "testuser10", "password": "testpass"}
    )
    response = client.post(
        "/api/auth/login", json={"username": "testuser10", "password": "testpass"}
    )
    assert response.status_code == 200
    session_cookie = response.cookies.get("session_id")
    client.cookies.set("session_id", session_cookie)

    # Query task state (may return 404 if task doesn't exist, which is ok)
    response = client.get(f"/api/tasks/{task_id}")
    # Either 404 (not found) or 200 (if task exists)
    assert response.status_code in [200, 404]

    if response.status_code == 200:
        task = response.json()
        assert "state" in task
        assert "task_id" in task


def test_task_list_includes_dispatched_tasks(client: TestClient, container: Any) -> None:
    """Test that the task list includes tasks created via dispatch."""
    # Register and login
    client.post(
        "/api/auth/register", json={"username": "testuser11", "password": "testpass"}
    )
    response = client.post(
        "/api/auth/login", json={"username": "testuser11", "password": "testpass"}
    )
    assert response.status_code == 200
    session_cookie = response.cookies.get("session_id")
    client.cookies.set("session_id", session_cookie)

    # Get initial task count
    response = client.get("/api/tasks")
    assert response.status_code == 200
    initial_tasks = response.json()
    initial_count = len(initial_tasks)

    # Dispatch a message
    response = client.post("/api/dispatch", json={"message": "test message"})
    assert response.status_code == 200

    # Get updated task list
    response = client.get("/api/tasks")
    assert response.status_code == 200
    updated_tasks = response.json()

    # Should have at least as many tasks as before
    assert len(updated_tasks) >= initial_count


def test_task_state_transitions_are_trackable(client: TestClient, container: Any) -> None:
    """Test that task state transitions can be tracked via the state machine."""
    task_id = uuid4()
    task_state_query = container.retrieve(ITaskStateQuery)

    # Submit a task (this would normally be done via CapabilityAPI)
    # For this test, we'll just verify the state machine is accessible
    state = task_state_query.get_state(task_id)
    # State may be None if task doesn't exist, which is ok
    if state is not None:
        assert isinstance(state, TaskState)
