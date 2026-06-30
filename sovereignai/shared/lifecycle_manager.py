from __future__ import annotations

from collections import deque
from threading import Lock
from time import monotonic

from sovereignai.shared.trace_emitter import TraceEmitter
from sovereignai.shared.types import ComponentId, ComponentStatus, TraceLevel

CIRCUIT_BREAKER_THRESHOLD = 50      # errors
CIRCUIT_BREAKER_WINDOW_SECONDS = 10.0


class LifecycleManager:

    def __init__(self, trace: TraceEmitter) -> None:
        self._trace = trace
        self._statuses: dict[ComponentId, ComponentStatus] = {}
        self._error_log: dict[ComponentId, deque[float]] = {}
        self._lock = Lock()

    def register(self, component_id: ComponentId) -> None:
        with self._lock:
            self._statuses[component_id] = ComponentStatus.ACTIVE
            self._error_log[component_id] = deque()

    def get_status(self, component_id: ComponentId) -> ComponentStatus:
        with self._lock:
            return self._statuses.get(component_id, ComponentStatus.STOPPED)

    def try_recover(self, component_id: ComponentId) -> ComponentStatus:
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
        with self._lock:
            self._statuses[component_id] = status
        self._trace.emit(
            component="LifecycleManager",
            level=TraceLevel.INFO,
            message=f"Component {component_id} status set to {status}",
        )

    def reset(self, component_id: ComponentId) -> None:
        with self._lock:
            self._error_log[component_id] = deque()
            self._statuses[component_id] = ComponentStatus.ACTIVE
        self._trace.emit(
            component="LifecycleManager",
            level=TraceLevel.INFO,
            message=f"Component {component_id} reset to ACTIVE (error log cleared)",
        )

    def record_error(self, component_id: ComponentId) -> None:
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
