"""
Present Bypass Menu Action for Governor.py v1.5

This action presents a bypass menu to the user when a tool is blocked.
It provides options to bypass the block with explicit approval.

This implements the present_bypass_menu action specified in v1.5 spec §6.3.
"""

from typing import Dict, Any, List
from ._base import RuleAction, ActionResult, ActionContext
import uuid
import os
import sys
import json
from datetime import datetime


def log_execution(component: str, data: Dict[str, Any]):
    """Log execution to daily JSONL file."""
    try:
        log_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "logs")
        os.makedirs(log_dir, exist_ok=True)
        
        # Daily log file: Layer3-Python-Execution-Log-MM-DD-YYYY.jsonl
        today = datetime.utcnow()
        log_filename = f"Layer3-Python-Execution-Log-{today.strftime('%m-%d-%Y')}.jsonl"
        log_file = os.path.join(log_dir, log_filename)
        
        log_entry = {
            "action": component,
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


class PresentBypassMenuAction(RuleAction):
    """
    Action to present a bypass menu to the user.
    
    This action generates a bypass menu with options for the user
    to bypass a blocked tool operation with explicit approval.
    """
    
    @property
    def name(self) -> str:
        """Get the action name."""
        return "present_bypass_menu"
    
    def get_required_params(self) -> List[str]:
        """Get list of required parameter names."""
        return []  # No required parameters
    
    def validate_params(self, params: Dict[str, Any]) -> None:
        """
        Validate action parameters.
        
        Args:
            params: Action parameters from rule configuration
            
        Raises:
            ValueError: If parameters are invalid
        """
        # No required parameters for bypass menu action
        pass
    
    def evaluate(self, payload: Dict[str, Any], params: Dict[str, Any],
                 context: ActionContext) -> ActionResult:
        """
        Evaluate the present bypass menu action.
        
        Args:
            payload: Hook event payload
            params: Action parameters
            context: Action context
            
        Returns:
            ActionResult with deny decision and bypass menu
        """
        # Log action execution
        log_execution("PresentBypassMenu", {
            "action": "present_bypass_menu",
            "tool": payload.get("tool", "unknown"),
            "params": params
        })
        
        tool_name = payload.get("tool", "unknown")
        # Note: ActionContext doesn't have phase field in current implementation
        # We'll use a placeholder or extract from state_machine if available
        current_phase = "unknown"
        if context.state_machine:
            current_phase = context.state_machine.get_phase()
        
        # Generate bypass key with UUID4
        bypass_key = f"phase_enforcement:{tool_name}:{uuid.uuid4()}"
        
        # Build bypass menu
        bypass_menu = {
            "title": f"Tool Not Allowed in {current_phase} Phase",
            "message": f"The tool '{tool_name}' is not allowed in the {current_phase} phase.",
            "options": [
                {
                    "label": "Bypass and Execute",
                    "action": "bypass",
                    "bypass_key": bypass_key,
                    "expires": "once"
                },
                {
                    "label": "Cancel",
                    "action": "cancel"
                }
            ]
        }
        
        additional_context = f"""
=== BYPASS MENU ===
Tool: {tool_name}
Phase: {current_phase}
Bypass Key: {bypass_key}

Options:
1. Bypass and Execute (once-scope bypass)
2. Cancel (tool execution blocked)

To bypass permanently, use: /bypass phase_enforcement:{tool_name}
=== END MENU ===
"""
        
        return ActionResult(
            decision="deny",
            reason=f"Tool {tool_name} not allowed in {current_phase} phase - bypass menu presented",
            additional_context=additional_context,
            bypass_menu=bypass_menu
        )
