"""Tests for the TraceMemoryBackend."""
from __future__ import annotations

import os
import tempfile

import pytest

from sovereignai.memory.trace_backend import TraceMemoryBackend
from sovereignai.shared.trace_emitter import TraceEmitter
from sovereignai.shared.types import TraceEvent, TraceLevel, new_correlation_id


@pytest.fixture
def temp_db_path() -> str:
    """Provide a temporary database path for testing."""
    fd, path = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    yield path
    try:
        os.unlink(path)
    except Exception:
        pass


@pytest.fixture
def trace_backend(temp_db_path: str) -> TraceMemoryBackend:
    """Provide a TraceMemoryBackend instance with a temporary database."""
    trace = TraceEmitter()
    backend = TraceMemoryBackend(trace=trace)
    # Override the db path for testing
    backend._db_path = temp_db_path
    backend._conn = None
    backend._initialize_db()
    return backend


def test_trace_backend_store_accepts_standard_contract(trace_backend: TraceMemoryBackend) -> None:
    """Verify store accepts the standard memory backend contract (data dict, metadata dict)."""
    record_id = trace_backend.store(
        data={
            "component": "test",
            "level": "info",
            "message": "test message",
            "correlation_id": str(new_correlation_id()),
        },
        metadata={
            "task_id": "task-1",
            "task_state": "executing",
        },
    )
    assert isinstance(record_id, str)
    assert len(record_id) == 36  # UUID4 format


def test_trace_backend_store_without_metadata(trace_backend: TraceMemoryBackend) -> None:
    """Verify store works without optional metadata dict."""
    record_id = trace_backend.store(
        data={
            "component": "test",
            "level": "info",
            "message": "test message",
            "correlation_id": str(new_correlation_id()),
        },
        metadata=None,
    )
    assert isinstance(record_id, str)


def test_trace_backend_query_by_task_id(trace_backend: TraceMemoryBackend) -> None:
    """Verify query can filter by task_id."""
    trace_backend.store(
        data={
            "component": "test",
            "level": "info",
            "message": "test message",
            "correlation_id": str(new_correlation_id()),
        },
        metadata={"task_id": "task-1", "task_state": "executing"},
    )
    trace_backend.store(
        data={
            "component": "test",
            "level": "info",
            "message": "test message",
            "correlation_id": str(new_correlation_id()),
        },
        metadata={"task_id": "task-2", "task_state": "executing"},
    )

    results = trace_backend.query({"task_id": "task-1"})
    assert len(results) == 1
    assert results[0]["task_id"] == "task-1"


def test_trace_backend_query_by_correlation_id(trace_backend: TraceMemoryBackend) -> None:
    """Verify query can filter by correlation_id."""
    corr_id = str(new_correlation_id())
    trace_backend.store(
        data={
            "component": "test",
            "level": "info",
            "message": "test message",
            "correlation_id": corr_id,
        },
    )

    results = trace_backend.query({"correlation_id": corr_id})
    assert len(results) == 1
    assert results[0]["correlation_id"] == corr_id


def test_trace_backend_delete_removes_record(trace_backend: TraceMemoryBackend) -> None:
    """Verify delete removes a trace event by id."""
    record_id = trace_backend.store(
        data={
            "component": "test",
            "level": "info",
            "message": "test message",
            "correlation_id": str(new_correlation_id()),
        },
    )

    deleted = trace_backend.delete(record_id)
    assert deleted is True

    # Verify record is gone
    results = trace_backend.query({})
    assert len(results) == 0


def test_trace_backend_get_last_task_states(trace_backend: TraceMemoryBackend) -> None:
    """Verify get_last_task_states returns the last state for each task."""
    task_id = "task-1"

    # Store multiple state transitions for the same task
    trace_backend.store(
        data={
            "component": "TaskStateMachine",
            "level": "info",
            "message": "Task transitioned",
            "correlation_id": str(new_correlation_id()),
        },
        metadata={"task_id": task_id, "task_state": "received"},
    )
    trace_backend.store(
        data={
            "component": "TaskStateMachine",
            "level": "info",
            "message": "Task transitioned",
            "correlation_id": str(new_correlation_id()),
        },
        metadata={"task_id": task_id, "task_state": "executing"},
    )
    trace_backend.store(
        data={
            "component": "TaskStateMachine",
            "level": "info",
            "message": "Task transitioned",
            "correlation_id": str(new_correlation_id()),
        },
        metadata={"task_id": task_id, "task_state": "complete"},
    )

    # Should return only the last state
    last_states = trace_backend.get_last_task_states()
    assert last_states[task_id] == "complete"


def test_trace_backend_get_last_task_states_uses_timestamp_not_id(trace_backend: TraceMemoryBackend) -> None:
    """Verify get_last_task_states uses MAX(timestamp) not MAX(id) per Rev7.

    UUID4 is random, not monotonic. Using MAX(id) would return the wrong state.
    This test verifies the fix uses MAX(timestamp) instead.
    """
    task_id = "task-1"

    # Store states with different timestamps
    import time
    time.sleep(0.01)  # Ensure different timestamps
    trace_backend.store(
        data={
            "component": "TaskStateMachine",
            "level": "info",
            "message": "Task transitioned",
            "correlation_id": str(new_correlation_id()),
        },
        metadata={"task_id": task_id, "task_state": "received"},
    )
    time.sleep(0.01)
    trace_backend.store(
        data={
            "component": "TaskStateMachine",
            "level": "info",
            "message": "Task transitioned",
            "correlation_id": str(new_correlation_id()),
        },
        metadata={"task_id": task_id, "task_state": "complete"},
    )

    last_states = trace_backend.get_last_task_states()
    # Should return "complete" (the most recent by timestamp), not "received"
    assert last_states[task_id] == "complete"


def test_trace_backend_close_cleans_up(trace_backend: TraceMemoryBackend) -> None:
    """Verify close closes the database connection."""
    assert trace_backend._conn is not None
    trace_backend.close()
    assert trace_backend._conn is None
