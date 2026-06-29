"""Episodic memory backend using SQLite for durable storage.

Per OR87: Stores episodic memory in ~/.sovereignai/episodic.db with WAL mode
and busy_timeout=5000 for atomic writes.
"""
from __future__ import annotations

import json
import os
import sqlite3
import uuid
from typing import TYPE_CHECKING

from sovereignai.shared.trace_emitter import TraceEmitter
from sovereignai.shared.types import TraceLevel, now_utc

if TYPE_CHECKING:
    pass


class EpisodicMemoryBackend:
    """SQLite backend for episodic memory — stores task events and observations.

    Per OR89: Uses atomic writes with WAL mode and busy_timeout=5000.
    Per OR87: Database file is ~/.sovereignai/episodic.db.
    """

    def __init__(self, trace: TraceEmitter) -> None:
        """Create an episodic memory backend with a dedicated SQLite database.

        Args:
            trace: Trace emitter for logging operations and errors.
        """
        self._trace = trace
        self._db_path = os.path.expanduser("~/.sovereignai/episodic.db")
        self._conn: sqlite3.Connection | None = None
        self._initialize_db()

    def _initialize_db(self) -> None:
        """Create the database file and schema if they do not exist.

        Creates the episodes table with indexes for task_id and timestamp queries.
        """
        os.makedirs(os.path.dirname(self._db_path), exist_ok=True)
        self._conn = sqlite3.connect(self._db_path)
        self._conn.execute("PRAGMA journal_mode=WAL")
        self._conn.execute("PRAGMA busy_timeout=5000")
        self._conn.execute("""
            CREATE TABLE IF NOT EXISTS episodes (
                id TEXT PRIMARY KEY,
                timestamp REAL NOT NULL,
                component TEXT NOT NULL,
                task_id TEXT,
                event_type TEXT NOT NULL,
                data TEXT NOT NULL,
                metadata TEXT
            )
        """)
        self._conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_episodes_task ON episodes(task_id)"
        )
        self._conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_episodes_time ON episodes(timestamp)"
        )
        self._conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_episodes_task_time ON episodes(task_id, timestamp)"
        )
        self._conn.commit()

    def store(self, data: dict, metadata: dict | None = None) -> str:
        """Store an episodic memory record and return the generated record id.

        Args:
            data: Episode fields. Must contain: component (str), event_type (str),
                data (str). Optional: timestamp (float), task_id (str).
            metadata: Optional metadata dict (not used by episodic backend).

        Returns:
            The generated record id (UUID string).
        """
        record_id = str(uuid.uuid4())
        timestamp = data.get("timestamp", now_utc().timestamp())
        component = data["component"]
        task_id = data.get("task_id")
        event_type = data["event_type"]
        episode_data = data["data"]
        metadata_json = json.dumps(metadata) if metadata else None

        if self._conn:
            self._conn.execute(
                """
                INSERT INTO episodes
                (id, timestamp, component, task_id, event_type, data, metadata)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (record_id, timestamp, component, task_id, event_type, episode_data, metadata_json),
            )
            self._conn.commit()

        self._trace.emit(
            component="episodic_memory",
            level=TraceLevel.DEBUG,
            message=f"Stored episode {record_id} for component {component}",
        )
        return record_id

    def query(self, query: dict) -> list[dict]:
        """Query episodic memory records matching the specified criteria and filters.

        Supports batch query via task_ids: list[str] for WHERE task_id IN (...).

        Args:
            query: Query parameters. Supported keys:
                - task_id: Single task ID (str)
                - task_ids: List of task IDs (list[str])
                - component: Filter by component name (str)
                - event_type: Filter by event type (str)
                - limit: Maximum number of results (int)

        Returns:
            List of matching episode records as dicts, sorted by timestamp ascending.
        """
        if not self._conn:
            return []

        # Build SQL query dynamically based on parameters
        conditions = []
        params = []

        if "task_id" in query:
            conditions.append("task_id = ?")
            params.append(query["task_id"])

        if "task_ids" in query and isinstance(query["task_ids"], list):
            placeholders = ",".join(["?"] * len(query["task_ids"]))
            conditions.append(f"task_id IN ({placeholders})")
            params.extend(query["task_ids"])

        if "component" in query:
            conditions.append("component = ?")
            params.append(query["component"])

        if "event_type" in query:
            conditions.append("event_type = ?")
            params.append(query["event_type"])

        where_clause = " AND ".join(conditions) if conditions else "1=1"
        limit_clause = f"LIMIT {query['limit']}" if "limit" in query else ""

        sql = f"""
            SELECT id, timestamp, component, task_id, event_type, data, metadata
            FROM episodes
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
                "component": row[2],
                "task_id": row[3],
                "event_type": row[4],
                "data": row[5],
                "metadata": json.loads(row[6]) if row[6] else None,
            })

        self._trace.emit(
            component="episodic_memory",
            level=TraceLevel.DEBUG,
            message=f"Query returned {len(results)} episodes",
        )
        return results

    def delete(self, record_id: str) -> bool:
        """Delete an episodic memory record by its unique identifier string.

        Args:
            record_id: The id of the record to delete.

        Returns:
            True if the record was deleted, False if not found.
        """
        if not self._conn:
            return False

        cursor = self._conn.execute("DELETE FROM episodes WHERE id = ?", (record_id,))
        self._conn.commit()
        deleted = cursor.rowcount > 0

        if deleted:
            self._trace.emit(
                component="episodic_memory",
                level=TraceLevel.DEBUG,
                message=f"Deleted episode {record_id}",
            )

        return deleted

    def close(self) -> None:
        """Close the database connection and clean up all related resources."""
        if self._conn:
            self._conn.close()
            self._conn = None
