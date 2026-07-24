#!/usr/bin/env python3
"""
Everything capture hook for comprehensive logging.
Captures all chat interactions, tool executions, and AI thinking to agent-specific session files.
This hook is designed to be called from multiple integration points.
"""

import sys
import json
import os
from pathlib import Path
from datetime import datetime

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))
from hook_utils import get_verbosity, should_print, show_hook_header, show_hook_result

def log_everything(event_type, content, sender="System", metadata=None):
    """Log everything to the agent-specific session file."""
    session_file = os.environ.get('DEVIN_SESSION_FILE')
    
    if not session_file:
        return False
    
    session_file_path = Path(session_file)
    if not session_file_path.exists():
        return False
    
    timestamp = datetime.now()
    
    try:
        with open(session_file_path, 'a', encoding='utf-8') as f:
            f.write(f"\n### {event_type}\n")
            f.write(f"**Timestamp**: {timestamp.isoformat()}\n")
            f.write(f"**Sender**: {sender}\n")
            
            if metadata:
                f.write(f"**Metadata**: {json.dumps(metadata, indent=2)}\n")
            
            f.write(f"\n{content}\n")
            f.write("---\n")
        
        return True
    except Exception as e:
        return False

def main():
    """Main everything capture hook logic."""
    verbosity = get_verbosity()
    show_hook_header("Everything Capture Hook", verbosity)
    
    # This hook captures everything from stdin
    try:
        data = sys.stdin.read()
        if data:
            try:
                # Try to parse as JSON for structured data
                env_vars = json.loads(data)
                event_type = env_vars.get('event_type', 'Event')
                content = env_vars.get('content', '')
                sender = env_vars.get('sender', 'System')
                metadata = env_vars.get('metadata', {})
                
                success = log_everything(event_type, content, sender, metadata)
                
                if success:
                    show_hook_result(f"Logged {event_type} from {sender}", success=True, verbosity=verbosity)
                else:
                    show_hook_result("No active session file - event not logged", success=False, verbosity=verbosity)
            except:
                # Treat as raw text content
                success = log_everything("Raw Content", data, "System")
                
                if success:
                    show_hook_result("Logged raw content", success=True, verbosity=verbosity)
                else:
                    show_hook_result("No active session file - content not logged", success=False, verbosity=verbosity)
        else:
            show_hook_result("No content to log", success=True, verbosity=verbosity)
    except Exception as e:
        show_hook_result(f"Error logging event: {e}", success=False, verbosity=verbosity)
    
    return 0

if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except Exception as e:
        print(f"Error in everything capture hook: {e}", file=sys.stderr)
        sys.exit(1)
