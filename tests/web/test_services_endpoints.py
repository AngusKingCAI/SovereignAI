"""Tests for services and databases endpoints."""
from fastapi.testclient import TestClient


def test_get_hardware_endpoint(client: TestClient) -> None:
    """Test that hardware endpoint returns hardware info."""
    response = client.get("/api/hardware")
    assert response.status_code == 200
    data = response.json()
    assert "cpu_count" in data
    assert "ram_total_mb" in data


def test_get_model_detail_endpoint(client: TestClient) -> None:
    """Test that model detail endpoint returns model info."""
    response = client.get("/api/models/catalog/test-model-id")
    assert response.status_code == 200
    data = response.json()
    assert "model_id" in data
    assert "files" in data
