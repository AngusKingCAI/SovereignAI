"""Test compatibility matrix storage and queries."""

import json
from unittest.mock import MagicMock

import pytest

from sovereignai.versioning.compatibility_matrix import CompatibilityMatrix


@pytest.fixture(autouse=True)
def cleanup_matrix_files() -> None:
    """Clean up matrix files before and after each test."""
    matrix = CompatibilityMatrix(trace=MagicMock())
    if matrix.STORAGE_PATH.exists():
        matrix.STORAGE_PATH.unlink()
    if matrix.BACKUP_PATH.exists():
        matrix.BACKUP_PATH.unlink()
    yield
    if matrix.STORAGE_PATH.exists():
        matrix.STORAGE_PATH.unlink()
    if matrix.BACKUP_PATH.exists():
        matrix.BACKUP_PATH.unlink()


def test_record_and_flush() -> None:
    """Record entries and flush to disk."""
    mock_trace = MagicMock()
    matrix = CompatibilityMatrix(trace=mock_trace)

    # Record some entries
    matrix.record(
        component_a="comp1",
        version_a="1.0.0",
        content_hash_a="hash1",
        component_b="comp2",
        version_b="1.0.0",
        content_hash_b="hash2",
        status="compatible",
    )

    matrix.record(
        component_a="comp1",
        version_a="1.0.0",
        content_hash_a="hash1",
        component_b="comp3",
        version_b="2.0.0",
        content_hash_b="hash3",
        status="incompatible",
    )

    # Flush to disk
    matrix.flush()

    # Verify file was created
    assert matrix.STORAGE_PATH.exists()

    # Load and verify content
    with matrix.STORAGE_PATH.open("r") as f:
        data = json.load(f)

    assert data["schema_version"] == 1
    assert len(data["entries"]) == 2
    assert data["entries"][0]["component_a"] == "comp1"
    assert data["entries"][0]["status"] == "compatible"
    assert data["entries"][1]["status"] == "incompatible"


def test_is_tested_with_matching_hashes() -> None:
    """Test is_tested returns True when hashes match."""
    mock_trace = MagicMock()
    matrix = CompatibilityMatrix(trace=mock_trace)

    # Record an entry
    matrix.record(
        component_a="comp1",
        version_a="1.0.0",
        content_hash_a="hash1",
        component_b="comp2",
        version_b="1.0.0",
        content_hash_b="hash2",
        status="compatible",
    )
    matrix.flush()

    # Query with matching hashes
    result = matrix.is_tested(
        component_a="comp1",
        version_a="1.0.0",
        content_hash_a="hash1",
        component_b="comp2",
        version_b="1.0.0",
        content_hash_b="hash2",
    )

    assert result is True


def test_is_tested_with_mismatched_hashes() -> None:
    """Test is_tested returns False when hashes differ (stale entry)."""
    mock_trace = MagicMock()
    matrix = CompatibilityMatrix(trace=mock_trace)

    # Record an entry
    matrix.record(
        component_a="comp1",
        version_a="1.0.0",
        content_hash_a="hash1",
        component_b="comp2",
        version_b="1.0.0",
        content_hash_b="hash2",
        status="compatible",
    )
    matrix.flush()

    # Query with different hash (stale)
    result = matrix.is_tested(
        component_a="comp1",
        version_a="1.0.0",
        content_hash_a="hash1_new",
        component_b="comp2",
        version_b="1.0.0",
        content_hash_b="hash2",
    )

    assert result is False


def test_get_status_unknown() -> None:
    """Test get_status returns 'unknown' for untested combinations."""
    mock_trace = MagicMock()
    matrix = CompatibilityMatrix(trace=mock_trace)

    result = matrix.get_status(
        component_a="comp1",
        version_a="1.0.0",
        content_hash_a="hash1",
        component_b="comp2",
        version_b="1.0.0",
        content_hash_b="hash2",
    )

    assert result == "unknown"


def test_get_status_with_content_hash_invalidation() -> None:
    """Test get_status returns 'unknown' when content hash differs."""
    mock_trace = MagicMock()
    matrix = CompatibilityMatrix(trace=mock_trace)

    # Record an entry
    matrix.record(
        component_a="comp1",
        version_a="1.0.0",
        content_hash_a="hash1",
        component_b="comp2",
        version_b="1.0.0",
        content_hash_b="hash2",
        status="compatible",
    )
    matrix.flush()

    # Query with different hash (should invalidate)
    result = matrix.get_status(
        component_a="comp1",
        version_a="1.0.0",
        content_hash_a="hash1_new",
        component_b="comp2",
        version_b="1.0.0",
        content_hash_b="hash2",
    )

    assert result == "unknown"


def test_corruption_recovery_from_backup() -> None:
    """Test recovery from backup when main file is corrupted."""
    mock_trace = MagicMock()
    matrix = CompatibilityMatrix(trace=mock_trace)

    # Write a valid backup
    backup_data = {
        "schema_version": 1,
        "entries": [
            {
                "component_a": "comp1",
                "version_a": "1.0.0",
                "content_hash_a": "hash1",
                "component_b": "comp2",
                "version_b": "1.0.0",
                "content_hash_b": "hash2",
                "tested_at": "2026-06-29T12:00:00Z",
                "status": "compatible",
            }
        ],
    }

    with matrix.BACKUP_PATH.open("w") as f:
        json.dump(backup_data, f)

    # Corrupt the main file
    with matrix.STORAGE_PATH.open("w") as f:
        f.write("corrupted json {{{")

    # Load should recover from backup
    data = matrix._load_with_recovery(matrix.STORAGE_PATH)

    assert data["schema_version"] == 1
    assert len(data["entries"]) == 1
    assert data["entries"][0]["component_a"] == "comp1"

    # Verify WARN trace was emitted
    mock_trace.emit.assert_called()
    warn_calls = [
        call for call in mock_trace.emit.call_args_list if "WARN" in str(call)
    ]
    assert len(warn_calls) > 0


def test_corruption_recovery_rebuild_empty() -> None:
    """Test rebuild with empty matrix when both main and backup are corrupted."""
    mock_trace = MagicMock()
    matrix = CompatibilityMatrix(trace=mock_trace)

    # Corrupt both files
    with matrix.STORAGE_PATH.open("w") as f:
        f.write("corrupted")
    with matrix.BACKUP_PATH.open("w") as f:
        f.write("corrupted")

    # Load should rebuild with empty matrix
    data = matrix._load_with_recovery(matrix.STORAGE_PATH)

    assert data["schema_version"] == 1
    assert len(data["entries"]) == 0

    # Verify WARN trace was emitted
    mock_trace.emit.assert_called()


def test_pruning_to_max_entries() -> None:
    """Test that entries are pruned to MAX_ENTRIES."""
    mock_trace = MagicMock()
    matrix = CompatibilityMatrix(trace=mock_trace)

    # Record more than MAX_ENTRIES
    for i in range(matrix.MAX_ENTRIES + 100):
        matrix.record(
            component_a=f"comp{i}",
            version_a="1.0.0",
            content_hash_a=f"hash{i}",
            component_b="comp{i+1}",
            version_b="1.0.0",
            content_hash_b=f"hash{i+1}",
            status="compatible",
        )

    matrix.flush()

    # Load and verify count
    with matrix.STORAGE_PATH.open("r") as f:
        data = json.load(f)

    assert len(data["entries"]) == matrix.MAX_ENTRIES
