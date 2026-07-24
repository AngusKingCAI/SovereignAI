#!/usr/bin/env python3
"""
StopFailure hook for StopFailure.
Logs when the turn ends due to an API error.
"""

import sys
import json
from pathlib import Path
from datetime import datetime

def main():
    """Log stop failure events."""
    try:
        # Read event data from stdin
        data = sys.stdin.read()
        if data.strip():
            env_vars = json.loads(data)
        else:
            env_vars = {}
        
        # Log the stop failure
        log_file = Path("C:/SovereignAI/.claude/stop-failures.log")
        log_file.parent.mkdir(exist_ok=True)
        
        timestamp = datetime.now().isoformat()
        log_entry = f"[{timestamp}] Stop failure event\n"
        
        with open(log_file, 'a', encoding='utf-8') as f:
            f.write(log_entry)
        
        return 0
        
    except Exception as e:
        # Don't block operations even if logging fails
        return 0

if __name__ == "__main__":
    sys.exit(main())