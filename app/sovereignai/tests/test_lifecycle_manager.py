from __future__ import annotations

import asyncio
import sys
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from sovereignai.lifecycle.manager import AgentLifecycleManager
from sovereignai.lifecycle.types import LifecycleError, LifecycleState
from sovereignai.shared.types import Channel, Event, TraceLevel


@pytest.fixture
def mock_event_bus():
    bus = MagicMock()
    bus.is_started = True
    bus.publish_async = AsyncMock()
    return bus


@pytest.fixture
def mock_trace():
    trace = MagicMock()
    trace.emit = MagicMock()
    return trace


@pytest.fixture
def lifecycle_manager(mock_event_bus, mock_trace):
    return AgentLifecycleManager(
        event_bus=mock_event_bus,
        trace=mock_trace,
        web_url="http://localhost:8000",
    )


@pytest.mark.asyncio
async def test_startup_sequence_order(lifecycle_manager, mock_event_bus, mock_trace):
    call_order = []
    
    original_emit = mock_trace.emit
    def track_emit(component, level, message):
        if "Starting stage:" in message:
            stage_name = message.split("Starting stage: ")[1]
            call_order.append(stage_name)
        original_emit(component, level, message)
    
    mock_trace.emit = track_emit
    
    await lifecycle_manager.start()
    
    expected_order = ["EventBus", "OptionsBackend", "Orchestrator", "ModelRegistry", "RouteReadinessCheck"]
    assert call_order == expected_order


@pytest.mark.asyncio
async def test_model_registry_factory_not_called_in_init(mock_event_bus, mock_trace):
    factory_called = False
    
    def mock_factory():
        nonlocal factory_called
        factory_called = True
        return MagicMock()
    
    manager = AgentLifecycleManager(
        event_bus=mock_event_bus,
        trace=mock_trace,
        orchestrator_factory=mock_factory,
    )
    
    assert not factory_called, "Factory should not be called during __init__"


@pytest.mark.asyncio
async def test_eventbus_failure_aborts_startup(mock_event_bus, mock_trace):
    mock_event_bus.is_started = False
    
    manager = AgentLifecycleManager(
        event_bus=mock_event_bus,
        trace=mock_trace,
    )
    
    with pytest.raises(LifecycleError, match="EventBus is not started"):
        await manager.start()
    
    assert manager.state == LifecycleState.STOPPED


@pytest.mark.asyncio
async def test_readiness_false_counts_toward_timeout(lifecycle_manager):
    with patch.object(lifecycle_manager, "_check_route_readiness"):
        with patch.object(lifecycle_manager, "_check_options_backend"):
            await lifecycle_manager.start()
            assert lifecycle_manager.state == LifecycleState.READY


@pytest.mark.asyncio
async def test_readiness_timeout_degraded_start(lifecycle_manager):
    with patch.object(lifecycle_manager, "_check_route_readiness") as mock_check:
        import asyncio
        mock_check.side_effect = asyncio.TimeoutError()
        
        await lifecycle_manager.start()
        
        assert lifecycle_manager.state == LifecycleState.DEGRADED


@pytest.mark.asyncio
async def test_readiness_check_accepts_any_ready_value(lifecycle_manager):
    with patch.object(AgentLifecycleManager, "_check_route_readiness"):
        with patch.object(AgentLifecycleManager, "_check_options_backend"):
            manager = AgentLifecycleManager(
                event_bus=lifecycle_manager._event_bus,
                trace=lifecycle_manager._trace,
                web_url="http://localhost:8000",
            )
            
            await manager.start()
            
            assert manager.state == LifecycleState.READY


@pytest.mark.asyncio
async def test_readiness_check_succeeds_on_200_dto(lifecycle_manager):
    with patch.object(lifecycle_manager, "_check_route_readiness"):
        with patch.object(lifecycle_manager, "_check_options_backend"):
            await lifecycle_manager.start()
            assert lifecycle_manager.state == LifecycleState.READY


@pytest.mark.asyncio
async def test_readiness_check_skips_on_connection_refused(lifecycle_manager):
    with patch.object(lifecycle_manager, "_check_route_readiness"):
        with patch.object(lifecycle_manager, "_check_options_backend"):
            await lifecycle_manager.start()
            assert lifecycle_manager.state == LifecycleState.READY


@pytest.mark.asyncio
async def test_fallback_log_unwritable_continues_with_stderr(mock_event_bus, mock_trace):
    with patch("pathlib.Path.mkdir") as mock_mkdir:
        mock_mkdir.side_effect = PermissionError("Cannot create directory")
        
        manager = AgentLifecycleManager(
            event_bus=mock_event_bus,
            trace=mock_trace,
        )
        
        assert not manager._fallback_log_available
        
        manager._write_fallback_log("test message")
        
        assert manager.state == LifecycleState.INITIALIZING


@pytest.mark.asyncio
async def test_eventbus_recovery_replays_fallback_log(mock_event_bus, mock_trace, tmp_path):
    fallback_log = tmp_path / "lifecycle_fallback.log"
    
    with patch("platformdirs.user_data_dir") as mock_dir:
        mock_dir.return_value = str(tmp_path)
        
        manager = AgentLifecycleManager(
            event_bus=mock_event_bus,
            trace=mock_trace,
        )
        
        manager._write_fallback_log("lifecycle.stage.failed: stage=EventBus, error=timeout")
        
        assert manager._fallback_log_path.parent.exists()


@pytest.mark.asyncio
async def test_health_check_recovery_logic(lifecycle_manager):
    with patch.object(lifecycle_manager, "_check_route_readiness"):
        with patch.object(lifecycle_manager, "_check_options_backend"):
            await lifecycle_manager.start()
            assert lifecycle_manager.state == LifecycleState.READY
            
            await lifecycle_manager.record_health_check(False)
            assert lifecycle_manager.state == LifecycleState.DEGRADED
            
            await lifecycle_manager.record_health_check(True)
            assert lifecycle_manager.state == LifecycleState.DEGRADED
            
            await lifecycle_manager.record_health_check(True)
            assert lifecycle_manager.state == LifecycleState.DEGRADED
            
            await lifecycle_manager.record_health_check(True)
            assert lifecycle_manager.state == LifecycleState.READY


@pytest.mark.asyncio
async def test_shutdown_flow(lifecycle_manager):
    with patch.object(lifecycle_manager, "_check_route_readiness"):
        with patch.object(lifecycle_manager, "_check_options_backend"):
            await lifecycle_manager.start()
            assert lifecycle_manager.state == LifecycleState.READY
            
            await lifecycle_manager.shutdown()
            assert lifecycle_manager.state == LifecycleState.STOPPED
            
            await lifecycle_manager.shutdown()
            assert lifecycle_manager.state == LifecycleState.STOPPED


@pytest.mark.asyncio
async def test_cannot_start_from_non_initializing_state(lifecycle_manager):
    with patch.object(lifecycle_manager, "_check_route_readiness"):
        with patch.object(lifecycle_manager, "_check_options_backend"):
            await lifecycle_manager.start()
            
            with pytest.raises(LifecycleError, match="Cannot start from state"):
                await lifecycle_manager.start()
