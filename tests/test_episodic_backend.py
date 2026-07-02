from __future__ import annotations

import os
import tempfile
from collections.abc import Generator
from datetime import timedelta

import pytest

from sovereignai.memory.episodic_backend import EpisodicMemoryBackend
from sovereignai.shared.trace_emitter import TraceEmitter
from sovereignai.shared.types import EpisodicQuery, now_utc


@pytest.fixture
def temp_db_path() -> Generator[str, None, None]:
    import contextlib
    fd, path = tempfile.mkstemp(suffix='.db')
    os.close(fd)
    yield path
    with contextlib.suppress(Exception):
        os.unlink(path)

@pytest.fixture
def episodic_backend(temp_db_path: str) -> EpisodicMemoryBackend:
    trace = TraceEmitter()
    backend = EpisodicMemoryBackend(trace=trace)
    backend._db_path = temp_db_path
    backend._conn = None
    backend._initialize_db()
    return backend

def test_episodic_backend_store_returns_record_id(episodic_backend: EpisodicMemoryBackend) -> None:  # noqa: E501
    record_id = episodic_backend.store(data={  # noqa: E501
        'component': 'test',
        'event_type': 'test_event',
        'data': '{}'
    })
    assert isinstance(record_id, str)
    assert len(record_id) == 36

def test_episodic_backend_query_by_task_id(episodic_backend: EpisodicMemoryBackend) -> None:  # noqa: E501
    episodic_backend.store(data={  # noqa: E501
        'component': 'test',
        'event_type': 'test_event',
        'data': '{}',
        'task_id': 'task-1'
    })
    episodic_backend.store(data={  # noqa: E501
        'component': 'test',
        'event_type': 'test_event',
        'data': '{}',
        'task_id': 'task-2'
    })
    results = episodic_backend.query(EpisodicQuery(session_id='task-1'))
    assert len(results) == 1
    assert results[0]['task_id'] == 'task-1'

def test_episodic_backend_query_by_time_range(episodic_backend: EpisodicMemoryBackend) -> None:  # noqa: E501
    now = now_utc()
    past = now - timedelta(hours=1)
    future = now + timedelta(hours=1)

    episodic_backend.store(data={  # noqa: E501
        'component': 'test',
        'event_type': 'test_event',
        'data': '{}',
        'task_id': 'task-1'
    })
    results = episodic_backend.query(EpisodicQuery(session_id='task-1', time_range=(past, future)))
    assert len(results) == 1

def test_episodic_backend_delete_removes_record(episodic_backend: EpisodicMemoryBackend) -> None:  # noqa: E501
    record_id = episodic_backend.store(data={  # noqa: E501
        'component': 'test',
        'event_type': 'test_event',
        'data': '{}',
        'task_id': 'task-1'
    })
    deleted = episodic_backend.delete(record_id)
    assert deleted is True
    results = episodic_backend.query(EpisodicQuery(session_id='task-1'))
    assert len(results) == 0

def test_episodic_backend_delete_nonexistent_returns_false(episodic_backend: EpisodicMemoryBackend) -> None:  # noqa: E501
    deleted = episodic_backend.delete('nonexistent-id')
    assert deleted is False

def test_episodic_backend_close_cleans_up(episodic_backend: EpisodicMemoryBackend) -> None:
    assert episodic_backend._conn is not None
    episodic_backend.close()
    assert episodic_backend._conn is None
