from unittest.mock import Mock

from fastapi.testclient import TestClient

from sovereignai.shared.trace_emitter import TraceEmitter
from sovereignai.shared.types import TraceEvent, TraceLevel, new_correlation_id, now_utc
from web.main import app
from web.schemas import TraceEventDTO


def test_get_traces_history_returns_200_with_list():
    client = TestClient(app)

    mock_trace = TraceEmitter()
    mock_trace.emit(component="Test", level=TraceLevel.INFO, message="test message")

    mock_auth = Mock()
    mock_auth._password_hashes = ["test"]

    app.state.container = Mock()
    app.state.container.retrieve.side_effect = (  # noqa: E501
        lambda x: mock_trace if x == TraceEmitter else mock_auth
    )

    response = client.get("/api/traces/history", headers={"cookie": "session_id=test"})

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1
    assert data[0]["component"] == "Test"
    assert data[0]["level"] == "info"
    assert data[0]["message"] == "test message"


def test_sse_subscription_receives_live_events():
    mock_trace = TraceEmitter()
    mock_auth = Mock()
    mock_auth.validate.return_value = Mock(username="test")

    app.state.container = Mock()
    app.state.container.retrieve.side_effect = (  # noqa: E501
        lambda x: mock_trace if x == TraceEmitter else mock_auth
    )

    received_events = []

    def on_event(event):
        received_events.append(event)

    unsubscribe = mock_trace.subscribe_callback(on_event)

    mock_trace.emit(component="Test", level=TraceLevel.INFO, message="test message")

    unsubscribe()

    assert len(received_events) == 1
    assert received_events[0].message == "test message"


def test_unsubscribe_stops_receiving_events():
    mock_trace = TraceEmitter()

    received_events = []

    def on_event(event):
        received_events.append(event)

    unsubscribe = mock_trace.subscribe_callback(on_event)

    mock_trace.emit(component="Test", level=TraceLevel.INFO, message="test1")
    unsubscribe()
    mock_trace.emit(component="Test", level=TraceLevel.INFO, message="test2")

    assert len(received_events) == 1
    assert received_events[0].message == "test1"


def test_faulty_callback_does_not_block_emit():
    import time

    mock_trace = TraceEmitter()

    received_events = []

    def faulty_callback(event):
        raise Exception("test error")

    def good_callback(event):
        received_events.append(event)

    unsub1 = mock_trace.subscribe_callback(faulty_callback)
    unsub2 = mock_trace.subscribe_callback(good_callback)

    mock_trace.emit(component="Test", level=TraceLevel.INFO, message="test message")

    time.sleep(0.5)  # Allow async callback delivery

    unsub1()
    unsub2()

    assert len(received_events) == 1
    assert received_events[0].message == "test message"


def test_trace_event_dto_serialization():
    event = TraceEvent(
        component="Test",
        level=TraceLevel.INFO,
        message="test message",
        timestamp=now_utc(),
        correlation_id=new_correlation_id(),
    )

    dto = TraceEventDTO(
        timestamp=event.timestamp.isoformat(),
        level=event.level.value,
        component=event.component,
        correlation_id=str(event.correlation_id),
        message=event.message,
    )

    data = dto.model_dump(mode='json')
    assert data["component"] == "Test"
    assert data["level"] == "info"
    assert data["message"] == "test message"
    assert "correlation_id" in data
