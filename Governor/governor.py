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
from datetime import datetime
import os

# Centralized logging function for all Governor Python files
def log_governor_execution(component: str, data: Dict[str, Any]):
    """Log execution to daily JSONL file."""
    try:
        log_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "logs")
        os.makedirs(log_dir, exist_ok=True)
        
        # Daily log file: Governor-Python-Execution-Log-MM-DD-YYYY.jsonl
        today = datetime.utcnow()
        log_filename = f"Governor-Python-Execution-Log-{today.strftime('%m-%d-%Y')}.jsonl"
        log_file = os.path.join(log_dir, log_filename)
        
        log_entry = {
            "File": "Governor",
            "hook": component,
            "Time": today.strftime('%Y-%m-%dT%H:%M:%S'),
            "data": data
        }
        
        with open(log_file, 'a', encoding='utf-8') as f:
            f.write(json.dumps(log_entry) + "\n")
            f.flush()
            
    except Exception as e:
        # Don't fail if logging fails, but print error to stderr
        sys.stderr.write(f"Logging error: {e}\n")
        sys.stderr.flush()

# Import debug logging
try:
    from .debug_logging import debug_log, is_debug_enabled
except ImportError:
    from debug_logging import debug_log, is_debug_enabled

# Import handler logging
try:
    from .hook_handlers._base import log_handler_execution
except ImportError:
    from hook_handlers._base import log_handler_execution

# Import trace ID management
try:
    from .trace_id import generate_trace_id, set_trace_id, get_trace_id
except ImportError:
    from trace_id import generate_trace_id, set_trace_id, get_trace_id

# Governor imports (package-relative with fallback for direct execution)
try:
    from .protocol import build_hook_response, to_devin_decision
except ImportError:
    from protocol import build_hook_response, to_devin_decision

# Import hook handlers package (package-relative with fallback)
try:
    from .hook_handlers import _HOOK_HANDLERS
except ImportError:
    from hook_handlers import _HOOK_HANDLERS


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
    
    # Get handler from registry
    handler = _HOOK_HANDLERS.get(hook_name)
    if not handler:
        raise ValueError(f"No handler registered for hook: {hook_name}")
    
    # Instantiate state machine and engine
    try:
        from .state_machine import StateMachine
    except ImportError:
        from state_machine import StateMachine
    
    try:
        from .engine import Engine
    except ImportError:
        from engine import Engine
    
    state_machine = StateMachine()
    engine = Engine()
    
    # Generate or get trace ID and add to payload
    current_trace_id = get_trace_id()
    if "trace_id" not in payload:
        payload["trace_id"] = current_trace_id
    
    debug_log("governor", f"Dispatching hook: {hook_name}", trace_id=current_trace_id)
    
    # Execute handler
    response = handler.execute(payload, state_machine, engine)
    
    # Log execution at governor level
    log_governor_execution(hook_name, {
        "decision": response.get("decision", "unknown")
    })
    
    return response


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
        # Read payload first to get hook name from stdin
        payload = _read_payload()
        
        # Try to get hook name from payload first
        hook_name = payload.get("hook_name") or payload.get("hook") or payload.get("event")
        
        # Try sys.argv[1] as fallback
        if not hook_name and len(sys.argv) >= 2:
            hook_name = sys.argv[1]
        
        # Try environment variable
        if not hook_name:
            hook_name = os.environ.get("GOVERNOR_HOOK_NAME")
        
        # If still no hook name, try to infer from command used to invoke
        if not hook_name and len(sys.argv) >= 1:
            # The hook name might be passed via stdin or as part of the workflow
            # Log the argv for debugging
            sys.stderr.write(f"DEBUG: argv = {sys.argv}, payload keys = {list(payload.keys())}\n")
            sys.stderr.flush()
        
        # If still no hook name, try to infer from payload or use default
        if not hook_name:
            hook_name = "unknown"
            sys.stderr.write(f"WARNING: No hook name provided, argv: {sys.argv}, payload: {payload}\n")
            sys.stderr.flush()
        
        # DEBUG: Print to see if Governor is called
        print(f"GOVERNOR CALLED: hook={hook_name}", flush=True, file=sys.stderr)
        
        # If hook_name is unknown, we still need to validate for the error handler
        if hook_name == "unknown":
            # But don't raise error, just continue with unknown
            pass
        
        # Dispatch hook (payload is already read above)
        response = _dispatch_hook(hook_name, payload)
        
        # Output response as JSON
        print(json.dumps(response, indent=2))
        
    except Exception as e:
        # Fail-open error handling
        hook_name = sys.argv[1] if len(sys.argv) >= 2 else "Unknown"
        payload = {}
        
        # DEBUG: Print error
        print(f"GOVERNOR ERROR: {e}", flush=True, file=sys.stderr)
        
        error_response = _dispatch_error(hook_name, e, payload)
        print(json.dumps(error_response, indent=2))
        
        # Also print traceback to stderr for debugging
        traceback.print_exc(file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
