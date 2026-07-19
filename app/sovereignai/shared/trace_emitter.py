from __future__ import annotations

import contextlib
import queue
import threading
import time
from collections import deque
from collections.abc import Callable
from threading import Lock
from typing import TYPE_CHECKING

from sovereignai.shared.types import (
    TraceEvent,
    TraceLevel,
    current_correlation_id,
    new_correlation_id,
    now_utc,
)
from sovereignai.shared.types_base import CorrelationId

if TYPE_CHECKING:
    pass


class _DrainShutdown:
    """Sentinel class for signaling drain thread exit (DD-20.10.2)."""
    __slots__ = ()


DRAIN_SHUTDOWN = _DrainShutdown()


class BoundedTraceQueue:
    """Bounded queue with circuit breaker pattern for trace events (DD-20.10.1)."""

    def __init__(
        self,
        maxsize: int = 1000,
        high_water_ratio: float = 0.9,
        low_water_ratio: float = 0.5,
        emit_callback: Callable[[TraceEvent], None] | None = None,
    ) -> None:
        self._queue: queue.Queue[TraceEvent | _DrainShutdown] = queue.Queue(maxsize=maxsize)
        self._maxsize = maxsize
        self._high_water = int(maxsize * high_water_ratio)
        self._low_water = int(maxsize * low_water_ratio)
        self._emit_callback = emit_callback
        self._deferred = False
        self._drop_counter = 0
        self._overload_start_time: float | None = None
        self._lock = Lock()
        self._drain_thread: threading.Thread | None = None
        self._shutdown_event = threading.Event()

    def put(self, event: TraceEvent, timeout: float = 0.1) -> bool:
        """Put event in queue. Returns True if enqueued, False if dropped."""
        if self._deferred:
            with self._lock:
                self._drop_counter += 1
            return False

        try:
            self._queue.put(event, block=False, timeout=timeout)
            self._check_high_water()
            return True
        except queue.Full:
            self._trip_circuit_breaker()
            with self._lock:
                self._drop_counter += 1
            if self._emit_callback:
                with contextlib.suppress(Exception):
                    self._emit_callback(
                        TraceEvent(
                            component="BoundedTraceQueue",
                            level=TraceLevel.WARN,
                            message="queue.put.full: dropped event",
                            timestamp=now_utc(),
                            correlation_id=event.correlation_id,
                        )
                    )
            return False

    def _check_high_water(self) -> None:
        """Check if queue hit high-water mark and trip circuit breaker if needed."""
        if self._queue.qsize() >= self._high_water and not self._deferred:
            self._trip_circuit_breaker()

    def _trip_circuit_breaker(self) -> None:
        """Trip circuit breaker on high-water mark (DD-20.10.1)."""
        with self._lock:
            if self._deferred:
                return
            self._deferred = True
            self._overload_start_time = time.time()

        if self._emit_callback:
            msg = f"queue.overload.start: {self._high_water}/{self._maxsize}"
            with contextlib.suppress(Exception):
                self._emit_callback(
                    TraceEvent(
                        component="BoundedTraceQueue",
                        level=TraceLevel.WARN,
                        message=msg,
                        timestamp=now_utc(),
                        correlation_id=new_correlation_id(),
                    )
                )

    def _check_low_water(self) -> None:
        """Check if queue dropped to low-water mark and reset circuit breaker if needed."""
        if self._queue.qsize() <= self._low_water and self._deferred:
            self._reset_circuit_breaker()

    def _reset_circuit_breaker(self) -> None:
        """Reset circuit breaker on low-water mark (DD-20.10.1)."""
        with self._lock:
            if not self._deferred:
                return
            drops = self._drop_counter
            start_time = self._overload_start_time
            duration = time.time() - start_time if start_time else 0.0
            self._deferred = False
            self._drop_counter = 0
            self._overload_start_time = None

        if self._emit_callback:
            msg = f"queue.overload.end: drops={drops}, duration={duration:.2f}s"
            with contextlib.suppress(Exception):
                self._emit_callback(
                    TraceEvent(
                        component="BoundedTraceQueue",
                        level=TraceLevel.INFO,
                        message=msg,
                        timestamp=now_utc(),
                        correlation_id=new_correlation_id(),
                    )
                )

    def start_drain_thread(self, callback: Callable[[list[TraceEvent]], None]) -> None:
        """Start drain thread that batches events and calls callback."""
        if self._drain_thread is not None:
            return

        def drain_worker() -> None:
            batch: list[TraceEvent] = []
            while not self._shutdown_event.is_set():
                try:
                    item = self._queue.get(timeout=0.1)
                    if item is DRAIN_SHUTDOWN:
                        break
                    if isinstance(item, TraceEvent):
                        batch.append(item)
                    if len(batch) >= 50:
                        callback(batch)
                        batch = []
                        self._check_low_water()
                except queue.Empty:
                    if batch:
                        callback(batch)
                        batch = []
                        self._check_low_water()
            if batch:
                callback(batch)

        self._drain_thread = threading.Thread(target=drain_worker, daemon=True)
        self._drain_thread.start()

    def stop_drain_thread(self, timeout: float = 5.0) -> None:
        """Stop drain thread with sentinel value (DD-20.10.2)."""
        if self._drain_thread is None:
            return

        self._queue.put(DRAIN_SHUTDOWN, block=False)
        self._drain_thread.join(timeout=timeout)
        if self._drain_thread.is_alive():
            pending = self._queue.qsize()
            if self._emit_callback:
                msg = f"queue.drain.timeout: pending={pending}"
                with contextlib.suppress(Exception):
                    self._emit_callback(
                        TraceEvent(
                            component="BoundedTraceQueue",
                            level=TraceLevel.WARN,
                            message=msg,
                            timestamp=now_utc(),
                            correlation_id=new_correlation_id(),
                        )
                    )
        self._drain_thread = None

    def is_deferred(self) -> bool:
        """Check if circuit breaker is currently tripped."""
        with self._lock:
            return self._deferred

    def drop_count(self) -> int:
        """Get total drop count since last circuit breaker reset."""
        with self._lock:
            return self._drop_counter

# O(1) level priority mapping for performance (S2.12)
TRACE_LEVEL_PRIORITY: dict[TraceLevel, int] = {
    TraceLevel.TRACE: 0,
    TraceLevel.DEBUG: 1,
    TraceLevel.INFO: 2,
    TraceLevel.WARN: 3,
    TraceLevel.ERROR: 4,
    TraceLevel.CRITICAL: 5,
}


class _SubscriberQueue:
    """Wrapper for subscriber callback with bounded queue."""

    def __init__(
        self,
        callback: Callable[[TraceEvent], None],
        max_queue_size: int = 1000,
        emit_callback: Callable[[TraceEvent], None] | None = None,
    ) -> None:
        self._callback = callback
        self._queue = BoundedTraceQueue(
            maxsize=max_queue_size,
            emit_callback=emit_callback,
        )
        self._queue.start_drain_thread(self._drain_callback)

    def _drain_callback(self, batch: list[TraceEvent]) -> None:
        """Call subscriber callback with batch of events."""
        for event in batch:
            with contextlib.suppress(Exception):
                self._callback(event)

    def put(self, event: TraceEvent) -> bool:
        """Put event in subscriber queue."""
        return self._queue.put(event)

    def stop(self) -> None:
        """Stop drain thread for this subscriber."""
        self._queue.stop_drain_thread()


class TraceEmitter:

    def __init__(self, max_events: int = 10000) -> None:
        self._events: list[TraceEvent] = []
        self._lock = Lock()
        self._max_events = max_events
        self._subscribers: list[_SubscriberQueue] = []
        self._recent_events: deque[TraceEvent] = deque(maxlen=500)

    def emit(
        self,
        component: str,
        level: TraceLevel,
        message: str,
        correlation_id: CorrelationId | None = None,
    ) -> None:
        if correlation_id is None:
            correlation_id = current_correlation_id() or new_correlation_id()
        event = TraceEvent(
            component=component,
            level=level,
            message=message,
            timestamp=now_utc(),
            correlation_id=correlation_id,
        )
        with self._lock:
            self._events.append(event)
            if len(self._events) > self._max_events:
                self._events.pop(0)
            self._recent_events.append(event)
            for subscriber in self._subscribers:
                try:
                    subscriber.put(event)
                except Exception:
                    with contextlib.suppress(Exception):
                        internal_event = TraceEvent(
                            component="TraceEmitter",
                            level=TraceLevel.ERROR,
                            message="Subscriber callback failed",
                            timestamp=now_utc(),
                            correlation_id=correlation_id,
                        )
                        self._events.append(internal_event)

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

    def recent_events(self) -> list[TraceEvent]:
        with self._lock:
            return list(self._recent_events)

    def subscribe_callback(
        self,
        callback: Callable[[TraceEvent], None],
        max_queue_size: int = 1000,
    ) -> Callable[[], None]:
        subscriber = _SubscriberQueue(
            callback,
            max_queue_size=max_queue_size,
            emit_callback=self._emit_internal,
        )
        with self._lock:
            self._subscribers.append(subscriber)

        def unsubscribe() -> None:
            with self._lock:
                if subscriber in self._subscribers:
                    self._subscribers.remove(subscriber)
            subscriber.stop()

        return unsubscribe

    def _emit_internal(self, event: TraceEvent) -> None:
        """Emit internal event (e.g., queue overload warnings)."""
        with self._lock, contextlib.suppress(Exception):
            self._events.append(event)
            if len(self._events) > self._max_events:
                self._events.pop(0)
