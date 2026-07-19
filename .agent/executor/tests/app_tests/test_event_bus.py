from __future__ import annotations

from uuid import uuid4

import pytest
from sovereignai.shared.event_bus import EventBus
from sovereignai.shared.event_registry import EventRegistry
from sovereignai.shared.trace_emitter import TraceEmitter
from sovereignai.shared.types import Channel, Event, TraceLevel, now_utc


@pytest.fixture
def trace_emitter() -> TraceEmitter:
    return TraceEmitter()

@pytest.fixture
def event_bus(trace_emitter: TraceEmitter) -> EventBus:
    # For legacy sync publish/subscribe tests, don't start the bus
    # and don't use registry - just use the old sync interface
    from sovereignai.shared.event_bus import EventBus
    registry = EventRegistry()
    return EventBus(trace=trace_emitter, registry=registry)

@pytest.fixture
def sample_event() -> Event:
    return Event(
        channel=Channel('test-channel'),
        correlation_id=uuid4(),
        timestamp=now_utc(),
        version=1,
        trace_level=TraceLevel.INFO,
        payload={}
    )

def test_subscribe_and_publish_delivers_event(event_bus: EventBus, sample_event: Event) -> None:
    received_events: list[Event] = []

    def subscriber(event: Event) -> None:
        received_events.append(event)
    event_bus.subscribe(Channel('test-channel'), subscriber)
    event_bus.start()
    event_bus.publish(sample_event)
    event_bus.stop()
    assert len(received_events) == 1

def test_multiple_subscribers_receive_in_registration_order(  # noqa: E501
    event_bus: EventBus,
    sample_event: Event
) -> None:
    received_order: list[str] = []

    def subscriber_a(event: Event) -> None:
        received_order.append('a')

    def subscriber_b(event: Event) -> None:
        received_order.append('b')

    def subscriber_c(event: Event) -> None:
        received_order.append('c')
    event_bus.subscribe(Channel('test-channel'), subscriber_a)
    event_bus.subscribe(Channel('test-channel'), subscriber_b)
    event_bus.subscribe(Channel('test-channel'), subscriber_c)
    event_bus.start()
    event_bus.publish(sample_event)
    event_bus.stop()
    assert received_order == ['a', 'b', 'c']

def test_subscriber_exception_does_not_silently_swallow(  # noqa: E501
    event_bus: EventBus,
    sample_event: Event,
    trace_emitter: TraceEmitter
) -> None:
    received_by_second: list[Event] = []

    def failing_subscriber(event: Event) -> None:
        raise ValueError('Test exception')

    def second_subscriber(event: Event) -> None:
        received_by_second.append(event)
    event_bus.subscribe(Channel('test-channel'), failing_subscriber)
    event_bus.subscribe(Channel('test-channel'), second_subscriber)
    event_bus.start()
    event_bus.publish(sample_event)
    event_bus.stop()
    assert len(received_by_second) == 1
    error_events = trace_emitter.get_events(level=TraceLevel.ERROR)
    assert len(error_events) > 0
    assert any('ValueError' in event.message for event in error_events)

def test_unrelated_channels_are_isolated(event_bus: EventBus, sample_event: Event) -> None:
    received_on_a: list[Event] = []
    received_on_b: list[Event] = []

    def subscriber_a(event: Event) -> None:
        received_on_a.append(event)

    def subscriber_b(event: Event) -> None:
        received_on_b.append(event)
    event_bus.subscribe(Channel('channel-a'), subscriber_a)
    event_bus.subscribe(Channel('channel-b'), subscriber_b)
    event_a = Event(
        channel=Channel('channel-a'),
        correlation_id=uuid4(),
        timestamp=now_utc(),
        version=1,
        trace_level=TraceLevel.INFO,
        payload={}
    )
    event_bus.start()
    event_bus.publish(event_a)
    event_bus.stop()
    assert len(received_on_a) == 1
    assert len(received_on_b) == 0

def test_publish_to_empty_channel_is_noop(event_bus: EventBus, sample_event: Event) -> None:
    event_bus.publish(sample_event)
    assert True

def test_trace_emitter_called_on_subscriber_failure(  # noqa: E501
    event_bus: EventBus,
    sample_event: Event,
    trace_emitter: TraceEmitter
) -> None:

    def failing_subscriber(event: Event) -> None:
        raise RuntimeError('Subscriber failed')
    event_bus.subscribe(Channel('test-channel'), failing_subscriber)
    event_bus.start()
    event_bus.publish(sample_event)
    event_bus.stop()
    error_events = trace_emitter.get_events(level=TraceLevel.ERROR)
    assert len(error_events) > 0
    assert any('RuntimeError' in event.message for event in error_events)

def test_concurrent_publish_and_subscribe(event_bus: EventBus) -> None:
    import threading
    received_events: list[Event] = []
    lock = threading.Lock()

    def subscriber(event: Event) -> None:
        with lock:
            received_events.append(event)
    event_bus.subscribe(Channel('test-channel'), subscriber)
    event_bus.start()

    def publish_many() -> None:
        for _i in range(10):
            event = Event(  # noqa: E501
                channel=Channel('test-channel'),
                correlation_id=uuid4(),
                timestamp=now_utc(),
                version=1,
                trace_level=TraceLevel.INFO,
                payload={}
            )
            event_bus.publish(event)

    threads = [threading.Thread(target=publish_many) for _ in range(5)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    event_bus.stop()
    assert len(received_events) == 50
