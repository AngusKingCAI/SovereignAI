from __future__ import annotations

import os

import pytest
from fastapi.testclient import TestClient
from sovereignai.main import build_container

from app.web.main import app


@pytest.fixture
def client() -> TestClient:
    container = build_container()
    app.state.container = container
    return TestClient(app)


@pytest.fixture
def container(client: TestClient):
    return client.app.state.container  # type: ignore[attr-defined]


def test_events_types_requires_auth(client: TestClient) -> None:
    if not os.environ.get("SOVEREIGNAI_FULL_STACK_TESTS"):
        pytest.skip("Set SOVEREIGNAI_FULL_STACK_TESTS=1 to run")

    response = client.get("/api/events/types")
    assert response.status_code == 401


def test_events_subscriptions_requires_auth(client: TestClient) -> None:
    if not os.environ.get("SOVEREIGNAI_FULL_STACK_TESTS"):
        pytest.skip("Set SOVEREIGNAI_FULL_STACK_TESTS=1 to run")

    response = client.get("/api/events/subscriptions")
    assert response.status_code == 401


def test_events_types_returns_list(client: TestClient, container) -> None:
    if not os.environ.get("SOVEREIGNAI_FULL_STACK_TESTS"):
        pytest.skip("Set SOVEREIGNAI_FULL_STACK_TESTS=1 to run")

    from sovereignai.shared.auth import AuthMiddleware

    auth = container.retrieve(AuthMiddleware)
    auth.register_user("testuser", "testpass")
    session = auth.login("testuser", "testpass")

    client.cookies.set("session_id", session.token)

    response = client.get("/api/events/types")
    assert response.status_code == 200
    data = response.json()
    assert "event_types" in data
    assert isinstance(data["event_types"], list)


def test_events_subscriptions_returns_list(client: TestClient, container) -> None:
    if not os.environ.get("SOVEREIGNAI_FULL_STACK_TESTS"):
        pytest.skip("Set SOVEREIGNAI_FULL_STACK_TESTS=1 to run")

    from sovereignai.shared.auth import AuthMiddleware

    auth = container.retrieve(AuthMiddleware)
    auth.register_user("testuser", "testpass")
    session = auth.login("testuser", "testpass")

    client.cookies.set("session_id", session.token)

    response = client.get("/api/events/subscriptions")
    assert response.status_code == 200
    data = response.json()
    assert "subscriptions" in data
    assert isinstance(data["subscriptions"], list)
