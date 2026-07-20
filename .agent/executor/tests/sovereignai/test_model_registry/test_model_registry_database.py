from datetime import datetime
from pathlib import Path

from sovereignai.model_registry.database import (
    get_db_path,
    get_last_successful_sync_at,
    initialize_database,
)


def test_get_db_path() -> None:
    path = get_db_path()
    assert isinstance(path, Path)
    assert str(path).endswith("model_registry.db")


def test_initialize_database_creates_tables(tmp_path: Path) -> None:
    db_path = tmp_path / "test.db"
    conn = initialize_database(db_path)

    # Check that all tables exist (excluding sqlite_sequence which is internal)
    cursor = conn.execute(
        """
        SELECT name FROM sqlite_master
        WHERE type='table' AND name != 'sqlite_sequence'
        ORDER BY name
        """
    )
    tables = [row["name"] for row in cursor.fetchall()]

    expected_tables = [
        "families",
        "model_versions",
        "models",
        "providers",
        "sync_errors",
        "sync_runs"
    ]
    assert tables == expected_tables

    conn.close()


def test_initialize_database_wal_mode(tmp_path: Path) -> None:
    db_path = tmp_path / "test.db"
    conn = initialize_database(db_path)

    cursor = conn.execute("PRAGMA journal_mode")
    row = cursor.fetchone()
    assert row[0] == "wal"

    conn.close()


def test_initialize_database_providers_table(tmp_path: Path) -> None:
    db_path = tmp_path / "test.db"
    conn = initialize_database(db_path)

    # Insert a provider
    conn.execute("""
        INSERT INTO providers (id, name, api_base_url, auth_type, is_enabled)
        VALUES (?, ?, ?, ?, ?)
    """, ("openai", "OpenAI", "https://api.openai.com/v1", "bearer_token", 1))
    conn.commit()

    # Query it back
    cursor = conn.execute("SELECT * FROM providers WHERE id = ?", ("openai",))
    row = cursor.fetchone()
    assert row["id"] == "openai"
    assert row["name"] == "OpenAI"
    assert row["api_base_url"] == "https://api.openai.com/v1"
    assert row["auth_type"] == "bearer_token"
    assert row["is_enabled"] == 1

    conn.close()


def test_initialize_database_families_table(tmp_path: Path) -> None:
    db_path = tmp_path / "test.db"
    conn = initialize_database(db_path)

    # Insert a provider first
    conn.execute("""
        INSERT INTO providers (id, name, api_base_url, auth_type, is_enabled)
        VALUES (?, ?, ?, ?, ?)
    """, ("openai", "OpenAI", "https://api.openai.com/v1", "bearer_token", 1))

    # Insert a family
    conn.execute("""
        INSERT INTO families (id, provider_id, name, description)
        VALUES (?, ?, ?, ?)
    """, ("gpt-4", "openai", "GPT-4", "GPT-4 family"))
    conn.commit()

    # Query it back
    cursor = conn.execute("SELECT * FROM families WHERE id = ?", ("gpt-4",))
    row = cursor.fetchone()
    assert row["id"] == "gpt-4"
    assert row["provider_id"] == "openai"
    assert row["name"] == "GPT-4"
    assert row["description"] == "GPT-4 family"

    conn.close()


def test_initialize_database_models_table(tmp_path: Path) -> None:
    db_path = tmp_path / "test.db"
    conn = initialize_database(db_path)

    # Insert provider and family first
    conn.execute("""
        INSERT INTO providers (id, name, api_base_url, auth_type, is_enabled)
        VALUES (?, ?, ?, ?, ?)
    """, ("openai", "OpenAI", "https://api.openai.com/v1", "bearer_token", 1))

    conn.execute("""
        INSERT INTO families (id, provider_id, name, description)
        VALUES (?, ?, ?, ?)
    """, ("gpt-4", "openai", "GPT-4", "GPT-4 family"))

    # Insert a model
    conn.execute("""
        INSERT INTO models (id, family_id, name)
        VALUES (?, ?, ?)
    """, ("gpt-4-turbo", "gpt-4", "GPT-4 Turbo"))
    conn.commit()

    # Query it back
    cursor = conn.execute("SELECT * FROM models WHERE id = ?", ("gpt-4-turbo",))
    row = cursor.fetchone()
    assert row["id"] == "gpt-4-turbo"
    assert row["family_id"] == "gpt-4"
    assert row["name"] == "GPT-4 Turbo"

    conn.close()


def test_initialize_database_model_versions_table(tmp_path: Path) -> None:
    db_path = tmp_path / "test.db"
    conn = initialize_database(db_path)

    # Insert provider, family, and model first
    conn.execute("""
        INSERT INTO providers (id, name, api_base_url, auth_type, is_enabled)
        VALUES (?, ?, ?, ?, ?)
    """, ("openai", "OpenAI", "https://api.openai.com/v1", "bearer_token", 1))

    conn.execute("""
        INSERT INTO families (id, provider_id, name, description)
        VALUES (?, ?, ?, ?)
    """, ("gpt-4", "openai", "GPT-4", "GPT-4 family"))

    conn.execute("""
        INSERT INTO models (id, family_id, name)
        VALUES (?, ?, ?)
    """, ("gpt-4-turbo", "gpt-4", "GPT-4 Turbo"))

    # Insert a model version
    conn.execute(
        """
        INSERT INTO model_versions (
            id, model_id, version_string, release_date, is_latest,
            context_window, supports_vision, supports_tools, capabilities
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            "gpt-4-turbo-2024-04-09",
            "gpt-4-turbo",
            "2024-04-09",
            "2024-04-09T00:00:00",
            1,
            128000,
            1,
            1,
            '{"function_calling": true}',
        ),
    )
    conn.commit()

    # Query it back
    cursor = conn.execute("SELECT * FROM model_versions WHERE id = ?", ("gpt-4-turbo-2024-04-09",))
    row = cursor.fetchone()
    assert row["id"] == "gpt-4-turbo-2024-04-09"
    assert row["model_id"] == "gpt-4-turbo"
    assert row["version_string"] == "2024-04-09"
    assert row["is_latest"] == 1
    assert row["context_window"] == 128000
    assert row["supports_vision"] == 1
    assert row["supports_tools"] == 1
    assert row["capabilities"] == '{"function_calling": true}'

    conn.close()


def test_initialize_database_sync_runs_table(tmp_path: Path) -> None:
    db_path = tmp_path / "test.db"
    conn = initialize_database(db_path)

    # Insert a provider first
    conn.execute("""
        INSERT INTO providers (id, name, api_base_url, auth_type, is_enabled)
        VALUES (?, ?, ?, ?, ?)
    """, ("openai", "OpenAI", "https://api.openai.com/v1", "bearer_token", 1))

    # Insert a sync run
    conn.execute("""
        INSERT INTO sync_runs (provider_id, started_at, completed_at, status, error_class)
        VALUES (?, ?, ?, ?, ?)
    """, ("openai", "2024-04-09T10:00:00", "2024-04-09T10:05:00", "SUCCESS", None))
    conn.commit()

    # Query it back
    cursor = conn.execute("SELECT * FROM sync_runs WHERE provider_id = ?", ("openai",))
    row = cursor.fetchone()
    assert row["provider_id"] == "openai"
    assert row["started_at"] == "2024-04-09T10:00:00"
    assert row["completed_at"] == "2024-04-09T10:05:00"
    assert row["status"] == "SUCCESS"
    assert row["error_class"] is None

    conn.close()


def test_initialize_database_sync_errors_table(tmp_path: Path) -> None:
    db_path = tmp_path / "test.db"
    conn = initialize_database(db_path)

    # Insert a sync error
    conn.execute("""
        INSERT INTO sync_errors (timestamp, provider_adapter_name, error_class, safe_error_message)
        VALUES (?, ?, ?, ?)
    """, ("2024-04-09T10:00:00", "openai_adapter", "ProviderAuthError", "Invalid API key"))
    conn.commit()

    # Query it back
    cursor = conn.execute("SELECT * FROM sync_errors")
    row = cursor.fetchone()
    assert row["timestamp"] == "2024-04-09T10:00:00"
    assert row["provider_adapter_name"] == "openai_adapter"
    assert row["error_class"] == "ProviderAuthError"
    assert row["safe_error_message"] == "Invalid API key"

    conn.close()


def test_get_last_successful_sync_at_no_syncs(tmp_path: Path) -> None:
    db_path = tmp_path / "test.db"
    conn = initialize_database(db_path)

    # Insert a provider
    conn.execute("""
        INSERT INTO providers (id, name, api_base_url, auth_type, is_enabled)
        VALUES (?, ?, ?, ?, ?)
    """, ("openai", "OpenAI", "https://api.openai.com/v1", "bearer_token", 1))
    conn.commit()

    # Query last successful sync
    last_sync = get_last_successful_sync_at(conn, "openai")
    assert last_sync is None

    conn.close()


def test_get_last_successful_sync_at_with_syncs(tmp_path: Path) -> None:
    db_path = tmp_path / "test.db"
    conn = initialize_database(db_path)

    # Insert a provider
    conn.execute("""
        INSERT INTO providers (id, name, api_base_url, auth_type, is_enabled)
        VALUES (?, ?, ?, ?, ?)
    """, ("openai", "OpenAI", "https://api.openai.com/v1", "bearer_token", 1))

    # Insert multiple sync runs
    conn.execute("""
        INSERT INTO sync_runs (provider_id, started_at, completed_at, status, error_class)
        VALUES (?, ?, ?, ?, ?)
    """, ("openai", "2024-04-09T10:00:00", "2024-04-09T10:05:00", "FAILED", "ProviderAuthError"))

    conn.execute("""
        INSERT INTO sync_runs (provider_id, started_at, completed_at, status, error_class)
        VALUES (?, ?, ?, ?, ?)
    """, ("openai", "2024-04-10T10:00:00", "2024-04-10T10:05:00", "SUCCESS", None))

    conn.execute("""
        INSERT INTO sync_runs (provider_id, started_at, completed_at, status, error_class)
        VALUES (?, ?, ?, ?, ?)
    """, ("openai", "2024-04-11T10:00:00", "2024-04-11T10:05:00", "SUCCESS", None))
    conn.commit()

    # Query last successful sync
    last_sync = get_last_successful_sync_at(conn, "openai")
    assert last_sync == datetime(2024, 4, 11, 10, 5, 0)

    conn.close()


def test_get_last_successful_sync_at_only_failed(tmp_path: Path) -> None:
    db_path = tmp_path / "test.db"
    conn = initialize_database(db_path)

    # Insert a provider
    conn.execute("""
        INSERT INTO providers (id, name, api_base_url, auth_type, is_enabled)
        VALUES (?, ?, ?, ?, ?)
    """, ("openai", "OpenAI", "https://api.openai.com/v1", "bearer_token", 1))

    # Insert only failed sync runs
    conn.execute("""
        INSERT INTO sync_runs (provider_id, started_at, completed_at, status, error_class)
        VALUES (?, ?, ?, ?, ?)
    """, ("openai", "2024-04-09T10:00:00", "2024-04-09T10:05:00", "FAILED", "ProviderAuthError"))
    conn.commit()

    # Query last successful sync
    last_sync = get_last_successful_sync_at(conn, "openai")
    assert last_sync is None

    conn.close()


def test_initialize_database_idempotent(tmp_path: Path) -> None:
    db_path = tmp_path / "test.db"

    # Initialize twice
    conn1 = initialize_database(db_path)
    conn1.close()

    conn2 = initialize_database(db_path)

    # Should still work (excluding sqlite_sequence which is internal)
    cursor = conn2.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name != 'sqlite_sequence'"
    )
    tables = [row["name"] for row in cursor.fetchall()]
    assert len(tables) == 6

    conn2.close()
