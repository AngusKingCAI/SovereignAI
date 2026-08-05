"""
Present Bypass Menu Action for Governor.py v1.5

This action presents a bypass menu to the user when a tool is blocked.
It provides options to bypass the block with explicit approval.

This implements the present_bypass_menu action specified in v1.5 spec §6.3.
"""

from typing import Dict, Any, List
from ._base import RuleAction, ActionResult, ActionContext
import uuid


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
