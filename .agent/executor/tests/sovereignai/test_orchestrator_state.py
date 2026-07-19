from __future__ import annotations

import pytest
from sovereignai.orchestrator.state import (
    ConversationState,
    ConversationStateManager,
    Message,
)


@pytest.mark.asyncio
async def test_conversation_state_creation() -> None:
    state = ConversationState()
    assert state.session_id
    assert len(state.message_history) == 0
    assert state.active_department is None
    assert len(state.pending_clarifications) == 0
    assert len(state.session_metadata) == 0


@pytest.mark.asyncio
async def test_conversation_state_with_messages() -> None:
    state = ConversationState()
    state.message_history.append(Message(role="user", content="hello"))
    state.message_history.append(Message(role="assistant", content="hi there"))

    assert len(state.message_history) == 2
    assert state.message_history[0].role == "user"
    assert state.message_history[1].content == "hi there"


@pytest.mark.asyncio
async def test_state_manager_save_and_load() -> None:
    manager = ConversationStateManager(":memory:")

    state = await manager.create_session()
    state.message_history.append(Message(role="user", content="test"))
    state.active_department = "coding"

    await manager.save_state(state)

    loaded = await manager.load_state(state.session_id)
    assert loaded is not None
    assert loaded.session_id == state.session_id
    assert len(loaded.message_history) == 1
    assert loaded.active_department == "coding"

    manager.close()


@pytest.mark.asyncio
async def test_state_manager_load_nonexistent() -> None:
    manager = ConversationStateManager(":memory:")

    loaded = await manager.load_state("nonexistent-id")
    assert loaded is None

    manager.close()


@pytest.mark.asyncio
async def test_state_manager_delete_session() -> None:
    manager = ConversationStateManager(":memory:")

    state = await manager.create_session()
    await manager.delete_session(state.session_id)

    loaded = await manager.load_state(state.session_id)
    assert loaded is None

    manager.close()


@pytest.mark.asyncio
async def test_state_manager_purge_old_sessions() -> None:
    manager = ConversationStateManager(":memory:")

    state1 = await manager.create_session()
    state2 = await manager.create_session()

    from datetime import datetime, timedelta

    state1.updated_at = datetime.utcnow() - timedelta(days=10)
    await manager.save_state(state1)

    await manager.purge_old_sessions()

    loaded1 = await manager.load_state(state1.session_id)
    loaded2 = await manager.load_state(state2.session_id)

    assert loaded1 is None
    assert loaded2 is not None

    manager.close()


@pytest.mark.asyncio
async def test_state_manager_purge_with_custom_retention() -> None:
    manager = ConversationStateManager(":memory:")
    manager._conversation_retention_days = 1

    state = await manager.create_session()

    from datetime import datetime, timedelta

    state.updated_at = datetime.utcnow() - timedelta(days=2)
    await manager.save_state(state)

    await manager.purge_old_sessions()

    loaded = await manager.load_state(state.session_id)
    assert loaded is None

    manager.close()


def test_message_creation() -> None:
    message = Message(role="user", content="hello")
    assert message.role == "user"
    assert message.content == "hello"
    assert message.timestamp


def test_conversation_state_metadata() -> None:
    state = ConversationState()
    state.session_metadata["user_id"] = "123"
    state.session_metadata["theme"] = "dark"

    assert state.session_metadata["user_id"] == "123"
    assert state.session_metadata["theme"] == "dark"


def test_conversation_state_clarifications() -> None:
    state = ConversationState()
    state.pending_clarifications.append("What project?")
    state.pending_clarifications.append("Which file?")

    assert len(state.pending_clarifications) == 2
    assert "What project?" in state.pending_clarifications
