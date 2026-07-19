from __future__ import annotations

import asyncio
import datetime
import tempfile
import uuid
from pathlib import Path

import pytest
from sovereignai.managers.base import DepartmentManager
from sovereignai.messaging.adapter import DepartmentMessagingAdapter
from sovereignai.messaging.bus import InterDepartmentBus
from sovereignai.messaging.schema import CrossDepartmentMessage, MessageType
from sovereignai.shared.container import DIContainer
from sovereignai.shared.event_bus import EventBus
from sovereignai.shared.event_registry import EventRegistry
from sovereignai.shared.trace_emitter import TraceEmitter


class MockResearchManager(DepartmentManager):

    def __init__(self, container: DIContainer) -> None:
        super().__init__(container)
        self.research_results = []

    async def build_context(self, task):
        return {"domain": "research"}

    async def _build_context_impl(self, task):
        return {"domain": "research"}

    def validate(self, deliverable):
        return {"valid": True}

    async def execute_task(self, task):
        result = {"research": f"Research completed for {task}"}
        self.research_results.append(result)
        return result


class MockCodingManager(DepartmentManager):

    def __init__(self, container: DIContainer) -> None:
        super().__init__(container)
        self.coding_results = []

    async def build_context(self, task):
        return {"domain": "coding"}

    async def _build_context_impl(self, task):
        return {"domain": "coding"}

    def validate(self, deliverable):
        return {"valid": True}

    async def execute_task(self, task):
        result = {"code": f"Code implemented for {task}"}
        self.coding_results.append(result)
        return result


@pytest.fixture
def container():
    return DIContainer()


@pytest.fixture
def trace():
    return TraceEmitter()


@pytest.fixture
def registry():
    return EventRegistry()


@pytest.fixture
def event_bus(trace, registry):
    return EventBus(trace=trace, registry=registry)


@pytest.fixture
def temp_db():
    with tempfile.NamedTemporaryFile(delete=False, suffix=".db") as f:
        db_path = Path(f.name)
    yield db_path
    if db_path.exists():
        db_path.unlink()


@pytest.fixture
def bus(event_bus, registry, trace, temp_db):
    allowed = {"coding", "research", "orchestrator"}
    return InterDepartmentBus(
        event_bus=event_bus,
        registry=registry,
        trace=trace,
        allowed_departments=allowed,
        audit_db_path=temp_db,
    )


@pytest.fixture
def research_manager(container):
    return MockResearchManager(container)


@pytest.fixture
def coding_manager(container):
    return MockCodingManager(container)


@pytest.fixture
def research_adapter(research_manager, bus, trace):
    return DepartmentMessagingAdapter(
        manager=research_manager, department_name="research", bus=bus, trace=trace
    )


@pytest.fixture
def coding_adapter(coding_manager, bus, trace):
    return DepartmentMessagingAdapter(
        manager=coding_manager, department_name="coding", bus=bus, trace=trace
    )


def test_multi_department_workflow(
    bus, research_adapter, coding_adapter, research_manager, coding_manager
):
    async def workflow():
        research_request = CrossDepartmentMessage(
            sender="orchestrator",
            recipient="research",
            payload={"task": "Research AI implementation patterns"},
            correlation_id=uuid.uuid4(),
            timestamp=datetime.datetime.now(datetime.UTC),
            message_type=MessageType.REQUEST,
        )

        research_response = await bus.send(research_request)
        assert research_response is not None
        assert research_response.sender == "research"
        assert research_response.recipient == "orchestrator"
        assert research_response.message_type == MessageType.RESPONSE

        coding_request = CrossDepartmentMessage(
            sender="orchestrator",
            recipient="coding",
            payload={
                "task": "Implement AI based on research",
                "research_data": research_response.payload,
            },
            correlation_id=uuid.uuid4(),
            timestamp=datetime.datetime.now(datetime.UTC),
            message_type=MessageType.REQUEST,
        )

        coding_response = await bus.send(coding_request)
        assert coding_response is not None
        assert coding_response.sender == "coding"
        assert coding_response.recipient == "orchestrator"
        assert coding_response.message_type == MessageType.RESPONSE

        return {
            "research": research_response.payload,
            "coding": coding_response.payload,
        }

    result = asyncio.run(workflow())
    assert "research" in result
    assert "coding" in result


def test_orchestrator_coordinates_departments(
    bus, research_adapter, coding_adapter, research_manager, coding_manager
):
    async def orchestrator_workflow():
        task = "Research this and code it"

        research_msg = CrossDepartmentMessage(
            sender="orchestrator",
            recipient="research",
            payload={"task": task},
            correlation_id=uuid.uuid4(),
            timestamp=datetime.datetime.now(datetime.UTC),
            message_type=MessageType.REQUEST,
        )

        research_result = await bus.send(research_msg)
        if research_result is None:
            return {"error": "Research failed"}

        coding_msg = CrossDepartmentMessage(
            sender="orchestrator",
            recipient="coding",
            payload={"task": task, "research": research_result.payload},
            correlation_id=uuid.uuid4(),
            timestamp=datetime.datetime.now(datetime.UTC),
            message_type=MessageType.REQUEST,
        )

        coding_result = await bus.send(coding_msg)
        if coding_result is None:
            return {"error": "Coding failed"}

        return {
            "status": "completed",
            "research": research_result.payload,
            "coding": coding_result.payload,
        }

    result = asyncio.run(orchestrator_workflow())
    assert result["status"] == "completed"
    assert "research" in result
    assert "coding" in result


def test_department_isolation(bus, research_adapter, coding_adapter):
    async def test_isolation():
        msg_to_research = CrossDepartmentMessage(
            sender="orchestrator",
            recipient="research",
            payload={"task": "Research task"},
            correlation_id=uuid.uuid4(),
            timestamp=datetime.datetime.now(datetime.UTC),
            message_type=MessageType.REQUEST,
        )

        msg_to_coding = CrossDepartmentMessage(
            sender="orchestrator",
            recipient="coding",
            payload={"task": "Coding task"},
            correlation_id=uuid.uuid4(),
            timestamp=datetime.datetime.now(datetime.UTC),
            message_type=MessageType.REQUEST,
        )

        research_response = await bus.send(msg_to_research)
        coding_response = await bus.send(msg_to_coding)

        assert research_response is not None
        assert coding_response is not None
        assert research_response.sender == "research"
        assert coding_response.sender == "coding"

    asyncio.run(test_isolation())


def test_error_handling_in_workflow(bus, research_adapter, coding_adapter):
    async def workflow_with_error():
        invalid_msg = CrossDepartmentMessage(
            sender="orchestrator",
            recipient="education",
            payload={"task": "Task to non-existent department"},
            correlation_id=uuid.uuid4(),
            timestamp=datetime.datetime.now(datetime.UTC),
            message_type=MessageType.REQUEST,
        )

        response = await bus.send(invalid_msg)
        assert response is None

        valid_msg = CrossDepartmentMessage(
            sender="orchestrator",
            recipient="research",
            payload={"task": "Valid task"},
            correlation_id=uuid.uuid4(),
            timestamp=datetime.datetime.now(datetime.UTC),
            message_type=MessageType.REQUEST,
        )

        response = await bus.send(valid_msg)
        assert response is not None

    asyncio.run(workflow_with_error())


def test_concurrent_department_requests(bus, research_adapter, coding_adapter):
    async def concurrent_workflow():
        tasks = []
        for i in range(3):
            research_msg = CrossDepartmentMessage(
                sender="orchestrator",
                recipient="research",
                payload={"task": f"Research task {i}"},
                correlation_id=uuid.uuid4(),
                timestamp=datetime.datetime.now(datetime.UTC),
                message_type=MessageType.REQUEST,
            )
            tasks.append(bus.send(research_msg))

        responses = await asyncio.gather(*tasks)
        assert len(responses) == 3
        for response in responses:
            assert response is not None
            assert response.sender == "research"

    asyncio.run(concurrent_workflow())
