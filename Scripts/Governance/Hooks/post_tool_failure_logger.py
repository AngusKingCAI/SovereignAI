#!/usr/bin/env python3
"""
PostToolUseFailure logger hook for PostToolUseFailure.
Logs tool failures for debugging and error tracking.
"""

import sys
import json
from pathlib import Path
from datetime import datetime

def main():
    """Log tool failures."""
    try:
        # Read event data from stdin
        data = sys.stdin.read()
        if data.strip():
            env_vars = json.loads(data)
        else:
            env_vars = {}
        
        # Extract tool information
        tool_name = env_vars.get('tool_name', 'unknown')
        tool_input = env_vars.get('tool_input', {})
        tool_response = env_vars.get('tool_response', {})
        
        # Log the failure
        log_file = Path("C:/SovereignAI/.claude/tool-failures.log")
        log_file.parent.mkdir(exist_ok=True)
        
        timestamp = datetime.now().isoformat()
        log_entry = f"[{timestamp}] Tool failure: {tool_name}\n"
        log_entry += f"Input: {json.dumps(tool_input, indent=2)[:200]}\n"
        log_entry += f"Response: {json.dumps(tool_response, indent=2)[:200]}\n"
        log_entry += "---\n"
        
        with open(log_file, 'a', encoding='utf-8') as f:
            f.write(log_entry)
        
        return 0
        
    except Exception as e:
        # Don't block operations even if logging fails
        return 0

if __name__ == "__main__":
    sys.exit(main())