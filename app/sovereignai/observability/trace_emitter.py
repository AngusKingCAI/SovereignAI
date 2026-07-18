from __future__ import annotations

from sovereignai.shared.event_bus import EventBus
from sovereignai.shared.trace_emitter import TraceEmitter
from sovereignai.shared.types import TraceLevel


class TraceEmitterWrapper:
    """Wraps TraceEmitter to bridge with EventBus for structured trace events."""

    def __init__(self, event_bus: EventBus, inner: TraceEmitter) -> None:
        self._event_bus = event_bus
        self._inner = inner

    def emit_event(
        self, event_name: str, payload: dict, level: TraceLevel = TraceLevel.INFO
    ) -> None:
        """Emit a trace event via EventBus when started, otherwise fallback to inner emitter."""
        # Prefix with "trace." if not already (case-insensitive)
        if not event_name.lower().startswith("trace."):
            prefixed_name = f"trace.{event_name}"
        else:
            prefixed_name = event_name

        if self._event_bus.is_started:
            # Event doesn't have payload field - include in correlation_id or use metadata
            # For now, we'll include payload info in the message via inner emitter
            # Note: extend Event type to support structured payload if needed
            self._inner.emit(
                component="trace",
                level=level,
                message=f"{prefixed_name}: {payload}",
            )
        else:
            # Fallback to inner emitter when EventBus not started
            self._inner.emit(
                component="trace",
                level=level,
                message=f"{prefixed_name}: {payload}",
            )
