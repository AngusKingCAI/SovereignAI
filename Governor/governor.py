"""
Governor.py - Entry point for Devin CLI hook system
Layer 1: Entry point. Own logging. Imports protocol.py ONLY.
"""

import sys
import json
import os
import uuid
import traceback
from datetime import datetime

# Get Governor package root
GOVERNOR_ROOT = os.path.dirname(os.path.abspath(__file__))


def log_execution(component: str, data: dict):
    """Write to daily JSONL log file."""
    try:
        log_dir = os.path.join(GOVERNOR_ROOT, "logs")
        os.makedirs(log_dir, exist_ok=True)
        
        today = datetime.utcnow().strftime("%m-%d-%Y")
        log_file = os.path.join(log_dir, f"Governor-Log-{today}.jsonl")
        
        entry = {
            "File": "governor.py",
            "hook": component,
            "Time": datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S'),
            "data": data
        }
        
        with open(log_file, 'a', encoding='utf-8') as f:
            f.write(json.dumps(entry) + "\n")
            f.flush()
            
    except Exception as e:
        sys.stderr.write(f"Logging error: {e}\n")
        sys.stderr.flush()


def generate_trace_id():
    """Generate a new UUID4 trace ID."""
    return str(uuid.uuid4())


# Import protocol mapping
try:
    from .protocol import build_hook_response
except ImportError:
    from protocol import build_hook_response

# Import handler registry
try:
    from .hook_handlers import _HOOK_HANDLERS
except ImportError:
    from hook_handlers import _HOOK_HANDLERS

# Import state machine and engine
try:
    from .state_machine import StateMachine
    from .engine import Engine
except ImportError:
    from state_machine import StateMachine
    from engine import Engine


def main():
    """Main entry point for Governor hook handling."""
    try:
        hook_name = sys.argv[1]
        payload = json.loads(sys.stdin.read() or "{}")
        trace_id = generate_trace_id()
        
        log_execution(hook_name, {"event": "hook_fired", "trace_id": trace_id})
        
        handler = _HOOK_HANDLERS.get(hook_name)
        if not handler:
            raise ValueError(f"No handler for: {hook_name}")
        
        state_machine = StateMachine()
        engine = Engine()
        response = handler.execute(payload, state_machine, engine)
        
        # If response is None, handler wants to exit with code 0 (let normal permissions handle it)
        if response is None:
            log_execution(hook_name, {"event": "hook_complete", "decision": "exit_0"})
            sys.exit(0)
        
        log_execution(hook_name, {"event": "hook_complete", "decision": response.get("decision")})
        print(json.dumps(response, indent=2))
        
    except SystemExit as e:
        # Re-raise SystemExit to respect exit codes
        raise
    except Exception as e:
        log_execution("error", {"event": "hook_error", "error": str(e)})
        traceback.print_exc(file=sys.stderr)
        
        # Build error response
        response = build_hook_response(
            internal_decision="allow",
            reason=f"governor_error: {e}",
            hook_event_name=hook_name if 'hook_name' in dir() else "Unknown"
        )
        print(json.dumps(response, indent=2))
        sys.exit(1)


if __name__ == "__main__":
    main()
