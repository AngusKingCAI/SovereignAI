from time import monotonic
from unittest.mock import patch

import pytest

from sovereignai.shared.lifecycle_manager import LifecycleManager
from sovereignai.shared.trace_emitter import TraceEmitter
from sovereignai.shared.types import ComponentId, ComponentStatus


@pytest.fixture
def trace() -> TraceEmitter:
    return TraceEmitter()

@pytest.fixture
def lifecycle(trace: TraceEmitter) -> LifecycleManager:
    return LifecycleManager(trace=trace)

def test_register_sets_active(lifecycle: LifecycleManager) -> None:
    component_id = ComponentId('test_component')
    lifecycle.register(component_id)
    assert lifecycle.get_status(component_id) == ComponentStatus.ACTIVE

def test_unregistered_returns_stopped(lifecycle: LifecycleManager) -> None:
    component_id = ComponentId('unknown_component')
    assert lifecycle.get_status(component_id) == ComponentStatus.STOPPED

def test_record_error_below_threshold_stays_active(lifecycle: LifecycleManager) -> None:
    component_id = ComponentId('test_component')
    lifecycle.register(component_id)
    for _ in range(49):
        lifecycle.record_error(component_id)
    assert lifecycle.get_status(component_id) == ComponentStatus.ACTIVE

def test_record_error_at_threshold_circuit_breaks(lifecycle: LifecycleManager) -> None:
    component_id = ComponentId('test_component')
    lifecycle.register(component_id)
    for _ in range(51):
        lifecycle.record_error(component_id)
    assert lifecycle.get_status(component_id) == ComponentStatus.CIRCUIT_BROKEN

def test_try_recover_after_window_expires_returns_true(lifecycle: LifecycleManager) -> None:
    component_id = ComponentId('test_component')
    lifecycle.register(component_id)
    for _ in range(51):
        lifecycle.record_error(component_id)
    assert lifecycle.get_status(component_id) == ComponentStatus.CIRCUIT_BROKEN
    with patch('sovereignai.shared.lifecycle_manager.monotonic') as mock_monotonic:
        mock_monotonic.return_value = monotonic() + 11.0
        status = lifecycle.try_recover(component_id)
        assert status == ComponentStatus.ACTIVE

def test_circuit_broken_is_not_available() -> None:
    assert not ComponentStatus.CIRCUIT_BROKEN.is_available()

def test_active_is_available() -> None:
    assert ComponentStatus.ACTIVE.is_available()
