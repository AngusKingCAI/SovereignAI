#!/usr/bin/env python3
"""
PostToolUse Hook - Log operations and update state
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

def update_session_context(session_context):
    """Update session context with operation counters."""
    # Increment operation counters would happen here based on tool_name
    # For now, just save the context back
    project_root = get_project_root()
    session_file = project_root / "Logs" / "Architect" / "Gating" / "session-context.json"
    
    with open(session_file, 'w', encoding='utf-8') as f:
        json.dump(session_context, f, indent=2)

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

def track_workflow_progress(tool_name, workflow_state):
    """Track workflow progress based on tool operations."""
    if not workflow_state:
        workflow_state = {
            "current_step": 1,
            "workflow_complete": False,
            "cycle_count": 0,
            "last_reset": datetime.now().isoformat(),
            "status": "initialized"
        }
        save_workflow_state(workflow_state)
        return workflow_state
    
    # Simple workflow step detection based on operations
    if tool_name == "ask_user_question":
        # Likely step where user interaction occurs
        current_step = workflow_state.get("current_step", 1)
        if current_step < 9:
            workflow_state["current_step"] = current_step + 1
            workflow_state["status"] = f"in_progress_step_{current_step + 1}"
            save_workflow_state(workflow_state)
    
    return workflow_state

def log_operation_to_audit_trail(session_context, tool_name, file_path, result):
    """Log tool operation to audit trail."""
    project_root = get_project_root()
    audit_log_file = project_root / "Logs" / "Architect" / "Gating" / "audit-trail.log"
    
    timestamp = datetime.now().isoformat()
    session_id = session_context.get('session_id', 'unknown')
    current_phase = session_context.get('current_phase', 'unknown')
    
    # Format the log entry
    file_info = f"file={file_path}" if file_path else "no_file"
    result_info = f"result={result}" if result else "no_result"
    log_entry = f"[{timestamp}] TOOL_USE: session_id={session_id}, phase={current_phase}, tool={tool_name}, {file_info}, {result_info}\n"
    
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
        
        # Extract tool information
        tool_name = event_data.get('tool_name', '')
        tool_input = event_data.get('tool_input', {})
        tool_result = event_data.get('tool_result', {})
        
        # Get file path from tool input if available
        file_path = None
        if 'file_path' in tool_input:
            file_path = tool_input['file_path']
        elif 'path' in tool_input:
            file_path = tool_input['path']
        elif 'command' in tool_input:
            file_path = tool_input['command']
        
        # Load session context
        session_context = load_session_context()
        if not session_context:
            print("Warning: No session context found for logging", file=sys.stderr)
            sys.exit(0)  # Don't block operation if logging fails
        
        # Log operation to audit trail
        log_operation_to_audit_trail(session_context, tool_name, file_path, str(tool_result)[:100])
        
        # Update session context
        update_session_context(session_context)
        
        # Track workflow progress
        workflow_state = load_workflow_state()
        workflow_state = track_workflow_progress(tool_name, workflow_state)
        
        # Check if workflow should cycle back to step 1
        if check_workflow_completion(workflow_state):
            print("Workflow complete - cycling back to step 1")
            reset_workflow_to_step1()
        
        # Return success (logging failures don't block operations)
        print(f"Operation logged: {tool_name}")
        sys.exit(0)
        
    except Exception as e:
        print(f"Logging failed (operation still succeeded): {str(e)}", file=sys.stderr)
        sys.exit(0)  # Don't block operation if logging fails

if __name__ == "__main__":
    main()
