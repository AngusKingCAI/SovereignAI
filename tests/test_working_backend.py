from __future__ import annotations

import pytest

from sovereignai.memory.working_backend import WorkingMemoryBackend
from sovereignai.shared.trace_emitter import TraceEmitter
from sovereignai.shared.types import TaskState


@pytest.fixture
def working_backend() -> WorkingMemoryBackend:
    trace = TraceEmitter()
    return WorkingMemoryBackend(trace=trace)

def test_working_backend_store_returns_record_id(working_backend: WorkingMemoryBackend) -> None:
    record_id = working_backend.store(data={'task_id': 'task-1', 'key': 'test_key', 'value': 'test_value'})
    assert isinstance(record_id, str)
    assert len(record_id) == 36

def test_working_backend_query_by_task_id(working_backend: WorkingMemoryBackend) -> None:
    working_backend.store(data={'task_id': 'task-1', 'key': 'key1', 'value': 'value1'})
    working_backend.store(data={'task_id': 'task-2', 'key': 'key2', 'value': 'value2'})
    results = working_backend.query({'task_id': 'task-1'})
    assert len(results) == 1
    assert results[0]['task_id'] == 'task-1'

def test_working_backend_query_by_key(working_backend: WorkingMemoryBackend) -> None:
    working_backend.store(data={'task_id': 'task-1', 'key': 'key1', 'value': 'value1'})
    working_backend.store(data={'task_id': 'task-1', 'key': 'key2', 'value': 'value2'})
    results = working_backend.query({'task_id': 'task-1', 'key': 'key1'})
    assert len(results) == 1
    assert results[0]['key'] == 'key1'

def test_working_backend_delete_removes_record(working_backend: WorkingMemoryBackend) -> None:
    record_id = working_backend.store(data={'task_id': 'task-1', 'key': 'test_key', 'value': 'test_value'})
    deleted = working_backend.delete(record_id)
    assert deleted is True
    results = working_backend.query({'task_id': 'task-1'})
    assert len(results) == 0

def test_working_backend_cleanup_removes_all_task_records(working_backend: WorkingMemoryBackend) -> None:
    working_backend.store(data={'task_id': 'task-1', 'key': 'key1', 'value': 'value1'})
    working_backend.store(data={'task_id': 'task-1', 'key': 'key2', 'value': 'value2'})
    working_backend.store(data={'task_id': 'task-2', 'key': 'key3', 'value': 'value3'})
    working_backend.cleanup('task-1')
    results = working_backend.query({'task_id': 'task-1'})
    assert len(results) == 0
    results = working_backend.query({'task_id': 'task-2'})
    assert len(results) == 1

def test_working_backend_cleanup_nonexistent_task_no_error(working_backend: WorkingMemoryBackend) -> None:
    working_backend.cleanup('nonexistent-task')

def test_working_backend_enum_string_comparison_robustness(working_backend: WorkingMemoryBackend) -> None:
    terminal_states = (TaskState.COMPLETE.value, TaskState.FAILED.value)
    assert TaskState.COMPLETE.value in terminal_states
    assert TaskState.FAILED.value in terminal_states
    assert 'complete' in terminal_states
    assert 'failed' in terminal_states
    assert TaskState.RECEIVED.value not in terminal_states
    assert 'received' not in terminal_states
