"""Tests for the ProceduralMemoryBackend."""
from __future__ import annotations

import os
import tempfile

import pytest

from sovereignai.memory.procedural_backend import (
    ProceduralMemoryBackend,
    ProceduralMemoryLockTimeout,
)
from sovereignai.shared.trace_emitter import TraceEmitter


@pytest.fixture
def temp_json_path() -> str:
    """Provide a temporary JSON path for testing."""
    fd, path = tempfile.mkstemp(suffix=".json")
    os.close(fd)
    yield path
    try:
        os.unlink(path)
    except Exception:
        pass


@pytest.fixture
def procedural_backend(temp_json_path: str) -> ProceduralMemoryBackend:
    """Provide a ProceduralMemoryBackend instance with a temporary JSON file."""
    trace = TraceEmitter()
    backend = ProceduralMemoryBackend(trace=trace)
    backend._path = temp_json_path
    backend._ensure_file_exists()
    return backend


def test_procedural_backend_store_returns_record_id(procedural_backend: ProceduralMemoryBackend) -> None:
    """Verify store returns a UUID string record id."""
    record_id = procedural_backend.store(
        data={
            "pattern": "test pattern",
            "confidence": 0.9,
        }
    )
    assert isinstance(record_id, str)
    assert len(record_id) == 36  # UUID4 format


def test_procedural_backend_lock_timeout_raises_exception(procedural_backend: ProceduralMemoryBackend) -> None:
    """Verify lock timeout raises ProceduralMemoryLockTimeout."""
    # Acquire the lock manually
    lock_path = procedural_backend._path + ".lock"
    with open(lock_path, "w") as f:
        f.write("test-pid")

    # Try to store with a short timeout
    procedural_backend._acquire_lock = lambda timeout_s=0.1: False
    with pytest.raises(ProceduralMemoryLockTimeout):
        procedural_backend.store(
            data={
                "pattern": "test pattern",
                "confidence": 0.9,
            }
        )

    # Clean up lock
    try:
        os.unlink(lock_path)
    except Exception:
        pass


def test_procedural_backend_query_by_pattern(procedural_backend: ProceduralMemoryBackend) -> None:
    """Verify query can filter by pattern substring."""
    procedural_backend.store(
        data={
            "pattern": "search pattern",
            "confidence": 0.9,
        }
    )
    procedural_backend.store(
        data={
            "pattern": "other pattern",
            "confidence": 0.8,
        }
    )

    results = procedural_backend.query({"pattern": "search"})
    assert len(results) == 1
    assert "search" in results[0]["pattern"]


def test_procedural_backend_query_by_min_confidence(procedural_backend: ProceduralMemoryBackend) -> None:
    """Verify query can filter by minimum confidence threshold."""
    procedural_backend.store(
        data={
            "pattern": "high confidence",
            "confidence": 0.9,
        }
    )
    procedural_backend.store(
        data={
            "pattern": "low confidence",
            "confidence": 0.5,
        }
    )

    results = procedural_backend.query({"min_confidence": 0.8})
    assert len(results) == 1
    assert results[0]["confidence"] == 0.9


def test_procedural_backend_delete_removes_record(procedural_backend: ProceduralMemoryBackend) -> None:
    """Verify delete removes a pattern by id."""
    record_id = procedural_backend.store(
        data={
            "pattern": "test pattern",
            "confidence": 0.9,
        }
    )

    deleted = procedural_backend.delete(record_id)
    assert deleted is True

    # Verify record is gone
    results = procedural_backend.query({})
    assert len(results) == 0


def test_procedural_backend_prune_low_confidence(procedural_backend: ProceduralMemoryBackend) -> None:
    """Verify prune_low_confidence removes patterns below threshold."""
    procedural_backend.store(
        data={
            "pattern": "high confidence",
            "confidence": 0.9,
        }
    )
    procedural_backend.store(
        data={
            "pattern": "low confidence",
            "confidence": 0.3,
        }
    )

    procedural_backend.prune_low_confidence(0.5)

    results = procedural_backend.query({})
    assert len(results) == 1
    assert results[0]["confidence"] == 0.9


def test_procedural_backend_hard_cap_enforcement(procedural_backend: ProceduralMemoryBackend) -> None:
    """Verify hard cap enforcement evicts oldest patterns when exceeded."""
    from sovereignai.memory.procedural_backend import MAX_PATTERNS

    # Set a small cap for testing by monkey-patching
    original_max = MAX_PATTERNS
    import sovereignai.memory.procedural_backend as proc_module
    proc_module.MAX_PATTERNS = 3

    try:
        # Add patterns with different last_used timestamps
        procedural_backend.store(
            data={
                "pattern": "oldest",
                "confidence": 0.9,
                "last_used": 1.0,
            }
        )
        procedural_backend.store(
            data={
                "pattern": "middle",
                "confidence": 0.9,
                "last_used": 2.0,
            }
        )
        procedural_backend.store(
            data={
                "pattern": "newest",
                "confidence": 0.9,
                "last_used": 3.0,
            }
        )

        # Add one more to trigger eviction
        procedural_backend.store(
            data={
                "pattern": "trigger",
                "confidence": 0.9,
                "last_used": 4.0,
            }
        )

        # Should have 3 patterns, oldest evicted
        results = procedural_backend.query({})
        assert len(results) == 3
        pattern_names = {r["pattern"] for r in results}
        assert "oldest" not in pattern_names
    finally:
        proc_module.MAX_PATTERNS = original_max
