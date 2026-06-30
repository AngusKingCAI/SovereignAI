"""HuggingFace database schema definition and migrations.

This module defines the schema for the HuggingFace models database and
provides migration functions to add new columns for hierarchical model browsing.
"""
import sqlite3
from pathlib import Path

from sovereignai.shared.trace_emitter import TraceEmitter, TraceLevel


def get_db_path() -> Path:
    """Return the path to the HuggingFace database."""
    return Path.home() / ".sovereignai" / "databases" / "huggingface" / "models.db"


def init_schema(conn: sqlite3.Connection, trace: TraceEmitter | None = None) -> None:
    """Initialize the database schema with all required tables and indexes.

    Args:
        conn: SQLite database connection.
        trace: Optional trace emitter for logging.
    """
    trace = trace or TraceEmitter()
    trace.emit(
        component="huggingface_schema",
        level=TraceLevel.INFO,
        message="Initializing HuggingFace database schema",
    )

    cursor = conn.cursor()

    # Main models table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS models (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            repo_id TEXT NOT NULL,
            filename TEXT NOT NULL,
            quantization TEXT,
            size_gb REAL,
            vram_required_gb REAL,
            active_bytes_gb REAL,
            downloads INTEGER DEFAULT 0,
            likes INTEGER DEFAULT 0,
            last_modified TEXT,
            -- Hierarchical browsing fields
            org TEXT,
            family TEXT,
            model_version TEXT,
            quant_level INTEGER DEFAULT 0,
            file_type TEXT DEFAULT 'other',
            category TEXT,
            category_group TEXT,
            -- Additional metadata
            parameter_count TEXT,
            context_length TEXT,
            license TEXT,
            architecture TEXT,
            sync_timestamp TEXT
        )
    """)

    # Create indexes for performance
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_models_repo_id ON models(repo_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_models_org ON models(org)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_models_family ON models(family)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_models_model_version ON models(model_version)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_models_file_type ON models(file_type)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_models_category ON models(category)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_models_quant_level ON models(quant_level)")

    conn.commit()
    trace.emit(
        component="huggingface_schema",
        level=TraceLevel.INFO,
        message="HuggingFace database schema initialized",
    )


def migrate_to_v2(conn: sqlite3.Connection, trace: TraceEmitter | None = None) -> None:
    """Migrate database to v2 schema with hierarchical browsing fields.

    This migration adds the following columns:
    - org: Organization name (e.g., "google", "meta-llama")
    - family: Model family (e.g., "gemini", "llama")
    - model_version: Model version (e.g., "gemini-1.5")
    - quant_level: Quantization level integer (0=unquantized, 20=Q2, 40=Q4, etc.)
    - file_type: File type (gguf, safetensors, pytorch, onnx, other)
    - category: HF pipeline-tag category
    - category_group: Top-level category group

    Args:
        conn: SQLite database connection.
        trace: Optional trace emitter for logging.
    """
    trace = trace or TraceEmitter()
    trace.emit(
        component="huggingface_schema",
        level=TraceLevel.INFO,
        message="Migrating HuggingFace database to v2 schema",
    )

    cursor = conn.cursor()

    # Check if migration already applied
    cursor.execute("PRAGMA table_info(models)")
    columns = {row[1] for row in cursor.fetchall()}

    if "org" in columns:
        trace.emit(
            component="huggingface_schema",
            level=TraceLevel.DEBUG,
            message="Migration to v2 already applied",
        )
        return

    # Add new columns
    cursor.execute("ALTER TABLE models ADD COLUMN org TEXT")
    cursor.execute("ALTER TABLE models ADD COLUMN family TEXT")
    cursor.execute("ALTER TABLE models ADD COLUMN model_version TEXT")
    cursor.execute("ALTER TABLE models ADD COLUMN quant_level INTEGER DEFAULT 0")
    cursor.execute("ALTER TABLE models ADD COLUMN file_type TEXT DEFAULT 'other'")
    cursor.execute("ALTER TABLE models ADD COLUMN category TEXT")
    cursor.execute("ALTER TABLE models ADD COLUMN category_group TEXT")

    # Add additional metadata columns
    cursor.execute("ALTER TABLE models ADD COLUMN parameter_count TEXT")
    cursor.execute("ALTER TABLE models ADD COLUMN context_length TEXT")
    cursor.execute("ALTER TABLE models ADD COLUMN license TEXT")
    cursor.execute("ALTER TABLE models ADD COLUMN architecture TEXT")

    # Create indexes
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_models_org ON models(org)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_models_family ON models(family)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_models_model_version ON models(model_version)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_models_file_type ON models(file_type)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_models_category ON models(category)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_models_quant_level ON models(quant_level)")

    conn.commit()
    trace.emit(
        component="huggingface_schema",
        level=TraceLevel.INFO,
        message="HuggingFace database migrated to v2 schema",
    )


def ensure_latest_schema(trace: TraceEmitter | None = None) -> None:
    """Ensure the database has the latest schema applied.

    Args:
        trace: Optional trace emitter for logging.
    """
    trace = trace or TraceEmitter()
    db_path = get_db_path()

    if not db_path.exists():
        trace.emit(
            component="huggingface_schema",
            level=TraceLevel.WARN,
            message="Database does not exist, skipping migration",
        )
        return

    conn = sqlite3.connect(str(db_path))
    try:
        migrate_to_v2(conn, trace)
    finally:
        conn.close()
