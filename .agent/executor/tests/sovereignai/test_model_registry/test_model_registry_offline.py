from datetime import datetime, timedelta
from pathlib import Path

from sovereignai.model_registry.database import initialize_database
from sovereignai.model_registry.offline import (
    get_offline_status,
    get_stale_threshold,
    is_data_stale,
    should_trigger_sync,
)

# Constants for test consistency
FRESH = "fresh"
STALE = "stale"
NO_DATA = "no_data"


def test_get_stale_threshold_default() -> None:
    threshold = get_stale_threshold(24, 24)
    assert threshold == timedelta(hours=48)  # 2 * 24


def test_get_stale_threshold_min_floor() -> None:
    threshold = get_stale_threshold(1, 24)
    assert threshold == timedelta(hours=24)  # Minimum 24h floor


def test_get_stale_threshold_large_interval() -> None:
    threshold = get_stale_threshold(48, 24)
    assert threshold == timedelta(hours=96)  # 2 * 48


def test_get_stale_threshold_custom_min() -> None:
    threshold = get_stale_threshold(12, 12)
    assert threshold == timedelta(hours=24)  # 2 * 12


def test_is_data_stale_no_syncs(tmp_path: Path) -> None:
    db_path = tmp_path / "test.db"
    conn = initialize_database(db_path)

    status, last_sync = is_data_stale(conn, "nonexistent")
    assert status == NO_DATA
    assert last_sync is None

    conn.close()


def test_is_data_stale_fresh(tmp_path: Path) -> None:
    db_path = tmp_path / "test.db"
    conn = initialize_database(db_path)

    # Insert a recent successful sync
    recent_time = datetime.now() - timedelta(hours=1)
    conn.execute(
        """
        INSERT INTO providers (id, name, api_base_url, auth_type, is_enabled)
        VALUES (?, ?, ?, ?, ?)
        """,
        ("test", "Test", "https://test.com", "api_key", 1),
    )
    conn.execute(
        """
        INSERT INTO sync_runs (provider_id, started_at, completed_at, status, error_class)
        VALUES (?, ?, ?, ?, ?)
        """,
        ("test", recent_time.isoformat(), recent_time.isoformat(), "SUCCESS", None),
    )
    conn.commit()

    status, last_sync = is_data_stale(conn, "test", 24, 24)
    assert status == FRESH
    assert last_sync is not None
    assert last_sync >= recent_time

    conn.close()


def test_is_data_stale_stale(tmp_path: Path) -> None:
    db_path = tmp_path / "test.db"
    conn = initialize_database(db_path)

    # Insert an old successful sync (beyond threshold)
    old_time = datetime.now() - timedelta(hours=50)  # Beyond 48h threshold
    conn.execute(
        """
        INSERT INTO providers (id, name, api_base_url, auth_type, is_enabled)
        VALUES (?, ?, ?, ?, ?)
        """,
        ("test", "Test", "https://test.com", "api_key", 1),
    )
    conn.execute(
        """
        INSERT INTO sync_runs (provider_id, started_at, completed_at, status, error_class)
        VALUES (?, ?, ?, ?, ?)
        """,
        ("test", old_time.isoformat(), old_time.isoformat(), "SUCCESS", None),
    )
    conn.commit()

    status, last_sync = is_data_stale(conn, "test", 24, 24)
    assert status == STALE
    assert last_sync is not None

    conn.close()


def test_is_data_stale_only_failed_syncs(tmp_path: Path) -> None:
    db_path = tmp_path / "test.db"
    conn = initialize_database(db_path)

    # Insert only failed syncs
    recent_time = datetime.now() - timedelta(hours=1)
    conn.execute(
        """
        INSERT INTO providers (id, name, api_base_url, auth_type, is_enabled)
        VALUES (?, ?, ?, ?, ?)
        """,
        ("test", "Test", "https://test.com", "api_key", 1),
    )
    conn.execute(
        """
        INSERT INTO sync_runs (provider_id, started_at, completed_at, status, error_class)
        VALUES (?, ?, ?, ?, ?)
        """,
        ("test", recent_time.isoformat(), recent_time.isoformat(), "FAILED", "TestError"),
    )
    conn.commit()

    status, last_sync = is_data_stale(conn, "test", 24, 24)
    assert status == NO_DATA
    assert last_sync is None

    conn.close()


def test_should_trigger_sync_no_data(tmp_path: Path) -> None:
    db_path = tmp_path / "test.db"
    conn = initialize_database(db_path)

    assert should_trigger_sync(conn, "nonexistent") is True

    conn.close()


def test_should_trigger_sync_stale(tmp_path: Path) -> None:
    db_path = tmp_path / "test.db"
    conn = initialize_database(db_path)

    old_time = datetime.now() - timedelta(hours=50)
    conn.execute(
        """
        INSERT INTO providers (id, name, api_base_url, auth_type, is_enabled)
        VALUES (?, ?, ?, ?, ?)
        """,
        ("test", "Test", "https://test.com", "api_key", 1),
    )
    conn.execute(
        """
        INSERT INTO sync_runs (provider_id, started_at, completed_at, status, error_class)
        VALUES (?, ?, ?, ?, ?)
        """,
        ("test", old_time.isoformat(), old_time.isoformat(), "SUCCESS", None),
    )
    conn.commit()

    assert should_trigger_sync(conn, "test", 24, 24) is True

    conn.close()


def test_should_trigger_sync_fresh(tmp_path: Path) -> None:
    db_path = tmp_path / "test.db"
    conn = initialize_database(db_path)

    recent_time = datetime.now() - timedelta(hours=1)
    conn.execute(
        """
        INSERT INTO providers (id, name, api_base_url, auth_type, is_enabled)
        VALUES (?, ?, ?, ?, ?)
        """,
        ("test", "Test", "https://test.com", "api_key", 1),
    )
    conn.execute(
        """
        INSERT INTO sync_runs (provider_id, started_at, completed_at, status, error_class)
        VALUES (?, ?, ?, ?, ?)
        """,
        ("test", recent_time.isoformat(), recent_time.isoformat(), "SUCCESS", None),
    )
    conn.commit()

    assert should_trigger_sync(conn, "test", 24, 24) is False

    conn.close()


def test_get_offline_status_no_data(tmp_path: Path) -> None:
    db_path = tmp_path / "test.db"
    conn = initialize_database(db_path)

    status = get_offline_status(conn, "nonexistent")
    assert status["status"] == NO_DATA
    assert status["last_sync_at"] is None
    assert status["is_stale"] is False
    assert status["has_data"] is False
    assert status["should_sync"] is True

    conn.close()


def test_get_offline_status_fresh(tmp_path: Path) -> None:
    db_path = tmp_path / "test.db"
    conn = initialize_database(db_path)

    recent_time = datetime.now() - timedelta(hours=1)
    conn.execute(
        """
        INSERT INTO providers (id, name, api_base_url, auth_type, is_enabled)
        VALUES (?, ?, ?, ?, ?)
        """,
        ("test", "Test", "https://test.com", "api_key", 1),
    )
    conn.execute(
        """
        INSERT INTO sync_runs (provider_id, started_at, completed_at, status, error_class)
        VALUES (?, ?, ?, ?, ?)
        """,
        ("test", recent_time.isoformat(), recent_time.isoformat(), "SUCCESS", None),
    )
    conn.commit()

    status = get_offline_status(conn, "test", 24, 24)
    assert status["status"] == FRESH
    assert status["last_sync_at"] is not None
    assert status["is_stale"] is False
    assert status["has_data"] is True
    assert status["should_sync"] is False

    conn.close()


def test_get_offline_status_stale(tmp_path: Path) -> None:
    db_path = tmp_path / "test.db"
    conn = initialize_database(db_path)

    old_time = datetime.now() - timedelta(hours=50)
    conn.execute(
        """
        INSERT INTO providers (id, name, api_base_url, auth_type, is_enabled)
        VALUES (?, ?, ?, ?, ?)
        """,
        ("test", "Test", "https://test.com", "api_key", 1),
    )
    conn.execute(
        """
        INSERT INTO sync_runs (provider_id, started_at, completed_at, status, error_class)
        VALUES (?, ?, ?, ?, ?)
        """,
        ("test", old_time.isoformat(), old_time.isoformat(), "SUCCESS", None),
    )
    conn.commit()

    status = get_offline_status(conn, "test", 24, 24)
    assert status["status"] == STALE
    assert status["last_sync_at"] is not None
    assert status["is_stale"] is True
    assert status["has_data"] is True
    assert status["should_sync"] is True

    conn.close()


def test_custom_sync_interval(tmp_path: Path) -> None:
    db_path = tmp_path / "test.db"
    conn = initialize_database(db_path)

    # With 12h interval, threshold is 24h (2 * 12)
    recent_time = datetime.now() - timedelta(hours=20)  # Within 24h threshold
    conn.execute(
        """
        INSERT INTO providers (id, name, api_base_url, auth_type, is_enabled)
        VALUES (?, ?, ?, ?, ?)
        """,
        ("test", "Test", "https://test.com", "api_key", 1),
    )
    conn.execute(
        """
        INSERT INTO sync_runs (provider_id, started_at, completed_at, status, error_class)
        VALUES (?, ?, ?, ?, ?)
        """,
        ("test", recent_time.isoformat(), recent_time.isoformat(), "SUCCESS", None),
    )
    conn.commit()

    status, _ = is_data_stale(conn, "test", 12, 12)
    assert status == FRESH

    conn.close()


def test_custom_min_threshold(tmp_path: Path) -> None:
    db_path = tmp_path / "test.db"
    conn = initialize_database(db_path)

    # With 1h interval but 12h min, threshold is 12h
    recent_time = datetime.now() - timedelta(hours=10)  # Within 12h threshold
    conn.execute(
        """
        INSERT INTO providers (id, name, api_base_url, auth_type, is_enabled)
        VALUES (?, ?, ?, ?, ?)
        """,
        ("test", "Test", "https://test.com", "api_key", 1),
    )
    conn.execute(
        """
        INSERT INTO sync_runs (provider_id, started_at, completed_at, status, error_class)
        VALUES (?, ?, ?, ?, ?)
        """,
        ("test", recent_time.isoformat(), recent_time.isoformat(), "SUCCESS", None),
    )
    conn.commit()

    status, _ = is_data_stale(conn, "test", 1, 12)
    assert status == FRESH

    conn.close()
