#!/usr/bin/env python3
"""
Instructions logger hook for InstructionsLoaded.
Logs when CLAUDE.md or .claude/rules/*.md files are loaded.
"""

import sys
import json
from pathlib import Path
from datetime import datetime

def main():
    """Log instructions loading."""
    try:
        # Read event data from stdin
        data = sys.stdin.read()
        if data.strip():
            env_vars = json.loads(data)
        else:
            env_vars = {}
        
        # Extract file information
        file_path = env_vars.get('file_path', 'unknown')
        
        # Log the instructions loading
        log_file = Path("C:/SovereignAI/.claude/instructions-loaded.log")
        log_file.parent.mkdir(exist_ok=True)
        
        timestamp = datetime.now().isoformat()
        log_entry = f"[{timestamp}] Instructions loaded: {file_path}\n"
        
        with open(log_file, 'a', encoding='utf-8') as f:
            f.write(log_entry)
        
        return 0
        
    except Exception as e:
        # Don't block operations even if logging fails
        return 0

if __name__ == "__main__":
    sys.exit(main())