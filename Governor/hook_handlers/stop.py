"""
Stop Handler - Check completion requirements
Layer 2: Handler. Imports _base.py ONLY.
"""

import os
import sys
import json
from typing import Dict, Any
from datetime import datetime

# Get Governor package root
GOVERNOR_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def log_execution(component: str, data: Dict[str, Any]):
    """Log execution to daily JSONL file."""
    try:
        log_dir = os.path.join(GOVERNOR_ROOT, "logs")
        os.makedirs(log_dir, exist_ok=True)
        
        today = datetime.utcnow().strftime("%m-%d-%Y")
        log_file = os.path.join(log_dir, f"Hook-Handler-Log-{today}.jsonl")
        
        entry = {
            "File": "stop.py",
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


try:
    from ._base import HookHandler
except ImportError:
    from hook_handlers._base import HookHandler


class StopHandler(HookHandler):
    """Handler for Stop hook events."""
    
    @property
    def hook_name(self) -> str:
        return "Stop"
    
    @property
    def can_block(self) -> bool:
        return True
    
    def execute(self, payload: Dict[str, Any], state_machine: Any, 
               engine: Any) -> Dict[str, Any]:
        """Execute the Stop handler logic."""
        log_execution("Stop", {"event": "stop"})
        
        current_phase = state_machine.get_phase()
        violations = state_machine.get_violations()
        
        # Check for un-bypassed violations
        if len(violations) > 0:
            return self._build_deny_response(
                reason=f"Session stop blocked: {len(violations)} un-bypassed violations",
                additional_context=f"Violations: {len(violations)}"
            )
        
        return self._build_allow_response(
            reason=f"Session stop approved. Phase: {current_phase}"
        )
