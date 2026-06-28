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
        capability_index=container.retrieve(ICapabilityIndex),  # type: ignore[type-abstract]
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

    # 7. AuthMiddleware — depends on TraceEmitter, singleton (Plan 4)
    from sovereignai.shared.auth import AuthMiddleware
    auth = AuthMiddleware(trace=trace)
    container.register_singleton(AuthMiddleware, auth)

    # 8. CapabilityAPI — depends on AuthMiddleware + ICapabilityIndex
    #    + ITaskStateQuery + TaskStateMachine
    # Rev2 per Finding 1: passes the concrete TaskStateMachine so submit_task
    # can call submit() (the ITaskStateQuery protocol is query-only).
    from sovereignai.shared.capability_api import CapabilityAPI
    from sovereignai.shared.capability_graph import ICapabilityIndex
    from sovereignai.shared.task_state_machine import ITaskStateQuery, TaskStateMachine
    api = CapabilityAPI(
        auth=auth,
        capability_index=container.retrieve(ICapabilityIndex),  # type: ignore[type-abstract]
        task_state_query=container.retrieve(ITaskStateQuery),  # type: ignore[type-abstract]
        state_machine=container.retrieve(TaskStateMachine),
        trace=trace,
    )
    container.register_singleton(CapabilityAPI, api)

    # 9. RelayPlaceholder — depends on TraceEmitter, singleton (Plan 4)
    # Real relay server deferred to a post-batch plan per A4.
    from sovereignai.shared.relay_placeholder import RelayPlaceholder
    relay = RelayPlaceholder(trace=trace)
    container.register_singleton(RelayPlaceholder, relay)

    # === Q26 CONFIRMATION ===
    # Per A3: Q26 ("single file instantiates all core components explicitly")
    # is confirmed at Plan 4 /close. As of this plan, main.py wires:
    #   1. TraceEmitter (Plan 1)
    #   2. EventBus (Plan 1)
    #   3. CapabilityGraph + ICapabilityIndex (Plan 2)
    #   4. LifecycleManager (Plan 3)
    #   5. RoutingEngine (Plan 3)
    #   6. TaskStateMachine + ITaskStateQuery (Plan 3)
    #   7. AuthMiddleware (Plan 4)
    #   8. CapabilityAPI (Plan 4)
    #   9. RelayPlaceholder (Plan 4 — real relay deferred per A4)
    # All 9 components instantiated explicitly in topological order.
    # No runtime magic, no auto-discovery (per Q26 resolution).

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
