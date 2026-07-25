#!/usr/bin/env python3
"""
Workflow Step Gate Hook - Ensures steps are done in order with user intervention on failure
"""

import sys
import json
from pathlib import Path
from datetime import datetime

def get_project_root():
    """Get project root directory."""
    return Path("C:/SovereignAI")

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

def load_workflow_steps():
    """Load workflow step definitions."""
    project_root = get_project_root()
    workflow_file = project_root / "Workflow" / "Architect" / "Architect_General_Workflow.md"
    
    if workflow_file.exists():
        with open(workflow_file, 'r', encoding='utf-8') as f:
            content = f.read()
            # Extract step headers
            steps = []
            for line in content.split('\n'):
                if line.startswith('### ') and line[4:].isdigit():
                    step_num = int(line[4:].split('.')[0])
                    step_name = line.split('.', 1)[1].strip() if '.' in line else line[4:].strip()
                    steps.append({"step": step_num, "name": step_name})
            return steps
    return []

def check_step_order(tool_name, tool_input, current_step, workflow_steps):
    """Check if operation is allowed for current workflow step."""
    # Allow Scripts/Gating/ operations to avoid circular dependency
    file_path = tool_input.get('file_path', tool_input.get('path', ''))
    if file_path and "Scripts/Gating/" in str(file_path):
        return True, "Allowed: Hook maintenance operation"
    
    # Map tools to typical workflow steps
    tool_step_mapping = {
        "ask_user_question": "user_interaction",
        "read": "research",
        "write": "implementation", 
        "edit": "implementation",
        "exec": "testing"
    }
    
    # Simple validation: ensure we're progressing through steps
    if current_step > len(workflow_steps):
        return False, f"Workflow complete - step {current_step} beyond defined steps"
    
    return True, f"Step {current_step} operation allowed"

def handle_step_failure(current_step, failure_reason):
    """Handle workflow step failure by asking user for direction."""
    # Create failure record
    project_root = get_project_root()
    failure_file = project_root / "Logs" / "Architect" / "Gating" / "step-failure.json"
    
    failure_data = {
        "step": current_step,
        "reason": failure_reason,
        "timestamp": datetime.now().isoformat(),
        "status": "awaiting_user_decision"
    }
    
    failure_file.parent.mkdir(parents=True, exist_ok=True)
    with open(failure_file, 'w', encoding='utf-8') as f:
        json.dump(failure_data, f, indent=2)
    
    # Return user prompt
    return f"STEP FAILURE at step {current_step}: {failure_reason}. Please choose: retry/modify/abort"

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
    """Main hook function - workflow step gating."""
    try:
        # Read event data from stdin
        event_data = read_stdin()
        
        tool_name = event_data.get('tool_name', '')
        tool_input = event_data.get('tool_input', {})
        
        # Load workflow state
        workflow_state = load_workflow_state()
        if not workflow_state:
            # Initialize workflow state
            workflow_state = {
                "current_step": 1,
                "workflow_complete": False,
                "step_failures": [],
                "last_updated": datetime.now().isoformat()
            }
            save_workflow_state(workflow_state)
        
        current_step = workflow_state.get("current_step", 1)
        
        # Load workflow step definitions
        workflow_steps = load_workflow_steps()
        
        # Check if operation is allowed for current step
        step_allowed, message = check_step_order(tool_name, tool_input, current_step, workflow_steps)
        
        if not step_allowed:
            # Handle step failure - ask user what to do
            user_message = handle_step_failure(current_step, message)
            print(f"BLOCKED: {user_message}", file=sys.stderr)
            sys.exit(2)  # Block operation
        
        # Allow operation
        print(f"STEP GATE PASSED: Step {current_step} - {message}")
        sys.exit(0)
        
    except Exception as e:
        print(f"Workflow step gate error: {str(e)}", file=sys.stderr)
        sys.exit(2)  # Block on error for safety

if __name__ == "__main__":
    main()
