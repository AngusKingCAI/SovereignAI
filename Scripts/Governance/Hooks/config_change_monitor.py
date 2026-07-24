#!/usr/bin/env python3
"""
Config change monitor hook for ConfigChange.
Logs configuration file changes for tracking and debugging.
"""

import sys
import json
from pathlib import Path
from datetime import datetime

def main():
    """Monitor configuration changes."""
    try:
        # Read event data from stdin
        data = sys.stdin.read()
        if data.strip():
            env_vars = json.loads(data)
        else:
            env_vars = {}
        
        # Extract config change information
        config_file = env_vars.get('config_file', 'unknown')
        change_type = env_vars.get('change_type', 'unknown')
        
        # Log the change
        log_file = Path("C:/SovereignAI/.claude/config-changes.log")
        log_file.parent.mkdir(exist_ok=True)
        
        timestamp = datetime.now().isoformat()
        log_entry = f"[{timestamp}] Config {change_type}: {config_file}\n"
        
        with open(log_file, 'a', encoding='utf-8') as f:
            f.write(log_entry)
        
        return 0
        
    except Exception as e:
        # Don't block operations even if logging fails
        return 0

if __name__ == "__main__":
    sys.exit(main())