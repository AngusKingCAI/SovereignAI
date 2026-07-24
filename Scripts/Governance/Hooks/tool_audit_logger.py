#!/usr/bin/env python3
"""
Tool audit logger hook for PostToolUse.
Creates an audit trail of every tool call for compliance or debugging.
"""

import sys
import json
import os
from pathlib import Path
from datetime import datetime

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

def format_content_readable(content):
    """Format content in a readable way without truncation."""
    if isinstance(content, str):
        return content
    else:
        return json.dumps(content, indent=2)

def summarize_tool_input(tool_name, tool_input):
    """Create a readable summary of tool input."""
    if tool_name == 'write':
        file_path = tool_input.get('file_path', 'unknown')
        content_length = len(tool_input.get('content', ''))
        return f"File: {file_path} ({content_length} characters)"
    elif tool_name == 'edit':
        file_path = tool_input.get('file_path', 'unknown')
        old_length = len(tool_input.get('old_string', ''))
        new_length = len(tool_input.get('new_string', ''))
        return f"File: {file_path} (edit: {old_length} -> {new_length} chars)"
    elif tool_name == 'read':
        file_path = tool_input.get('file_path', 'unknown')
        return f"File: {file_path}"
    elif tool_name == 'exec':
        command = tool_input.get('command', '')
        return f"Command: {command}"
    else:
        return f"Input: {json.dumps(tool_input, indent=2)}"

def log_tool_use(tool_name, tool_input, tool_result):
    """Log tool use to the unified session file with full content display."""
    session_file = get_current_session_file()
    
    if not session_file:
        return False
    
    session_file_path = Path(session_file)
    if not session_file_path.exists():
        return False
    
    timestamp = datetime.now()
    
    try:
        with open(session_file_path, 'a', encoding='utf-8') as f:
            f.write(f"\n### Tool Use: {tool_name}\n")
            f.write(f"**Timestamp**: {timestamp.isoformat()}\n")
            f.write(f"**Tool**: {tool_name}\n")
            
            # Use summary for certain tools, then show full content
            if tool_name in ['write', 'edit', 'read', 'exec']:
                summary = summarize_tool_input(tool_name, tool_input)
                f.write(f"**Input Summary**: {summary}\n")
                
                # Show full content for all operations
                if tool_name == 'edit':
                    old_string = tool_input.get('old_string', '')
                    new_string = tool_input.get('new_string', '')
                    f.write(f"**Old String** ({len(old_string)} chars):\n```\n{old_string}\n```\n")
                    f.write(f"**New String** ({len(new_string)} chars):\n```\n{new_string}\n```\n")
                elif tool_name == 'write':
                    content = tool_input.get('content', '')
                    f.write(f"**Content** ({len(content)} chars):\n```\n{content}\n```\n")
                else:
                    # For read and exec, show the full input
                    f.write(f"**Input**:\n```\n{format_content_readable(tool_input)}\n```\n")
            else:
                f.write(f"**Input**:\n```\n{format_content_readable(tool_input)}\n```\n")
            
            f.write(f"**Result**:\n```\n{format_content_readable(tool_result)}\n```\n")
            f.write("---\n")
        return True
    except Exception:
        return False

def main():
    """Log all tool calls to audit trail."""
    try:
        # Read event data from stdin
        data = sys.stdin.read()
        if data.strip():
            env_vars = json.loads(data)
        else:
            env_vars = {}
        
        # Extract tool information
        tool_name = env_vars.get('tool_name', 'unknown')
        tool_input = env_vars.get('tool_input', {})
        tool_result = env_vars.get('tool_result', {})
        
        # Log to unified session file with improved formatting
        log_tool_use(tool_name, tool_input, tool_result)
        
        # Also create audit log entry for compliance
        timestamp = datetime.now().isoformat()
        log_entry = {
            "timestamp": timestamp,
            "tool_name": tool_name,
            "tool_input": tool_input,
            "success": tool_result.get('success', True)
        }
        
        # Write to audit log
        log_file = Path("C:/SovereignAI/.claude/tool-audit.log")
        log_file.parent.mkdir(exist_ok=True)
        
        with open(log_file, 'a', encoding='utf-8') as f:
            f.write(json.dumps(log_entry) + "\n")
        
        return 0
        
    except Exception as e:
        # Don't block operations even if logging fails
        return 0

if __name__ == "__main__":
    sys.exit(main())