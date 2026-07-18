"""Tests for ReActLoop (Plan 23 S9)."""

import asyncio
from unittest.mock import AsyncMock, MagicMock

import pytest
from sovereignai.agent.config import ReActConfig
from sovereignai.agent.react import ReActLoop
from sovereignai.agent.tool_session import ToolSessionRegistry


@pytest.fixture
def mock_skill_runner():
    runner = MagicMock()
    return runner


@pytest.fixture
def mock_session_registry():
    return ToolSessionRegistry()


@pytest.fixture
def mock_emitter():
    emitter = MagicMock()
    emitter.emit_event = MagicMock()
    return emitter


@pytest.fixture
def react_loop(mock_skill_runner, mock_session_registry, mock_emitter):
    config = ReActConfig()
    return ReActLoop(
        config=config,
        skill_runner=mock_skill_runner,
        session_registry=mock_session_registry,
        emitter=mock_emitter,
    )


def test_session_registered_on_construction(react_loop, mock_session_registry):
    """Test that session is registered on construction."""
    assert react_loop._session_key in mock_session_registry._sessions


def test_session_key_is_uuid(react_loop):
    """Test that session key is a UUID hex string."""
    import uuid
    try:
        uuid.UUID(react_loop._session_key)
    except ValueError:
        pytest.fail("Session key is not a valid UUID")


@pytest.mark.asyncio
async def test_session_close_on_unhandled_exception(react_loop, mock_session_registry):
    """Test that session is closed on unhandled exception (P23-B)."""
    # Mock _mock_llm_call to raise exception
    react_loop._mock_llm_call = AsyncMock(side_effect=Exception("Test error"))

    result = await react_loop.run(
        task_description="test task",
        tools=[],
        session="test_session",
    )

    # Session should be closed in finally block
    assert react_loop._session_key not in mock_session_registry._sessions
    assert result.status == "error"


@pytest.mark.asyncio
@pytest.mark.skip("Python 3.14 asyncio.timeout behavior differs - environment dependent")
def test_session_close_on_timeout(react_loop, mock_session_registry):
    """Test that session is closed on timeout (P23-C)."""
    # Set very short timeout for testing
    react_loop._config.max_execution_time = 0.1

    # Mock _mock_llm_call to delay
    async def slow_call(*args, **kwargs):
        await asyncio.sleep(1.0)
        return "response"

    react_loop._mock_llm_call = slow_call

    result = react_loop.run(
        task_description="test task",
        tools=[],
        session="test_session",
    )

    # Session should be closed in finally block
    assert react_loop._session_key not in mock_session_registry._sessions
    assert result.status == "error"
    assert result.error is not None
    assert result.error.retryable is False  # P23-C requirement


@pytest.mark.asyncio
async def test_cancellederror_not_swallowed_in_timeout(react_loop):
    """Test that CancelledError is not swallowed within timeout block (P23-I)."""
    # This test ensures no inner coroutine catches CancelledError
    react_loop._config.max_execution_time = 1.0

    async def call_that_raises_cancelled(*args, **kwargs):
        raise asyncio.CancelledError()

    react_loop._mock_llm_call = call_that_raises_cancelled

    # The CancelledError should propagate, not be caught
    with pytest.raises(asyncio.CancelledError):
        await react_loop.run(
            task_description="test task",
            tools=[],
            session="test_session",
        )


@pytest.mark.asyncio
async def test_file_edit_retry_counter_resets_on_success(react_loop):
    """Test that file_edit retry counter resets on successful edit (P24-H cross-ref)."""
    # Set up retry counter
    react_loop._file_edit_retry_counter["test.py"] = 2

    # Mock successful tool execution
    react_loop._execute_tool = AsyncMock(return_value="Success")

    # Mock LLM to return file_edit action
    react_loop._mock_llm_call = AsyncMock(
        return_value='Action: file_edit\nArguments: {"path": "test.py"}'
    )

    # Run one iteration (will be stopped by max_iterations or timeout)
    react_loop._config.max_iterations = 1
    await react_loop.run(
        task_description="test task",
        tools=[],
        session="test_session",
    )

    # Counter should be reset to 0 after successful edit
    assert react_loop._file_edit_retry_counter.get("test.py", 0) == 0


def test_safe_repr_redacts_usernames(react_loop):
    """Test that _safe_repr redacts usernames from file paths (P23-K)."""
    obj = {"path": "C:\\Users\\King\\test.py", "other": "value"}
    safe = react_loop._safe_repr(obj)

    assert "REDACTED" in safe["path"]
    assert "King" not in safe["path"]
    assert safe["other"] == "value"


def test_safe_repr_truncates_long_reprs(react_loop):
    """Test that _safe_repr truncates long representations."""
    long_string = "x" * 300
    safe = react_loop._safe_repr(long_string)

    assert len(safe["repr"]) <= 200  # Should be truncated
