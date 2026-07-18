from __future__ import annotations

from datetime import timedelta
from unittest.mock import patch

import pytest
from sovereignai.shared.auth import AuthMiddleware
from sovereignai.shared.trace_emitter import TraceEmitter
from sovereignai.shared.types import AuthError, SessionToken, now_utc


@pytest.fixture
def auth() -> AuthMiddleware:
    trace = TraceEmitter()
    return AuthMiddleware(trace=trace)

def test_register_user_stores_hash_not_plaintext(auth: AuthMiddleware) -> None:
    username = 'testuser'
    password = 'plaintext123'
    auth.register_user(username, password)
    assert password not in str(auth._password_hashes)
    assert password not in str(auth._salts)
    assert isinstance(auth._password_hashes[username], bytes)
    assert isinstance(auth._salts[username], bytes)

def test_login_valid_credentials_returns_token(auth: AuthMiddleware) -> None:
    username = 'testuser'
    password = 'correct_password'
    auth.register_user(username, password)
    token = auth.login(username, password)
    assert isinstance(token, SessionToken)
    assert token.username == username
    assert token.token
    assert token.issued_at <= now_utc()
    assert token.expires_at > now_utc()

def test_login_unknown_user_raises(auth: AuthMiddleware) -> None:
    with pytest.raises(AuthError, match='Unknown user'):
        auth.login('nonexistent', 'password')

def test_login_wrong_password_raises(auth: AuthMiddleware) -> None:
    username = 'testuser'
    password = 'correct_password'
    auth.register_user(username, password)
    with pytest.raises(AuthError, match='Invalid password'):
        auth.login(username, 'wrong_password')

def test_validate_valid_token_returns_token(auth: AuthMiddleware) -> None:
    username = 'testuser'
    password = 'password'
    auth.register_user(username, password)
    token = auth.login(username, password)
    validated = auth.validate(token.token)
    assert validated == token

def test_validate_unknown_token_raises(auth: AuthMiddleware) -> None:
    with pytest.raises(AuthError, match='Unknown session token'):
        auth.validate('random_token_string')

def test_validate_expired_token_raises_and_deleted(auth: AuthMiddleware) -> None:
    username = 'testuser'
    password = 'password'
    auth.register_user(username, password)
    token = auth.login(username, password)
    with patch('sovereignai.shared.auth.now_utc') as mock_now:
        mock_now.return_value = token.expires_at + timedelta(hours=1)
        with pytest.raises(AuthError, match='Session token expired'):
            auth.validate(token.token)
    assert token.token not in auth._tokens

def test_register_duplicate_user_raises(auth: AuthMiddleware) -> None:
    username = 'testuser'
    auth.register_user(username, 'password')
    with pytest.raises(ValueError, match='already registered'):
        auth.register_user(username, 'different_password')
