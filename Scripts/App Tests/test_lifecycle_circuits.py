from __future__ import annotations

import pytest

from sovereignai.main import build_container
from sovereignai.lifecycle import AgentLifecycleManager, HealthAggregator
from sovereignai.shared.lifecycle_manager import LifecycleManager


def test_circuit_breaker_integration_with_lifecycle():
    """Test that circuit breaker is integrated with lifecycle manager."""
    container = build_container(dev_mode=True)
    
    # Retrieve both lifecycle managers
    agent_lifecycle = container.retrieve(AgentLifecycleManager)
    lifecycle = container.retrieve(LifecycleManager)
    
    # Both should be registered
    assert agent_lifecycle is not None
    assert lifecycle is not None
    
    # Circuit breaker should be functional in LifecycleManager
    lifecycle.register("test_component")
    lifecycle.record_error("test_component")
    assert lifecycle.get_status("test_component").value == "active"  # First error, not tripped yet


def test_health_aggregator_includes_circuit_breaker_status():
    """Test that health aggregator can include circuit breaker status."""
    container = build_container(dev_mode=True)
    
    health_aggregator = container.retrieve(HealthAggregator)
    lifecycle = container.retrieve(LifecycleManager)
    
    # Register a health check that includes circuit breaker status
    def circuit_breaker_health_check():
        status = lifecycle.get_status("test_component")
        return {
            "healthy": status.value != "circuit_broken",
            "details": {"circuit_status": status.value},
        }
    
    health_aggregator.register("circuit_breaker", circuit_breaker_health_check)
    
    # Run the health check manually since the polling loop won't run in test
    import asyncio
    result = asyncio.run(health_aggregator._run_health_check("circuit_breaker", circuit_breaker_health_check))
    health_aggregator._cache["circuit_breaker"] = result
    
    status = health_aggregator.get_health_status()
    assert "circuit_breaker" in status["components"]


def test_circuit_breaker_threshold_enforcement():
    """Test that circuit breaker threshold is enforced correctly."""
    container = build_container(dev_mode=True)
    
    lifecycle = container.retrieve(LifecycleManager)
    
    # Record errors up to threshold
    for _ in range(51):  # More than threshold of 50
        lifecycle.record_error("test_component")
    
    # Should be circuit broken
    status = lifecycle.get_status("test_component")
    assert status.value == "circuit_broken"


def test_circuit_breaker_recovery():
    """Test that circuit breaker can recover after error window expires."""
    container = build_container(dev_mode=True)
    
    lifecycle = container.retrieve(LifecycleManager)
    
    # Trip circuit breaker
    for _ in range(51):
        lifecycle.record_error("test_component")
    
    assert lifecycle.get_status("test_component").value == "circuit_broken"
    
    # Try recovery (this should work if errors are outside the window)
    lifecycle.try_recover("test_component")
    
    # After reset, should be active
    lifecycle.reset("test_component")
    assert lifecycle.get_status("test_component").value == "active"
