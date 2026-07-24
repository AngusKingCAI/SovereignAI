#!/usr/bin/env python3
"""
PermissionDenied hook for PermissionDenied.
Handles tool calls denied by auto mode classifier and can retry them.
"""

import sys
import json
from pathlib import Path
from datetime import datetime

def main():
    """Handle permission denied events."""
    try:
        # Read event data from stdin
        data = sys.stdin.read()
        if data.strip():
            env_vars = json.loads(data)
        else:
            env_vars = {}
        
        # Extract tool information
        tool_name = env_vars.get('tool_name', 'unknown')
        
        # Log the permission denial
        log_file = Path("C:/SovereignAI/.claude/permission-denied.log")
        log_file.parent.mkdir(exist_ok=True)
        
        timestamp = datetime.now().isoformat()
        log_entry = f"[{timestamp}] Permission denied: {tool_name}\n"
        
        with open(log_file, 'a', encoding='utf-8') as f:
            f.write(log_entry)
        
        # Allow retry for safe operations
        if tool_name in ['read', 'grep']:
            output = {
                "hookSpecificOutput": {
                    "hookEventName": "PermissionDenied",
                    "retry": True
                }
            }
            print(json.dumps(output, indent=2))
        
        return 0
        
    except Exception as e:
        # Don't block operations even if hook fails
        return 0

if __name__ == "__main__":
    sys.exit(main())