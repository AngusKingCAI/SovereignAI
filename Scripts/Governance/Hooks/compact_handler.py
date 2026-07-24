#!/usr/bin/env python3
"""
Compact hooks for PreCompact and PostCompact.
Handles context compaction events.
"""

import sys
import json
from pathlib import Path
from datetime import datetime

def main():
    """Handle compact events."""
    try:
        # Read event data from stdin
        data = sys.stdin.read()
        if data.strip():
            env_vars = json.loads(data)
        else:
            env_vars = {}
        
        # Get hook event from stdin data
        hook_event = env_vars.get('hook_event_name', 'PreCompact')
        
        # Extract compact information
        summary = env_vars.get('summary', '')
        
        # Log the compact event
        log_file = Path("C:/SovereignAI/.claude/compact-events.log")
        log_file.parent.mkdir(exist_ok=True)
        
        timestamp = datetime.now().isoformat()
        log_entry = f"[{timestamp}] Compact {hook_event}\n"
        if summary:
            log_entry += f"Summary: {summary[:100]}\n"
        
        with open(log_file, 'a', encoding='utf-8') as f:
            f.write(log_entry)
        
        return 0
        
    except Exception as e:
        # Don't block operations even if logging fails
        return 0

if __name__ == "__main__":
    sys.exit(main())