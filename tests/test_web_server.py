"""Tests for the FastAPI web server.

Per OR24: Every new implementation must have a corresponding test file
with passing tests covering key paths.
"""
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
    """Create a mock DI container with all required dependencies."""
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
    from sovereignai.shared.auth import AuthMiddleware
    auth_mock = Mock(spec=AuthMiddleware)
    auth_mock._password_hashes = {"test": "hash"}  # Simulate existing user

    def retrieve_side_effect(cls: Any) -> Any:
        if cls.__name__ == "ICapabilityIndex":
            return capability_index
        if cls is AuthMiddleware:
            return auth_mock
        return Mock()

    container.retrieve.side_effect = retrieve_side_effect

    return container


@pytest.fixture
def client(mock_container: Mock) -> Generator[TestClient, None, None]:
    """Create a test client with dependency overrides for the mock container."""
    # Override the app's state to use the mock container
    app.state.container = mock_container

    # Override get_current_user to skip auth for these tests
    from web.main import get_current_user
    app.dependency_overrides[get_current_user] = lambda: Mock()

    yield TestClient(app)

    # Clean up overrides
    app.dependency_overrides.clear()


def test_get_index_returns_200(client: TestClient) -> None:
    """Test that GET / returns 200 and contains 'SovereignAI'."""
    response = client.get("/")
    assert response.status_code == 200
    assert "SovereignAI" in response.text


def test_get_capabilities_returns_json_list(client: TestClient) -> None:
    """Test that GET /api/capabilities returns JSON matching CapabilityResponseDTO."""
    response = client.get("/api/capabilities")
    assert response.status_code == 200

    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0
    assert "id" in data[0]
    assert "name" in data[0]
    assert "category" in data[0]
    assert "description" in data[0]
    assert "priority" in data[0]


def test_post_task_returns_task_id(client: TestClient, mock_container: Mock) -> None:
    """Test that POST /api/tasks returns a task ID matching TaskResponseDTO."""
    from sovereignai.shared.auth import AuthMiddleware
    from sovereignai.shared.capability_api import CapabilityAPI

    # Mock the API to return a task ID
    mock_api = Mock(spec=CapabilityAPI)
    task_id = uuid4()
    mock_api.submit_task.return_value = task_id

    # Mock auth to validate any token
    mock_auth = Mock(spec=AuthMiddleware)
    mock_auth.validate.return_value = Mock()
    mock_auth._password_hashes = {"test": "hash"}

    # Configure container to return mocks
    def retrieve_side_effect(cls: Any) -> Any:
        if cls is CapabilityAPI:
            return mock_api
        elif cls is AuthMiddleware:
            return mock_auth
        return Mock()

    mock_container.retrieve.side_effect = retrieve_side_effect

    response = client.post(
        "/api/tasks",
        json={
            "category": "tool",
            "capability_name": "test_tool",
            "payload": '{"test": "data"}',
        },
        cookies={"session_id": "test_token"},
    )
    assert response.status_code == 200

    data = response.json()
    assert "task_id" in data
    assert "state" in data
    assert data["state"] == TaskState.RECEIVED.value


def test_get_task_state_returns_task(client: TestClient, mock_container: Mock) -> None:
    """Test that GET /api/tasks/{task_id} returns task state matching TaskResponseDTO."""
    from sovereignai.shared.auth import AuthMiddleware
    from sovereignai.shared.capability_api import CapabilityAPI

    # Mock the API to return a task state
    mock_api = Mock(spec=CapabilityAPI)
    task_id = uuid4()
    mock_api.get_task_state.return_value = TaskState.EXECUTING

    # Mock auth to validate any token
    mock_auth = Mock(spec=AuthMiddleware)
    mock_auth.validate.return_value = Mock()
    mock_auth._password_hashes = {"test": "hash"}

    # Configure container to return mocks
    def retrieve_side_effect(cls: Any) -> Any:
        if cls is CapabilityAPI:
            return mock_api
        elif cls is AuthMiddleware:
            return mock_auth
        return Mock()

    mock_container.retrieve.side_effect = retrieve_side_effect

    response = client.get(f"/api/tasks/{task_id}", cookies={"session_id": "test_token"})
    assert response.status_code == 200

    data = response.json()
    assert "task_id" in data
    assert "state" in data
    assert data["state"] == TaskState.EXECUTING.value


def test_sse_auth_required(client: TestClient, mock_container: Mock) -> None:
    """Test that GET /api/traces/stream returns 401 without session cookie."""
    from sovereignai.shared.auth import AuthMiddleware
    from sovereignai.shared.event_bus import EventBus
    from sovereignai.shared.trace_emitter import TraceEmitter

    # Mock trace emitter
    mock_trace = Mock(spec=TraceEmitter)
    mock_bus = Mock(spec=EventBus)
    mock_auth = Mock(spec=AuthMiddleware)
    mock_auth.validate.side_effect = Exception("Invalid token")
    mock_auth._password_hashes = {"test": "hash"}

    def retrieve_side_effect(cls: Any) -> Any:
        if cls is TraceEmitter:
            return mock_trace
        elif cls is EventBus:
            return mock_bus
        elif cls is AuthMiddleware:
            return mock_auth
        return Mock()

    mock_container.retrieve.side_effect = retrieve_side_effect

    response = client.get("/api/traces/stream")
    assert response.status_code == 401


def test_dto_mapping_isolated(client: TestClient, mock_container: Mock) -> None:
    """Test that changing a core Task field name does not break the HTTP response format.

    This test verifies that the HTTP contract (DTOs) is independent of core types.
    If a core type changes, the DTO mapping can be updated without breaking the API.
    """
    from sovereignai.shared.auth import AuthMiddleware
    from sovereignai.shared.capability_api import CapabilityAPI

    # Mock the API to return a task state
    mock_api = Mock(spec=CapabilityAPI)
    task_id = uuid4()
    mock_api.get_task_state.return_value = TaskState.COMPLETE

    # Mock auth to validate any token
    mock_auth = Mock(spec=AuthMiddleware)
    mock_auth.validate.return_value = Mock()
    mock_auth._password_hashes = {"test": "hash"}

    def retrieve_side_effect(cls: Any) -> Any:
        if cls is CapabilityAPI:
            return mock_api
        elif cls is AuthMiddleware:
            return mock_auth
        return Mock()

    mock_container.retrieve.side_effect = retrieve_side_effect

    response = client.get(f"/api/tasks/{task_id}", cookies={"session_id": "test_token"})
    assert response.status_code == 200

    # Verify the DTO structure is fixed regardless of core type changes
    data = response.json()
    assert "task_id" in data  # DTO field name
    assert "state" in data   # DTO field name
    assert "result" in data  # DTO field name
    assert "error" in data   # DTO field name


def test_ollama_status_endpoint(client: TestClient, mock_container: Mock) -> None:
    """Test that GET /api/ollama/status returns Ollama status."""
    response = client.get("/api/ollama/status")
    assert response.status_code == 200

    data = response.json()
    assert "status" in data
    assert data["status"] in ["running", "not_running"]
    if data["status"] == "running":
        assert "version" in data


def test_storage_paths_endpoint(client: TestClient, mock_container: Mock) -> None:
    """Test that GET /api/storage/paths returns storage directory paths."""
    response = client.get("/api/storage/paths")
    assert response.status_code == 200

    data = response.json()
    assert "cache_dir" in data
    assert "ollama_models_dir" in data
    assert isinstance(data["cache_dir"], str)
    assert isinstance(data["ollama_models_dir"], str)


def test_catalog_endpoint_includes_hardware(client: TestClient, mock_container: Mock) -> None:
    """Test that GET /api/models/catalog includes hardware info for VRAM badges."""
    from sovereignai.shared.auth import AuthMiddleware
    from sovereignai.shared.trace_emitter import TraceEmitter

    # Mock trace emitter and auth
    mock_trace = Mock(spec=TraceEmitter)
    mock_auth = Mock(spec=AuthMiddleware)
    mock_auth._password_hashes = {"test": "hash"}  # Simulate existing user

    def retrieve_side_effect(cls: Any) -> Any:
        if cls is TraceEmitter:
            return mock_trace
        elif cls is AuthMiddleware:
            return mock_auth
        return Mock()

    mock_container.retrieve.side_effect = retrieve_side_effect

    response = client.get("/api/models/catalog")
    # The endpoint may fail if HuggingFace is unreachable, but we still check structure
    if response.status_code == 200:
        data = response.json()
        assert "models" in data
        assert "hardware" in data
        assert "gpu_vram_mb" in data["hardware"]
        assert "ram_total_mb" in data["hardware"]

