from __future__ import annotations

import datetime
import uuid

from sovereignai.messaging.schema import CrossDepartmentMessage, MessageType


def test_message_type_enum():
    assert MessageType.REQUEST == "request"
    assert MessageType.RESPONSE == "response"
    assert MessageType.NOTIFICATION == "notification"
    assert MessageType.ERROR == "error"


def test_cross_department_message_creation():
    msg = CrossDepartmentMessage(
        sender="coding",
        recipient="research",
        payload={"task": "implement feature"},
        correlation_id=uuid.uuid4(),
        timestamp=datetime.datetime.now(datetime.UTC),
        message_type=MessageType.REQUEST,
    )
    assert msg.sender == "coding"
    assert msg.recipient == "research"
    assert msg.payload == {"task": "implement feature"}
    assert msg.message_type == MessageType.REQUEST


def test_cross_department_message_frozen():
    msg = CrossDepartmentMessage(
        sender="coding",
        recipient="research",
        payload={"task": "implement feature"},
        correlation_id=uuid.uuid4(),
        timestamp=datetime.datetime.now(datetime.UTC),
        message_type=MessageType.REQUEST,
    )
    try:
        msg.sender = "education"
        raise AssertionError("Should not be able to modify frozen dataclass")
    except (AttributeError, TypeError):
        pass


def test_cross_department_message_all_message_types():
    correlation_id = uuid.uuid4()
    timestamp = datetime.datetime.now(datetime.UTC)
    payload = {"data": "test"}

    request_msg = CrossDepartmentMessage(
        sender="coding",
        recipient="research",
        payload=payload,
        correlation_id=correlation_id,
        timestamp=timestamp,
        message_type=MessageType.REQUEST,
    )
    assert request_msg.message_type == MessageType.REQUEST

    response_msg = CrossDepartmentMessage(
        sender="research",
        recipient="coding",
        payload=payload,
        correlation_id=correlation_id,
        timestamp=timestamp,
        message_type=MessageType.RESPONSE,
    )
    assert response_msg.message_type == MessageType.RESPONSE

    notification_msg = CrossDepartmentMessage(
        sender="operations",
        recipient="all",
        payload=payload,
        correlation_id=correlation_id,
        timestamp=timestamp,
        message_type=MessageType.NOTIFICATION,
    )
    assert notification_msg.message_type == MessageType.NOTIFICATION

    error_msg = CrossDepartmentMessage(
        sender="coding",
        recipient="orchestrator",
        payload=payload,
        correlation_id=correlation_id,
        timestamp=timestamp,
        message_type=MessageType.ERROR,
    )
    assert error_msg.message_type == MessageType.ERROR
