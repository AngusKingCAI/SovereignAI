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


def read_session_state() -> dict:
    """Read full session state including agent and workflow state."""
    state_file = get_session_state_file()
    
    if not state_file.exists():
        return {"agent": None, "workflow_state": None}
    
    try:
        with open(state_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (json.JSONDecodeError, KeyError):
        return {"agent": None, "workflow_state": None}


def write_agent_context(agent: str) -> None:
    """Write current agent context to session state file."""
    state_file = get_session_state_file()
    state_data = read_session_state()
    state_data["agent"] = agent
    
    with open(state_file, 'w', encoding='utf-8') as f:
        json.dump(state_data, f, indent=2)


def write_workflow_state(workflow_state: str) -> None:
    """Write current workflow state to session state file."""
    state_file = get_session_state_file()
    state_data = read_session_state()
    state_data["workflow_state"] = workflow_state
    
    with open(state_file, 'w', encoding='utf-8') as f:
        json.dump(state_data, f, indent=2)


def read_agent_context() -> str | None:
    """Read current agent context from session state file."""
    state_data = read_session_state()
    return state_data.get("agent")


def read_workflow_state() -> str | None:
    """Read current workflow state from session state file."""
    state_data = read_session_state()
    return state_data.get("workflow_state")


def clear_session_state() -> None:
    """Clear session state file."""
    state_file = get_session_state_file()
    
    if state_file.exists():
        state_file.unlink()


if __name__ == "__main__":
    if len(sys.argv) > 1:
        # Check for workflow flag first
        if "--workflow" in sys.argv:
            workflow_index = sys.argv.index("--workflow")
            if len(sys.argv) > workflow_index + 1:
                workflow_state = sys.argv[workflow_index + 1]
                write_workflow_state(workflow_state)
                print(f"Workflow state updated: {workflow_state}")
            else:
                print("Usage: python session_state.py --workflow <workflow_state>")
                sys.exit(1)
        
        # Check for agent argument (non-flag first argument)
        if len(sys.argv) > 1 and not sys.argv[1].startswith("--"):
            agent = sys.argv[1]
            write_agent_context(agent)
            print(f"Agent context updated: {agent} agent active")
    else:
        print("Usage: python session_state.py <agent_name> [--workflow <workflow_state>] OR python session_state.py --workflow <workflow_state>")
        sys.exit(1)