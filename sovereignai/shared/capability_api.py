from __future__ import annotations

import asyncio
from collections.abc import AsyncGenerator
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
    HardwareSnapshot,
    MemoryBackendInfo,
    ModelEntry,
    NoActiveProviderError,
    ServiceStatus,
    Task,
    TaskState,
    TaskStateSummary,
    TraceEvent,
    TraceLevel,
    bind_correlation_id,
    current_correlation_id,
    new_correlation_id,
    now_utc,
    reset_correlation_id,
)


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
                from sovereignai.memory.working_backend import WorkingMemoryBackend
                from sovereignai.memory.episodic_backend import EpisodicMemoryBackend
                from sovereignai.memory.procedural_backend import ProceduralMemoryBackend
                from sovereignai.memory.trace_backend import TraceMemoryBackend

                backend_type = "unknown"
                if isinstance(backend, WorkingMemoryBackend):
                    backend_type = "working"
                    capacity_mb = 0
                    used_mb = sum(len(records) for records in backend._store.values())
                elif isinstance(backend, (EpisodicMemoryBackend, ProceduralMemoryBackend, TraceMemoryBackend)):
                    if isinstance(backend, EpisodicMemoryBackend):
                        backend_type = "episodic"
                    elif isinstance(backend, ProceduralMemoryBackend):
                        backend_type = "procedural"
                    else:
                        backend_type = "trace"
                    cursor = backend._conn.cursor()
                    cursor.execute("SELECT COUNT(*) FROM episodes")
                    record_count = cursor.fetchone()[0] or 0
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
        return catalog.list_models()

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

    def query_service_registry(self, token: str) -> list[ServiceStatus]:
        self._auth.validate(token)
        results = []
        if self._service_registry is None:
            return results
        for service_name in self._service_registry.list_services():
            provider = self._service_registry.get_service(service_name)
            status = provider.health_check()
            results.append(status)
        return results

    def query_logs(self, token: str, correlation_id: str | None = None) -> list[TraceEvent]:
        self._auth.validate(token)
        return self._trace.get_events()
