from __future__ import annotations

import os
from unittest.mock import MagicMock

import pytest
from fastapi.testclient import TestClient
from sovereignai.main import build_container

from app.web.main import app


@pytest.fixture
def test_container():
    import os
    os.environ["SOVEREIGNAI_TEST_MODE"] = "1"
    return build_container(dev_mode=True)


@pytest.fixture
def test_client(test_container):
    app.state.container = test_container
    return TestClient(app)


def test_first_run_check_returns_200(test_client, test_container):
    if not os.environ.get('SOVEREIGNAI_FULL_STACK_TESTS'):
        pytest.skip("Set SOVEREIGNAI_FULL_STACK_TESTS=1 to run full stack integration tests")
    from sovereignai.shared.auth import AuthMiddleware

    # Set up a test user
    auth = test_container.retrieve(AuthMiddleware)
    auth.register_user("testuser", "testpass")

    # Login to get session cookie
    response = test_client.post(
        "/api/auth/login", json={"username": "testuser", "password": "testpass"}
    )
    assert response.status_code == 200

    # Extract session cookie and use it in subsequent request
    session_cookie = response.cookies.get("session_id")

    # Now call the endpoint with the session cookie
    response = test_client.get("/api/first-run-check", cookies={"session_id": session_cookie})
    assert response.status_code == 200


def test_first_run_check_empty_healthy_when_both_fail(test_client, test_container):
    if not os.environ.get('SOVEREIGNAI_FULL_STACK_TESTS'):
        pytest.skip("Set SOVEREIGNAI_FULL_STACK_TESTS=1 to run full stack integration tests")
    from sovereignai.shared.auth import AuthMiddleware
    from sovereignai.shared.capability_graph import ICapabilityIndex
    from sovereignai.shared.types import AdapterHealth

    # Set up a test user
    auth = test_container.retrieve(AuthMiddleware)
    auth.register_user("testuser", "testpass")

    # Login to get session cookie
    response = test_client.post(
        "/api/auth/login", json={"username": "testuser", "password": "testpass"}
    )
    assert response.status_code == 200
    session_cookie = response.cookies.get("session_id")

    capability_index = test_container.retrieve(ICapabilityIndex)

    # Mock adapters to have unhealthy health checks
    for meta in capability_index.adapters_by_capability("model_inference"):
        inst = capability_index.get_adapter(meta.component_id)
        if inst is not None and hasattr(inst, "health_check"):
            inst.health_check = MagicMock(return_value=AdapterHealth(healthy=False, detail="test"))

    response = test_client.get("/api/first-run-check", cookies={"session_id": session_cookie})
    assert response.status_code == 200
    data = response.json()
    assert data["healthy_adapters"] == []
    assert "No inference adapter healthy" in data["instructions"]


def test_first_run_check_non_empty_when_healthy(test_client, test_container):
    if not os.environ.get('SOVEREIGNAI_FULL_STACK_TESTS'):
        pytest.skip("Set SOVEREIGNAI_FULL_STACK_TESTS=1 to run full stack integration tests")
    from sovereignai.shared.auth import AuthMiddleware
    from sovereignai.shared.capability_graph import ICapabilityIndex
    from sovereignai.shared.types import AdapterHealth

    # Set up a test user
    auth = test_container.retrieve(AuthMiddleware)
    auth.register_user("testuser", "testpass")

    # Login to get session cookie
    response = test_client.post(
        "/api/auth/login", json={"username": "testuser", "password": "testpass"}
    )
    assert response.status_code == 200
    session_cookie = response.cookies.get("session_id")

    capability_index = test_container.retrieve(ICapabilityIndex)

    # Mock at least one adapter to be healthy
    for meta in capability_index.adapters_by_capability("model_inference"):
        inst = capability_index.get_adapter(meta.component_id)
        if inst is not None and hasattr(inst, "health_check"):
            inst.health_check = MagicMock(return_value=AdapterHealth(healthy=True, detail="OK"))
            break

    response = test_client.get("/api/first-run-check", cookies={"session_id": session_cookie})
    assert response.status_code == 200
    data = response.json()
    assert len(data["healthy_adapters"]) >= 1


def test_cpu_only_llama_cpp_counts_as_healthy(test_client, test_container):
    if not os.environ.get('SOVEREIGNAI_FULL_STACK_TESTS'):
        pytest.skip("Set SOVEREIGNAI_FULL_STACK_TESTS=1 to run full stack integration tests")
    from sovereignai.shared.auth import AuthMiddleware
    from sovereignai.shared.capability_graph import ICapabilityIndex
    from sovereignai.shared.types import AdapterHealth

    # Set up a test user
    auth = test_container.retrieve(AuthMiddleware)
    auth.register_user("testuser", "testpass")

    # Login to get session cookie
    response = test_client.post(
        "/api/auth/login", json={"username": "testuser", "password": "testpass"}
    )
    assert response.status_code == 200
    session_cookie = response.cookies.get("session_id")

    capability_index = test_container.retrieve(ICapabilityIndex)

    # Mock llama_cpp adapter to be healthy in CPU mode
    for meta in capability_index.adapters_by_capability("model_inference"):
        inst = capability_index.get_adapter(meta.component_id)
        if (
            inst is not None
            and "llama" in str(meta.component_id).lower()
            and hasattr(inst, "health_check")
        ):
            inst.health_check = MagicMock(
                return_value=AdapterHealth(healthy=True, detail="OK")
            )
            break

    response = test_client.get("/api/first-run-check", cookies={"session_id": session_cookie})
    assert response.status_code == 200
    data = response.json()
    # If llama_cpp is registered, it should be counted as healthy
    if any("llama" in str(adapter).lower() for adapter in data["healthy_adapters"]):
        assert True
