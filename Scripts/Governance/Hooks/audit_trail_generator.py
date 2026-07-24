#!/usr/bin/env python3
"""
Audit Trail Generation Hook - PostToolUse
Automatically generates comprehensive audit trail entries for all operations
"""

import json
import sys
import os
import uuid
from pathlib import Path
from datetime import datetime
from typing import Dict, Optional

# Project root
PROJECT_ROOT = Path("C:/SovereignAI")


def get_current_agent() -> str:
    """Get current agent from config."""
    try:
        config_file = PROJECT_ROOT / ".devin" / "agent_config.json"
        if config_file.exists():
            with open(config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
            return config.get('current_agent', 'Architect')
    except Exception:
        pass
    return "Architect"


def get_session_id() -> str:
    """Get current session ID."""
    session_id = os.environ.get('DEVIN_SESSION_ID')
    if not session_id:
        session_id = str(uuid.uuid4())
    return session_id


def create_audit_entry(tool_name: str, tool_input: Dict, agent_type: str, session_id: str) -> Dict:
    """Create audit trail entry."""
    return {
        "timestamp": datetime.now().isoformat(),
        "session_id": session_id,
        "agent_type": agent_type,
        "tool_name": tool_name,
        "tool_input": tool_input,
        "operation_id": str(uuid.uuid4())
    }


def write_audit_trail(entry: Dict, agent_type: str):
    """Write audit trail entry to log file."""
    audit_dir = PROJECT_ROOT / "Logs" / agent_type / "Audit"
    audit_dir.mkdir(parents=True, exist_ok=True)
    
    audit_file = audit_dir / "audit-trail.jsonl"
    
    with open(audit_file, 'a', encoding='utf-8') as f:
        f.write(json.dumps(entry) + "\n")


def main():
    """Main hook execution."""
    try:
        # Read event data from stdin
        input_data = json.loads(sys.stdin.read())
        hook_event = input_data.get("hook_event_name", "PostToolUse")
        
        if hook_event != "PostToolUse":
            print(json.dumps({"hookSpecificOutput": {"hookEventName": hook_event}}))
            sys.exit(0)
        
        tool_name = input_data.get("tool_name", "")
        tool_input = input_data.get("tool_input", {})
        
        # Get agent and session information
        agent_type = get_current_agent()
        session_id = get_session_id()
        
        # Create audit entry
        audit_entry = create_audit_entry(tool_name, tool_input, agent_type, session_id)
        
        # Write to audit trail
        write_audit_trail(audit_entry, agent_type)
        
        print(json.dumps({"hookSpecificOutput": {"hookEventName": "PostToolUse"}}))
        sys.exit(0)
        
    except Exception as e:
        print(f"Audit trail generation error: {e}", file=sys.stderr)
        print(json.dumps({"hookSpecificOutput": {"hookEventName": "PostToolUse"}}))
        sys.exit(1)


if __name__ == "__main__":
    main()