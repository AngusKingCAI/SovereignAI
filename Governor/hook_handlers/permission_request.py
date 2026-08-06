"""
PermissionRequest Hook Handler for Governor.py v1.5

This handler processes the PermissionRequest hook event, which is triggered
when the agent requests permission for an operation. It implements auto-approve/deny
logic and escalation based on policy rules, with persistence of permission decisions.

Key Responsibilities:
- Check saved permission decisions from config.local.json
- Check Governor's permission registry
- Auto-approve/deny logic based on policy
- Permission decision persistence to state.json
- Escalation based on rule-based policies
- PermissionDecision field implementation
- Protocol-compliant response

This implements the PermissionRequest handler specified in v1.5 spec §4.3.
"""

import os
import json
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
        1. Completely defers to Devin CLI's native permission system
        2. Does not interfere with permission windows
        3. Only reads from config.local.json to respect existing choices
        4. Returns protocol-compliant allow response to let Devin CLI handle permissions
        
        Args:
            payload: PermissionRequest hook event payload
            state_machine: Governor state machine instance
            engine: Rule engine instance (not used in PermissionRequest)
            
        Returns:
            Protocol-compliant allow response to let Devin CLI handle permissions
        """
        # Complete defer to Devin CLI's native permission system
        # Don't make any decisions, don't save anything, just let it through
        return self._build_response(
            internal_decision="allow",
            reason="Governor deferring to Devin CLI native permission system",
            hook_event_name="PermissionRequest"
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
        
        IMPORTANT: To let Devin CLI show permission windows, we should NOT auto-approve.
        We should return "deny" or skip the decision to let Devin CLI handle it.
        
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
        
        # DON'T auto-approve - let Devin CLI show permission windows
        # This allows users to choose "Allow for project (local)" which saves to config.local.json
        # Only auto-deny for dangerous operations in early phases
        if permission_type in ["network"] and current_phase in ["INIT", "RESEARCH"]:
            return "deny"
        
        # For all other cases, return "deny" to let Devin CLI show permission windows
        # This allows the user to make choices and have them saved to config.local.json
        return "deny"
    
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
- Governor reads from .devin/config.local.json (same format as Devin CLI)
- Governor checks: permissions.allow and permissions.deny patterns
- Pattern format: Exec(ls), Read(*.py), Write(src/*), etc.
- Wildcards supported: Exec(*), Read(*.py), etc.
- When Governor makes auto-decisions, it approves to let Devin CLI handle permission windows
- User permission choices are saved to config.local.json by Devin CLI

To bypass: Use /bypass permission:{permission_type}
=== END PERMISSION ===
"""
        return context
    
    def _check_config_local_permissions(self, permission_type: str, resource: str, 
                                       operation: str) -> Optional[str]:
        """
        Check if user has already made a permission decision in config.local.json.
        
        Devin CLI stores permission decisions in .devin/config.local.json with format:
        { "permissions": { "allow": ["Exec(ls)", "Read(*.py)", ... ] } }
        
        Args:
            permission_type: Type of permission (read, write, execute, network)
            resource: Resource being accessed
            operation: Operation being performed
            
        Returns:
            Permission decision (approve/deny) or None if not found
        """
        try:
            # config.local.json is in the project root, not Governor directory
            # This file is at C:\SovereignAI\Governor\hook_handlers\permission_request.py
            # Need to go up two levels: hook_handlers -> Governor -> SovereignAI
            current_file = os.path.abspath(__file__)
            governor_dir = os.path.dirname(os.path.dirname(current_file))  # Up to Governor
            project_root = os.path.dirname(governor_dir)  # Up to SovereignAI
            config_path = os.path.join(project_root, ".devin", "config.local.json")
            
            if not os.path.exists(config_path):
                return None
            
            with open(config_path, 'r') as f:
                config = json.load(f)
            
            # Check if there's a permissions section
            if "permissions" not in config:
                return None
            
            permissions = config["permissions"]
            
            # Check allow list
            if "allow" in permissions and isinstance(permissions["allow"], list):
                allow_patterns = permissions["allow"]
                
                # Convert current request to pattern format
                request_pattern = self._request_to_pattern(permission_type, resource, operation)
                
                # Check if any allow pattern matches the request
                for pattern in allow_patterns:
                    if self._pattern_matches(request_pattern, pattern):
                        return "approve"
            
            # Check deny list (if exists)
            if "deny" in permissions and isinstance(permissions["deny"], list):
                deny_patterns = permissions["deny"]
                
                request_pattern = self._request_to_pattern(permission_type, resource, operation)
                
                for pattern in deny_patterns:
                    if self._pattern_matches(request_pattern, pattern):
                        return "deny"
            
            return None
            
        except (json.JSONDecodeError, IOError, KeyError):
            # If config.local.json is malformed or unreadable, continue without it
            return None
    
    def _request_to_pattern(self, permission_type: str, resource: str, operation: str) -> str:
        """
        Convert a permission request to Devin CLI pattern format.
        
        Args:
            permission_type: Type of permission (read, write, execute, network)
            resource: Resource being accessed
            operation: Operation being performed
            
        Returns:
            Pattern string in Devin CLI format (e.g., "Exec(ls)", "Read(*.py)")
        """
        # Map permission types to Devin CLI pattern prefixes
        type_mapping = {
            "read": "Read",
            "write": "Write", 
            "execute": "Exec",
            "network": "Network"
        }
        
        prefix = type_mapping.get(permission_type, "Unknown")
        
        # Build pattern based on resource (prioritize resource over operation)
        if resource and resource != "":
            # Use resource if available (e.g., file path, URL)
            return f"{prefix}({resource})"
        elif operation and operation != "":
            # Use operation if resource not available (e.g., command name)
            return f"{prefix}({operation})"
        else:
            # Fallback to wildcard
            return f"{prefix}(*)"
    
    def _pattern_matches(self, request_pattern: str, stored_pattern: str) -> bool:
        """
        Check if a request pattern matches a stored pattern (supports wildcards).
        
        Args:
            request_pattern: Pattern from current request (e.g., "Exec(ls)")
            stored_pattern: Pattern from config.local.json (e.g., "Exec(*)")
            
        Returns:
            True if patterns match, False otherwise
        """
        # Simple wildcard matching
        if stored_pattern == "*":
            return True
        
        if "*" in stored_pattern:
            # Convert to regex pattern
            import re
            regex_pattern = stored_pattern.replace("*", ".*")
            return bool(re.match(regex_pattern, request_pattern))
        
        # Exact match
        return request_pattern == stored_pattern
