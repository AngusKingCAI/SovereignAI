from __future__ import annotations

import hashlib
import os
import secrets
from datetime import timedelta
from threading import Lock

from sovereignai.shared.trace_emitter import TraceEmitter
from sovereignai.shared.types import (
    AuthError,
    SessionToken,
    TraceLevel,
    now_utc,
)

# Token expires after 8 hours (configurable in a future plan via Options panel)
_TOKEN_TTL = timedelta(hours=8)


class AuthMiddleware:

    def __init__(self, trace: TraceEmitter) -> None:
        self._trace = trace
        self._password_hashes: dict[str, bytes] = {}  # username -> salted hash
        self._salts: dict[str, bytes] = {}             # username -> salt
        self._tokens: dict[str, SessionToken] = {}     # token string -> SessionToken
        self._lock = Lock()

    def register_user(self, username: str, password: str) -> None:
        with self._lock:
            if username in self._password_hashes:
                raise ValueError(f"User {username!r} already registered")
            salt = os.urandom(32)
            hashed = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"),
                                         salt, iterations=100_000)
            self._salts[username] = salt
            self._password_hashes[username] = hashed
        self._trace.emit(
            component="AuthMiddleware",
            level=TraceLevel.INFO,
            message=f"User {username!r} registered",
        )

    def login(self, username: str, password: str) -> SessionToken:
        with self._lock:
            if username not in self._password_hashes:
                raise AuthError(f"Unknown user {username!r}")
            salt = self._salts[username]
            expected = self._password_hashes[username]
            actual = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"),
                                         salt, iterations=100_000)
            if not secrets.compare_digest(expected, actual):
                raise AuthError(f"Invalid password for {username!r}")
            # Issue token
            issued = now_utc()
            token_str = secrets.token_hex(32)
            token = SessionToken(
                token=token_str,
                username=username,
                issued_at=issued,
                expires_at=issued + _TOKEN_TTL,
            )
            self._tokens[token_str] = token
        self._trace.emit(
            component="AuthMiddleware",
            level=TraceLevel.INFO,
            message=f"User {username!r} logged in (token expires {token.expires_at})",
        )
        return token

    def validate(self, token_str: str) -> SessionToken:
        with self._lock:
            token = self._tokens.get(token_str)
            if token is None:
                raise AuthError("Unknown session token")
            if now_utc() > token.expires_at:
                del self._tokens[token_str]
                raise AuthError("Session token expired")
        return token
