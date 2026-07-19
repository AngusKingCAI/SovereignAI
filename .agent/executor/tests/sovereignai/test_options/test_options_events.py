import tempfile
from pathlib import Path
from unittest.mock import Mock

import pytest
from sovereignai.options.backend import SQLiteOptionsBackend


@pytest.fixture
def temp_db() -> Path:
    """Create temporary database for testing."""
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        return Path(f.name)


@pytest.fixture
def mock_event_bus() -> Mock:
    """Create mock event bus."""
    return Mock()


@pytest.fixture
def backend(temp_db: Path, mock_event_bus: Mock) -> SQLiteOptionsBackend:
    """Create backend instance with temporary database and mock event bus."""
    b = SQLiteOptionsBackend(temp_db, event_bus=mock_event_bus)
    yield b
    b.close()


def test_backend_emits_event_on_set(backend: SQLiteOptionsBackend, mock_event_bus: Mock) -> None:
    """Test backend emits event when setting option."""
    backend.set("test_key", "test_value")

    # Verify event was published
    assert mock_event_bus.publish.called
    call_args = mock_event_bus.publish.call_args
    assert call_args[0][0].channel == "options.changed"


def test_backend_emits_event_on_delete(backend: SQLiteOptionsBackend, mock_event_bus: Mock) -> None:
    """Test backend emits event when deleting option."""
    backend.set("test_key", "test_value")
    backend.delete("test_key")

    # Verify event was published twice (set + delete)
    assert mock_event_bus.publish.call_count == 2


def test_backend_no_event_on_delete_nonexistent(
    backend: SQLiteOptionsBackend, mock_event_bus: Mock,
) -> None:
    """Test backend does not emit event when deleting nonexistent key."""
    backend.delete("nonexistent_key")

    # Verify no event was published
    assert not mock_event_bus.publish.called


def test_backend_event_bus_optional(temp_db: Path) -> None:
    """Test backend works without event bus."""
    backend = SQLiteOptionsBackend(temp_db, event_bus=None)
    backend.set("test_key", "test_value")
    backend.delete("test_key")
    backend.close()

    # Should not raise
    assert True


def test_backend_event_publish_failure_does_not_prevent_write(
    backend: SQLiteOptionsBackend, mock_event_bus: Mock,
) -> None:
    """Test event publish failure does not prevent write."""
    mock_event_bus.publish.side_effect = Exception("Event bus error")

    # Should not raise despite event publish failure
    backend.set("test_key", "test_value")

    # Verify write succeeded
    value = backend.get("test_key")
    assert value == "test_value"


def test_backend_event_publish_failure_does_not_prevent_delete(
    backend: SQLiteOptionsBackend, mock_event_bus: Mock,
) -> None:
    """Test event publish failure does not prevent delete."""
    backend.set("test_key", "test_value")
    mock_event_bus.publish.side_effect = Exception("Event bus error")

    # Should not raise despite event publish failure
    deleted = backend.delete("test_key")

    # Verify delete succeeded
    assert deleted is True
    value = backend.get("test_key")
    assert value is None
