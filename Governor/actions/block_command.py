"""
Block Command Action - Simple deny action
Layer 4: Action. Imports _base.py ONLY.
"""

from typing import Dict, Any, List
from ._base import RuleAction, ActionResult, ActionContext

class BlockCommandAction(RuleAction):
    """Action to block a command/tool execution."""
    
    @property
    def name(self) -> str:
        return "block_command"
    
    def get_required_params(self) -> List[str]:
        return []
    
    def evaluate(self, payload: Dict[str, Any], params: Dict[str, Any],
                 context: ActionContext) -> ActionResult:
        """Evaluate the block command action."""
        tool_name = payload.get("tool_name", "unknown")
        reason = params.get("reason", f"Tool {tool_name} blocked by governance rule")
        allow_bypass = params.get("allow_bypass", False)
        
        # Log action evaluation
        from ._base import log_execution
        log_execution("block_command_action", {
            "tool": tool_name,
            "reason": reason,
            "allow_bypass": allow_bypass
        })
        
        if allow_bypass:
            result = ActionResult(
                decision="deny",
                reason=reason,
                permission_decision="ask",
                permission_decision_reason=reason
            )
            log_execution("block_command_action", {
                "result_decision": result.decision,
                "result_permission_decision": result.permission_decision
            })
            return result
        
        return ActionResult(
            decision="deny",
            reason=reason
        )
