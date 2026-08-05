"""
Governor.py v1.5 - Entry Point and Hook Dispatcher

This is the main entry point for Governor that receives hook events from
Devin CLI and routes them to the appropriate hook handlers.

Architecture:
- Receives hook name as CLI argument (sys.argv[1])
- Reads JSON payload from stdin
- Routes to appropriate hook handler via auto-discovery
- Implements fail-open error handling
- Integrates with state machine lifecycle
- Logs all events to audit trail

Usage:
    python Governor/governor.py SessionStart
    python Governor/governor.py PreToolUse
    python Governor/governor.py PostToolUse
    # ... etc for all 8 hooks
"""

import sys
import json
import traceback
from typing import Dict, Any, Optional

# Governor imports
from protocol import build_hook_response, to_devin_decision

# Hook handler registry (will be populated by auto-discovery in Phase 2)
_HOOK_HANDLERS = {}


def register_hook_handler(hook_name: str, handler_class):
    """Register a hook handler for a specific hook event."""
    _HOOK_HANDLERS[hook_name] = handler_class


def _dispatch_error(hook_name: str, error: Exception, payload: Dict[str, Any]) -> Dict[str, Any]:
    """
    Fail-open error handler with Devin protocol compliance.
    
    When Governor encounters an error, it must fail-open (allow the operation)
    to prevent blocking the agent due to harness failures. This ensures that
    bugs in Governor don't prevent development work.
    
    Args:
        hook_name: Name of the hook that failed
        error: The exception that occurred
        payload: Original hook payload
        
    Returns:
        Protocol-compliant hook response with "approve" decision
        
    Example:
        >>> _dispatch_error("PreToolUse", ValueError("test"), {})
        {
            "decision": "approve",
            "governor_internal": {"decision": "allow"},
            "reason": "governor_error: test",
            "hookSpecificOutput": {"hookEventName": "PreToolUse"}
        }
    """
    error_message = f"{type(error).__name__}: {str(error)}"
    
    # Log the error (will be implemented in Task 1.7)
    # log_event(hook_name, payload, {"decision": "allow", "reason": f"governor_error: {error_message}"}, level="error")
    
    # Return fail-open response
    return build_hook_response(
        internal_decision="allow",
        reason=f"governor_error: {error_message}",
        hook_event_name=hook_name
    )


def _read_payload() -> Dict[str, Any]:
    """
    Read JSON payload from stdin.
    
    Devin CLI sends hook event data as JSON via stdin.
    
    Returns:
        Parsed JSON payload as dict
        
    Raises:
        ValueError: If payload cannot be parsed as JSON
    """
    try:
        payload_str = sys.stdin.read()
        if not payload_str:
            return {}
        return json.loads(payload_str)
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON payload: {e}")


def _dispatch_hook(hook_name: str, payload: Dict[str, Any]) -> Dict[str, Any]:
    """
    Dispatch hook event to appropriate handler.
    
    Args:
        hook_name: Name of the hook event
        payload: Hook event payload
        
    Returns:
        Protocol-compliant hook response
        
    Raises:
        ValueError: If hook_name is not recognized
    """
    # Valid hook names per v1.5 spec
    valid_hooks = [
        "SessionStart",
        "UserPromptSubmit", 
        "PreToolUse",
        "PostToolUse",
        "PermissionRequest",
        "Stop",
        "SessionEnd",
        "PostCompaction"
    ]
    
    if hook_name not in valid_hooks:
        raise ValueError(f"Unknown hook: {hook_name}. Valid hooks: {valid_hooks}")
    
    # TODO: Route to actual hook handler (will be implemented in Phase 2)
    # For now, return a basic response
    # handler = _HOOK_HANDLERS.get(hook_name)
    # if handler:
    #     return handler.execute(payload, state_machine, engine)
    
    # Placeholder response until hook handlers are implemented
    return build_hook_response(
        internal_decision="allow",
        reason=f"Hook handler for {hook_name} not yet implemented (Phase 2)",
        hook_event_name=hook_name
    )


def main():
    """
    Main entry point for Governor.
    
    Workflow:
    1. Parse hook name from sys.argv[1]
    2. Read JSON payload from stdin
    3. Dispatch to appropriate hook handler
    4. Return JSON response to stdout
    5. Handle errors with fail-open policy
    """
    try:
        # Parse hook name
        if len(sys.argv) < 2:
            raise ValueError("Hook name required as first argument")
        
        hook_name = sys.argv[1]
        
        # Read payload from stdin
        payload = _read_payload()
        
        # Dispatch hook
        response = _dispatch_hook(hook_name, payload)
        
        # Output response as JSON
        print(json.dumps(response, indent=2))
        
    except Exception as e:
        # Fail-open error handling
        hook_name = sys.argv[1] if len(sys.argv) >= 2 else "Unknown"
        payload = {}
        
        error_response = _dispatch_error(hook_name, e, payload)
        print(json.dumps(error_response, indent=2))
        
        # Also print traceback to stderr for debugging
        traceback.print_exc(file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
