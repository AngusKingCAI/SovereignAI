"""
Trace ID Management for Governor.py v1.5

This module provides trace ID generation and propagation for
correlating events across the entire Governor execution flow.

Key Functions:
- generate_trace_id(): Generate a UUID4 trace ID
- get_trace_id(): Get current trace ID from context or environment
- set_trace_id(): Set trace ID in context
- trace_context(): Context manager for trace ID propagation

This implements the trace ID system specified in v1.5 spec §4.5.
"""

import uuid
import os
from typing import Optional
from contextlib import contextmanager

# Trace ID environment variable
TRACE_ID_ENV_VAR = "GOVERNOR_TRACE_ID"

# Thread-local storage for trace ID
import threading
_trace_id_local = threading.local()


def generate_trace_id() -> str:
    """
    Generate a new UUID4 trace ID.
    
    Returns:
        UUID4 string trace ID
    """
    return str(uuid.uuid4())


def get_trace_id() -> str:
    """
    Get the current trace ID from context or environment.
    
    Priority:
    1. Thread-local storage (set by set_trace_id)
    2. Environment variable (GOVERNOR_TRACE_ID)
    3. Generate new trace ID if none exists
    
    Returns:
        Current trace ID string
    """
    # Check thread-local storage first
    if hasattr(_trace_id_local, 'trace_id') and _trace_id_local.trace_id:
        return _trace_id_local.trace_id
    
    # Check environment variable
    env_trace_id = os.getenv(TRACE_ID_ENV_VAR)
    if env_trace_id:
        return env_trace_id
    
    # Generate new trace ID as fallback
    new_trace_id = generate_trace_id()
    set_trace_id(new_trace_id)
    return new_trace_id


def set_trace_id(trace_id: str) -> None:
    """
    Set the trace ID in thread-local storage.
    
    Args:
        trace_id: Trace ID string to set
    """
    _trace_id_local.trace_id = trace_id


@contextmanager
def trace_context(trace_id: Optional[str] = None):
    """
    Context manager for trace ID propagation.
    
    Args:
        trace_id: Trace ID to use, or None to generate new one
        
    Yields:
        Trace ID string
    """
    if trace_id is None:
        trace_id = generate_trace_id()
    
    old_trace_id = None
    if hasattr(_trace_id_local, 'trace_id'):
        old_trace_id = _trace_id_local.trace_id
    
    set_trace_id(trace_id)
    
    try:
        yield trace_id
    finally:
        if old_trace_id:
            set_trace_id(old_trace_id)
        elif hasattr(_trace_id_local, 'trace_id'):
            del _trace_id_local.trace_id


def reset_trace_id() -> None:
    """
    Reset the trace ID in thread-local storage.
    """
    if hasattr(_trace_id_local, 'trace_id'):
        del _trace_id_local.trace_id
