"""
Debug Logging for Governor.py v1.5

This module provides per-layer debug logging functionality for Governor.
It supports environment variable-based debug level control for different
components: engine, state_machine, hook_handlers, actions, audit.

Key Functions:
- set_debug_level(): Set debug level for a specific layer
- is_debug_enabled(): Check if debug is enabled for a layer
- debug_log(): Log debug message if enabled

This implements the debug logging specified in v1.5 spec §4.6.
"""

import os
from typing import Dict, Set

# Debug level environment variables
DEBUG_LEVELS = {
    "GOVERNOR_DEBUG_ENGINE": "engine",
    "GOVERNOR_DEBUG_STATE_MACHINE": "state_machine",
    "GOVERNOR_DEBUG_HOOK_HANDLERS": "hook_handlers",
    "GOVERNOR_DEBUG_ACTIONS": "actions",
    "GOVERNOR_DEBUG_AUDIT": "audit"
}

# Set of enabled debug layers
_enabled_debug_layers: Set[str] = set()

def _load_debug_settings() -> None:
    """Load debug settings from environment variables."""
    global _enabled_debug_layers
    _enabled_debug_layers = set()
    
    for env_var, layer in DEBUG_LEVELS.items():
        if os.getenv(env_var, "").lower() in ("1", "true", "yes", "on"):
            _enabled_debug_layers.add(layer)

# Load debug settings on module import
_load_debug_settings()

def is_debug_enabled(layer: str) -> bool:
    """
    Check if debug is enabled for a specific layer.
    
    Args:
        layer: Layer name (engine, state_machine, hook_handlers, actions, audit)
        
    Returns:
        True if debug is enabled for the layer
    """
    return layer in _enabled_debug_layers

def debug_log(layer: str, message: str, **kwargs) -> None:
    """
    Log a debug message if the layer's debug is enabled.
    
    Args:
        layer: Layer name (engine, state_machine, hook_handlers, actions, audit)
        message: Debug message
        **kwargs: Additional context data
    """
    if is_debug_enabled(layer):
        import sys
        from datetime import datetime
        
        timestamp = datetime.utcnow().isoformat()
        context_str = " ".join(f"{k}={v}" for k, v in kwargs.items())
        debug_line = f"[{timestamp}] [{layer.upper()}] {message}"
        if context_str:
            debug_line += f" | {context_str}"
        
        print(debug_line, file=sys.stderr)

def set_debug_level(layer: str, enabled: bool) -> None:
    """
    Set debug level for a specific layer.
    
    Args:
        layer: Layer name (engine, state_machine, hook_handlers, actions, audit)
        enabled: Whether to enable debug for this layer
    """
    if enabled:
        _enabled_debug_layers.add(layer)
    elif layer in _enabled_debug_layers:
        _enabled_debug_layers.remove(layer)

def get_enabled_layers() -> Set[str]:
    """
    Get the set of currently enabled debug layers.
    
    Returns:
        Set of enabled layer names
    """
    return _enabled_debug_layers.copy()
