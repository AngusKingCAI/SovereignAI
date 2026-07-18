from __future__ import annotations

import threading

import pytest
from sovereignai.shared.container import DIContainer


class DummyInterface:

    def __init__(self, value: int=0) -> None:
        self.value = value

class AnotherInterface:

    def __init__(self, value: str='') -> None:
        self.value = value

@pytest.fixture
def container() -> DIContainer:
    return DIContainer()

def test_register_and_retrieve_singleton(container: DIContainer) -> None:
    instance = DummyInterface(value=42)
    container.register_singleton(DummyInterface, instance)
    retrieved = container.retrieve(DummyInterface)
    assert retrieved is instance
    assert retrieved.value == 42

def test_register_and_retrieve_factory(container: DIContainer) -> None:
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
    singleton = DummyInterface(value=100)

    def factory() -> DummyInterface:
        return DummyInterface(value=200)
    container.register_singleton(DummyInterface, singleton)
    container.register_factory(DummyInterface, factory)
    retrieved = container.retrieve(DummyInterface)
    assert retrieved is singleton
    assert retrieved.value == 100

def test_retrieve_unregistered_raises_keyerror(container: DIContainer) -> None:
    with pytest.raises(KeyError, match='No singleton or factory registered'):
        container.retrieve(DummyInterface)

def test_different_types_are_isolated(container: DIContainer) -> None:
    dummy_instance = DummyInterface(value=1)
    another_instance = AnotherInterface(value='test')
    container.register_singleton(DummyInterface, dummy_instance)
    container.register_singleton(AnotherInterface, another_instance)
    retrieved_dummy = container.retrieve(DummyInterface)
    retrieved_another = container.retrieve(AnotherInterface)
    assert retrieved_dummy is dummy_instance
    assert retrieved_another is another_instance

def test_di_container_thread_safety(container: DIContainer) -> None:
    container.register_singleton(DummyInterface, DummyInterface(value=42))
    errors: list[Exception] = []
    lock = threading.Lock()

    def register_and_retrieve() -> None:
        try:
            container.register_factory(AnotherInterface, lambda: AnotherInterface(value='test'))
            container.retrieve(DummyInterface)
            container.retrieve(AnotherInterface)
        except Exception as e:
            with lock:
                errors.append(e)
    threads = [threading.Thread(target=register_and_retrieve) for _ in range(10)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    assert len(errors) == 0, f'Thread-safety test failed with errors: {errors}'
    assert isinstance(container.retrieve(DummyInterface), DummyInterface)
    assert isinstance(container.retrieve(AnotherInterface), AnotherInterface)
