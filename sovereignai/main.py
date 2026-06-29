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

import atexit
import os
import sys
from uuid import UUID

from sovereignai.shared.container import DIContainer
from sovereignai.shared.event_bus import EventBus
from sovereignai.shared.trace_emitter import TraceEmitter
from sovereignai.shared.types import (
    TASK_STATE_CHANNEL,
    TaskState,
    TaskStateChanged,
    TraceLevel,
    _is_valid_uuid,
    new_correlation_id,
    now_utc,
)


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

    # Scan skills/user/, skills/external/, adapters/external/, and adapters/internal/ for manifest.toml files
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
    from sovereignai.librarian.librarian import Librarian
    from sovereignai.memory.episodic_backend import EpisodicMemoryBackend
    from sovereignai.memory.procedural_backend import ProceduralMemoryBackend
    from sovereignai.memory.trace_backend import TraceMemoryBackend
    from sovereignai.memory.working_backend import WorkingMemoryBackend

    # Instantiate memory backends
    episodic_backend = EpisodicMemoryBackend(trace=trace)
    procedural_backend = ProceduralMemoryBackend(trace=trace)
    working_backend = WorkingMemoryBackend(trace=trace)
    trace_backend = TraceMemoryBackend(trace=trace)

    # Register backends in container (not as singletons — they're stateful but not shared)
    container.register(EpisodicMemoryBackend, episodic_backend)
    container.register(ProceduralMemoryBackend, procedural_backend)
    container.register(WorkingMemoryBackend, working_backend)
    container.register(TraceMemoryBackend, trace_backend)

    # Instantiate and register Librarian
    librarian = Librarian(capability_graph=graph, trace=trace)
    container.register_singleton(Librarian, librarian)

    # Wire TraceEmitter → TraceMemoryBackend (durable persistence)
    # Per Rev5 F1: regular trace events do NOT carry task_state (TraceEvent has no such field).
    # TaskStateChanged events are persisted separately by the subscriber below.
    from sovereignai.shared.types import TraceEvent

    def _on_trace_emitted(event: TraceEvent) -> None:
        """Persist every trace event to the durable trace backend."""
        try:
            trace_backend.store(
                data={
                    "component": event.component,
                    "level": event.level.value,
                    "message": event.message,
                    "correlation_id": str(event.correlation_id),
                },
                metadata={},  # Regular traces have no task_state — that's fine.
            )
        except Exception:
            pass
    trace.subscribe_callback(_on_trace_emitted)

    # Per Rev5 F1: ALSO subscribe to TaskStateChanged events and persist them with
    # task_id + task_state metadata. This populates the task_state column that
    # get_last_task_states() queries for crash recovery. Without this, crash
    # recovery finds no incomplete tasks (the Rev4 bug).
    def _on_task_state_changed_persist(event: TaskStateChanged) -> None:
        """Persist task state transitions to the trace backend for crash recovery."""
        try:
            trace_backend.store(
                data={
                    "component": "TaskStateMachine",
                    "level": "info",
                    "message": f"Task {event.task_id} transitioned {event.old_state} → {event.new_state}",
                    "correlation_id": str(event.correlation_id) if hasattr(event, 'correlation_id') and event.correlation_id else str(new_correlation_id()),
                },
                metadata={
                    "task_id": str(event.task_id),
                    "task_state": event.new_state.value if hasattr(event.new_state, 'value') else str(event.new_state),
                },
            )
        except Exception:
            pass
    bus.subscribe(TASK_STATE_CHANNEL, _on_task_state_changed_persist, subscriber_id="trace_persist")

    # Wire WorkingMemoryBackend.cleanup to TaskStateChanged (per Rev3 N20)
    def _on_task_state_changed(event: TaskStateChanged) -> None:
        """Free working memory when a task reaches a terminal state.

        Per Rev6: wrapped in try/except so a cleanup failure doesn't kill the dispatch loop
        (which would prevent the persist handler from running on future events).
        Ordering: this handler runs AFTER _on_task_state_changed_persist (registration order).
        """
        # Compare against enum VALUES for robustness against string deserialization
        terminal_states = (TaskState.COMPLETE.value, TaskState.FAILED.value)
        new_state_val = event.new_state.value if isinstance(event.new_state, TaskState) else str(event.new_state)
        if new_state_val in terminal_states:
            try:
                working_backend.cleanup(str(event.task_id))
            except Exception as e:
                trace.emit(
                    component="working_memory",
                    level=TraceLevel.WARN,
                    message=f"Working memory cleanup failed for task {event.task_id}: {e}",
                )
    bus.subscribe(TASK_STATE_CHANNEL, _on_task_state_changed, subscriber_id="working_memory_cleanup")

    # 13. Crash recovery (non-blocking, automatic, failure-isolated) (Plan 11)
    def run_crash_recovery(container: DIContainer, trace: TraceEmitter) -> None:
        """Run crash recovery on startup. Best-effort — never blocks startup.

        Per Rev3 N5: if a shutdown marker exists, the previous shutdown was clean — skip recovery.
        Per Rev3 N9: the entire recovery loop is wrapped in try/except — on any failure,
        log to stderr and continue.
        """
        marker_path = os.path.expanduser("~/.sovereignai/.shutdown_marker")
        try:
            if os.path.exists(marker_path):
                # Per Rev5 F6: validate marker content (magic string) before trusting it.
                # A partial/corrupted marker (from a crash mid-write) must NOT skip recovery.
                try:
                    with open(marker_path, "r") as f:
                        content = f.read()
                    if content.startswith("SOVEREIGNAI_CLEAN_SHUTDOWN_V1\n"):
                        # Valid marker — previous shutdown was clean
                        os.unlink(marker_path)
                        trace.emit(component="recovery", level=TraceLevel.INFO,
                                   message="Clean shutdown detected — skipping crash recovery")
                        return
                    else:
                        # Invalid marker content — treat as no marker (crash)
                        trace.emit(component="recovery", level=TraceLevel.WARN,
                                   message="Shutdown marker exists but content invalid — treating as crash")
                except Exception:
                    # Can't read marker — treat as no marker (crash)
                    trace.emit(component="recovery", level=TraceLevel.WARN,
                               message="Shutdown marker unreadable — treating as crash")

            # No marker — previous shutdown was a crash. Run recovery.
            last_task_states = trace_backend.get_last_task_states()

            for task_id_str, state in last_task_states.items():
                if state in ("received", "queued", "executing"):
                    trace.emit(
                        component="recovery",
                        level=TraceLevel.WARN,
                        message=f"Task {task_id_str} was incomplete (state={state}) at crash; marking as recovered-failed. Side effects not replayed.",
                        correlation_id=UUID(task_id_str) if _is_valid_uuid(task_id_str) else None,
                    )
                    trace_backend.store(
                        data={
                            "component": "recovery",
                            "level": "warn",
                            "message": f"recovered: incomplete at crash (was {state})",
                            "correlation_id": task_id_str if _is_valid_uuid(task_id_str) else str(new_correlation_id()),
                        },
                        metadata={"task_id": task_id_str, "task_state": "failed"},
                    )
        except Exception as e:
            # N9: never let recovery break startup
            print(f"SovereignAI crash recovery failed (non-fatal): {e}", file=sys.stderr)
            trace.emit(component="recovery", level=TraceLevel.ERROR,
                       message=f"Crash recovery failed (non-fatal): {e}")

    def on_clean_shutdown(container: DIContainer, trace: TraceEmitter) -> None:
        """Write shutdown marker on clean shutdown. Called from main.py shutdown handler.

        Per Rev5 F6: uses atomic write (temp + os.replace) and a magic string for
        validation. A partial write (crash mid-write) produces an invalid marker
        that is treated as 'no marker' (crash) on next startup.
        """
        marker_path = os.path.expanduser("~/.sovereignai/.shutdown_marker")
        magic = "SOVEREIGNAI_CLEAN_SHUTDOWN_V1\n"
        try:
            os.makedirs(os.path.dirname(marker_path), exist_ok=True)
            tmp_path = marker_path + ".tmp"
            with open(tmp_path, "w") as f:
                f.write(magic + now_utc().isoformat())
            os.replace(tmp_path, marker_path)
        except Exception:
            pass

    # Run crash recovery on startup
    run_crash_recovery(container, trace)

    # Register shutdown handler for clean shutdown marker
    atexit.register(on_clean_shutdown, container, trace)

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
