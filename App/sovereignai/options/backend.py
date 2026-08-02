"""Options backend with SQLite persistence and encryption."""
from __future__ import annotations

import os
import sqlite3
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Protocol, runtime_checkable

from cryptography.fernet import Fernet, InvalidToken


@runtime_checkable
class OptionsBackend(Protocol):
    """Protocol for options storage backend."""

    def get(self, key: str, default: Any = None) -> Any:  # noqa: ANN401
        """Get option value by key."""
        ...

    def set(self, key: str, value: Any) -> None:  # noqa: ANN401
        """Set option value by key."""
        ...

    def delete(self, key: str) -> bool:
        """Delete option by key. Returns True if deleted."""
        ...

    def get_api_key(self, provider: str) -> str | None:
        """Get API key for provider."""
        ...

    def set_api_key(self, provider: str, key: str) -> None:
        """Set API key for provider (encrypted)."""
        ...

    def delete_api_key(self, provider: str) -> bool:
        """Delete API key for provider. Returns True if deleted."""
        ...


class SQLiteOptionsBackend:
    """SQLite-based options backend with encryption support.

    Uses WAL mode for atomic writes (AR21). API keys encrypted at rest.
    Follows TaskGraphCache pattern from Plan 24.
    """

    def __init__(self, db_path: Path | str = "options.db", event_bus: Any = None) -> None:  # noqa: ANN401
        """Initialize SQLite options backend.

        Args:
            db_path: Path to SQLite database file.
            event_bus: Optional EventBus for emitting change events.
        """
        self._db_path = db_path
        self._connection: sqlite3.Connection | None = None
        self._closed = False
        self._fernet: Fernet | None = None
        self._event_bus = event_bus
        self._initialize_encryption()
        self._initialize_db()

    def _initialize_encryption(self) -> None:
        """Initialize Fernet encryption from environment or key file."""
        env_key = os.environ.get("SOVEREIGNAI_ENCRYPTION_KEY", "")
        key_path = Path(".secrets/fernet.key")

        # Environment variable takes precedence
        if env_key:
            try:
                self._fernet = Fernet(env_key.encode())
                return
            except Exception:
                pass

        # Fall back to key file
        if key_path.exists():
            key = key_path.read_text().strip()
            try:
                self._fernet = Fernet(key.encode())
                return
            except Exception:
                pass

        # No valid key found - disable encryption (fail-open for dev)
        # In production, this should fail-closed per plan spec
        import warnings

        warnings.warn(
            "No valid encryption key found. API keys will be stored plaintext.",
            stacklevel=2,
        )
        self._fernet = None

    def _initialize_db(self) -> None:
        """Initialize SQLite database with WAL mode and tables."""
        if self._closed:
            return

        self._connection = sqlite3.connect(self._db_path)
        self._connection.row_factory = sqlite3.Row

        # Enable WAL mode for atomic writes (AR21)
        cursor = self._connection.cursor()
        cursor.execute("PRAGMA journal_mode=WAL")

        # Create options table
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS options (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
        """
        )

        # Create api_keys table
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS api_keys (
                provider TEXT PRIMARY KEY,
                key TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
        """
        )

        self._connection.commit()

    def get(self, key: str, default: Any = None) -> Any:  # noqa: ANN401
        """Get option value by key.

        Args:
            key: Option key.
            default: Default value if key not found.

        Returns:
            Option value or default.
        """
        if self._closed or self._connection is None:
            return default

        cursor = self._connection.cursor()
        cursor.execute("SELECT value FROM options WHERE key = ?", (key,))
        row = cursor.fetchone()

        if row is None:
            return default

        import json

        try:
            return json.loads(row["value"])  # type: ignore
        except json.JSONDecodeError:
            return row["value"]

    def set(self, key: str, value: Any) -> None:  # noqa: ANN401
        """Set option value by key.

        Args:
            key: Option key.
            value: Option value (will be JSON serialized).
        """
        if self._closed or self._connection is None:
            return

        import json

        cursor = self._connection.cursor()
        cursor.execute(
            """
            INSERT INTO options (key, value, updated_at)
            VALUES (?, ?, ?)
            ON CONFLICT(key) DO UPDATE SET
                value = excluded.value,
                updated_at = excluded.updated_at
        """,
            (key, json.dumps(value), datetime.now(UTC).isoformat()),
        )
        self._connection.commit()

        # Emit event if event_bus is available
        if self._event_bus is not None:
            try:
                from sovereignai.shared.types import Channel, Event

                event = Event(channel=Channel("options.changed"))
                self._event_bus.publish(event)
            except Exception:
                pass  # Event emission is best-effort

    def delete(self, key: str) -> bool:
        """Delete option by key.

        Args:
            key: Option key.

        Returns:
            True if key was deleted, False if not found.
        """
        if self._closed or self._connection is None:
            return False

        cursor = self._connection.cursor()
        cursor.execute("DELETE FROM options WHERE key = ?", (key,))
        self._connection.commit()
        deleted = cursor.rowcount > 0

        # Emit event if event_bus is available
        if deleted and self._event_bus is not None:
            try:
                from sovereignai.shared.types import Channel, Event

                event = Event(channel=Channel("options.deleted"))
                self._event_bus.publish(event)
            except Exception:
                pass  # Event emission is best-effort

        return deleted

    def get_api_key(self, provider: str) -> str | None:
        """Get API key for provider.

        Args:
            provider: Provider name.

        Returns:
            Decrypted API key or None if not found.
        """
        if self._closed or self._connection is None:
            return None

        cursor = self._connection.cursor()
        cursor.execute("SELECT key FROM api_keys WHERE provider = ?", (provider,))
        row = cursor.fetchone()

        if row is None:
            return None

        encrypted_key = row["key"]

        if self._fernet is None:
            return encrypted_key  # type: ignore

        try:
            return self._fernet.decrypt(encrypted_key.encode()).decode()
        except InvalidToken:
            return None

    def set_api_key(self, provider: str, key: str) -> None:
        """Set API key for provider (encrypted).

        Args:
            provider: Provider name.
            key: API key value.
        """
        if self._closed or self._connection is None:
            return

        encrypted_key = key
        if self._fernet is not None:
            encrypted_key = self._fernet.encrypt(key.encode()).decode()

        cursor = self._connection.cursor()
        cursor.execute(
            """
            INSERT INTO api_keys (provider, key, updated_at)
            VALUES (?, ?, ?)
            ON CONFLICT(provider) DO UPDATE SET
                key = excluded.key,
                updated_at = excluded.updated_at
        """,
            (provider, encrypted_key, datetime.now(UTC).isoformat()),
        )
        self._connection.commit()

    def delete_api_key(self, provider: str) -> bool:
        """Delete API key for provider.

        Args:
            provider: Provider name.

        Returns:
            True if key was deleted, False if not found.
        """
        if self._closed or self._connection is None:
            return False

        cursor = self._connection.cursor()
        cursor.execute("DELETE FROM api_keys WHERE provider = ?", (provider,))
        self._connection.commit()
        return cursor.rowcount > 0

    def close(self) -> None:
        """Close SQLite connection. Idempotent."""
        if self._closed:
            return

        if self._connection is not None:
            self._connection.close()
            self._connection = None

        self._closed = True

    def __del__(self) -> None:
        """Cleanup on deletion."""
        self.close()
