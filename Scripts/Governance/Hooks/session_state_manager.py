#!/usr/bin/env python3
"""
Session State Management Hook - SessionEnd
Automatically updates session state, generates session summaries, and manages session transitions
"""

import json
import sys
import os
import re
import uuid
from pathlib import Path
from datetime import datetime
from typing import Dict, Optional

# Project root
PROJECT_ROOT = Path("C:/SovereignAI")


def get_current_session_id() -> str:
    """Get current session ID from environment or generate new one."""
    session_id = os.environ.get('DEVIN_SESSION_ID')
    if not session_id:
        session_id = str(uuid.uuid4())
    return session_id


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


def generate_session_summary(session_id: str, agent_type: str) -> Dict:
    """Generate session summary based on session logs."""
    logs_dir = PROJECT_ROOT / "Logs" / agent_type / "Sessions"
    
    summary = {
        "session_id": session_id,
        "agent_type": agent_type,
        "timestamp": datetime.now().isoformat(),
        "operation_count": 0,
        "status": "completed"
    }
    
    # Try to read session log if it exists
    session_log_file = logs_dir / f"{session_id}.json"
    if session_log_file.exists():
        try:
            with open(session_log_file, 'r', encoding='utf-8') as f:
                session_data = json.load(f)
            summary["operation_count"] = len(session_data.get("operations", []))
            summary["status"] = session_data.get("status", "completed")
        except Exception:
            pass
    
    return summary


def update_session_state(summary: Dict):
    """Update session state in logs directory."""
    logs_dir = PROJECT_ROOT / "Logs" / summary["agent_type"] / "Sessions"
    logs_dir.mkdir(parents=True, exist_ok=True)
    
    # Write session summary
    summary_file = logs_dir / f"{summary['session_id']}-summary.json"
    with open(summary_file, 'w', encoding='utf-8') as f:
        json.dump(summary, f, indent=2)


def detect_phase_transition(agent_type: str) -> Optional[str]:
    """Detect if session completion should trigger phase transition."""
    # Check if workflow completion criteria met
    gates_dir = PROJECT_ROOT / "Logs" / "Architect" / "Gates"
    
    # This is a simplified check - actual implementation would be more sophisticated
    if gates_dir.exists():
        state_files = list(gates_dir.glob("phase-*-state.json"))
        if state_files:
            # Find highest completed phase
            phase_numbers = []
            for state_file in state_files:
                match = re.search(r'phase-(\d+)-state', state_file.name)
                if match:
                    phase_numbers.append(int(match.group(1)))
            
            if phase_numbers:
                highest_phase = max(phase_numbers)
                # Suggest next phase
                return f"phase_{highest_phase + 1}"
    
    return None


def main():
    """Main hook execution."""
    try:
        # Read event data from stdin
        input_data = json.loads(sys.stdin.read())
        hook_event = input_data.get("hook_event_name", "SessionEnd")
        
        if hook_event != "SessionEnd":
            print(json.dumps({"hookSpecificOutput": {"hookEventName": hook_event}}))
            sys.exit(0)
        
        # Get session information
        session_id = get_current_session_id()
        agent_type = get_current_agent()
        
        # Generate session summary
        summary = generate_session_summary(session_id, agent_type)
        
        # Update session state
        update_session_state(summary)
        
        # Detect phase transition
        next_phase = detect_phase_transition(agent_type)
        if next_phase:
            summary["suggested_next_phase"] = next_phase
        
        # Return session summary as additional context
        output = {
            "hookSpecificOutput": {
                "hookEventName": "SessionEnd",
                "additionalContext": f"Session {session_id} completed. Operations: {summary['operation_count']}. Status: {summary['status']}."
            }
        }
        
        print(json.dumps(output))
        sys.exit(0)
        
    except Exception as e:
        print(f"Session state management error: {e}", file=sys.stderr)
        print(json.dumps({"hookSpecificOutput": {"hookEventName": "SessionEnd"}}))
        sys.exit(1)


if __name__ == "__main__":
    main()