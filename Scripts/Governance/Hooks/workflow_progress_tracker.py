#!/usr/bin/env python3
"""
Workflow Progress Tracking Hook - PostToolUse
Automatically tracks workflow progress and detects when phases/steps are complete
"""

import json
import sys
import re
from pathlib import Path
from datetime import datetime
from typing import Dict, Optional, List

# Project root
PROJECT_ROOT = Path("C:/SovereignAI")

# Workflow step patterns for different agents
WORKFLOW_PATTERNS = {
    "Architect": [
        r"✅ Gate \d+ PASS",
        r"Workflow step \d+ completed",
        r"Implementation complete"
    ],
    "Planner": [
        r"✅ Gate \d+ PASS",
        r"Plan creation complete",
        r"Review completed"
    ],
    "Executor": [
        r"✅ Gate \d+ PASS",
        r"Implementation complete",
        r"Tests passed"
    ]
}


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


def detect_workflow_completion(content: str, agent_type: str) -> bool:
    """Detect if workflow step is complete based on content."""
    patterns = WORKFLOW_PATTERNS.get(agent_type, WORKFLOW_PATTERNS["Architect"])
    
    for pattern in patterns:
        if re.search(pattern, content, re.IGNORECASE):
            return True
    
    return False


def update_workflow_progress(agent_type: str, step_completed: bool, tool_name: str, file_path: str):
    """Update workflow progress tracking."""
    progress_dir = PROJECT_ROOT / "Logs" / agent_type / "Progress"
    progress_dir.mkdir(parents=True, exist_ok=True)
    
    progress_file = progress_dir / "workflow-progress.json"
    
    # Load existing progress or create new
    if progress_file.exists():
        try:
            with open(progress_file, 'r', encoding='utf-8') as f:
                progress_data = json.load(f)
        except Exception:
            progress_data = {"steps_completed": [], "last_updated": None}
    else:
        progress_data = {"steps_completed": [], "last_updated": None}
    
    # Add new step if not already tracked
    step_key = f"{tool_name}:{file_path}"
    if step_key not in progress_data["steps_completed"]:
        progress_data["steps_completed"].append(step_key)
    
    progress_data["last_updated"] = datetime.now().isoformat()
    progress_data["total_steps"] = len(progress_data["steps_completed"])
    
    # Write updated progress
    with open(progress_file, 'w', encoding='utf-8') as f:
        json.dump(progress_data, f, indent=2)


def main():
    """Main hook execution."""
    try:
        # Read event data from stdin
        input_data = json.loads(sys.stdin.read())
        hook_event = input_data.get("hook_event_name", "PostToolUse")
        
        if hook_event != "PostToolUse":
            print(json.dumps({"hookSpecificOutput": {"hookEventName": hook_event}}))
            sys.exit(0)
        
        tool_name = input_data.get("tool_name", "")
        tool_input = input_data.get("tool_input", {})
        
        # Only track workflow-related operations
        file_path = tool_input.get("file_path", "")
        
        if not file_path or not any(prefix in file_path for prefix in ["Workflow/", "Rules/", "Agents/"]):
            print(json.dumps({"hookSpecificOutput": {"hookEventName": "PostToolUse"}}))
            sys.exit(0)
        
        # Get current agent
        agent_type = get_current_agent()
        
        # Update workflow progress
        update_workflow_progress(agent_type, True, tool_name, file_path)
        
        # Check if content indicates workflow completion
        if "content" in tool_input:
            content = tool_input["content"]
            is_complete = detect_workflow_completion(content, agent_type)
            
            if is_complete:
                output = {
                    "hookSpecificOutput": {
                        "hookEventName": "PostToolUse",
                        "additionalContext": f"Workflow step completed: {tool_name} on {file_path}"
                    }
                }
                print(json.dumps(output))
                sys.exit(0)
        
        print(json.dumps({"hookSpecificOutput": {"hookEventName": "PostToolUse"}}))
        sys.exit(0)
        
    except Exception as e:
        print(f"Workflow progress tracking error: {e}", file=sys.stderr)
        print(json.dumps({"hookSpecificOutput": {"hookEventName": "PostToolUse"}}))
        sys.exit(1)


if __name__ == "__main__":
    main()