from __future__ import annotations

from unittest.mock import MagicMock

import pytest
from fastapi.testclient import TestClient

from app.web.routes.trace import health_router, set_dependencies


@pytest.fixture
def client():
    from fastapi import FastAPI
    app = FastAPI()
    app.include_router(health_router)
    return TestClient(app)


@pytest.fixture
def mock_health_aggregator():
    aggregator = MagicMock()
    aggregator.get_health_status.return_value = {
        "status": "healthy",
        "components": {},
        "cache_age_ms": 100,
    }
    return aggregator


@pytest.fixture
def mock_lifecycle_manager():
    manager = MagicMock()
    from sovereignai.lifecycle.types import LifecycleState
    manager.state = LifecycleState.READY
    return manager


def test_ready_no_cookie_returns_dto(client, mock_lifecycle_manager):
    set_dependencies(lifecycle_manager_dep=mock_lifecycle_manager)
    
    response = client.get("/api/lifecycle/ready")
    
    assert response.status_code == 200
    data = response.json()
    assert "ready" in data
    assert "state" in data


def test_ready_during_drain_returns_false(client, mock_lifecycle_manager):
    from sovereignai.lifecycle.types import LifecycleState
    mock_lifecycle_manager.state = LifecycleState.SHUTTING_DOWN
    
    set_dependencies(lifecycle_manager_dep=mock_lifecycle_manager)
    
    response = client.get("/api/lifecycle/ready")
    
    assert response.status_code == 200
    data = response.json()
    assert data["ready"] is False


def test_ready_before_startup_completes(client, mock_lifecycle_manager):
    from sovereignai.lifecycle.types import LifecycleState
    mock_lifecycle_manager.state = LifecycleState.INITIALIZING
    
    set_dependencies(lifecycle_manager_dep=mock_lifecycle_manager)
    
    response = client.get("/api/lifecycle/ready")
    
    assert response.status_code == 200
    data = response.json()
    assert data["ready"] is False


def test_health_endpoint(client, mock_health_aggregator):
    set_dependencies(health_aggregator_dep=mock_health_aggregator)
    
    response = client.get("/api/health")
    
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert "components" in data
    assert "cache_age_ms" in data
