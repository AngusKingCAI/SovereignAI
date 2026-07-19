import tempfile
from datetime import UTC
from pathlib import Path

import pytest
from sovereignai.options.backend import SQLiteOptionsBackend


@pytest.fixture
def temp_db() -> Path:
    """Create temporary database for testing."""
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        return Path(f.name)


@pytest.fixture
def backend(temp_db: Path) -> SQLiteOptionsBackend:
    """Create backend instance with temporary database."""
    b = SQLiteOptionsBackend(temp_db, event_bus=None)
    yield b
    b.close()


def test_backend_initialization(backend: SQLiteOptionsBackend) -> None:
    """Test backend initializes successfully."""
    assert backend._connection is not None
    assert not backend._closed


def test_backend_get_default(backend: SQLiteOptionsBackend) -> None:
    """Test get returns default for missing key."""
    value = backend.get("nonexistent_key", "default_value")
    assert value == "default_value"


def test_backend_get_none_default(backend: SQLiteOptionsBackend) -> None:
    """Test get returns None for missing key when no default."""
    value = backend.get("nonexistent_key")
    assert value is None


def test_backend_set_get(backend: SQLiteOptionsBackend) -> None:
    """Test set and get basic values."""
    backend.set("test_key", "test_value")
    value = backend.get("test_key")
    assert value == "test_value"


def test_backend_set_get_json(backend: SQLiteOptionsBackend) -> None:
    """Test set and get JSON serialized values."""

    data = {"nested": {"value": 123}, "list": [1, 2, 3]}
    backend.set("json_key", data)
    value = backend.get("json_key")
    assert value == data


def test_backend_set_update(backend: SQLiteOptionsBackend) -> None:
    """Test set updates existing key."""
    backend.set("test_key", "value1")
    backend.set("test_key", "value2")
    value = backend.get("test_key")
    assert value == "value2"


def test_backend_delete(backend: SQLiteOptionsBackend) -> None:
    """Test delete removes key."""
    backend.set("test_key", "test_value")
    deleted = backend.delete("test_key")
    assert deleted is True
    value = backend.get("test_key")
    assert value is None


def test_backend_delete_nonexistent(backend: SQLiteOptionsBackend) -> None:
    """Test delete returns False for nonexistent key."""
    deleted = backend.delete("nonexistent_key")
    assert deleted is False


def test_backend_api_key_get_none(backend: SQLiteOptionsBackend) -> None:
    """Test get_api_key returns None for missing provider."""
    key = backend.get_api_key("openai")
    assert key is None


def test_backend_api_key_set_get(backend: SQLiteOptionsBackend) -> None:
    """Test set_api_key and get_api_key."""
    backend.set_api_key("openai", "sk-test-123")
    key = backend.get_api_key("openai")
    assert key == "sk-test-123"


def test_backend_api_key_update(backend: SQLiteOptionsBackend) -> None:
    """Test set_api_key updates existing key."""
    backend.set_api_key("openai", "sk-test-123")
    backend.set_api_key("openai", "sk-test-456")
    key = backend.get_api_key("openai")
    assert key == "sk-test-456"


def test_backend_api_key_delete(backend: SQLiteOptionsBackend) -> None:
    """Test delete_api_key removes key."""
    backend.set_api_key("openai", "sk-test-123")
    deleted = backend.delete_api_key("openai")
    assert deleted is True
    key = backend.get_api_key("openai")
    assert key is None


def test_backend_api_key_delete_nonexistent(backend: SQLiteOptionsBackend) -> None:
    """Test delete_api_key returns False for nonexistent provider."""
    deleted = backend.delete_api_key("openai")
    assert deleted is False


def test_backend_close_idempotent(backend: SQLiteOptionsBackend) -> None:
    """Test close is idempotent."""
    backend.close()
    backend.close()
    assert backend._closed is True


def test_backend_operations_after_close(backend: SQLiteOptionsBackend) -> None:
    """Test operations after close are safe."""
    backend.close()
    backend.set("test_key", "value")
    value = backend.get("test_key", "default")
    assert value == "default"


def test_backend_wal_mode(backend: SQLiteOptionsBackend) -> None:
    """Test WAL mode is enabled."""
    cursor = backend._connection.cursor()
    cursor.execute("PRAGMA journal_mode")
    mode = cursor.fetchone()[0]
    assert mode == "wal"


def test_backend_persistence(temp_db: Path) -> None:
    """Test data persists across backend instances."""
    b1 = SQLiteOptionsBackend(temp_db)
    b1.set("test_key", "test_value")
    b1.set_api_key("openai", "sk-test-123")
    b1.close()

    b2 = SQLiteOptionsBackend(temp_db)
    value = b2.get("test_key")
    key = b2.get_api_key("openai")
    b2.close()

    assert value == "test_value"
    assert key == "sk-test-123"


def test_backend_empty_string_default(backend: SQLiteOptionsBackend) -> None:
    """Test empty string default."""
    value = backend.get("nonexistent", "")
    assert value == ""


def test_backend_zero_default(backend: SQLiteOptionsBackend) -> None:
    """Test zero default."""
    value = backend.get("nonexistent", 0)
    assert value == 0


def test_backend_false_default(backend: SQLiteOptionsBackend) -> None:
    """Test False default."""
    value = backend.get("nonexistent", False)
    assert value is False


def test_backend_multiple_keys(backend: SQLiteOptionsBackend) -> None:
    """Test multiple keys can be stored."""
    backend.set("key1", "value1")
    backend.set("key2", "value2")
    backend.set("key3", "value3")

    assert backend.get("key1") == "value1"
    assert backend.get("key2") == "value2"
    assert backend.get("key3") == "value3"


def test_backend_multiple_providers(backend: SQLiteOptionsBackend) -> None:
    """Test multiple API keys can be stored."""
    backend.set_api_key("openai", "sk-openai-123")
    backend.set_api_key("ollama", "sk-ollama-456")
    backend.set_api_key("hf", "sk-hf-789")

    assert backend.get_api_key("openai") == "sk-openai-123"
    assert backend.get_api_key("ollama") == "sk-ollama-456"
    assert backend.get_api_key("hf") == "sk-hf-789"


def test_backend_complex_json(backend: SQLiteOptionsBackend) -> None:
    """Test complex JSON structures."""
    data = {
        "users": [
            {"id": 1, "name": "Alice"},
            {"id": 2, "name": "Bob"},
        ],
        "settings": {"theme": "dark", "language": "en"},
    }
    backend.set("complex_key", data)
    value = backend.get("complex_key")
    assert value == data


def test_backend_list_value(backend: SQLiteOptionsBackend) -> None:
    """Test list values."""
    data = [1, 2, 3, 4, 5]
    backend.set("list_key", data)
    value = backend.get("list_key")
    assert value == data


def test_backend_datetime_value(backend: SQLiteOptionsBackend) -> None:
    """Test datetime values."""
    from datetime import datetime

    dt = datetime.now(UTC)
    backend.set("datetime_key", dt.isoformat())
    value = backend.get("datetime_key")
    assert value == dt.isoformat()
