from __future__ import annotations

from collections.abc import Callable
from threading import Lock
from typing import Any, TypeVar, cast

T = TypeVar("T")


class DIContainer:

    def __init__(self, event_bus: Any = None, trace: Any = None) -> None:
        self._instances: dict[type[Any], Any] = {}
        self._factories: dict[type[Any], Callable[[], Any]] = {}
        self._lock = Lock()
        self._event_bus = event_bus
        self._trace = trace

    def register_singleton(self, interface: type[T], instance: T) -> None:
        with self._lock:
            self._instances[interface] = instance

    def register_factory(
        self, interface: type[T], factory: Callable[[], T]
    ) -> None:
        with self._lock:
            self._factories[interface] = factory

    def retrieve(self, interface: type[T]) -> T:
        with self._lock:
            if interface in self._instances:
                return cast(T, self._instances[interface])
            if interface in self._factories:
                factory = self._factories[interface]
            else:
                raise KeyError(f"No singleton or factory registered for {interface!r}")
        # Call factory outside the lock so slow factories do not block
        # other retrieve() or register() calls.
        return cast(T, factory())

    def remove(self, component_type: type) -> None:
        with self._lock:
            instance = self._instances.pop(component_type, None)

        if instance is not None and self._event_bus is not None:
            component_id = getattr(instance, "component_id", None) or getattr(
                instance, "_component_id", None
            )
            subscriber_id = component_id if component_id else id(instance)
            self._event_bus.unsubscribe_all(subscriber_id=subscriber_id)
            if self._trace is not None:
                from sovereignai.shared.types import TraceLevel

                self._trace.emit(
                    component="container",
                    level=TraceLevel.WARN,
                    message=(
                        f"Removed {component_type} from container "
                        "and unsubscribed all its event handlers"
                    ),
                )
