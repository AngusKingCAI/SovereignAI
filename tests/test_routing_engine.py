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
    return TraceEmitter()

@pytest.fixture
def lifecycle(trace: TraceEmitter) -> LifecycleManager:
    return LifecycleManager(trace=trace)

@pytest.fixture
def capability_index() -> ICapabilityIndex:
    index = Mock(spec=ICapabilityIndex)
    return index

@pytest.fixture
def router(capability_index: ICapabilityIndex, lifecycle: LifecycleManager) -> RoutingEngine:
    return RoutingEngine(capability_index=capability_index, lifecycle_manager=lifecycle)

@pytest.fixture
def provider_a() -> tuple[ComponentId, CapabilityDeclaration]:
    return (ComponentId('component_a'), CapabilityDeclaration(category=CapabilityCategory.TOOL, name='test', version='1.0.0', priority=5))

@pytest.fixture
def provider_b() -> tuple[ComponentId, CapabilityDeclaration]:
    return (ComponentId('component_b'), CapabilityDeclaration(category=CapabilityCategory.TOOL, name='test', version='1.0.0', priority=10))

def test_route_returns_highest_priority_active(router: RoutingEngine, capability_index: ICapabilityIndex, lifecycle: LifecycleManager, provider_a: tuple[ComponentId, CapabilityDeclaration], provider_b: tuple[ComponentId, CapabilityDeclaration]) -> None:
    component_a, _ = provider_a
    component_b, _ = provider_b
    lifecycle.register(component_a)
    lifecycle.register(component_b)
    capability_index.find_providers.return_value = [provider_b, provider_a]
    result = router.route(CapabilityCategory.TOOL, 'test')
    assert result == component_b

def test_route_skips_circuit_broken(router: RoutingEngine, capability_index: ICapabilityIndex, lifecycle: LifecycleManager, provider_a: tuple[ComponentId, CapabilityDeclaration], provider_b: tuple[ComponentId, CapabilityDeclaration]) -> None:
    component_a, _ = provider_a
    component_b, _ = provider_b
    lifecycle.register(component_a)
    lifecycle.register(component_b)
    for _ in range(51):
        lifecycle.record_error(component_a)
    capability_index.find_providers.return_value = [provider_a, provider_b]
    result = router.route(CapabilityCategory.TOOL, 'test')
    assert result == component_b

def test_route_recovers_circuit_broken_when_window_expired(router: RoutingEngine, capability_index: ICapabilityIndex, lifecycle: LifecycleManager, provider_a: tuple[ComponentId, CapabilityDeclaration], provider_b: tuple[ComponentId, CapabilityDeclaration]) -> None:
    component_a, _ = provider_a
    component_b, _ = provider_b
    lifecycle.register(component_a)
    lifecycle.register(component_b)
    for _ in range(51):
        lifecycle.record_error(component_a)
    capability_index.find_providers.return_value = [provider_a, provider_b]
    from time import monotonic
    from unittest.mock import patch
    with patch('sovereignai.shared.lifecycle_manager.monotonic') as mock_monotonic:
        mock_monotonic.return_value = monotonic() + 11.0
        lifecycle.try_recover(component_a)
    result = router.route(CapabilityCategory.TOOL, 'test')
    assert result == component_a

def test_route_raises_when_no_active_provider(router: RoutingEngine, capability_index: ICapabilityIndex, lifecycle: LifecycleManager, provider_a: tuple[ComponentId, CapabilityDeclaration], provider_b: tuple[ComponentId, CapabilityDeclaration]) -> None:
    component_a, _ = provider_a
    component_b, _ = provider_b
    lifecycle.register(component_a)
    lifecycle.register(component_b)
    for _ in range(51):
        lifecycle.record_error(component_a)
        lifecycle.record_error(component_b)
    capability_index.find_providers.return_value = [provider_a, provider_b]
    with pytest.raises(NoActiveProviderError):
        router.route(CapabilityCategory.TOOL, 'test')

def test_route_raises_when_no_providers_at_all(router: RoutingEngine, capability_index: ICapabilityIndex) -> None:
    capability_index.find_providers.return_value = []
    with pytest.raises(NoActiveProviderError):
        router.route(CapabilityCategory.TOOL, 'test')
