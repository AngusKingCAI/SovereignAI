#!/usr/bin/env python3
"""
MessageDisplay hook for MessageDisplay.
Logs when assistant message text is displayed.
"""

import sys
import json
from pathlib import Path
from datetime import datetime

def main():
    """Log message display events."""
    try:
        # Read event data from stdin
        data = sys.stdin.read()
        if data.strip():
            env_vars = json.loads(data)
        else:
            env_vars = {}
        
        # Extract message information
        message_text = env_vars.get('message_text', '')
        
        # Log the message display
        log_file = Path("C:/SovereignAI/.claude/message-display.log")
        log_file.parent.mkdir(exist_ok=True)
        
        timestamp = datetime.now().isoformat()
        log_entry = f"[{timestamp}] Message displayed: {len(message_text)} characters\n"
        
        with open(log_file, 'a', encoding='utf-8') as f:
            f.write(log_entry)
        
        return 0
        
    except Exception as e:
        # Don't block operations even if logging fails
        return 0

if __name__ == "__main__":
    sys.exit(main())