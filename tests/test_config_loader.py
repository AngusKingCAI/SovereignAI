"""Tests for config_loader module."""
import json
import os
import tempfile
from pathlib import Path

import pytest

from sovereignai.shared.config_loader import (
    delete_api_key,
    get_api_key,
    get_config_value,
    load_config,
    save_config,
    set_api_key,
    set_config_value,
)


@pytest.fixture
def temp_config_file(monkeypatch):
    """Create a temporary config file for testing."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        temp_path = f.name
    monkeypatch.setattr('sovereignai.shared.config_loader.CONFIG_PATH', Path(temp_path))
    yield temp_path
    if os.path.exists(temp_path):
        os.unlink(temp_path)


def test_load_config_empty(temp_config_file):
    """Test loading config when file doesn't exist."""
    os.unlink(temp_config_file)
    config = load_config()
    assert config == {}


def test_load_config_valid(temp_config_file):
    """Test loading valid config."""
    test_config = {"api_keys": {"openai": "sk-test"}, "ollama": {"host": "localhost"}}
    with open(temp_config_file, 'w') as f:
        json.dump(test_config, f)
    config = load_config()
    assert config == test_config


def test_load_config_invalid_json(temp_config_file):
    """Test loading config with invalid JSON."""
    with open(temp_config_file, 'w') as f:
        f.write("invalid json")
    config = load_config()
    assert config == {}


def test_save_config(temp_config_file):
    """Test saving config."""
    test_config = {"test": "value"}
    save_config(test_config)
    with open(temp_config_file) as f:
        loaded = json.load(f)
    assert loaded == test_config


def test_get_config_value_simple(temp_config_file):
    """Test getting a simple config value."""
    test_config = {"simple": "value"}
    save_config(test_config)
    assert get_config_value("simple") == "value"


def test_get_config_value_nested(temp_config_file):
    """Test getting a nested config value with dotted key."""
    test_config = {"ollama": {"host": "localhost:11434"}}
    save_config(test_config)
    assert get_config_value("ollama.host") == "localhost:11434"


def test_get_config_value_missing(temp_config_file):
    """Test getting a missing config value returns default."""
    assert get_config_value("missing.key", "default") == "default"


def test_get_config_value_invalid_path(temp_config_file):
    """Test getting a value from an invalid nested path."""
    test_config = {"simple": "value"}
    save_config(test_config)
    assert get_config_value("simple.nested", "default") == "default"


def test_set_config_value_simple(temp_config_file):
    """Test setting a simple config value."""
    set_config_value("simple", "value")
    assert get_config_value("simple") == "value"


def test_set_config_value_nested(temp_config_file):
    """Test setting a nested config value."""
    set_config_value("ollama.host", "localhost:11434")
    assert get_config_value("ollama.host") == "localhost:11434"


def test_set_api_key(temp_config_file):
    """Test setting an API key."""
    set_api_key("openai", "sk-test123")
    assert get_api_key("openai") == "sk-test123"


def test_get_api_key_missing(temp_config_file):
    """Test getting a missing API key."""
    assert get_api_key("missing") is None


def test_delete_api_key(temp_config_file):
    """Test deleting an API key."""
    set_api_key("openai", "sk-test123")
    assert get_api_key("openai") == "sk-test123"
    delete_api_key("openai")
    assert get_api_key("openai") is None


def test_delete_api_key_missing(temp_config_file):
    """Test deleting a missing API key doesn't error."""
    delete_api_key("missing")  # Should not raise
