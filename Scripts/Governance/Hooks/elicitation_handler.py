#!/usr/bin/env python3
"""
Elicitation hooks for Elicitation and ElicitationResult.
Handles MCP server user input requests and responses.
"""

import sys
import json
from pathlib import Path
from datetime import datetime

def main():
    """Handle elicitation events."""
    try:
        # Read event data from stdin
        data = sys.stdin.read()
        if data.strip():
            env_vars = json.loads(data)
        else:
            env_vars = {}
        
        # Get hook event from stdin data
        hook_event = env_vars.get('hook_event_name', 'Elicitation')
        
        # Extract elicitation information
        mcp_server_name = env_vars.get('mcp_server_name', 'unknown')
        elicitation_id = env_vars.get('elicitation_id', 'unknown')
        
        # Log the elicitation event
        log_file = Path("C:/SovereignAI/.claude/elicitation-events.log")
        log_file.parent.mkdir(exist_ok=True)
        
        timestamp = datetime.now().isoformat()
        log_entry = f"[{timestamp}] Elicitation {hook_event}: {mcp_server_name} ({elicitation_id})\n"
        
        with open(log_file, 'a', encoding='utf-8') as f:
            f.write(log_entry)
        
        return 0
        
    except Exception as e:
        # Don't block operations even if logging fails
        return 0

if __name__ == "__main__":
    sys.exit(main())