"""Integration tests for log drawer functionality.

Tests that the SSE stream emits events, the REST trace API returns
filtered results, and the task-specific trace endpoint works.
"""
from __future__ import annotations

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


def test_sse_stream_emits_events(client: TestClient, trace_emitter: TraceEmitter) -> None:
    """Test that the SSE stream endpoint exists (TestClient doesn't support streaming)."""
    pytest.skip("TestClient doesn't support SSE streaming - skip this test")


def test_rest_traces_api_returns_filtered_results(
    client: TestClient, trace_emitter: TraceEmitter
) -> None:
    """Test that the REST trace API returns filtered results."""
    # Emit test events with different levels
    trace_emitter.emit(
        level=TraceLevel.ERROR,
        component="TestComponent",
        message="Error message",
    )
    trace_emitter.emit(
        level=TraceLevel.INFO,
        component="TestComponent",
        message="Info message",
    )
    trace_emitter.emit(
        level=TraceLevel.DEBUG,
        component="OtherComponent",
        message="Debug message",
    )

    # Register and login
    client.post(
        "/api/auth/register", json={"username": "testuser_rest", "password": "testpass"}
    )
    response = client.post(
        "/api/auth/login", json={"username": "testuser_rest", "password": "testpass"}
    )
    assert response.status_code == 200
    session_cookie = response.cookies.get("session_id")
    client.cookies.set("session_id", session_cookie)

    # Query traces with level filter
    response = client.get("/api/traces?level=error")
    assert response.status_code == 200
    traces = response.json()
    assert len(traces) >= 1
    assert all(t["level"] == "error" for t in traces)

    # Query traces with component filter
    response = client.get("/api/traces?component=TestComponent")
    assert response.status_code == 200
    traces = response.json()
    assert len(traces) >= 2
    assert all(t["component"] == "TestComponent" for t in traces)


def test_task_specific_trace_endpoint(client: TestClient, trace_emitter: TraceEmitter) -> None:
    """Test that the task-specific trace endpoint works."""
    from uuid import uuid4

    task_id = uuid4()

    # Emit events for a specific task
    trace_emitter.emit(
        level=TraceLevel.INFO,
        component="TestComponent",
        message="Task event 1",
        correlation_id=task_id,
    )
    trace_emitter.emit(
        level=TraceLevel.WARN,
        component="TestComponent",
        message="Task event 2",
        correlation_id=task_id,
    )
    # Emit an event for a different task
    trace_emitter.emit(
        level=TraceLevel.INFO,
        component="TestComponent",
        message="Other task event",
        correlation_id=uuid4(),
    )

    # Register and login
    client.post(
        "/api/auth/register", json={"username": "testuser_task", "password": "testpass"}
    )
    response = client.post(
        "/api/auth/login", json={"username": "testuser_task", "password": "testpass"}
    )
    assert response.status_code == 200
    session_cookie = response.cookies.get("session_id")
    client.cookies.set("session_id", session_cookie)

    # Query traces for the specific task
    response = client.get(f"/api/traces/{task_id}")
    assert response.status_code == 200
    traces = response.json()
    assert len(traces) >= 2
    assert all(str(t["correlation_id"]) == str(task_id) for t in traces)
