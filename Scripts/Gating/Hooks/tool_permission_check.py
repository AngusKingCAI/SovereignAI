#!/usr/bin/env python3
"""
PreToolUse Hook - Validate tool permissions against current phase
"""

import sys
import json
import os
from pathlib import Path

def get_project_root():
    """Get project root directory."""
    return Path("C:/SovereignAI")

def load_session_context():
    """Load current session context."""
    project_root = get_project_root()
    session_file = project_root / "Logs" / "Architect" / "Gating" / "session-context.json"
    
    if session_file.exists():
        with open(session_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    return None

def load_phase_permissions():
    """Load phase permissions configuration."""
    project_root = get_project_root()
    config_file = project_root / "Scripts" / "Gating" / "Config" / "phase_permissions.json"
    
    if config_file.exists():
        with open(config_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def check_tool_permission(tool_name, file_path, current_phase, phase_permissions):
    """Check if tool operation is allowed in current phase."""
    phase_key = f"phase_{current_phase}"
    
    if phase_key not in phase_permissions:
        # Default to deny if phase not defined
        return False, f"Phase {current_phase} not defined in permissions"
    
    phase_config = phase_permissions[phase_key]
    
    # Allow Scripts/Gating/ operations to avoid circular dependency
    if file_path and "Scripts/Gating/" in str(file_path):
        return True, "Allowed: Hook maintenance operation"
    
    # Check if tool is allowed
    allowed_tools = phase_config.get("allowed_tools", [])
    if tool_name not in allowed_tools:
        return False, f"Tool '{tool_name}' not allowed in phase {current_phase}"
    
    # Check file operations if file_path provided
    if file_path:
        # Determine operation type based on tool name
        operation_type = None
        if tool_name in ["write", "edit"]:
            operation_type = "modify"
        elif tool_name == "exec":
            # Check if command contains delete operations
            exec_command = str(file_path).lower()
            if any(cmd in exec_command for cmd in ["rm ", "rmdir ", "del ", "remove"]):
                operation_type = "delete"
        
        # Check forbidden operations based on operation type
        forbidden_ops = phase_config.get("forbidden_operations", [])
        for forbidden in forbidden_ops:
            if forbidden.startswith("modify:") and operation_type == "modify" and file_path.startswith(forbidden[7:]):
                return False, f"Modification of {forbidden[7:]} forbidden in phase {current_phase}"
            elif forbidden.startswith("delete:") and operation_type == "delete":
                if forbidden[7:] == "*" or file_path.startswith(forbidden[7:]):
                    return False, f"Deletion operations forbidden in phase {current_phase}"
        
        # Check allowed file operations
        allowed_ops = phase_config.get("allowed_file_operations", [])
        operation_allowed = False
        for allowed in allowed_ops:
            if allowed.startswith("read:*"):
                operation_allowed = True
                break
            elif allowed.startswith("modify:") and operation_type == "modify" and file_path.startswith(allowed[7:]):
                operation_allowed = True
                break
            elif allowed.startswith("create:") and operation_type == "modify" and file_path.startswith(allowed[7:]):
                operation_allowed = True
                break
        
        if not operation_allowed:
            return False, f"File operation on {file_path} not allowed in phase {current_phase}"
    
    return True, "Permission granted"

def check_phase_completion(current_phase, phase_permissions):
    """Check if required previous phases are complete."""
    phase_key = f"phase_{current_phase}"
    
    if phase_key not in phase_permissions:
        return True, []  # Can't check if phase not defined
    
    phase_config = phase_permissions[phase_key]
    required_completions = phase_config.get("required_completions", [])
    
    incomplete_phases = []
    for required_phase in required_completions:
        # Check if required phase state file exists and is complete
        project_root = get_project_root()
        state_file = project_root / "Logs" / "Architect" / "Gating" / f"{required_phase}-state.json"
        
        if not state_file.exists():
            incomplete_phases.append(required_phase)
        else:
            with open(state_file, 'r', encoding='utf-8') as f:
                state_data = json.load(f)
                if state_data.get("metadata", {}).get("implementation_status") != "complete":
                    incomplete_phases.append(required_phase)
    
    if incomplete_phases:
        return False, incomplete_phases
    
    return True, []

def read_stdin():
    """Read JSON data from stdin."""
    try:
        data = sys.stdin.read()
        if data:
            return json.loads(data)
    except json.JSONDecodeError:
        pass
    return {}

def main():
    """Main hook function."""
    try:
        # Read event data from stdin
        event_data = read_stdin()
        
        # Extract tool information
        tool_name = event_data.get('tool_name', '')
        tool_input = event_data.get('tool_input', {})
        
        # Get file path from tool input if available
        file_path = None
        command = None
        if 'file_path' in tool_input:
            file_path = tool_input['file_path']
        elif 'path' in tool_input:
            file_path = tool_input['path']
        elif 'command' in tool_input:
            command = tool_input['command']
        
        # Load session context
        session_context = load_session_context()
        if not session_context:
            print("Error: No session context found", file=sys.stderr)
            sys.exit(2)
        
        current_phase = session_context.get('current_phase', '0')
        
        # Load phase permissions
        phase_permissions = load_phase_permissions()
        if not phase_permissions:
            print("Error: Phase permissions configuration not found", file=sys.stderr)
            sys.exit(2)
        
        # Check phase completion prerequisites
        phase_complete, incomplete_phases = check_phase_completion(current_phase, phase_permissions)
        if not phase_complete:
            print(f"Permission denied: Required phases not complete: {incomplete_phases}", file=sys.stderr)
            sys.exit(2)
        
        # Check tool permission
        # Use command for exec operations, file_path for others
        check_target = command if tool_name == "exec" and command else file_path
        permission_allowed, message = check_tool_permission(tool_name, check_target, current_phase, phase_permissions)
        
        if not permission_allowed:
            print(f"Permission denied: {message}", file=sys.stderr)
            sys.exit(2)
        
        # Permission granted
        print(f"Permission granted: {tool_name} in phase {current_phase}")
        sys.exit(0)
        
    except Exception as e:
        print(f"Permission check failed: {str(e)}", file=sys.stderr)
        sys.exit(2)

if __name__ == "__main__":
    main()
