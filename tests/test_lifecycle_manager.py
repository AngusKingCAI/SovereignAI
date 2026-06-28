"""Tests for the lifecycle manager."""
from time import monotonic
from unittest.mock import patch

import pytest

from sovereignai.shared.lifecycle_manager import LifecycleManager
from sovereignai.shared.trace_emitter import TraceEmitter
from sovereignai.shared.types import ComponentId, ComponentStatus


@pytest.fixture
def trace() -> TraceEmitter:
    """Create a trace emitter for testing."""
    return TraceEmitter()


@pytest.fixture
def lifecycle(trace: TraceEmitter) -> LifecycleManager:
    """Create a lifecycle manager for testing."""
    return LifecycleManager(trace=trace)


def test_register_sets_active(lifecycle: LifecycleManager) -> None:
    """Verify that registering a component sets its status to ACTIVE."""
    component_id = ComponentId("test_component")
    lifecycle.register(component_id)
    assert lifecycle.get_status(component_id) == ComponentStatus.ACTIVE


def test_unregistered_returns_stopped(lifecycle: LifecycleManager) -> None:
    """Verify that querying an unregistered component returns STOPPED."""
    component_id = ComponentId("unknown_component")
    assert lifecycle.get_status(component_id) == ComponentStatus.STOPPED


def test_record_error_below_threshold_stays_active(lifecycle: LifecycleManager) -> None:
    """Verify that recording 49 errors keeps the component ACTIVE."""
    component_id = ComponentId("test_component")
    lifecycle.register(component_id)
    for _ in range(49):
        lifecycle.record_error(component_id)
    assert lifecycle.get_status(component_id) == ComponentStatus.ACTIVE


def test_record_error_at_threshold_circuit_breaks(lifecycle: LifecycleManager) -> None:
    """Verify that recording 51 errors within 10 seconds trips the circuit breaker."""
    component_id = ComponentId("test_component")
    lifecycle.register(component_id)
    for _ in range(51):
        lifecycle.record_error(component_id)
    assert lifecycle.get_status(component_id) == ComponentStatus.CIRCUIT_BROKEN


def test_try_recover_after_window_expires_returns_true(lifecycle: LifecycleManager) -> None:
    """Verify that try_recover returns True when the error window expires."""
    component_id = ComponentId("test_component")
    lifecycle.register(component_id)
    for _ in range(51):
        lifecycle.record_error(component_id)
    assert lifecycle.get_status(component_id) == ComponentStatus.CIRCUIT_BROKEN

    with patch("sovereignai.shared.lifecycle_manager.monotonic") as mock_monotonic:
        mock_monotonic.return_value = monotonic() + 11.0
        status = lifecycle.try_recover(component_id)
        assert status == ComponentStatus.ACTIVE


def test_circuit_broken_is_not_available() -> None:
    """Verify that CIRCUIT_BROKEN status is not available."""
    assert not ComponentStatus.CIRCUIT_BROKEN.is_available()


def test_active_is_available() -> None:
    """Verify that ACTIVE status is available."""
    assert ComponentStatus.ACTIVE.is_available()
