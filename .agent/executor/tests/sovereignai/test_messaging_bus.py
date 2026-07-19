from __future__ import annotations

import asyncio
import datetime
import tempfile
import uuid
from pathlib import Path

import pytest
from sovereignai.messaging.bus import InterDepartmentBus
from sovereignai.messaging.schema import CrossDepartmentMessage, MessageType
from sovereignai.shared.event_bus import EventBus
from sovereignai.shared.event_registry import EventRegistry
from sovereignai.shared.trace_emitter import TraceEmitter
from sovereignai.shared.types import Channel, Event, TraceLevel


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


def test_bus_initialization(bus):
    assert bus._allowed_departments == {"coding", "research", "orchestrator"}


def test_register_handler_allowed_recipient(bus):
    async def dummy_handler(msg):
        return None

    bus.register_handler("coding", dummy_handler)
    assert "coding" in bus._handlers
    assert len(bus._handlers["coding"]) == 1


def test_register_handler_disallowed_recipient(bus):
    async def dummy_handler(msg):
        return None

    with pytest.raises(ValueError, match="not in whitelist"):
        bus.register_handler("education", dummy_handler)


def test_send_message_with_allowed_sender_and_recipient(bus):
    response_payload = {"result": "success"}

    async def coding_handler(msg):
        return CrossDepartmentMessage(
            sender="coding",
            recipient="research",
            payload=response_payload,
            correlation_id=msg.correlation_id,
            timestamp=datetime.datetime.now(datetime.UTC),
            message_type=MessageType.RESPONSE,
        )

    bus.register_handler("coding", coding_handler)

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
    assert response.payload == response_payload


def test_send_message_with_disallowed_sender(bus):
    async def coding_handler(msg):
        return None

    bus.register_handler("coding", coding_handler)

    msg = CrossDepartmentMessage(
        sender="education",
        recipient="coding",
        payload={"task": "implement feature"},
        correlation_id=uuid.uuid4(),
        timestamp=datetime.datetime.now(datetime.UTC),
        message_type=MessageType.REQUEST,
    )

    response = asyncio.run(bus.send(msg))
    assert response is None


def test_send_message_with_disallowed_recipient(bus):
    async def coding_handler(msg):
        return None

    bus.register_handler("coding", coding_handler)

    msg = CrossDepartmentMessage(
        sender="research",
        recipient="education",
        payload={"task": "implement feature"},
        correlation_id=uuid.uuid4(),
        timestamp=datetime.datetime.now(datetime.UTC),
        message_type=MessageType.REQUEST,
    )

    response = asyncio.run(bus.send(msg))
    assert response is None


def test_send_message_no_handlers_registered(bus):
    msg = CrossDepartmentMessage(
        sender="research",
        recipient="coding",
        payload={"task": "implement feature"},
        correlation_id=uuid.uuid4(),
        timestamp=datetime.datetime.now(datetime.UTC),
        message_type=MessageType.REQUEST,
    )

    response = asyncio.run(bus.send(msg))
    assert response is None


def test_send_message_handler_exception(bus):
    async def failing_handler(msg):
        raise RuntimeError("Handler failed")

    bus.register_handler("coding", failing_handler)

    msg = CrossDepartmentMessage(
        sender="research",
        recipient="coding",
        payload={"task": "implement feature"},
        correlation_id=uuid.uuid4(),
        timestamp=datetime.datetime.now(datetime.UTC),
        message_type=MessageType.REQUEST,
    )

    response = asyncio.run(bus.send(msg))
    assert response is None


def test_send_message_sync_handler(bus):
    def sync_handler(msg):
        return CrossDepartmentMessage(
            sender="coding",
            recipient="research",
            payload={"result": "sync success"},
            correlation_id=msg.correlation_id,
            timestamp=datetime.datetime.now(datetime.UTC),
            message_type=MessageType.RESPONSE,
        )

    bus.register_handler("coding", sync_handler)

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
    assert response.payload == {"result": "sync success"}


def test_publish_event(bus):
    event = Event(
        channel=Channel("test.channel"),
        correlation_id=uuid.uuid4(),
        timestamp=datetime.datetime.now(datetime.UTC),
        version=1,
        trace_level=TraceLevel.INFO,
    )
    bus.publish_event(event)


def test_publish_event_async(bus):
    async def test_async():
        event = Event(
            channel=Channel("test.channel"),
            correlation_id=uuid.uuid4(),
            timestamp=datetime.datetime.now(datetime.UTC),
            version=1,
            trace_level=TraceLevel.INFO,
        )
        await bus.publish_event_async(event)

    asyncio.run(test_async())
