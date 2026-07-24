#!/usr/bin/env python3
"""
Skill boundary enforcement hook for PreToolUse.
Enforces skill-specific boundaries and restrictions before tool execution.
"""

import sys
import json
import os
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))
from hook_utils import get_verbosity, should_print, show_hook_header, show_hook_result, show_hook_error, show_hook_error_details

def enforce_skill_boundaries(tool_name, tool_input, current_skill):
    """Enforce skill-specific boundaries based on tool and agent."""
    project_root = Path("C:/SovereignAI")
    
    # Define skill-specific boundaries
    skill_boundaries = {
        "architect": {
            "allowed_directories": ["Agents", "Rules", "Workflow", "Scripts", "Logs", "Docs"],
            "forbidden_directories": ["App"],
            "allowed_operations": ["read", "write", "edit", "grep", "find_file_by_name"],
            "forbidden_operations": ["exec destructive commands"],
            "allowed_file_patterns": ["*.md", "*.json", "*.py"],
            "scope_note": "Infrastructure design only, no application code"
        },
        "executor": {
            "allowed_directories": ["App", "Scripts/src", "Scripts/tests"],
            "forbidden_directories": ["Agents", "Rules", "Workflow", "Docs"],
            "allowed_operations": ["read", "write", "edit", "exec", "grep"],
            "forbidden_operations": ["git push", "production deployment"],
            "allowed_file_patterns": ["*.py", "*.js", "*.ts", "*.json"],
            "scope_note": "Application code execution only"
        },
        "planner": {
            "allowed_directories": ["Workflow", "Docs"],
            "forbidden_directories": ["App", "Scripts/src"],
            "allowed_operations": ["read", "write", "edit", "grep"],
            "forbidden_operations": ["exec build commands"],
            "allowed_file_patterns": ["*.md", "*.json"],
            "scope_note": "Planning and documentation only"
        },
        "researcher": {
            "allowed_directories": ["Docs", "Agents"],
            "forbidden_directories": ["App", "Scripts/src"],
            "allowed_operations": ["read", "web_search", "grep"],
            "forbidden_operations": ["write to production files"],
            "allowed_file_patterns": ["*.md", "*.txt", "*.json"],
            "scope_note": "Research and documentation only"
        },
        "reviewer": {
            "allowed_directories": ["Logs", "Workflow", "Agents"],
            "forbidden_directories": ["App", "Scripts/src"],
            "allowed_operations": ["read", "grep"],
            "forbidden_operations": ["write to source files"],
            "allowed_file_patterns": ["*.md", "*.json", "*.jsonl"],
            "scope_note": "Review and verification only"
        }
    }
    
    # If no skill specified, allow everything
    if not current_skill or current_skill not in skill_boundaries:
        return True, "No skill boundary enforcement"
    
    boundaries = skill_boundaries[current_skill]
    
    # Check directory access
    file_path = tool_input.get('file_path', '')
    if file_path:
        file_path = Path(file_path)
        
        # Check forbidden directories
        for forbidden_dir in boundaries['forbidden_directories']:
            if forbidden_dir in str(file_path):
                return False, f"Skill {current_skill} cannot access {forbidden_dir}/ directory: {boundaries['scope_note']}"
        
        # Check allowed directories
        if boundaries['allowed_directories']:
            in_allowed_dir = any(dir in str(file_path) for dir in boundaries['allowed_directories'])
            if not in_allowed_dir:
                return False, f"Skill {current_skill} can only access: {', '.join(boundaries['allowed_directories'])}"
    
    # Check operation restrictions
    if tool_name == "exec":
        command = tool_input.get('command', '')
        if command:
            for forbidden_op in boundaries['forbidden_operations']:
                if forbidden_op in command.lower():
                    return False, f"Skill {current_skill} cannot perform: {forbidden_op}"
    
    return True, f"Skill {current_skill} boundary check passed"

def main():
    """Main skill boundary enforcement logic."""
    verbosity = get_verbosity()
    show_hook_header("Skill Boundary Enforcement", verbosity)
    
    # Get hook environment from stdin
    try:
        data = sys.stdin.read()
        if data:
            env_vars = json.loads(data)
        else:
            env_vars = {}
    except:
        env_vars = {}
    
    # Extract current skill from environment (set by skill invocation)
    current_skill = os.environ.get('DEVIN_CURRENT_SKILL', '')
    
    # Extract tool information
    tool_name = env_vars.get('tool_name', '')
    tool_input = env_vars.get('tool_input', {})
    
    # Enforce boundaries
    allowed, message = enforce_skill_boundaries(tool_name, tool_input, current_skill)
    
    show_hook_result(f"Boundary check: {message}", success=allowed, verbosity=verbosity)
    
    if not allowed:
        show_hook_error("Skill boundary violation - operation blocked", verbosity)
        show_hook_error_details(f"Skill boundary violation - operation blocked", verbosity)
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
    
    return 0  # Allow the operation

if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except Exception as e:
        print(f"Error in skill boundary enforcement: {e}", file=sys.stderr)
        sys.exit(1)
