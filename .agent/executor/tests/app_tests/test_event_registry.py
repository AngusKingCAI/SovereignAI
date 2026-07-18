from __future__ import annotations

import pytest
from sovereignai.shared.event_registry import EventRegistry


@pytest.fixture
def event_registry() -> EventRegistry:
    return EventRegistry()


def test_register_handler(event_registry: EventRegistry) -> None:
    def handler(event: object) -> None:
        pass

    event_registry.register("test.event", None, handler)
    handlers = event_registry.handlers_for("test.event")
    assert len(handlers) == 1
    assert handlers[0].handler is handler


def test_register_multiple_handlers(event_registry: EventRegistry) -> None:
    def handler1(event: object) -> None:
        pass

    def handler2(event: object) -> None:
        pass

    event_registry.register("test.event", None, handler1)
    event_registry.register("test.event", None, handler2)
    handlers = event_registry.handlers_for("test.event")
    assert len(handlers) == 2


def test_wildcard_handler_matches_all(event_registry: EventRegistry) -> None:
    def wildcard_handler(event: object) -> None:
        pass

    def specific_handler(event: object) -> None:
        pass

    event_registry.register("*", None, wildcard_handler)
    event_registry.register("test.event", None, specific_handler)

    handlers = event_registry.handlers_for("test.event")
    assert len(handlers) == 2

    handlers = event_registry.handlers_for("other.event")
    assert len(handlers) == 1
    assert handlers[0].handler is wildcard_handler


def test_queue_maxsize_default(event_registry: EventRegistry) -> None:
    def handler(event: object) -> None:
        pass

    event_registry.register("test.event", None, handler)
    handlers = event_registry.handlers_for("test.event")
    assert handlers[0].queue_maxsize == 1000


def test_queue_maxsize_custom(event_registry: EventRegistry) -> None:
    def handler(event: object) -> None:
        pass

    event_registry.register("test.event", None, handler, queue_maxsize=500)
    handlers = event_registry.handlers_for("test.event")
    assert handlers[0].queue_maxsize == 500


def test_post_start_register_raises(event_registry: EventRegistry) -> None:
    event_registry.mark_started()

    def handler(event: object) -> None:
        pass

    with pytest.raises(RuntimeError, match="Cannot register handlers after EventBus.start"):
        event_registry.register("test.event", None, handler)


def test_handlers_for_unknown_event_returns_empty(event_registry: EventRegistry) -> None:
    handlers = event_registry.handlers_for("unknown.event")
    assert len(handlers) == 0


def test_signature_validation_with_payload_class(event_registry: EventRegistry) -> None:
    from dataclasses import dataclass

    @dataclass
    class TestPayload:
        value: str

    def handler(event: TestPayload) -> None:
        pass

    event_registry.register("test.event", TestPayload, handler)
    handlers = event_registry.handlers_for("test.event")
    assert handlers[0].payload_class is TestPayload


def test_signature_validation_wildcard_skips_validation(event_registry: EventRegistry) -> None:
    def handler(event: object) -> None:
        pass

    event_registry.register("*", None, handler)
    handlers = event_registry.handlers_for("*")
    assert handlers[0].payload_class is None
