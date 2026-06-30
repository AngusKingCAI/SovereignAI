"""Tests for traces endpoints."""
from fastapi.testclient import TestClient


def test_get_traces_endpoint(client: TestClient) -> None:
    """Test that traces endpoint returns trace events."""
    response = client.get("/api/traces")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


def test_get_traces_with_filters(client: TestClient) -> None:
    """Test that traces endpoint accepts filters."""
    response = client.get("/api/traces?level=info&limit=10")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


def test_get_traces_for_task(client: TestClient) -> None:
    """Test that traces for task endpoint returns events."""
    response = client.get("/api/traces/test-task-id")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


def test_get_installed_models(client: TestClient) -> None:
    """Test that installed models endpoint returns models."""
    response = client.get("/api/models/installed")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


def test_get_model_catalog(client: TestClient) -> None:
    """Test that model catalog endpoint returns models."""
    response = client.get("/api/models/catalog")
    assert response.status_code == 200
    data = response.json()
    assert "models" in data
    assert "total" in data
