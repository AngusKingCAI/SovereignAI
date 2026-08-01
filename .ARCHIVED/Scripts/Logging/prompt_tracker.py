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
from session_state import write_agent_context, ensure_trace_context, get_trace_id
from agent_detector import detect_agent_from_prompt


def determine_log_level(event: str) -> str:
    """Determine appropriate log level based on event type."""
    if event == "session_start":
        return "INFO"
    if event == "user_prompt":
        return "INFO"
    return "DEBUG"


def format_structured_entry(entry: dict) -> str:
    """Format log entry as structured JSON with standard fields."""
    structured_entry = {
        "timestamp": entry.get('timestamp'),
        "level": entry.get('level', 'INFO'),
        "service": "devin-cli",
        "event": entry.get('event'),
        "session_id": entry.get('session_id'),
        "trace_id": entry.get('trace_id'),
        "agent": entry.get('agent'),
        "prompt_id": entry.get('prompt_id'),
        "working_directory": entry.get('working_directory'),
        "prompt": entry.get('prompt')
    }
    
    return json.dumps(structured_entry, ensure_ascii=False)


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
    """Track user prompt with structured JSON format and markdown fallback."""
    try:
        data = json.load(sys.stdin)
    except (json.JSONDecodeError, ValueError) as e:
        print(f"❌ Failed to parse stdin JSON: {e}", file=sys.stderr)
        return
    
    session_id = data.get("session_id", "unknown")
    prompt = data.get("prompt", "")
    timestamp = datetime.now().isoformat()
    
    # Ensure trace context exists
    trace_id = ensure_trace_context()
    
    # Detect agent from prompt content
    agent = detect_agent_from_prompt(prompt)
    
    # Store agent context in session state for other hooks to use
    write_agent_context(agent)
    
    # Create log directory based on detected agent (use environment-aware path)
    current_path = Path(__file__).resolve()
    project_root = current_path.parent.parent.parent.resolve()
    log_dir = project_root / "Logs" / agent / "Session"
    log_dir.mkdir(parents=True, exist_ok=True)
    
    # Use Agent_Date_Time_Session naming format with .jsonl extension
    date_time = datetime.now().strftime("%d-%m-%y_%H-%M")
    # Capitalize session name (first letter of each word)
    session_name = session_id.title() if session_id else "Unknown"
    
    # Find existing session file with matching session_id (case-insensitive)
    try:
        # Look for .jsonl files for the detected agent
        jsonl_files = list(log_dir.glob(f"{agent}_*_{session_name}.jsonl"))
        
        if jsonl_files:
            # Sort by date to get the most recent
            jsonl_files.sort(key=lambda f: f.stat().st_mtime, reverse=True)
            log_file = jsonl_files[0]
        else:
            log_file = log_dir / f"{agent}_{date_time}_{session_name}.jsonl"
    except (OSError, IndexError):
        log_file = log_dir / f"{agent}_{date_time}_{session_name}.jsonl"
    
    # Create session start entry if this is the first prompt
    if not log_file.exists():
        session_start_entry = {
            "event": "session_start",
            "timestamp": timestamp,
            "session_id": session_id,
            "trace_id": trace_id,
            "agent": agent,
            "working_directory": os.getcwd(),
            "level": "INFO"
        }
        with open(log_file, 'a', encoding='utf-8', errors='replace') as f:
            # Write only structured JSON entry
            f.write(format_structured_entry(session_start_entry) + "\n")
    
    # Create prompt entry with structured fields
    log_level = determine_log_level("user_prompt")
    entry = {
        "event": "user_prompt",
        "timestamp": timestamp,
        "session_id": session_id,
        "trace_id": trace_id,
        "prompt_id": data.get("prompt_id", "unknown"),
        "prompt": prompt,
        "level": log_level,
        "agent": agent,
        "working_directory": os.getcwd()
    }
    
    # Write only structured JSON entry
    with open(log_file, 'a', encoding='utf-8', errors='replace') as f:
        f.write(format_structured_entry(entry) + "\n")
    
    print(f"✅ Prompt tracked: {session_id} (Agent: {agent}, Level: {log_level})", file=sys.stderr)


if __name__ == "__main__":
    track_prompt()