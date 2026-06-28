"""Placeholder for the relay server — returns a structured error, does not accept connections.

Per A4: the relay server (E2EE endpoint for remote UIs) is deferred
out of Plan 4 entirely. Remote UIs are explicitly a later deliverable.
This placeholder ensures any code that tries to use the relay gets a
clear, structured error rather than a silent failure or a connection
that hangs.
"""
from __future__ import annotations

from sovereignai.shared.trace_emitter import TraceEmitter
from sovereignai.shared.types import RelayNotSupportedError, TraceLevel


class RelayPlaceholder:
    """Stub that rejects all connection attempts with a structured error.

    This is NOT the real relay server. The real server will be
    implemented in a dedicated post-batch plan. Until then, any code
    that tries to use the relay gets a RelayNotSupportedError (per
    Finding 5 — Rev2) and a trace event.
    """

    def __init__(self, trace: TraceEmitter) -> None:
        """Create a relay placeholder that logs all connection attempts.

        Args:
            trace: Trace emitter for logging attempts (so the user can
                see if anything is trying to use the relay).
        """
        self._trace = trace

    def attempt_connection(self, source: str) -> None:
        """Reject a connection attempt by raising RelayNotSupportedError.

        Per Finding 5 (Rev2): raises a typed exception instead of
        returning a plain string. Callers catch RelayNotSupportedError
        programmatically to distinguish "relay not supported" from
        other errors.

        Args:
            source: Description of what tried to connect (e.g. "phone_app").

        Raises:
            RelayNotSupportedError: Always — the relay is not yet implemented.
        """
        self._trace.emit(
            component="RelayPlaceholder",
            level=TraceLevel.WARN,
            message=f"Connection attempt from {source!r} rejected — relay not yet supported",
        )
        raise RelayNotSupportedError()
