"""Test web UI panel structure and navigation.

Per S5: Use FastAPI TestClient to verify HTML structure.
"""
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
    """Create a mock DI container with all required dependencies."""
    from typing import Any

    from sovereignai.shared.auth import AuthMiddleware

    container = Mock()

    # Mock ICapabilityIndex
    capability_index = Mock()
    capability_index.list_all_components.return_value = [
        ComponentManifest(
            component_id=ComponentId("TestAdapter"),
            version="1.0.0",
            provides=(
                CapabilityDeclaration(
                    category=CapabilityCategory.TOOL,
                    name="test_tool",
                    version="1.0.0",
                    priority=0,
                ),
            ),
            requires=(),
            author="test",
            content_hash="abc123",
        ),
    ]

    # Mock AuthMiddleware with _password_hashes attribute
    auth_mock = Mock(spec=AuthMiddleware)
    auth_mock._password_hashes = {"test": "hash"}

    def retrieve_side_effect(cls: Any) -> Any:
        if cls.__name__ == "ICapabilityIndex":
            return capability_index
        if cls is AuthMiddleware:
            return auth_mock
        return Mock()

    container.retrieve.side_effect = retrieve_side_effect

    return container


@pytest.fixture
def client(mock_container: Mock) -> TestClient:
    """Create a test client with dependency overrides for the mock container."""
    # Override the app's state to use the mock container
    app.state.container = mock_container
    return TestClient(app)


def test_all_panels_render(client: TestClient) -> None:
    """Verify that all 10 panel sections exist in the HTML response.

    GET / and assert all panel-<name> sections are present.
    """
    response = client.get("/")
    assert response.status_code == 200
    html = response.text

    panels = [
        "panel-orchestrator",
        "panel-workers",
        "panel-tasks",
        "panel-skills",
        "panel-memory",
        "panel-models",
        "panel-adapters",
        "panel-hardware",
        "panel-logs",
        "panel-options",
    ]

    for panel in panels:
        assert f'id="{panel}"' in html, f"Panel {panel} not found in HTML"


def test_orchestrator_panel_has_chat_form(client: TestClient) -> None:
    """Verify that the orchestrator panel contains a chat form.

    Assert chat input and submit button exist in the HTML.
    """
    response = client.get("/")
    assert response.status_code == 200
    html = response.text

    assert 'id="chat-form"' in html
    assert 'id="chat-input"' in html
    assert '<button>' in html


def test_logs_panel_controls_exist(client: TestClient) -> None:
    """Verify that the Logs panel has filter controls.

    Assert level checkboxes, search input, source filter, and clear button exist.
    """
    response = client.get("/")
    assert response.status_code == 200
    html = response.text

    assert 'class="logs-controls"' in html
    assert 'data-level="error"' in html
    assert 'data-level="warn"' in html
    assert 'data-level="info"' in html
    assert 'data-level="debug"' in html
    assert 'data-level="trace"' in html
    assert 'id="logs-search"' in html
    assert 'id="logs-source-filter"' in html
    assert 'id="logs-clear"' in html
    assert 'id="logs-autoscroll"' in html
    assert 'id="logs-linewrap"' in html


def test_sidebar_navigation_exists(client: TestClient) -> None:
    """Verify that the sidebar navigation structure exists.

    Assert sidebar, sidebar-nav, and panel data attributes exist.
    """
    response = client.get("/")
    assert response.status_code == 200
    html = response.text

    assert 'id="sidebar"' in html
    assert 'class="sidebar-nav"' in html
    assert 'data-panel="orchestrator"' in html
    assert 'data-panel="workers"' in html
    assert 'data-panel="tasks"' in html
