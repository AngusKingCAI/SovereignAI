import sqlite3
import tempfile
from pathlib import Path

import pytest
from sovereignai.options.migrations import (
    Migration,
    MigrationRunner,
    get_default_migrations,
    migrate_v1,
)


@pytest.fixture
def temp_db() -> Path:
    """Create temporary database for testing."""
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        return Path(f.name)


@pytest.fixture
def runner(temp_db: Path) -> MigrationRunner:
    """Create migration runner with temporary database."""
    r = MigrationRunner(temp_db)
    yield r


def test_migration_runner_initialization(runner: MigrationRunner) -> None:
    """Test migration runner initializes successfully."""
    assert runner._db_path == runner._db_path
    assert runner._migrations == {}


def test_migration_registration(runner: MigrationRunner) -> None:
    """Test migration registration."""
    migration = Migration(version=1, up=lambda conn: None)
    runner.register(migration)
    assert 1 in runner._migrations
    assert runner._migrations[1] == migration


def test_get_current_version_new_db(runner: MigrationRunner) -> None:
    """Test get_current_version returns 0 for new database."""
    version = runner.get_current_version()
    assert version == 0


def test_get_current_version_with_schema(runner: MigrationRunner) -> None:
    """Test get_current_version returns version from schema_version table."""
    connection = sqlite3.connect(runner._db_path)
    cursor = connection.cursor()
    cursor.execute(
        """
        CREATE TABLE schema_version (
            version INTEGER PRIMARY KEY,
            updated_at TEXT NOT NULL
        )
    """
    )
    cursor.execute("INSERT INTO schema_version (version, updated_at) VALUES (1, '2024-01-01')")
    connection.commit()
    connection.close()

    version = runner.get_current_version()
    assert version == 1


def test_run_migrations_new_db(runner: MigrationRunner) -> None:
    """Test running migrations on new database."""
    runner.register(Migration(version=1, up=migrate_v1))
    runner.run_migrations()

    # Verify schema version was set
    version = runner.get_current_version()
    assert version == 1

    # Verify tables were created
    connection = sqlite3.connect(runner._db_path)
    cursor = connection.cursor()
    cursor.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name='options'"
    )
    assert cursor.fetchone() is not None

    cursor.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name='api_keys'"
    )
    assert cursor.fetchone() is not None
    connection.close()


def test_run_migrations_idempotent(runner: MigrationRunner) -> None:
    """Test running migrations twice is idempotent."""
    runner.register(Migration(version=1, up=migrate_v1))
    runner.run_migrations()
    runner.run_migrations()

    version = runner.get_current_version()
    assert version == 1


def test_run_migrations_partial(runner: MigrationRunner) -> None:
    """Test running migrations with consecutive versions."""
    # Register migration 1 only
    runner.register(Migration(version=1, up=migrate_v1))

    # Run migrations - should run version 1
    runner.run_migrations()

    # Close connection to ensure fresh read
    if runner._connection is not None:
        runner._connection.close()
        runner._connection = None

    version = runner.get_current_version()
    assert version == 1


def test_run_migrations_no_migrations(runner: MigrationRunner) -> None:
    """Test running with no registered migrations."""
    runner.run_migrations()
    version = runner.get_current_version()
    assert version == 0


def test_migrate_v1_creates_tables(temp_db: Path) -> None:
    """Test migrate_v1 creates the required tables."""
    connection = sqlite3.connect(temp_db)
    migrate_v1(connection)
    connection.commit()

    cursor = connection.cursor()
    cursor.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name='options'"
    )
    assert cursor.fetchone() is not None

    cursor.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name='api_keys'"
    )
    assert cursor.fetchone() is not None

    connection.close()


def test_migrate_v1_idempotent(temp_db: Path) -> None:
    """Test migrate_v1 is idempotent."""
    connection = sqlite3.connect(temp_db)
    migrate_v1(connection)
    migrate_v1(connection)
    connection.commit()
    connection.close()


def test_get_default_migrations() -> None:
    """Test get_default_migrations returns expected migrations."""
    migrations = get_default_migrations()
    assert 1 in migrations
    assert isinstance(migrations[1], Migration)
    assert migrations[1].version == 1


def test_migration_runner_with_default_migrations(temp_db: Path) -> None:
    """Test migration runner with default migrations."""
    runner = MigrationRunner(temp_db)
    for migration in get_default_migrations().values():
        runner.register(migration)

    runner.run_migrations()

    version = runner.get_current_version()
    assert version == 1

    connection = sqlite3.connect(temp_db)
    cursor = connection.cursor()
    cursor.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name='options'"
    )
    assert cursor.fetchone() is not None
    connection.close()


def test_schema_version_table_structure(runner: MigrationRunner) -> None:
    """Test schema_version table has correct structure."""
    runner.register(Migration(version=1, up=migrate_v1))
    runner.run_migrations()

    connection = sqlite3.connect(runner._db_path)
    cursor = connection.cursor()
    cursor.execute("PRAGMA table_info(schema_version)")
    columns = cursor.fetchall()

    column_names = [col[1] for col in columns]
    assert "version" in column_names
    assert "updated_at" in column_names

    connection.close()


def test_schema_version_updated_at_format(runner: MigrationRunner) -> None:
    """Test schema_version updated_at is ISO format."""
    runner.register(Migration(version=1, up=migrate_v1))
    runner.run_migrations()

    connection = sqlite3.connect(runner._db_path)
    cursor = connection.cursor()
    cursor.execute("SELECT updated_at FROM schema_version")
    row = cursor.fetchone()

    from datetime import datetime

    datetime.fromisoformat(row[0])  # Should not raise

    connection.close()
