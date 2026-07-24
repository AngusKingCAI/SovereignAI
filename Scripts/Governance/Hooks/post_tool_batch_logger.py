#!/usr/bin/env python3
"""
PostToolBatch hook for PostToolBatch.
Logs after a full batch of parallel tool calls resolves.
"""

import sys
import json
from pathlib import Path
from datetime import datetime

def main():
    """Log tool batch completion."""
    try:
        # Read event data from stdin
        data = sys.stdin.read()
        if data.strip():
            env_vars = json.loads(data)
        else:
            env_vars = {}
        
        # Extract batch information
        batch_results = env_vars.get('batch_results', [])
        
        # Log the batch completion
        log_file = Path("C:/SovereignAI/.claude/tool-batches.log")
        log_file.parent.mkdir(exist_ok=True)
        
        timestamp = datetime.now().isoformat()
        log_entry = f"[{timestamp}] Tool batch completed: {len(batch_results)} tools\n"
        
        with open(log_file, 'a', encoding='utf-8') as f:
            f.write(log_entry)
        
        return 0
        
    except Exception as e:
        # Don't block operations even if logging fails
        return 0

if __name__ == "__main__":
    sys.exit(main())