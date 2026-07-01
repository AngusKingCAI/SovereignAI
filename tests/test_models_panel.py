from __future__ import annotations

from typing import Any

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
