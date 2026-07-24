#!/usr/bin/env python3
"""
Transcript monitor hook for comprehensive conversation logging.
Monitors the Devin CLI transcript file and captures all conversation activity in real-time.
"""

import sys
import json
import os
from pathlib import Path
from datetime import datetime
import time

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))
from hook_utils import get_verbosity, should_print, show_hook_header, show_hook_result

def log_conversation_from_transcript(transcript_path, session_file):
    """Read and log all conversation from transcript file."""
    try:
        if not transcript_path or not Path(transcript_path).exists():
            return False
        
        with open(transcript_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        timestamp = datetime.now()
        
        with open(session_file, 'a', encoding='utf-8') as f:
            f.write(f"\n### Full Conversation from Transcript\n")
            f.write(f"**Timestamp**: {timestamp.isoformat()}\n")
            f.write(f"**Source**: {transcript_path}\n\n")
            
            for line in lines:
                if line.strip():
                    try:
                        entry = json.loads(line)
                        role = entry.get('role', 'unknown')
                        content = entry.get('content', '')
                        
                        if content:
                            f.write(f"**{role.upper()}**:\n")
                            f.write(f"{content}\n\n")
                    except:
                        continue
            
            f.write("---\n")
        
        return True
    except Exception as e:
        return False

def main():
    """Main transcript monitor logic."""
    verbosity = get_verbosity()
    show_hook_header("Transcript Monitor", verbosity)
    
    # Get hook environment from stdin
    try:
        data = sys.stdin.read()
        if data:
            env_vars = json.loads(data)
        else:
            env_vars = {}
    except:
        env_vars = {}
    
    # Get transcript path and session file
    transcript_path = env_vars.get('transcript_path', '')
    session_file = os.environ.get('DEVIN_SESSION_FILE')
    
    if not session_file:
        show_hook_result("No active session file", success=False, verbosity=verbosity)
        return 0
    
    if not transcript_path:
        show_hook_result("No transcript path available", success=False, verbosity=verbosity)
        return 0
    
    # Log conversation from transcript
    success = log_conversation_from_transcript(transcript_path, session_file)
    
    if success:
        show_hook_result("Logged conversation from transcript", success=True, verbosity=verbosity)
    else:
        show_hook_result("Failed to log conversation from transcript", success=False, verbosity=verbosity)
    
    return 0

if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except Exception as e:
        print(f"Error in transcript monitor: {e}", file=sys.stderr)
        sys.exit(1)