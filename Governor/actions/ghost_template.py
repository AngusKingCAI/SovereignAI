"""
Ghost Template Action for Governor.py v1.5

This action generates code from templates and injects it into the
context without actually writing files (ghost mode). Useful for
previewing generated code before committing.

This implements the ghost_template action specified in v1.5 spec §6.3.
"""

from typing import Dict, Any, List
from ._base import RuleAction, ActionResult, ActionContext

# Import template loader (package-relative)
try:
    from ..template_loader import render_template
except ImportError:
    from template_loader import render_template


class GhostTemplateAction(RuleAction):
    """
    Action to generate code from templates in ghost mode.
    
    This action renders a template and returns the generated code
    without writing it to disk. Useful for previewing before committing.
    """
    
    @property
    def name(self) -> str:
        """Get the action name."""
        return "ghost_template"
    
    def get_required_params(self) -> List[str]:
        """Get list of required parameter names."""
        return ["template_id"]
    
    def validate_params(self, params: Dict[str, Any]) -> None:
        """
        Validate action parameters.
        
        Args:
            params: Action parameters from rule configuration
            
        Raises:
            ValueError: If parameters are invalid
        """
        # Call parent validation which checks required params
        super().validate_params(params)
    
    def evaluate(self, payload: Dict[str, Any], params: Dict[str, Any],
                 context: ActionContext) -> ActionResult:
        """
        Evaluate the ghost template action.
        
        Args:
            payload: Hook event payload
            params: Action parameters
            context: Action context
            
        Returns:
            ActionResult with allow decision and generated code
        """
        template_id = params.get("template_id")
        template_vars = params.get("variables", {})
        
        try:
            generated_code = render_template(template_id, template_vars)
            
            additional_context = f"""
=== GHOST TEMPLATE GENERATION ===
Template: {template_id}
Variables: {template_vars}

Generated Code (Ghost Mode - Not Written):
{generated_code}
=== END GENERATION ===
"""
            
            return ActionResult(
                decision="allow",
                reason=f"Generated code from template {template_id} (ghost mode)",
                additional_context=additional_context
            )
        except Exception as e:
            return ActionResult(
                decision="allow",  # Fail-open on template errors
                reason=f"Template generation failed: {e}",
                additional_context=f"Error: {str(e)}"
            )
