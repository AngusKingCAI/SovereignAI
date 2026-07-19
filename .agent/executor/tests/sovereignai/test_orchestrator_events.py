from __future__ import annotations

import pytest
from sovereignai.orchestrator import Orchestrator
from sovereignai.orchestrator.classifier import RuleBasedClassifier
from sovereignai.shared.container import DIContainer
from sovereignai.shared.event_bus import EventBus
from sovereignai.shared.event_registry import EventRegistry
from sovereignai.shared.trace_emitter import TraceEmitter


@pytest.mark.asyncio
async def test_orchestrator_event_subscription() -> None:
    container = DIContainer()
    trace = TraceEmitter()
    registry = EventRegistry()
    event_bus = EventBus(trace=trace, registry=registry)
    container.register_singleton(TraceEmitter, trace)
    container.register_singleton(EventBus, event_bus)
    container.register_singleton(EventRegistry, registry)

    classifier = RuleBasedClassifier()
    orchestrator = Orchestrator(
        container,
        classifier=classifier,
        db_path=":memory:",
    )

    assert orchestrator._event_bus is not None

    await orchestrator.shutdown()


@pytest.mark.asyncio
async def test_orchestrator_emits_clarification_needed() -> None:
    container = DIContainer()
    trace = TraceEmitter()
    registry = EventRegistry()
    event_bus = EventBus(trace=trace, registry=registry)
    container.register_singleton(TraceEmitter, trace)
    container.register_singleton(EventBus, event_bus)
    container.register_singleton(EventRegistry, registry)

    classifier = RuleBasedClassifier()
    orchestrator = Orchestrator(
        container,
        classifier=classifier,
        db_path=":memory:",
    )

    response = await orchestrator.handle_message("hello world")
    assert "not sure which department" in response.lower()

    await orchestrator.shutdown()


@pytest.mark.asyncio
async def test_orchestrator_emits_response_ready() -> None:
    container = DIContainer()
    trace = TraceEmitter()
    registry = EventRegistry()
    event_bus = EventBus(trace=trace, registry=registry)
    container.register_singleton(TraceEmitter, trace)
    container.register_singleton(EventBus, event_bus)
    container.register_singleton(EventRegistry, registry)

    from sovereignai.managers.coding import CodingManager
    manager = CodingManager(container)
    container.register_singleton(CodingManager, manager)

    classifier = RuleBasedClassifier()
    orchestrator = Orchestrator(
        container,
        classifier=classifier,
        db_path=":memory:",
    )

    response = await orchestrator.handle_message("fix the bug")
    assert response

    await orchestrator.shutdown()
