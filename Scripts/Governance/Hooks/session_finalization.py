#!/usr/bin/env python3
"""
Session finalization hook for Devin CLI governance system.
Performs final validation, generates compliance reports, and handles session cleanup.
"""

import sys
import json
import os
import hashlib
from pathlib import Path
from datetime import datetime

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

# Import simple logger
from simple_logger import log_session_end, get_current_session

def load_config():
    """Load governance configuration."""
    config_dir = Path(__file__).parent.parent / "Config"
    governance_config = config_dir / "governance_rules.json"
    
    if governance_config.exists():
        try:
            with open(governance_config) as f:
                return json.load(f)
        except json.JSONDecodeError as e:
            print(f"Warning: Could not parse governance config: {e}")
            return {}
    return {}

def get_session_context():
    """Get current session context using simple logger."""
    session_id = get_current_session()
    
    # Try to detect agent type from environment
    agent_type = os.environ.get('DEVIN_AGENT_TYPE', 'General')
    
    # Return simple session context
    return {
        'session_id': session_id,
        'agent_type': agent_type,
        'operations_count': 0  # Will be updated by operation logger
    }

def verify_completion(session_context, config):
    """Verify that all required operations for the session are complete."""
    current_phase = session_context.get('current_phase')
    if not current_phase:
        return True, "No phase set, nothing to verify"
    
    logs_dir = Path(__file__).parent.parent.parent.parent / "Logs" / "Architect" / "Gates"
    state_file = logs_dir / f"phase-{current_phase}-state.json"
    
    if not state_file.exists():
        return False, f"No state file for phase {current_phase}"
    
    try:
        with open(state_file) as f:
            state = json.load(f)
        
        metadata = state.get('metadata', {})
        
        # Check implementation status
        if metadata.get('implementation_status') != 'complete':
            return False, f"Phase {current_phase} implementation not complete"
        
        # Check test status
        if metadata.get('test_status') != 'passing':
            return False, f"Phase {current_phase} tests not passing"
        
        return True, f"Phase {current_phase} completion verified"
    except json.JSONDecodeError as e:
        return False, f"Could not parse state file for phase {current_phase}: {e}"

def generate_compliance_report(session_context, config):
    """Generate compliance report for the session using simple logger."""
    session_id = get_current_session()
    
    # Try to detect agent type from environment
    agent_type = os.environ.get('DEVIN_AGENT_TYPE', 'General')
    
    # Log session end with summary using simple logger
    summary = f"Session completed with {session_context.get('operations_count', 0)} operations"
    log_file = log_session_end(session_id, summary, agent_type)
    
    return True, f"Session ended and logged to: {log_file}"

def validate_integrity(session_context):
    """Validate cryptographic integrity of state files."""
    logs_dir = Path(__file__).parent.parent.parent.parent / "Logs" / "Architect" / "Gates"
    
    integrity_issues = []
    
    # Check all phase state files
    for state_file in logs_dir.glob("phase-*-state.json"):
        try:
            with open(state_file) as f:
                state = json.load(f)
            
            stored_hash = state.get('state_hash')
            if not stored_hash:
                integrity_issues.append(f"State file {state_file.name} missing hash")
                continue
            
            # Recalculate hash
            state_copy = state.copy()
            state_copy['state_hash'] = None
            state_json = json.dumps(state_copy, sort_keys=True)
            calculated_hash = hashlib.sha256(state_json.encode()).hexdigest()
            
            if calculated_hash != stored_hash:
                integrity_issues.append(f"State file {state_file.name} hash mismatch")
        except json.JSONDecodeError as e:
            integrity_issues.append(f"State file {state_file.name} parse error: {e}")
    
    if integrity_issues:
        return False, f"Integrity issues: {integrity_issues}"
    
    return True, "All state files integrity verified"

def check_phase_status(session_context):
    """Check and report current phase status."""
    current_phase = session_context.get('current_phase')
    if not current_phase:
        return True, "No active phase"
    
    logs_dir = Path(__file__).parent.parent.parent.parent / "Logs" / "Architect" / "Gates"
    state_file = logs_dir / f"phase-{current_phase}-state.json"
    
    if not state_file.exists():
        return True, f"Phase {current_phase} has no state file"
    
    try:
        with open(state_file) as f:
            state = json.load(f)
        
        metadata = state.get('metadata', {})
        status = f"Phase {current_phase}: {metadata.get('implementation_status', 'unknown')}"
        
        return True, status
    except json.JSONDecodeError as e:
        return True, f"Phase {current_phase}: could not parse state file"

def cleanup_temporary_files(session_context):
    """Clean up temporary files from the session."""
    logs_dir = Path(__file__).parent.parent.parent.parent / "Logs" / "Architect" / "Gates"
    
    # Clean up any temporary session files
    temp_files = logs_dir.glob(f"temp-{session_context.get('session_id', '*')}*")
    
    cleaned_count = 0
    for temp_file in temp_files:
        try:
            temp_file.unlink()
            cleaned_count += 1
        except:
            pass
    
    return True, f"Cleaned {cleaned_count} temporary files"

def archive_session_logs(session_context):
    """Archive session logs for long-term storage."""
    logs_dir = Path(__file__).parent.parent.parent.parent / "Logs" / "Architect" / "Gates"
    
    session_id = session_context.get('session_id', 'unknown')
    timestamp = datetime.now().strftime("%Y%m%d")
    
    # Create archive directory if it doesn't exist
    archive_dir = logs_dir / "archived_sessions" / timestamp
    archive_dir.mkdir(parents=True, exist_ok=True)
    
    # Archive session-specific files
    files_to_archive = [
        logs_dir / "session-context.json",
        logs_dir / f"compliance-report-{session_id}.json"
    ]
    
    archived_count = 0
    for file_path in files_to_archive:
        if file_path.exists():
            try:
                import shutil
                shutil.copy(file_path, archive_dir / file_path.name)
                archived_count += 1
            except:
                pass
    
    return True, f"Archived {archived_count} session files"

def main():
    """Main session finalization logic."""
    print("=== Session Finalization ===")
    print(f"Timestamp: {datetime.now().isoformat()}")
    
    # Get session context
    session_context = get_session_context()
    session_id = get_current_session()
    
    print(f"Session ID: {session_id}")
    
    # Load configuration
    config = load_config()
    
    # Get hook configuration
    governance = config.get('governance', {}) or {}
    finalization_config = governance.get('hook_configuration', {}).get('session_finalization', {}) or {}
    
    # Generate compliance report (now just session end logging)
    if finalization_config.get('generate_compliance_report', True):
        print("Generating session completion report...")
        generated, message = generate_compliance_report(session_context, config)
        print(f"Report generation: {message}")
    
    print("=== Session Finalization Complete ===")
    return 0  # Don't block session closure

if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except Exception as e:
        print(f"Error in session finalization: {e}", file=sys.stderr)
        sys.exit(1)