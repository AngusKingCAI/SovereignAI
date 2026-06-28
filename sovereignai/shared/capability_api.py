"""Public contract that UI processes consume to query state and submit tasks.

Per AR7: UIs may not import from sovereignai/ internals directly. They
consume this API only. The API depends on ICapabilityIndex (Plan 2)
and ITaskStateQuery (Plan 3) — never on concrete classes.

Per P8: the API exposes three operations:
  1. query_capabilities — what can the system do right now?
  2. submit_task — ask the system to do something
  3. subscribe_traces — observe what's happening (deferred to a later plan)
"""
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
    """Public interface for UI processes to query state and submit tasks.

    The API validates the session token on every call (per P6 login
    gate). It depends on a mix of protocols and concrete classes:
    - Query path (query_capabilities, get_task_state): uses ICapabilityIndex
      and ITaskStateQuery protocols (AR7-compliant).
    - Write path (submit_task): uses concrete TaskStateMachine (the
      ITaskStateQuery protocol is query-only; submit requires the writer).
    - Auth: uses concrete AuthMiddleware (auth is part of the API's
      constructor, not a queryable protocol).

    Per Rev3 Finding 13: docstring updated to accurately describe the
    concrete/protocol split (Rev2 incorrectly claimed "depends only on
    protocols").
    """

    def __init__(
        self,
        auth: AuthMiddleware,
        capability_index: ICapabilityIndex,
        task_state_query: ITaskStateQuery,
        state_machine: TaskStateMachine,
        trace: TraceEmitter,
    ) -> None:
        """Create a Capability API wired to the core's query protocols.

        Args:
            auth: Auth middleware for validating session tokens.
            capability_index: Protocol for querying capabilities (Plan 2).
            task_state_query: Protocol for querying task state (Plan 3).
            state_machine: Concrete TaskStateMachine for submitting tasks
                (per Finding 1 — submit_task needs the writer, not just
                the query protocol). Retrieved from the DI container.
            trace: Trace emitter for logging API calls.
        """
        self._auth = auth
        self._index = capability_index
        self._tasks = task_state_query
        self._state_machine = state_machine
        self._trace = trace

    def query_capabilities(
        self, token: str, query: CapabilityQuery
    ) -> CapabilityResponse:
        """Return the components that currently provide a requested capability category.

        Args:
            token: Session token from a prior login() call.
            query: What capability the UI is asking about.

        Returns:
            CapabilityResponse with the list of provider component IDs.

        Raises:
            AuthError: If the token is invalid or expired.
        """
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
        """Accept a new task from a UI process and return its tracking ID.

        Per Finding 1 (Rev2): the task IS submitted to the
        TaskStateMachine — it enters RECEIVED state and is queryable via
        ITaskStateQuery.get_state(). The actual routing to a worker
        remains deferred (post-batch) — the task stays in RECEIVED until
        a future plan wires the routing pipeline.

        Per Finding 2 (Rev2): the `category` parameter is now required —
        callers specify whether this is a TOOL, MODEL_INFERENCE, MEMORY,
        or COMMUNICATION capability. Rev1 hardcoded TOOL.

        Per Finding 3 (Rev2): the capability is validated against
        ICapabilityIndex before the task is accepted. If no provider is
        registered, NoActiveProviderError is raised.

        Args:
            token: Session token from a prior login() call.
            category: The capability category (TOOL, MODEL_INFERENCE, etc.).
            capability_name: What capability the task needs.
            payload: Opaque task payload (JSON or similar).

        Returns:
            UUID of the newly-created task (in RECEIVED state).

        Raises:
            AuthError: If the token is invalid or expired.
            NoActiveProviderError: If no provider is registered for the
                requested capability.
        """
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
        """Return the current state of a task by its ID, or None if unknown.

        Per Finding 5 (Rev2, Plan 3): ITaskStateQuery.get_state() now
        returns None for unknown UUIDs instead of FAILED. This method
        passes through the None — callers must handle it explicitly.

        Args:
            token: Session token from a prior login() call.
            task_id: UUID of the task to query.

        Returns:
            TaskState if the task is tracked, None if unknown.

        Raises:
            AuthError: If the token is invalid or expired.
        """
        self._auth.validate(token)
        return self._tasks.get_state(task_id)
