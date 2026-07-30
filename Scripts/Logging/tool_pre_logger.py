"""Pre-tool logger - captures tool attempts before execution (Markdown format)."""

from __future__ import annotations

import json
import os
import sys
from datetime import datetime
from pathlib import Path

# Import session state and agent detection
sys.path.insert(0, str(Path(__file__).parent))
from session_state import read_agent_context, ensure_trace_context, get_trace_id


def determine_log_level(tool_name: str) -> str:
    """Determine appropriate log level based on tool."""
    if tool_name in ["exec", "write", "edit"]:
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
        "tool_name": entry.get('tool_name'),
        "status": entry.get('status'),
        "prompt_id": entry.get('prompt_id'),
        "working_directory": entry.get('working_directory'),
        "tool_input": entry.get('tool_input')
    }
    
    # Include tool_input if present (truncate large content)
    if 'tool_input' in entry:
        tool_input = entry['tool_input'].copy()
        # Truncate content fields to prevent massive JSON objects
        if 'content' in tool_input and len(str(tool_input['content'])) > 1000:
            tool_input['content'] = str(tool_input['content'])[:1000] + "... [truncated]"
        if 'old_string' in tool_input and len(str(tool_input['old_string'])) > 1000:
            tool_input['old_string'] = str(tool_input['old_string'])[:1000] + "... [truncated]"
        if 'new_string' in tool_input and len(str(tool_input['new_string'])) > 1000:
            tool_input['new_string'] = str(tool_input['new_string'])[:1000] + "... [truncated]"
        structured_entry["tool_input"] = tool_input
    
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
    # Read agent from session state, default to Architect if not found
    agent = read_agent_context(session_id) or "Architect"
    
    # Use environment-aware path for reliability
    current_path = Path(__file__).resolve()
    project_root = current_path.parent.parent.parent.resolve()
    log_dir = project_root / "Logs" / agent / "Session"
    log_dir.mkdir(parents=True, exist_ok=True)
    
    # Find existing session file with matching session_id (case-insensitive)
    try:
        session_name = session_id.title() if session_id else "Unknown"
        json_files = list(log_dir.glob(f"{agent}_*_{session_name}.json"))
        
        if json_files:
            json_files.sort(key=lambda f: f.stat().st_mtime, reverse=True)
            return json_files[0]
    except (OSError, IndexError):
        pass
    
    # Create new session file
    date_time = datetime.now().strftime("%d-%m-%y_%H-%M")
    session_name = session_id.title() if session_id else "Unknown"
    log_file = log_dir / f"{agent}_{date_time}_{session_name}.json"
    
    # Ensure trace context exists for session start
    trace_id = ensure_trace_context()
    
    # Create session start entry with trace context
    session_start_entry = {
        "event": "session_start",
        "timestamp": datetime.now().isoformat(),
        "session_id": session_id,
        "trace_id": trace_id,
        "agent": agent,
        "working_directory": os.getcwd(),
        "level": "INFO"
    }
    
    with open(log_file, 'a', encoding='utf-8', errors='replace') as f:
        # Write only structured JSON entry
        f.write(format_structured_entry(session_start_entry) + "\n")
    
    return log_file


def log_tool_pre() -> None:
    """Log tool attempt before execution with structured JSON format and markdown fallback."""
    try:
        data = json.load(sys.stdin)
    except (json.JSONDecodeError, ValueError) as e:
        print(f"❌ Failed to parse stdin JSON: {e}", file=sys.stderr)
        return
    
    session_id = data.get("session_id", "unknown")
    session_file = get_session_file(session_id)
    
    # Ensure trace context exists
    trace_id = ensure_trace_context()
    
    # Read agent from session state for logging
    agent = read_agent_context(session_id) or "Architect"
    
    # Extract tool information
    tool_name = data.get("tool_name", "unknown")
    tool_input = data.get("tool_input", {})
    
    # Determine log level
    log_level = determine_log_level(tool_name)
    
    # Create tool attempt entry with structured fields
    entry = {
        "event": "tool_attempt",
        "timestamp": datetime.now().isoformat(),
        "session_id": session_id,
        "trace_id": trace_id,
        "prompt_id": data.get("prompt_id", "unknown"),
        "agent": agent,
        "tool_name": tool_name,
        "tool_input": tool_input,
        "status": "attempt",
        "level": log_level,
        "working_directory": os.getcwd()
    }
    
    # Write only structured JSON entry
    with open(session_file, 'a', encoding='utf-8', errors='replace') as f:
        f.write(format_structured_entry(entry) + "\n")
    
    print(f"✅ Tool attempt logged: {tool_name} (Agent: {agent}, Level: {log_level})", file=sys.stderr)


if __name__ == "__main__":
    log_tool_pre()
