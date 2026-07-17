from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from web.main import app


@pytest.mark.skip(reason="Requires full FastAPI container setup")
def test_list_endpoint_returns_correct_dto() -> None:
    with TestClient(app) as client:
        # First, we need to authenticate
        response = client.post(
            "/api/auth/register",
            json={"username": "testuser", "password": "testpass"},
        )
        assert response.status_code == 200

        response = client.post(
            "/api/auth/login",
            json={"username": "testuser", "password": "testpass"},
        )
        assert response.status_code == 200

        # Now test the skills endpoint
        response = client.get("/api/skills")
        assert response.status_code == 200

        data = response.json()
        assert "skills" in data
        assert isinstance(data["skills"], list)


@pytest.mark.skip(reason="Requires full FastAPI container setup")
def test_execute_endpoint_with_mock_skill() -> None:
    with TestClient(app) as client:
        # Authenticate
        response = client.post(
            "/api/auth/register",
            json={"username": "testuser", "password": "testpass"},
        )
        assert response.status_code == 200

        response = client.post(
            "/api/auth/login",
            json={"username": "testuser", "password": "testpass"},
        )
        assert response.status_code == 200

        # Test execute endpoint (may fail if skill not registered)
        response = client.post(
            "/api/skills/file_read/execute",
            json={"skill_id": "file_read", "args": {"path": "test.txt"}},
        )
        # May return 404 or 500 if skill not found, but should not be 401 (auth)
        assert response.status_code != 401


@pytest.mark.skip(reason="Requires full FastAPI container setup")
def test_auth_rejection_without_cookie() -> None:
    with TestClient(app) as client:
        # Test without authentication
        response = client.get("/api/skills")
        assert response.status_code == 401

        response = client.post(
            "/api/skills/file_read/execute",
            json={"skill_id": "file_read", "args": {}},
        )
        assert response.status_code == 401
