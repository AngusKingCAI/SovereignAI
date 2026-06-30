"""Tests for model catalog endpoints."""
from fastapi.testclient import TestClient


def test_get_installed_models(client: TestClient):
    """Test /api/models/installed endpoint."""
    response = client.get("/api/models/installed")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


def test_get_all_models(client: TestClient):
    """Test /api/models endpoint."""
    response = client.get("/api/models")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert "installed" in data
    assert "providers" in data


def test_get_hierarchical_catalog(client: TestClient):
    """Test /api/models/catalog endpoint."""
    response = client.get("/api/models/catalog?limit=1")
    assert response.status_code == 200
    data = response.json()
    assert "models" in data


def test_get_model_detail(client: TestClient):
    """Test /api/models/catalog/{model_id} endpoint."""
    response = client.get("/api/models/catalog/llama3.2")
    assert response.status_code == 200
    data = response.json()
    assert "model_id" in data


def test_pull_model(client: TestClient):
    """Test /api/models/pull endpoint."""
    response = client.post("/api/models/pull", json={
        "model": "llama3.2",
        "quant": "Q4_K_M"
    })
    assert response.status_code == 200
    data = response.json()
    assert "status" in data


def test_get_pull_status(client: TestClient):
    """Test /api/models/pull-status endpoint."""
    response = client.get("/api/models/pull-status?model=llama3.2")
    assert response.status_code == 200
    data = response.json()
    # The endpoint returns a dict keyed by model_id
    assert isinstance(data, dict)


def test_get_hierarchical_catalog_with_params(client: TestClient):
    """Test /api/models/catalog with search and filter parameters."""
    response = client.get("/api/models/catalog?search=llama&limit=1")
    assert response.status_code == 200
    data = response.json()
    assert "models" in data
