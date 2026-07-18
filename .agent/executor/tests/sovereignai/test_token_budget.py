"""Tests for TokenBudgetHistory (Plan 23 S9)."""

import pytest
from sovereignai.agent.history import TokenBudgetExceededError, TokenBudgetHistory


@pytest.fixture
def history():
    return TokenBudgetHistory(max_context_tokens=8192)


def test_add_turn(history):
    """Test adding a conversation turn."""
    history.add_turn("user", "Hello")
    assert len(history.history) == 1
    assert history.history[0] == {"role": "user", "content": "Hello"}


def test_add_multiple_turns(history):
    """Test adding multiple conversation turns."""
    history.add_turn("system", "You are helpful")
    history.add_turn("user", "Hello")
    history.add_turn("assistant", "Hi there")

    assert len(history.history) == 3


def test_to_messages_empty_history(history):
    """Test converting empty history to messages."""
    messages = history.to_messages(budget=8192)
    assert messages == []


def test_to_messages_preserves_system_and_task(history):
    """Test that system prompt and task description are preserved."""
    history.add_turn("system", "You are helpful")
    history.add_turn("user", "Task description")
    history.add_turn("assistant", "Response")
    history.add_turn("user", "Follow-up")

    messages = history.to_messages(budget=8192)

    # System and task should be preserved
    assert messages[0]["role"] == "system"
    assert messages[1]["role"] == "user"
    assert "Task description" in messages[1]["content"]


def test_to_messages_preserves_last_2_turns(history):
    """Test that last 2 turns are preserved."""
    history.add_turn("system", "System")
    history.add_turn("user", "Task")
    history.add_turn("assistant", "Response 1")
    history.add_turn("user", "Follow-up 1")
    history.add_turn("assistant", "Response 2")
    history.add_turn("user", "Follow-up 2")

    messages = history.to_messages(budget=8192)

    # Last 2 turns should be preserved
    assert messages[-2]["role"] == "assistant"
    assert "Response 2" in messages[-2]["content"]
    assert messages[-1]["role"] == "user"
    assert "Follow-up 2" in messages[-1]["content"]


def test_to_messages_truncation_order(history):
    """Test that middle turns are truncated first when budget exceeded."""
    # Add many turns
    history.add_turn("system", "System")
    history.add_turn("user", "Task")
    for i in range(10):
        history.add_turn("assistant", f"Response {i}")
        history.add_turn("user", f"Follow-up {i}")

    # Small budget to force truncation
    messages = history.to_messages(budget=1000)

    # Should have system, task, and last 2 turns
    assert len(messages) >= 4  # Minimum: system + task + last 2
    assert messages[0]["role"] == "system"
    assert messages[1]["role"] == "user"


def test_budget_exceeded_error_on_impossible_minimum(history):
    """Test that TokenBudgetExceededError is raised when pinned minimum exceeds budget."""
    # Add system and task (pinned minimum)
    history.add_turn("system", "You are helpful")
    history.add_turn("user", "A very long task description that exceeds the budget")

    # Budget smaller than pinned minimum
    with pytest.raises(TokenBudgetExceededError) as exc_info:
        history.to_messages(budget=10)

    assert exc_info.value.minimum > exc_info.value.maximum


def test_token_estimation_approximation(history):
    """Test that token estimation uses 4 chars per token approximation."""
    # 100 characters should estimate to ~25 tokens
    history.add_turn("user", "x" * 100)

    messages = history.to_messages(budget=100)  # 100 tokens budget

    # Should fit since 100 chars / 4 = 25 tokens < 100
    assert len(messages) == 1


def test_to_messages_with_insufficient_budget(history):
    """Test behavior when budget is very small but > minimum."""
    history.add_turn("system", "System")
    history.add_turn("user", "Task")
    history.add_turn("assistant", "Response")

    # Budget just enough for system + task
    messages = history.to_messages(budget=50)

    # Should preserve system and task, drop middle turns
    assert len(messages) >= 2
    assert messages[0]["role"] == "system"
