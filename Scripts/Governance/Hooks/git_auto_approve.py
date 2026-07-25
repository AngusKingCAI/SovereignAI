#!/usr/bin/env python3
"""
Git Auto-Approve Hook - PermissionRequest
Auto-approves local git commands but requires permission for push, pull, and restore operations
"""
import json
import sys

def main():
    """Auto-approve local git commands, require permission for push."""
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
        
        # Require permission for git push, pull, and restore operations
        if tool_name == 'exec' and command.startswith('git '):
            if 'push' in command or 'pull' in command or 'restore' in command:
                # Don't return anything for these operations to require user permission
                sys.exit(0)
            else:
                # Auto-approve local git operations
                output = {
                    "decision": "approve",
                    "reason": "Local git command auto-approved for development workflow"
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