"""Episodic event consumer for persisting orchestrator and messaging events.

This module provides EpisodicEventConsumer which subscribes to all orchestrator.*
and messaging.* events, persists them to SQLite with configurable retention,
and runs background pruning.
"""
from __future__ import annotations

import asyncio
import contextlib
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import TYPE_CHECKING

import aiosqlite

from sovereignai.shared.trace_emitter import TraceEmitter
from sovereignai.shared.types import Event, TraceLevel

if TYPE_CHECKING:
    from sovereignai.options.schema import BehaviorSettings


class EpisodicEventConsumer:
    """Consumes and persists orchestrator and messaging events with retention pruning.

    Subscribes to orchestrator.* and messaging.* events, stores them in SQLite,
    and runs background pruning based on retention days configuration.
    """

    def __init__(
        self,
        db_path: Path,
        behavior_settings: BehaviorSettings,
        trace: TraceEmitter,
    ) -> None:
        """Initialize EpisodicEventConsumer.

        Args:
            db_path: Path to SQLite database for episodic events.
            behavior_settings: Behavior settings with retention configuration.
            trace: Trace emitter for logging.
        """
        self._db_path = db_path
        self._behavior_settings = behavior_settings
        self._trace = trace
        self._stop_event = asyncio.Event()
        self._prune_task: asyncio.Task[None] | None = None
        self._connection: aiosqlite.Connection | None = None
        self._initialized = False
        self._trace.emit(
            component="EpisodicEventConsumer",
            level=TraceLevel.DEBUG,
            message="EpisodicEventConsumer initialized",
        )

    async def _initialize_db(self) -> None:
        """Initialize SQLite database with episodic events table."""
        if self._initialized:
            return

        # Ensure parent directory exists
        self._db_path.parent.mkdir(parents=True, exist_ok=True)

        self._connection = await aiosqlite.connect(str(self._db_path))
        await self._connection.execute(
            """
            CREATE TABLE IF NOT EXISTS episodic_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                event_type TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                correlation_id TEXT NOT NULL,
                summary TEXT NOT NULL,
                created_at TEXT NOT NULL DEFAULT (datetime('utc'))
            )
        """
        )
        await self._connection.execute(
            "CREATE INDEX IF NOT EXISTS idx_timestamp ON episodic_events(timestamp)"
        )
        await self._connection.execute(
            "CREATE INDEX IF NOT EXISTS idx_event_type ON episodic_events(event_type)"
        )
        await self._connection.commit()
        self._initialized = True

    async def start(self) -> None:
        """Start the consumer: initialize DB and start background pruning."""
        await self._initialize_db()
        self._prune_task = asyncio.create_task(self._prune_loop())
        self._trace.emit(
            component="EpisodicEventConsumer",
            level=TraceLevel.INFO,
            message="EpisodicEventConsumer started",
        )

    async def stop(self) -> None:
        """Stop the consumer: cancel pruning and close connection."""
        if self._prune_task:
            self._prune_task.cancel()
            with contextlib.suppress(asyncio.CancelledError):
                await self._prune_task
            self._prune_task = None

        if self._connection:
            await self._connection.close()
            self._connection = None

        self._initialized = False
        self._trace.emit(
            component="EpisodicEventConsumer",
            level=TraceLevel.INFO,
            message="EpisodicEventConsumer stopped",
        )

    async def handle_event(self, event: Event) -> None:
        """Handle and persist an event.

        Args:
            event: Event to persist.
        """
        if self._stop_event.is_set():
            return

        if not self._initialized:
            await self._initialize_db()

        if self._connection is None:
            return

        event_type = getattr(event, "channel", "unknown")
        timestamp = getattr(event, "timestamp", datetime.now(UTC)).isoformat()
        correlation_id = str(getattr(event, "correlation_id", ""))
        summary = getattr(event, "summary", str(event))
        created_at = datetime.now(UTC).isoformat()

        await self._connection.execute(
            """
            INSERT INTO episodic_events (event_type, timestamp, correlation_id, summary, created_at)
            VALUES (?, ?, ?, ?, ?)
        """,
            (event_type, timestamp, correlation_id, summary, created_at),
        )
        await self._connection.commit()

    async def _prune_loop(self) -> None:
        """Background loop to prune old events based on retention policy."""
        while not self._stop_event.is_set():
            try:
                await self._prune_old_events()
                # Sleep for 1 hour before next prune
                await asyncio.sleep(3600)
            except asyncio.CancelledError:
                break
            except Exception as exc:
                self._trace.emit(
                    component="EpisodicEventConsumer",
                    level=TraceLevel.ERROR,
                    message=f"Error in prune loop: {exc}",
                )
                await asyncio.sleep(3600)

    async def _prune_old_events(self) -> None:
        """Prune events older than retention period."""
        retention_days = self._behavior_settings.episodic_retention_days
        cutoff_date = datetime.now(UTC) - timedelta(days=retention_days)
        cutoff_iso = cutoff_date.isoformat()

        if self._connection is None:
            return

        cursor = await self._connection.execute(
            """
            DELETE FROM episodic_events
            WHERE timestamp < ?
        """,
            (cutoff_iso,),
        )
        deleted_count = cursor.rowcount
        await self._connection.commit()

        if deleted_count > 0:
            self._trace.emit(
                component="EpisodicEventConsumer",
                level=TraceLevel.DEBUG,
                message=f"Pruned {deleted_count} old episodic events",
            )
