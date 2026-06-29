"""Trace emitter — the single observability surface for all components.

Every component receives a TraceEmitter via constructor injection (per
AR4, AR6). Components emit structured trace events; the emitter records
them. The emitter is a singleton (per AR4) — one instance per process,
shared across all components.

The emitter is NOT a context bag (per AR6). It carries trace data only
— never business logic, configuration, or cross-component state.
"""
from __future__ import annotations

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
    """Record trace events from all components in a single in-memory log.

    The emitter is the sole observability surface (per P9). Components
    call emit() to record events; the Log drawer (in a UI process, built
    later) reads from this log via the Capability API (Plan 4).

    This is a singleton per AR4 — one instance per process, registered
    in the DI container. Components receive it via constructor injection.

    Thread-safe: multiple components may emit concurrently.
    """

    def __init__(self, max_events: int = 10000) -> None:
        """Create an empty trace emitter with a bounded in-memory log.

        Args:
            max_events: Maximum number of events to retain. When the log
                exceeds this, oldest events are dropped first. Keeps
                memory bounded over long-running sessions.
        """
        self._events: list[TraceEvent] = []
        self._lock = Lock()
        self._max_events = max_events
        self._callbacks: list[callable] = []

    def emit(
        self,
        component: str,
        level: TraceLevel,
        message: str,
        correlation_id: UUID | None = None,
    ) -> None:
        """Record a single trace event from a named component into the in-memory log.

        Args:
            component: Name of the emitting component (e.g. "EventBus").
            level: Severity of the event.
            message: Plain-English description of what happened.
            correlation_id: Optional UUID grouping events from the same
                task. If None, the event is uncorrelated.
        """
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
            for callback in self._callbacks:
                try:
                    callback(event)
                except Exception:
                    # Callback failures must not break emission
                    pass

    def get_events(
        self, level: TraceLevel | None = None, component: str | None = None
    ) -> list[TraceEvent]:
        """Return a filtered list of recorded trace events from the in-memory log.

        Args:
            level: If provided, return only events at this level or above.
            component: If provided, return only events from this component.

        Returns:
            List of matching events, oldest first.
        """
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

    def subscribe_callback(self, callback: callable) -> None:
        """Register a callback function to be invoked on every trace event emission.

        The callback receives the TraceEvent object as its sole argument.
        This enables durable persistence (e.g. writing to SQLite) without
        coupling the emitter to any specific storage backend.

        Args:
            callback: A function accepting a single TraceEvent argument.
        """
        with self._lock:
            self._callbacks.append(callback)
