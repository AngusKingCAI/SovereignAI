from __future__ import annotations

from uuid import UUID, uuid4

from sovereignai.shared.auth import AuthMiddleware
from sovereignai.shared.capability_graph import ICapabilityIndex
from sovereignai.shared.task_state_machine import ITaskStateQuery, TaskStateMachine
from sovereignai.shared.trace_emitter import TraceEmitter
from sovereignai.shared.types import (
    CapabilityAPIError,
    CapabilityCategory,
    CapabilityDeclaration,
    CapabilityQuery,
    CapabilityResponse,
    DAGValidationError,
    NoActiveProviderError,
    Task,
    TaskState,
    TraceLevel,
    now_utc,
)


class CapabilityAPI:

    def __init__(
        self,
        auth: AuthMiddleware,
        capability_index: ICapabilityIndex,
        task_state_query: ITaskStateQuery,
        state_machine: TaskStateMachine,
        trace: TraceEmitter,
    ) -> None:
        self._auth = auth
        self._index = capability_index
        self._tasks = task_state_query
        self._state_machine = state_machine
        self._trace = trace

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
        self._auth.validate(token)
        # Per Finding 3: validate capability exists before accepting
        providers = self._index.find_providers(category, capability_name)
        if not providers:
            raise NoActiveProviderError(
                f"No provider registered for {category}/{capability_name}"
            )
        # Defensive copy: extract provider_id and declaration before creating Task (S2.25 L14)
        provider_id, declaration = providers[0]
        task_id = uuid4()
        task = Task(
            task_id=task_id,
            capability=CapabilityDeclaration(
                category=category,
                name=capability_name,
                version=declaration.version,  # use the highest-priority provider's version
            ),
            payload=payload,
            submitted_at=now_utc(),
        )
        # Per Finding 1: submit to the state machine so the task is tracked
        # Per Rev3 Finding 9: wrap in try/except to convert lower-level
        # errors to CapabilityAPIError.
        # Per Rev4 Finding 4: catch ONLY specific exceptions (not bare
        # `except Exception`). Unexpected exceptions (TypeError,
        # AttributeError, etc.) propagate uncaught — they indicate bugs
        # that should fail fast, not be masked.
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

    def get_task_state(self, token: str, task_id: UUID) -> TaskState | None:
        self._auth.validate(token)
        return self._tasks.get_state(task_id)
