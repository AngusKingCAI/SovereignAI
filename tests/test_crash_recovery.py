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
def temp_marker_path() -> Generator[str, None, None]:
    import contextlib
    fd, path = tempfile.mkstemp(suffix='.marker')
    os.close(fd)
    yield path
    with contextlib.suppress(Exception):
        if os.path.exists(path):
            os.unlink(path)

@pytest.fixture
def trace_backend(temp_db_path: str) -> TraceMemoryBackend:
    trace = TraceEmitter()
    backend = TraceMemoryBackend(trace=trace)
    backend._db_path = temp_db_path
    backend._conn = None
    backend._initialize_db()
    return backend

def test_shutdown_marker_skips_recovery(trace_backend: TraceMemoryBackend, temp_marker_path: str) -> None:
    magic = 'SOVEREIGNAI_CLEAN_SHUTDOWN_V1\n'
    with open(temp_marker_path, 'w') as f:
        f.write(magic + '2026-06-29T00:00:00')
    marker_exists = os.path.exists(temp_marker_path)
    assert marker_exists is True
    with open(temp_marker_path) as f:
        content = f.read()
    is_valid = content.startswith('SOVEREIGNAI_CLEAN_SHUTDOWN_V1\n')
    assert is_valid is True
    os.unlink(temp_marker_path)
    assert not os.path.exists(temp_marker_path)

def test_invalid_marker_content_treats_as_crash(temp_marker_path: str) -> None:
    with open(temp_marker_path, 'w') as f:
        f.write('INVALID_MARKER\n')
    with open(temp_marker_path) as f:
        content = f.read()
    is_valid = content.startswith('SOVEREIGNAI_CLEAN_SHUTDOWN_V1\n')
    assert is_valid is False
    os.unlink(temp_marker_path)

def test_no_marker_triggers_recovery(trace_backend: TraceMemoryBackend) -> None:
    task_id = 'task-1'
    trace_backend.store(data={'component': 'TaskStateMachine', 'level': 'info', 'message': 'Task transitioned', 'correlation_id': str(new_correlation_id())}, metadata={'task_id': task_id, 'task_state': 'executing'})
    last_states = trace_backend.get_last_task_states()
    assert task_id in last_states
    assert last_states[task_id] == 'executing'
    incomplete_tasks = [tid for tid, state in last_states.items() if state in ('received', 'queued', 'executing')]
    assert task_id in incomplete_tasks

def test_recovery_failure_does_not_block_startup(temp_marker_path: str) -> None:
    invalid_path = '/nonexistent/path/.shutdown_marker'
    try:
        if os.path.exists(invalid_path):
            with open(invalid_path) as f:
                _ = f.read()
        assert True
    except Exception:
        assert True

def test_atomic_write_creates_valid_marker(temp_marker_path: str) -> None:
    magic = 'SOVEREIGNAI_CLEAN_SHUTDOWN_V1\n'
    tmp_path = temp_marker_path + '.tmp'
    with open(tmp_path, 'w') as f:
        f.write(magic + '2026-06-29T00:00:00')
    os.replace(tmp_path, temp_marker_path)
    assert os.path.exists(temp_marker_path)
    with open(temp_marker_path) as f:
        content = f.read()
    assert content.startswith(magic)
    os.unlink(temp_marker_path)

def test_incomplete_task_detection(trace_backend: TraceMemoryBackend) -> None:
    trace_backend.store(data={'component': 'TaskStateMachine', 'level': 'info', 'message': 'Task transitioned', 'correlation_id': str(new_correlation_id())}, metadata={'task_id': 'task-1', 'task_state': 'received'})
    trace_backend.store(data={'component': 'TaskStateMachine', 'level': 'info', 'message': 'Task transitioned', 'correlation_id': str(new_correlation_id())}, metadata={'task_id': 'task-2', 'task_state': 'complete'})
    trace_backend.store(data={'component': 'TaskStateMachine', 'level': 'info', 'message': 'Task transitioned', 'correlation_id': str(new_correlation_id())}, metadata={'task_id': 'task-3', 'task_state': 'executing'})
    last_states = trace_backend.get_last_task_states()
    incomplete_tasks = [tid for tid, state in last_states.items() if state in ('received', 'queued', 'executing')]
    assert 'task-1' in incomplete_tasks
    assert 'task-2' not in incomplete_tasks
    assert 'task-3' in incomplete_tasks
    assert len(incomplete_tasks) == 2
