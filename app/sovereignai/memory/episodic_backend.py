from __future__ import annotations

import json
import os
import sqlite3
import uuid
from typing import TYPE_CHECKING

from sovereignai.shared.trace_emitter import TraceEmitter
from sovereignai.shared.types import EpisodicQuery, TraceLevel, now_utc

if TYPE_CHECKING:
    pass


class EpisodicMemoryBackend:

    def __init__(self, trace: TraceEmitter, db_path: str | None = None) -> None:
        self._trace = trace
        self._db_path = db_path if db_path else os.path.expanduser("~/.sovereignai/episodic.db")
        self._conn: sqlite3.Connection | None = None
        self._initialize_db()

    def _initialize_db(self) -> None:
        if self._db_path != ":memory:":
            os.makedirs(os.path.dirname(self._db_path), exist_ok=True)
        self._conn = sqlite3.connect(self._db_path)
        self._conn.execute("PRAGMA journal_mode=WAL")
        self._conn.execute("PRAGMA busy_timeout=5000")
        self._conn.execute(
            """CREATE TABLE IF NOT EXISTS episodes (
                id TEXT PRIMARY KEY,
                timestamp REAL NOT NULL,
                component TEXT NOT NULL,
                task_id TEXT,
                event_type TEXT NOT NULL,
                data TEXT NOT NULL,
                metadata TEXT
            )"""
        )
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
        record_id = str(uuid.uuid4())
        timestamp = data.get("timestamp", now_utc().timestamp())
        component = data["component"]
        task_id = data.get("task_id")
        event_type = data["event_type"]
        episode_data = data["data"]
        metadata_json = json.dumps(metadata) if metadata else None

        if self._conn:
            self._conn.execute(
                """INSERT INTO episodes
                (id, timestamp, component, task_id, event_type, data, metadata)
                VALUES (?, ?, ?, ?, ?, ?, ?)""",
                (record_id, timestamp, component, task_id, event_type, episode_data, metadata_json),
            )
            self._conn.commit()

        self._trace.emit(
            component="episodic_memory",
            level=TraceLevel.DEBUG,
            message=f"Stored episode {record_id} for component {component}",
        )
        return record_id

    def query(self, query: EpisodicQuery) -> list[dict]:
        if not self._conn:
            return []

        # Build SQL query dynamically based on EpisodicQuery parameters
        conditions = []
        params: list[str | float] = []

        # Map session_id to task_id for compatibility
        conditions.append("task_id = ?")
        params.append(query.session_id)

        if query.time_range:
            start_ts, end_ts = query.time_range
            conditions.append("timestamp >= ? AND timestamp <= ?")
            params.extend([start_ts.timestamp(), end_ts.timestamp()])

        if query.tags:
            # Tags stored in metadata JSON - query requires parsing
            # For now, return all records and filter in Python
            pass

        where_clause = " AND ".join(conditions) if conditions else "1=1"

        sql = f"""SELECT id, timestamp, component, task_id, event_type, data, metadata
            FROM episodes
            WHERE {where_clause}
            ORDER BY timestamp ASC"""  # nosec B608

        cursor = self._conn.execute(sql, params)
        results = []
        for row in cursor:
            metadata = json.loads(row[6]) if row[6] else None

            # Filter by tags if specified
            if query.tags and metadata:
                record_tags = metadata.get("tags", [])
                if not any(tag in record_tags for tag in query.tags):
                    continue

            results.append({
                "id": row[0],
                "timestamp": row[1],
                "component": row[2],
                "task_id": row[3],
                "event_type": row[4],
                "data": row[5],
                "metadata": metadata,
            })

        self._trace.emit(
            component="episodic_memory",
            level=TraceLevel.DEBUG,
            message=f"Query returned {len(results)} episodes",
        )
        return results

    def delete(self, record_id: str) -> bool:
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
        if self._conn:
            self._conn.close()
            self._conn = None
