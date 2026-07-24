#!/usr/bin/env python3
"""
Chat capture hook for UserPromptSubmit and Stop events.
Captures user messages and reads transcript for AI responses to the unified session file.
"""

import sys
import json
import os
from pathlib import Path
from datetime import datetime

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))
from hook_utils import get_verbosity, should_print, show_hook_header, show_hook_result

def get_current_session_file():
    """Get current session file from config or environment."""
    # First try environment variable
    session_file = os.environ.get('DEVIN_SESSION_FILE')
    if session_file:
        return session_file
    
    # Fallback: read from agent config to find latest session
    try:
        project_root = Path("C:/SovereignAI")
        config_file = project_root / ".devin" / "agent_config.json"
        
        if config_file.exists():
            with open(config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            current_agent = config.get('current_agent', 'Architect')
            logs_dir = project_root / "Logs" / current_agent
            
            if logs_dir.exists():
                # Find the most recent session file
                session_files = list(logs_dir.glob("*.md"))
                if session_files:
                    # Sort by modification time and get the most recent
                    latest_file = max(session_files, key=lambda f: f.stat().st_mtime)
                    return str(latest_file)
    except Exception:
        pass
    
    return None

def log_chat_event(event_type, content, sender="System", metadata=None):
    """Log chat events to the unified session file."""
    session_file = get_current_session_file()
    
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

def read_transcript_last_ai_message(transcript_path):
    """Read the last AI message from the transcript file."""
    try:
        if not transcript_path or not Path(transcript_path).exists():
            return None
        
        with open(transcript_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        # Look for the last assistant message in the transcript
        # Transcript format is JSONL, so we need to parse lines
        last_ai_message = None
        for line in reversed(lines):
            if line.strip():
                try:
                    entry = json.loads(line)
                    if entry.get('role') == 'assistant':
                        content = entry.get('content', '')
                        if content:
                            last_ai_message = content
                            break
                except:
                    continue
        
        return last_ai_message
    except Exception as e:
        return None

def main():
    """Main chat capture hook logic."""
    verbosity = get_verbosity()
    show_hook_header("Chat Capture Hook", verbosity)
    
    # Get hook environment from stdin
    try:
        data = sys.stdin.read()
        if data.strip():
            env_vars = json.loads(data)
        else:
            env_vars = {}
    except Exception as e:
        show_hook_result(f"Error reading stdin: {e}", success=False, verbosity=verbosity)
        env_vars = {}
    
    # Get hook event from stdin data (Devin CLI passes event in JSON, not env var)
    hook_event = env_vars.get('hook_event_name', 'Unknown')
    
    # Extract event-specific information based on hook event type
    if hook_event == 'UserPromptSubmit':
        # Capture user message
        prompt = env_vars.get('prompt', '')
        session_id = env_vars.get('session_id', 'unknown')
        
        if prompt:
            success = log_chat_event("User Message", prompt, "User", {
                "session_id": session_id,
                "event": "UserPromptSubmit"
            })
            
            if success:
                show_hook_result("Logged user message", success=True, verbosity=verbosity)
            else:
                show_hook_result("No active session file - message not logged", success=False, verbosity=verbosity)
        else:
            show_hook_result("No user message content to log", success=True, verbosity=verbosity)
    
    elif hook_event == 'Stop':
        # Capture turn completion and read transcript for AI response
        session_id = env_vars.get('session_id', 'unknown')
        transcript_path = env_vars.get('transcript_path', '')
        
        # Read the last AI message from transcript
        ai_message = read_transcript_last_ai_message(transcript_path)
        
        if ai_message:
            success = log_chat_event("AI Response", ai_message, "Assistant", {
                "session_id": session_id,
                "event": "Stop",
                "transcript_source": True
            })
            
            if success:
                show_hook_result("Logged AI response from transcript", success=True, verbosity=verbosity)
            else:
                show_hook_result("No active session file - AI response not logged", success=False, verbosity=verbosity)
        else:
            # Fallback: log turn completion without AI content
            success = log_chat_event("Turn Completed", "Turn finished (no AI content available in transcript)", "System", {
                "session_id": session_id,
                "event": "Stop",
                "transcript_source": False
            })
            
            if success:
                show_hook_result("Logged turn completion", success=True, verbosity=verbosity)
            else:
                show_hook_result("No active session file - turn completion not logged", success=False, verbosity=verbosity)
    
    else:
        show_hook_result(f"Unknown hook event: {hook_event}", success=False, verbosity=verbosity)
    
    return 0

if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except Exception as e:
        print(f"Error in chat capture hook: {e}", file=sys.stderr)
        sys.exit(1)