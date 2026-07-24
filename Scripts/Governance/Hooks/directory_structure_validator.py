#!/usr/bin/env python3
"""
Directory structure validation hook for PreToolUse.
Validates directory structure compliance before directory operations.
"""

import sys
import json
import os
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))
from hook_utils import get_verbosity, should_print, show_hook_header, show_hook_result, show_hook_error, show_hook_error_details

def validate_directory_structure(target_path):
    """Validate directory structure compliance."""
    project_root = Path("C:/SovereignAI")
    
    # Define mandatory directories
    mandatory_dirs = {
        "Agents",
        "Rules", 
        "Workflow",
        "Scripts",
        "Logs",
        "Docs"
    }
    
    # Define allowed directories at root level
    allowed_root_dirs = mandatory_dirs | {
        "App",
        ".devin",
        ".git",
        ".claude",
        ".windsurf"
    }
    
    target_path = Path(target_path).resolve()
    
    # Check if operation is within project root
    try:
        target_path.relative_to(project_root)
    except ValueError:
        return False, f"Path {target_path} is outside C:/SovereignAI directory"
    
    # Check if this is a root-level directory operation
    relative_path = target_path.relative_to(project_root)
    
    # If creating a directory directly under project root
    if len(relative_path.parts) == 1:
        dir_name = relative_path.parts[0]
        
        # Check if it's an allowed root directory
        if dir_name not in allowed_root_dirs:
            return False, f"Directory {dir_name} is not allowed at project root. Allowed directories: {sorted(allowed_root_dirs)}"
    
    # Check for proper nesting in mandatory directories
    for mandatory_dir in mandatory_dirs:
        if str(relative_path).startswith(mandatory_dir):
            # Verify the mandatory directory exists
            mandatory_path = project_root / mandatory_dir
            if not mandatory_path.exists():
                return False, f"Mandatory directory {mandatory_dir} does not exist"
    
    return True, "Directory structure validation passed"

def main():
    """Main directory structure validation logic."""
    verbosity = get_verbosity()
    show_hook_header("Directory Structure Validation", verbosity)
    
    # Get hook environment from stdin
    try:
        data = sys.stdin.read()
        if data:
            env_vars = json.loads(data)
        else:
            env_vars = {}
    except:
        env_vars = {}
    
    # Extract file path from tool input
    tool_input = env_vars.get('tool_input', {})
    file_path = tool_input.get('file_path', '')
    
    # If this is a directory creation operation
    if not file_path:
        show_hook_result("No file path provided, allowing operation", success=True, verbosity=verbosity)
        return 0
    
    # Validate directory structure
    allowed, message = validate_directory_structure(file_path)
    
    show_hook_result(f"Validation result: {message}", success=allowed, verbosity=verbosity)
    
    if not allowed:
        show_hook_error("Directory structure validation failed - operation blocked", verbosity)
        show_hook_error_details(f"Directory structure validation failed - operation blocked", verbosity)
        # Return permission decision to block
        output = {
            "hookSpecificOutput": {
                "hookEventName": "PreToolUse",
                "permissionDecision": "deny",
                "permissionDecisionReason": message
            }
        }
        print(json.dumps(output, indent=2))
        return 2  # Block the operation
    
    show_hook_result("Directory structure validation passed", success=True, verbosity=verbosity)
    return 0  # Allow the operation

if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except Exception as e:
        print(f"Error in directory structure validation: {e}", file=sys.stderr)
        sys.exit(1)
