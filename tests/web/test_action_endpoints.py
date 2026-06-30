"""Tests for service and database action endpoints with success traces."""
from unittest.mock import MagicMock, patch

from fastapi.testclient import TestClient


def test_download_service_success_trace(client: TestClient):
    """Test /api/services/{service_name}/download emits success trace."""
    with patch('sovereignai.services.registry.ServiceRegistry') as mock_registry:
        mock_service_class = MagicMock()
        mock_service = MagicMock()
        mock_service_class.return_value = mock_service
        mock_registry.get.return_value = mock_service_class

        response = client.post("/api/services/ollama/download")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["service"] == "ollama"


def test_update_service_success_trace(client: TestClient):
    """Test /api/services/{service_name}/update emits success trace."""
    with patch('sovereignai.services.registry.ServiceRegistry') as mock_registry:
        mock_service_class = MagicMock()
        mock_service = MagicMock()
        mock_service_class.return_value = mock_service
        mock_registry.get.return_value = mock_service_class

        response = client.post("/api/services/ollama/update")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["service"] == "ollama"


def test_uninstall_service_success_trace(client: TestClient):
    """Test /api/services/{service_name}/uninstall emits success trace."""
    with patch('sovereignai.services.registry.ServiceRegistry') as mock_registry:
        mock_service_class = MagicMock()
        mock_service = MagicMock()
        mock_service_class.return_value = mock_service
        mock_registry.get.return_value = mock_service_class

        response = client.post("/api/services/ollama/uninstall")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["service"] == "ollama"


def test_start_service_success_trace(client: TestClient):
    """Test /api/services/{service_name}/start emits success trace."""
    with patch('sovereignai.services.registry.ServiceRegistry') as mock_registry:
        mock_service_class = MagicMock()
        mock_service = MagicMock()
        mock_status = MagicMock()
        mock_status.running = False
        mock_service.status.return_value = mock_status
        mock_service_class.return_value = mock_service
        mock_registry.get.return_value = mock_service_class

        response = client.post("/api/services/ollama/start")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["service"] == "ollama"


def test_stop_service_success_trace(client: TestClient):
    """Test /api/services/{service_name}/stop emits success trace."""
    with patch('sovereignai.services.registry.ServiceRegistry') as mock_registry:
        mock_service_class = MagicMock()
        mock_service = MagicMock()
        mock_service_class.return_value = mock_service
        mock_registry.get.return_value = mock_service_class

        response = client.post("/api/services/ollama/stop")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["service"] == "ollama"


def test_restart_service_success_trace(client: TestClient):
    """Test /api/services/{service_name}/restart emits success trace."""
    with patch('sovereignai.services.registry.ServiceRegistry') as mock_registry:
        mock_service_class = MagicMock()
        mock_service = MagicMock()
        mock_service_class.return_value = mock_service
        mock_registry.get.return_value = mock_service_class

        response = client.post("/api/services/ollama/restart")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["service"] == "ollama"


def test_download_database_success_trace(client: TestClient):
    """Test /api/databases/{db_name}/download emits success trace."""
    with patch('sovereignai.databases.registry.DatabaseRegistry') as mock_registry:
        mock_db_class = MagicMock()
        mock_db = MagicMock()
        mock_db_class.return_value = mock_db
        mock_registry.get.return_value = mock_db_class

        response = client.post("/api/databases/huggingface/download")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["database"] == "huggingface"


def test_update_database_success_trace(client: TestClient):
    """Test /api/databases/{db_name}/update emits success trace."""
    with patch('sovereignai.databases.registry.DatabaseRegistry') as mock_registry:
        mock_db_class = MagicMock()
        mock_db = MagicMock()
        mock_db_class.return_value = mock_db
        mock_registry.get.return_value = mock_db_class

        response = client.post("/api/databases/huggingface/update")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["database"] == "huggingface"


def test_uninstall_database_success_trace(client: TestClient):
    """Test /api/databases/{db_name}/uninstall emits success trace."""
    with patch('sovereignai.databases.registry.DatabaseRegistry') as mock_registry:
        mock_db_class = MagicMock()
        mock_db = MagicMock()
        mock_db_class.return_value = mock_db
        mock_registry.get.return_value = mock_db_class

        response = client.post("/api/databases/huggingface/uninstall")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["database"] == "huggingface"
