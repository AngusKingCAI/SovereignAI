"""Tests for memory API endpoints via Orchestrator facade.

Tests verify API exposure (AR1 compliant) with proper DTO handling and
503 responses when MemoryGateway is not ready.
"""
from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock

import pytest
from fastapi.testclient import TestClient

from app.web.routes.orchestrator import router


@pytest.fixture
def mock_orchestrator_facade() -> MagicMock:
    """Mock orchestrator facade."""
    facade = MagicMock()
    facade.handle_memory_request = AsyncMock(return_value={"status": "ok"})
    return facade


@pytest.fixture
def mock_memory_gateway() -> MagicMock:
    """Mock memory gateway."""
    gateway = MagicMock()
    gateway.is_ready = MagicMock(return_value=True)
    return gateway


@pytest.fixture
def client(mock_orchestrator_facade: MagicMock, mock_memory_gateway: MagicMock) -> TestClient:
    """Test client with mocked dependencies."""
    # Override global dependencies
    import app.web.routes.orchestrator as routes_module
    routes_module.orchestrator_facade = mock_orchestrator_facade
    routes_module.memory_gateway = mock_memory_gateway

    from fastapi import FastAPI
    app = FastAPI()
    app.include_router(router)
    return TestClient(app)


def test_graph_query_returns_dto(client: TestClient, mock_orchestrator_facade: MagicMock) -> None:
    """Test graph query returns proper DTO structure."""
    mock_orchestrator_facade.handle_memory_request.return_value = {
        "entities": [
            {
                "id": "entity1",
                "type": "Person",
                "name": "Alice",
                "attributes": {"age": 30},
            }
        ]
    }

    response = client.get("/api/orchestrator/memory/graph?entity_id=entity1")

    assert response.status_code == 200
    data = response.json()
    assert "entities" in data
    assert len(data["entities"]) == 1
    assert data["entities"][0]["id"] == "entity1"
    assert data["entities"][0]["type"] == "Person"


def test_memory_not_ready_503(client: TestClient, mock_memory_gateway: MagicMock) -> None:
    """Test memory endpoint returns 503 when not ready."""
    # Mock memory gateway as not ready
    mock_memory_gateway.is_ready = MagicMock(return_value=False)

    response = client.get("/api/orchestrator/memory/test")

    assert response.status_code == 503
    assert "Retry-After" in response.headers
    assert response.headers["Retry-After"] == "5"
    assert "memory_not_ready" in str(response.content)


def test_conflicts_sorted_fresh_first(
    client: TestClient, mock_orchestrator_facade: MagicMock
) -> None:
    """Test conflicts endpoint returns conflicts sorted by first_observed_at descending."""
    mock_orchestrator_facade.handle_memory_request.return_value = {
        "conflicts": [
            {
                "conflict_id": "conflict1",
                "entity_name": "Alice",
                "entity_type": "Person",
                "canonical_uuid": "uuid1",
                "candidate_uuids": ["uuid2", "uuid3"],
                "first_observed_at": "2024-01-02T00:00:00Z",
                "resolution_status": "unresolved",
            },
            {
                "conflict_id": "conflict2",
                "entity_name": "Bob",
                "entity_type": "Person",
                "canonical_uuid": "uuid4",
                "candidate_uuids": ["uuid5"],
                "first_observed_at": "2024-01-01T00:00:00Z",
                "resolution_status": "unresolved",
            },
        ]
    }

    response = client.get("/api/orchestrator/memory/conflicts")

    assert response.status_code == 200
    data = response.json()
    assert "conflicts" in data
    # Verify sorted by first_observed_at descending
    assert data["conflicts"][0]["first_observed_at"] >= data["conflicts"][1]["first_observed_at"]


def test_episodic_time_range_filter(
    client: TestClient, mock_orchestrator_facade: MagicMock
) -> None:
    """Test episodic endpoint with time range filter."""
    mock_orchestrator_facade.handle_memory_request.return_value = {
        "events": [
            {
                "id": 1,
                "event_type": "task.completed",
                "timestamp": "2024-01-02T00:00:00Z",
                "correlation_id": "corr1",
                "summary": "Task completed",
            }
        ]
    }

    response = client.get(
        "/api/orchestrator/memory/episodic?since=2024-01-01T00:00:00Z&until=2024-01-03T00:00:00Z"
    )

    assert response.status_code == 200
    data = response.json()
    assert "events" in data
    assert len(data["events"]) == 1


def test_conflicts_pagination_offset_limit(
    client: TestClient, mock_orchestrator_facade: MagicMock
) -> None:
    """Test conflicts endpoint with offset/limit pagination."""
    mock_orchestrator_facade.handle_memory_request.return_value = {
        "conflicts": [
            {
                "conflict_id": f"conflict{i}",
                "entity_name": f"Entity{i}",
                "entity_type": "Person",
                "canonical_uuid": f"uuid{i}",
                "candidate_uuids": [],
                "first_observed_at": "2024-01-01T00:00:00Z",
                "resolution_status": "unresolved",
            }
            for i in range(10, 20)  # Return conflicts 10-19
        ],
        "total": 100,
        "offset": 10,
        "limit": 10,
    }

    response = client.get("/api/orchestrator/memory/conflicts?offset=10&limit=10")

    assert response.status_code == 200
    data = response.json()
    assert "conflicts" in data
    assert len(data["conflicts"]) == 10
    assert data["offset"] == 10
    assert data["limit"] == 10
    assert data["total"] == 100


def test_conflicts_max_page_size_500(client: TestClient) -> None:
    """Test conflicts endpoint enforces max page size of 500."""
    # Request larger than max
    response = client.get("/api/orchestrator/memory/conflicts?limit=1000")

    # Should return 400 for invalid limit
    assert response.status_code == 400


def test_conflicts_stable_ordering(client: TestClient, mock_orchestrator_facade: MagicMock) -> None:
    """Test conflicts endpoint returns stable ordering."""
    # First request
    mock_orchestrator_facade.handle_memory_request.return_value = {
        "conflicts": [
            {
                "conflict_id": "conflict1",
                "entity_name": "Alice",
                "entity_type": "Person",
                "canonical_uuid": "uuid1",
                "candidate_uuids": ["uuid2"],
                "first_observed_at": "2024-01-01T00:00:00Z",
                "resolution_status": "unresolved",
            }
        ]
    }

    response1 = client.get("/api/orchestrator/memory/conflicts")
    data1 = response1.json()

    # Second request should return same order
    response2 = client.get("/api/orchestrator/memory/conflicts")
    data2 = response2.json()

    assert data1["conflicts"][0]["conflict_id"] == data2["conflicts"][0]["conflict_id"]


def test_conflicts_resolution_status_dto_valid(
    client: TestClient, mock_orchestrator_facade: MagicMock
) -> None:
    """Test conflicts endpoint returns valid resolution_status field."""
    mock_orchestrator_facade.handle_memory_request.return_value = {
        "conflicts": [
            {
                "conflict_id": "conflict1",
                "entity_name": "Alice",
                "entity_type": "Person",
                "canonical_uuid": "uuid1",
                "candidate_uuids": ["uuid2"],
                "first_observed_at": "2024-01-01T00:00:00Z",
                "resolution_status": "unresolved",
            },
            {
                "conflict_id": "conflict2",
                "entity_name": "Bob",
                "entity_type": "Person",
                "canonical_uuid": "uuid3",
                "candidate_uuids": ["uuid4"],
                "first_observed_at": "2024-01-01T00:00:00Z",
                "resolution_status": "suppressed_by_dedup",
            },
        ]
    }

    response = client.get("/api/orchestrator/memory/conflicts")

    assert response.status_code == 200
    data = response.json()
    assert "conflicts" in data
    # Verify resolution_status values are valid
    valid_statuses = {"unresolved", "suppressed_by_dedup"}
    for conflict in data["conflicts"]:
        assert conflict["resolution_status"] in valid_statuses
