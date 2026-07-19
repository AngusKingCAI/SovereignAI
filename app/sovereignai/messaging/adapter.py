from __future__ import annotations

import datetime
from typing import TYPE_CHECKING

from sovereignai.managers.base import DepartmentManager
from sovereignai.messaging.bus import InterDepartmentBus
from sovereignai.messaging.schema import CrossDepartmentMessage, MessageType
from sovereignai.shared.trace_emitter import TraceEmitter
from sovereignai.shared.types import TraceLevel

if TYPE_CHECKING:
    pass


class DepartmentMessagingAdapter:

    def __init__(
        self,
        manager: DepartmentManager,
        department_name: str,
        bus: InterDepartmentBus,
        trace: TraceEmitter,
    ) -> None:
        self._manager = manager
        self._department_name = department_name
        self._bus = bus
        self._trace = trace

        self._bus.register_handler(department_name, self.handle_message)

        self._trace.emit(
            component="DepartmentMessagingAdapter",
            level=TraceLevel.INFO,
            message=f"Adapter registered for department {department_name}",
        )

    async def handle_message(
        self, message: CrossDepartmentMessage
    ) -> CrossDepartmentMessage | None:
        self._trace.emit(
            component="DepartmentMessagingAdapter",
            level=TraceLevel.DEBUG,
            message=f"Received message for {self._department_name}: {message.message_type}",
        )

        if message.message_type == MessageType.REQUEST:
            return await self._handle_request(message)
        elif message.message_type == MessageType.RESPONSE:
            return await self._handle_response(message)
        elif message.message_type == MessageType.NOTIFICATION:
            return await self._handle_notification(message)
        elif message.message_type == MessageType.ERROR:
            return await self._handle_error(message)

        return None

    async def _handle_request(
        self, message: CrossDepartmentMessage
    ) -> CrossDepartmentMessage | None:
        try:
            result = await self._process_request(message)
            return CrossDepartmentMessage(
                sender=self._department_name,
                recipient=message.sender,
                payload=result,
                correlation_id=message.correlation_id,
                timestamp=datetime.datetime.now(datetime.UTC),
                message_type=MessageType.RESPONSE,
            )
        except Exception as exc:
            self._trace.emit(
                component="DepartmentMessagingAdapter",
                level=TraceLevel.ERROR,
                message=f"Request handling failed: {exc}",
            )
            return CrossDepartmentMessage(
                sender=self._department_name,
                recipient=message.sender,
                payload={"error": str(exc)},
                correlation_id=message.correlation_id,
                timestamp=datetime.datetime.now(datetime.UTC),
                message_type=MessageType.ERROR,
            )

    async def _handle_response(
        self, message: CrossDepartmentMessage
    ) -> CrossDepartmentMessage | None:
        self._trace.emit(
            component="DepartmentMessagingAdapter",
            level=TraceLevel.DEBUG,
            message=f"Response received for correlation_id {message.correlation_id}",
        )
        return None

    async def _handle_notification(
        self, message: CrossDepartmentMessage
    ) -> CrossDepartmentMessage | None:
        self._trace.emit(
            component="DepartmentMessagingAdapter",
            level=TraceLevel.DEBUG,
            message=f"Notification received: {message.payload}",
        )
        return None

    async def _handle_error(
        self, message: CrossDepartmentMessage
    ) -> CrossDepartmentMessage | None:
        self._trace.emit(
            component="DepartmentMessagingAdapter",
            level=TraceLevel.WARN,
            message=f"Error received from {message.sender}: {message.payload}",
        )
        return None

    async def _process_request(self, message: CrossDepartmentMessage) -> dict:
        return {"status": "processed", "original_payload": message.payload}
