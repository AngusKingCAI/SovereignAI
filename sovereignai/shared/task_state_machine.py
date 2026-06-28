"""Track task state transitions and publish them on the event bus.

Per A6: composite tasks must pass DAG validation before entering the
state machine. The validator (S5 of this plan) is called from
submit() before the task is accepted.

Per A7: persistence is in-memory only. Durable backends and crash
recovery are deferred to DEBT. On restart, all task state is lost.

Per A9: state transitions are published on TASK_STATE_CHANNEL. The
event bus guarantees in-order delivery per channel, so subscribers
see transitions in the order they occurred.
"""
from __future__ import annotations

from threading import Lock
from typing import Protocol, runtime_checkable
from uuid import UUID

from sovereignai.shared.event_bus import EventBus
from sovereignai.shared.trace_emitter import TraceEmitter
from sovereignai.shared.types import (
    TASK_STATE_CHANNEL,
    DAGSpec,
    InvalidStateTransitionError,
    Task,
    TaskState,
    TaskStateChanged,
    UnknownTaskError,
    now_utc,
)

# NOTE (Rev6 Finding 3): UnknownTaskError, InvalidStateTransitionError, and
# DAGValidationError are defined in shared/types.py (Plan 3 S1.1 per Rev5
# Finding 1) and imported above. Do NOT define local copies — the import is
# canonical. Local definitions would create separate exception classes that
# callers catching types.DAGValidationError would not match.


@runtime_checkable
class ITaskStateQuery(Protocol):
    """Locked query interface for the task state machine.

    Plan 4's Capability API imports ONLY this protocol — never the
    concrete TaskStateMachine class. This enforces AR7 (UIs are
    separate processes consuming the Capability API).
    """

    def get_state(self, task_id: UUID) -> TaskState | None:
        """Return the current state of a task by its ID, or None if unknown.

        Args:
            task_id: UUID of the task to query.

        Returns:
            TaskState if the task is tracked, None if unknown (per
            Finding 5 — None distinguishes "never submitted" from
            "submitted and failed").
        """
        ...

    def list_tasks(self) -> tuple[Task, ...]:
        """Return all tasks currently tracked by the state machine.

        Returns:
            Tuple of Task instances, oldest first.
        """
        ...


# Valid state transitions (per the state machine diagram in the vision)
_VALID_TRANSITIONS: dict[TaskState, list[TaskState]] = {
    TaskState.RECEIVED: [TaskState.QUEUED, TaskState.FAILED],
    TaskState.QUEUED: [TaskState.EXECUTING, TaskState.FAILED],
    TaskState.EXECUTING: [TaskState.COMPLETE, TaskState.FAILED],
    TaskState.COMPLETE: [],   # terminal
    TaskState.FAILED: [],     # terminal
}


class TaskStateMachine:
    """Track task state transitions and publish them on the event bus.

    The state machine depends on EventBus (Plan 1) for publishing
    transitions and TraceEmitter (Plan 1) for logging invalid
    transition attempts. It implements ITaskStateQuery so callers
    depend on the protocol, not the concrete class.
    """

    def __init__(self, bus: EventBus, trace: TraceEmitter) -> None:
        """Create an empty state machine with no tracked tasks.

        Args:
            bus: Event bus for publishing TaskStateChanged events.
            trace: Trace emitter for logging invalid transitions.
        """
        self._bus = bus
        self._trace = trace
        self._tasks: dict[UUID, Task] = {}
        self._states: dict[UUID, TaskState] = {}
        self._lock = Lock()

    def submit(self, task: Task, dag: DAGSpec | None = None) -> None:
        """Accept a new task into the RECEIVED state, validating its DAG if provided.

        Per Finding 1 (Rev2): if a `dag` parameter is provided, the DAG
        validator runs BEFORE the task enters RECEIVED. If validation
        fails, DAGValidationError is raised and the task is NOT submitted.
        This satisfies A6 (composite skills must validate before entering
        the state machine).

        Per Finding 6 (Rev3): `dag` is now typed as `Optional[DAGSpec]`
        (a frozen dataclass defined in shared/types.py). Rev2 used a
        string forward reference `Optional["DAGSpec"]` but never
        defined the type — mypy blocked.

        Args:
            task: Frozen Task instance to track.
            dag: Optional DAGSpec for composite tasks. If provided,
                validated via validate_dag() before submission.
                If None (atomic task), validation is skipped.

        Raises:
            DAGValidationError: If `dag` is provided and fails validation.
        """
        if dag is not None:
            from sovereignai.shared.dag_validator import validate_dag
            validate_dag(
                nodes=list(dag.nodes),
                edges=list(dag.edges),
                input_types=dag.input_types,
                output_types=dag.output_types,
            )
        with self._lock:
            self._tasks[task.task_id] = task
            self._states[task.task_id] = TaskState.RECEIVED
        self._publish(task.task_id, None, TaskState.RECEIVED)

    def transition(self, task_id: UUID, new_state: TaskState) -> None:
        """Move a task to a new state if the transition is valid.

        Per Finding 3 (Rev2): invalid transitions now raise
        InvalidStateTransitionError instead of being silently logged.
        The task's state is NOT modified on invalid transition. Other
        tasks are unaffected (per-task isolation).

        Per Finding 11 (Rev3): unknown task_ids raise UnknownTaskError
        (not InvalidStateTransitionError with FAILED as old_state).

        Args:
            task_id: UUID of the task to transition.
            new_state: Target state.

        Raises:
            UnknownTaskError: If the task_id was never submitted.
            InvalidStateTransitionError: If the transition is not in
                the valid transitions table.
        """
        with self._lock:
            old_state = self._states.get(task_id)
            if old_state is None:
                raise UnknownTaskError(task_id)
            if new_state not in _VALID_TRANSITIONS.get(old_state, []):
                raise InvalidStateTransitionError(task_id, old_state, new_state)
            self._states[task_id] = new_state
        self._publish(task_id, old_state, new_state)

    def get_state(self, task_id: UUID) -> TaskState | None:
        """Return the current state of a task by its ID, or None if unknown.

        Per Finding 5 (Rev2): returns None for unknown UUIDs instead of
        FAILED. Callers must handle None explicitly — a None means "task
        was never submitted" which is distinct from "task was submitted
        and failed."

        Args:
            task_id: UUID of the task to query.

        Returns:
            TaskState if the task is tracked, None if unknown.
        """
        with self._lock:
            return self._states.get(task_id)

    def list_tasks(self) -> tuple[Task, ...]:
        """Return all tasks currently tracked by the state machine.

        Returns:
            Tuple of Task instances, in insertion order (oldest first).
        """
        with self._lock:
            return tuple(self._tasks.values())

    def _publish(self, task_id: UUID, old_state: TaskState | None,
                 new_state: TaskState) -> None:
        """Publish a TaskStateChanged event on the task state channel.

        Per Finding 7 (Rev2): uses `now_utc()` directly from the
        top-level import instead of the removed `now_utc_safe()` wrapper.

        Args:
            task_id: UUID of the task that transitioned.
            old_state: Previous state, or None for the initial RECEIVED.
            new_state: New state.
        """
        event = TaskStateChanged(
            channel=TASK_STATE_CHANNEL,
            correlation_id=task_id,
            timestamp=now_utc(),
            task_id=task_id,
            old_state=old_state or TaskState.RECEIVED,
            new_state=new_state,
        )
        self._bus.publish(event)


# Removed in Rev2 per Finding 7: now_utc_safe() lazy-import wrapper.
# _publish() now calls now_utc() directly from the top-level import.
