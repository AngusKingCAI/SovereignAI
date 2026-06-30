"""Tests for correlation ID propagation."""
from uuid import uuid4

from sovereignai.shared.correlation import (
    copy_correlation_id_to_thread,
    get_correlation_id,
    new_correlation_scope,
    set_correlation_id,
)


def test_set_and_get_correlation_id() -> None:
    """Test that set_correlation_id and get_correlation_id work correctly."""
    test_id = uuid4()
    set_correlation_id(test_id)
    assert get_correlation_id() == test_id


def test_new_correlation_scope() -> None:
    """Test that new_correlation_scope creates a new context."""
    outer_id = uuid4()
    set_correlation_id(outer_id)

    with new_correlation_scope(uuid4()):
        inner_id = get_correlation_id()
        assert inner_id != outer_id

    # After scope, should restore outer ID
    assert get_correlation_id() == outer_id


def test_nested_scopes() -> None:
    """Test that nested correlation scopes work correctly."""
    outer_id = uuid4()
    set_correlation_id(outer_id)

    with new_correlation_scope(uuid4()):
        middle_id = get_correlation_id()
        with new_correlation_scope(uuid4()):
            inner_id = get_correlation_id()
            assert inner_id != middle_id
            assert inner_id != outer_id
        assert get_correlation_id() == middle_id

    assert get_correlation_id() == outer_id


def test_copy_correlation_id_to_thread() -> None:
    """Test that copy_correlation_id_to_thread propagates correlation ID to a thread."""
    import threading

    test_id = uuid4()
    set_correlation_id(test_id)

    thread_local = threading.local()

    def thread_func():
        copy_correlation_id_to_thread()
        thread_local.captured_id = get_correlation_id()

    thread = threading.Thread(target=thread_func)
    thread.start()
    thread.join()

    assert thread_local.captured_id == test_id
