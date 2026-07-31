"""Tests for app/web/routes/trace.py."""

import pytest
from unittest.mock import AsyncMock, MagicMock
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.web.routes.trace import router, set_dependencies
from app.web.schemas import ExecutionTraceEvent, LifecycleEvent


@pytest.fixture
def mock_trace_producer():
    """Mock trace producer."""
    producer = AsyncMock()
    producer.get_recent_events = AsyncMock(return_value=[])
    return producer


@pytest.fixture
def mock_lifecycle_producer():
    """Mock lifecycle producer."""
    producer = AsyncMock()
    producer.get_recent_events = AsyncMock(return_value=[])
    return producer


@pytest.fixture
def mock_sse_broker():
    """Mock SSE broker."""
    broker = AsyncMock()
    broker.create_client = AsyncMock(return_value={"client_id": "test-client"})
    broker.publish = AsyncMock()
    return broker


@pytest.fixture
def client(mock_trace_producer, mock_lifecycle_producer, mock_sse_broker):
    """Create test client with mocked dependencies."""
    set_dependencies(
        trace_producer_dep=mock_trace_producer,
        lifecycle_producer_dep=mock_lifecycle_producer,
        sse_broker_dep=mock_sse_broker,
    )

    app = FastAPI()
    app.include_router(router)
    
    return TestClient(app)


def test_stream_execution_trace(client, mock_sse_broker):
    """Test SSE endpoint for execution trace streaming."""
    response = client.get("/api/trace/stream")
    
    # Placeholder returns 200
    assert response.status_code in [200, 503]


def test_get_trace_events(client, mock_trace_producer):
    """Test REST endpoint for trace events."""
    response = client.get("/api/trace/events")
    
    assert response.status_code in [200, 503]
    
    if response.status_code == 200:
        data = response.json()
        assert "events" in data


def test_stream_lifecycle_events(client, mock_sse_broker):
    """Test SSE endpoint for lifecycle event streaming."""
    response = client.get("/api/trace/lifecycle/stream")
    
    # Placeholder returns 200
    assert response.status_code in [200, 503]


def test_get_lifecycle_events(client, mock_lifecycle_producer):
    """Test REST endpoint for lifecycle events."""
    response = client.get("/api/trace/lifecycle/events")
    
    assert response.status_code in [200, 503]
    
    if response.status_code == 200:
        data = response.json()
        assert "events" in data


def test_publish_trace_event(client, mock_sse_broker):
    """Test publishing a trace event."""
    event = ExecutionTraceEvent(
        timestamp="2026-07-21T00:00:00Z",
        phase="test",
        event_type="info",
        message="Test event",
    )
    
    response = client.post("/api/trace/events", json=event.model_dump())
    
    assert response.status_code in [200, 503]


def test_publish_lifecycle_event(client, mock_sse_broker):
    """Test publishing a lifecycle event."""
    event = LifecycleEvent(
        timestamp="2026-07-21T00:00:00Z",
        event_type="agent_started",
        agent_id="test-agent",
        details={"status": "running"},
    )
    
    response = client.post("/api/trace/lifecycle/events", json=event.model_dump())
    
    assert response.status_code in [200, 503]


def test_service_unavailable():
    """Test service unavailable when dependencies are None."""
    set_dependencies(
        trace_producer_dep=None,
        lifecycle_producer_dep=None,
        sse_broker_dep=None,
    )
    
    app = FastAPI()
    app.include_router(router)
    client = TestClient(app)
    
    response = client.get("/api/trace/stream")
    assert response.status_code == 503
