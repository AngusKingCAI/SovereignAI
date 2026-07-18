"""Concurrency tests for ReActLoop (Plan 23 S9)."""

import pytest
import asyncio
from unittest.mock import MagicMock, AsyncMock

from sovereignai.agent.config import ReActConfig
from sovereignai.agent.react import ReActLoop
from sovereignai.agent.tool_session import ToolSessionRegistry
from sovereignai.observability.trace_emitter import TraceEmitterWrapper


@pytest.fixture
def mock_skill_runner():
    return MagicMock()


@pytest.fixture
def mock_session_registry():
    return ToolSessionRegistry()


@pytest.fixture
def mock_emitter():
    emitter = MagicMock()
    emitter.emit_event = MagicMock()
    return emitter


@pytest.fixture
def mock_event_bus():
    bus = MagicMock()
    bus.is_started = True
    return bus


@pytest.mark.asyncio
async def test_two_concurrent_react_loops(mock_skill_runner, mock_session_registry, mock_emitter, mock_event_bus):
    """Test that two concurrent ReActLoop instances have separate state."""
    trace_wrapper = TraceEmitterWrapper(event_bus=mock_event_bus, inner=mock_emitter)

    config = ReActConfig()

    # Create two ReActLoop instances
    loop1 = ReActLoop(
        config=config,
        skill_runner=mock_skill_runner,
        session_registry=mock_session_registry,
        emitter=trace_wrapper,
    )

    loop2 = ReActLoop(
        config=config,
        skill_runner=mock_skill_runner,
        session_registry=mock_session_registry,
        emitter=trace_wrapper,
    )

    # Verify different session keys
    assert loop1._session_key != loop2._session_key

    # Both should be registered
    assert loop1._session_key in mock_session_registry._sessions
    assert loop2._session_key in mock_session_registry._sessions


@pytest.mark.asyncio
async def test_retry_counters_per_instance(mock_skill_runner, mock_session_registry, mock_emitter, mock_event_bus):
    """Test that retry counters are per-instance, not shared."""
    trace_wrapper = TraceEmitterWrapper(event_bus=mock_event_bus, inner=mock_emitter)

    config = ReActConfig()

    loop1 = ReActLoop(
        config=config,
        skill_runner=mock_skill_runner,
        session_registry=mock_session_registry,
        emitter=trace_wrapper,
    )

    loop2 = ReActLoop(
        config=config,
        skill_runner=mock_skill_runner,
        session_registry=mock_session_registry,
        emitter=trace_wrapper,
    )

    # Set retry counter on loop1
    loop1._file_edit_retry_counter["test.py"] = 3

    # loop2 should not have this counter
    assert loop2._file_edit_retry_counter.get("test.py", 0) == 0


@pytest.mark.asyncio
async def test_error_cleans_up_resources(mock_skill_runner, mock_session_registry, mock_emitter, mock_event_bus):
    """Test that errors clean up resources properly."""
    trace_wrapper = TraceEmitterWrapper(event_bus=mock_event_bus, inner=mock_emitter)

    config = ReActConfig()

    loop = ReActLoop(
        config=config,
        skill_runner=mock_skill_runner,
        session_registry=mock_session_registry,
        emitter=trace_wrapper,
    )

    # Mock LLM to raise error
    loop._mock_llm_call = AsyncMock(side_effect=Exception("Test error"))

    # Run should fail and clean up
    result = await loop.run(
        task_description="Test",
        tools=[],
        session="test",
    )

    assert result.status == "error"
    assert loop._session_key not in mock_session_registry._sessions


@pytest.mark.asyncio
async def test_duplicate_registration_raises(mock_skill_runner, mock_session_registry, mock_emitter, mock_event_bus):
    """Test that duplicate tool registration with different runner raises."""
    trace_wrapper = TraceEmitterWrapper(event_bus=mock_event_bus, inner=mock_emitter)

    config = ReActConfig()

    loop1 = ReActLoop(
        config=config,
        skill_runner=mock_skill_runner,
        session_registry=mock_session_registry,
        emitter=trace_wrapper,
    )

    # Try to register same session key with different runner
    runner2 = MagicMock()
    with pytest.raises(ValueError, match="already registered with different runner"):
        mock_session_registry.register(loop1._session_key, runner2)


@pytest.mark.asyncio
async def test_session_key_is_uuid(mock_skill_runner, mock_session_registry, mock_emitter, mock_event_bus):
    """Test that session keys are valid UUIDs (per S9 requirement)."""
    import uuid

    trace_wrapper = TraceEmitterWrapper(event_bus=mock_event_bus, inner=mock_emitter)

    config = ReActConfig()

    loop = ReActLoop(
        config=config,
        skill_runner=mock_skill_runner,
        session_registry=mock_session_registry,
        emitter=trace_wrapper,
    )

    # Should be valid UUID
    try:
        uuid.UUID(loop._session_key)
    except ValueError:
        pytest.fail("Session key is not a valid UUID")
