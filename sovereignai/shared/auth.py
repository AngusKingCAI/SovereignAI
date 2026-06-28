"""Authenticate UI processes and issue session tokens.

Per P6: all UI connections (local and remote) authenticate via a
login gate. The user creates a username + password on first-run
setup; UIs authenticate and receive a session token. Tokens are
attached to every subsequent request.

Per AR4: the token store is instance state, not module-level. The
AuthMiddleware receives it via constructor injection.
"""
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
    """Validate session tokens and issue new ones after username/password check.

    The middleware stores password hashes (never plaintext) and active
    session tokens. It does NOT store the user's password in memory
    after initial setup — only the hash (per P10 security principle).
    """

    def __init__(self, trace: TraceEmitter) -> None:
        """Create an empty auth middleware with no registered users.

        Args:
            trace: Trace emitter for logging auth events (login
                attempts, token validations, failures).
        """
        self._trace = trace
        self._password_hashes: dict[str, bytes] = {}  # username -> salted hash
        self._salts: dict[str, bytes] = {}             # username -> salt
        self._tokens: dict[str, SessionToken] = {}     # token string -> SessionToken
        self._lock = Lock()

    def register_user(self, username: str, password: str) -> None:
        """Add a new user with a username and password for first-run setup.

        Stores a salted hash of the password — never the plaintext.
        If the user already exists, raises ValueError (no silent
        overwrite per P13).

        Args:
            username: The login name.
            password: The plaintext password (hashed before storage).

        Raises:
            ValueError: If the username is already registered.
        """
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
        """Verify credentials and return a fresh session token if valid.

        Args:
            username: The login name.
            password: The plaintext password to verify.

        Returns:
            SessionToken valid for TOKEN_TTL (8 hours by default).

        Raises:
            AuthError: If the username is unknown or the password
                does not match.
        """
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
        """Check that a session token is valid and not expired.

        Args:
            token_str: The opaque token string from a UI request.

        Returns:
            The matching SessionToken if valid.

        Raises:
            AuthError: If the token is unknown or expired.
        """
        with self._lock:
            token = self._tokens.get(token_str)
            if token is None:
                raise AuthError("Unknown session token")
            if now_utc() > token.expires_at:
                del self._tokens[token_str]
                raise AuthError("Session token expired")
        return token
