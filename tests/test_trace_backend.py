from __future__ import annotations

import os
import tempfile
from collections.abc import Generator

import pytest

from sovereignai.memory.trace_backend import TraceMemoryBackend
from sovereignai.shared.trace_emitter import TraceEmitter
from sovereignai.shared.types import new_correlation_id


@pytest.fixture
def temp_db_path() -> Generator[str, None, None]:
    import contextlib
    fd, path = tempfile.mkstemp(suffix='.db')
    os.close(fd)
    yield path
    with contextlib.suppress(Exception):
        os.unlink(path)

@pytest.fixture
def trace_backend(temp_db_path: str) -> TraceMemoryBackend:
    trace = TraceEmitter()
    backend = TraceMemoryBackend(trace=trace)
    backend._db_path = temp_db_path
    backend._conn = None
    backend._initialize_db()
    return backend

def test_trace_backend_store_accepts_standard_contract(trace_backend: TraceMemoryBackend) -> None:
    record_id = trace_backend.store(data={'component': 'test', 'level': 'info', 'message': 'test message', 'correlation_id': str(new_correlation_id())}, metadata={'task_id': 'task-1', 'task_state': 'executing'})
    assert isinstance(record_id, str)
    assert len(record_id) == 36

def test_trace_backend_store_without_metadata(trace_backend: TraceMemoryBackend) -> None:
    record_id = trace_backend.store(data={'component': 'test', 'level': 'info', 'message': 'test message', 'correlation_id': str(new_correlation_id())}, metadata=None)
    assert isinstance(record_id, str)

def test_trace_backend_query_by_task_id(trace_backend: TraceMemoryBackend) -> None:
    trace_backend.store(data={'component': 'test', 'level': 'info', 'message': 'test message', 'correlation_id': str(new_correlation_id())}, metadata={'task_id': 'task-1', 'task_state': 'executing'})
    trace_backend.store(data={'component': 'test', 'level': 'info', 'message': 'test message', 'correlation_id': str(new_correlation_id())}, metadata={'task_id': 'task-2', 'task_state': 'executing'})
    results = trace_backend.query({'task_id': 'task-1'})
    assert len(results) == 1
    assert results[0]['task_id'] == 'task-1'

def test_trace_backend_query_by_correlation_id(trace_backend: TraceMemoryBackend) -> None:
    corr_id = str(new_correlation_id())
    trace_backend.store(data={'component': 'test', 'level': 'info', 'message': 'test message', 'correlation_id': corr_id})
    results = trace_backend.query({'correlation_id': corr_id})
    assert len(results) == 1
    assert results[0]['correlation_id'] == corr_id

def test_trace_backend_delete_removes_record(trace_backend: TraceMemoryBackend) -> None:
    record_id = trace_backend.store(data={'component': 'test', 'level': 'info', 'message': 'test message', 'correlation_id': str(new_correlation_id())})
    deleted = trace_backend.delete(record_id)
    assert deleted is True
    results = trace_backend.query({})
    assert len(results) == 0

def test_trace_backend_get_last_task_states(trace_backend: TraceMemoryBackend) -> None:
    task_id = 'task-1'
    trace_backend.store(data={'component': 'TaskStateMachine', 'level': 'info', 'message': 'Task transitioned', 'correlation_id': str(new_correlation_id())}, metadata={'task_id': task_id, 'task_state': 'received'})
    trace_backend.store(data={'component': 'TaskStateMachine', 'level': 'info', 'message': 'Task transitioned', 'correlation_id': str(new_correlation_id())}, metadata={'task_id': task_id, 'task_state': 'executing'})
    trace_backend.store(data={'component': 'TaskStateMachine', 'level': 'info', 'message': 'Task transitioned', 'correlation_id': str(new_correlation_id())}, metadata={'task_id': task_id, 'task_state': 'complete'})
    last_states = trace_backend.get_last_task_states()
    assert last_states[task_id] == 'complete'

def test_trace_backend_get_last_task_states_uses_timestamp_not_id(trace_backend: TraceMemoryBackend) -> None:
    task_id = 'task-1'
    import time
    time.sleep(0.01)
    trace_backend.store(data={'component': 'TaskStateMachine', 'level': 'info', 'message': 'Task transitioned', 'correlation_id': str(new_correlation_id())}, metadata={'task_id': task_id, 'task_state': 'received'})
    time.sleep(0.01)
    trace_backend.store(data={'component': 'TaskStateMachine', 'level': 'info', 'message': 'Task transitioned', 'correlation_id': str(new_correlation_id())}, metadata={'task_id': task_id, 'task_state': 'complete'})
    last_states = trace_backend.get_last_task_states()
    assert last_states[task_id] == 'complete'

def test_trace_backend_close_cleans_up(trace_backend: TraceMemoryBackend) -> None:
    assert trace_backend._conn is not None
    trace_backend.close()
    assert trace_backend._conn is None
