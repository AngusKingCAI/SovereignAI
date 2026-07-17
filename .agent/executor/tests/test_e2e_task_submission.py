from __future__ import annotations

from typing import Any
from unittest.mock import Mock, patch
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient
from sovereignai.main import build_container


@pytest.fixture
def client() -> TestClient:
    from web.main import app
    container = build_container()
    app.state.container = container
    return TestClient(app)

@pytest.fixture
def container(client: TestClient) -> Any:
    return client.app.state.container

@pytest.fixture
def authenticated_client(client: TestClient, container: Any) -> TestClient:
    from sovereignai.shared.auth import AuthMiddleware
    auth = container.retrieve(AuthMiddleware)
    auth.register_user('testuser', 'password123')
    login_response = client.post(  # noqa: E501
        '/api/auth/login',
        json={'username': 'testuser', 'password': 'password123'}
    )
    session_cookie = login_response.cookies.get('session_id')
    if session_cookie:
        client.cookies.set('session_id', session_cookie)
    return client

def test_search_task_end_to_end(authenticated_client: TestClient, container: Any) -> None:
    from sovereignai.shared.capability_api import CapabilityAPI
    capability_api_mock = Mock()
    task_id = uuid4()
    capability_api_mock.submit_task = Mock(return_value=task_id)
    original_retrieve = container.retrieve

    def selective_retrieve(interface: Any) -> Any:
        if interface is CapabilityAPI:
            return capability_api_mock
        return original_retrieve(interface)
    with patch.object(container, 'retrieve', side_effect=selective_retrieve):
        response = authenticated_client.post(  # noqa: E501
            '/api/dispatch',
            json={'message': 'search for Python tutorials'}
        )
        assert response.status_code == 200
        result = response.json()
        assert result['task_id'] == str(task_id)
        capability_api_mock.submit_task.assert_called_once()

def test_task_state_updates_visible(authenticated_client: TestClient, container: Any) -> None:
    response = authenticated_client.get('/api/tasks')
    assert response.status_code == 200
    result = response.json()
    assert isinstance(result, list)
