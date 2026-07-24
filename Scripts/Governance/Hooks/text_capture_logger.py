#!/usr/bin/env python3
"""
Text capture logger hook for capturing user messages and thinking.
Logs all text interactions to the unified session file in real-time.
"""

import sys
import json
import os
from pathlib import Path
from datetime import datetime

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))
from hook_utils import get_verbosity, should_print, show_hook_header, show_hook_result

def log_text_interaction(message_type, content, sender="AI"):
    """Log text interaction to the unified session file."""
    session_file = os.environ.get('DEVIN_SESSION_FILE')
    
    if not session_file:
        return False
    
    session_file_path = Path(session_file)
    if not session_file_path.exists():
        return False
    
    timestamp = datetime.now()
    
    try:
        with open(session_file_path, 'a', encoding='utf-8') as f:
            f.write(f"\n### {message_type}\n")
            f.write(f"**Timestamp**: {timestamp.isoformat()}\n")
            f.write(f"**Sender**: {sender}\n\n")
            f.write(f"{content}\n")
            f.write("---\n")
        
        return True
    except Exception as e:
        return False

def main():
    """Main text capture logger logic."""
    verbosity = get_verbosity()
    show_hook_header("Text Capture Logger", verbosity)
    
    # This hook is designed to be called manually or via other mechanisms
    # For now, we'll implement a simple version that logs from stdin
    try:
        data = sys.stdin.read()
        if data:
            try:
                env_vars = json.loads(data)
                message_type = env_vars.get('message_type', 'Message')
                content = env_vars.get('content', '')
                sender = env_vars.get('sender', 'AI')
                
                success = log_text_interaction(message_type, content, sender)
                
                if success:
                    show_hook_result(f"Logged {message_type}", success=True, verbosity=verbosity)
                else:
                    show_hook_result("No active session file - text not logged", success=False, verbosity=verbosity)
            except:
                # Treat as raw text content
                success = log_text_interaction("User Message", data, "User")
                
                if success:
                    show_hook_result("Logged user message", success=True, verbosity=verbosity)
                else:
                    show_hook_result("No active session file - text not logged", success=False, verbosity=verbosity)
        else:
            show_hook_result("No content to log", success=True, verbosity=verbosity)
    except Exception as e:
        show_hook_result(f"Error logging text: {e}", success=False, verbosity=verbosity)
    
    return 0

if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except Exception as e:
        print(f"Error in text capture logger: {e}", file=sys.stderr)
        sys.exit(1)
