from __future__ import annotations

from unittest.mock import Mock

import pytest
from fastapi.testclient import TestClient

from sovereignai.shared.types import (
    CapabilityCategory,
    CapabilityDeclaration,
    ComponentId,
    ComponentManifest,
)
from web.main import app


@pytest.fixture
def mock_container() -> Mock:
    from typing import Any

    from sovereignai.shared.auth import AuthMiddleware
    container = Mock()
    capability_index = Mock()
    capability_index.list_all_components.return_value = [ComponentManifest(component_id=ComponentId('TestAdapter'), version='1.0.0', provides=(CapabilityDeclaration(category=CapabilityCategory.TOOL, name='test_tool', version='1.0.0', priority=0),), requires=(), author='test', content_hash='abc123')]
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
def client(mock_container: Mock) -> TestClient:
    app.state.container = mock_container
    return TestClient(app)

def test_all_panels_render(client: TestClient) -> None:
    response = client.get('/')
    assert response.status_code == 200
    html = response.text
    panels = ['panel-orchestrator', 'panel-workers', 'panel-tasks', 'panel-skills', 'panel-memory', 'panel-models', 'panel-adapters', 'panel-hardware', 'panel-options']
    for panel in panels:
        assert f'id="{panel}"' in html, f'Panel {panel} not found in HTML'

def test_orchestrator_panel_has_chat_form(client: TestClient) -> None:
    response = client.get('/')
    assert response.status_code == 200
    html = response.text
    assert 'id="chat-form"' in html
    assert 'id="chat-input"' in html
    assert '<button>' in html

def test_log_drawer_controls_exist(client: TestClient) -> None:
    response = client.get('/')
    assert response.status_code == 200
    html = response.text
    assert 'id="log-controls"' in html
    assert 'data-level="ERROR"' in html
    assert 'data-level="WARN"' in html
    assert 'data-level="INFO"' in html
    assert 'data-level="DEBUG"' in html
    assert 'data-level="TRACE"' in html
    assert 'id="log-search"' in html
    assert 'id="log-clear"' in html

def test_sidebar_navigation_exists(client: TestClient) -> None:
    response = client.get('/')
    assert response.status_code == 200
    html = response.text
    assert 'id="sidebar"' in html
    assert 'class="sidebar-nav"' in html
    assert 'data-panel="orchestrator"' in html
    assert 'data-panel="workers"' in html
    assert 'data-panel="tasks"' in html
