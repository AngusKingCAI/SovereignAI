"""Correlation ID context variable for tracing.

Per OR98: Every trace event emitted in response to a user-initiated action
must carry a correlation_id that propagates from the entry point through
every downstream call.
"""
import contextvars
from threading import local
from typing import Any
from uuid import UUID, uuid4

# Context variable for current correlation ID
_correlation_id: contextvars.ContextVar[UUID | None] = contextvars.ContextVar(
    "correlation_id", default=None
)

# Thread-local storage for thread propagation
_thread_local = local()


def set_correlation_id(correlation_id: UUID | None) -> None:
    """Set the current correlation ID in the async context variable for tracing.

    Args:
        correlation_id: The correlation ID to set, or None to clear.
    """
    _correlation_id.set(correlation_id)
    # Also store in thread-local for thread propagation
    _thread_local.correlation_id = correlation_id


def get_correlation_id() -> UUID | None:
    """Get the current correlation ID from the async context variable for tracing.

    Returns:
        The current correlation ID, or None if not set.
    """
    try:
        return _correlation_id.get()
    except LookupError:
        return None


def new_correlation_scope(correlation_id: UUID | None) -> "CorrelationScope":
    """Create a new correlation ID scope as a context manager.

    Args:
        correlation_id: The correlation ID for the new scope.

    Returns:
        A context manager that sets and restores the correlation ID.
    """
    return CorrelationScope(correlation_id)


class CorrelationScope:
    """Context manager for a correlation ID scope."""

    def __init__(self, correlation_id: UUID | None) -> None:
        """Initialize the scope with a correlation ID.

        Args:
            correlation_id: The correlation ID for this scope.
        """
        self._new_id = correlation_id
        self._old_id: UUID | None = None

    def __enter__(self) -> "CorrelationScope":
        """Enter the scope and set the new correlation ID."""
        self._old_id = get_correlation_id()
        set_correlation_id(self._new_id)
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Exit the scope and restore the old correlation ID."""
        _ = exc_type, exc_val, exc_tb  # Unused but required by context manager protocol
        set_correlation_id(self._old_id)


def generate_correlation_id() -> UUID:
    """Generate a new correlation ID.

    Returns:
        A new UUID4 correlation ID.
    """
    return uuid4()


def copy_correlation_id_to_thread() -> None:
    """Copy the current correlation ID to thread-local storage for thread propagation.

    This should be called when spawning a new thread to propagate the
    correlation ID into the new thread's context.
    """
    _thread_local.correlation_id = get_correlation_id()


def get_thread_correlation_id() -> UUID | None:
    """Get the correlation ID from thread-local storage.

    Returns:
        The thread-local correlation ID, or None if not set.
    """
    return getattr(_thread_local, "correlation_id", None)
