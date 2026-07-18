from datetime import UTC, datetime
from uuid import uuid4

import pytest
from sovereignai.shared.event_bus import EventBus
from sovereignai.shared.event_registry import EventRegistry
from sovereignai.shared.task_state_machine import ITaskStateQuery, TaskStateMachine
from sovereignai.shared.trace_emitter import TraceEmitter
from sovereignai.shared.types import (
    TASK_STATE_CHANNEL,
    CapabilityCategory,
    CapabilityDeclaration,
    DAGSpec,
    DAGValidationError,
    InvalidStateTransitionError,
    Task,
    TaskState,
    UnknownTaskError,
)


@pytest.fixture
def bus(trace: TraceEmitter) -> EventBus:
    registry = EventRegistry()
    return EventBus(trace=trace, registry=registry)

@pytest.fixture
def trace() -> TraceEmitter:
    return TraceEmitter()

@pytest.fixture
def machine(bus: EventBus, trace: TraceEmitter) -> TaskStateMachine:
    return TaskStateMachine(bus=bus, trace=trace)

def test_submit_sets_received(machine: TaskStateMachine) -> None:
    task = Task(  # noqa: E501
        task_id=uuid4(),
        capability=CapabilityDeclaration(
            category=CapabilityCategory.TOOL,
            name='test_tool',
            version='1.0.0'
        ),
        payload='{}',
        submitted_at=datetime.now(UTC)
    )
    machine.submit(task)
    assert machine.get_state(task.task_id) == TaskState.RECEIVED

def test_valid_transition_publishes_event(machine: TaskStateMachine, bus: EventBus) -> None:
    events_received = []
    bus.subscribe(TASK_STATE_CHANNEL, lambda e: events_received.append(e))
    task = Task(  # noqa: E501
        task_id=uuid4(),
        capability=CapabilityDeclaration(
            category=CapabilityCategory.TOOL,
            name='test_tool',
            version='1.0.0'
        ),
        payload='{}',
        submitted_at=datetime.now(UTC)
    )
    machine.submit(task)
    machine.transition(task.task_id, TaskState.QUEUED)
    assert len(events_received) == 2
    assert events_received[1].old_state == TaskState.RECEIVED
    assert events_received[1].new_state == TaskState.QUEUED

def test_invalid_transition_raises(machine: TaskStateMachine) -> None:
    task = Task(  # noqa: E501
        task_id=uuid4(),
        capability=CapabilityDeclaration(
            category=CapabilityCategory.TOOL,
            name='test_tool',
            version='1.0.0'
        ),
        payload='{}',
        submitted_at=datetime.now(UTC)
    )
    machine.submit(task)
    with pytest.raises(InvalidStateTransitionError):
        machine.transition(task.task_id, TaskState.COMPLETE)
    assert machine.get_state(task.task_id) == TaskState.RECEIVED

def test_terminal_states_raise_on_transition(machine: TaskStateMachine) -> None:
    task = Task(  # noqa: E501
        task_id=uuid4(),
        capability=CapabilityDeclaration(
            category=CapabilityCategory.TOOL,
            name='test_tool',
            version='1.0.0'
        ),
        payload='{}',
        submitted_at=datetime.now(UTC)
    )
    machine.submit(task)
    machine.transition(task.task_id, TaskState.QUEUED)
    machine.transition(task.task_id, TaskState.EXECUTING)
    machine.transition(task.task_id, TaskState.COMPLETE)
    with pytest.raises(InvalidStateTransitionError):
        machine.transition(task.task_id, TaskState.QUEUED)

def test_get_state_unknown_returns_none(machine: TaskStateMachine) -> None:
    unknown_id = uuid4()
    assert machine.get_state(unknown_id) is None

def test_list_tasks_returns_insertion_order(machine: TaskStateMachine) -> None:  # noqa: E501
    task1 = Task(  # noqa: E501
        task_id=uuid4(),
        capability=CapabilityDeclaration(
            category=CapabilityCategory.TOOL,
            name='test_tool',
            version='1.0.0'
        ),
        payload='{}',
        submitted_at=datetime.now(UTC)
    )
    task2 = Task(  # noqa: E501
        task_id=uuid4(),
        capability=CapabilityDeclaration(
            category=CapabilityCategory.TOOL,
            name='test_tool',
            version='1.0.0'
        ),
        payload='{}',
        submitted_at=datetime.now(UTC)
    )
    task3 = Task(  # noqa: E501
        task_id=uuid4(),
        capability=CapabilityDeclaration(
            category=CapabilityCategory.TOOL,
            name='test_tool',
            version='1.0.0'
        ),
        payload='{}',
        submitted_at=datetime.now(UTC)
    )
    machine.submit(task1)
    machine.submit(task2)
    machine.submit(task3)
    tasks = machine.list_tasks()
    assert tasks == (task1, task2, task3)

def test_protocol_compliance(machine: TaskStateMachine) -> None:
    assert isinstance(machine, ITaskStateQuery)

def test_transitions_published_in_order(machine: TaskStateMachine, bus: EventBus) -> None:
    events_received = []
    bus.subscribe(TASK_STATE_CHANNEL, lambda e: events_received.append(e))
    task = Task(  # noqa: E501
        task_id=uuid4(),
        capability=CapabilityDeclaration(
            category=CapabilityCategory.TOOL,
            name='test_tool',
            version='1.0.0'
        ),
        payload='{}',
        submitted_at=datetime.now(UTC)
    )
    machine.submit(task)
    machine.transition(task.task_id, TaskState.QUEUED)
    machine.transition(task.task_id, TaskState.EXECUTING)
    assert len(events_received) == 3
    assert events_received[0].new_state == TaskState.RECEIVED
    assert events_received[1].new_state == TaskState.QUEUED
    assert events_received[2].new_state == TaskState.EXECUTING

def test_transition_unknown_task_raises_unknown_task_error(machine: TaskStateMachine) -> None:
    unknown_id = uuid4()
    with pytest.raises(UnknownTaskError):
        machine.transition(unknown_id, TaskState.QUEUED)

def test_submit_with_valid_dag_passes(machine: TaskStateMachine) -> None:
    task = Task(  # noqa: E501
        task_id=uuid4(),
        capability=CapabilityDeclaration(
            category=CapabilityCategory.TOOL,
            name='test_tool',
            version='1.0.0'
        ),
        payload='{}',
        submitted_at=datetime.now(UTC)
    )
    dag = DAGSpec(  # noqa: E501
        nodes=('node1', 'node2'),
        edges=(('node1', 'node2'),),
        input_types={'node2': 'type1'},
        output_types={'node1': 'type1'}
    )
    machine.submit(task, dag=dag)
    assert machine.get_state(task.task_id) == TaskState.RECEIVED

def test_submit_with_invalid_dag_raises(machine: TaskStateMachine) -> None:
    task = Task(  # noqa: E501
        task_id=uuid4(),
        capability=CapabilityDeclaration(
            category=CapabilityCategory.TOOL,
            name='test_tool',
            version='1.0.0'
        ),
        payload='{}',
        submitted_at=datetime.now(UTC)
    )
    dag = DAGSpec(  # noqa: E501
        nodes=('node1', 'node2'),
        edges=(('node1', 'node2'), ('node2', 'node1')),
        input_types={},
        output_types={}
    )
    with pytest.raises(DAGValidationError):
        machine.submit(task, dag=dag)
    assert machine.get_state(task.task_id) is None
