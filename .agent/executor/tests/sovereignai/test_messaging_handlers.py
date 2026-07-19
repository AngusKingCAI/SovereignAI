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


class MockDepartmentManager(DepartmentManager):

    def __init__(self, container: DIContainer) -> None:
        super().__init__(container)
        self.processed_requests = []

    async def build_context(self, task):
        return {"mock": "context"}

    async def _build_context_impl(self, task):
        return {"mock": "context"}

    def validate(self, deliverable):
        return {"valid": True}

    async def execute_task(self, task):
        return {"result": "task completed"}


@pytest.fixture
def container():
    return DIContainer()


@pytest.fixture
def manager(container):
    return MockDepartmentManager(container)


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
def adapter(manager, bus, trace):
    return DepartmentMessagingAdapter(
        manager=manager, department_name="coding", bus=bus, trace=trace
    )


def test_adapter_initialization(adapter, manager, bus, trace):
    assert adapter._manager == manager
    assert adapter._department_name == "coding"
    assert adapter._bus == bus
    assert adapter._trace == trace


def test_adapter_registers_handler(bus, adapter):
    assert "coding" in bus._handlers
    assert len(bus._handlers["coding"]) == 1


def test_handle_request(adapter):
    msg = CrossDepartmentMessage(
        sender="research",
        recipient="coding",
        payload={"task": "implement feature"},
        correlation_id=uuid.uuid4(),
        timestamp=datetime.datetime.now(datetime.UTC),
        message_type=MessageType.REQUEST,
    )

    response = asyncio.run(adapter.handle_message(msg))
    assert response is not None
    assert response.sender == "coding"
    assert response.recipient == "research"
    assert response.message_type == MessageType.RESPONSE
    assert response.payload["status"] == "processed"


def test_handle_request_with_error(adapter):
    msg = CrossDepartmentMessage(
        sender="research",
        recipient="coding",
        payload={"task": "implement feature"},
        correlation_id=uuid.uuid4(),
        timestamp=datetime.datetime.now(datetime.UTC),
        message_type=MessageType.REQUEST,
    )

    async def failing_process(message):
        raise RuntimeError("Processing failed")

    adapter._process_request = failing_process

    response = asyncio.run(adapter.handle_message(msg))
    assert response is not None
    assert response.message_type == MessageType.ERROR
    assert "error" in response.payload


def test_handle_response(adapter):
    msg = CrossDepartmentMessage(
        sender="research",
        recipient="coding",
        payload={"result": "success"},
        correlation_id=uuid.uuid4(),
        timestamp=datetime.datetime.now(datetime.UTC),
        message_type=MessageType.RESPONSE,
    )

    response = asyncio.run(adapter.handle_message(msg))
    assert response is None


def test_handle_notification(adapter):
    msg = CrossDepartmentMessage(
        sender="operations",
        recipient="coding",
        payload={"alert": "system maintenance"},
        correlation_id=uuid.uuid4(),
        timestamp=datetime.datetime.now(datetime.UTC),
        message_type=MessageType.NOTIFICATION,
    )

    response = asyncio.run(adapter.handle_message(msg))
    assert response is None


def test_handle_error(adapter):
    msg = CrossDepartmentMessage(
        sender="research",
        recipient="coding",
        payload={"error": "processing failed"},
        correlation_id=uuid.uuid4(),
        timestamp=datetime.datetime.now(datetime.UTC),
        message_type=MessageType.ERROR,
    )

    response = asyncio.run(adapter.handle_message(msg))
    assert response is None


def test_auto_reply_with_correlation_id(adapter):
    correlation_id = uuid.uuid4()
    msg = CrossDepartmentMessage(
        sender="research",
        recipient="coding",
        payload={"task": "implement feature"},
        correlation_id=correlation_id,
        timestamp=datetime.datetime.now(datetime.UTC),
        message_type=MessageType.REQUEST,
    )

    response = asyncio.run(adapter.handle_message(msg))
    assert response is not None
    assert response.correlation_id == correlation_id


def test_message_routing_through_bus_and_adapter(bus, adapter):
    msg = CrossDepartmentMessage(
        sender="research",
        recipient="coding",
        payload={"task": "implement feature"},
        correlation_id=uuid.uuid4(),
        timestamp=datetime.datetime.now(datetime.UTC),
        message_type=MessageType.REQUEST,
    )

    response = asyncio.run(bus.send(msg))
    assert response is not None
    assert response.sender == "coding"
    assert response.recipient == "research"
    assert response.message_type == MessageType.RESPONSE
