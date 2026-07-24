#!/usr/bin/env python3
"""
Notification hook for Notification.
Logs Claude Code notifications for tracking and debugging.
"""

import sys
import json
from pathlib import Path
from datetime import datetime

def main():
    """Log notifications."""
    try:
        # Read event data from stdin
        data = sys.stdin.read()
        if data.strip():
            env_vars = json.loads(data)
        else:
            env_vars = {}
        
        # Extract notification information
        notification_type = env_vars.get('notification_type', 'unknown')
        message = env_vars.get('message', '')
        
        # Log the notification
        log_file = Path("C:/SovereignAI/.claude/notifications.log")
        log_file.parent.mkdir(exist_ok=True)
        
        timestamp = datetime.now().isoformat()
        log_entry = f"[{timestamp}] Notification ({notification_type}): {message[:100]}\n"
        
        with open(log_file, 'a', encoding='utf-8') as f:
            f.write(log_entry)
        
        return 0
        
    except Exception as e:
        # Don't block operations even if logging fails
        return 0

if __name__ == "__main__":
    sys.exit(main())