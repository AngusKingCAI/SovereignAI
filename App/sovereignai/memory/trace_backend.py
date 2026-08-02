from __future__ import annotations

import sqlite3
import uuid
from typing import TYPE_CHECKING

from sovereignai.shared.trace_emitter import TraceEmitter
from sovereignai.shared.types import TraceEvent, TraceLevel, TraceQuery, now_utc
from sovereignai.shared.types_base import CorrelationId

if TYPE_CHECKING:
    pass


class TraceMemoryBackend:

    def __init__(self, trace: TraceEmitter, db_path: str | None = None) -> None:
        self._trace = trace
        self._db_path = db_path if db_path else "~/.sovereignai/trace.db"
        self._conn: sqlite3.Connection | None = None
        self._initialize_db()

    def _initialize_db(self) -> None:
        import os

        db_path = os.path.expanduser(self._db_path)
        if db_path != ":memory:":
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
        record_id = str(uuid.uuid4())
        event = TraceEvent(
            component=data["component"],
            level=TraceLevel(data["level"]),
            message=data["message"],
            timestamp=data.get("timestamp") or now_utc(),
            correlation_id=CorrelationId(uuid.UUID(data["correlation_id"])),
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

    def query(self, query: TraceQuery) -> list[dict]:
        if not self._conn:
            return []

        conditions = []
        params = []

        if query.correlation_id:
            conditions.append("correlation_id = ?")
            params.append(query.correlation_id)

        if query.span_type:
            conditions.append("component = ?")
            params.append(query.span_type)

        if query.task_id:
            conditions.append("task_id = ?")
            params.append(query.task_id)

        where_clause = " AND ".join(conditions) if conditions else "1=1"

        sql = f"""
            SELECT id, timestamp, level, component, message, correlation_id, task_id, task_state
            FROM traces
            WHERE {where_clause}
            ORDER BY timestamp ASC
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
        if self._conn:
            self._conn.close()
            self._conn = None
