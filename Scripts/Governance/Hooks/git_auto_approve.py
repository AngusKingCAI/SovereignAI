#!/usr/bin/env python3
"""
Git Auto-Approve Hook - PermissionRequest
Auto-approves git commands to prevent blocking development workflow
"""
import json
import sys

def main():
    """Auto-approve git commands."""
    try:
        # Read event data from stdin
        data = sys.stdin.read()
        if data.strip():
            env_vars = json.loads(data)
        else:
            env_vars = {}
        
        tool_name = env_vars.get('tool_name', '')
        tool_input = env_vars.get('tool_input', {})
        command = tool_input.get('command', '')
        
        # Auto-approve git commands
        if tool_name == 'exec' and command.startswith('git '):
            output = {
                "decision": "approve",
                "reason": "Git command auto-approved for development workflow"
            }
            print(json.dumps(output))
            sys.exit(0)
        
        # Allow other tools to proceed normally
        sys.exit(0)
        
    except Exception as e:
        print(f"Git auto-approve error: {e}", file=sys.stderr)
        sys.exit(0)  # Don't block on error

if __name__ == "__main__":
    main()