"""Tests for the routing engine."""
from unittest.mock import Mock

import pytest

from sovereignai.shared.capability_graph import ICapabilityIndex
from sovereignai.shared.lifecycle_manager import LifecycleManager
from sovereignai.shared.routing_engine import RoutingEngine
from sovereignai.shared.trace_emitter import TraceEmitter
from sovereignai.shared.types import (
    CapabilityCategory,
    CapabilityDeclaration,
    ComponentId,
    NoActiveProviderError,
)


@pytest.fixture
def trace() -> TraceEmitter:
    """Create a trace emitter for testing."""
    return TraceEmitter()


@pytest.fixture
def lifecycle(trace: TraceEmitter) -> LifecycleManager:
    """Create a lifecycle manager for testing."""
    return LifecycleManager(trace=trace)


@pytest.fixture
def capability_index() -> ICapabilityIndex:
    """Create a mock capability index for testing."""
    index = Mock(spec=ICapabilityIndex)
    return index


@pytest.fixture
def router(capability_index: ICapabilityIndex, lifecycle: LifecycleManager) -> RoutingEngine:
    """Create a routing engine for testing."""
    return RoutingEngine(capability_index=capability_index, lifecycle_manager=lifecycle)


@pytest.fixture
def provider_a() -> tuple[ComponentId, CapabilityDeclaration]:
    """Create a provider with priority 5."""
    return (
        ComponentId("component_a"),
        CapabilityDeclaration(
            category=CapabilityCategory.TOOL,
            name="test",
            version="1.0.0",
            priority=5,
        ),
    )


@pytest.fixture
def provider_b() -> tuple[ComponentId, CapabilityDeclaration]:
    """Create a provider with priority 10."""
    return (
        ComponentId("component_b"),
        CapabilityDeclaration(
            category=CapabilityCategory.TOOL,
            name="test",
            version="1.0.0",
            priority=10,
        ),
    )


def test_route_returns_highest_priority_active(
    router: RoutingEngine,
    capability_index: ICapabilityIndex,
    lifecycle: LifecycleManager,
    provider_a: tuple[ComponentId, CapabilityDeclaration],
    provider_b: tuple[ComponentId, CapabilityDeclaration],
) -> None:
    """Verify that routing returns the highest-priority active provider."""
    component_a, _ = provider_a
    component_b, _ = provider_b
    lifecycle.register(component_a)
    lifecycle.register(component_b)

    capability_index.find_providers.return_value = [provider_b, provider_a]  # type: ignore[attr-defined]

    result = router.route(CapabilityCategory.TOOL, "test")
    assert result == component_b


def test_route_skips_circuit_broken(
    router: RoutingEngine,
    capability_index: ICapabilityIndex,
    lifecycle: LifecycleManager,
    provider_a: tuple[ComponentId, CapabilityDeclaration],
    provider_b: tuple[ComponentId, CapabilityDeclaration],
) -> None:
    """Verify that routing skips circuit-broken components."""
    component_a, _ = provider_a
    component_b, _ = provider_b
    lifecycle.register(component_a)
    lifecycle.register(component_b)

    # Circuit-break component_a
    for _ in range(51):
        lifecycle.record_error(component_a)

    capability_index.find_providers.return_value = [provider_a, provider_b]  # type: ignore[attr-defined]

    result = router.route(CapabilityCategory.TOOL, "test")
    assert result == component_b


def test_route_recovers_circuit_broken_when_window_expired(
    router: RoutingEngine,
    capability_index: ICapabilityIndex,
    lifecycle: LifecycleManager,
    provider_a: tuple[ComponentId, CapabilityDeclaration],
    provider_b: tuple[ComponentId, CapabilityDeclaration],
) -> None:
    """Verify that routing recovers a circuit-broken component when the error window expires."""
    component_a, _ = provider_a
    component_b, _ = provider_b
    lifecycle.register(component_a)
    lifecycle.register(component_b)

    # Circuit-break component_a
    for _ in range(51):
        lifecycle.record_error(component_a)

    capability_index.find_providers.return_value = [provider_a, provider_b]  # type: ignore[attr-defined]

    # Force recovery by calling try_recover (simulating window expiry)
    from time import monotonic
    from unittest.mock import patch
    with patch("sovereignai.shared.lifecycle_manager.monotonic") as mock_monotonic:
        mock_monotonic.return_value = monotonic() + 11.0
        lifecycle.try_recover(component_a)

    result = router.route(CapabilityCategory.TOOL, "test")
    assert result == component_a


def test_route_raises_when_no_active_provider(
    router: RoutingEngine,
    capability_index: ICapabilityIndex,
    lifecycle: LifecycleManager,
    provider_a: tuple[ComponentId, CapabilityDeclaration],
    provider_b: tuple[ComponentId, CapabilityDeclaration],
) -> None:
    """Verify that routing raises NoActiveProviderError when all providers are circuit-broken."""
    component_a, _ = provider_a
    component_b, _ = provider_b
    lifecycle.register(component_a)
    lifecycle.register(component_b)

    # Circuit-break both components
    for _ in range(51):
        lifecycle.record_error(component_a)
        lifecycle.record_error(component_b)

    capability_index.find_providers.return_value = [provider_a, provider_b]  # type: ignore[attr-defined]

    with pytest.raises(NoActiveProviderError):
        router.route(CapabilityCategory.TOOL, "test")


def test_route_raises_when_no_providers_at_all(
    router: RoutingEngine,
    capability_index: ICapabilityIndex,
) -> None:
    """Verify that routing raises NoActiveProviderError when no providers are registered."""
    capability_index.find_providers.return_value = []  # type: ignore[attr-defined]

    with pytest.raises(NoActiveProviderError):
        router.route(CapabilityCategory.TOOL, "test")
