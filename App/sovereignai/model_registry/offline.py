import sqlite3
from datetime import datetime, timedelta
from typing import Literal

from sovereignai.model_registry.database import get_last_successful_sync_at


class StaleStatus:
    """Status of data staleness constants."""

    FRESH = "fresh"
    STALE = "stale"
    NO_DATA = "no_data"


def get_stale_threshold(
    sync_interval_hours: int = 24,
    min_threshold_hours: int = 24,
) -> timedelta:
    """Calculate stale threshold based on sync interval.

    Args:
        sync_interval_hours: Configured sync interval in hours
        min_threshold_hours: Minimum threshold in hours (default 24h for UX)

    Returns:
        Timedelta representing the stale threshold
    """
    threshold_hours = max(min_threshold_hours, 2 * sync_interval_hours)
    return timedelta(hours=threshold_hours)


def is_data_stale(
    conn: sqlite3.Connection,
    provider_id: str,
    sync_interval_hours: int = 24,
    min_threshold_hours: int = 24,
) -> tuple[Literal["fresh", "stale", "no_data"], datetime | None]:
    """Check if provider data is stale.

    Args:
        conn: Database connection
        provider_id: Provider ID to check
        sync_interval_hours: Configured sync interval in hours
        min_threshold_hours: Minimum threshold in hours (default 24h)

    Returns:
        Tuple of (status, last_sync_at):
        - status: "fresh", "stale", or "no_data" (string)
        - last_sync_at: Last successful sync timestamp or None
    """
    last_sync = get_last_successful_sync_at(conn, provider_id)

    if last_sync is None:
        return "no_data", None

    threshold = get_stale_threshold(sync_interval_hours, min_threshold_hours)
    age = datetime.now() - last_sync

    if age > threshold:
        return "stale", last_sync

    return "fresh", last_sync


def should_trigger_sync(
    conn: sqlite3.Connection,
    provider_id: str,
    sync_interval_hours: int = 24,
    min_threshold_hours: int = 24,
) -> bool:
    """Determine if sync should be auto-triggered for a provider.

    Args:
        conn: Database connection
        provider_id: Provider ID to check
        sync_interval_hours: Configured sync interval in hours
        min_threshold_hours: Minimum threshold in hours (default 24h)

    Returns:
        True if sync should be triggered, False otherwise
    """
    status, _ = is_data_stale(conn, provider_id, sync_interval_hours, min_threshold_hours)
    return status in (StaleStatus.STALE, StaleStatus.NO_DATA)


def get_offline_status(
    conn: sqlite3.Connection,
    provider_id: str,
    sync_interval_hours: int = 24,
    min_threshold_hours: int = 24,
) -> dict[str, str | bool | None]:
    """Get comprehensive offline status for a provider.

    Args:
        conn: Database connection
        provider_id: Provider ID to check
        sync_interval_hours: Configured sync interval in hours
        min_threshold_hours: Minimum threshold in hours (default 24h)

    Returns:
        Dict with status information including:
        - status: "fresh", "stale", or "no_data"
        - last_sync_at: Last successful sync timestamp or None
        - is_stale: Boolean indicating if data is stale
        - has_data: Boolean indicating if any data exists
        - should_sync: Boolean indicating if sync should be triggered
    """
    status, last_sync = is_data_stale(
        conn, provider_id, sync_interval_hours, min_threshold_hours
    )

    return {
        "provider_id": provider_id,
        "status": status,
        "last_sync_at": last_sync.isoformat() if last_sync else None,
        "is_stale": status == StaleStatus.STALE,
        "has_data": status != StaleStatus.NO_DATA,
        "should_sync": status in (StaleStatus.STALE, StaleStatus.NO_DATA),
    }
