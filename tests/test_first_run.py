from __future__ import annotations

from typing import Any

import pytest
from fastapi.testclient import TestClient

from sovereignai.main import build_container


@pytest.fixture
def client() -> TestClient:
    from web.main import app
    container = build_container()
    app.state.container = container
    return TestClient(app)

@pytest.fixture
def container(client: TestClient) -> Any:
    return client.app.state.container

def test_no_users_redirects_to_register(client: TestClient, container: Any) -> None:
    from sovereignai.shared.auth import AuthMiddleware
    auth = container.retrieve(AuthMiddleware)
    auth._password_hashes.clear()
    response = client.get('/', follow_redirects=False)
    assert response.status_code == 307
    assert response.headers['location'] == '/register'

def test_after_register_redirects_to_login(client: TestClient, container: Any) -> None:
    from sovereignai.shared.auth import AuthMiddleware
    auth = container.retrieve(AuthMiddleware)
    auth.register_user('testuser', 'password123')
    response = client.get('/register', follow_redirects=False)
    assert response.status_code == 307
    assert response.headers['location'] == '/login'

def test_static_files_not_redirected(client: TestClient, container: Any) -> None:
    from sovereignai.shared.auth import AuthMiddleware
    auth = container.retrieve(AuthMiddleware)
    auth._password_hashes.clear()
    response = client.get('/static/styles.css')
    assert response.status_code == 200

def test_api_returns_401_on_first_run(client: TestClient, container: Any) -> None:
    from sovereignai.shared.auth import AuthMiddleware
    auth = container.retrieve(AuthMiddleware)
    auth._password_hashes.clear()
    response = client.get('/api/capabilities')
    assert response.status_code == 401
    assert 'detail' in response.json()

def test_auth_endpoints_allowed_on_first_run(client: TestClient, container: Any) -> None:
    from sovereignai.shared.auth import AuthMiddleware
    auth = container.retrieve(AuthMiddleware)
    auth._password_hashes.clear()
    response = client.post(  # noqa: E501
        '/api/auth/register',
        json={'username': 'newuser', 'password': 'password123'}
    )
    assert response.status_code == 200
    assert response.json() == {'status': 'created'}
