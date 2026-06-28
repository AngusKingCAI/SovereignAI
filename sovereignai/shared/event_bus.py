"""Typed event bus with in-order delivery per channel.

The bus is transparent infrastructure (per Q6 resolution): it routes
events, it does not orchestrate. Subscribers register for a channel;
publishers send events to a channel. The bus guarantees that events on
the same channel arrive at each subscriber in publish order.
"""
from __future__ import annotations

from collections import defaultdict
from collections.abc import Callable
from threading import Lock

from sovereignai.shared.trace_emitter import TraceEmitter

from sovereignai.shared.types import (
    Channel,
    Event,
    TraceLevel,
)

Subscriber = Callable[[Event], None]


class EventBus:
    """Route events from publishers to subscribers, preserving per-channel order.

    Each channel has its own subscriber list and its own ordering guarantee.
    A subscriber registered for channel A will receive channel A's events in
    publish order, but may receive channel B's events in any order relative
    to channel A's.
    """

    def __init__(self, trace: TraceEmitter) -> None:
        """Create an empty event bus with no subscribers yet.

        Args:
            trace: The trace emitter for logging subscriber failures. The
                bus never silently swallows errors (per P10) — if a
                subscriber raises, the bus logs at ERROR and continues.
        """
        self._trace = trace
        self._subscribers: dict[Channel, list[Subscriber]] = defaultdict(list)
        self._lock = Lock()

    def subscribe(self, channel: Channel, subscriber: Subscriber) -> None:
        """Register a subscriber to receive events sent to a specific channel.

        Multiple subscribers may register for the same channel; each
        receives every event published to that channel. Subscribers are
        called in registration order for each event.

        Args:
            channel: The typed channel identifier to listen on.
            subscriber: A callable that accepts an Event. It will be
                called synchronously on the publishing thread.
        """
        with self._lock:
            self._subscribers[channel].append(subscriber)
        self._trace.emit(
            component="EventBus",
            level=TraceLevel.DEBUG,
            message=f"Subscriber registered for channel {channel}",
        )

    def publish(self, event: Event) -> None:
        """Send an event to all subscribers registered on its channel.

        Subscribers are called synchronously in registration order. If a
        subscriber raises an exception, the bus catches it, logs at ERROR
        with full context, and continues to the next subscriber. The bus
        never silently swallows failures (per P10, criterion 28).

        Args:
            event: The event to publish. Must already carry its channel,
                correlation ID, and timestamp.
        """
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
