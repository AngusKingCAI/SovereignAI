#!/usr/bin/env python3
"""
PostToolUse Hook: Plan Write Tracking

Runs after any write/edit operation to plan files.
Updates workflow state and re-runs phase gates for the current phase.
"""

import sys
import json
import os
from pathlib import Path
from datetime import datetime

def main():
    # Read hook input from stdin
    try:
        hook_input = json.loads(sys.stdin.read())
    except:
        # If no input, allow operation
        sys.exit(0)
    
    tool_name = hook_input.get("tool_name", "")
    tool_input = hook_input.get("tool_input", {})
    
    # Only track write/edit operations
    if tool_name not in ["write", "edit"]:
        sys.exit(0)
    
    # Check if operation is on plan files
    file_path = tool_input.get("file_path", "")
    if not file_path:
        sys.exit(0)
    
    # Convert to Path and check if it's a plan file
    path_obj = Path(file_path)
    
    # Check if file is in plans directory or has plan-like name
    is_plan_file = (
        "plans" in path_obj.parts or 
        "plan" in path_obj.name.lower() or
        path_obj.name.startswith("plan-")
    )
    
    if not is_plan_file:
        sys.exit(0)
    
    print(f"PostToolUse Hook: Tracking plan file modification: {path_obj.name}")
    
    # Update workflow state (placeholder for now)
    # In production, this would:
    # 1. Update workflow_state table with new mtime
    # 2. Re-run phase gates for the current phase
    # 3. Log the modification for audit trail
    
    # For now, we'll just log the modification
    timestamp = datetime.now().isoformat()
    print(f"   Timestamp: {timestamp}")
    print(f"   Operation: {tool_name}")
    print(f"   File: {path_obj}")
    
    # In production, this would trigger phase gate re-validation
    # For now, we'll just acknowledge the modification
    print(f"PostToolUse Hook: Plan file modification tracked")
    
    sys.exit(0)  # Always allow operation (this is tracking, not blocking)

if __name__ == "__main__":
    main()