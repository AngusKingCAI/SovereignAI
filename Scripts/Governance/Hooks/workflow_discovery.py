#!/usr/bin/env python3
"""
Workflow discovery hook for SessionStart.
Automatically discovers and populates workflow metadata without using model tokens.
"""

import sys
import json
import os
import traceback
from pathlib import Path
from datetime import datetime

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))
from hook_utils import get_verbosity, should_print, show_hook_header, show_hook_result

def discover_workflows():
    """Discover available workflows from Workflow/ directory."""
    project_root = Path("C:/SovereignAI")
    workflow_dir = project_root / "Workflow"
    
    workflows = {}
    
    if not workflow_dir.exists():
        return workflows
    
    # Scan each agent's workflow directory
    for agent_dir in workflow_dir.iterdir():
        if agent_dir.is_dir():
            agent_workflows = []
            
            # Find all .md files in the agent's workflow directory
            try:
                workflow_files = list(agent_dir.glob("*.md"))
            except Exception as e:
                print(f"Warning: Could not scan {agent_dir}: {e}")
                continue
                
            for workflow_file in workflow_files:
                try:
                    # Read first 15 lines to extract metadata
                    with open(workflow_file, 'r', encoding='utf-8') as f:
                        content = f.read()
                        lines = content.split('\n')[:15]
                    
                    # Extract metadata from header
                    metadata = {
                        "file": workflow_file.name,
                        "path": str(workflow_file.relative_to(project_root))
                    }
                    
                    for line in lines:
                        if line and isinstance(line, str):
                            line = line.strip()
                            if line.startswith("**Workflow Name**:"):
                                parts = line.split(":", 1)
                                if len(parts) > 1:
                                    metadata["name"] = parts[1].strip()
                            elif line.startswith("**Description**:"):
                                parts = line.split(":", 1)
                                if len(parts) > 1:
                                    metadata["description"] = parts[1].strip()
                            elif line.startswith("**Status**:"):
                                parts = line.split(":", 1)
                                if len(parts) > 1:
                                    metadata["status"] = parts[1].strip()
                    
                    if "name" in metadata:
                        agent_workflows.append(metadata)
                except Exception as e:
                    print(f"Warning: Could not read {workflow_file}: {e}")
                    traceback.print_exc()
            
            if agent_workflows:
                workflows[agent_dir.name] = agent_workflows
    
    return workflows

def main():
    """Main workflow discovery logic."""
    verbosity = get_verbosity()
    show_hook_header("Workflow Discovery Hook", verbosity)
    
    # Discover workflows
    workflows = discover_workflows()
    
    if not workflows:
        show_hook_result("No workflows discovered", success=True, verbosity=verbosity)
        return 0
    
    # Format as additional context
    workflow_context = "Available Workflows:\n"
    
    for agent_name, agent_workflows in workflows.items():
        workflow_context += f"\n{agent_name}:\n"
        for workflow in agent_workflows:
            workflow_context += f"  - {workflow.get('name', workflow['file'])}: {workflow.get('description', 'No description')}\n"
    
    # Output as additionalContext for skill access
    output = {
        "hookSpecificOutput": {
            "hookEventName": "SessionStart",
            "additionalContext": workflow_context
        }
    }
    
    print(json.dumps(output, indent=2))
    show_hook_result(f"Discovered {sum(len(w) for w in workflows.values())} workflows across {len(workflows)} agents", success=True, verbosity=verbosity)
    
    return 0

if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except Exception as e:
        print(f"Error in workflow discovery: {e}", file=sys.stderr)
        sys.exit(1)
