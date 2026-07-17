from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
from threading import Lock
from typing import TYPE_CHECKING

from app.sovereignai.shared.types import TraceEvent

if TYPE_CHECKING:
    from collections.abc import Callable


class FileTraceSubscriber:

    def __init__(self, log_dir: str = "app/logs") -> None:
        self._log_dir = Path(log_dir)
        self._log_dir.mkdir(parents=True, exist_ok=True)
        filename = datetime.now(UTC).strftime("%Y-%m-%d_%H-%M-%S.log")
        self._file_path = self._log_dir / filename
        self._file = open(self._file_path, "a", encoding="utf-8")  # noqa: SIM115
        self._lock = Lock()
        self._unsubscribe: Callable[[], None] | None = None

    def __call__(self, event: TraceEvent) -> None:
        try:
            line = json.dumps(
                {
                    "timestamp": event.timestamp,
                    "level": event.level,
                    "component": event.component,
                    "message": event.message,
                    "correlation_id": event.correlation_id,
                },
                default=str,
            )
            with self._lock:
                self._file.write(line + "\n")
                self._file.flush()
        except Exception:
            pass

    def close(self) -> None:
        self._file.close()

    def unsubscribe(self) -> None:
        if self._unsubscribe:
            self._unsubscribe()
        self.close()
