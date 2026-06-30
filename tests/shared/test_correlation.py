"""Test correlation ID context variable."""
from uuid import uuid4

from sovereignai.shared.correlation import (
    get_correlation_id,
    new_correlation_scope,
    set_correlation_id,
)


def test_set_and_get_correlation_id() -> None:
    """Verify set_correlation_id and get_correlation_id work."""
    test_id = uuid4()
    set_correlation_id(test_id)
    assert get_correlation_id() == test_id


def test_get_correlation_id_none_outside_scope() -> None:
    """Verify get_correlation_id returns None outside scope."""
    # Clear any existing correlation ID
    set_correlation_id(None)
    assert get_correlation_id() is None


def test_new_correlation_scope_context_manager() -> None:
    """Verify new_correlation_scope context manager works."""
    outer_id = uuid4()
    set_correlation_id(outer_id)

    with new_correlation_scope(uuid4()):
        # Inside scope, should have the new ID
        inner_id = get_correlation_id()
        assert inner_id != outer_id

    # Outside scope, should restore the outer ID
    assert get_correlation_id() == outer_id


def test_thread_propagation() -> None:
    """Verify correlation ID propagates to threads."""
    import threading
    test_id = uuid4()
    set_correlation_id(test_id)

    def check_id() -> None:
        assert get_correlation_id() == test_id

    thread = threading.Thread(target=check_id)
    thread.start()
    thread.join()
