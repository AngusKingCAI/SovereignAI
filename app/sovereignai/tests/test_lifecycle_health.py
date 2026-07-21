from __future__ import annotations

import asyncio
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock

import pytest

from sovereignai.lifecycle.health import HealthAggregator, HealthCheckResult


@pytest.fixture
def mock_trace():
    trace = MagicMock()
    trace.emit = MagicMock()
    return trace


@pytest.fixture
def health_aggregator(mock_trace):
    return HealthAggregator(trace=mock_trace)


@pytest.mark.asyncio
async def test_register_and_deregister(health_aggregator):
    def mock_health_check():
        return {"healthy": True, "details": {"status": "ok"}}
    
    health_aggregator.register("test_component", mock_health_check)
    assert "test_component" in health_aggregator._health_checks
    
    health_aggregator.deregister("test_component")
    assert "test_component" not in health_aggregator._health_checks


@pytest.mark.asyncio
async def test_polling_loop_runs(health_aggregator):
    call_count = 0
    
    def mock_health_check():
        nonlocal call_count
        call_count += 1
        return {"healthy": True, "details": {"status": "ok"}}
    
    health_aggregator.register("test_component", mock_health_check)
    await health_aggregator.start()
    
    await asyncio.sleep(6)  # Wait for at least one poll cycle
    
    await health_aggregator.stop()
    
    assert call_count >= 1


@pytest.mark.asyncio
async def test_polling_error_handling(health_aggregator):
    def failing_health_check():
        raise Exception("Health check failed")
    
    health_aggregator.register("failing_component", failing_health_check)
    await health_aggregator.start()
    
    await asyncio.sleep(6)  # Wait for at least one poll cycle
    
    await health_aggregator.stop()
    
    assert "failing_component" in health_aggregator._cache
    assert not health_aggregator._cache["failing_component"].healthy


@pytest.mark.asyncio
async def test_get_health_status(health_aggregator):
    def mock_health_check():
        return {"healthy": True, "details": {"status": "ok"}}
    
    health_aggregator.register("test_component", mock_health_check)
    await health_aggregator.start()
    
    await asyncio.sleep(1)  # Let polling run once
    
    status = health_aggregator.get_health_status()
    
    assert "status" in status
    assert "components" in status
    assert "cache_age_ms" in status
    assert "test_component" in status["components"]
    
    await health_aggregator.stop()


@pytest.mark.asyncio
async def test_async_health_check_supported(health_aggregator):
    async def async_health_check():
        return {"healthy": True, "details": {"status": "ok"}}
    
    health_aggregator.register("async_component", async_health_check)
    await health_aggregator.start()
    
    await asyncio.sleep(1)
    
    status = health_aggregator.get_health_status()
    assert "async_component" in status["components"]
    
    await health_aggregator.stop()


@pytest.mark.asyncio
async def test_overall_status_calculation(health_aggregator):
    def healthy_check():
        return {"healthy": True, "details": {}}
    
    def unhealthy_check():
        return {"healthy": False, "details": {}}
    
    health_aggregator.register("healthy", healthy_check)
    health_aggregator.register("unhealthy", unhealthy_check)
    await health_aggregator.start()
    
    await asyncio.sleep(1)
    
    status = health_aggregator.get_health_status()
    assert status["status"] == "degraded"
    
    await health_aggregator.stop()


@pytest.mark.asyncio
async def test_start_stop_idempotent(health_aggregator):
    await health_aggregator.start()
    await health_aggregator.start()  # Should not raise
    assert health_aggregator._running
    
    await health_aggregator.stop()
    await health_aggregator.stop()  # Should not raise
    assert not health_aggregator._running


@pytest.mark.asyncio
async def test_cache_age_tracking(health_aggregator):
    def mock_health_check():
        return {"healthy": True, "details": {}}
    
    health_aggregator.register("test", mock_health_check)
    await health_aggregator.start()
    
    await asyncio.sleep(1)
    
    status = health_aggregator.get_health_status()
    assert status["cache_age_ms"] >= 0
    
    await health_aggregator.stop()
