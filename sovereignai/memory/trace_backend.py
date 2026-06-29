"""Trace memory backend using SQLite for durable trace event storage.

Per OR87: Stores trace events in ~/.sovereignai/trace.db with WAL mode
and busy_timeout=5000 for atomic writes.
Per Rev7: get_last_task_states() uses MAX(timestamp) not MAX(id) because
UUID4 is random, not monotonic.
"""
from __future__ import annotations

import sqlite3
import uuid
from typing import TYPE_CHECKING

from sovereignai.shared.trace_emitter import TraceEmitter
from sovereignai.shared.types import TraceEvent, TraceLevel, now_utc

if TYPE_CHECKING:
    pass


class TraceMemoryBackend:
    """SQLite backend for trace memory — stores observability events for crash recovery.

    Per OR89: Uses atomic writes with WAL mode and busy_timeout=5000.
    Per OR87: Database file is ~/.sovereignai/trace.db.

    The store() method conforms to the standard memory backend contract:
    store(data: dict, metadata: dict) -> str.
    """

    def __init__(self, trace: TraceEmitter) -> None:
        """Create a trace memory backend with a dedicated SQLite database.

        Args:
            trace: Trace emitter for logging operations and errors.
        """
        self._trace = trace
        self._db_path = "~/.sovereignai/trace.db"
        self._conn: sqlite3.Connection | None = None
        self._initialize_db()

    def _initialize_db(self) -> None:
        """Create the database file and schema if they do not exist.

        Creates the traces table with indexes for correlation_id, task_id, and timestamp.
        """
        import os

        db_path = os.path.expanduser(self._db_path)
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        self._conn = sqlite3.connect(db_path)
        self._conn.execute("PRAGMA journal_mode=WAL")
        self._conn.execute("PRAGMA busy_timeout=5000")
        self._conn.execute("""
            CREATE TABLE IF NOT EXISTS traces (
                id TEXT PRIMARY KEY,
                timestamp REAL NOT NULL,
                level TEXT NOT NULL,
                component TEXT NOT NULL,
                message TEXT NOT NULL,
                correlation_id TEXT NOT NULL,
                task_id TEXT,
                task_state TEXT
            )
        """)
        self._conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_traces_correlation ON traces(correlation_id)"
        )
        self._conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_traces_time ON traces(timestamp)"
        )
        self._conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_traces_task ON traces(task_id)"
        )
        self._conn.commit()

    def store(self, data: dict, metadata: dict | None = None) -> str:
        """Store a trace event and return the generated record id.

        Conforms to the standard memory backend contract per Rev3 N2.

        Args:
            data: Trace event fields. Must contain: component (str), level (str),
                message (str), correlation_id (str). Optional: timestamp (float).
            metadata: Optional dict with task_id (str) and task_state (str).

        Returns:
            The generated record id (UUID string).
        """
        record_id = str(uuid.uuid4())
        event = TraceEvent(
            component=data["component"],
            level=TraceLevel(data["level"]),
            message=data["message"],
            timestamp=data.get("timestamp") or now_utc(),
            correlation_id=uuid.UUID(data["correlation_id"]),
        )
        task_id = (metadata or {}).get("task_id")
        task_state = (metadata or {}).get("task_state")

        if self._conn:
            self._conn.execute(
                """
                INSERT INTO traces
                (id, timestamp, level, component, message, correlation_id, task_id, task_state)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    record_id,
                    event.timestamp.timestamp(),
                    event.level.value,
                    event.component,
                    event.message,
                    str(event.correlation_id),
                    task_id,
                    task_state,
                ),
            )
            self._conn.commit()

        self._trace.emit(
            component="trace_memory",
            level=TraceLevel.DEBUG,
            message=f"Stored trace event {record_id} for component {event.component}",
        )
        return record_id

    def query(self, query: dict) -> list[dict]:
        """Query trace events matching the specified criteria and filters list.

        Args:
            query: Query parameters. Supported keys:
                - task_id: Filter by task ID (str)
                - correlation_id: Filter by correlation ID (str)
                - component: Filter by component name (str)
                - level: Filter by trace level (str)
                - limit: Maximum number of results (int)

        Returns:
            List of matching trace records as dicts, sorted by timestamp ascending.
        """
        if not self._conn:
            return []

        conditions = []
        params = []

        if "task_id" in query:
            conditions.append("task_id = ?")
            params.append(query["task_id"])

        if "correlation_id" in query:
            conditions.append("correlation_id = ?")
            params.append(query["correlation_id"])

        if "component" in query:
            conditions.append("component = ?")
            params.append(query["component"])

        if "level" in query:
            conditions.append("level = ?")
            params.append(query["level"])

        where_clause = " AND ".join(conditions) if conditions else "1=1"
        limit_clause = f"LIMIT {query['limit']}" if "limit" in query else ""

        sql = f"""
            SELECT id, timestamp, level, component, message, correlation_id, task_id, task_state
            FROM traces
            WHERE {where_clause}
            ORDER BY timestamp ASC
            {limit_clause}
        """  # nosec B608

        cursor = self._conn.execute(sql, params)
        results = []
        for row in cursor:
            results.append({
                "id": row[0],
                "timestamp": row[1],
                "level": row[2],
                "component": row[3],
                "message": row[4],
                "correlation_id": row[5],
                "task_id": row[6],
                "task_state": row[7],
            })

        self._trace.emit(
            component="trace_memory",
            level=TraceLevel.DEBUG,
            message=f"Query returned {len(results)} trace events",
        )
        return results

    def delete(self, record_id: str) -> bool:
        """Delete a trace event by its unique identifier from storage.

        Args:
            record_id: The id of the trace event to delete.

        Returns:
            True if the record was deleted, False if not found.
        """
        if not self._conn:
            return False

        cursor = self._conn.execute("DELETE FROM traces WHERE id = ?", (record_id,))
        self._conn.commit()
        deleted = cursor.rowcount > 0

        if deleted:
            self._trace.emit(
                component="trace_memory",
                level=TraceLevel.DEBUG,
                message=f"Deleted trace event {record_id}",
            )

        return deleted

    def get_last_task_states(self) -> dict[str, str]:
        """Return the last recorded state for each task that has a task_state.

        Per Rev7: Uses MAX(timestamp) not MAX(id) because UUID4 is random,
        not monotonic. This returns the LAST recorded state by timestamp.

        Returns:
            Dict mapping task_id (str) to task_state (str).
        """
        if not self._conn:
            return {}

        sql = """
            SELECT task_id, task_state FROM traces
            WHERE rowid IN (
                SELECT rowid FROM traces t1
                WHERE t1.task_id IS NOT NULL AND t1.task_state IS NOT NULL
                AND t1.timestamp = (
                    SELECT MAX(timestamp) FROM traces t2
                    WHERE t2.task_id = t1.task_id AND t2.task_state IS NOT NULL
                )
            )
        """

        cursor = self._conn.execute(sql)
        return {row[0]: row[1] for row in cursor}

    def close(self) -> None:
        """Close the database connection and clean up all related resources."""
        if self._conn:
            self._conn.close()
            self._conn = None
