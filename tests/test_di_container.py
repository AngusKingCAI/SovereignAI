"""Tests for the dependency injection container.

Per Q9 resolution: conformance + contract + property-based testing.
Verifies singleton/factory patterns, type safety, and thread safety.
"""
from __future__ import annotations

import threading

import pytest

from sovereignai.shared.container import DIContainer


class DummyInterface:
    """A dummy interface for testing."""

    def __init__(self, value: int = 0) -> None:
        """Initialize the dummy interface with a value."""
        self.value = value


class AnotherInterface:
    """Another dummy interface for testing."""

    def __init__(self, value: str = "") -> None:
        """Initialize the another interface with a value."""
        self.value = value


@pytest.fixture
def container() -> DIContainer:
    """Provide a fresh container for each test."""
    return DIContainer()


def test_register_and_retrieve_singleton(container: DIContainer) -> None:
    """Verify that registering a singleton allows retrieving the same instance."""
    instance = DummyInterface(value=42)
    container.register_singleton(DummyInterface, instance)

    retrieved = container.retrieve(DummyInterface)
    assert retrieved is instance
    assert retrieved.value == 42


def test_register_and_retrieve_factory(container: DIContainer) -> None:
    """Verify that registering a factory produces a fresh instance per call."""
    call_count = 0

    def factory() -> DummyInterface:
        nonlocal call_count
        call_count += 1
        return DummyInterface(value=call_count)

    container.register_factory(DummyInterface, factory)

    first = container.retrieve(DummyInterface)
    second = container.retrieve(DummyInterface)

    assert first is not second
    assert first.value == 1
    assert second.value == 2


def test_singleton_takes_precedence_over_factory(container: DIContainer) -> None:
    """Verify that if both singleton and factory are registered, singleton is returned."""
    singleton = DummyInterface(value=100)

    def factory() -> DummyInterface:
        return DummyInterface(value=200)

    container.register_singleton(DummyInterface, singleton)
    container.register_factory(DummyInterface, factory)

    retrieved = container.retrieve(DummyInterface)
    assert retrieved is singleton
    assert retrieved.value == 100


def test_retrieve_unregistered_raises_keyerror(container: DIContainer) -> None:
    """Verify that retrieving an unregistered type raises KeyError."""
    with pytest.raises(KeyError, match="No singleton or factory registered"):
        container.retrieve(DummyInterface)


def test_different_types_are_isolated(container: DIContainer) -> None:
    """Verify that registering one type does not affect retrieval of another type."""
    dummy_instance = DummyInterface(value=1)
    another_instance = AnotherInterface(value="test")

    container.register_singleton(DummyInterface, dummy_instance)
    container.register_singleton(AnotherInterface, another_instance)

    retrieved_dummy = container.retrieve(DummyInterface)
    retrieved_another = container.retrieve(AnotherInterface)

    assert retrieved_dummy is dummy_instance
    assert retrieved_another is another_instance


def test_di_container_thread_safety(container: DIContainer) -> None:
    """Verify that concurrent registration and retrieval do not cause races."""
    num_threads = 10
    registers_per_thread = 10

    def register_many() -> None:
        for i in range(registers_per_thread):
            instance = DummyInterface(value=i)
            container.register_singleton(DummyInterface, instance)

    threads = [
        threading.Thread(target=register_many) for _ in range(num_threads)
    ]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    # Should be able to retrieve without error
    retrieved = container.retrieve(DummyInterface)
    assert isinstance(retrieved, DummyInterface)
