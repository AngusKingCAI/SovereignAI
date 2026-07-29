"""Session state management for agent context persistence."""

import json
import sys
from pathlib import Path


def get_session_state_file() -> Path:
    """Get the single session state file path."""
    script_dir = Path(__file__).parent
    state_dir = script_dir / ".session_state"
    state_dir.mkdir(parents=True, exist_ok=True)
    return state_dir / "session_state.json"


def write_agent_context(agent: str) -> None:
    """Write current agent context to session state file."""
    state_file = get_session_state_file()
    state_data = {"agent": agent}
    
    with open(state_file, 'w', encoding='utf-8') as f:
        json.dump(state_data, f, indent=2)


def read_agent_context() -> str | None:
    """Read current agent context from session state file."""
    state_file = get_session_state_file()
    
    if not state_file.exists():
        return None
    
    try:
        with open(state_file, 'r', encoding='utf-8') as f:
            state_data = json.load(f)
            return state_data.get("agent")
    except (json.JSONDecodeError, KeyError):
        return None


def clear_session_state() -> None:
    """Clear session state file."""
    state_file = get_session_state_file()
    
    if state_file.exists():
        state_file.unlink()


if __name__ == "__main__":
    if len(sys.argv) > 1:
        agent = sys.argv[1]
        write_agent_context(agent)
        print(f"Session state updated: {agent} agent active")
    else:
        print("Usage: python session_state.py <agent_name>")
        sys.exit(1)