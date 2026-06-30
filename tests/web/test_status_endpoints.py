"""Tests for services and databases status endpoints."""
from unittest.mock import MagicMock, patch

from fastapi.testclient import TestClient


def test_get_service_status(client: TestClient):
    """Test /api/services/{service_name}/status endpoint."""
    with patch('sovereignai.services.registry.ServiceRegistry') as mock_registry:
        mock_service_class = MagicMock()
        mock_service = MagicMock()
        mock_status = MagicMock()
        mock_status.installed = True
        mock_status.running = False
        mock_status.version = "0.1.0"
        mock_status.pid = None
        mock_status.error = None
        mock_service.status.return_value = mock_status
        mock_service_class.return_value = mock_service
        mock_registry.get.return_value = mock_service_class
        mock_registry.list_all.return_value = {"ollama": mock_service_class}

        response = client.get("/api/services/ollama/status")
        assert response.status_code == 200
        data = response.json()
        assert data["installed"] is True
        assert data["running"] is False
        assert data["version"] == "0.1.0"
        assert data["pid"] is None
        assert data["error"] is None


def test_get_service_status_not_found(client: TestClient):
    """Test /api/services/{service_name}/status with non-existent service."""
    with patch('sovereignai.services.registry.ServiceRegistry') as mock_registry:
        mock_registry.get.return_value = None

        response = client.get("/api/services/nonexistent/status")
        assert response.status_code == 404


def test_get_database_status(client: TestClient):
    """Test /api/databases/{db_name}/status endpoint."""
    with patch('sovereignai.databases.registry.DatabaseRegistry') as mock_registry:
        mock_db_class = MagicMock()
        mock_db = MagicMock()
        mock_status = MagicMock()
        mock_status.installed = True
        mock_status.version = "1.0.0"
        mock_status.error = None
        mock_db.status.return_value = mock_status
        mock_db_class.return_value = mock_db
        mock_registry.get.return_value = mock_db_class
        mock_registry.list_all.return_value = {"huggingface": mock_db_class}

        response = client.get("/api/databases/huggingface/status")
        assert response.status_code == 200
        data = response.json()
        assert data["installed"] is True
        assert data["version"] == "1.0.0"
        assert data["error"] is None


def test_get_database_status_not_found(client: TestClient):
    """Test /api/databases/{db_name}/status with non-existent database."""
    with patch('sovereignai.databases.registry.DatabaseRegistry') as mock_registry:
        mock_registry.get.return_value = None

        response = client.get("/api/databases/nonexistent/status")
        assert response.status_code == 404
