"""Track component health and enforce the circuit breaker rule.

Per AR16: a component that records more than 50 errors in 10 seconds
is automatically unloaded (circuit-broken). The Routing Engine queries
the Lifecycle Manager to skip circuit-broken components.

Per AR18: no component manages its own lifecycle. This module is the
sole authority for spawning, promoting, loading, and unloading.
"""
from __future__ import annotations

from collections import deque
from threading import Lock
from time import monotonic

from sovereignai.shared.trace_emitter import TraceEmitter
from sovereignai.shared.types import ComponentId, ComponentStatus, TraceLevel

CIRCUIT_BREAKER_THRESHOLD = 50      # errors
CIRCUIT_BREAKER_WINDOW_SECONDS = 10.0


class LifecycleManager:
    """Track component status and enforce the circuit breaker rule.

    Per AR16: a component that records more than 50 errors in 10 seconds
    is automatically unloaded (circuit-broken). The Routing Engine queries
    the Lifecycle Manager to skip circuit-broken components.

    Per AR18: no component manages its own lifecycle. This module is the
    sole authority for spawning, promoting, loading, and unloading.

    Per Finding 2 (Rev2): circuit breaker now auto-recovers. If
    `get_status()` is called and the error window has expired (no errors
    in the last 10 seconds), status flips from CIRCUIT_BROKEN back to
    ACTIVE. A `reset()` method is also provided for explicit recovery.

    Per Finding 4 (Rev2): emits an ERROR trace when the circuit breaks.
    """

    def __init__(self, trace: TraceEmitter) -> None:
        """Create a lifecycle manager instance with no registered components yet.

        Args:
            trace: Trace emitter for logging circuit-breaker trips and
                status changes (per Finding 4 — P9 observability).
        """
        self._trace = trace
        self._statuses: dict[ComponentId, ComponentStatus] = {}
        self._error_log: dict[ComponentId, deque[float]] = {}
        self._lock = Lock()

    def register(self, component_id: ComponentId) -> None:
        """Start tracking a component with ACTIVE status in the lifecycle manager.

        Args:
            component_id: The component to register.
        """
        with self._lock:
            self._statuses[component_id] = ComponentStatus.ACTIVE
            self._error_log[component_id] = deque()

    def get_status(self, component_id: ComponentId) -> ComponentStatus:
        """Return the current status of a registered component as a read-only value.

        Per Finding 7 (Rev3): this method is now read-only. It returns
        the current status WITHOUT auto-recovering. Auto-recovery moved
        to `try_recover()` which callers invoke explicitly. This separates
        "what is the status?" from "should we attempt recovery?" — the
        conflation in Rev2 caused semantic unsoundness (a component never
        queried stayed broken forever; a single query flipped it).

        Args:
            component_id: The component to query.

        Returns:
            ComponentStatus. Returns STOPPED if the component was
            never registered (defensive default).
        """
        with self._lock:
            return self._statuses.get(component_id, ComponentStatus.STOPPED)

    def try_recover(self, component_id: ComponentId) -> ComponentStatus:
        """Attempt recovery; return resulting status (single locked call per Rev5 Finding 5)."""
        now = monotonic()
        recovered = False
        with self._lock:
            status = self._statuses.get(component_id, ComponentStatus.STOPPED)
            if status is ComponentStatus.CIRCUIT_BROKEN:
                log = self._error_log.get(component_id, deque())
                cutoff = now - CIRCUIT_BREAKER_WINDOW_SECONDS
                while log and log[0] < cutoff:
                    log.popleft()
                if len(log) == 0:
                    self._statuses[component_id] = ComponentStatus.ACTIVE
                    status = ComponentStatus.ACTIVE
                    recovered = True
        if recovered:
            self._trace.emit(
                component="LifecycleManager",
                level=TraceLevel.INFO,
                message=f"Component {component_id} recovered to ACTIVE (error window expired)",
            )
        return status

    def set_status(self, component_id: ComponentId, status: ComponentStatus) -> None:
        """Manually set a component's status (per Finding 6 — Rev2).

        Use for operational signals: degrade a component under load, stop
        a component for maintenance. The circuit breaker's auto-trip
        (record_error) and auto-recover (get_status) still apply on top
        of this manual setting.

        Args:
            component_id: The component to update.
            status: The new status.
        """
        with self._lock:
            self._statuses[component_id] = status
        self._trace.emit(
            component="LifecycleManager",
            level=TraceLevel.INFO,
            message=f"Component {component_id} status set to {status}",
        )

    def reset(self, component_id: ComponentId) -> None:
        """Clear a component's error log and restore ACTIVE status (per Finding 2 — Rev2).

        Use after fixing the underlying cause of a circuit break, or to
        force recovery without waiting for the window to expire.

        Args:
            component_id: The component to reset.
        """
        with self._lock:
            self._error_log[component_id] = deque()
            self._statuses[component_id] = ComponentStatus.ACTIVE
        self._trace.emit(
            component="LifecycleManager",
            level=TraceLevel.INFO,
            message=f"Component {component_id} reset to ACTIVE (error log cleared)",
        )

    def record_error(self, component_id: ComponentId) -> None:
        """Record one error for a component and check the circuit breaker.

        If the rolling 10-second error count exceeds the threshold
        (50 per AR16), the component is automatically circuit-broken.
        Per Finding 4 (Rev2): emits an ERROR trace when the circuit
        breaks, so operators can see the trip in the Log drawer.

        Args:
            component_id: The component that experienced an error.
        """
        now = monotonic()
        with self._lock:
            log = self._error_log.setdefault(component_id, deque())
            log.append(now)
            # Drop entries outside the window
            cutoff = now - CIRCUIT_BREAKER_WINDOW_SECONDS
            while log and log[0] < cutoff:
                log.popleft()
            # Check threshold (AR16: "more than 50" — exclusive, trips at 51)
            if len(log) > CIRCUIT_BREAKER_THRESHOLD:
                if self._statuses.get(component_id) != ComponentStatus.CIRCUIT_BROKEN:
                    self._statuses[component_id] = ComponentStatus.CIRCUIT_BROKEN
                    # Emit trace outside the lock to avoid deadlock on TraceEmitter
                    tripped = True
                    error_count = len(log)
                else:
                    tripped = False
                    error_count = len(log)
            else:
                tripped = False
                error_count = len(log)
        if tripped:
            self._trace.emit(
                component="LifecycleManager",
                level=TraceLevel.ERROR,
                message=(
                    f"Circuit breaker tripped for {component_id} "
                    f"({error_count} errors in {CIRCUIT_BREAKER_WINDOW_SECONDS}s)"
                ),
            )
