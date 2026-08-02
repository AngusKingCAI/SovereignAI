from __future__ import annotations

import asyncio
from collections.abc import AsyncGenerator
from typing import TYPE_CHECKING, Any, cast
from uuid import UUID, uuid4

from sovereignai.shared.auth import AuthMiddleware
from sovereignai.shared.capability_graph import ICapabilityIndex
from sovereignai.shared.database_registry import DatabaseRegistry
from sovereignai.shared.hardware_probe import HardwareProbe
from sovereignai.shared.model_catalog import ModelCatalog
from sovereignai.shared.service_registry import ServiceRegistry
from sovereignai.shared.task_state_machine import ITaskStateQuery, TaskStateMachine
from sovereignai.shared.trace_emitter import TraceEmitter
from sovereignai.shared.types import (
    CapabilityAPIError,
    CapabilityCategory,
    CapabilityDeclaration,
    CapabilityQuery,
    CapabilityResponse,
    DAGValidationError,
    EpisodicQuery,
    EpisodicResult,
    HardwareSnapshot,
    MemoryBackendInfo,
    ModelEntry,
    ModelFilter,
    NoActiveProviderError,
    ProceduralQuery,
    ProceduralResult,
    Task,
    TaskState,
    TaskStateSummary,
    TraceEvent,
    TraceLevel,
    TraceQuery,
    TraceResult,
    WorkingQuery,
    WorkingResult,
    bind_correlation_id,
    current_correlation_id,
    new_correlation_id,
    now_utc,
    reset_correlation_id,
)

if TYPE_CHECKING:
    from services.base import ServiceStatus


class CapabilityAPI:

    def __init__(
        self,
        auth: AuthMiddleware,
        capability_index: ICapabilityIndex,
        task_state_query: ITaskStateQuery,
        state_machine: TaskStateMachine,
        trace: TraceEmitter,
        hardware_probe: HardwareProbe,
        database_registry: DatabaseRegistry | None = None,
        service_registry: ServiceRegistry | None = None,
        memory_backends: dict[str, object] | None = None,
        lifecycle_manager: object | None = None,
    ) -> None:
        self._auth = auth
        self._index = capability_index
        self._tasks = task_state_query
        self._state_machine = state_machine
        self._trace = trace
        self._hardware_probe = hardware_probe
        self._database_registry = database_registry
        self._service_registry = service_registry
        self._memory_backends = memory_backends or {}
        self._lifecycle_manager = lifecycle_manager

    def query_capabilities(
        self, token: str, query: CapabilityQuery
    ) -> CapabilityResponse:
        self._auth.validate(token)
        providers = self._index.find_providers(query.category, query.name)
        component_ids = tuple(component_id for component_id, _ in providers)
        self._trace.emit(
            component="CapabilityAPI",
            level=TraceLevel.DEBUG,
            message=f"Query {query.category}/{query.name} -> {len(component_ids)} providers",
        )
        return CapabilityResponse(query=query, providers=component_ids)

    def submit_task(
        self,
        token: str,
        category: CapabilityCategory,
        capability_name: str,
        payload: str,
    ) -> UUID:
        existing = current_correlation_id()
        token_obj = None
        if existing is None:
            cid = new_correlation_id()
            token_obj = bind_correlation_id(cid)

        try:
            self._auth.validate(token)
            providers = self._index.find_providers(category, capability_name)
            if not providers:
                raise NoActiveProviderError(
                    f"No provider registered for {category}/{capability_name}"
                )
            provider_id, declaration = providers[0]
            task_id = uuid4()
            task = Task(
                task_id=task_id,
                capability=CapabilityDeclaration(
                    category=category,
                    name=capability_name,
                    version=declaration.version,
                ),
                payload=payload,
                submitted_at=now_utc(),
            )
            try:
                self._state_machine.submit(task)
            except DAGValidationError as exc:
                raise CapabilityAPIError(
                    f"Failed to submit task {task_id} to state machine: {exc}",
                    cause=exc,
                ) from exc
            self._trace.emit(
                component="CapabilityAPI",
                level=TraceLevel.INFO,
                message=f"Task {task_id} submitted for {category}/{capability_name!r}",
            )
            return task_id
        finally:
            if existing is None and token_obj is not None:
                reset_correlation_id(token_obj)

    def get_task_state(self, token: str, task_id: UUID) -> TaskState | None:
        self._auth.validate(token)
        return self._tasks.get_state(task_id)

    def sample_hardware(self) -> HardwareSnapshot:
        return self._hardware_probe.sample()

    async def stream_hardware(self) -> AsyncGenerator[HardwareSnapshot, None]:
        while True:
            yield self._hardware_probe.sample()
            await asyncio.sleep(1.0)

    def query_memory_backends(self, token: str) -> list[MemoryBackendInfo]:
        self._auth.validate(token)
        results = []
        if self._memory_backends is None:
            return results
        for name, backend in self._memory_backends.items():
            try:
                from sovereignai.memory.episodic_backend import EpisodicMemoryBackend
                from sovereignai.memory.procedural_backend import ProceduralMemoryBackend
                from sovereignai.memory.trace_backend import TraceMemoryBackend
                from sovereignai.memory.working_backend import WorkingMemoryBackend

                backend_type = "unknown"
                if isinstance(backend, WorkingMemoryBackend):
                    backend_type = "working"
                    capacity_mb = 0
                    used_mb = sum(len(records) for records in backend._store.values())
                elif isinstance(
                    backend,
                    (EpisodicMemoryBackend, ProceduralMemoryBackend, TraceMemoryBackend),
                ):
                    if isinstance(backend, EpisodicMemoryBackend):
                        backend_type = "episodic"
                        if backend._conn:
                            cursor = backend._conn.cursor()
                            cursor.execute("SELECT COUNT(*) FROM episodes")
                            record_count = cursor.fetchone()[0] or 0
                        else:
                            record_count = 0
                    elif isinstance(backend, ProceduralMemoryBackend):
                        backend_type = "procedural"
                        # Procedural backend doesn't use SQLite
                        record_count = 0
                    else:
                        backend_type = "trace"
                        record_count = 0
                    capacity_mb = 0
                    used_mb = record_count
                else:
                    backend_type = "unknown"
                    capacity_mb = 0
                    used_mb = 0

                results.append(
                    MemoryBackendInfo(
                        name=name,
                        type=backend_type,
                        status="active",
                        capacity_mb=capacity_mb,
                        used_mb=used_mb,
                    )
                )
            except Exception as e:
                self._trace.emit(
                    component="CapabilityAPI",
                    level=TraceLevel.ERROR,
                    message=f"Failed to query memory backend {name}: {e}",
                )
        return results

    def query_hardware_status(self, token: str) -> HardwareSnapshot:
        self._auth.validate(token)
        return self._hardware_probe.sample()

    def query_model_catalog(self, token: str) -> list[ModelEntry]:
        self._auth.validate(token)
        if self._database_registry is None:
            return []
        catalog = ModelCatalog(self._database_registry, self._trace)
        return cast(list[ModelEntry], catalog.list_models(ModelFilter()))

    def query_skills(self, token: str) -> list[dict[str, Any]]:
        self._auth.validate(token)
        results: list[dict[str, Any]] = []
        manifests = self._index.list_all_components()

        for manifest in manifests:
            for cap in manifest.provides:
                if cap.category.value == "skill":
                    results.append(
                        {
                            "id": str(manifest.component_id),
                            "name": cap.name,
                            "version": manifest.version,
                            "description": f"{manifest.component_id} v{manifest.version}",
                        }
                    )

        return results

    def query_task_states(self, token: str) -> list[TaskStateSummary]:
        self._auth.validate(token)
        results = []
        tasks = self._tasks.list_tasks()
        for task in tasks:
            state = self._tasks.get_state(task.task_id)
            if state:
                results.append(
                    TaskStateSummary(
                        task_id=task.task_id,
                        state=state,
                        worker_id=None,
                        submitted_at=task.submitted_at,
                        completed_at=None,
                    )
                )
        return results

    def query_service_registry(self, token: str) -> list[tuple[str, ServiceStatus]]:
        self._auth.validate(token)
        results: list[tuple[str, ServiceStatus]] = []
        if self._service_registry is None:
            return results
        for service_name in self._service_registry.list_services():
            provider = self._service_registry.get_service(service_name)
            status = provider.health_check()
            results.append((service_name, status))
        return results

    def query_logs(self, token: str, correlation_id: str | None = None) -> list[TraceEvent]:
        self._auth.validate(token)
        return cast(list[TraceEvent], self._trace.get_events())

    def query_memory(
        self,
        token: str,
        query: EpisodicQuery | ProceduralQuery | WorkingQuery | TraceQuery,
    ) -> list[EpisodicResult | ProceduralResult | WorkingResult | TraceResult]:
        self._auth.validate(token)
        if self._memory_backends is None:
            return []

        match query:
            case EpisodicQuery():
                backend = self._memory_backends.get("episodic")
                if backend is None:
                    return []
                from sovereignai.memory.episodic_backend import EpisodicMemoryBackend

                if not isinstance(backend, EpisodicMemoryBackend):
                    return []
                raw_results = backend.query(query)
                return [
                    EpisodicResult(
                        id=r["id"],
                        timestamp=r["timestamp"],
                        component=r["component"],
                        task_id=r["task_id"],
                        event_type=r["event_type"],
                        data=r["data"],
                        metadata=r["metadata"],
                    )
                    for r in raw_results
                ]
            case ProceduralQuery():
                backend = self._memory_backends.get("procedural")
                if backend is None:
                    return []
                from sovereignai.memory.procedural_backend import ProceduralMemoryBackend

                if not isinstance(backend, ProceduralMemoryBackend):
                    return []
                raw_results = backend.query(query)
                return [
                    ProceduralResult(
                        id=r.get("id", ""),
                        pattern=r.get("pattern", ""),
                        confidence=r.get("confidence", 0.0),
                        created_at=r.get("created_at", 0.0),
                    )
                    for r in raw_results
                ]
            case WorkingQuery():
                backend = self._memory_backends.get("working")
                if backend is None:
                    return []
                from sovereignai.memory.working_backend import WorkingMemoryBackend

                if not isinstance(backend, WorkingMemoryBackend):
                    return []
                raw_results = backend.query(query)
                return [
                    WorkingResult(
                        id=r.get("id", ""),
                        context_id=r.get("context_id", ""),
                        data=r,
                    )
                    for r in raw_results
                ]
            case TraceQuery():
                backend = self._memory_backends.get("trace")
                if backend is None:
                    return []
                from sovereignai.memory.trace_backend import TraceMemoryBackend

                if not isinstance(backend, TraceMemoryBackend):
                    return []
                raw_results = backend.query(query)
                return [
                    TraceResult(
                        id=r.get("id", ""),
                        timestamp=r.get("timestamp", 0.0),
                        component=r.get("component", ""),
                        level=r.get("level", ""),
                        message=r.get("message", ""),
                        correlation_id=r.get("correlation_id", ""),
                    )
                    for r in raw_results
                ]
            case _:
                return []
