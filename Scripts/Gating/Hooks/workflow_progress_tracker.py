#!/usr/bin/env python3
"""
Workflow Progress Tracker Hook - Track workflow execution and enforce cycle back to step 1
"""

import sys
import json
import os
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

def check_workflow_completion(workflow_state):
    """Check if workflow has completed step 9 and should cycle back."""
    if not workflow_state:
        return False
    
    current_step = workflow_state.get("current_step", 0)
    workflow_complete = workflow_state.get("workflow_complete", False)
    
    # If workflow is complete (step 9 done), it should cycle back to step 1
    if workflow_complete or current_step >= 9:
        return True
    
    return False

def reset_workflow_to_step1():
    """Reset workflow state to step 1 for next cycle."""
    workflow_state = {
        "current_step": 1,
        "workflow_complete": False,
        "cycle_count": 0,
        "last_reset": datetime.now().isoformat(),
        "status": "ready_for_next_task"
    }
    save_workflow_state(workflow_state)
    return workflow_state

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
        hook_event = event_data.get('hook_event_name', 'PostToolUse')
        
        # Load current workflow state
        workflow_state = load_workflow_state()
        
        # Initialize workflow state if it doesn't exist
        if not workflow_state:
            workflow_state = {
                "current_step": 1,
                "workflow_complete": False,
                "cycle_count": 0,
                "last_reset": datetime.now().isoformat(),
                "status": "initialized"
            }
            save_workflow_state(workflow_state)
            print("Workflow state initialized at step 1")
            sys.exit(0)
        
        # Check if workflow should cycle back to step 1
        if check_workflow_completion(workflow_state):
            print("Workflow complete - cycling back to step 1")
            reset_workflow_to_step1()
            sys.exit(0)
        
        # Track workflow progress based on tool operations
        tool_name = event_data.get('tool_name', '')
        
        # Simple workflow step detection based on operations
        if tool_name == "ask_user_question":
            # Likely step where user interaction occurs
            current_step = workflow_state.get("current_step", 1)
            if current_step < 9:
                workflow_state["current_step"] = current_step + 1
                save_workflow_state(workflow_state)
                print(f"Workflow progressed to step {workflow_state['current_step']}")
        
        sys.exit(0)
        
    except Exception as e:
        print(f"Workflow progress tracking failed: {str(e)}", file=sys.stderr)
        sys.exit(2)

if __name__ == "__main__":
    main()
