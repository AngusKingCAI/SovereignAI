from __future__ import annotations

from collections import defaultdict
from collections.abc import Callable
from threading import Lock

from app.sovereignai.shared.trace_emitter import TraceEmitter
from app.sovereignai.shared.types import Channel, Event, TraceLevel

Subscriber = Callable[[Event], None]


class EventBus:

    def __init__(self, trace: TraceEmitter) -> None:
        self._trace = trace
        self._subscribers: dict[Channel, list[Subscriber]] = defaultdict(list)
        self._lock = Lock()

    def subscribe(self, channel: Channel, subscriber: Subscriber) -> None:
        with self._lock:
            self._subscribers[channel].append(subscriber)
        self._trace.emit(
            component="EventBus",
            level=TraceLevel.DEBUG,
            message=f"Subscriber registered for channel {channel}",
        )

    def publish(self, event: Event) -> None:
        with self._lock:
            subscribers = list(self._subscribers.get(event.channel, []))
        for subscriber in subscribers:
            try:
                subscriber(event)
            except Exception as exc:
                self._trace.emit(
                    component="EventBus",
                    level=TraceLevel.ERROR,
                    message=(
                        f"Subscriber {subscriber!r} raised {type(exc).__name__} "
                        f"on channel {event.channel}: {exc}"
                    ),
                )
