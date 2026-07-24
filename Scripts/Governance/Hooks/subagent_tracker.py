#!/usr/bin/env python3
"""
Subagent hooks for SubagentStart and SubagentStop.
Tracks subagent spawning and completion.
"""

import sys
import json
from pathlib import Path
from datetime import datetime

def main():
    """Track subagent events."""
    try:
        # Read event data from stdin
        data = sys.stdin.read()
        if data.strip():
            env_vars = json.loads(data)
        else:
            env_vars = {}
        
        # Get hook event from stdin data
        hook_event = env_vars.get('hook_event_name', 'SubagentStart')
        
        # Extract subagent information
        agent_id = env_vars.get('agent_id', 'unknown')
        agent_type = env_vars.get('agent_type', 'unknown')
        
        # Log the subagent event
        log_file = Path("C:/SovereignAI/.claude/subagent-events.log")
        log_file.parent.mkdir(exist_ok=True)
        
        timestamp = datetime.now().isoformat()
        log_entry = f"[{timestamp}] Subagent {hook_event}: {agent_type} ({agent_id})\n"
        
        with open(log_file, 'a', encoding='utf-8') as f:
            f.write(log_entry)
        
        return 0
        
    except Exception as e:
        # Don't block operations even if logging fails
        return 0

if __name__ == "__main__":
    sys.exit(main())