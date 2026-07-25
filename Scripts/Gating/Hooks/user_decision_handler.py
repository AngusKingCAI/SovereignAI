#!/usr/bin/env python3
"""
User Decision Handler Hook - Handles user intervention on workflow step failures
"""

import sys
import json
from pathlib import Path
from datetime import datetime

def get_project_root():
    """Get project root directory."""
    return Path("C:/SovereignAI")

def load_step_failure():
    """Load current step failure state."""
    project_root = get_project_root()
    failure_file = project_root / "Logs" / "Architect" / "Gating" / "step-failure.json"
    
    if failure_file.exists():
        with open(failure_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    return None

def clear_step_failure():
    """Clear step failure state after user decision."""
    project_root = get_project_root()
    failure_file = project_root / "Logs" / "Architect" / "Gating" / "step-failure.json"
    
    if failure_file.exists():
        failure_file.unlink()

def handle_user_decision(user_input, workflow_state):
    """Process user decision on step failure."""
    failure_data = load_step_failure()
    
    if not failure_data:
        return "No active step failure to resolve"
    
    step = failure_data.get("step", 1)
    user_input_lower = user_input.lower()
    
    if "retry" in user_input_lower:
        # User wants to retry current step
        workflow_state["current_step"] = step
        workflow_state["last_updated"] = datetime.now().isoformat()
        return f"Retrying step {step}"
    
    elif "modify" in user_input_lower:
        # User wants to modify approach, stay on current step
        workflow_state["current_step"] = step
        workflow_state["last_updated"] = datetime.now().isoformat()
        return f"Modifying approach for step {step}"
    
    elif "abort" in user_input_lower:
        # User wants to abort workflow
        workflow_state["workflow_complete"] = True
        workflow_state["aborted"] = True
        workflow_state["last_updated"] = datetime.now().isoformat()
        clear_step_failure()
        return "Workflow aborted by user"
    
    elif "next" in user_input_lower or "continue" in user_input_lower:
        # User wants to skip to next step
        workflow_state["current_step"] = step + 1
        workflow_state["last_updated"] = datetime.now().isoformat()
        clear_step_failure()
        return f"Advancing to step {step + 1}"
    
    else:
        return f"Unknown decision. Please choose: retry/modify/abort/next"

def load_workflow_state():
    """Load current workflow state."""
    project_root = get_project_root()
    workflow_file = project_root / "Logs" / "Architect" / "Gating" / "workflow-state.json"
    
    if workflow_file.exists():
        with open(workflow_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    return None

def save_workflow_state(workflow_state):
    """Save workflow state to file."""
    project_root = get_project_root()
    workflow_file = project_root / "Logs" / "Architect" / "Gating" / "workflow-state.json"
    
    # Ensure directory exists
    workflow_file.parent.mkdir(parents=True, exist_ok=True)
    
    with open(workflow_file, 'w', encoding='utf-8') as f:
        json.dump(workflow_state, f, indent=2)

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
    """Main hook function - user decision handling."""
    try:
        # Read event data from stdin
        event_data = read_stdin()
        
        user_message = event_data.get('user_message', '')
        
        # Load workflow state
        workflow_state = load_workflow_state()
        if not workflow_state:
            workflow_state = {
                "current_step": 1,
                "workflow_complete": False,
                "step_failures": [],
                "last_updated": datetime.now().isoformat()
            }
        
        # Check if there's an active step failure
        failure_data = load_step_failure()
        if failure_data:
            # Process user decision
            decision_result = handle_user_decision(user_message, workflow_state)
            save_workflow_state(workflow_state)
            print(f"USER DECISION PROCESSED: {decision_result}")
        else:
            print("No active step failure - normal operation")
        
        sys.exit(0)
        
    except Exception as e:
        print(f"User decision handler error: {str(e)}", file=sys.stderr)
        sys.exit(0)  # Don't block user input on error

if __name__ == "__main__":
    main()
