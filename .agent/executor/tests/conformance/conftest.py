from unittest.mock import Mock

import pytest


@pytest.fixture
def mock_adapter():
    adapter = Mock()
    adapter.health_check = Mock(return_value=True)
    adapter.manifest = Mock()
    return adapter

@pytest.fixture
def mock_skill():
    skill = Mock()
    skill.execute = Mock()
    skill.manifest = Mock()
    return skill

@pytest.fixture
def mock_memory_backend():
    backend = Mock()
    backend.store = Mock(return_value='test_id')
    backend.retrieve = Mock(return_value={'data': 'test'})
    return backend
