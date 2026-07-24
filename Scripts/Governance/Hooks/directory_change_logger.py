#!/usr/bin/env python3
"""
Directory change logger hook for CwdChanged.
Logs working directory changes for tracking and debugging.
"""

import sys
import json
from pathlib import Path
from datetime import datetime

def main():
    """Log directory changes."""
    try:
        # Read event data from stdin
        data = sys.stdin.read()
        if data.strip():
            env_vars = json.loads(data)
        else:
            env_vars = {}
        
        # Extract directory information
        old_cwd = env_vars.get('old_cwd', 'unknown')
        new_cwd = env_vars.get('new_cwd', 'unknown')
        
        # Log the directory change
        log_file = Path("C:/SovereignAI/.claude/directory-changes.log")
        log_file.parent.mkdir(exist_ok=True)
        
        timestamp = datetime.now().isoformat()
        log_entry = f"[{timestamp}] Directory changed: {old_cwd} -> {new_cwd}\n"
        
        with open(log_file, 'a', encoding='utf-8') as f:
            f.write(log_entry)
        
        return 0
        
    except Exception as e:
        # Don't block operations even if logging fails
        return 0

if __name__ == "__main__":
    sys.exit(main())