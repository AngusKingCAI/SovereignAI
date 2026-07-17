from __future__ import annotations

from sovereignai.skills.session import SkillSession


def test_session_state_isolation() -> None:
    session = SkillSession()

    session.set("id1", "key1", "value1")
    session.set("id2", "key1", "value2")

    assert session.get("id1", "key1") == "value1"
    assert session.get("id2", "key1") == "value2"


def test_get_history() -> None:
    session = SkillSession()

    session.add_turn("id1", "user", "hello")
    session.add_turn("id1", "assistant", "hi there")

    history = session.get_history("id1")
    assert len(history) == 2
    assert history[0].role == "user"
    assert history[0].content == "hello"
    assert history[1].role == "assistant"
    assert history[1].content == "hi there"


def test_get_history_empty() -> None:
    session = SkillSession()
    history = session.get_history("nonexistent")
    assert history == []


def test_get_nonexistent_key() -> None:
    session = SkillSession()
    assert session.get("id1", "nonexistent") is None
