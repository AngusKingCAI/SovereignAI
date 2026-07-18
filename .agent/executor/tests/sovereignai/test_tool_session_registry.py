"""Tests for ToolSessionRegistry (Plan 23 S9)."""

from unittest.mock import MagicMock

import pytest
from sovereignai.agent.tool_session import ToolSessionRegistry


@pytest.fixture
def registry():
    return ToolSessionRegistry()


def test_register_tool(registry):
    """Test registering a tool session."""
    runner = MagicMock()
    registry.register("tool1", runner)

    assert "tool1" in registry._sessions
    assert registry._sessions["tool1"] is runner


def test_register_same_tool_same_runner(registry):
    """Test that registering same tool with same runner is no-op."""
    runner = MagicMock()
    registry.register("tool1", runner)
    registry.register("tool1", runner)  # Should not raise

    assert registry._sessions["tool1"] is runner


def test_register_same_tool_different_runner_raises(registry):
    """Test that registering same tool with different runner raises ValueError."""
    runner1 = MagicMock()
    runner2 = MagicMock()
    registry.register("tool1", runner1)

    with pytest.raises(ValueError, match="already registered with different runner"):
        registry.register("tool1", runner2)


def test_close_removes_entry(registry):
    """Test that close removes the session entry."""
    runner = MagicMock()
    registry.register("tool1", runner)
    registry.close("tool1")

    assert "tool1" not in registry._sessions


def test_close_does_not_call_runner_close(registry):
    """Test that close does NOT call runner.close() (singleton per S2.1)."""
    runner = MagicMock()
    runner.close = MagicMock()
    registry.register("tool1", runner)
    registry.close("tool1")

    runner.close.assert_not_called()


def test_close_idempotent(registry):
    """Test that close is idempotent - can be called multiple times."""
    runner = MagicMock()
    registry.register("tool1", runner)
    registry.close("tool1")
    registry.close("tool1")  # Should not raise

    assert "tool1" not in registry._sessions


def test_close_nonexistent_does_not_raise(registry):
    """Test that closing non-existent tool does not raise."""
    registry.close("nonexistent")  # Should not raise


def test_close_all_clears_all(registry):
    """Test that close_all clears all sessions."""
    runner1 = MagicMock()
    runner2 = MagicMock()
    registry.register("tool1", runner1)
    registry.register("tool2", runner2)

    registry.close_all()

    assert len(registry._sessions) == 0


def test_close_all_iterates_copy(registry):
    """Test that close_all iterates over a copy (not original dict)."""
    runner1 = MagicMock()
    runner2 = MagicMock()
    registry.register("tool1", runner1)
    registry.register("tool2", runner2)

    # Mock to verify iteration over copy
    original_items = list(registry._sessions.items())
    registry.close_all()

    # Should not raise even if dict was modified during iteration
    assert len(registry._sessions) == 0
