#!/usr/bin/env python3
"""
Task hooks for TaskCreated and TaskCompleted.
Tracks task creation and completion.
"""

import sys
import json
from pathlib import Path
from datetime import datetime

def main():
    """Track task events."""
    try:
        # Read event data from stdin
        data = sys.stdin.read()
        if data.strip():
            env_vars = json.loads(data)
        else:
            env_vars = {}
        
        # Get hook event from stdin data
        hook_event = env_vars.get('hook_event_name', 'TaskCreated')
        
        # Extract task information
        task_id = env_vars.get('task_id', 'unknown')
        task_content = env_vars.get('task_content', '')
        
        # Log the task event
        log_file = Path("C:/SovereignAI/.claude/task-events.log")
        log_file.parent.mkdir(exist_ok=True)
        
        timestamp = datetime.now().isoformat()
        log_entry = f"[{timestamp}] Task {hook_event}: {task_id}\n"
        log_entry += f"Content: {task_content[:100]}{'...' if len(task_content) > 100 else ''}\n"
        
        with open(log_file, 'a', encoding='utf-8') as f:
            f.write(log_entry)
        
        return 0
        
    except Exception as e:
        # Don't block operations even if logging fails
        return 0

if __name__ == "__main__":
    sys.exit(main())