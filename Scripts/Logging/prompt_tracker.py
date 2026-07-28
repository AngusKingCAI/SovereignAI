"""Simple prompt tracker - captures user prompts only."""

from __future__ import annotations

import json
import os
import sys
import textwrap
from datetime import datetime
from pathlib import Path

# Import session state and agent detection
sys.path.insert(0, str(Path(__file__).parent))
from session_state import write_agent_context
from agent_detector import detect_agent_from_prompt


def format_readable_entry(entry: dict) -> str:
    """Format a log entry for maximum readability with markdown formatting."""
    formatted = []
    
    # Header with markdown
    formatted.append(f"### {entry.get('event', 'unknown').upper()}")
    formatted.append(f"**Timestamp**: {entry.get('timestamp', 'unknown')}")
    formatted.append(f"**Session**: {entry.get('session_id', 'unknown')}")
    
    if 'prompt_id' in entry:
        formatted.append(f"**Prompt ID**: {entry['prompt_id']}")
    
    if 'agent' in entry:
        formatted.append(f"**Agent**: {entry['agent']}")
    
    if 'working_directory' in entry:
        formatted.append(f"**Working Directory**: {entry['working_directory']}")
    
    formatted.append("")  # Empty line for separation
    
    # Prompt content with markdown
    if 'prompt' in entry:
        formatted.append(f"**Prompt**:")
        formatted.append("```")
        formatted.append(str(entry['prompt']))
        formatted.append("```")
        formatted.append("")
    
    formatted.append("---")
    formatted.append("")
    
    return "\n".join(formatted)


def track_prompt() -> None:
    """Track user prompt with basic context."""
    try:
        data = json.load(sys.stdin)
    except:
        print("❌ Failed to parse stdin JSON", file=sys.stderr)
        return
    
    session_id = data.get("session_id", "unknown")
    prompt = data.get("prompt", "")
    timestamp = datetime.now().isoformat()
    
    # Detect agent from prompt content
    agent = detect_agent_from_prompt(prompt)
    
    # Store agent context in session state for other hooks to use
    write_agent_context(session_id, agent)
    
    # Create log directory based on detected agent
    log_dir = Path(f"Logs/{agent}/Session")
    log_dir.mkdir(parents=True, exist_ok=True)
    
    # Use Agent_Date_Time_Session naming format
    date_time = datetime.now().strftime("%d-%m-%y_%H-%M")
    # Capitalize session name (first letter of each word)
    session_name = session_id.title() if session_id else "Unknown"
    
    # Find existing session file with matching session_id (case-insensitive)
    try:
        # Look for .md files for the detected agent
        md_files = list(log_dir.glob(f"{agent}_*_{session_name}.md"))
        
        if md_files:
            # Sort by date to get the most recent
            md_files.sort(key=lambda f: f.stat().st_mtime, reverse=True)
            log_file = md_files[0]
        else:
            log_file = log_dir / f"{agent}_{date_time}_{session_name}.md"
    except:
        log_file = log_dir / f"{agent}_{date_time}_{session_name}.md"
    
    # Create session start entry if this is the first prompt
    if not log_file.exists():
        session_start_entry = {
            "event": "session_start",
            "timestamp": timestamp,
            "session_id": session_id,
            "agent": agent,
            "working_directory": os.getcwd()
        }
        with open(log_file, 'a', encoding='utf-8') as f:
            f.write(format_readable_entry(session_start_entry))
    
    # Create prompt entry with readable formatting
    entry = {
        "event": "user_prompt",
        "timestamp": timestamp,
        "session_id": session_id,
        "prompt_id": data.get("prompt_id", "unknown"),
        "prompt": prompt
    }
    
    with open(log_file, 'a', encoding='utf-8') as f:
        f.write(format_readable_entry(entry))
    
    print(f"✅ Prompt tracked: {session_id} (Agent: {agent})", file=sys.stderr)


if __name__ == "__main__":
    track_prompt()