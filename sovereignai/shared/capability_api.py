from __future__ import annotations

import asyncio
from collections.abc import AsyncGenerator
from uuid import UUID, uuid4

from sovereignai.shared.auth import AuthMiddleware
from sovereignai.shared.capability_graph import ICapabilityIndex
from sovereignai.shared.hardware_probe import HardwareProbe
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
    NoActiveProviderError,
    Task,
    TaskState,
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
    ) -> None:
        self._auth = auth
        self._index = capability_index
        self._tasks = task_state_query
        self._state_machine = state_machine
        self._trace = trace
        self._hardware_probe = hardware_probe

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
