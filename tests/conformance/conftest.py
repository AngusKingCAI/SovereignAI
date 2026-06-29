"""Pytest fixtures for conformance tests."""
from unittest.mock import Mock

import pytest


@pytest.fixture
def mock_adapter():
    """Mock adapter instance for conformance testing."""
    adapter = Mock()
    adapter.health_check = Mock(return_value=True)
    adapter.manifest = Mock()
    return adapter


@pytest.fixture
def mock_skill():
    """Mock skill instance for conformance testing."""
    skill = Mock()
    skill.execute = Mock()
    skill.manifest = Mock()
    return skill


@pytest.fixture
def mock_memory_backend():
    """Mock memory backend instance for conformance testing."""
    backend = Mock()
    backend.store = Mock(return_value="test_id")
    backend.retrieve = Mock(return_value={"data": "test"})
    return backend
