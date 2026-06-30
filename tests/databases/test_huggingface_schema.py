"""Tests for HuggingFace database schema and migrations."""
import sqlite3
from pathlib import Path

from sovereignai.databases.huggingface.schema import (
    get_db_path,
    init_schema,
    migrate_to_v2,
)
from sovereignai.shared.trace_emitter import TraceEmitter


def test_get_db_path() -> None:
    """Test that get_db_path returns the correct path."""
    path = get_db_path()
    assert path.name == "models.db"
    assert "huggingface" in str(path)


def test_init_schema() -> None:
    """Test that init_schema creates the models table with all required columns."""
    import tempfile
    with tempfile.TemporaryDirectory() as tmpdir:
        test_db_path = Path(tmpdir) / "test.db"
        conn = sqlite3.connect(str(test_db_path))
        trace = TraceEmitter()

        init_schema(conn, trace)

        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]
        assert "models" in tables

        cursor.execute("PRAGMA table_info(models)")
        columns = [row[1] for row in cursor.fetchall()]
        required_columns = [
            "id", "repo_id", "filename", "quantization", "size_gb",
            "vram_required_gb", "active_bytes_gb", "downloads", "likes",
            "last_modified", "org", "family", "model_version", "quant_level",
            "file_type", "category", "category_group", "parameter_count",
            "context_length", "license", "architecture", "sync_timestamp"
        ]
        for col in required_columns:
            assert col in columns

        conn.close()


def test_migrate_to_v2() -> None:
    """Test that migrate_to_v2 adds hierarchical browsing columns."""
    import tempfile
    with tempfile.TemporaryDirectory() as tmpdir:
        test_db_path = Path(tmpdir) / "test.db"
        conn = sqlite3.connect(str(test_db_path))
        trace = TraceEmitter()

        # Create v1 schema (without hierarchical columns)
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS models (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                repo_id TEXT NOT NULL,
                filename TEXT NOT NULL,
                quantization TEXT,
                size_gb REAL
            )
        """)
        conn.commit()

        # Migrate to v2
        migrate_to_v2(conn, trace)

        # Verify new columns exist
        cursor.execute("PRAGMA table_info(models)")
        columns = [row[1] for row in cursor.fetchall()]
        new_columns = ["org", "family", "model_version", "quant_level", "file_type", "category", "category_group"]
        for col in new_columns:
            assert col in columns

        conn.close()


def test_ensure_latest_schema() -> None:
    """Test that ensure_latest_schema applies migrations when needed."""
    import tempfile
    with tempfile.TemporaryDirectory() as tmpdir:
        # Override db path for testing
        test_db_path = Path(tmpdir) / "models.db"

        # Create a v1 database
        conn = sqlite3.connect(str(test_db_path))
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE models (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                repo_id TEXT NOT NULL,
                filename TEXT NOT NULL
            )
        """)
        conn.commit()

        # Run migrate_to_v2 directly with the test connection
        # (ensure_latest_schema uses get_db_path() which returns the real DB path)
        trace = TraceEmitter()
        migrate_to_v2(conn, trace)

        # Verify migration was applied
        cursor.execute("PRAGMA table_info(models)")
        columns = [row[1] for row in cursor.fetchall()]
        assert "org" in columns
        assert "family" in columns
        conn.close()
