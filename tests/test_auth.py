"""Tests for AuthMiddleware — PBKDF2 hashing, session tokens, 8h TTL."""
from __future__ import annotations

from datetime import timedelta

import pytest

from sovereignai.shared.auth import AuthMiddleware
from sovereignai.shared.trace_emitter import TraceEmitter
from sovereignai.shared.types import AuthError, SessionToken, now_utc


@pytest.fixture
def auth() -> AuthMiddleware:
    """Create an AuthMiddleware instance for testing."""
    trace = TraceEmitter()
    return AuthMiddleware(trace=trace)


def test_register_user_stores_hash_not_plaintext(auth: AuthMiddleware) -> None:
    """Verify that register_user stores a salted hash, not the plaintext password."""
    username = "testuser"
    password = "plaintext123"
    auth.register_user(username, password)
    # The password should NOT be stored in plaintext
    assert password not in str(auth._password_hashes)
    assert password not in str(auth._salts)
    # The hash should be bytes (not a string)
    assert isinstance(auth._password_hashes[username], bytes)
    assert isinstance(auth._salts[username], bytes)


def test_login_valid_credentials_returns_token(auth: AuthMiddleware) -> None:
    """Verify that login with valid credentials returns a SessionToken."""
    username = "testuser"
    password = "correct_password"
    auth.register_user(username, password)
    token = auth.login(username, password)
    assert isinstance(token, SessionToken)
    assert token.username == username
    assert token.token  # non-empty token string
    assert token.issued_at <= now_utc()
    assert token.expires_at > now_utc()


def test_login_unknown_user_raises(auth: AuthMiddleware) -> None:
    """Verify that login with an unknown username raises AuthError."""
    with pytest.raises(AuthError, match="Unknown user"):
        auth.login("nonexistent", "password")


def test_login_wrong_password_raises(auth: AuthMiddleware) -> None:
    """Verify that login with a wrong password raises AuthError."""
    username = "testuser"
    password = "correct_password"
    auth.register_user(username, password)
    with pytest.raises(AuthError, match="Invalid password"):
        auth.login(username, "wrong_password")


def test_validate_valid_token_returns_token(auth: AuthMiddleware) -> None:
    """Verify that validate with a valid token returns the SessionToken."""
    username = "testuser"
    password = "password"
    auth.register_user(username, password)
    token = auth.login(username, password)
    validated = auth.validate(token.token)
    assert validated == token


def test_validate_unknown_token_raises(auth: AuthMiddleware) -> None:
    """Verify that validate with a random token string raises AuthError."""
    with pytest.raises(AuthError, match="Unknown session token"):
        auth.validate("random_token_string")


def test_validate_expired_token_raises_and_deleted(auth: AuthMiddleware) -> None:
    """Verify that validate with an expired token raises AuthError and deletes the token."""
    username = "testuser"
    password = "password"
    auth.register_user(username, password)
    token = auth.login(username, password)
    # Manually expire the token by setting expires_at to the past
    # We need to mutate the token store directly since SessionToken is frozen
    expired_token = SessionToken(
        token=token.token,
        username=token.username,
        issued_at=token.issued_at,
        expires_at=now_utc() - timedelta(hours=9),  # 9 hours ago
    )
    auth._tokens[token.token] = expired_token
    # Validate should raise AuthError
    with pytest.raises(AuthError, match="Session token expired"):
        auth.validate(token.token)
    # Token should be deleted from the store
    assert token.token not in auth._tokens


def test_register_duplicate_user_raises(auth: AuthMiddleware) -> None:
    """Verify that registering the same username twice raises ValueError."""
    username = "testuser"
    auth.register_user(username, "password")
    with pytest.raises(ValueError, match="already registered"):
        auth.register_user(username, "different_password")
