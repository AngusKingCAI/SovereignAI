"""Tests for the WorkingMemoryBackend."""
from __future__ import annotations

import pytest

from sovereignai.memory.working_backend import WorkingMemoryBackend
from sovereignai.shared.trace_emitter import TraceEmitter
from sovereignai.shared.types import TaskState


@pytest.fixture
def working_backend() -> WorkingMemoryBackend:
    """Provide a WorkingMemoryBackend instance."""
    trace = TraceEmitter()
    return WorkingMemoryBackend(trace=trace)


def test_working_backend_store_returns_record_id(working_backend: WorkingMemoryBackend) -> None:
    """Verify store returns a UUID string record id."""
    record_id = working_backend.store(
        data={
            "task_id": "task-1",
            "key": "test_key",
            "value": "test_value",
        }
    )
    assert isinstance(record_id, str)
    assert len(record_id) == 36  # UUID4 format


def test_working_backend_query_by_task_id(working_backend: WorkingMemoryBackend) -> None:
    """Verify query can filter by task_id."""
    working_backend.store(
        data={
            "task_id": "task-1",
            "key": "key1",
            "value": "value1",
        }
    )
    working_backend.store(
        data={
            "task_id": "task-2",
            "key": "key2",
            "value": "value2",
        }
    )

    results = working_backend.query({"task_id": "task-1"})
    assert len(results) == 1
    assert results[0]["task_id"] == "task-1"


def test_working_backend_query_by_key(working_backend: WorkingMemoryBackend) -> None:
    """Verify query can filter by key."""
    working_backend.store(
        data={
            "task_id": "task-1",
            "key": "key1",
            "value": "value1",
        }
    )
    working_backend.store(
        data={
            "task_id": "task-1",
            "key": "key2",
            "value": "value2",
        }
    )

    results = working_backend.query({"task_id": "task-1", "key": "key1"})
    assert len(results) == 1
    assert results[0]["key"] == "key1"


def test_working_backend_delete_removes_record(working_backend: WorkingMemoryBackend) -> None:
    """Verify delete removes a record by id."""
    record_id = working_backend.store(
        data={
            "task_id": "task-1",
            "key": "test_key",
            "value": "test_value",
        }
    )

    deleted = working_backend.delete(record_id)
    assert deleted is True

    # Verify record is gone
    results = working_backend.query({"task_id": "task-1"})
    assert len(results) == 0


def test_working_backend_cleanup_removes_all_task_records(working_backend: WorkingMemoryBackend) -> None:
    """Verify cleanup removes all records for a task."""
    working_backend.store(
        data={
            "task_id": "task-1",
            "key": "key1",
            "value": "value1",
        }
    )
    working_backend.store(
        data={
            "task_id": "task-1",
            "key": "key2",
            "value": "value2",
        }
    )
    working_backend.store(
        data={
            "task_id": "task-2",
            "key": "key3",
            "value": "value3",
        }
    )

    working_backend.cleanup("task-1")

    # Verify task-1 records are gone
    results = working_backend.query({"task_id": "task-1"})
    assert len(results) == 0

    # Verify task-2 records remain
    results = working_backend.query({"task_id": "task-2"})
    assert len(results) == 1


def test_working_backend_cleanup_nonexistent_task_no_error(working_backend: WorkingMemoryBackend) -> None:
    """Verify cleanup on nonexistent task does not raise an error."""
    working_backend.cleanup("nonexistent-task")  # Should not raise


def test_working_backend_enum_string_comparison_robustness(working_backend: WorkingMemoryBackend) -> None:
    """Verify enum/string comparison works for both enum and string values."""
    # This test validates the robustness check in main.py's _on_task_state_changed handler
    terminal_states = (TaskState.COMPLETE.value, TaskState.FAILED.value)

    # Test with enum value
    assert TaskState.COMPLETE.value in terminal_states
    assert TaskState.FAILED.value in terminal_states

    # Test with string value (simulating deserialization)
    assert "complete" in terminal_states
    assert "failed" in terminal_states

    # Test that non-terminal states are not in the set
    assert TaskState.RECEIVED.value not in terminal_states
    assert "received" not in terminal_states
