"""
Block Command Action for Governor.py v1.5

This action blocks the execution of a command/tool that violates
governance rules. It provides a clear error message and explanation.

This implements the block_command action specified in v1.5 spec §6.3.
"""

from typing import Dict, Any, List
from ._base import RuleAction, ActionResult, ActionContext


class BlockCommandAction(RuleAction):
    """
    Action to block a command/tool execution.
    
    This action is used when a tool violates governance rules.
    It provides a clear error message and blocks the operation.
    """
    
    @property
    def name(self) -> str:
        """Get the action name."""
        return "block_command"
    
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
        # No required parameters for block action
        pass
    
    def evaluate(self, payload: Dict[str, Any], params: Dict[str, Any],
                 context: ActionContext) -> ActionResult:
        """
        Evaluate the block command action.
        
        Args:
            payload: Hook event payload
            params: Action parameters
            context: Action context
            
        Returns:
            ActionResult with deny decision
        """
        tool_name = payload.get("tool", "unknown")
        # Note: ActionContext doesn't have phase field in current implementation
        # We'll use a placeholder or extract from state_machine if available
        current_phase = "unknown"
        if context.state_machine:
            current_phase = context.state_machine.get_phase()
        
        reason = params.get("reason", f"Tool {tool_name} blocked by governance rule")
        
        additional_context = f"""
=== BLOCKED BY GOVERNOR ===
Tool: {tool_name}
Phase: {current_phase}
Reason: {reason}

To proceed, you must either:
1. Transition to an appropriate phase
2. Use a bypass command: /bypass <rule_id>:<tool>
=== END BLOCK ===
"""
        
        return ActionResult(
            decision="deny",
            reason=reason,
            additional_context=additional_context
        )
