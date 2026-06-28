"""Tests for the composition root.

Verifies that the DI container is wired correctly with Plan 1 components.
"""
from __future__ import annotations

import subprocess

from sovereignai.main import build_container
from sovereignai.shared.capability_graph import CapabilityGraph, ICapabilityIndex
from sovereignai.shared.container import DIContainer
from sovereignai.shared.event_bus import EventBus
from sovereignai.shared.trace_emitter import TraceEmitter
from sovereignai.shared.types import Channel, Event, new_correlation_id, now_utc


def test_build_container_returns_populated_container() -> None:
    """Verify that build_container returns a DIContainer with TraceEmitter and EventBus."""
    container = build_container()

    assert isinstance(container, DIContainer)

    # Should be able to retrieve TraceEmitter
    trace = container.retrieve(TraceEmitter)
    assert isinstance(trace, TraceEmitter)

    # Should be able to retrieve EventBus
    bus = container.retrieve(EventBus)
    assert isinstance(bus, EventBus)


def test_trace_emitter_is_singleton() -> None:
    """Verify that retrieving TraceEmitter twice returns the same instance."""
    container = build_container()

    first = container.retrieve(TraceEmitter)
    second = container.retrieve(TraceEmitter)

    assert first is second


def test_event_bus_is_singleton() -> None:
    """Verify that retrieving EventBus twice returns the same instance."""
    container = build_container()

    first = container.retrieve(EventBus)
    second = container.retrieve(EventBus)

    assert first is second


def test_event_bus_has_trace_emitter_wired() -> None:
    """Verify that EventBus has TraceEmitter wired by checking subscriber failure logging."""
    container = build_container()

    bus = container.retrieve(EventBus)
    trace = container.retrieve(TraceEmitter)

    # Register a failing subscriber
    def failing_subscriber(event: object) -> None:
        raise ValueError("Test failure")

    bus.subscribe(Channel("test"), failing_subscriber)

    # Publish an event
    event = Event(
        channel=Channel("test"),
        correlation_id=new_correlation_id(),
        timestamp=now_utc(),
    )
    bus.publish(event)

    # Verify TraceEmitter recorded the error
    error_events = trace.get_events()
    assert len(error_events) > 0
    assert any("ValueError" in e.message for e in error_events)


def test_main_smoke_test() -> None:
    """Verify that running the main module exits successfully and produces expected output."""
    result = subprocess.run(
        [".venv/Scripts/python.exe", "-m", "sovereignai.main"],
        cwd="c:\\SovereignAI",
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0
    assert "Composition root built successfully" in result.stdout


def test_capability_graph_registered() -> None:
    """Verify that CapabilityGraph is registered in the container and retrievable."""
    container = build_container()
    graph = container.retrieve(CapabilityGraph)
    assert isinstance(graph, CapabilityGraph)


def test_icapability_index_registered() -> None:
    """Verify that ICapabilityIndex is registered and returns the same graph instance."""
    container = build_container()
    graph = container.retrieve(CapabilityGraph)
    index = container.retrieve(ICapabilityIndex)
    assert index is graph  # Same instance registered against both types


def test_capability_graph_is_singleton() -> None:
    """Verify that retrieving CapabilityGraph twice returns the same instance."""
    container = build_container()
    first = container.retrieve(CapabilityGraph)
    second = container.retrieve(CapabilityGraph)
    assert first is second
