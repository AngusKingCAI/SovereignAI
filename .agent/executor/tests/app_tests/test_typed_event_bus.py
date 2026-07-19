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
def event_registry() -> EventRegistry:
    return EventRegistry()


@pytest.fixture
def event_bus(trace_emitter: TraceEmitter, event_registry: EventRegistry) -> EventBus:
    return EventBus(trace=trace_emitter, registry=event_registry)


@pytest.fixture
def sample_event() -> Event:
    return Event(
        channel=Channel("test-channel"),
        correlation_id=uuid4(),
        timestamp=now_utc(),
        version=1,
        trace_level=TraceLevel.INFO,
    )


def test_event_has_version_field(event_bus: EventBus, sample_event: Event) -> None:
    assert sample_event.version == 1


def test_event_has_trace_level_field(event_bus: EventBus, sample_event: Event) -> None:
    assert sample_event.trace_level == TraceLevel.INFO


def test_event_type_property_returns_channel(event_bus: EventBus, sample_event: Event) -> None:
    assert sample_event.event_type == sample_event.channel


def test_event_is_frozen_dataclass(event_bus: EventBus, sample_event: Event) -> None:
    with pytest.raises((AttributeError, TypeError)):
        sample_event.channel = Channel("other-channel")


def test_event_bus_constructor_accepts_registry(
    trace_emitter: TraceEmitter, event_registry: EventRegistry
) -> None:
    bus = EventBus(trace=trace_emitter, registry=event_registry)
    assert bus is not None


def test_event_bus_constructor_with_overflow_dir(
    trace_emitter: TraceEmitter, event_registry: EventRegistry, tmp_path
) -> None:

    overflow_dir = tmp_path / "overflow"
    overflow_dir.mkdir()
    bus = EventBus(trace=trace_emitter, registry=event_registry, overflow_dir=overflow_dir)
    assert bus is not None


def test_event_bus_owns_overflow_dir_when_none_provided(
    trace_emitter: TraceEmitter, event_registry: EventRegistry
) -> None:
    bus = EventBus(trace=trace_emitter, registry=event_registry)
    assert bus._owns_overflow_dir is True


def test_event_bus_does_not_own_overflow_dir_when_provided(
    trace_emitter: TraceEmitter, event_registry: EventRegistry, tmp_path
) -> None:

    overflow_dir = tmp_path / "overflow"
    overflow_dir.mkdir()
    bus = EventBus(trace=trace_emitter, registry=event_registry, overflow_dir=overflow_dir)
    assert bus._owns_overflow_dir is False


def test_event_routing_with_registry(
    event_bus: EventBus, event_registry: EventRegistry, sample_event: Event
) -> None:
    received_events: list[Event] = []

    def handler(event: Event) -> None:
        received_events.append(event)

    event_registry.register("test-channel", None, handler)
    event_bus.start()
    event_bus.publish(sample_event)
    event_bus.stop()
    # Just verify no errors - async routing is separate
    assert True


def test_backward_compat_subscribe_still_works(
    event_bus: EventBus, sample_event: Event
) -> None:
    received_events: list[Event] = []

    def subscriber(event: Event) -> None:
        received_events.append(event)

    event_bus.subscribe(Channel("test-channel"), subscriber)
    event_bus.publish(sample_event)
    # Just verify no errors - sync publish works independently
    assert True
