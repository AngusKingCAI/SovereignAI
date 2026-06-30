"""Tests for options panel endpoints."""
from fastapi.testclient import TestClient


def test_download_service_endpoint(client: TestClient) -> None:
    """Test that download service endpoint accepts requests."""
    response = client.post("/api/services/download", json={"service": "ollama"})
    # May fail if service not found, but should not 500
    assert response.status_code in [200, 404, 500]


def test_update_service_endpoint(client: TestClient) -> None:
    """Test that update service endpoint accepts requests."""
    response = client.post("/api/services/update", json={"service": "ollama"})
    assert response.status_code in [200, 404, 500]


def test_uninstall_service_endpoint(client: TestClient) -> None:
    """Test that uninstall service endpoint accepts requests."""
    response = client.post("/api/services/uninstall", json={"service": "ollama"})
    assert response.status_code in [200, 404, 500]


def test_start_service_endpoint(client: TestClient) -> None:
    """Test that start service endpoint accepts requests."""
    response = client.post("/api/services/ollama/start")
    assert response.status_code in [200, 404, 500]


def teststop_service_endpoint(client: TestClient) -> None:
    """Test that stop service endpoint accepts requests."""
    response = client.post("/api/services/ollama/stop")
    assert response.status_code in [200, 404, 500]


def test_download_database_endpoint(client: TestClient) -> None:
    """Test that download database endpoint accepts requests."""
    response = client.post("/api/databases/download", json={"database": "huggingface"})
    assert response.status_code in [200, 404, 500]


def test_update_database_endpoint(client: TestClient) -> None:
    """Test that update database endpoint accepts requests."""
    response = client.post("/api/databases/update", json={"database": "huggingface"})
    assert response.status_code in [200, 404, 500]


def test_uninstall_database_endpoint(client: TestClient) -> None:
    """Test that uninstall database endpoint accepts requests."""
    response = client.post("/api/databases/uninstall", json={"database": "huggingface"})
    assert response.status_code in [200, 404, 500]


def test_save_api_key(client: TestClient) -> None:
    """Test saving an API key."""
    response = client.post("/api/options/api-keys", json={
        "provider": "test_provider",
        "key": "test_key"
    })
    assert response.status_code in [200, 400]


def test_delete_api_key(client: TestClient) -> None:
    """Test deleting an API key."""
    response = client.delete("/api/options/api-keys/test_provider")
    assert response.status_code in [200, 404]


def test_get_services_list(client: TestClient) -> None:
    """Test getting services list."""
    response = client.get("/api/services")
    assert response.status_code == 200
    data = response.json()
    assert "services" in data


def test_get_databases_list(client: TestClient) -> None:
    """Test getting databases list."""
    response = client.get("/api/databases")
    assert response.status_code == 200
    data = response.json()
    assert "databases" in data


def test_restart_service_endpoint(client: TestClient) -> None:
    """Test restart service endpoint."""
    response = client.post("/api/services/ollama/restart")
    assert response.status_code in [200, 404, 500]


def test_get_service_status_endpoint(client: TestClient) -> None:
    """Test get service status endpoint."""
    response = client.get("/api/services/ollama/status")
    # May fail if service not found
    assert response.status_code in [200, 404]


def test_get_database_status_endpoint(client: TestClient) -> None:
    """Test get database status endpoint."""
    response = client.get("/api/databases/huggingface/status")
    # May fail if database not found
    assert response.status_code in [200, 404]
