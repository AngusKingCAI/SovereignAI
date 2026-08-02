"""Migration system for options database schema."""
from __future__ import annotations

import sqlite3
from collections.abc import Callable
from datetime import UTC
from pathlib import Path


class Migration:
    """Represents a database schema migration."""

    def __init__(self, version: int, up: Callable[[sqlite3.Connection], None]) -> None:
        """Initialize migration.

        Args:
            version: Target schema version.
            up: Migration function to upgrade to this version.
        """
        self.version = version
        self.up = up


class MigrationRunner:
    """Manages database schema migrations."""

    def __init__(self, db_path: Path | str) -> None:
        """Initialize migration runner.

        Args:
            db_path: Path to SQLite database.
        """
        self._db_path = db_path
        self._connection: sqlite3.Connection | None = None
        self._migrations: dict[int, Migration] = {}
        self._connection_owned = False

    def register(self, migration: Migration) -> None:
        """Register a migration.

        Args:
            migration: Migration to register.
        """
        self._migrations[migration.version] = migration

    def get_current_version(self) -> int:
        """Get current schema version.

        Returns:
            Current schema version (0 if not initialized).
        """
        connection = (
            self._connection
            if self._connection is not None
            else sqlite3.connect(self._db_path)
        )
        close_after = self._connection is None
        try:
            cursor = connection.cursor()
            cursor.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name='schema_version'"
            )
            if cursor.fetchone() is None:
                return 0

            cursor.execute("SELECT version FROM schema_version LIMIT 1")
            row = cursor.fetchone()
            return row[0] if row else 0
        finally:
            if close_after:
                connection.close()

    def run_migrations(self) -> None:
        """Run pending migrations to bring schema to latest version."""
        if self._connection is None:
            self._connection = sqlite3.connect(self._db_path)
            self._connection.row_factory = sqlite3.Row
            self._connection_owned = True

        # Always re-read current version to ensure we have fresh state
        current_version = self.get_current_version()
        target_version = max(self._migrations.keys()) if self._migrations else 0

        if current_version >= target_version:
            return

        # Run migrations in order
        for version in sorted(self._migrations.keys()):
            if version > current_version:
                migration = self._migrations[version]
                migration.up(self._connection)
                self._update_schema_version(version)
                current_version = version  # Update current version after each migration

    def _update_schema_version(self, version: int) -> None:
        """Update schema version in database.

        Args:
            version: New schema version.
        """
        if self._connection is None:
            return

        cursor = self._connection.cursor()
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS schema_version (
                version INTEGER PRIMARY KEY,
                updated_at TEXT NOT NULL
            )
        """
        )

        from datetime import datetime

        cursor.execute(
            """
            INSERT INTO schema_version (version, updated_at)
            VALUES (?, ?)
            ON CONFLICT(version) DO UPDATE SET
                version = excluded.version,
                updated_at = excluded.updated_at
        """,
            (version, datetime.now(UTC).isoformat()),
        )
        self._connection.commit()  # Ensure immediate commit


def migrate_v1(connection: sqlite3.Connection) -> None:
    """Initial schema migration (version 1).

    Creates the options and api_keys tables.
    """
    cursor = connection.cursor()

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


def get_default_migrations() -> dict[int, Migration]:
    """Get default migrations for options backend.

    Returns:
        Dictionary mapping version to Migration objects.
    """
    return {
        1: Migration(version=1, up=migrate_v1),
    }
