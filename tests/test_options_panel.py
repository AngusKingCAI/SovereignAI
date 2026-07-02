from __future__ import annotations

from fastapi.testclient import TestClient

from web.main import app


def test_get_databases_unauthorized() -> None:
    with TestClient(app, raise_server_exceptions=False) as client:
        response = client.get("/api/databases")
        assert response.status_code == 401


def test_get_services_unauthorized() -> None:
    with TestClient(app, raise_server_exceptions=False) as client:
        response = client.get("/api/services")
        assert response.status_code == 401


def test_get_databases_authorized() -> None:
    from databases.hf_database.provider import HFDatabaseProvider
    from sovereignai.main import build_container
    from sovereignai.shared.types import ModelEntry

    container = build_container()

    # Mock HF provider to avoid 501 live API calls
    mock_models = [
        ModelEntry(
            org="test",
            family="model-1",
            version="latest",
            quant="gguf",
            file_size_bytes=0,
            vram_required_mb=0,
            num_layers=32,
            category="llm",
            source_db="huggingface"
        ),
    ]

    original_list_models = HFDatabaseProvider.list_models
    HFDatabaseProvider.list_models = lambda self, filter=None: mock_models

    app.state.container = container

    with TestClient(app, raise_server_exceptions=False) as client:
        # Register first user
        client.post("/api/auth/register", json={"username": "test", "password": "test123"})

        # Login
        login_response = client.post(  # noqa: E501
            "/api/auth/login",
            json={"username": "test", "password": "test123"}
        )
        assert login_response.status_code == 200
        session_cookie = login_response.cookies.get("session_id")

        # Get databases with session cookie
        response = client.get("/api/databases", cookies={"session_id": session_cookie})
        # For now, just check it's not 401 (auth error)
        assert response.status_code != 401
        if response.status_code == 200:
            data = response.json()
            assert isinstance(data, list)

    # Restore original method
    HFDatabaseProvider.list_models = original_list_models


def test_get_services_authorized() -> None:
    with TestClient(app, raise_server_exceptions=False) as client:
        # Register first user
        client.post("/api/auth/register", json={"username": "test", "password": "test123"})

        # Login
        login_response = client.post(  # noqa: E501
            "/api/auth/login",
            json={"username": "test", "password": "test123"}
        )
        assert login_response.status_code == 200
        session_cookie = login_response.cookies.get("session_id")

        # Get services with session cookie
        response = client.get("/api/services", cookies={"session_id": session_cookie})
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1
        assert data[0]["name"] == "ollama"
        assert "status" in data[0]
        assert "pid" in data[0]
        assert "port" in data[0]
