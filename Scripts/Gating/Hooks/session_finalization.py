#!/usr/bin/env python3
"""
SessionEnd Hook - Final validation and session cleanup
"""

import sys
import json
from pathlib import Path
from datetime import datetime

def get_project_root():
    """Get project root directory."""
    return Path("C:/SovereignAI")

def load_session_context():
    """Load current session context."""
    project_root = get_project_root()
    session_file = project_root / "Logs" / "Architect" / "Gating" / "session-context.json"
    
    if session_file.exists():
        with open(session_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    return None

def generate_session_summary(session_context):
    """Generate session completion summary."""
    session_id = session_context.get('session_id', 'unknown')
    current_phase = session_context.get('current_phase', 'unknown')
    timestamp = session_context.get('timestamp', 'unknown')
    operation_counters = session_context.get('operation_counters', {})
    
    summary = {
        "session_id": session_id,
        "start_time": timestamp,
        "end_time": datetime.now().isoformat(),
        "current_phase": current_phase,
        "operations": operation_counters,
        "status": "completed"
    }
    
    return summary

def log_session_end_to_audit_trail(session_context, session_summary):
    """Log session end to audit trail."""
    project_root = get_project_root()
    audit_log_file = project_root / "Logs" / "Architect" / "Gating" / "audit-trail.log"
    
    timestamp = datetime.now().isoformat()
    session_id = session_context.get('session_id', 'unknown')
    current_phase = session_context.get('current_phase', 'unknown')
    
    # Format the log entry
    log_entry = f"[{timestamp}] SESSION_END: session_id={session_id}, phase={current_phase}, operations={session_summary['operations']}, status={session_summary['status']}\n"
    
    with open(audit_log_file, 'a', encoding='utf-8') as f:
        f.write(log_entry)

def save_session_summary(session_summary):
    """Save session summary to file."""
    project_root = get_project_root()
    summary_file = project_root / "Logs" / "Architect" / "Gating" / f"session-{session_summary['session_id']}.json"
    
    with open(summary_file, 'w', encoding='utf-8') as f:
        json.dump(session_summary, f, indent=2)

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
        
        # Load session context
        session_context = load_session_context()
        if not session_context:
            print("Warning: No session context found for finalization", file=sys.stderr)
            sys.exit(0)  # Don't block session end if context missing
        
        # Generate session summary
        session_summary = generate_session_summary(session_context)
        
        # Log session end to audit trail
        log_session_end_to_audit_trail(session_context, session_summary)
        
        # Save session summary
        save_session_summary(session_summary)
        
        # Output completion message
        print(f"Session finalized: {session_summary['session_id']}")
        sys.exit(0)
        
    except Exception as e:
        print(f"Session finalization failed: {str(e)}", file=sys.stderr)
        sys.exit(0)  # Don't block session end if finalization fails

if __name__ == "__main__":
    main()
