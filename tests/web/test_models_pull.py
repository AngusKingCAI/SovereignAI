"""Tests for models pull endpoint."""
from fastapi.testclient import TestClient


def test_pull_model_requires_model_param(client: TestClient) -> None:
    """Test that pull endpoint requires model parameter."""
    response = client.post("/api/models/pull", json={})
    assert response.status_code == 400
    assert "model is required" in response.json()["detail"]


def test_pull_model_with_valid_request(client: TestClient) -> None:
    """Test that pull endpoint accepts valid request."""
    response = client.post("/api/models/pull", json={"model": "test-org/test-model", "quant": "Q4_K_M"})
    # Should return 200 (status is tracked in-memory)
    assert response.status_code == 200


def test_pull_status_endpoint(client: TestClient) -> None:
    """Test that pull status endpoint returns status."""
    response = client.get("/api/models/pull-status?model=test-model")
    assert response.status_code == 200
    data = response.json()
    # Status is keyed by model name
    assert isinstance(data, dict)
