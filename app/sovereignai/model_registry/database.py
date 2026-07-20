import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Literal


def get_db_path() -> Path:
    """Get the path to the model registry database."""
    return Path("model_registry.db")


def initialize_database(db_path: Path | None = None) -> sqlite3.Connection:
    """Initialize the model registry database with required tables."""
    if db_path is None:
        db_path = get_db_path()

    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row

    # Enable WAL mode for better concurrency
    conn.execute("PRAGMA journal_mode=WAL")

    # Create providers table
    conn.execute("""
        CREATE TABLE IF NOT EXISTS providers (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            api_base_url TEXT NOT NULL,
            auth_type TEXT NOT NULL,
            is_enabled INTEGER NOT NULL DEFAULT 1
        )
    """)

    # Create families table
    conn.execute("""
        CREATE TABLE IF NOT EXISTS families (
            id TEXT PRIMARY KEY,
            provider_id TEXT NOT NULL,
            name TEXT NOT NULL,
            description TEXT DEFAULT '',
            FOREIGN KEY (provider_id) REFERENCES providers(id)
        )
    """)
    conn.execute("CREATE INDEX IF NOT EXISTS idx_families_provider ON families(provider_id)")

    # Create models table
    conn.execute("""
        CREATE TABLE IF NOT EXISTS models (
            id TEXT PRIMARY KEY,
            family_id TEXT NOT NULL,
            name TEXT NOT NULL,
            FOREIGN KEY (family_id) REFERENCES families(id)
        )
    """)
    conn.execute("CREATE INDEX IF NOT EXISTS idx_models_family ON models(family_id)")

    # Create model_versions table
    conn.execute("""
        CREATE TABLE IF NOT EXISTS model_versions (
            id TEXT PRIMARY KEY,
            model_id TEXT NOT NULL,
            version_string TEXT NOT NULL,
            release_date TEXT,
            is_latest INTEGER NOT NULL DEFAULT 0,
            context_window INTEGER,
            supports_vision INTEGER NOT NULL DEFAULT 0,
            supports_tools INTEGER NOT NULL DEFAULT 0,
            capabilities TEXT DEFAULT '{}',
            FOREIGN KEY (model_id) REFERENCES models(id)
        )
    """)
    conn.execute("CREATE INDEX IF NOT EXISTS idx_versions_model ON model_versions(model_id)")

    # Create sync_runs table
    conn.execute("""
        CREATE TABLE IF NOT EXISTS sync_runs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            provider_id TEXT NOT NULL,
            started_at TEXT NOT NULL,
            completed_at TEXT,
            status TEXT NOT NULL,
            error_class TEXT,
            FOREIGN KEY (provider_id) REFERENCES providers(id)
        )
    """)
    conn.execute(
        "CREATE INDEX IF NOT EXISTS idx_sync_runs_provider_completed "
        "ON sync_runs(provider_id, completed_at)"
    )

    # Create sync_errors table
    conn.execute("""
        CREATE TABLE IF NOT EXISTS sync_errors (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            provider_adapter_name TEXT NOT NULL,
            error_class TEXT NOT NULL,
            safe_error_message TEXT NOT NULL
        )
    """)

    conn.commit()
    return conn


SyncStatus = Literal["SUCCESS", "FAILED", "RUNNING"]


def get_last_successful_sync_at(conn: sqlite3.Connection, provider_id: str) -> datetime | None:
    """Get the last successful sync timestamp for a provider."""
    cursor = conn.execute(
        """
        SELECT MAX(completed_at) as last_sync
        FROM sync_runs
        WHERE provider_id = ? AND status = 'SUCCESS'
        """,
        (provider_id,)
    )
    row = cursor.fetchone()
    if row and row["last_sync"]:
        return datetime.fromisoformat(row["last_sync"])
    return None
