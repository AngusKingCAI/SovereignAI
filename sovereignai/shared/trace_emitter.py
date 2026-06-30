from __future__ import annotations

from collections.abc import Callable
from threading import Lock
from typing import TYPE_CHECKING
from uuid import UUID

from sovereignai.shared.types import TraceEvent, TraceLevel, new_correlation_id, now_utc

if TYPE_CHECKING:
    pass

# O(1) level priority mapping for performance (S2.12)
TRACE_LEVEL_PRIORITY: dict[TraceLevel, int] = {
    TraceLevel.TRACE: 0,
    TraceLevel.DEBUG: 1,
    TraceLevel.INFO: 2,
    TraceLevel.WARN: 3,
    TraceLevel.ERROR: 4,
}


class TraceEmitter:

    def __init__(self, max_events: int = 10000) -> None:
        self._events: list[TraceEvent] = []
        self._lock = Lock()
        self._max_events = max_events
        self._callbacks: list[Callable[[TraceEvent], None]] = []

    def emit(
        self,
        component: str,
        level: TraceLevel,
        message: str,
        correlation_id: UUID | None = None,
    ) -> None:
        # Import here to avoid circular import at module load
        event = TraceEvent(
            component=component,
            level=level,
            message=message,
            timestamp=now_utc(),
            correlation_id=correlation_id or new_correlation_id(),
        )
        with self._lock:
            self._events.append(event)
            if len(self._events) > self._max_events:
                self._events.pop(0)
            # Notify all registered callbacks for durable persistence
            import contextlib
            for callback in self._callbacks:
                with contextlib.suppress(Exception):
                    callback(event)

    def get_events(
        self, level: TraceLevel | None = None, component: str | None = None
    ) -> list[TraceEvent]:
        with self._lock:
            events = list(self._events)
        if level is not None:
            # Ordered comparison via O(1) priority lookup (S2.12)
            min_priority = TRACE_LEVEL_PRIORITY[level]
            events = [
                e for e in events if TRACE_LEVEL_PRIORITY[e.level] >= min_priority
            ]
        if component is not None:
            events = [e for e in events if e.component == component]
        return events

    def subscribe_callback(self, callback: Callable[[TraceEvent], None]) -> None:
        with self._lock:
            self._callbacks.append(callback)
