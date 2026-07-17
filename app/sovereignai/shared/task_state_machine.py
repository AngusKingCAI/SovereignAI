from __future__ import annotations

from threading import RLock
from typing import Protocol, runtime_checkable
from uuid import UUID

from app.sovereignai.shared.event_bus import EventBus
from app.sovereignai.shared.trace_emitter import TraceEmitter
from app.sovereignai.shared.types import (
    TASK_STATE_CHANNEL,
    DAGSpec,
    InvalidStateTransitionError,
    Task,
    TaskState,
    TaskStateChanged,
    UnknownTaskError,
    now_utc,
)
from app.sovereignai.shared.types_base import CorrelationId

# NOTE (Rev6 Finding 3): UnknownTaskError, InvalidStateTransitionError, and
# DAGValidationError are defined in shared/types.py (Plan 3 S1.1 per Rev5
# Finding 1) and imported above. Do NOT define local copies — the import is
# canonical. Local definitions would create separate exception classes that
# callers catching types.DAGValidationError would not match.


@runtime_checkable
class ITaskStateQuery(Protocol):

    def get_state(self, task_id: UUID) -> TaskState | None:
        ...

    def list_tasks(self) -> tuple[Task, ...]:
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

    def __init__(self, bus: EventBus, trace: TraceEmitter) -> None:
        self._bus = bus
        self._trace = trace
        self._tasks: dict[UUID, Task] = {}
        self._states: dict[UUID, TaskState] = {}
        self._lock = RLock()

    def submit(self, task: Task, dag: DAGSpec | None = None) -> None:
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
        with self._lock:
            old_state = self._states.get(task_id)
            if old_state is None:
                raise UnknownTaskError(task_id)
            if new_state not in _VALID_TRANSITIONS.get(old_state, []):
                raise InvalidStateTransitionError(task_id, old_state, new_state)
            self._states[task_id] = new_state
        self._publish(task_id, old_state, new_state)

    def get_state(self, task_id: UUID) -> TaskState | None:
        with self._lock:
            return self._states.get(task_id)

    def list_tasks(self) -> tuple[Task, ...]:
        with self._lock:
            return tuple(self._tasks.values())

    def _publish(self, task_id: UUID, old_state: TaskState | None,
                 new_state: TaskState) -> None:
        event = TaskStateChanged(
            channel=TASK_STATE_CHANNEL,
            correlation_id=CorrelationId(task_id),
            timestamp=now_utc(),
            task_id=task_id,
            old_state=old_state or TaskState.RECEIVED,
            new_state=new_state,
        )
        self._bus.publish(event)


# Removed in Rev2 per Finding 7: now_utc_safe() lazy-import wrapper.
# _publish() now calls now_utc() directly from the top-level import.
