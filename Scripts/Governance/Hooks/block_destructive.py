#!/usr/bin/env python3
"""
Block destructive commands hook for PreToolUse.
Prevents dangerous commands like rm -rf from executing.
"""

import sys
import json

def main():
    """Block destructive commands."""
    try:
        # Read event data from stdin
        data = sys.stdin.read()
        if data.strip():
            env_vars = json.loads(data)
        else:
            env_vars = {}
        
        # Check if this is an exec command
        tool_name = env_vars.get('tool_name', '')
        if tool_name != 'exec':
            return 0  # Not an exec command, allow
        
        # Get the command
        tool_input = env_vars.get('tool_input', {})
        command = tool_input.get('command', '')
        
        # Check for destructive patterns
        destructive_patterns = ['rm -rf', 'rm -rf /', 'del /f /s /q', 'format', 'mkfs']
        
        for pattern in destructive_patterns:
            if pattern in command:
                # Block the command
                output = {
                    "hookSpecificOutput": {
                        "hookEventName": "PreToolUse",
                        "permissionDecision": "deny",
                        "permissionDecisionReason": f"Destructive command blocked by hook: contains '{pattern}'"
                    }
                }
                print(json.dumps(output, indent=2))
                return 2  # Exit code 2 blocks the action
        
        return 0  # Allow the command
        
    except Exception as e:
        # On error, allow the command to avoid blocking legitimate actions
        return 0

if __name__ == "__main__":
    sys.exit(main())