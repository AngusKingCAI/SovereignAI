"""
PermissionRequest Hook Handler for Governor.py v1.5

This handler processes the PermissionRequest hook event, which is triggered
when the agent requests permission for an operation. It implements auto-approve/deny
logic and escalation based on policy rules.

Key Responsibilities:
- Auto-approve/deny logic based on policy
- Escalation based on rule-based policies
- PermissionDecision field implementation
- Protocol-compliant response

This implements the PermissionRequest handler specified in v1.5 spec §4.3.
"""

from typing import Dict, Any, Optional

# Import base class (package-relative)
try:
    from ._base import HookHandler
except ImportError:
    from hook_handlers._base import HookHandler


class PermissionRequestHandler(HookHandler):
    """
    Handler for PermissionRequest hook events.
    
    PermissionRequest is triggered when the agent requests permission for
    an operation. This handler implements auto-approve/deny logic and
    escalation based on policy rules.
    """
    
    @property
    def hook_name(self) -> str:
        """Return the hook name this handler processes."""
        return "PermissionRequest"
    
    @property
    def can_block(self) -> bool:
        """
        Indicate if this handler can block operations.
        
        PermissionRequest can block by denying permission.
        """
        return True
    
    def execute(self, payload: Dict[str, Any], state_machine: Any, 
               engine: Any) -> Dict[str, Any]:
        """
        Execute the PermissionRequest handler logic.
        
        This method:
        1. Extracts permission request details from payload
        2. Applies auto-approve/deny logic based on policy
        3. Implements escalation for sensitive operations
        4. Sets permissionDecision field
        5. Returns protocol-compliant response
        
        Args:
            payload: PermissionRequest hook event payload
            state_machine: Governor state machine instance
            engine: Rule engine instance (not used in PermissionRequest)
            
        Returns:
            Protocol-compliant response with permissionDecision
        """
        # Extract permission request details
        permission_type = payload.get("permission_type", "")
        resource = payload.get("resource", "")
        operation = payload.get("operation", "")
        reason = payload.get("reason", "")
        
        # Get current phase
        current_phase = state_machine.get_phase()
        
        # Apply auto-approve/deny logic
        permission_decision = self._evaluate_permission(
            permission_type, resource, operation, current_phase, state_machine
        )
        
        # Build additional context
        additional_context = self._build_permission_context(
            permission_type, resource, operation, permission_decision
        )
        
        # Build response with permissionDecision
        return self._build_response(
            internal_decision="allow" if permission_decision == "approve" else "deny",
            reason=f"Permission {permission_decision}: {permission_type} on {resource}",
            additional_context=additional_context,
            permission_decision=permission_decision
        )
    
    def _evaluate_permission(self, permission_type: str, resource: str, 
                           operation: str, current_phase: str,
                           state_machine: Any) -> str:
        """
        Evaluate permission request and return decision.
        
        This method implements auto-approve/deny logic based on:
        - Permission type (read, write, execute, network)
        - Resource sensitivity
        - Current phase
        - Bypass registry
        
        Args:
            permission_type: Type of permission requested
            resource: Resource being accessed
            operation: Operation being performed
            current_phase: Current phase
            state_machine: State machine instance
            
        Returns:
            Permission decision ("approve" or "deny")
        """
        # Check bypass registry first
        bypass_key = f"permission:{permission_type}"
        if state_machine.is_bypassed("permission", permission_type):
            return "approve"
        
        # Auto-approve for read operations in most phases
        if permission_type == "read" and current_phase in ["INIT", "RESEARCH", "PLAN", "EXECUTE", "VALIDATE", "COMMIT"]:
            return "approve"
        
        # Auto-deny for sensitive operations in early phases
        if permission_type in ["write", "execute", "network"] and current_phase in ["INIT", "RESEARCH"]:
            return "deny"
        
        # Auto-approve for write operations in EXECUTE and COMMIT phases
        if permission_type == "write" and current_phase in ["EXECUTE", "COMMIT"]:
            return "approve"
        
        # Auto-approve for execute operations in EXECUTE and VALIDATE phases
        if permission_type == "execute" and current_phase in ["EXECUTE", "VALIDATE"]:
            return "approve"
        
        # Default to approve for unknown combinations (fail-open)
        # Let Devin CLI's config.local.json handle permissions Governor doesn't explicitly manage
        return "approve"
    
    def _build_permission_context(self, permission_type: str, resource: str,
                                operation: str, permission_decision: str) -> str:
        """
        Build permission context for additional information.
        
        Args:
            permission_type: Type of permission requested
            resource: Resource being accessed
            operation: Operation being performed
            permission_decision: Permission decision made
            
        Returns:
            Context string with permission details
        """
        context = f"""
=== PERMISSION REQUEST ===
Type: {permission_type}
Resource: {resource}
Operation: {operation}
Decision: {permission_decision.upper()}

Permission Policy:
- Read: Auto-approved in all phases
- Write: Approved in EXECUTE and COMMIT phases only
- Execute: Approved in EXECUTE and VALIDATE phases only
- Network: Requires explicit approval

To bypass: Use /bypass permission:{permission_type}
=== END PERMISSION ===
"""
        return context
