"""Tests for the composition root.

Verifies that the DI container is wired correctly with Plan 1 components.
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

from sovereignai.main import build_container
from sovereignai.shared.auth import AuthMiddleware
from sovereignai.shared.capability_api import CapabilityAPI
from sovereignai.shared.capability_graph import CapabilityGraph, ICapabilityIndex
from sovereignai.shared.container import DIContainer
from sovereignai.shared.event_bus import EventBus
from sovereignai.shared.lifecycle_manager import LifecycleManager
from sovereignai.shared.relay_placeholder import RelayPlaceholder
from sovereignai.shared.routing_engine import RoutingEngine
from sovereignai.shared.task_state_machine import ITaskStateQuery, TaskStateMachine
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
    project_root = Path(__file__).resolve().parents[1]
    result = subprocess.run(
        [sys.executable, "-m", "sovereignai.main"],
        cwd=str(project_root),
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
    index = container.retrieve(ICapabilityIndex)  # type: ignore[type-abstract]
    assert index is graph  # Same instance registered against both types


def test_capability_graph_is_singleton() -> None:
    """Verify that retrieving CapabilityGraph twice returns the same instance."""
    container = build_container()
    first = container.retrieve(CapabilityGraph)
    second = container.retrieve(CapabilityGraph)
    assert first is second


def test_lifecycle_manager_registered() -> None:
    """Verify that LifecycleManager is registered in the container and retrievable."""
    container = build_container()
    lifecycle = container.retrieve(LifecycleManager)
    assert isinstance(lifecycle, LifecycleManager)


def test_routing_engine_registered() -> None:
    """Verify that RoutingEngine is registered in the container and retrievable."""
    container = build_container()
    router = container.retrieve(RoutingEngine)
    assert isinstance(router, RoutingEngine)


def test_task_state_machine_registered() -> None:
    """Verify that TaskStateMachine is registered in the container and retrievable."""
    container = build_container()
    state_machine = container.retrieve(TaskStateMachine)
    assert isinstance(state_machine, TaskStateMachine)


def test_itask_state_query_registered() -> None:
    """Verify that ITaskStateQuery is registered and returns the same state machine instance."""
    container = build_container()
    state_machine = container.retrieve(TaskStateMachine)
    query = container.retrieve(ITaskStateQuery)  # type: ignore[type-abstract]
    assert query is state_machine  # Same instance registered against both types


def test_routing_engine_has_capability_index_wired() -> None:
    """Verify that RoutingEngine has the registered CapabilityGraph wired as its _index."""
    container = build_container()
    router = container.retrieve(RoutingEngine)
    graph = container.retrieve(CapabilityGraph)
    assert router._index is graph


def test_routing_engine_has_lifecycle_wired() -> None:
    """Verify that RoutingEngine has the registered LifecycleManager wired as its _lifecycle."""
    container = build_container()
    router = container.retrieve(RoutingEngine)
    lifecycle = container.retrieve(LifecycleManager)
    assert router._lifecycle is lifecycle


def test_auth_middleware_registered() -> None:
    """Verify that AuthMiddleware is registered in the container and retrievable."""
    container = build_container()
    auth = container.retrieve(AuthMiddleware)
    assert isinstance(auth, AuthMiddleware)


def test_capability_api_registered() -> None:
    """Verify that CapabilityAPI is registered in the container and retrievable."""
    container = build_container()
    api = container.retrieve(CapabilityAPI)
    assert isinstance(api, CapabilityAPI)


def test_relay_placeholder_registered() -> None:
    """Verify that RelayPlaceholder is registered in the container and retrievable."""
    container = build_container()
    relay = container.retrieve(RelayPlaceholder)
    assert isinstance(relay, RelayPlaceholder)


def test_capability_api_has_auth_wired() -> None:
    """Verify that CapabilityAPI has the registered AuthMiddleware wired as its _auth."""
    container = build_container()
    api = container.retrieve(CapabilityAPI)
    auth = container.retrieve(AuthMiddleware)
    assert api._auth is auth


def test_capability_api_has_capability_index_wired() -> None:
    """Verify that CapabilityAPI has the registered CapabilityGraph wired as its _index."""
    container = build_container()
    api = container.retrieve(CapabilityAPI)
    graph = container.retrieve(CapabilityGraph)
    assert api._index is graph


def test_capability_api_has_task_state_query_wired() -> None:
    """Verify that CapabilityAPI has the registered TaskStateMachine wired as its _tasks."""
    container = build_container()
    api = container.retrieve(CapabilityAPI)
    state_machine = container.retrieve(TaskStateMachine)
    assert api._tasks is state_machine


def test_q26_all_components_instantiated_in_main() -> None:
    """Verify that all 9 components are instantiated in main.py build_container() (Q26 audit).

    Per A3: Q26 ("single file instantiates all core components explicitly")
    is confirmed at Plan 4 /close. This test parses main.py via AST and verifies
    that all component classes are instantiated in build_container().
    """
    import ast

    main_path = "sovereignai/main.py"
    with open(main_path) as f:
        tree = ast.parse(f.read())

    # Find the build_container function
    build_container_func = None
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == "build_container":
            build_container_func = node
            break

    assert build_container_func is not None, "build_container function not found"

    # Collect all class instantiations in the function
    instantiations = set()
    for stmt in build_container_func.body:
        for node in ast.walk(stmt):
            if isinstance(node, ast.Call):
                # Get the type being instantiated
                if isinstance(node.func, ast.Name):
                    instantiations.add(node.func.id)
                elif isinstance(node.func, ast.Attribute):
                    instantiations.add(node.func.attr)

    # Verify all 9 components are instantiated
    expected_components = {
        "DIContainer",
        "TraceEmitter",
        "EventBus",
        "CapabilityGraph",
        "LifecycleManager",
        "RoutingEngine",
        "TaskStateMachine",
        "AuthMiddleware",
        "CapabilityAPI",
        "RelayPlaceholder",
    }

    for component in expected_components:
        assert component in instantiations, f"{component} not instantiated in build_container()"

