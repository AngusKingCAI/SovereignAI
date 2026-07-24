#!/usr/bin/env python3
"""
Real-time activity logger hook for PostToolUse.
Logs all tool activities to the unified session file in real-time.
"""

import sys
import json
import os
from pathlib import Path
from datetime import datetime

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))
from hook_utils import get_verbosity, should_print, show_hook_header, show_hook_result

def log_tool_activity(tool_name, tool_input, tool_result, execution_time):
    """Log tool activity to the unified session file."""
    session_file = os.environ.get('DEVIN_SESSION_FILE')
    
    if not session_file:
        return False
    
    session_file_path = Path(session_file)
    if not session_file_path.exists():
        return False
    
    timestamp = datetime.now()
    
    try:
        with open(session_file_path, 'a', encoding='utf-8') as f:
            f.write(f"\n### Tool Execution: {tool_name}\n")
            f.write(f"**Timestamp**: {timestamp.isoformat()}\n")
            f.write(f"**Execution Time**: {execution_time:.3f}s\n\n")
            
            # Log tool input
            f.write("**Tool Input**:\n")
            f.write(f"```json\n{json.dumps(tool_input, indent=2)}\n```\n\n")
            
            # Log tool result (truncated if too long)
            f.write("**Tool Result**:\n")
            if isinstance(tool_result, str) and len(tool_result) > 2000:
                f.write(f"```\n{tool_result[:2000]}...\n```\n\n")
            else:
                f.write(f"```json\n{json.dumps(tool_result, indent=2)[:2000]}\n```\n\n")
            
            f.write("---\n")
        
        return True
    except Exception as e:
        return False

def read_transcript_content(transcript_path):
    """Read recent conversation content from transcript file."""
    try:
        if not transcript_path or not Path(transcript_path).exists():
            return None
        
        with open(transcript_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        # Get last few entries from transcript
        recent_entries = []
        for line in reversed(lines[-10:]):  # Last 10 entries
            if line.strip():
                try:
                    entry = json.loads(line)
                    role = entry.get('role', 'unknown')
                    content = entry.get('content', '')
                    if content:
                        recent_entries.append(f"{role.upper()}: {content[:200]}")  # Truncate long messages
                except:
                    continue
        
        return "\n".join(reversed(recent_entries)) if recent_entries else None
    except Exception as e:
        return None

def main():
    """Main real-time activity logger logic."""
    verbosity = get_verbosity()
    show_hook_header("Real-time Activity Logger", verbosity)
    
    # Get hook environment from stdin
    try:
        data = sys.stdin.read()
        if data:
            env_vars = json.loads(data)
        else:
            env_vars = {}
    except:
        env_vars = {}
    
    # Extract tool information
    tool_name = env_vars.get('tool_name', 'unknown')
    tool_input = env_vars.get('tool_input', {})
    tool_result = env_vars.get('tool_result', {})
    execution_time = env_vars.get('execution_time', 0.0)
    transcript_path = env_vars.get('transcript_path', '')
    
    # Log activity to unified session file
    success = log_tool_activity(tool_name, tool_input, tool_result, execution_time)
    
    if success:
        show_hook_result(f"Logged tool execution: {tool_name}", success=True, verbosity=verbosity)
        
        # Also log recent conversation context from transcript
        conversation_context = read_transcript_content(transcript_path)
        if conversation_context:
            session_file = os.environ.get('DEVIN_SESSION_FILE')
            if session_file:
                session_file_path = Path(session_file)
                if session_file_path.exists():
                    with open(session_file_path, 'a', encoding='utf-8') as f:
                        f.write(f"\n**Conversation Context**:\n")
                        f.write(f"```\n{conversation_context}\n```\n")
                        f.write("---\n")
    else:
        show_hook_result("No active session file - activity not logged", success=False, verbosity=verbosity)
    
    return 0

if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except Exception as e:
        print(f"Error in real-time activity logger: {e}", file=sys.stderr)
        sys.exit(1)
