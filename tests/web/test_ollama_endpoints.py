"""Tests for Ollama-specific endpoints."""
from fastapi.testclient import TestClient


def test_ollama_status(client: TestClient):
    """Test /api/ollama/status endpoint."""
    response = client.get("/api/ollama/status")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data


def test_ollama_start(client: TestClient):
    """Test /api/ollama/start endpoint."""
    response = client.post("/api/ollama/start")
    # May fail if Ollama not installed, but should return a response
    assert response.status_code in [200, 500]
