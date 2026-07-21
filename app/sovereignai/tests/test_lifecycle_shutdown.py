from __future__ import annotations

import asyncio
import signal
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from sovereignai.lifecycle.shutdown import GracefulShutdown
from sovereignai.lifecycle.types import LifecycleState
from sovereignai.shared.trace_emitter import TraceEmitter


@pytest.fixture
def mock_lifecycle_manager():
    manager = MagicMock()
    manager.state = LifecycleState.READY
    manager.shutdown = AsyncMock()
    return manager


@pytest.fixture
def mock_trace():
    trace = MagicMock(spec=TraceEmitter)
    trace.emit = MagicMock()
    return trace


@pytest.fixture
def graceful_shutdown(mock_lifecycle_manager, mock_trace, tmp_path):
    sentinel_path = tmp_path / "shutdown_sentinel"
    return GracefulShutdown(
        lifecycle_manager=mock_lifecycle_manager,
        trace=mock_trace,
        sentinel_path=sentinel_path,
    )


@pytest.mark.asyncio
async def test_sigterm_triggers_shutdown(graceful_shutdown, mock_lifecycle_manager):
    await graceful_shutdown.start()
    
    # Manually trigger shutdown (signal handlers are platform-specific)
    await graceful_shutdown._handle_signal(signal.SIGTERM)
    
    await asyncio.sleep(0.1)  # Let shutdown task run
    
    mock_lifecycle_manager.shutdown.assert_called_once()


@pytest.mark.asyncio
async def test_sigint_triggers_shutdown(graceful_shutdown, mock_lifecycle_manager):
    await graceful_shutdown.start()
    
    # Manually trigger shutdown
    await graceful_shutdown._handle_signal(signal.SIGINT)
    
    await asyncio.sleep(0.1)
    
    mock_lifecycle_manager.shutdown.assert_called_once()


@pytest.mark.asyncio
async def test_sentinel_file_triggers_shutdown(graceful_shutdown, mock_lifecycle_manager):
    await graceful_shutdown.start()
    
    # Create sentinel file
    graceful_shutdown.create_sentinel()
    
    # Wait for sentinel monitoring to detect it
    await asyncio.sleep(2.0)
    
    mock_lifecycle_manager.shutdown.assert_called_once()


@pytest.mark.asyncio
async def test_sentinel_creation_and_removal(graceful_shutdown):
    assert not graceful_shutdown._sentinel_path.exists()
    
    graceful_shutdown.create_sentinel()
    assert graceful_shutdown._sentinel_path.exists()
    
    graceful_shutdown.remove_sentinel()
    assert not graceful_shutdown._sentinel_path.exists()


@pytest.mark.asyncio
async def test_shutdown_idempotent(graceful_shutdown, mock_lifecycle_manager):
    await graceful_shutdown.start()
    
    # Trigger shutdown multiple times
    await graceful_shutdown._handle_signal(signal.SIGTERM)
    await asyncio.sleep(0.1)
    
    call_count = mock_lifecycle_manager.shutdown.call_count
    
    await graceful_shutdown._handle_signal(signal.SIGTERM)
    await asyncio.sleep(0.1)
    
    # Should not call shutdown again
    assert mock_lifecycle_manager.shutdown.call_count == call_count


@pytest.mark.asyncio
async def test_stop_cancels_sentinel_monitoring(graceful_shutdown):
    await graceful_shutdown.start()
    
    await graceful_shutdown.stop()
    
    assert graceful_shutdown._sentinel_task.cancelled()


@pytest.mark.asyncio
async def test_shutdown_error_handling(graceful_shutdown, mock_lifecycle_manager):
    mock_lifecycle_manager.shutdown.side_effect = Exception("Shutdown failed")
    
    await graceful_shutdown.start()
    await graceful_shutdown._handle_signal(signal.SIGTERM)
    
    await asyncio.sleep(0.1)
    
    # Should not raise, just log error
    mock_lifecycle_manager.shutdown.assert_called_once()
