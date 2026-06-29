"""Tests for REST trace API endpoints.

Tests /api/traces with level, component, task_id filters + pagination.
"""
from __future__ import annotations

from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

from sovereignai.shared.trace_emitter import TraceEmitter
from sovereignai.shared.types import TraceLevel
from web.main import app


@pytest.fixture
def client() -> TestClient:
    """Create a test client for the FastAPI app with lifespan context."""
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
def trace_emitter(client: TestClient) -> TraceEmitter:
    """Get the TraceEmitter from the app state."""
    return client.app.state.container.retrieve(TraceEmitter)


def test_traces_with_level_filter(client: TestClient, trace_emitter: TraceEmitter) -> None:
    """Test /api/traces with level filter."""
    # Emit events with different levels
    for _ in range(5):
        trace_emitter.emit(
            level=TraceLevel.ERROR,
            component="TestComponent",
            message="Error message",
        )
    for _ in range(3):
        trace_emitter.emit(
            level=TraceLevel.INFO,
            component="TestComponent",
            message="Info message",
        )

    # Register and login
    client.post(
        "/api/auth/register", json={"username": "testuser_level", "password": "testpass"}
    )
    response = client.post(
        "/api/auth/login", json={"username": "testuser_level", "password": "testpass"}
    )
    assert response.status_code == 200
    session_cookie = response.cookies.get("session_id")
    client.cookies.set("session_id", session_cookie)

    response = client.get("/api/traces?level=error")
    assert response.status_code == 200
    traces = response.json()
    assert len(traces) >= 5
    assert all(t["level"] == "error" for t in traces)


def test_traces_with_component_filter(client: TestClient, trace_emitter: TraceEmitter) -> None:
    """Test /api/traces with component filter."""
    # Emit events for different components
    for _ in range(4):
        trace_emitter.emit(
            level=TraceLevel.INFO,
            component="ComponentA",
            message="Message from A",
        )
    for _ in range(2):
        trace_emitter.emit(
            level=TraceLevel.INFO,
            component="ComponentB",
            message="Message from B",
        )

    # Register and login
    client.post(
        "/api/auth/register", json={"username": "testuser_comp", "password": "testpass"}
    )
    response = client.post(
        "/api/auth/login", json={"username": "testuser_comp", "password": "testpass"}
    )
    assert response.status_code == 200
    session_cookie = response.cookies.get("session_id")
    client.cookies.set("session_id", session_cookie)

    response = client.get("/api/traces?component=ComponentA")
    assert response.status_code == 200
    traces = response.json()
    assert len(traces) >= 4
    assert all(t["component"] == "ComponentA" for t in traces)


def test_traces_with_task_id_filter(client: TestClient, trace_emitter: TraceEmitter) -> None:
    """Test /api/traces with task_id filter."""
    task_id = uuid4()
    other_task_id = uuid4()

    # Emit events for specific task
    for _ in range(3):
        trace_emitter.emit(
            level=TraceLevel.INFO,
            component="TestComponent",
            message="Task event",
            correlation_id=task_id,
        )
    # Emit events for other task
    for _ in range(2):
        trace_emitter.emit(
            level=TraceLevel.INFO,
            component="TestComponent",
            message="Other task event",
            correlation_id=other_task_id,
        )

    # Register and login
    client.post(
        "/api/auth/register", json={"username": "testuser_taskid", "password": "testpass"}
    )
    response = client.post(
        "/api/auth/login", json={"username": "testuser_taskid", "password": "testpass"}
    )
    assert response.status_code == 200
    session_cookie = response.cookies.get("session_id")
    client.cookies.set("session_id", session_cookie)

    response = client.get(f"/api/traces?task_id={task_id}")
    assert response.status_code == 200
    traces = response.json()
    assert len(traces) >= 3
    assert all(str(t["correlation_id"]) == str(task_id) for t in traces)


def test_traces_pagination(client: TestClient, trace_emitter: TraceEmitter) -> None:
    """Test /api/traces with pagination (limit and offset)."""
    # Emit many events
    for i in range(20):
        trace_emitter.emit(
            level=TraceLevel.INFO,
            component="TestComponent",
            message=f"Message {i}",
        )

    # Register and login
    client.post(
        "/api/auth/register", json={"username": "testuser_page", "password": "testpass"}
    )
    response = client.post(
        "/api/auth/login", json={"username": "testuser_page", "password": "testpass"}
    )
    assert response.status_code == 200
    session_cookie = response.cookies.get("session_id")
    client.cookies.set("session_id", session_cookie)

    # Test limit
    response = client.get("/api/traces?limit=5")
    assert response.status_code == 200
    traces = response.json()
    assert len(traces) <= 5

    # Test offset
    response = client.get("/api/traces?limit=5&offset=10")
    assert response.status_code == 200
    traces = response.json()
    assert len(traces) <= 5


def test_traces_max_limit_enforced(client: TestClient, trace_emitter: TraceEmitter) -> None:
    """Test that the max limit of 1000 is enforced."""
    # Emit many events
    for i in range(1500):
        trace_emitter.emit(
            level=TraceLevel.INFO,
            component="TestComponent",
            message=f"Message {i}",
        )

    # Register and login
    client.post(
        "/api/auth/register", json={"username": "testuser_max", "password": "testpass"}
    )
    response = client.post(
        "/api/auth/login", json={"username": "testuser_max", "password": "testpass"}
    )
    assert response.status_code == 200
    session_cookie = response.cookies.get("session_id")
    client.cookies.set("session_id", session_cookie)

    # Request more than max limit
    response = client.get("/api/traces?limit=2000")
    assert response.status_code == 200
    traces = response.json()
    assert len(traces) <= 1000
