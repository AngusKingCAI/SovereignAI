#!/usr/bin/env python3
"""
FileChanged hook for FileChanged.
Watches for file changes on disk.
"""

import sys
import json
from pathlib import Path
from datetime import datetime

def main():
    """Watch file changes."""
    try:
        # Read event data from stdin
        data = sys.stdin.read()
        if data.strip():
            env_vars = json.loads(data)
        else:
            env_vars = {}
        
        # Extract file information
        file_path = env_vars.get('file_path', 'unknown')
        change_type = env_vars.get('change_type', 'unknown')
        
        # Log the file change
        log_file = Path("C:/SovereignAI/.claude/file-changes.log")
        log_file.parent.mkdir(exist_ok=True)
        
        timestamp = datetime.now().isoformat()
        log_entry = f"[{timestamp}] File {change_type}: {file_path}\n"
        
        with open(log_file, 'a', encoding='utf-8') as f:
            f.write(log_entry)
        
        return 0
        
    except Exception as e:
        # Don't block operations even if logging fails
        return 0

if __name__ == "__main__":
    sys.exit(main())