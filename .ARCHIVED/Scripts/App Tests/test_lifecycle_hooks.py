from __future__ import annotations

import asyncio
import logging
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from sovereignai.lifecycle.hooks import HookPhase, LifecycleHookRegistry
from sovereignai.lifecycle.types import LifecycleError


@pytest.fixture
def mock_event_bus():
    bus = MagicMock()
    bus.publish_async = AsyncMock()
    return bus


@pytest.fixture
def mock_trace():
    trace = MagicMock()
    trace.emit = MagicMock()
    return trace


@pytest.fixture
def hook_registry(mock_event_bus, mock_trace):
    return LifecycleHookRegistry(
        event_bus=mock_event_bus,
        trace=mock_trace,
    )


@pytest.mark.asyncio
async def test_critical_startup_hook_failure_aborts(hook_registry):
    critical_hook = MagicMock(side_effect=Exception("Critical hook failed"))
    hook_registry.register_startup_hook("critical", critical_hook, critical=True)
    
    await hook_registry.close_registration()
    
    with pytest.raises(LifecycleError, match="Critical startup hook failed"):
        await hook_registry.run_startup_hooks()
    
    assert hook_registry.phase == HookPhase.STARTUP_DONE


@pytest.mark.asyncio
async def test_non_critical_startup_hook_failure_continues(hook_registry):
    non_critical_hook = MagicMock(side_effect=Exception("Non-critical hook failed"))
    hook_registry.register_startup_hook("non_critical", non_critical_hook, critical=False)
    
    await hook_registry.close_registration()
    
    await hook_registry.run_startup_hooks()
    
    assert hook_registry.phase == HookPhase.STARTUP_DONE


@pytest.mark.asyncio
async def test_shutdown_hook_concurrent_timeout(hook_registry):
    async def slow_hook():
        await asyncio.sleep(20)
    
    hook_registry.register_shutdown_hook("slow", slow_hook, critical=False)
    hook_registry.register_shutdown_hook("fast", lambda: None, critical=False)
    
    await hook_registry.close_registration()
    hook_registry._phase = HookPhase.STARTUP_DONE
    
    await hook_registry.run_shutdown_hooks()
    
    assert hook_registry.phase == HookPhase.SHUTDOWN_DONE


@pytest.mark.asyncio
async def test_max_5_startup_hooks_enforced(hook_registry):
    for i in range(5):
        hook_registry.register_startup_hook(f"hook_{i}", lambda: None, critical=False)
    
    with pytest.raises(LifecycleError, match="Maximum startup hooks"):
        hook_registry.register_startup_hook("hook_6", lambda: None, critical=False)


@pytest.mark.asyncio
async def test_max_5_shutdown_hooks_enforced(hook_registry):
    for i in range(5):
        hook_registry.register_shutdown_hook(f"hook_{i}", lambda: None, critical=False)
    
    with pytest.raises(LifecycleError, match="Maximum shutdown hooks"):
        hook_registry.register_shutdown_hook("hook_6", lambda: None, critical=False)


@pytest.mark.asyncio
async def test_register_after_close_fails(hook_registry):
    await hook_registry.close_registration()
    
    with pytest.raises(LifecycleError, match="Cannot register startup hook"):
        hook_registry.register_startup_hook("late", lambda: None, critical=False)
    
    with pytest.raises(LifecycleError, match="Cannot register shutdown hook"):
        hook_registry.register_shutdown_hook("late", lambda: None, critical=False)


@pytest.mark.asyncio
async def test_hook_phases_transition(hook_registry):
    assert hook_registry.phase == HookPhase.REGISTRATION_OPEN
    
    hook_registry.register_startup_hook("test", lambda: None, critical=False)
    await hook_registry.close_registration()
    assert hook_registry.phase == HookPhase.REGISTRATION_CLOSED
    
    await hook_registry.run_startup_hooks()
    assert hook_registry.phase == HookPhase.STARTUP_DONE
    
    hook_registry._phase = HookPhase.STARTUP_DONE
    await hook_registry.run_shutdown_hooks()
    assert hook_registry.phase == HookPhase.SHUTDOWN_DONE


@pytest.mark.asyncio
async def test_async_hooks_supported(hook_registry):
    async_flag = False
    
    async def async_hook():
        nonlocal async_flag
        async_flag = True
    
    hook_registry.register_startup_hook("async", async_hook, critical=False)
    await hook_registry.close_registration()
    await hook_registry.run_startup_hooks()
    
    assert async_flag


@pytest.mark.asyncio
async def test_critical_shutdown_hook_failure_logged(hook_registry):
    critical_hook = MagicMock(side_effect=Exception("Critical shutdown failed"))
    hook_registry.register_shutdown_hook("critical", critical_hook, critical=True)
    
    await hook_registry.close_registration()
    hook_registry._phase = HookPhase.STARTUP_DONE
    
    await hook_registry.run_shutdown_hooks()
    
    assert hook_registry.phase == HookPhase.SHUTDOWN_DONE
