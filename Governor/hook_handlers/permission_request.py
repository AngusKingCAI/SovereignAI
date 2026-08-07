"""
PermissionRequest Handler - Custom permission logic
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
            "File": "permission_request.py",
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


class PermissionRequestHandler(HookHandler):
    """Handler for PermissionRequest hook events."""
    
    @property
    def hook_name(self) -> str:
        return "PermissionRequest"
    
    @property
    def can_block(self) -> bool:
        return True
    
    def execute(self, payload: Dict[str, Any], state_machine: Any, 
               engine: Any) -> Dict[str, Any]:
        """Execute the PermissionRequest handler logic."""
        tool_name = payload.get("tool_name", "unknown")
        
        log_execution("PermissionRequest", {
            "event": "permission_request",
            "tool": tool_name
        })
        
        # Evaluate rules via engine (engine handles ActionContext creation)
        if engine:
            rule_results = engine.evaluate_rules("PermissionRequest", payload, state_machine)
            
            for result in rule_results:
                if result.decision == "deny":
                    if result.permission_decision == "ask":
                        return self._build_response(
                            internal_decision="deny",
                            reason=result.reason,
                            permission_decision="ask",
                            permission_decision_reason=result.permission_decision_reason or result.reason
                        )
                    return self._build_deny_response(
                        reason=f"Rule blocked: {result.reason}"
                    )
        
        # No Governor rule matched - return None to let normal permissions handle it
        log_execution("PermissionRequest", {
            "event": "no_rule_match",
            "action": "return_none"
        })
        return None