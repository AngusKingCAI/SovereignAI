"""Pre-tool logger - captures tool attempts before execution (Markdown format)."""

from __future__ import annotations

import json
import os
import sys
from datetime import datetime
from pathlib import Path


def format_readable_entry(entry: dict) -> str:
    """Format a log entry for maximum readability with markdown formatting."""
    formatted = []
    
    # Header with markdown
    formatted.append(f"### {entry.get('event', 'unknown').upper()}")
    formatted.append(f"**Timestamp**: {entry.get('timestamp', 'unknown')}")
    formatted.append(f"**Session**: {entry.get('session_id', 'unknown')}")
    
    if 'prompt_id' in entry:
        formatted.append(f"**Prompt ID**: {entry['prompt_id']}")
    
    if 'tool_name' in entry:
        formatted.append(f"**Tool**: {entry['tool_name']}")
        formatted.append(f"**Status**: {entry.get('status', 'unknown')}")
    
    formatted.append("")  # Empty line for separation
    
    # Tool-specific input formatting
    if 'tool_input' in entry:
        tool_name = entry.get('tool_name', 'unknown')
        tool_input = entry['tool_input']
        
        if tool_name == 'write':
            file_path = tool_input.get('file_path', 'unknown')
            content = tool_input.get('content', '')
            formatted.append(f"**Input Summary**: File: {file_path} ({len(content)} characters)")
            formatted.append(f"**Content** ({len(content)} chars):")
            formatted.append("```")
            formatted.append(content)
            formatted.append("```")
        elif tool_name == 'edit':
            file_path = tool_input.get('file_path', 'unknown')
            old_string = tool_input.get('old_string', '')
            new_string = tool_input.get('new_string', '')
            formatted.append(f"**Input Summary**: File: {file_path} (edit: {len(old_string)} -> {len(new_string)} chars)")
            formatted.append(f"**Old String** ({len(old_string)} chars):")
            formatted.append("```")
            formatted.append(old_string)
            formatted.append("```")
            formatted.append(f"**New String** ({len(new_string)} chars):")
            formatted.append("```")
            formatted.append(new_string)
            formatted.append("```")
        elif tool_name == 'read':
            file_path = tool_input.get('file_path', 'unknown')
            formatted.append(f"**Input Summary**: File: {file_path}")
            formatted.append(f"**Input**:")
            formatted.append("```")
            formatted.append(json.dumps(tool_input, indent=2))
            formatted.append("```")
        elif tool_name == 'exec':
            command = tool_input.get('command', '')
            formatted.append(f"**Input Summary**: Command: {command}")
            formatted.append(f"**Input**:")
            formatted.append("```")
            formatted.append(json.dumps(tool_input, indent=2))
            formatted.append("```")
        else:
            formatted.append(f"**Input**:")
            formatted.append("```")
            formatted.append(json.dumps(tool_input, indent=2))
            formatted.append("```")
        
        formatted.append("")
    
    if 'error' in entry and entry['error']:
        formatted.append(f"**Error**:")
        formatted.append("```")
        formatted.append(str(entry['error']))
        formatted.append("```")
        formatted.append("")
    
    formatted.append("---")
    formatted.append("")
    
    return "\n".join(formatted)


def get_session_file(session_id: str) -> Path:
    """Get or create the current session file."""
    log_dir = Path("Logs/Architect/Session")
    log_dir.mkdir(parents=True, exist_ok=True)
    
    # Find existing session file with matching session_id (case-insensitive)
    try:
        session_name = session_id.title() if session_id else "Unknown"
        md_files = list(log_dir.glob(f"Architect_*_{session_name}.md"))
        
        if md_files:
            md_files.sort(key=lambda f: f.stat().st_mtime, reverse=True)
            return md_files[0]
    except:
        pass
    
    # Create new session file
    agent = "Architect"
    date_time = datetime.now().strftime("%d-%m-%y_%H-%M")
    session_name = session_id.title() if session_id else "Unknown"
    log_file = log_dir / f"{agent}_{date_time}_{session_name}.md"
    
    # Create session start entry
    session_start_entry = {
        "event": "session_start",
        "timestamp": datetime.now().isoformat(),
        "session_id": session_id,
        "agent": agent,
        "working_directory": os.getcwd()
    }
    
    with open(log_file, 'a', encoding='utf-8') as f:
        f.write(format_readable_entry(session_start_entry))
    
    return log_file


def log_tool_pre() -> None:
    """Log tool attempt before execution."""
    try:
        data = json.load(sys.stdin)
    except:
        print("❌ Failed to parse stdin JSON", file=sys.stderr)
        return
    
    session_id = data.get("session_id", "unknown")
    session_file = get_session_file(session_id)
    
    # Extract tool information
    tool_name = data.get("tool_name", "unknown")
    tool_input = data.get("tool_input", {})
    
    # Create tool attempt entry
    entry = {
        "event": "tool_attempt",
        "timestamp": datetime.now().isoformat(),
        "session_id": session_id,
        "prompt_id": data.get("prompt_id", "unknown"),
        "tool_name": tool_name,
        "tool_input": tool_input,
        "status": "attempt"
    }
    
    with open(session_file, 'a', encoding='utf-8') as f:
        f.write(format_readable_entry(entry))
    
    print(f"✅ Tool attempt logged: {tool_name}", file=sys.stderr)


if __name__ == "__main__":
    log_tool_pre()
