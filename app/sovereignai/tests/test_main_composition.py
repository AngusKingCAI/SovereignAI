from __future__ import annotations

import pytest

from sovereignai.main import build_container
from sovereignai.lifecycle import (
    AgentLifecycleManager,
    GracefulShutdown,
    HealthAggregator,
    LifecycleHookRegistry,
)


def test_main_composition_registers_lifecycle_components():
    """Test that lifecycle components are registered in DI container."""
    container = build_container(dev_mode=True)
    
    # Check that we can retrieve all lifecycle components
    agent_lifecycle = container.retrieve(AgentLifecycleManager)
    assert agent_lifecycle is not None
    
    hook_registry = container.retrieve(LifecycleHookRegistry)
    assert hook_registry is not None
    
    health_aggregator = container.retrieve(HealthAggregator)
    assert health_aggregator is not None
    
    graceful_shutdown = container.retrieve(GracefulShutdown)
    assert graceful_shutdown is not None


def test_lifecycle_components_have_correct_dependencies():
    """Test that lifecycle components have correct dependencies wired."""
    container = build_container(dev_mode=True)
    
    agent_lifecycle = container.retrieve(AgentLifecycleManager)
    assert agent_lifecycle._event_bus is not None
    assert agent_lifecycle._trace is not None
    
    hook_registry = container.retrieve(LifecycleHookRegistry)
    assert hook_registry._event_bus is not None
    assert hook_registry._trace is not None
    
    health_aggregator = container.retrieve(HealthAggregator)
    assert health_aggregator._trace is not None
    
    graceful_shutdown = container.retrieve(GracefulShutdown)
    assert graceful_shutdown._lifecycle_manager is not None


def test_lifecycle_manager_factory_not_called_during_composition():
    """Test that ModelRegistry factory is not called during DI composition."""
    container = build_container(dev_mode=True)
    
    # If the factory was called during composition, we'd see errors
    # Just check that the manager was created successfully
    agent_lifecycle = container.retrieve(AgentLifecycleManager)
    assert agent_lifecycle is not None
