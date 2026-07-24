#!/usr/bin/env python3
"""
Auto-approve safe operations hook for PermissionRequest.
Automatically approves safe read and grep operations to reduce friction.
"""

import sys
import json

def main():
    """Auto-approve safe operations."""
    try:
        # Read event data from stdin
        data = sys.stdin.read()
        if data.strip():
            env_vars = json.loads(data)
        else:
            env_vars = {}
        
        # Extract tool information
        tool_name = env_vars.get('tool_name', 'unknown')
        
        # Auto-approve read and grep operations
        if tool_name in ['read', 'grep']:
            output = {
                "hookSpecificOutput": {
                    "hookEventName": "PermissionRequest",
                    "permissionDecision": "allow",
                    "permissionDecisionReason": f"Auto-approved safe {tool_name} operation"
                }
            }
            print(json.dumps(output, indent=2))
        
        return 0
        
    except Exception as e:
        # Don't block operations even if auto-approve fails
        return 0

if __name__ == "__main__":
    sys.exit(main())