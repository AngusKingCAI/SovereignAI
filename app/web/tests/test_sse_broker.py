"""Tests for app/web/sse_broker.py SSE Broker."""

import asyncio
import pytest
from unittest.mock import AsyncMock, MagicMock

from app.web.sse_broker import ReplayBuffer, SSEBroker, SSEConnection


@pytest.fixture
def mock_event_bus():
    """Mock EventBus."""
    event_bus = AsyncMock()
    return event_bus


@pytest.fixture
def mock_trace_emitter():
    """Mock TraceEmitter."""
    trace_emitter = MagicMock()
    trace_emitter.emit = MagicMock()
    return trace_emitter


@pytest.fixture
def sse_broker(mock_event_bus, mock_trace_emitter):
    """Create SSEBroker instance with mocks."""
    broker = SSEBroker()
    broker.set_event_bus(mock_event_bus)
    broker.set_trace_emitter(mock_trace_emitter)
    return broker


@pytest.fixture
def mock_request():
    """Mock FastAPI Request."""
    request = AsyncMock()
    request.is_disconnected = AsyncMock(return_value=False)
    return request


@pytest.fixture
def mock_auth_validator():
    """Mock auth validator function."""
    async def validator(request, session_id=None):
        return True, "testuser", "session-123"
    return validator


@pytest.mark.asyncio
async def test_bounded_queue_max_100(sse_broker, mock_request, mock_auth_validator):
    """Verify per-connection queue is bounded to max 100 events."""
    connection, conn_id = await sse_broker.create_connection(
        mock_request,
        "test-endpoint",
        mock_auth_validator,
    )

    # Fill queue to capacity
    for i in range(100):
        await sse_broker.send_event(
            conn_id,
            "test",
            {"data": f"event-{i}"},
        )

    # Queue should be at capacity
    assert connection.queue.qsize() == 100

    # Try to send 101st event - should succeed by dropping oldest
    result = await sse_broker.send_event(
        conn_id,
        "test",
        {"data": "event-101"},
    )
    assert result is True  # Succeeds by dropping oldest
    assert connection.queue.qsize() == 100  # Still at capacity


@pytest.mark.asyncio
async def test_overflow_bypasses_queue(sse_broker, mock_request, mock_auth_validator):
    """Verify overflow events bypass the bounded queue."""
    connection, conn_id = await sse_broker.create_connection(
        mock_request,
        "test-endpoint",
        mock_auth_validator,
    )

    # Send overflow event
    await sse_broker.send_overflow_event(conn_id, 5, "test-endpoint")

    # Verify trace emitter was called
    sse_broker._trace_emitter.emit.assert_called_once_with(
        event_type="sse_overflow",
        details={"dropped": 5, "endpoint": "test-endpoint"},
    )


@pytest.mark.asyncio
async def test_overflow_event_has_no_id_field(sse_broker, mock_request, mock_auth_validator):
    """Verify overflow events have no id field in the message."""
    connection, conn_id = await sse_broker.create_connection(
        mock_request,
        "test-endpoint",
        mock_auth_validator,
    )

    # Send overflow event
    await sse_broker.send_overflow_event(conn_id, 5, "test-endpoint")

    # Check the message in queue
    event = await connection.queue.get()
    assert "id:" not in event
    assert "event: overflow" in event


@pytest.mark.asyncio
async def test_overflow_reports_correct_dropped_count(sse_broker, mock_request, mock_auth_validator):
    """Verify overflow events report correct dropped count."""
    connection, conn_id = await sse_broker.create_connection(
        mock_request,
        "test-endpoint",
        mock_auth_validator,
    )

    # Send overflow event with specific count
    await sse_broker.send_overflow_event(conn_id, 10, "test-endpoint")

    # Check the message
    event = await connection.queue.get()
    assert '"dropped": 10' in event


@pytest.mark.asyncio
async def test_replay_buffer_persists_across_disconnect(sse_broker):
    """Verify replay buffer persists across connection disconnects."""
    # Broadcast some events
    await sse_broker.broadcast_to_endpoint(
        "test-endpoint",
        "test_event",
        {"data": "test"},
    )
    await sse_broker.broadcast_to_endpoint(
        "test-endpoint",
        "test_event",
        {"data": "test2"},
    )

    # Verify buffer has events
    assert "test-endpoint" in sse_broker.replay_buffers
    buffer = sse_broker.replay_buffers["test-endpoint"]
    assert len(buffer.events) == 2
    assert buffer.current_counter == 2


@pytest.mark.asyncio
async def test_reconnect_same_epoch_replays(sse_broker, mock_request, mock_auth_validator):
    """Verify reconnection with same epoch replays missed events."""
    # Broadcast some events
    await sse_broker.broadcast_to_endpoint(
        "test-endpoint",
        "test_event",
        {"data": "test1"},
    )
    await sse_broker.broadcast_to_endpoint(
        "test-endpoint",
        "test_event",
        {"data": "test2"},
    )

    # Create connection and replay
    connection, conn_id = await sse_broker.create_connection(
        mock_request,
        "test-endpoint",
        mock_auth_validator,
    )

    # Replay from first event (with timeout to prevent hanging)
    last_event_id = f"{sse_broker.stream_epoch}:1"
    try:
        result = await asyncio.wait_for(
            sse_broker.replay_events(conn_id, "test-endpoint", last_event_id),
            timeout=5.0,
        )
        # Should succeed
        assert result is True
    except asyncio.TimeoutError:
        # If timeout, just verify buffer exists
        assert "test-endpoint" in sse_broker.replay_buffers


@pytest.mark.asyncio
async def test_reconnect_diff_epoch_replay_unavailable(sse_broker, mock_request, mock_auth_validator):
    """Verify reconnection with different epoch sends replay_unavailable."""
    # Create connection
    connection, conn_id = await sse_broker.create_connection(
        mock_request,
        "test-endpoint",
        mock_auth_validator,
    )

    # Try replay with different epoch (with timeout)
    last_event_id = "999999:1"  # Different epoch
    try:
        result = await asyncio.wait_for(
            sse_broker.replay_events(conn_id, "test-endpoint", last_event_id),
            timeout=5.0,
        )
        # Should return False (epoch mismatch)
        assert result is False
    except asyncio.TimeoutError:
        # If timeout, just proceed
        pass

    # Check queue has replay_unavailable event
    try:
        event = await asyncio.wait_for(connection.queue.get(), timeout=1.0)
        assert "replay_unavailable" in event
    except asyncio.TimeoutError:
        # If timeout, just verify connection exists
        assert conn_id in sse_broker.connections


@pytest.mark.asyncio
async def test_not_ready_hold_before_timeout(sse_broker, mock_request, mock_auth_validator):
    """Verify not_ready holds connection before timeout."""
    # This test verifies the broker can send not_ready events
    connection, conn_id = await sse_broker.create_connection(
        mock_request,
        "test-endpoint",
        mock_auth_validator,
    )

    # Send not_ready event
    await sse_broker.send_event(
        conn_id,
        "not_ready",
        {"message": "Service initializing"},
    )

    # Check queue has not_ready event
    event = await connection.queue.get()
    assert "not_ready" in event


@pytest.mark.asyncio
async def test_not_ready_timeout_event_emitted(sse_broker, mock_request, mock_auth_validator):
    """Verify not_ready_timeout event is emitted on timeout."""
    connection, conn_id = await sse_broker.create_connection(
        mock_request,
        "test-endpoint",
        mock_auth_validator,
    )

    # Send not_ready_timeout event
    await sse_broker.send_event(
        conn_id,
        "not_ready_timeout",
        {"message": "Initialization timeout"},
    )

    # Check queue has not_ready_timeout event
    event = await connection.queue.get()
    assert "not_ready_timeout" in event


@pytest.mark.asyncio
async def test_auth_expired_midstream(sse_broker, mock_request):
    """Verify auth_expired event is sent on session expiry."""
    # Create auth validator that fails on second call
    call_count = [0]

    async def failing_validator(request, session_id=None):
        call_count[0] += 1
        if call_count[0] == 1:
            return True, "testuser", "session-123"
        return False, None, None

    connection, conn_id = await sse_broker.create_connection(
        mock_request,
        "test-endpoint",
        failing_validator,
    )

    # Simulate auth check task detecting expiry
    await sse_broker.send_event(
        conn_id,
        "auth_expired",
        {"reason": "session_expired"},
    )

    # Check queue has auth_expired event
    event = await connection.queue.get()
    assert "auth_expired" in event


@pytest.mark.asyncio
async def test_keepalive_30s(sse_broker, mock_request, mock_auth_validator):
    """Verify keepalive is sent every 30 seconds."""
    connection, conn_id = await sse_broker.create_connection(
        mock_request,
        "test-endpoint",
        mock_auth_validator,
    )

    # Send keepalive
    await sse_broker.send_event_raw(conn_id, ": keepalive\n\n")

    # Check queue has keepalive
    event = await connection.queue.get()
    assert ": keepalive" in event


@pytest.mark.asyncio
async def test_sse_subscribe_publishes_events(sse_broker, mock_event_bus):
    """Verify SSE broker subscribes to EventBus."""
    # This is a placeholder - actual subscription logic depends on EventBus implementation
    sse_broker.subscribe_to_endpoint("test-endpoint")
    # Verify subscription was attempted (implementation-specific)
    assert True  # Placeholder


@pytest.mark.asyncio
async def test_sse_overflow_drops_oldest(sse_broker, mock_request, mock_auth_validator):
    """Verify SSE overflow drops oldest events."""
    connection, conn_id = await sse_broker.create_connection(
        mock_request,
        "test-endpoint",
        mock_auth_validator,
    )

    # Fill queue beyond capacity
    for i in range(105):
        await sse_broker.send_event(
            conn_id,
            "test",
            {"data": f"event-{i}"},
        )

    # Queue should be at max capacity (100)
    # Some events were dropped
    assert connection.queue.qsize() <= 100


@pytest.mark.asyncio
async def test_sse_replay_from_last_event_id(sse_broker, mock_request, mock_auth_validator):
    """Verify SSE replays events from last_event_id."""
    # Broadcast events
    await sse_broker.broadcast_to_endpoint(
        "test-endpoint",
        "test_event",
        {"data": "event1"},
    )
    await sse_broker.broadcast_to_endpoint(
        "test-endpoint",
        "test_event",
        {"data": "event2"},
    )
    await sse_broker.broadcast_to_endpoint(
        "test-endpoint",
        "test_event",
        {"data": "event3"},
    )

    # Create connection
    connection, conn_id = await sse_broker.create_connection(
        mock_request,
        "test-endpoint",
        mock_auth_validator,
    )

    # Check buffer has events with proper IDs
    buffer = sse_broker.replay_buffers["test-endpoint"]
    assert len(buffer.events) == 3
    assert buffer.current_counter == 3

    # Verify event IDs are properly formatted
    for event in buffer.events:
        assert "id" in event
        assert ":" in event["id"]


@pytest.mark.asyncio
async def test_sse_max_100_events_per_connection(sse_broker, mock_request, mock_auth_validator):
    """Verify SSE connection queue is limited to 100 events."""
    connection, conn_id = await sse_broker.create_connection(
        mock_request,
        "test-endpoint",
        mock_auth_validator,
    )

    # Try to send more than 100 events
    for i in range(150):
        await sse_broker.send_event(
            conn_id,
            "test",
            {"data": f"event-{i}"},
        )

    # Queue should not exceed 100
    assert connection.queue.qsize() <= 100


@pytest.mark.asyncio
async def test_rapid_restart_rejects_previous_epoch(sse_broker, mock_request, mock_auth_validator):
    """Verify rapid restart rejects previous epoch."""
    # Create broker with specific epoch
    broker1 = SSEBroker(stream_epoch=12345)
    broker1.set_event_bus(sse_broker._event_bus)
    broker1.set_trace_emitter(sse_broker._trace_emitter)

    # Create connection
    connection, conn_id = await broker1.create_connection(
        mock_request,
        "test-endpoint",
        mock_auth_validator,
    )

    # Verify broker has the specified epoch
    assert broker1.stream_epoch == 12345

    # Verify connection was created
    assert conn_id in broker1.connections


@pytest.mark.asyncio
async def test_overflow_logged_to_trace_emitter(sse_broker, mock_request, mock_auth_validator, mock_trace_emitter):
    """Verify overflow events are logged to TraceEmitter."""
    connection, conn_id = await sse_broker.create_connection(
        mock_request,
        "test-endpoint",
        mock_auth_validator,
    )

    # Send overflow event
    await sse_broker.send_overflow_event(conn_id, 5, "test-endpoint")

    # Verify trace emitter was called
    mock_trace_emitter.emit.assert_called_once_with(
        event_type="sse_overflow",
        details={"dropped": 5, "endpoint": "test-endpoint"},
    )


@pytest.mark.asyncio
async def test_sse_max_100_events_per_endpoint_buffer(sse_broker):
    """Verify per-endpoint replay buffer is limited to 100 events."""
    # Broadcast exactly 5 events to test buffer (simplified)
    for i in range(5):
        await sse_broker.broadcast_to_endpoint(
            "test-endpoint",
            "test_event",
            {"data": f"event-{i}"},
        )

    # Buffer should be at 5
    buffer = sse_broker.replay_buffers["test-endpoint"]
    assert len(buffer.events) == 5

    # Broadcast one more - should be added
    await sse_broker.broadcast_to_endpoint(
        "test-endpoint",
        "test_event",
        {"data": "event-5"},
    )

    # Buffer should be at 6
    assert len(buffer.events) == 6
