import asyncio
import re
import sqlite3
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Protocol, runtime_checkable
from uuid import uuid4

from sovereignai.model_registry.database import get_last_successful_sync_at, initialize_database
from sovereignai.model_registry.events import SyncCompletedEvent
from sovereignai.model_registry.schema import NormalizedModelData
from sovereignai.shared.types import Channel, CorrelationId, Event


class ProviderAuthError(Exception):
    """Authentication failed for provider API."""


class ProviderRateLimitError(Exception):
    """Rate limit exceeded for provider API."""


class ProviderUnavailableError(Exception):
    """Provider API is temporarily unavailable."""


@runtime_checkable
class ProviderAdapterProtocol(Protocol):
    """Protocol for provider model adapters."""

    async def fetch_models(self, api_key: str) -> list[NormalizedModelData]:
        """Fetch models from provider API."""
        ...


class ModelSyncService:
    """Service for syncing model data from providers."""

    def __init__(self, db_path: Path | None = None, event_bus=None):  # type: ignore[no-untyped-def]
        self.db_path = db_path
        self._conn: sqlite3.Connection | None = None
        self._sync_lock = asyncio.Lock()
        self._event_bus = event_bus

    @property
    def conn(self) -> sqlite3.Connection:
        """Get database connection, initializing if needed."""
        if self._conn is None:
            self._conn = initialize_database(self.db_path)
        return self._conn

    def close(self) -> None:
        """Close database connection."""
        if self._conn:
            self._conn.close()
            self._conn = None

    async def sync_provider(
        self,
        provider_id: str,
        adapter: ProviderAdapterProtocol,
        api_key: str,
    ) -> dict[str, str]:
        """Sync models from a single provider.

        Returns dict with sync status information.
        """
        async with self._sync_lock:
            started_at = datetime.now()
            sync_run_id = self._create_sync_run(provider_id, started_at)

            try:
                # Fetch models with timeout
                models = await asyncio.wait_for(
                    adapter.fetch_models(api_key),
                    timeout=60,
                )

                # Cache results in database
                self._cache_models(provider_id, models)

                completed_at = datetime.now()
                self._update_sync_run(sync_run_id, completed_at, "SUCCESS", None)

                # Emit sync completed event
                self._emit_sync_event(
                    "success", provider_id, completed_at, None, len(models)
                )

                return {
                    "status": "success",
                    "provider_id": provider_id,
                    "started_at": started_at.isoformat(),
                    "completed_at": completed_at.isoformat(),
                    "models_count": str(len(models)),
                }

            except ProviderAuthError as e:
                completed_at = datetime.now()
                self._update_sync_run(sync_run_id, completed_at, "FAILED", "ProviderAuthError")
                self._log_sync_error(provider_id, "ProviderAuthError", str(e))
                self._emit_sync_event(
                    "failed", provider_id, completed_at, "ProviderAuthError", None
                )
                raise

            except ProviderRateLimitError as e:
                completed_at = datetime.now()
                self._update_sync_run(sync_run_id, completed_at, "FAILED", "ProviderRateLimitError")
                self._log_sync_error(provider_id, "ProviderRateLimitError", str(e))
                self._emit_sync_event(
                    "failed", provider_id, completed_at, "ProviderRateLimitError", None
                )
                raise

            except ProviderUnavailableError as e:
                completed_at = datetime.now()
                self._update_sync_run(
                    sync_run_id, completed_at, "FAILED", "ProviderUnavailableError"
                )
                self._log_sync_error(provider_id, "ProviderUnavailableError", str(e))
                self._emit_sync_event(
                    "failed", provider_id, completed_at, "ProviderUnavailableError", None
                )
                raise

            except TimeoutError:
                completed_at = datetime.now()
                self._update_sync_run(sync_run_id, completed_at, "FAILED", "TimeoutError")
                self._log_sync_error(provider_id, "TimeoutError", "Provider API timeout after 60s")
                self._emit_sync_event("failed", provider_id, completed_at, "TimeoutError", None)
                raise ProviderUnavailableError("Provider API timeout") from None

            except Exception as e:
                completed_at = datetime.now()
                error_class = type(e).__name__
                self._update_sync_run(sync_run_id, completed_at, "FAILED", error_class)
                self._log_sync_error(provider_id, error_class, str(e))
                self._emit_sync_event("failed", provider_id, completed_at, error_class, None)
                raise

    def _create_sync_run(self, provider_id: str, started_at: datetime) -> int:
        """Create a sync run record and return its ID."""
        cursor = self.conn.execute(
            """
            INSERT INTO sync_runs (provider_id, started_at, completed_at, status, error_class)
            VALUES (?, ?, ?, ?, ?)
            """,
            (provider_id, started_at.isoformat(), None, "RUNNING", None),
        )
        self.conn.commit()
        rowid = cursor.lastrowid
        if rowid is None:
            raise RuntimeError("Failed to create sync run")
        return rowid

    def _update_sync_run(
        self,
        sync_run_id: int,
        completed_at: datetime,
        status: str,
        error_class: str | None,
    ) -> None:
        """Update a sync run record with completion information."""
        self.conn.execute(
            """
            UPDATE sync_runs
            SET completed_at = ?, status = ?, error_class = ?
            WHERE id = ?
            """,
            (completed_at.isoformat(), status, error_class, sync_run_id),
        )
        self.conn.commit()

    def _cache_models(self, provider_id: str, models: list[NormalizedModelData]) -> None:
        """Cache fetched models in the database."""
        # Delete existing data for this provider (full refresh)
        self.conn.execute(
            "DELETE FROM model_versions WHERE model_id IN "
            "(SELECT id FROM models WHERE family_id IN "
            "(SELECT id FROM families WHERE provider_id = ?))",
            (provider_id,),
        )
        self.conn.execute(
            "DELETE FROM models WHERE family_id IN "
            "(SELECT id FROM families WHERE provider_id = ?)",
            (provider_id,),
        )
        self.conn.execute("DELETE FROM families WHERE provider_id = ?", (provider_id,))

        # Insert new data
        for model_data in models:
            # Insert or update provider
            self.conn.execute(
                """
                INSERT OR REPLACE INTO providers (id, name, api_base_url, auth_type, is_enabled)
                VALUES (?, ?, ?, ?, ?)
                """,
                (provider_id, provider_id, "", "api_key", 1),
            )

            # Create family ID
            family_id = f"{provider_id}-{model_data.model_id}"
            family_name = model_data.model_name

            # Insert family
            self.conn.execute(
                """
                INSERT OR REPLACE INTO families (id, provider_id, name, description)
                VALUES (?, ?, ?, ?)
                """,
                (family_id, provider_id, family_name, ""),
            )

            # Create model ID
            model_id = f"{family_id}-{model_data.version_string}"

            # Insert model
            self.conn.execute(
                """
                INSERT OR REPLACE INTO models (id, family_id, name)
                VALUES (?, ?, ?)
                """,
                (model_id, family_id, model_data.model_name),
            )

            # Create version ID
            version_id = f"{model_id}-v{model_data.version_string}"

            # Insert model version
            self.conn.execute(
                """
                INSERT OR REPLACE INTO model_versions (
                    id, model_id, version_string, release_date, is_latest,
                    context_window, supports_vision, supports_tools, capabilities
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    version_id,
                    model_id,
                    model_data.version_string,
                    model_data.release_date.isoformat() if model_data.release_date else None,
                    model_data.version_string,  # Use version_string as proxy for is_latest
                    model_data.context_window,
                    1 if model_data.supports_vision else 0,
                    1 if model_data.supports_tools else 0,
                    str(model_data.capabilities),
                ),
            )

        self.conn.commit()

    def _log_sync_error(
        self,
        provider_id: str,
        error_class: str,
        error_message: str,
    ) -> None:
        """Log a sync error to the sync_errors table."""
        safe_message = self._sanitize_error_message(error_message)

        self.conn.execute(
            """
            INSERT INTO sync_errors
            (timestamp, provider_adapter_name, error_class, safe_error_message)
            VALUES (?, ?, ?, ?)
            """,
            (datetime.now().isoformat(), provider_id, error_class, safe_message),
        )
        self.conn.commit()

    def _sanitize_error_message(self, message: str) -> str:
        """Sanitize error message to remove sensitive information."""
        # Strip API key patterns
        patterns = [
            r"sk-[a-zA-Z0-9]{20,}",
            r"AKIA[0-9A-Z]{16}",
            r"ghp_[a-zA-Z0-9]{36}",
        ]

        for pattern in patterns:
            message = re.sub(pattern, "***REDACTED***", message)

        # Truncate to 500 characters
        if len(message) > 500:
            message = message[:500]

        return message

    def _emit_sync_event(
        self,
        status: str,
        provider_id: str,
        timestamp: datetime,
        error_class: str | None,
        models_count: int | None,
    ) -> None:
        """Emit a sync completed event if event bus is available."""
        if self._event_bus is None:
            return

        sync_event = SyncCompletedEvent(
            status=status,
            provider_id=provider_id,
            timestamp=timestamp,
            error_class=error_class,
            models_count=models_count,
        )

        try:
            event = Event(
                channel=Channel("models.sync.completed"),
                correlation_id=CorrelationId(uuid4()),
                timestamp=timestamp.replace(tzinfo=UTC),
                payload=sync_event.model_dump(),
            )
            self._event_bus.publish(event)
        except Exception:  # nosec B110 - Event publishing failure should not break sync
            pass

    def cleanup_old_errors(self, retention_days: int = 30) -> None:
        """Clean up old sync errors based on retention policy."""
        cutoff_date = datetime.now() - timedelta(days=retention_days)

        self.conn.execute(
            """
            DELETE FROM sync_errors
            WHERE timestamp < ?
            """,
            (cutoff_date.isoformat(),),
        )
        self.conn.commit()

    def get_sync_status(self, provider_id: str) -> dict[str, str | int | None]:
        """Get sync status for a provider."""
        last_sync = get_last_successful_sync_at(self.conn, provider_id)

        # Get last error
        cursor = self.conn.execute(
            """
            SELECT timestamp, error_class, safe_error_message
            FROM sync_errors
            WHERE provider_adapter_name = ?
            ORDER BY timestamp DESC
            LIMIT 1
            """,
            (provider_id,),
        )
        error_row = cursor.fetchone()

        return {
            "provider_id": provider_id,
            "last_successful_sync_at": last_sync.isoformat() if last_sync else None,
            "last_error_timestamp": error_row["timestamp"] if error_row else None,
            "last_error_class": error_row["error_class"] if error_row else None,
            "last_error_message": error_row["safe_error_message"] if error_row else None,
        }
