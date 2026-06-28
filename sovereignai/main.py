"""Composition root — wires all Plan 1 core components explicitly.

Per A3: this file is incremental. Plan 1 wires only the Event Bus,
TraceEmitter, DI container, and shared types. Plans 2, 3, and 4 will
extend this file to add their components. Plan 4 performs the final
wiring audit.

Per AR4: this is the ONLY file that instantiates core components.
Every other file receives dependencies via constructor injection.

Per AR5: this file is exempt from the 15-argument constructor cap —
it wires all components explicitly in topological order.
"""
from __future__ import annotations

from sovereignai.shared.container import DIContainer
from sovereignai.shared.event_bus import EventBus
from sovereignai.shared.trace_emitter import TraceEmitter


def build_container() -> DIContainer:
    """Create and populate the dependency injection container with Plan 1 components.

    Wires components in topological order: TraceEmitter first (no deps),
    then EventBus (depends on TraceEmitter). Registers both as singletons
    in the container. Returns the populated container.

    Plans 2-4 will extend this function to add their components after
    the EventBus registration.
    """
    container = DIContainer()

    # 1. TraceEmitter — no dependencies, singleton
    trace = TraceEmitter()
    container.register_singleton(TraceEmitter, trace)

    # 2. EventBus — depends on TraceEmitter, singleton
    bus = EventBus(trace=trace)
    container.register_singleton(EventBus, bus)

    # 3. CapabilityGraph — depends on TraceEmitter, singleton (Plan 2)
    # Registered against ICapabilityIndex protocol so Plan 4's Capability
    # API can depend on the protocol, not the concrete class (per A5).
    # Rev2: graph now accepts TraceEmitter per Finding 3 (P9 compliance).
    from sovereignai.shared.capability_graph import (
        CapabilityGraph,
        ICapabilityIndex,
    )
    graph = CapabilityGraph(trace=trace)
    container.register_singleton(CapabilityGraph, graph)
    container.register_singleton(ICapabilityIndex, graph)  # type: ignore[type-abstract]

    # 4. LifecycleManager — depends on TraceEmitter, singleton (Plan 3)
    # Rev2 per Finding 4: accepts TraceEmitter to emit on circuit-breaker trips.
    from sovereignai.shared.lifecycle_manager import LifecycleManager
    lifecycle = LifecycleManager(trace=trace)
    container.register_singleton(LifecycleManager, lifecycle)

    # 5. RoutingEngine — depends on ICapabilityIndex + LifecycleManager
    from sovereignai.shared.routing_engine import RoutingEngine
    router = RoutingEngine(
        capability_index=container.retrieve(ICapabilityIndex),
        lifecycle_manager=lifecycle,
    )
    container.register_singleton(RoutingEngine, router)

    # 6. TaskStateMachine — depends on EventBus + TraceEmitter
    from sovereignai.shared.task_state_machine import (
        ITaskStateQuery,
        TaskStateMachine,
    )
    state_machine = TaskStateMachine(bus=bus, trace=trace)
    container.register_singleton(TaskStateMachine, state_machine)
    container.register_singleton(ITaskStateQuery, state_machine)  # type: ignore[type-abstract]

    return container


if __name__ == "__main__":
    """Run the composition root standalone for smoke testing.

    Builds the container, retrieves the EventBus and TraceEmitter, emits
    a startup trace event, and prints it. This verifies the wiring is
    functional before Plan 2 builds on top.
    """
    from sovereignai.shared.types import TraceLevel

    container = build_container()
    trace = container.retrieve(TraceEmitter)
    bus = container.retrieve(EventBus)

    trace.emit(
        component="main",
        level=TraceLevel.INFO,
        message="Composition root built successfully — Plan 1 components wired",
    )
    for event in trace.get_events():
        print(f"[{event.level.value}] {event.component}: {event.message}")
