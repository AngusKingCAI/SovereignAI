from __future__ import annotations

from sovereignai.shared.container import DIContainer
from sovereignai.shared.event_bus import EventBus
from sovereignai.shared.file_trace_subscriber import FileTraceSubscriber
from sovereignai.shared.trace_emitter import TraceEmitter
from sovereignai.shared.types import (
    TraceLevel,
)
from sovereignai.versioning.negotiator import FatalIncompatibilityError


def build_container(dev_mode: bool = False) -> DIContainer:
    # Create container with event_bus and trace for remove() support (per Rev9)
    # We'll set these after they're created
    container = DIContainer()

    # 1. TraceEmitter — no dependencies, singleton
    trace = TraceEmitter()
    container.register_singleton(TraceEmitter, trace)

    # 1.5. FileTraceSubscriber — depends on TraceEmitter, singleton (Plan 20.7.3)
    file_subscriber = FileTraceSubscriber()
    trace.subscribe_callback(file_subscriber)
    container.register_singleton(FileTraceSubscriber, file_subscriber)

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
    # Plan 13: graph accepts dev_mode flag for conformance gate bypass
    from sovereignai.shared.capability_graph import (
        CapabilityGraph,
        ICapabilityIndex,
    )
    graph = CapabilityGraph(trace=trace, dev_mode=dev_mode)
    container.register_singleton(CapabilityGraph, graph)
    container.register_singleton(ICapabilityIndex, graph)  # type: ignore[type-abstract]

    # 4. LifecycleManager — depends on TraceEmitter, singleton (Plan 3)
    # Rev2 per Finding 4: accepts TraceEmitter to emit on circuit-breaker trips.
    from sovereignai.shared.lifecycle_manager import LifecycleManager
    lifecycle = LifecycleManager(trace=trace)
    container.register_singleton(LifecycleManager, lifecycle)

    # 5. RoutingEngine — depends on ICapabilityIndex + LifecycleManager + TraceEmitter
    from sovereignai.shared.routing_engine import RoutingEngine
    router = RoutingEngine(
        capability_index=container.retrieve(ICapabilityIndex),  # type: ignore[type-abstract]
        lifecycle_manager=lifecycle,
        trace=trace,
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
    #    + ITaskStateQuery + TaskStateMachine + HardwareProbe
    # Rev2 per Finding 1: passes the concrete TaskStateMachine so submit_task
    # can call submit() (the ITaskStateQuery protocol is query-only).
    # Plan 18: added HardwareProbe dependency for sample_hardware() and stream_hardware()
    # Plan 20.9.1: database_registry, service_registry, memory_backends added after registration
    from sovereignai.shared.capability_api import CapabilityAPI
    from sovereignai.shared.capability_graph import ICapabilityIndex
    from sovereignai.shared.hardware_probe import HardwareProbe
    from sovereignai.shared.task_state_machine import ITaskStateQuery, TaskStateMachine
    api = CapabilityAPI(
        auth=auth,
        capability_index=container.retrieve(ICapabilityIndex),  # type: ignore[type-abstract]
        task_state_query=container.retrieve(ITaskStateQuery),  # type: ignore[type-abstract]
        state_machine=container.retrieve(TaskStateMachine),
        trace=trace,
        hardware_probe=HardwareProbe(),
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

    # Scan skills/user/, skills/external/, skills/official/, adapters/external/, and adapters/internal/  # noqa: E501
    # for manifest.toml files
    manifest_dirs = [
        Path("skills/user"),
        Path("skills/external"),
        Path("skills/official"),
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
    # Per L41 fix: ALL backends registered. Test mode uses :memory: SQLite.
    from sovereignai.librarian.librarian import Librarian
    from sovereignai.memory.episodic_backend import EpisodicMemoryBackend
    from sovereignai.memory.procedural_backend import ProceduralMemoryBackend
    from sovereignai.memory.trace_backend import TraceMemoryBackend
    from sovereignai.memory.working_backend import WorkingMemoryBackend

    episodic_backend = EpisodicMemoryBackend(trace=trace, db_path=None)
    container.register_singleton(EpisodicMemoryBackend, episodic_backend)

    procedural_backend = ProceduralMemoryBackend(trace=trace, file_path=None)
    container.register_singleton(ProceduralMemoryBackend, procedural_backend)

    working_backend = WorkingMemoryBackend(trace=trace)
    container.register_singleton(WorkingMemoryBackend, working_backend)

    trace_backend = TraceMemoryBackend(trace=trace, db_path=None)
    container.register_singleton(TraceMemoryBackend, trace_backend)

    librarian = Librarian(capability_graph=graph, trace=trace)
    container.register_singleton(Librarian, librarian)

    # 13. Register default_model_path_resolver (Plan 19 S2.1)
    # Note: Registered as a singleton since it's a pure function
    from sovereignai.shared.model_path_resolver import default_model_path_resolver
    container.register_singleton(default_model_path_resolver, default_model_path_resolver)  # type: ignore[arg-type]

    # 14. DatabaseRegistry and ServiceRegistry (Plan 17)
    from sovereignai.shared.database_registry import DatabaseRegistry
    from sovereignai.shared.service_registry import ServiceRegistry

    db_registry = DatabaseRegistry(trace=trace)
    container.register_singleton(DatabaseRegistry, db_registry)

    service_registry = ServiceRegistry(trace=trace)
    container.register_singleton(ServiceRegistry, service_registry)

    # 14.5. Update CapabilityAPI with registries and memory backends (Plan 20.9.1)
    from sovereignai.shared.capability_api import CapabilityAPI
    api_instance = container.retrieve(CapabilityAPI)
    api_instance._database_registry = db_registry
    api_instance._service_registry = service_registry
    api_instance._memory_backends = {
        "episodic": episodic_backend,
        "procedural": procedural_backend,
        "working": working_backend,
        "trace": trace_backend,
    }

    # 15. Register HFDatabaseProvider (Plan 17)
    from pathlib import Path

    from databases.hf_database.provider import HFDatabaseProvider

    hf_provider = HFDatabaseProvider(trace=trace, cache_dir=Path.home() / ".sovereignai" / "models")
    db_registry.register("huggingface", hf_provider)

    # 16. Register OllamaServiceProvider (Plan 17)
    from services.ollama_service.provider import OllamaServiceProvider

    ollama_provider = OllamaServiceProvider(trace=trace, port=11434)
    service_registry.register("ollama", ollama_provider)

    # 17. Register adapter instances after manifest loading (Plan 19 S3.1)
    # Order-dependent: adapters need model_path_resolver and database_registry
    from adapters.external.ollama_adapter.adapter import OllamaAdapter
    from sovereignai.shared.types import ComponentId

    if ComponentId("ollama_adapter") in graph._manifests:
        ollama_adapter = OllamaAdapter(trace=trace)
        graph.register(
            graph._manifests[ComponentId("ollama_adapter")],
            instance=ollama_adapter,
        )

    # 18. First-run adapter health check (Plan 19 S3.1)
    healthy = []
    for meta in graph.adapters_by_capability("model_inference"):
        inst = graph.get_adapter(meta.component_id)
        if inst is not None and hasattr(inst, "health_check"):
            health = inst.health_check()
            # Handle both bool (OllamaAdapter) and AdapterHealth (LlamaCppAdapter) return types
            is_healthy = health if isinstance(health, bool) else health.healthy
            if is_healthy:
                healthy.append(meta.component_id)

    if not healthy:
        trace.emit(
            component="main",
            level=TraceLevel.WARN,
            message="No inference adapter healthy — install Ollama or llama.cpp",
        )

    # 19. Version negotiator (Plan 12)
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

    # 16. HardwareProbe — no dependencies, singleton (Plan 14)
    from sovereignai.shared.hardware_probe import HardwareProbe
    hardware_probe = HardwareProbe()
    container.register_singleton(HardwareProbe, hardware_probe)

    # 18. Self-correction skill — depends on Librarian + TraceEmitter (Plan 14)
    # NOTE: Self-correction skill subscribes to TaskStateChanged events
    from sovereignai.skills.official.self_correction.skill import SelfCorrectionSkill
    self_correction = SelfCorrectionSkill(
        librarian=container.retrieve(Librarian),
        trace=trace,
    )
    container.register_singleton(SelfCorrectionSkill, self_correction)

    # 19. Wire self-correction skill to TaskStateChanged events (Plan 14)
    # Subscribe to the EventBus to receive task state change notifications
    from sovereignai.shared.types import Channel, Event
    def _wrap_task_state_changed(event: Event) -> None:
        if (
            hasattr(event, "task_id")
            and hasattr(event, "old_state")
            and hasattr(event, "new_state")
        ):
            self_correction.on_task_state_changed(event)  # type: ignore
    bus.subscribe(Channel("TaskStateChanged"), _wrap_task_state_changed)

    # 21. Register Test Manager and Worker for TUI (Plan 20.4 S8)
    from sovereignai.workers.test_manager import TestManager
    from sovereignai.workers.test_worker import TestWorker

    test_manager = TestManager(
        working_memory=container.retrieve(WorkingMemoryBackend),
        trace=trace,
    )
    container.register_singleton(TestManager, test_manager)

    test_worker = TestWorker(
        working_memory=container.retrieve(WorkingMemoryBackend),
        capability_graph=graph,
        trace=trace,
    )
    container.register_singleton(TestWorker, test_worker)

    # 20. Crash recovery (re-enabled per L41 fix)
    import os
    import sys


    marker_path = os.path.expanduser("~/.sovereignai/.shutdown_marker")
    try:
        if os.path.exists(marker_path):
            try:
                with open(marker_path) as f:
                    content = f.read()
                if content.startswith("SOVEREIGNAI_CLEAN_SHUTDOWN_V1\n"):
                    os.unlink(marker_path)
                    trace.emit(component="recovery", level=TraceLevel.INFO,
                               message="Clean shutdown detected — skipping crash recovery")
            except Exception:
                pass

        from sovereignai.memory.trace_backend import TraceMemoryBackend
        tb = container.retrieve(TraceMemoryBackend)
        last_task_states = tb.get_last_task_states()
        for task_id_str, state in last_task_states.items():
            if state in ("received", "queued", "executing"):
                trace.emit(component="recovery", level=TraceLevel.WARN,
                           message=f"Task {task_id_str} incomplete at crash; marking failed.")
                tb.store(
                    data={"component": "recovery", "level": "warn",
                          "message": f"recovered: was {state}",
                          "correlation_id": task_id_str},
                    metadata={"task_id": task_id_str, "task_state": "failed"},
                )
    except Exception as e:
        print(f"Crash recovery failed (non-fatal): {e}", file=sys.stderr)

    # Wire TraceEmitter → TraceMemoryBackend (deferred to background thread)
    import queue
    import threading
    _trace_queue: queue.Queue = queue.Queue()

    def _on_trace_emitted(event: object) -> None:
        import contextlib
        with contextlib.suppress(Exception):
            _trace_queue.put_nowait(event)

    def _trace_writer() -> None:
        while True:
            try:
                event = _trace_queue.get(timeout=5)
                if event is None:
                    break
                trace_backend.store(
                    data={
                        "component": event.component,
                        "level": event.level.value,
                        "message": event.message,
                        "correlation_id": str(event.correlation_id),
                    },
                    metadata={},
                )
            except Exception:
                pass

    if hasattr(trace, 'subscribe_callback'):
        _writer_thread = threading.Thread(target=_trace_writer, daemon=True)
        _writer_thread.start()
        trace.subscribe_callback(_on_trace_emitted)

    from sovereignai.shared.types import TASK_STATE_CHANNEL, TaskState

    def _on_task_state_persist(event: TaskState) -> None:
        try:
            # Cast to TaskStateChanged for metadata extraction
            if (
                hasattr(event, "task_id")
                and hasattr(event, "old_state")
                and hasattr(event, "new_state")
            ):
                task_changed = event  # type: ignore
                trace_backend.store(
                    data={
                        "component": "TaskStateMachine",
                        "level": "info",
                        "message": (
                            f"Task {task_changed.task_id}: "
                            f"{task_changed.old_state} → "
                            f"{task_changed.new_state}"
                        ),
                        "correlation_id": str(task_changed.task_id),
                    },
                    metadata={
                        "task_id": str(task_changed.task_id),
                        "task_state": (
                            task_changed.new_state.value
                            if hasattr(task_changed.new_state, "value")
                            else str(task_changed.new_state)
                        ),
                    },
                )
        except Exception:
            pass
    bus.subscribe(TASK_STATE_CHANNEL, _on_task_state_persist)

    def _on_task_cleanup(event: Event) -> None:
        terminal = (TaskState.COMPLETE.value, TaskState.FAILED.value)
        if hasattr(event, "task_id") and hasattr(event, "new_state"):
            task_changed = event  # type: ignore
            val = (
                task_changed.new_state.value
                if isinstance(task_changed.new_state, TaskState)
                else str(task_changed.new_state)
            )
            if val in terminal:
                try:
                    working_backend.cleanup(str(task_changed.task_id))
                except Exception as e:
                    trace.emit(component="working_memory", level=TraceLevel.WARN,
                               message=f"Cleanup failed for {task_changed.task_id}: {e}")
    bus.subscribe(TASK_STATE_CHANNEL, _on_task_cleanup)

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
    parser.add_argument(
        "--dev",
        action="store_true",
        help="Skip conformance gate (development only)",
    )
    args = parser.parse_args()

    try:
        container = build_container(dev_mode=args.dev)
        trace = container.retrieve(TraceEmitter)
        bus = container.retrieve(EventBus)

        trace.emit(
            component="main",
            level=TraceLevel.INFO,
            message="Composition root built successfully — Plan 1 components wired",
        )
        for event in trace.get_events():
            level_str = event.level.value if hasattr(event.level, 'value') else str(event.level)
            print(f"[{level_str}] {event.component}: {event.message}")
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
