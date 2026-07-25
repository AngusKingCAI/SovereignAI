#!/usr/bin/env python3
"""
SessionStart Hook - Initialize governance environment and load current phase state
"""

import sys
import json
import os
from pathlib import Path
from datetime import datetime
import uuid

def get_project_root():
    """Get project root directory."""
    return Path("C:/SovereignAI")

def load_phase_permissions():
    """Load phase permissions configuration."""
    project_root = get_project_root()
    config_file = project_root / "Scripts" / "Gating" / "Config" / "phase_permissions.json"
    
    if config_file.exists():
        with open(config_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def get_current_phase_state():
    """Get current phase state from state files."""
    project_root = get_project_root()
    state_dir = project_root / "Logs" / "Architect" / "Gating"
    
    if not state_dir.exists():
        return None
    
    # Find the most recent phase state file
    state_files = list(state_dir.glob("phase-*-state.json"))
    if state_files:
        # Sort by modification time and get the most recent
        latest_file = max(state_files, key=lambda f: f.stat().st_mtime)
        with open(latest_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    return None

def create_session_context():
    """Create session context for current session."""
    session_id = str(uuid.uuid4())
    timestamp = datetime.now().isoformat()
    
    # Get current phase state
    phase_state = get_current_phase_state()
    current_phase = phase_state.get("phase", "0") if phase_state else "0"
    
    session_context = {
        "session_id": session_id,
        "timestamp": timestamp,
        "current_phase": current_phase,
        "project_root": str(get_project_root()),
        "state_directory": str(get_project_root() / "Logs" / "Architect" / "Gating"),
        "environment_valid": True,
        "operation_counters": {
            "read": 0,
            "write": 0,
            "edit": 0,
            "exec": 0
        }
    }
    
    return session_context

def save_session_context(session_context):
    """Save session context to file."""
    project_root = get_project_root()
    session_file = project_root / "Logs" / "Architect" / "Gating" / "session-context.json"
    
    # Ensure directory exists
    session_file.parent.mkdir(parents=True, exist_ok=True)
    
    with open(session_file, 'w', encoding='utf-8') as f:
        json.dump(session_context, f, indent=2)

def initialize_audit_log(session_context):
    """Initialize audit log for current session."""
    project_root = get_project_root()
    audit_log_file = project_root / "Logs" / "Architect" / "Gating" / "audit-trail.log"
    
    # Ensure directory exists
    audit_log_file.parent.mkdir(parents=True, exist_ok=True)
    
    # Write session start entry
    timestamp = datetime.now().isoformat()
    log_entry = f"[{timestamp}] SESSION_START: session_id={session_context['session_id']}, phase={session_context['current_phase']}\n"
    
    with open(audit_log_file, 'a', encoding='utf-8') as f:
        f.write(log_entry)

def read_stdin():
    """Read JSON data from stdin."""
    try:
        data = sys.stdin.read()
        if data:
            return json.loads(data)
    except json.JSONDecodeError:
        pass
    return {}

def main():
    """Main hook function."""
    try:
        # Read event data from stdin
        event_data = read_stdin()
        hook_event = event_data.get('hook_event_name', 'SessionStart')
        
        # Load phase permissions
        phase_permissions = load_phase_permissions()
        if not phase_permissions:
            print("Warning: Phase permissions configuration not found", file=sys.stderr)
        
        # Create session context
        session_context = create_session_context()
        
        # Save session context
        save_session_context(session_context)
        
        # Initialize audit log
        initialize_audit_log(session_context)
        
        # Output success message
        print(f"Session initialized: {session_context['session_id']}, Phase: {session_context['current_phase']}")
        
        # Return success
        sys.exit(0)
        
    except Exception as e:
        print(f"Session initialization failed: {str(e)}", file=sys.stderr)
        sys.exit(2)

if __name__ == "__main__":
    main()
