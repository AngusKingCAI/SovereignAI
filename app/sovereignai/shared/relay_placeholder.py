from __future__ import annotations

from app.sovereignai.shared.trace_emitter import TraceEmitter
from app.sovereignai.shared.types import RelayNotSupportedError, TraceLevel


class RelayPlaceholder:

    def __init__(self, trace: TraceEmitter) -> None:
        self._trace = trace

    def attempt_connection(self, source: str) -> None:
        self._trace.emit(
            component="RelayPlaceholder",
            level=TraceLevel.WARN,
            message=f"Connection attempt from {source!r} rejected — relay not yet supported",
        )
        raise RelayNotSupportedError()
