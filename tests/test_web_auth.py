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

def test_login_success(client: TestClient, container: Any) -> None:
    from sovereignai.shared.auth import AuthMiddleware
    auth = container.retrieve(AuthMiddleware)
    auth.register_user('testuser', 'testpassword123')
    response = client.post('/api/auth/login', json={'username': 'testuser', 'password': 'testpassword123'})
    assert response.status_code == 200
    assert response.json() == {'status': 'authenticated'}
    assert 'session_id' in response.cookies

def test_login_failure(client: TestClient, container: Any) -> None:
    from sovereignai.shared.auth import AuthMiddleware
    auth = container.retrieve(AuthMiddleware)
    auth.register_user('testuser', 'testpassword123')
    response = client.post('/api/auth/login', json={'username': 'testuser', 'password': 'wrongpassword'})
    assert response.status_code == 401
    assert response.json()['detail'] == 'Invalid credentials'

def test_register_first_run(client: TestClient, container: Any) -> None:
    from sovereignai.shared.auth import AuthMiddleware
    auth = container.retrieve(AuthMiddleware)
    assert len(auth._password_hashes) == 0
    response = client.post('/api/auth/register', json={'username': 'newuser', 'password': 'password123'})
    assert response.status_code == 200
    assert response.json() == {'status': 'created'}
    assert len(auth._password_hashes) == 1

def test_register_after_user_exists(client: TestClient, container: Any) -> None:
    from sovereignai.shared.auth import AuthMiddleware
    auth = container.retrieve(AuthMiddleware)
    auth.register_user('firstuser', 'password123')
    response = client.post('/api/auth/register', json={'username': 'seconduser', 'password': 'password123'})
    assert response.status_code == 403
    assert 'Registration closed' in response.json()['detail']

def test_protected_endpoint_without_cookie(client: TestClient, container: Any) -> None:
    from sovereignai.shared.auth import AuthMiddleware
    auth = container.retrieve(AuthMiddleware)
    auth.register_user('testuser', 'password123')
    response = client.get('/api/capabilities')
    assert response.status_code == 401

def test_protected_endpoint_with_cookie(client: TestClient, container: Any) -> None:
    from sovereignai.shared.auth import AuthMiddleware
    auth = container.retrieve(AuthMiddleware)
    auth.register_user('testuser', 'password123')
    login_response = client.post('/api/auth/login', json={'username': 'testuser', 'password': 'password123'})
    session_cookie = login_response.cookies.get('session_id')
    response = client.get('/api/capabilities', cookies={'session_id': session_cookie or ''})
    assert response.status_code == 200

def test_sse_auth_required(client: TestClient, container: Any) -> None:
    from sovereignai.shared.auth import AuthMiddleware
    auth = container.retrieve(AuthMiddleware)
    auth.register_user('testuser', 'password123')
    response = client.get('/api/traces/stream')
    assert response.status_code == 401

def test_logout_clears_cookie(client: TestClient, container: Any) -> None:
    from sovereignai.shared.auth import AuthMiddleware
    auth = container.retrieve(AuthMiddleware)
    auth.register_user('testuser', 'password123')
    login_response = client.post('/api/auth/login', json={'username': 'testuser', 'password': 'password123'})
    assert 'session_id' in login_response.cookies
    logout_response = client.post('/api/auth/logout')
    assert logout_response.status_code == 200
    assert logout_response.json() == {'status': 'logged_out'}
