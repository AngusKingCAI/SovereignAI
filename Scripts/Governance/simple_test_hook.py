#!/usr/bin/env python3
"""
Simple test hook to verify Devin CLI hook system is working.
"""

import sys
import json
from datetime import datetime

def main():
    """Simple test hook that logs to a file."""
    # Read stdin (hook event data)
    try:
        data = sys.stdin.read()
        if data.strip():
            event_data = json.loads(data)
        else:
            event_data = {}
    except:
        event_data = {}
    
    # Log to test file
    timestamp = datetime.now().isoformat()
    hook_event = event_data.get('hook_event_name', 'Unknown')
    
    log_entry = f"[{timestamp}] Hook: {hook_event}\n"
    
    with open("C:/SovereignAI/hook_test.log", 'a') as f:
        f.write(log_entry)
    
    print(f"Test hook executed: {hook_event}")
    return 0

if __name__ == "__main__":
    sys.exit(main())