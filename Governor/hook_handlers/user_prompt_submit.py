"""
UserPromptSubmit Handler - Parse bypass commands
Layer 2: Handler. Imports _base.py ONLY.
"""

import re
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
            "File": "user_prompt_submit.py",
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


class UserPromptSubmitHandler(HookHandler):
    """Handler for UserPromptSubmit hook events."""
    
    @property
    def hook_name(self) -> str:
        return "UserPromptSubmit"
    
    @property
    def can_block(self) -> bool:
        return False
    
    def execute(self, payload: Dict[str, Any], state_machine: Any, 
               engine: Any) -> Dict[str, Any]:
        """Execute the UserPromptSubmit handler logic."""
        user_prompt = payload.get("user_prompt", "")
        
        log_execution("UserPromptSubmit", {
            "event": "user_prompt_submit",
            "prompt_length": len(user_prompt)
        })
        
        # Parse bypass commands
        bypass_pattern = r"/bypass\s+(\S+)"
        matches = re.findall(bypass_pattern, user_prompt)
        
        additional_context = ""
        for bypass_key in matches:
            if bypass_key == "all":
                state_machine.add_bypass(
                    rule_id="*",
                    tool_name="*",
                    scope="once",
                    reason="User requested bypass all",
                    source="user_command"
                )
                additional_context += "\n✓ Bypass registered: next tool call only"
            else:
                parts = bypass_key.split(":")
                if len(parts) >= 2:
                    rule_id = parts[0]
                    tool_name = parts[1]
                else:
                    rule_id = bypass_key
                    tool_name = "*"
                
                state_machine.add_bypass(
                    rule_id=rule_id,
                    tool_name=tool_name,
                    scope="session",
                    reason="User requested bypass",
                    source="user_command"
                )
                additional_context += f"\n✓ Bypass registered: {bypass_key}"
        
        return self._build_allow_response(
            reason="User prompt processed",
            additional_context=additional_context
        )
