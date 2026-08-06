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
        1. Extracts permission request details from payload
        2. Checks config.local.json for saved permission decisions
        3. Checks Governor's permission registry for saved decisions
        4. Applies auto-approve/deny logic based on policy
        5. Implements escalation for sensitive operations
        6. Saves permission decision to Governor's state if user made a choice
        7. Sets permissionDecision field
        8. Returns protocol-compliant response
        
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
        
        # Check if user has already made a decision for this request
        # First check config.local.json (Devin CLI's permission storage)
        user_decision = self._check_config_local_permissions(permission_type, resource, operation)
        
        # Then check Governor's permission registry
        if user_decision is None:
            user_decision = state_machine.get_permission_decision(permission_type, resource, operation)
        
        # Apply auto-approve/deny logic if no user decision found
        if user_decision is None:
            permission_decision = self._evaluate_permission(
                permission_type, resource, operation, current_phase, state_machine
            )
            # This is an auto-decision from Governor's policy
            # Save to config.local.json for persistence so Governor's decisions are remembered
            if permission_decision == "approve":
                self._save_permission_to_config(permission_type, resource, operation, permission_decision)
            # Also save to Governor state for session tracking
            state_machine.add_permission(
                permission_type=permission_type,
                resource=resource,
                operation=operation,
                decision=permission_decision,
                scope="session",
                reason="Governor auto-decision"
            )
        else:
            permission_decision = user_decision
            # This is a user decision from config.local.json, save to Governor state for this session
            state_machine.add_permission(
                permission_type=permission_type,
                resource=resource,
                operation=operation,
                decision=permission_decision,
                scope="session",
                reason="User decision from config.local.json"
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
        
        IMPORTANT: When Governor makes an auto-decision, we should NOT interfere
        with Devin CLI's normal permission flow. We should return "approve" to let
        Devin CLI handle the permission window and user choice.
        
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
        
        # For most cases, return "approve" to let Devin CLI handle permission windows
        # Governor's job is to enforce rules, not to replace user permission choices
        # The only exceptions are cases where we need to deny for security reasons
        
        # Auto-deny for dangerous operations in early phases
        if permission_type in ["network"] and current_phase in ["INIT", "RESEARCH"]:
            return "deny"
        
        # For all other cases, approve to let Devin CLI handle permission windows
        # This allows the user to make their own choices and have them saved to config.local.json
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
    
    def _save_permission_to_config(self, permission_type: str, resource: str, 
                                   operation: str, decision: str) -> None:
        """
        Save a permission decision to config.local.json in Devin CLI format.
        
        Args:
            permission_type: Type of permission (read, write, execute, network)
            resource: Resource being accessed
            operation: Operation being performed
            decision: Permission decision (approve/deny)
        """
        try:
            # config.local.json is in the project root, not Governor directory
            # This file is at C:\SovereignAI\Governor\hook_handlers\permission_request.py
            # Need to go up two levels: hook_handlers -> Governor -> SovereignAI
            current_file = os.path.abspath(__file__)
            governor_dir = os.path.dirname(os.path.dirname(current_file))  # Up to Governor
            project_root = os.path.dirname(governor_dir)  # Up to SovereignAI
            config_path = os.path.join(project_root, ".devin", "config.local.json")
            
            # Load existing config or create new
            if os.path.exists(config_path):
                with open(config_path, 'r') as f:
                    config = json.load(f)
            else:
                config = {}
            
            # Ensure permissions section exists
            if "permissions" not in config:
                config["permissions"] = {}
            
            # Convert request to pattern
            pattern = self._request_to_pattern(permission_type, resource, operation)
            
            # Save to appropriate list (allow or deny)
            if decision == "approve":
                if "allow" not in config["permissions"]:
                    config["permissions"]["allow"] = []
                
                # Add if not already present
                if pattern not in config["permissions"]["allow"]:
                    config["permissions"]["allow"].append(pattern)
            
            elif decision == "deny":
                if "deny" not in config["permissions"]:
                    config["permissions"]["deny"] = []
                
                # Add if not already present
                if pattern not in config["permissions"]["deny"]:
                    config["permissions"]["deny"].append(pattern)
            
            # Write back to file
            with open(config_path, 'w') as f:
                json.dump(config, f, indent=2)
                
        except (json.JSONDecodeError, IOError) as e:
            # If config.local.json cannot be written, continue without error
            pass
