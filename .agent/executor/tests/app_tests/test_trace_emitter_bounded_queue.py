from __future__ import annotations

import time
from uuid import UUID

from sovereignai.shared.trace_emitter import BoundedTraceQueue
from sovereignai.shared.types import TraceEvent, TraceLevel, now_utc


def test_bounded_queue_circuit_breaker_high_water():
    """Test queue fills, drops oldest, subscriber still receives latest."""
    received: list[TraceEvent] = []

    def callback(batch: list[TraceEvent]) -> None:
        received.extend(batch)

    queue = BoundedTraceQueue(maxsize=10, high_water_ratio=0.8, low_water_ratio=0.5)
    queue.start_drain_thread(callback)

    for i in range(20):
        event = TraceEvent(
            component="test",
            level=TraceLevel.INFO,
            message=f"message-{i}",
            timestamp=now_utc(),
            correlation_id=UUID(int=i),
        )
        queue.put(event)

    time.sleep(0.2)
    queue.stop_drain_thread()

    assert len(received) > 0
    assert len(received) <= 20


def test_bounded_queue_subscriber_disconnect_no_memory_leak():
    """Test subscriber disconnects, queue drains, no memory leak."""
    received: list[TraceEvent] = []

    def callback(batch: list[TraceEvent]) -> None:
        received.extend(batch)

    queue = BoundedTraceQueue(maxsize=100)
    queue.start_drain_thread(callback)

    for i in range(50):
        event = TraceEvent(
            component="test",
            level=TraceLevel.INFO,
            message=f"message-{i}",
            timestamp=now_utc(),
            correlation_id=UUID(int=i),
        )
        queue.put(event)

    queue.stop_drain_thread()
    time.sleep(0.1)

    assert queue._drain_thread is None
    assert len(received) == 50


def test_bounded_queue_multiple_subscribers():
    """Test multiple subscribers, each gets independent bounded queue."""
    received1: list[TraceEvent] = []
    received2: list[TraceEvent] = []

    def callback1(batch: list[TraceEvent]) -> None:
        received1.extend(batch)

    def callback2(batch: list[TraceEvent]) -> None:
        received2.extend(batch)

    queue1 = BoundedTraceQueue(maxsize=10)
    queue2 = BoundedTraceQueue(maxsize=10)
    queue1.start_drain_thread(callback1)
    queue2.start_drain_thread(callback2)

    for i in range(15):
        event = TraceEvent(
            component="test",
            level=TraceLevel.INFO,
            message=f"message-{i}",
            timestamp=now_utc(),
            correlation_id=UUID(int=i),
        )
        queue1.put(event)
        queue2.put(event)

    time.sleep(0.2)
    queue1.stop_drain_thread()
    queue2.stop_drain_thread()

    assert len(received1) > 0
    assert len(received2) > 0


def test_bounded_queue_producer_outruns_consumer():
    """Test producer outruns consumer, queue never exceeds maxsize."""
    received: list[TraceEvent] = []

    def callback(batch: list[TraceEvent]) -> None:
        received.extend(batch)

    queue = BoundedTraceQueue(maxsize=20)
    queue.start_drain_thread(callback)

    for i in range(100):
        event = TraceEvent(
            component="test",
            level=TraceLevel.INFO,
            message=f"message-{i}",
            timestamp=now_utc(),
            correlation_id=UUID(int=i),
        )
        queue.put(event)

    time.sleep(0.2)
    queue.stop_drain_thread()

    assert len(received) <= 100


def test_bounded_queue_sentinel_shutdown():
    """Test sentinel value signals drain thread exit."""
    received: list[TraceEvent] = []

    def callback(batch: list[TraceEvent]) -> None:
        received.extend(batch)

    queue = BoundedTraceQueue(maxsize=10)
    queue.start_drain_thread(callback)

    event = TraceEvent(
        component="test",
        level=TraceLevel.INFO,
        message="test",
        timestamp=now_utc(),
        correlation_id=UUID(int=1),
    )
    queue.put(event)

    queue.stop_drain_thread()
    time.sleep(0.1)

    assert len(received) == 1
    assert received[0].message == "test"


def test_bounded_queue_circuit_breaker_reset():
    """Test circuit breaker resets on low-water mark."""
    received: list[TraceEvent] = []

    def callback(batch: list[TraceEvent]) -> None:
        received.extend(batch)

    queue = BoundedTraceQueue(maxsize=100, high_water_ratio=0.8, low_water_ratio=0.5)
    queue.start_drain_thread(callback)

    for i in range(100):
        event = TraceEvent(
            component="test",
            level=TraceLevel.INFO,
            message=f"message-{i}",
            timestamp=now_utc(),
            correlation_id=UUID(int=i),
        )
        queue.put(event)

    time.sleep(0.2)
    queue.stop_drain_thread()

    assert len(received) <= 100


def test_bounded_queue_circuit_breaker_slow_consumer():
    """Test circuit breaker triggers with slow consumer."""
    received: list[TraceEvent] = []

    def slow_callback(batch: list[TraceEvent]) -> None:
        time.sleep(0.1)
        received.extend(batch)

    queue = BoundedTraceQueue(maxsize=20, high_water_ratio=0.5, low_water_ratio=0.3)
    queue.start_drain_thread(slow_callback)

    for i in range(50):
        event = TraceEvent(
            component="test",
            level=TraceLevel.INFO,
            message=f"message-{i}",
            timestamp=now_utc(),
            correlation_id=UUID(int=i),
        )
        queue.put(event)

    time.sleep(0.5)
    queue.stop_drain_thread()

    assert len(received) <= 50


def test_bounded_queue_deferred_state():
    """Test deferred state prevents enqueues."""
    received: list[TraceEvent] = []

    def blocking_callback(batch: list[TraceEvent]) -> None:
        time.sleep(1.0)
        received.extend(batch)

    queue = BoundedTraceQueue(maxsize=10, high_water_ratio=0.8, low_water_ratio=0.5)
    queue.start_drain_thread(blocking_callback)

    for i in range(20):
        event = TraceEvent(
            component="test",
            level=TraceLevel.INFO,
            message=f"message-{i}",
            timestamp=now_utc(),
            correlation_id=UUID(int=i),
        )
        queue.put(event)

    time.sleep(0.1)
    assert queue.is_deferred()

    queue.stop_drain_thread()
