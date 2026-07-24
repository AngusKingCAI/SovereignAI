#!/usr/bin/env python3
"""
Worktree hooks for WorktreeCreate and WorktreeRemove.
Handles git worktree creation and removal.
"""

import sys
import json
from pathlib import Path
from datetime import datetime

def main():
    """Handle worktree events."""
    try:
        # Read event data from stdin
        data = sys.stdin.read()
        if data.strip():
            env_vars = json.loads(data)
        else:
            env_vars = {}
        
        # Get hook event from stdin data
        hook_event = env_vars.get('hook_event_name', 'WorktreeCreate')
        
        # Extract worktree information
        worktree_path = env_vars.get('worktree_path', 'unknown')
        
        # Log the worktree event
        log_file = Path("C:/SovereignAI/.claude/worktree-events.log")
        log_file.parent.mkdir(exist_ok=True)
        
        timestamp = datetime.now().isoformat()
        log_entry = f"[{timestamp}] Worktree {hook_event}: {worktree_path}\n"
        
        with open(log_file, 'a', encoding='utf-8') as f:
            f.write(log_entry)
        
        return 0
        
    except Exception as e:
        # Don't block operations even if logging fails
        return 0

if __name__ == "__main__":
    sys.exit(main())