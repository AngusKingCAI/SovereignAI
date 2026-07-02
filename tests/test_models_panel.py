from __future__ import annotations

from collections.abc import Generator
from typing import Any

import pytest
from fastapi.testclient import TestClient

from databases.hf_database.provider import HFDatabaseProvider
from sovereignai.main import build_container
from sovereignai.shared.types import ModelEntry


@pytest.fixture(autouse=True)
def mock_hf_list_models() -> Generator[None, None, None]:
    mock_models = [
        ModelEntry(
            org="test",
            family="model-1",
            version="latest",
            quant="gguf",
            file_size_bytes=0,
            vram_required_mb=0,
            num_layers=32,
            category="llm",
            source_db="huggingface"
        ),
        ModelEntry(
            org="test",
            family="model-2",
            version="latest",
            quant="q4",
            file_size_bytes=4000000000,
            vram_required_mb=4000,
            num_layers=32,
            category="llm",
            source_db="huggingface"
        ),
    ]
    original_list_models = HFDatabaseProvider.list_models
    HFDatabaseProvider.list_models = lambda self, filter=None: mock_models
    yield
    HFDatabaseProvider.list_models = original_list_models


@pytest.fixture
def client() -> TestClient:
    from web.main import app
    container = build_container()
    app.state.container = container
    test_client = TestClient(app)
    yield test_client


@pytest.fixture
def container(client: TestClient) -> Any:
    return client.app.state.container  # type: ignore[attr-defined]


def test_models_endpoint_requires_auth(client: TestClient) -> None:
    response = client.get("/api/models")
    assert response.status_code == 401


def test_models_endpoint_returns_list(client: TestClient, container: Any) -> None:
    from sovereignai.shared.auth import AuthMiddleware
    auth = container.retrieve(AuthMiddleware)
    auth.register_user("testuser", "testpass")
    session = auth.login("testuser", "testpass")

    client.cookies.set("session_id", session.token)

    response = client.get("/api/models")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


def test_models_endpoint_with_filters(client: TestClient, container: Any) -> None:
    from sovereignai.shared.auth import AuthMiddleware
    auth = container.retrieve(AuthMiddleware)
    auth.register_user("testuser", "testpass")
    session = auth.login("testuser", "testpass")

    client.cookies.set("session_id", session.token)

    response = client.get("/api/models?search=llama&category=llm")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


def test_models_endpoint_with_vram_filter(client: TestClient, container: Any) -> None:
    from sovereignai.shared.auth import AuthMiddleware
    auth = container.retrieve(AuthMiddleware)
    auth.register_user("testuser", "testpass")
    session = auth.login("testuser", "testpass")

    client.cookies.set("session_id", session.token)

    response = client.get("/api/models?vram_fit=8000")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


def test_models_endpoint_with_quant_filter(client: TestClient, container: Any) -> None:
    from sovereignai.shared.auth import AuthMiddleware
    auth = container.retrieve(AuthMiddleware)
    auth.register_user("testuser", "testpass")
    session = auth.login("testuser", "testpass")

    client.cookies.set("session_id", session.token)

    response = client.get("/api/models?quant_level=q4")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
