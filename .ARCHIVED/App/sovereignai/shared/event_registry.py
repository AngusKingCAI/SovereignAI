from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass


@dataclass
class HandlerRegistration:
    event_type: str
    payload_class: type | None
    handler: Callable
    queue_maxsize: int = 1000


class EventRegistry:
    def __init__(self) -> None:
        self._handlers: dict[str, list[HandlerRegistration]] = {}
        self._started = False

    def register(
        self,
        event_type: str,
        payload_class: type | None,
        handler: Callable,
        queue_maxsize: int = 1000,
    ) -> None:
        if self._started:
            raise RuntimeError("Cannot register handlers after EventBus.start()")
        if event_type not in self._handlers:
            self._handlers[event_type] = []
        self._handlers[event_type].append(
            HandlerRegistration(
                event_type=event_type,
                payload_class=payload_class,
                handler=handler,
                queue_maxsize=queue_maxsize,
            )
        )

    def handlers_for(self, event_type: str) -> list[HandlerRegistration]:
        handlers = []
        if event_type in self._handlers:
            handlers.extend(self._handlers[event_type])
        if "*" in self._handlers:
            handlers.extend(self._handlers["*"])
        return handlers

    def mark_started(self) -> None:
        self._started = True
