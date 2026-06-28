"""Passive typed dependency injection container.

This module defines the container itself — a typed registry that holds
component instances and factories. The container does NOT auto-wire or
resolve dependencies. main.py (the Composition Root) explicitly
instantiates every component and registers it here.

Per A8: no @inject decorators, no auto-discovery, no runtime magic. The
container is a passive registry — put things in, take things out, by
type.

Per AR4: singletons (Orchestrator, Librarian Registry) are registered
as instances. Factories (Managers, Workers) are registered as callables
that produce a new instance per call.
"""
from __future__ import annotations

from collections.abc import Callable
from threading import Lock
from typing import Any, TypeVar, cast

T = TypeVar("T")


class DIContainer:
    """Typed registry for component instances and factories.

    The container is passive — it does not resolve dependencies or
    construct objects. Callers register instances or factories by type;
    callers retrieve them by type. The container enforces type safety
    at retrieval: requesting a type that wasn't registered raises.

    Thread-safe: registration and retrieval may happen concurrently
    from different components.
    """

    def __init__(self) -> None:
        """Create an empty container with no registered components."""
        self._instances: dict[type[Any], Any] = {}
        self._factories: dict[type[Any], Callable[[], Any]] = {}
        self._lock = Lock()

    def register_singleton(self, interface: type[T], instance: T) -> None:
        """Register a single instance that all callers will share in the container registry.

        Use for long-lived components like the EventBus or TraceEmitter.
        Retrieving the same interface always returns the same instance.

        Args:
            interface: The type key callers will use to retrieve.
            instance: The singleton instance to store.
        """
        with self._lock:
            self._instances[interface] = instance

    def register_factory(
        self, interface: type[T], factory: Callable[[], T]
    ) -> None:
        """Register a factory that produces a fresh instance per call in the container registry.

        Use for short-lived components like per-task Workers. Each
        retrieve() call invokes the factory and returns a new instance.

        Args:
            interface: The type key callers will use to retrieve.
            factory: A callable that takes no args and returns a new
                instance of the interface type.
        """
        with self._lock:
            self._factories[interface] = factory

    def retrieve(self, interface: type[T]) -> T:
        """Get a registered instance or invoke the registered factory from the container registry.

        Singletons take precedence: if both a singleton and a factory
        are registered for the same type, the singleton is returned.

        Args:
            interface: The type key previously registered.

        Returns:
            The singleton instance, or a fresh factory-produced instance.

        Raises:
            KeyError: If no singleton or factory is registered for the
                given interface.
        """
        with self._lock:
            if interface in self._instances:
                return cast(T, self._instances[interface])
            if interface in self._factories:
                return cast(T, self._factories[interface]())
        raise KeyError(f"No singleton or factory registered for {interface!r}")
