"""SQLite database for HuggingFace GGUF model catalog.

Per Plan 18.1 Phase 4: Standalone DB at settings/models.db with schema
for GGUF models, computed fields (vram_required_gb, active_bytes_gb),
and sync tracking. Tok/s is computed at query time, not stored.
"""
from __future__ import annotations

import json
import sqlite3
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

DB_PATH = Path("settings/models.db")


def init_db() -> sqlite3.Connection:
    """Initialize the models database with schema and indexes for GGUF catalog.

    Creates the database file and tables if they don't exist.
    Returns a connection to the database for use by other functions.
    """
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row

    conn.execute("""
        CREATE TABLE IF NOT EXISTS models (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            repo_id TEXT NOT NULL,
            model_family TEXT,
            architecture TEXT,
            base_parameter_count INTEGER,
            quantization TEXT,
            filename TEXT NOT NULL,
            file_size_bytes INTEGER NOT NULL,
            file_size_gb REAL NOT NULL,
            context_length INTEGER,
            license TEXT,
            downloads INTEGER,
            likes INTEGER,
            last_modified TEXT,
            tags TEXT,
            vram_required_gb REAL,
            active_bytes_gb REAL,
            sync_timestamp TEXT NOT NULL,
            UNIQUE(repo_id, quantization)
        )
    """)

    conn.execute("""
        CREATE INDEX IF NOT EXISTS idx_models_family
        ON models(model_family)
    """)

    conn.execute("""
        CREATE INDEX IF NOT EXISTS idx_models_size
        ON models(file_size_gb)
    """)

    conn.commit()
    return conn


def insert_or_update_model(
    conn: sqlite3.Connection,
    repo_id: str,
    model_family: str | None,
    architecture: str | None,
    base_parameter_count: int | None,
    quantization: str,
    filename: str,
    file_size_bytes: int,
    context_length: int | None,
    license: str | None,
    downloads: int | None,
    likes: int | None,
    last_modified: str,
    tags: list[str],
) -> None:
    """Insert or update a model record in the SQLite database.

    Computed fields (vram_required_gb, active_bytes_gb) are calculated at insert time.
    Uses INSERT OR REPLACE to handle duplicate repo_id and quantization pairs.
    """
    file_size_gb = file_size_bytes / (1024**3)

    # Compute vram_required_gb: file_size_gb × 1.2 (KV cache headroom)
    vram_required_gb = file_size_gb * 1.2

    # Compute active_bytes_gb: for now assume dense (file_size_gb)
    # MoE would require parsing architecture from config.json
    active_bytes_gb = file_size_gb

    tags_json = json.dumps(tags)
    sync_timestamp = datetime.now(UTC).isoformat()

    conn.execute("""
        INSERT OR REPLACE INTO models (
            repo_id, model_family, architecture, base_parameter_count,
            quantization, filename, file_size_bytes, file_size_gb,
            context_length, license, downloads, likes, last_modified,
            tags, vram_required_gb, active_bytes_gb, sync_timestamp
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        repo_id, model_family, architecture, base_parameter_count,
        quantization, filename, file_size_bytes, file_size_gb,
        context_length, license, downloads, likes, last_modified,
        tags_json, vram_required_gb, active_bytes_gb, sync_timestamp
    ))
    conn.commit()


def get_models(
    conn: sqlite3.Connection,
    search: str = "",
    family: str = "",
    limit: int = 50,
    offset: int = 0,
) -> list[dict[str, Any]]:
    """Query models from the database with pagination and optional filters.

    Args:
        conn: Database connection.
        search: Search term for repo_id or quantization.
        family: Filter by model family.
        limit: Maximum number of results to return.
        offset: Pagination offset for result set.

    Returns:
        List of model dictionaries matching the specified criteria.
    """
    query = "SELECT * FROM models WHERE 1=1"
    params: list[Any] = []

    if search:
        query += " AND (repo_id LIKE ? OR quantization LIKE ?)"
        params.extend([f"%{search}%", f"%{search}%"])

    if family:
        query += " AND model_family = ?"
        params.append(family)

    query += " ORDER BY downloads DESC LIMIT ? OFFSET ?"
    params.extend([limit, offset])

    rows = conn.execute(query, params).fetchall()
    return [dict(row) for row in rows]


def get_model_by_repo_and_quant(
    conn: sqlite3.Connection,
    repo_id: str,
    quantization: str,
) -> dict[str, Any] | None:
    """Retrieve a specific model record by its repository identifier and quantization."""
    row = conn.execute(
        "SELECT * FROM models WHERE repo_id = ? AND quantization = ?",
        (repo_id, quantization)
    ).fetchone()
    return dict(row) if row else None


def get_families(conn: sqlite3.Connection) -> list[str]:
    """Retrieve all unique model family names from the database for filtering."""
    query = "SELECT DISTINCT model_family FROM models WHERE model_family IS NOT NULL"
    rows = conn.execute(query).fetchall()
    return [row[0] for row in rows]


def get_total_count(conn: sqlite3.Connection, search: str = "", family: str = "") -> int:
    """Count the total number of models matching the specified search and family filters."""
    query = "SELECT COUNT(*) FROM models WHERE 1=1"
    params: list[Any] = []

    if search:
        query += " AND (repo_id LIKE ? OR quantization LIKE ?)"
        params.extend([f"%{search}%", f"%{search}%"])

    if family:
        query += " AND model_family = ?"
        params.append(family)

    row = conn.execute(query, params).fetchone()
    return row[0] if row else 0
