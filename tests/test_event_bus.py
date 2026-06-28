"""Tests for the event bus implementation.

Per Q9 resolution: conformance + contract + property-based testing.
Verifies in-order delivery per channel (A9) and no silent failures (P10).
"""
from __future__ import annotations

from uuid import uuid4

import pytest

from sovereignai.shared.event_bus import EventBus
from sovereignai.shared.trace_emitter import TraceEmitter
from sovereignai.shared.types import Channel, Event, TraceLevel, now_utc


@pytest.fixture
def trace_emitter() -> TraceEmitter:
    """Provide a fresh trace emitter for each test."""
    return TraceEmitter()


@pytest.fixture
def event_bus(trace_emitter: TraceEmitter) -> EventBus:
    """Provide a fresh event bus for each test."""
    return EventBus(trace=trace_emitter)


@pytest.fixture
def sample_event() -> Event:
    """Provide a sample event for testing."""
    return Event(
        channel=Channel("test-channel"),
        correlation_id=uuid4(),
        timestamp=now_utc(),
    )


def test_subscribe_and_publish_delivers_event(
    event_bus: EventBus,
    sample_event: Event,
) -> None:
    """Verify that a single subscriber receives the published event."""
    received_events: list[Event] = []

    def subscriber(event: Event) -> None:
        received_events.append(event)

    event_bus.subscribe(Channel("test-channel"), subscriber)
    event_bus.publish(sample_event)

    assert len(received_events) == 1
    assert received_events[0] is sample_event


def test_multiple_subscribers_receive_in_registration_order(
    event_bus: EventBus,
    sample_event: Event,
) -> None:
    """Verify that multiple subscribers receive events in registration order (A9)."""
    received_order: list[str] = []

    def subscriber_a(event: Event) -> None:
        received_order.append("a")

    def subscriber_b(event: Event) -> None:
        received_order.append("b")

    def subscriber_c(event: Event) -> None:
        received_order.append("c")

    event_bus.subscribe(Channel("test-channel"), subscriber_a)
    event_bus.subscribe(Channel("test-channel"), subscriber_b)
    event_bus.subscribe(Channel("test-channel"), subscriber_c)
    event_bus.publish(sample_event)

    assert received_order == ["a", "b", "c"]


def test_subscriber_exception_does_not_silently_swallow(
    event_bus: EventBus,
    sample_event: Event,
    trace_emitter: TraceEmitter,
) -> None:
    """Verify that subscriber exceptions are logged at ERROR and next subscriber still receives."""
    received_by_second: list[Event] = []

    def failing_subscriber(event: Event) -> None:
        raise ValueError("Test exception")

    def second_subscriber(event: Event) -> None:
        received_by_second.append(event)

    event_bus.subscribe(Channel("test-channel"), failing_subscriber)
    event_bus.subscribe(Channel("test-channel"), second_subscriber)
    event_bus.publish(sample_event)

    # Second subscriber should still receive the event
    assert len(received_by_second) == 1
    assert received_by_second[0] is sample_event

    # Trace emitter should have logged the error
    error_events = trace_emitter.get_events(level=TraceLevel.ERROR)
    assert len(error_events) > 0
    assert any("ValueError" in event.message for event in error_events)


def test_unrelated_channels_are_isolated(
    event_bus: EventBus,
    sample_event: Event,
) -> None:
    """Verify that a subscriber on channel A does not receive channel B's events."""
    received_on_a: list[Event] = []
    received_on_b: list[Event] = []

    def subscriber_a(event: Event) -> None:
        received_on_a.append(event)

    def subscriber_b(event: Event) -> None:
        received_on_b.append(event)

    event_bus.subscribe(Channel("channel-a"), subscriber_a)
    event_bus.subscribe(Channel("channel-b"), subscriber_b)

    event_a = Event(
        channel=Channel("channel-a"),
        correlation_id=uuid4(),
        timestamp=now_utc(),
    )
    event_bus.publish(event_a)

    assert len(received_on_a) == 1
    assert len(received_on_b) == 0


def test_publish_to_empty_channel_is_noop(
    event_bus: EventBus,
    sample_event: Event,
) -> None:
    """Verify that publishing to a channel with no subscribers is a no-op."""
    # No subscribers registered
    event_bus.publish(sample_event)

    # Should not raise an error
    assert True


def test_trace_emitter_called_on_subscriber_failure(
    event_bus: EventBus,
    sample_event: Event,
    trace_emitter: TraceEmitter,
) -> None:
    """Verify that the bus emits a TraceEvent at ERROR level when a subscriber raises."""
    def failing_subscriber(event: Event) -> None:
        raise RuntimeError("Subscriber failed")

    event_bus.subscribe(Channel("test-channel"), failing_subscriber)
    event_bus.publish(sample_event)

    error_events = trace_emitter.get_events(level=TraceLevel.ERROR)
    assert len(error_events) > 0
    assert any("RuntimeError" in event.message for event in error_events)


def test_concurrent_publish_and_subscribe(event_bus: EventBus) -> None:
    """Verify that concurrent publish and subscribe operations are thread-safe."""
    import threading
    received_events: list[Event] = []
    lock = threading.Lock()

    def subscriber(event: Event) -> None:
        with lock:
            received_events.append(event)

    event_bus.subscribe(Channel("test-channel"), subscriber)

    def publish_many() -> None:
        for _i in range(10):
            event = Event(
                channel=Channel("test-channel"),
                correlation_id=uuid4(),
                timestamp=now_utc(),
            )
            event_bus.publish(event)

    # Spawn 5 threads, each publishing 10 events
    threads = [threading.Thread(target=publish_many) for _ in range(5)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    # Should receive 50 events total
    assert len(received_events) == 50
