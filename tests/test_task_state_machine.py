"""Tests for the task state machine."""
from datetime import UTC, datetime
from uuid import uuid4

import pytest

from sovereignai.shared.event_bus import EventBus
from sovereignai.shared.task_state_machine import ITaskStateQuery, TaskStateMachine
from sovereignai.shared.trace_emitter import TraceEmitter
from sovereignai.shared.types import (
    CapabilityCategory,
    CapabilityDeclaration,
    DAGSpec,
    DAGValidationError,
    InvalidStateTransitionError,
    TASK_STATE_CHANNEL,
    Task,
    TaskState,
    TaskStateChanged,
    UnknownTaskError,
)


@pytest.fixture
def bus(trace: TraceEmitter) -> EventBus:
    """Create an event bus for testing."""
    return EventBus(trace=trace)


@pytest.fixture
def trace() -> TraceEmitter:
    """Create a trace emitter for testing."""
    return TraceEmitter()


@pytest.fixture
def machine(bus: EventBus, trace: TraceEmitter) -> TaskStateMachine:
    """Create a task state machine for testing."""
    return TaskStateMachine(bus=bus, trace=trace)


def test_submit_sets_received(machine: TaskStateMachine) -> None:
    """Submit a task and verify it enters RECEIVED state."""
    task = Task(
        task_id=uuid4(),
        capability=CapabilityDeclaration(
            category=CapabilityCategory.TOOL,
            name="test_tool",
            version="1.0.0",
        ),
        payload="{}",
        submitted_at=datetime.now(UTC),
    )
    machine.submit(task)
    assert machine.get_state(task.task_id) == TaskState.RECEIVED


def test_valid_transition_publishes_event(machine: TaskStateMachine, bus: EventBus) -> None:
    """Transition a task and verify a TaskStateChanged event is published."""
    events_received = []
    bus.subscribe(TASK_STATE_CHANNEL, lambda e: events_received.append(e))

    task = Task(
        task_id=uuid4(),
        capability=CapabilityDeclaration(
            category=CapabilityCategory.TOOL,
            name="test_tool",
            version="1.0.0",
        ),
        payload="{}",
        submitted_at=datetime.now(UTC),
    )
    machine.submit(task)

    machine.transition(task.task_id, TaskState.QUEUED)

    assert len(events_received) == 2  # submit + transition
    assert events_received[1].old_state == TaskState.RECEIVED
    assert events_received[1].new_state == TaskState.QUEUED


def test_invalid_transition_raises(machine: TaskStateMachine) -> None:
    """Attempt an invalid transition and verify InvalidStateTransitionError is raised."""
    task = Task(
        task_id=uuid4(),
        capability=CapabilityDeclaration(
            category=CapabilityCategory.TOOL,
            name="test_tool",
            version="1.0.0",
        ),
        payload="{}",
        submitted_at=datetime.now(UTC),
    )
    machine.submit(task)

    with pytest.raises(InvalidStateTransitionError):
        machine.transition(task.task_id, TaskState.COMPLETE)

    # State should remain unchanged
    assert machine.get_state(task.task_id) == TaskState.RECEIVED


def test_terminal_states_raise_on_transition(machine: TaskStateMachine) -> None:
    """Verify that transitioning from a terminal state raises InvalidStateTransitionError."""
    task = Task(
        task_id=uuid4(),
        capability=CapabilityDeclaration(
            category=CapabilityCategory.TOOL,
            name="test_tool",
            version="1.0.0",
        ),
        payload="{}",
        submitted_at=datetime.now(UTC),
    )
    machine.submit(task)
    machine.transition(task.task_id, TaskState.QUEUED)
    machine.transition(task.task_id, TaskState.EXECUTING)
    machine.transition(task.task_id, TaskState.COMPLETE)

    with pytest.raises(InvalidStateTransitionError):
        machine.transition(task.task_id, TaskState.QUEUED)


def test_get_state_unknown_returns_none(machine: TaskStateMachine) -> None:
    """Query an unknown task ID and verify None is returned."""
    unknown_id = uuid4()
    assert machine.get_state(unknown_id) is None


def test_list_tasks_returns_insertion_order(machine: TaskStateMachine) -> None:
    """Submit multiple tasks and verify list_tasks returns them in insertion order."""
    task1 = Task(
        task_id=uuid4(),
        capability=CapabilityDeclaration(
            category=CapabilityCategory.TOOL,
            name="test_tool",
            version="1.0.0",
        ),
        payload="{}",
        submitted_at=datetime.now(UTC),
    )
    task2 = Task(
        task_id=uuid4(),
        capability=CapabilityDeclaration(
            category=CapabilityCategory.TOOL,
            name="test_tool",
            version="1.0.0",
        ),
        payload="{}",
        submitted_at=datetime.now(UTC),
    )
    task3 = Task(
        task_id=uuid4(),
        capability=CapabilityDeclaration(
            category=CapabilityCategory.TOOL,
            name="test_tool",
            version="1.0.0",
        ),
        payload="{}",
        submitted_at=datetime.now(UTC),
    )

    machine.submit(task1)
    machine.submit(task2)
    machine.submit(task3)

    tasks = machine.list_tasks()
    assert tasks == (task1, task2, task3)


def test_protocol_compliance(machine: TaskStateMachine) -> None:
    """Verify the task state machine implements ITaskStateQuery."""
    assert isinstance(machine, ITaskStateQuery)


def test_transitions_published_in_order(machine: TaskStateMachine, bus: EventBus) -> None:
    """Verify that state transitions are published on the event bus in the correct order."""
    events_received = []
    bus.subscribe(TASK_STATE_CHANNEL, lambda e: events_received.append(e))

    task = Task(
        task_id=uuid4(),
        capability=CapabilityDeclaration(
            category=CapabilityCategory.TOOL,
            name="test_tool",
            version="1.0.0",
        ),
        payload="{}",
        submitted_at=datetime.now(UTC),
    )
    machine.submit(task)

    machine.transition(task.task_id, TaskState.QUEUED)
    machine.transition(task.task_id, TaskState.EXECUTING)

    assert len(events_received) == 3
    assert events_received[0].new_state == TaskState.RECEIVED
    assert events_received[1].new_state == TaskState.QUEUED
    assert events_received[2].new_state == TaskState.EXECUTING


def test_transition_unknown_task_raises_unknown_task_error(machine: TaskStateMachine) -> None:
    """Attempt to transition an unknown task and verify UnknownTaskError is raised."""
    unknown_id = uuid4()
    with pytest.raises(UnknownTaskError):
        machine.transition(unknown_id, TaskState.QUEUED)


def test_submit_with_valid_dag_passes(machine: TaskStateMachine) -> None:
    """Submit a task with a valid DAG and verify it enters RECEIVED state."""
    task = Task(
        task_id=uuid4(),
        capability=CapabilityDeclaration(
            category=CapabilityCategory.TOOL,
            name="test_tool",
            version="1.0.0",
        ),
        payload="{}",
        submitted_at=datetime.now(UTC),
    )
    dag = DAGSpec(
        nodes=("node1", "node2"),
        edges=(("node1", "node2"),),
        input_types={"node2": "type1"},
        output_types={"node1": "type1"},
    )
    machine.submit(task, dag=dag)
    assert machine.get_state(task.task_id) == TaskState.RECEIVED


def test_submit_with_invalid_dag_raises(machine: TaskStateMachine) -> None:
    """Submit a task with a cyclic DAG and verify DAGValidationError is raised."""
    task = Task(
        task_id=uuid4(),
        capability=CapabilityDeclaration(
            category=CapabilityCategory.TOOL,
            name="test_tool",
            version="1.0.0",
        ),
        payload="{}",
        submitted_at=datetime.now(UTC),
    )
    dag = DAGSpec(
        nodes=("node1", "node2"),
        edges=(("node1", "node2"), ("node2", "node1")),  # cycle
        input_types={},
        output_types={},
    )
    with pytest.raises(DAGValidationError):
        machine.submit(task, dag=dag)
    # Task should NOT be submitted
    assert machine.get_state(task.task_id) is None
