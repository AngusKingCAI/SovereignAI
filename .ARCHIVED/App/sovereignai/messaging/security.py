from __future__ import annotations

import sqlite3
import threading
import time
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING

from sovereignai.messaging.schema import CrossDepartmentMessage
from sovereignai.shared.trace_emitter import TraceEmitter
from sovereignai.shared.types import TraceLevel

if TYPE_CHECKING:
    pass


@dataclass
class AuditRecord:
    sender: str
    recipient: str
    message_type: str
    timestamp: str
    correlation_id: str
    status: str
    error_class: str | None
    payload_byte_length: int


class AuditLogger:

    def __init__(self, db_path: Path, trace: TraceEmitter) -> None:
        self._db_path = db_path
        self._trace = trace
        self._lock = threading.Lock()
        self._init_db()

    def _init_db(self) -> None:
        with self._lock:
            conn = sqlite3.connect(str(self._db_path))
            conn.execute("PRAGMA journal_mode=WAL")
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS messaging_audit (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    sender TEXT NOT NULL,
                    recipient TEXT NOT NULL,
                    type TEXT NOT NULL,
                    timestamp TEXT NOT NULL,
                    correlation_id TEXT NOT NULL,
                    status TEXT NOT NULL,
                    error_class TEXT,
                    payload_byte_length INTEGER NOT NULL
                )
            """
            )
            conn.commit()
            conn.close()

    def log_message(
        self,
        message: CrossDepartmentMessage,
        status: str,
        error_class: str | None = None,
    ) -> None:
        record = AuditRecord(
            sender=message.sender,
            recipient=message.recipient,
            message_type=message.message_type.value,
            timestamp=message.timestamp.isoformat(),
            correlation_id=str(message.correlation_id),
            status=status,
            error_class=error_class,
            payload_byte_length=len(str(message.payload)),
        )
        self._write_record(record)

    def _write_record(self, record: AuditRecord) -> None:
        with self._lock:
            try:
                conn = sqlite3.connect(str(self._db_path))
                conn.execute(
                    """
                    INSERT INTO messaging_audit
                    (sender, recipient, type, timestamp, correlation_id,
                     status, error_class, payload_byte_length)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                    (
                        record.sender,
                        record.recipient,
                        record.message_type,
                        record.timestamp,
                        record.correlation_id,
                        record.status,
                        record.error_class,
                        record.payload_byte_length,
                    ),
                )
                conn.commit()
                conn.close()
            except sqlite3.Error as exc:
                self._trace.emit(
                    component="AuditLogger",
                    level=TraceLevel.ERROR,
                    message=f"Failed to write audit record: {exc}",
                )


class RateLimiter:

    def __init__(
        self, max_messages: int = 100, window_seconds: int = 60, trace: TraceEmitter | None = None
    ) -> None:
        self._max_messages = max_messages
        self._window_seconds = window_seconds
        self._trace = trace
        self._timestamps: dict[str, list[float]] = defaultdict(list)
        self._lock = threading.Lock()

    def _get_key(self, sender: str, recipient: str) -> str:
        return f"{sender}:{recipient}"

    def is_allowed(self, sender: str, recipient: str) -> bool:
        key = self._get_key(sender, recipient)
        now = time.time()

        with self._lock:
            timestamps = self._timestamps[key]
            timestamps[:] = [t for t in timestamps if now - t < self._window_seconds]

            if len(timestamps) >= self._max_messages:
                if self._trace:
                    msg = (
                        f"Rate limit exceeded for {key}: "
                        f"{len(timestamps)} messages in {self._window_seconds}s"
                    )
                    self._trace.emit(
                        component="RateLimiter",
                        level=TraceLevel.WARN,
                        message=msg,
                    )
                return False

            timestamps.append(now)
            return True


class CircuitBreaker:

    def __init__(
        self,
        failure_threshold: int = 5,
        timeout_seconds: int = 30,
        trace: TraceEmitter | None = None,
    ) -> None:
        self._failure_threshold = failure_threshold
        self._timeout_seconds = timeout_seconds
        self._trace = trace
        self._failures: dict[str, int] = defaultdict(int)
        self._last_failure_time: dict[str, float] = {}
        self._lock = threading.Lock()

    def record_failure(self, recipient: str) -> bool:
        with self._lock:
            self._failures[recipient] += 1
            self._last_failure_time[recipient] = time.time()

            if self._failures[recipient] >= self._failure_threshold:
                if self._trace:
                    msg = (
                        f"Circuit breaker opened for recipient {recipient} "
                        f"after {self._failures[recipient]} failures"
                    )
                    self._trace.emit(
                        component="CircuitBreaker",
                        level=TraceLevel.ERROR,
                        message=msg,
                    )
                return True
            return False

    def record_success(self, recipient: str) -> None:
        with self._lock:
            self._failures[recipient] = 0
            self._last_failure_time[recipient] = 0.0

    def is_open(self, recipient: str) -> bool:
        with self._lock:
            failures = self._failures.get(recipient, 0)
            if failures < self._failure_threshold:
                return False

            last_failure = self._last_failure_time.get(recipient, 0)
            if time.time() - last_failure > self._timeout_seconds:
                self._failures[recipient] = 0
                return False

            return True

    def should_emit_circuit_event(self, recipient: str) -> bool:
        return self.record_failure(recipient)
