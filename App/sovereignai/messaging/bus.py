from __future__ import annotations

import asyncio
from collections.abc import Callable
from pathlib import Path
from typing import TYPE_CHECKING

from sovereignai.messaging.schema import CrossDepartmentMessage
from sovereignai.messaging.security import AuditLogger, CircuitBreaker, RateLimiter
from sovereignai.shared.event_bus import EventBus
from sovereignai.shared.event_registry import EventRegistry
from sovereignai.shared.trace_emitter import TraceEmitter
from sovereignai.shared.types import Channel, Event, TraceLevel

if TYPE_CHECKING:
    pass


MessageHandler = Callable[[CrossDepartmentMessage], CrossDepartmentMessage | None]


class InterDepartmentBus:

    def __init__(
        self,
        event_bus: EventBus,
        registry: EventRegistry,
        trace: TraceEmitter,
        allowed_departments: set[str] | None = None,
        audit_db_path: Path | None = None,
    ) -> None:
        self._event_bus = event_bus
        self._registry = registry
        self._trace = trace
        self._handlers: dict[str, list[MessageHandler]] = {}
        self._allowed_departments: set[str] = allowed_departments or {
            "coding",
            "research",
            "education",
            "communication",
            "security",
            "operations",
            "orchestrator",
        }

        if audit_db_path is None:
            audit_db_path = Path("messaging_audit.db")

        self._audit_logger = AuditLogger(audit_db_path, trace)
        self._rate_limiter = RateLimiter(max_messages=100, window_seconds=60, trace=trace)
        self._circuit_breaker = CircuitBreaker(failure_threshold=5, timeout_seconds=30, trace=trace)

        self._trace.emit(
            component="InterDepartmentBus",
            level=TraceLevel.INFO,
            message=f"InterDepartmentBus initialized with whitelist: {self._allowed_departments}",
        )

    def register_handler(
        self, recipient: str, handler: MessageHandler
    ) -> None:
        if recipient not in self._allowed_departments:
            raise ValueError(
                f"Cannot register handler for recipient '{recipient}': not in whitelist"
            )
        if recipient not in self._handlers:
            self._handlers[recipient] = []
        self._handlers[recipient].append(handler)
        self._trace.emit(
            component="InterDepartmentBus",
            level=TraceLevel.DEBUG,
            message=f"Handler registered for recipient {recipient}",
        )

    async def send(self, message: CrossDepartmentMessage) -> CrossDepartmentMessage | None:
        if message.sender not in self._allowed_departments:
            self._trace.emit(
                component="InterDepartmentBus",
                level=TraceLevel.WARN,
                message=f"Message rejected: sender '{message.sender}' not in whitelist",
            )
            self._audit_logger.log_message(message, "rejected", "sender_not_whitelisted")
            return None

        if message.recipient not in self._allowed_departments:
            self._trace.emit(
                component="InterDepartmentBus",
                level=TraceLevel.WARN,
                message=f"Message rejected: recipient '{message.recipient}' not in whitelist",
            )
            self._audit_logger.log_message(message, "rejected", "recipient_not_whitelisted")
            return None

        if not self._rate_limiter.is_allowed(message.sender, message.recipient):
            msg = (
                f"Message rejected: rate limit exceeded for "
                f"{message.sender} -> {message.recipient}"
            )
            self._trace.emit(
                component="InterDepartmentBus",
                level=TraceLevel.WARN,
                message=msg,
            )
            self._audit_logger.log_message(message, "rejected", "rate_limit_exceeded")
            return None

        if self._circuit_breaker.is_open(message.recipient):
            self._trace.emit(
                component="InterDepartmentBus",
                level=TraceLevel.WARN,
                message=f"Message rejected: circuit breaker open for recipient {message.recipient}",
            )
            self._audit_logger.log_message(message, "rejected", "circuit_breaker_open")
            return None

        handlers = self._handlers.get(message.recipient, [])
        if not handlers:
            self._trace.emit(
                component="InterDepartmentBus",
                level=TraceLevel.WARN,
                message=f"No handlers registered for recipient {message.recipient}",
            )
            self._audit_logger.log_message(message, "rejected", "no_handlers")
            return None

        self._audit_logger.log_message(message, "processing")

        response = None
        handler_error = None
        for handler in handlers:
            try:
                response = await self._call_handler(handler, message)
                if response is not None:
                    self._circuit_breaker.record_success(message.recipient)
                    self._audit_logger.log_message(message, "success")
                    break
            except Exception as exc:
                handler_error = exc
                self._trace.emit(
                    component="InterDepartmentBus",
                    level=TraceLevel.ERROR,
                    message=f"Handler raised exception for recipient {message.recipient}: {exc}",
                )

        if handler_error:
            self._circuit_breaker.record_failure(message.recipient)
            self._audit_logger.log_message(message, "error", type(handler_error).__name__)
            if self._circuit_breaker.should_emit_circuit_event(message.recipient):
                event = Event(
                    channel=Channel("messaging.circuit.open"),
                    correlation_id=message.correlation_id,
                    timestamp=message.timestamp,
                    version=1,
                    trace_level=TraceLevel.ERROR,
                )
                await self.publish_event_async(event)

        return response

    async def _call_handler(
        self, handler: MessageHandler, message: CrossDepartmentMessage
    ) -> CrossDepartmentMessage | None:
        if asyncio.iscoroutinefunction(handler):
            return await handler(message)
        else:
            return handler(message)

    def publish_event(self, event: Event) -> None:
        self._event_bus.publish(event)

    async def publish_event_async(self, event: Event) -> None:
        await self._event_bus.publish_async(event)
