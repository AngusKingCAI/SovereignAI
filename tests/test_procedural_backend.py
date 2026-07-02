from __future__ import annotations

import os
import tempfile
from collections.abc import Generator

import pytest

from sovereignai.memory.procedural_backend import (
    ProceduralMemoryBackend,
    ProceduralMemoryLockTimeoutError,
)
from sovereignai.shared.trace_emitter import TraceEmitter
from sovereignai.shared.types import ProceduralQuery


@pytest.fixture
def temp_json_path() -> Generator[str, None, None]:
    import contextlib
    fd, path = tempfile.mkstemp(suffix='.json')
    os.close(fd)
    yield path
    with contextlib.suppress(Exception):
        os.unlink(path)

@pytest.fixture
def procedural_backend(temp_json_path: str) -> ProceduralMemoryBackend:
    trace = TraceEmitter()
    backend = ProceduralMemoryBackend(trace=trace)
    backend._path = temp_json_path
    backend._ensure_file_exists()
    return backend

def test_procedural_backend_store_returns_record_id(procedural_backend: ProceduralMemoryBackend) -> None:  # noqa: E501
    record_id = procedural_backend.store(data={'pattern': 'test pattern', 'confidence': 0.9})
    assert isinstance(record_id, str)
    assert len(record_id) == 36

def test_procedural_backend_lock_timeout_raises_exception(procedural_backend: ProceduralMemoryBackend) -> None:  # noqa: E501
    lock_path = procedural_backend._path + '.lock'
    with open(lock_path, 'w') as f:
        f.write('test-pid')
    procedural_backend._acquire_lock = lambda timeout_s=0.1: False
    with pytest.raises(ProceduralMemoryLockTimeoutError):
        procedural_backend.store(data={'pattern': 'test pattern', 'confidence': 0.9})
    import contextlib
    with contextlib.suppress(Exception):
        os.unlink(lock_path)

def test_procedural_backend_query_by_skill_name(procedural_backend: ProceduralMemoryBackend) -> None:
    procedural_backend.store(data={'pattern': 'websearch skill pattern', 'confidence': 0.9})
    procedural_backend.store(data={'pattern': 'calculator skill pattern', 'confidence': 0.8})
    results = procedural_backend.query(ProceduralQuery(skill_name='websearch'))
    assert len(results) == 1
    assert 'websearch' in results[0]['pattern']

def test_procedural_backend_query_by_capability_type(procedural_backend: ProceduralMemoryBackend) -> None:  # noqa: E501
    procedural_backend.store(data={'pattern': 'model_inference capability', 'confidence': 0.9})
    procedural_backend.store(data={'pattern': 'tool capability', 'confidence': 0.8})
    results = procedural_backend.query(ProceduralQuery(capability_type='model_inference'))
    assert len(results) == 1
    assert 'model_inference' in results[0]['pattern']

def test_procedural_backend_delete_removes_record(procedural_backend: ProceduralMemoryBackend) -> None:  # noqa: E501
    record_id = procedural_backend.store(data={'pattern': 'test pattern', 'confidence': 0.9})
    deleted = procedural_backend.delete(record_id)
    assert deleted is True
    results = procedural_backend.query(ProceduralQuery())
    assert len(results) == 0

def test_procedural_backend_prune_low_confidence(procedural_backend: ProceduralMemoryBackend) -> None:  # noqa: E501
    procedural_backend.store(data={'pattern': 'high confidence', 'confidence': 0.9})
    procedural_backend.store(data={'pattern': 'low confidence', 'confidence': 0.3})
    procedural_backend.prune_low_confidence(0.5)
    results = procedural_backend.query(ProceduralQuery())
    assert len(results) == 1
    assert results[0]['confidence'] == 0.9

def test_procedural_backend_hard_cap_enforcement(procedural_backend: ProceduralMemoryBackend) -> None:  # noqa: E501
    from sovereignai.memory.procedural_backend import MAX_PATTERNS
    original_max = MAX_PATTERNS
    import sovereignai.memory.procedural_backend as proc_module
    proc_module.MAX_PATTERNS = 3
    try:
        procedural_backend.store(data={'pattern': 'oldest', 'confidence': 0.9, 'last_used': 1.0})
        procedural_backend.store(data={'pattern': 'middle', 'confidence': 0.9, 'last_used': 2.0})
        procedural_backend.store(data={'pattern': 'newest', 'confidence': 0.9, 'last_used': 3.0})
        procedural_backend.store(data={'pattern': 'trigger', 'confidence': 0.9, 'last_used': 4.0})
        results = procedural_backend.query(ProceduralQuery())
        assert len(results) == 3
        pattern_names = {r['pattern'] for r in results}
        assert 'oldest' not in pattern_names
    finally:
        proc_module.MAX_PATTERNS = original_max
