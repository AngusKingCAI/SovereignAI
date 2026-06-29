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
from sovereignai.shared.types import (
    TraceLevel,
)
from sovereignai.versioning.negotiator import FatalIncompatibilityError


def build_container() -> DIContainer:
    """Create and populate the dependency injection container with Plan 1 components.

    Wires components in topological order: TraceEmitter first (no deps),
    then EventBus (depends on TraceEmitter). Registers both as singletons
    in the container. Returns the populated container.

    Plans 2-4 will extend this function to add their components after
    the EventBus registration.
    """
    # Create container with event_bus and trace for remove() support (per Rev9)
    # We'll set these after they're created
    container = DIContainer()

    # 1. TraceEmitter — no dependencies, singleton
    trace = TraceEmitter()
    container.register_singleton(TraceEmitter, trace)

    # 2. EventBus — depends on TraceEmitter, singleton
    bus = EventBus(trace=trace)
    container.register_singleton(EventBus, bus)

    # Set event_bus and trace on container for remove() support (per Rev9)
    container._event_bus = bus
    container._trace = trace

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

    # 10. MessageDispatcher — depends on CapabilityAPI + CapabilityGraph +
    #     TaskStateMachine + TraceEmitter (Plan 7)
    from sovereignai.orchestrator.dispatcher import MessageDispatcher
    dispatcher = MessageDispatcher(
        capability_api=container.retrieve(CapabilityAPI),
        capability_graph=container.retrieve(CapabilityGraph),
        task_state_machine=container.retrieve(ITaskStateQuery),  # type: ignore[type-abstract]
        trace=trace,
    )
    container.register_singleton(MessageDispatcher, dispatcher)

    # 11. Load skill and adapter manifests and register in CapabilityGraph (Plan 7)
    from pathlib import Path

    from sovereignai.shared.manifest_parser import parse_manifest

    # Scan skills/user/, skills/external/, adapters/external/, and adapters/internal/  # noqa: E501
    # for manifest.toml files
    manifest_dirs = [
        Path("skills/user"),
        Path("skills/external"),
        Path("adapters/external"),
        Path("adapters/internal"),
    ]

    for manifest_dir in manifest_dirs:
        if manifest_dir.exists():
            for manifest_path in manifest_dir.glob("*/manifest.toml"):
                try:
                    manifest = parse_manifest(manifest_path)
                    graph.register(manifest)
                    trace.emit(
                        component="main",
                        level=TraceLevel.INFO,
                        message=f"Registered {manifest.component_id} from {manifest_path}",
                    )
                except Exception as exc:
                    trace.emit(
                        component="main",
                        level=TraceLevel.ERROR,
                        message=f"Failed to load manifest {manifest_path}: {exc}",
                    )

    # 12. Register memory backends + Librarian (Plan 11)
    # NOTE: Memory backends are initialized but their persistence is disabled in tests
    # to avoid database file I/O during test runs. The backends are functional for
    # in-memory operations.
    from sovereignai.librarian.librarian import Librarian
    from sovereignai.memory.working_backend import WorkingMemoryBackend

    # Instantiate working memory backend (in-process, no disk I/O)
    working_backend = WorkingMemoryBackend(trace=trace)
    container.register_singleton(WorkingMemoryBackend, working_backend)

    # Instantiate and register Librarian
    librarian = Librarian(capability_graph=graph, trace=trace)
    container.register_singleton(Librarian, librarian)

    # 14. Version negotiator (Plan 12)
    # Per Rev3 N7: non-interactive detection; per Rev3 N11: remove from DI container
    from sovereignai.versioning.negotiator import VersionNegotiator
    negotiator = VersionNegotiator(
        capability_graph=container.retrieve(ICapabilityIndex),  # type: ignore[type-abstract]
        trace=trace,
    )
    result = negotiator.negotiate()

    if not result.can_start:
        trace.emit(
            component="versioning",
            level=TraceLevel.ERROR,
            message=f"Fatal incompatibilities: {[str(i) for i in result.fatal_incompatibilities]}",
        )
        raise FatalIncompatibilityError(result.fatal_incompatibilities)

    for warning in result.warnings:
        trace.emit(
            component="versioning",
            level=TraceLevel.WARN,
            message=warning,
        )

    # Remove disabled plugins from BOTH the graph AND the DI container (per Rev3 N11)
    for plugin_id in result.disabled_plugins:
        graph.remove(plugin_id)
        # Note: we don't have the actual class type here, so we can't remove from container
        # The negotiator would need to track component classes to support this
        trace.emit(
            component="versioning",
            level=TraceLevel.WARN,
            message=(
                f"Plugin {plugin_id} disabled due to version "
                "incompatibility; removed from graph"
            ),
        )

    container.register_singleton(VersionNegotiator, negotiator)

    # 15. Crash recovery (non-blocking, automatic, failure-isolated) (Plan 11)
    # NOTE: Crash recovery is disabled in the composition root for now since
    # persistent backends are not initialized. This will be re-enabled when
    # the full memory system is wired in production mode.
    def run_crash_recovery(container: DIContainer, trace: TraceEmitter) -> None:
        """Run crash recovery on startup. Best-effort — never blocks startup.

        Per Rev3 N5: if a shutdown marker exists, the previous shutdown was clean — skip recovery.
        Per Rev3 N9: the entire recovery loop is wrapped in try/except — on any failure,
        log to stderr and continue.
        """
        # Disabled for now - persistent backends not initialized
        pass

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
    #   10. MessageDispatcher (Plan 7)
    #   11. Skill/adapter manifest loading (Plan 7)
    # All components instantiated explicitly in topological order.
    # No runtime magic, no auto-discovery (per Q26 resolution).

    return container


if __name__ == "__main__":
    import argparse
    import sys

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--no-wait", action="store_true",
        help="Exit immediately on fatal errors (for CI)"
    )
    args = parser.parse_args()

    try:
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
    except FatalIncompatibilityError as e:
        print(f"SovereignAI cannot start:\n{e}", file=sys.stderr)
        # F7: 30s countdown is DEFAULT. --no-wait skips it. isatty() is a HINT, not a hard gate.
        if args.no_wait:
            sys.exit(1)
        if not sys.stdin.isatty():
            print(
                "(Non-interactive terminal detected. "
                "Pass --no-wait to exit immediately.)",
                file=sys.stderr,
            )
        import time

        time.sleep(30)
        sys.exit(1)
