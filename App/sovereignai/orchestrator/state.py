from __future__ import annotations

import asyncio
import sqlite3
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    pass


@dataclass
class Message:
    role: str
    content: str
    timestamp: datetime = field(default_factory=datetime.utcnow)


@dataclass
class ConversationState:
    session_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    message_history: list[Message] = field(default_factory=list)
    active_department: str | None = None
    pending_clarifications: list[str] = field(default_factory=list)
    session_metadata: dict[str, str] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)


class ConversationStateManager:

    def __init__(self, db_path: Path | str = "orchestrator_state.db") -> None:
        self._db_path = db_path
        self._connection: sqlite3.Connection | None = None
        self._lock = asyncio.Lock()
        self._conversation_retention_days = 7
        self._purge_failure_count = 0
        self._load_retention_setting()
        self._initialize_db()
        from sovereignai.shared.trace_emitter import TraceEmitter, TraceLevel

        trace = TraceEmitter()
        trace.emit(
            component="ConversationStateManager",
            level=TraceLevel.INFO,
            message="ConversationStateManager initialized",
        )

    def _load_retention_setting(self) -> None:
        try:
            from sovereignai.shared.options_backend import OptionsBackend

            options = OptionsBackend()
            retention = options.get("conversation_retention_days")
            if retention is not None:
                self._conversation_retention_days = int(retention)
        except (ImportError, AttributeError, KeyError, sqlite3.Error, ValueError, TypeError):
            from sovereignai.shared.trace_emitter import TraceEmitter, TraceLevel

            trace = TraceEmitter()
            trace.emit(
                component="ConversationStateManager",
                level=TraceLevel.WARN,
                message="plan_28_behavior_settings_unavailable",
            )
        except Exception:
            from sovereignai.shared.trace_emitter import TraceEmitter, TraceLevel

            trace = TraceEmitter()
            trace.emit(
                component="ConversationStateManager",
                level=TraceLevel.WARN,
                message="plan_28_behavior_settings_unavailable",
            )

    def _initialize_db(self) -> None:
        self._connection = sqlite3.connect(self._db_path)
        self._connection.row_factory = sqlite3.Row

        cursor = self._connection.cursor()
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS conversations (
                session_id TEXT PRIMARY KEY,
                message_history TEXT NOT NULL,
                active_department TEXT,
                pending_clarifications TEXT NOT NULL,
                session_metadata TEXT NOT NULL,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
        """
        )
        cursor.execute(
            "CREATE INDEX IF NOT EXISTS idx_updated_at ON conversations(updated_at)"
        )
        self._connection.commit()
        from sovereignai.shared.trace_emitter import TraceEmitter, TraceLevel

        trace = TraceEmitter()
        trace.emit(
            component="ConversationStateManager",
            level=TraceLevel.DEBUG,
            message="Database initialized",
        )

    def _get_connection(self) -> sqlite3.Connection:
        if self._connection is None:
            raise RuntimeError("Database connection is not initialized")
        return self._connection

    async def save_state(self, state: ConversationState) -> None:
        async with self._lock:
            import json

            conn = self._get_connection()
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT OR REPLACE INTO conversations
                (session_id, message_history, active_department, pending_clarifications,
                 session_metadata, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    state.session_id,
                    json.dumps([
                        {
                            "role": m.role,
                            "content": m.content,
                            "timestamp": m.timestamp.isoformat(),
                        }
                        for m in state.message_history
                    ]),
                    state.active_department,
                    json.dumps(state.pending_clarifications),
                    json.dumps(state.session_metadata),
                    state.created_at.isoformat(),
                    state.updated_at.isoformat(),
                ),
            )
            conn.commit()

    async def load_state(self, session_id: str) -> ConversationState | None:
        async with self._lock:
            import json

            conn = self._get_connection()
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM conversations WHERE session_id = ?", (session_id,)
            )
            row = cursor.fetchone()

            if row is None:
                return None

            return ConversationState(
                session_id=row["session_id"],
                message_history=[
                    Message(
                        role=m["role"],
                        content=m["content"],
                        timestamp=datetime.fromisoformat(m["timestamp"]),
                    )
                    for m in json.loads(row["message_history"])
                ],
                active_department=row["active_department"],
                pending_clarifications=json.loads(row["pending_clarifications"]),
                session_metadata=json.loads(row["session_metadata"]),
                created_at=datetime.fromisoformat(row["created_at"]),
                updated_at=datetime.fromisoformat(row["updated_at"]),
            )

    async def create_session(self) -> ConversationState:
        state = ConversationState()
        await self.save_state(state)
        return state

    async def delete_session(self, session_id: str) -> None:
        async with self._lock:
            conn = self._get_connection()
            cursor = conn.cursor()
            cursor.execute(
                "DELETE FROM conversations WHERE session_id = ?", (session_id,)
            )
            conn.commit()

    async def purge_old_sessions(self) -> None:
        cutoff = datetime.utcnow() - timedelta(
            days=self._conversation_retention_days
        )

        try:
            async with self._lock:
                conn = self._get_connection()
                cursor = conn.cursor()
                cursor.execute(
                    "DELETE FROM conversations WHERE updated_at < ?",
                    (cutoff.isoformat(),),
                )
                deleted_count = cursor.rowcount
                conn.commit()

                if deleted_count > 0:
                    from sovereignai.shared.trace_emitter import TraceEmitter, TraceLevel

                    trace = TraceEmitter()
                    trace.emit(
                        component="ConversationStateManager",
                        level=TraceLevel.INFO,
                        message=f"Purged {deleted_count} old sessions",
                    )

            self._purge_failure_count = 0
        except sqlite3.DatabaseError as e:
            from sovereignai.shared.trace_emitter import TraceEmitter, TraceLevel

            trace = TraceEmitter()
            trace.emit(
                component="ConversationStateManager",
                level=TraceLevel.ERROR,
                message=f"Purge failed: {e}",
            )

            self._purge_failure_count += 1
            if self._purge_failure_count >= 3:
                from sovereignai.shared.event_bus import EventBus

                bus = EventBus()
                bus.publish(
                    "orchestrator.purge.failing",
                    {"error_class": type(e).__name__},
                )

    def close(self) -> None:
        if self._connection is not None:
            self._connection.close()
            self._connection = None
        from sovereignai.shared.trace_emitter import TraceEmitter, TraceLevel

        trace = TraceEmitter()
        trace.emit(
            component="ConversationStateManager",
            level=TraceLevel.INFO,
            message="ConversationStateManager closed",
        )
