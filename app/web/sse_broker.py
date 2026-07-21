"""SSE Broker for server-sent events.

Provides shared SSE infrastructure for Plan 31+ endpoints with:
- Per-connection bounded queues (max 100 events)
- Per-endpoint replay buffers (max 100 events) for reconnection
- Auth validation and session management
- Keepalive (30s)
- Overflow control
- Epoch protection for replay
"""

import asyncio
import contextlib
import secrets
import uuid
from collections import deque
from dataclasses import dataclass, field
from typing import Any, AsyncGenerator

from fastapi import Request


@dataclass
class SSEConnection:
    """Represents a single SSE client connection."""

    queue: asyncio.Queue
    authenticated: bool = False
    username: str | None = None
    session_id: str | None = None
    created_at: float = field(default_factory=lambda: asyncio.get_event_loop().time())


@dataclass
class ReplayBuffer:
    """Per-endpoint replay buffer for reconnection support."""

    events: deque = field(default_factory=lambda: deque(maxlen=100))
    current_counter: int = 0
    current_epoch: int = 0


class SSEBroker:
    """Shared SSE broker for Plan 31+ endpoints.

    Manages SSE connections, replay buffers, auth, and event delivery.
    """

    def __init__(self, stream_epoch: int | None = None):
        """Initialize SSE broker.

        Args:
            stream_epoch: Optional epoch ID. If not provided, generates UUID-based epoch.
        """
        if stream_epoch is None:
            # UUID-based epoch prevents collision on rapid restarts
            stream_epoch = uuid.uuid4().int % (2**63)

        self.stream_epoch = stream_epoch
        self.connections: dict[str, SSEConnection] = {}
        self.replay_buffers: dict[str, ReplayBuffer] = {}
        self._lock = asyncio.Lock()
        self._event_bus = None  # Will be injected via DI
        self._trace_emitter = None  # Will be injected via DI

    def set_event_bus(self, event_bus: Any) -> None:
        """Set EventBus for subscription."""
        self._event_bus = event_bus

    def set_trace_emitter(self, trace_emitter: Any) -> None:
        """Set TraceEmitter for overflow logging."""
        self._trace_emitter = trace_emitter

    async def subscribe_to_endpoint(self, endpoint_name: str) -> None:
        """Subscribe to EventBus events for an endpoint."""
        if self._event_bus is None:
            return

        # Subscription logic will be endpoint-specific
        # This is a placeholder for the actual subscription mechanism
        pass

    async def create_connection(
        self,
        request: Request,
        endpoint_name: str,
        auth_validator: Any,
    ) -> tuple[SSEConnection, str]:
        """Create a new SSE connection.

        Args:
            request: FastAPI request object
            endpoint_name: Name of the SSE endpoint
            auth_validator: Async function to validate auth, returns
                (is_valid, username, session_id)

        Returns:
            (connection, connection_id)
        """
        connection_id = secrets.token_urlsafe(16)

        # Validate auth
        is_valid, username, session_id = await auth_validator(request)
        if not is_valid:
            raise PermissionError("Authentication failed")

        # Create connection with bounded queue (max 100 events)
        queue: asyncio.Queue = asyncio.Queue(maxsize=100)
        connection = SSEConnection(
            queue=queue,
            authenticated=True,
            username=username,
            session_id=session_id,
        )

        async with self._lock:
            self.connections[connection_id] = connection
            # Ensure replay buffer exists for endpoint
            if endpoint_name not in self.replay_buffers:
                self.replay_buffers[endpoint_name] = ReplayBuffer(
                    current_epoch=self.stream_epoch
                )

        return connection, connection_id

    async def remove_connection(self, connection_id: str) -> None:
        """Remove a connection."""
        async with self._lock:
            if connection_id in self.connections:
                del self.connections[connection_id]

    async def send_event(
        self,
        connection_id: str,
        event_type: str,
        data: dict[str, Any],
        event_id: str | None = None,
    ) -> bool:
        """Send an event to a specific connection.

        Args:
            connection_id: Connection identifier
            event_type: SSE event type
            data: Event data (will be JSON serialized)
            event_id: Optional event ID (defaults to auto-generated)

        Returns:
            True if sent, False if queue overflow
        """
        async with self._lock:
            connection = self.connections.get(connection_id)
            if not connection:
                return False

            # Try to send to queue
            try:
                if event_id is None:
                    # Auto-generate event ID if not provided
                    event_id = f"{self.stream_epoch}:{secrets.token_urlsafe(8)}"

                import json
                sse_message = f"event: {event_type}\nid: {event_id}\ndata: {json.dumps(data)}\n\n"
                connection.queue.put_nowait(sse_message)
                return True
            except asyncio.QueueFull:
                # Queue overflow - drop oldest
                try:
                    connection.queue.get_nowait()
                    import json
                    sse_data = json.dumps(data)
                    sse_message = f"event: {event_type}\nid: {event_id}\ndata: {sse_data}\n\n"
                    connection.queue.put_nowait(sse_message)
                    return True
                except asyncio.QueueEmpty:
                    return False

    async def broadcast_to_endpoint(
        self,
        endpoint_name: str,
        event_type: str,
        data: dict[str, Any],
    ) -> None:
        """Broadcast an event to all connections on an endpoint.

        Also stores in replay buffer for reconnection support.

        Args:
            endpoint_name: Name of the endpoint
            event_type: SSE event type
            data: Event data
        """
        async with self._lock:
            # Ensure replay buffer exists for endpoint
            if endpoint_name not in self.replay_buffers:
                self.replay_buffers[endpoint_name] = ReplayBuffer(
                    current_epoch=self.stream_epoch
                )

            # Update replay buffer
            buffer = self.replay_buffers[endpoint_name]
            buffer.current_counter += 1
            event_id = f"{buffer.current_epoch}:{buffer.current_counter}"
            buffer.events.append(
                {
                    "id": event_id,
                    "type": event_type,
                    "data": data,
                }
            )

            # Broadcast to all connections
            connection_ids = list(self.connections.keys())
            for conn_id in connection_ids:
                await self.send_event(conn_id, event_type, data, event_id)

    async def replay_events(
        self,
        connection_id: str,
        endpoint_name: str,
        last_event_id: str | None,
    ) -> bool:
        """Replay missed events from buffer to a connection.

        Args:
            connection_id: Connection identifier
            endpoint_name: Name of the endpoint
            last_event_id: Last event ID from client (Last-Event-ID header)

        Returns:
            True if replay successful, False if epoch mismatch
        """
        async with self._lock:
            if endpoint_name not in self.replay_buffers:
                return True  # No buffer to replay from

            buffer = self.replay_buffers[endpoint_name]

            # Parse last_event_id to extract epoch and counter
            if last_event_id:
                try:
                    epoch_str, counter_str = last_event_id.split(":", 1)
                    last_epoch = int(epoch_str)
                    last_counter = int(counter_str)

                    # Check epoch mismatch
                    if last_epoch != buffer.current_epoch:
                        # Send replay_unavailable event
                        await self.send_event(
                            connection_id,
                            "replay_unavailable",
                            {"reason": "epoch_mismatch"},
                        )
                        return False
                except (ValueError, AttributeError):
                    # Invalid last_event_id format, skip replay
                    return True

            # Replay events after last_event_id
            if last_event_id:
                for event in buffer.events:
                    event_id = event["id"]
                    try:
                        _, counter_str = event_id.split(":", 1)
                        event_counter = int(counter_str)
                        if event_counter > last_counter:
                            await self.send_event(
                                connection_id,
                                event["type"],
                                event["data"],
                                event_id,
                            )
                    except (ValueError, AttributeError):
                        continue
            else:
                # No last_event_id, replay all
                for event in buffer.events:
                    await self.send_event(
                        connection_id,
                        event["type"],
                        event["data"],
                        event["id"],
                    )

        return True

    async def send_overflow_event(
        self,
        connection_id: str,
        dropped_count: int,
        endpoint_name: str,
    ) -> None:
        """Send overflow event outside the bounded queue.

        Overflow events bypass the queue and carry no id field.

        Args:
            connection_id: Connection identifier
            dropped_count: Number of events dropped
            endpoint_name: Name of the endpoint
        """
        async with self._lock:
            connection = self.connections.get(connection_id)
            if not connection:
                return

        # Send overflow event directly (bypass queue)
        # This is a simplified implementation - in production would use direct write
        overflow_data = {"dropped": dropped_count}
        import json
        overflow_message = f"event: overflow\ndata: {json.dumps(overflow_data)}\n\n"

        # Log to trace emitter
        if self._trace_emitter:
            self._trace_emitter.emit(
                event_type="sse_overflow",
                details={"dropped": dropped_count, "endpoint": endpoint_name},
            )

        # In real implementation, would write directly to response
        # For now, we'll put it in the queue but without id
        with contextlib.suppress(asyncio.QueueFull):
            connection.queue.put_nowait(overflow_message)

    async def keepalive_task(self, connection_id: str, interval: float = 30.0) -> None:
        """Send keepalive comments to keep connection alive.

        Args:
            connection_id: Connection identifier
            interval: Keepalive interval in seconds
        """
        while True:
            await asyncio.sleep(interval)

            async with self._lock:
                connection = self.connections.get(connection_id)
                if not connection:
                    break

            try:
                # Send keepalive comment
                keepalive_message = ": keepalive\n\n"
                await self.send_event_raw(connection_id, keepalive_message)
            except Exception:
                # Connection likely dead
                await self.remove_connection(connection_id)
                break

    async def send_event_raw(self, connection_id: str, message: str) -> None:
        """Send raw SSE message to connection."""
        async with self._lock:
            connection = self.connections.get(connection_id)
            if not connection:
                return

            with contextlib.suppress(asyncio.QueueFull):
                connection.queue.put_nowait(message)

    async def auth_check_task(
        self,
        connection_id: str,
        auth_validator: Any,
        interval: float = 30.0,
    ) -> None:
        """Periodically check auth session validity.

        Args:
            connection_id: Connection identifier
            auth_validator: Async function to validate auth
            interval: Check interval in seconds
        """
        while True:
            await asyncio.sleep(interval)

            async with self._lock:
                connection = self.connections.get(connection_id)
                if not connection:
                    break

            # Validate session
            is_valid = await auth_validator(None, connection.session_id)
            if not is_valid:
                # Send auth_expired event and close
                await self.send_event(
                    connection_id,
                    "auth_expired",
                    {"reason": "session_expired"},
                )
                await self.remove_connection(connection_id)
                break

    async def event_generator(
        self,
        connection_id: str,
        request: Request,
    ) -> AsyncGenerator[str, None]:
        """Generate SSE events for a connection.

        Args:
            connection_id: Connection identifier
            request: FastAPI request object

        Yields:
            SSE event strings
        """
        async with self._lock:
            connection = self.connections.get(connection_id)
            if not connection:
                return

        try:
            while True:
                # Check if client disconnected
                if await request.is_disconnected():
                    break

                # Get event from queue
                try:
                    event = await asyncio.wait_for(
                        connection.queue.get(),
                        timeout=1.0,
                    )
                    yield event
                except TimeoutError:
                    # No event, send keepalive
                    yield ": keepalive\n\n"
        except asyncio.CancelledError:
            pass
        finally:
            await self.remove_connection(connection_id)
