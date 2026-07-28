"""Session state management for agent context persistence."""

from __future__ import annotations

import json
from pathlib import Path


def get_session_state_file(session_id: str) -> Path:
    """Get the session state file path for a given session_id."""
    # Use script directory for session state storage
    script_dir = Path(__file__).parent
    state_dir = script_dir / ".session_state"
    state_dir.mkdir(parents=True, exist_ok=True)
    return state_dir / f"{session_id}.json"


def write_agent_context(session_id: str, agent: str) -> None:
    """Write agent context to session state file."""
    state_file = get_session_state_file(session_id)
    state_data = {"agent": agent}
    
    with open(state_file, 'w', encoding='utf-8') as f:
        json.dump(state_data, f, indent=2)


def read_agent_context(session_id: str) -> str | None:
    """Read agent context from session state file."""
    state_file = get_session_state_file(session_id)
    
    if not state_file.exists():
        return None
    
    try:
        with open(state_file, 'r', encoding='utf-8') as f:
            state_data = json.load(f)
            return state_data.get("agent")
    except (json.JSONDecodeError, KeyError):
        return None


def clear_session_state(session_id: str) -> None:
    """Clear session state file for a given session_id."""
    state_file = get_session_state_file(session_id)
    
    if state_file.exists():
        state_file.unlink()
