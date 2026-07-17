from __future__ import annotations

from collections.abc import Generator
from typing import Any
from unittest.mock import Mock
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient
from sovereignai.shared.types import (
    CapabilityCategory,
    CapabilityDeclaration,
    ComponentId,
    ComponentManifest,
    TaskState,
)
from web.main import app


@pytest.fixture
def mock_container() -> Mock:
    container = Mock()
    capability_index = Mock()
    capability_index.list_all_components.return_value = [  # noqa: E501
        ComponentManifest(
            component_id=ComponentId('TestAdapter'),
            version='1.0.0',
            provides=(
                CapabilityDeclaration(
                    category=CapabilityCategory.TOOL,
                    name='test_tool',
                    version='1.0.0',
                    priority=0
                ),
            ),
            requires=(),
            author='test',
            content_hash='abc123'
        )
    ]
    from sovereignai.shared.auth import AuthMiddleware
    auth_mock = Mock(spec=AuthMiddleware)
    auth_mock._password_hashes = {'test': 'hash'}

    def retrieve_side_effect(cls: Any) -> Any:
        if cls.__name__ == 'ICapabilityIndex':
            return capability_index
        if cls is AuthMiddleware:
            return auth_mock
        return Mock()
    container.retrieve.side_effect = retrieve_side_effect
    return container

@pytest.fixture
def client(mock_container: Mock) -> Generator[TestClient, None, None]:
    app.state.container = mock_container
    from web.main import get_current_user
    app.dependency_overrides[get_current_user] = lambda: Mock()
    yield TestClient(app)
    app.dependency_overrides.clear()

def test_get_index_returns_200(client: TestClient) -> None:
    response = client.get('/')
    assert response.status_code == 200
    assert 'SovereignAI' in response.text

def test_get_capabilities_returns_json_list(client: TestClient) -> None:
    response = client.get('/api/capabilities')
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0
    assert 'id' in data[0]
    assert 'name' in data[0]
    assert 'category' in data[0]
    assert 'description' in data[0]
    assert 'priority' in data[0]

def test_post_task_returns_task_id(client: TestClient, mock_container: Mock) -> None:
    from sovereignai.shared.auth import AuthMiddleware
    from sovereignai.shared.capability_api import CapabilityAPI
    mock_api = Mock(spec=CapabilityAPI)
    task_id = uuid4()
    mock_api.submit_task.return_value = task_id
    mock_auth = Mock(spec=AuthMiddleware)
    mock_auth.validate.return_value = Mock()
    mock_auth._password_hashes = {'test': 'hash'}

    def retrieve_side_effect(cls: Any) -> Any:
        if cls is CapabilityAPI:
            return mock_api
        elif cls is AuthMiddleware:
            return mock_auth
        return Mock()
    mock_container.retrieve.side_effect = retrieve_side_effect
    response = client.post(  # noqa: E501
        '/api/tasks',
        json={
            'category': 'tool',
            'capability_name': 'test_tool',
            'payload': '{"test": "data"}'
        },
        cookies={'session_id': 'test_token'}
    )
    assert response.status_code == 200
    data = response.json()
    assert 'task_id' in data
    assert 'state' in data
    assert data['state'] == TaskState.RECEIVED.value

def test_get_task_state_returns_task(client: TestClient, mock_container: Mock) -> None:
    from sovereignai.shared.auth import AuthMiddleware
    from sovereignai.shared.capability_api import CapabilityAPI
    mock_api = Mock(spec=CapabilityAPI)
    task_id = uuid4()
    mock_api.get_task_state.return_value = TaskState.EXECUTING
    mock_auth = Mock(spec=AuthMiddleware)
    mock_auth.validate.return_value = Mock()
    mock_auth._password_hashes = {'test': 'hash'}

    def retrieve_side_effect(cls: Any) -> Any:
        if cls is CapabilityAPI:
            return mock_api
        elif cls is AuthMiddleware:
            return mock_auth
        return Mock()
    mock_container.retrieve.side_effect = retrieve_side_effect
    response = client.get(f'/api/tasks/{task_id}', cookies={'session_id': 'test_token'})
    assert response.status_code == 200
    data = response.json()
    assert 'task_id' in data
    assert 'state' in data
    assert data['state'] == TaskState.EXECUTING.value

def test_sse_auth_required(client: TestClient, mock_container: Mock) -> None:
    from sovereignai.shared.auth import AuthMiddleware
    from sovereignai.shared.event_bus import EventBus
    from sovereignai.shared.trace_emitter import TraceEmitter
    mock_trace = Mock(spec=TraceEmitter)
    mock_bus = Mock(spec=EventBus)
    mock_auth = Mock(spec=AuthMiddleware)
    mock_auth.validate.side_effect = Exception('Invalid token')
    mock_auth._password_hashes = {'test': 'hash'}

    def retrieve_side_effect(cls: Any) -> Any:
        if cls is TraceEmitter:
            return mock_trace
        elif cls is EventBus:
            return mock_bus
        elif cls is AuthMiddleware:
            return mock_auth
        return Mock()
    mock_container.retrieve.side_effect = retrieve_side_effect
    response = client.get('/api/traces/stream')
    assert response.status_code == 401

def test_dto_mapping_isolated(client: TestClient, mock_container: Mock) -> None:
    from sovereignai.shared.auth import AuthMiddleware
    from sovereignai.shared.capability_api import CapabilityAPI
    mock_api = Mock(spec=CapabilityAPI)
    task_id = uuid4()
    mock_api.get_task_state.return_value = TaskState.COMPLETE
    mock_auth = Mock(spec=AuthMiddleware)
    mock_auth.validate.return_value = Mock()
    mock_auth._password_hashes = {'test': 'hash'}

    def retrieve_side_effect(cls: Any) -> Any:
        if cls is CapabilityAPI:
            return mock_api
        elif cls is AuthMiddleware:
            return mock_auth
        return Mock()
    mock_container.retrieve.side_effect = retrieve_side_effect
    response = client.get(f'/api/tasks/{task_id}', cookies={'session_id': 'test_token'})
    assert response.status_code == 200
    data = response.json()
    assert 'task_id' in data
    assert 'state' in data
    assert 'result' in data
    assert 'error' in data
