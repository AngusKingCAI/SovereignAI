"""Tests for authentication endpoints."""
from fastapi.testclient import TestClient


def test_logout(client: TestClient):
    """Test /api/auth/logout endpoint."""
    response = client.post("/api/auth/logout")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "logged_out"


def test_get_capabilities(client: TestClient):
    """Test /api/capabilities endpoint."""
    response = client.get("/api/capabilities")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


def test_get_workers(client: TestClient):
    """Test /api/workers endpoint."""
    response = client.get("/api/workers")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


def test_get_tasks(client: TestClient):
    """Test /api/tasks endpoint."""
    response = client.get("/api/tasks")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


def test_get_hardware(client: TestClient):
    """Test /api/hardware endpoint."""
    response = client.get("/api/hardware")
    assert response.status_code == 200
    data = response.json()
    assert "cpu_count" in data
    assert "ram_total_mb" in data


def test_get_storage_paths(client: TestClient):
    """Test /api/storage/paths endpoint."""
    response = client.get("/api/storage/paths")
    assert response.status_code == 200
    data = response.json()
    assert "cache_dir" in data


def test_get_options_config(client: TestClient):
    """Test /api/options/config endpoint."""
    response = client.get("/api/options/config")
    assert response.status_code == 200
    data = response.json()
    assert "api_keys" in data
    assert "ollama_host" in data
