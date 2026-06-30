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
