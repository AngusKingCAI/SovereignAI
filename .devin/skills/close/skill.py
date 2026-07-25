#!/usr/bin/env python3
"""
Close Agent Session Skill - Close current agent session and return to Architect
"""

import json
from pathlib import Path
from datetime import datetime
import sys

def get_project_root():
    """Get project root directory."""
    return Path("C:/SovereignAI")

def read_agent_config():
    """Read current agent configuration."""
    project_root = get_project_root()
    config_file = project_root / ".devin" / "agent_config.json"
    
    if config_file.exists():
        with open(config_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    # Default configuration
    return {
        "default_agent": "Architect",
        "current_agent": "Architect",
        "last_updated": datetime.now().isoformat(),
        "session_count": 0
    }

def write_agent_config(config):
    """Write agent configuration."""
    project_root = get_project_root()
    config_file = project_root / ".devin" / "agent_config.json"
    
    # Ensure directory exists
    config_file.parent.mkdir(parents=True, exist_ok=True)
    
    with open(config_file, 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=2)

def log_session_closure(current_agent):
    """Log session closure to appropriate agent log file."""
    project_root = get_project_root()
    logs_dir = project_root / "Logs" / current_agent
    
    # Ensure directory exists
    logs_dir.mkdir(parents=True, exist_ok=True)
    
    # Create log file with timestamp
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    log_file = logs_dir / f"{timestamp}.md"
    
    with open(log_file, 'w', encoding='utf-8') as f:
        f.write(f"# Session End\n\n")
        f.write(f"## Session Closure\n")
        f.write(f"- Agent: {current_agent}\n")
        f.write(f"- Timestamp: {datetime.now().isoformat()}\n")
        f.write(f"- Reason: User invoked /close\n")
        f.write(f"- Next Agent: Architect (default)\n")

def get_agent_workflows(agent_name):
    """Get list of available workflows for a specific agent."""
    project_root = get_project_root()
    workflow_dir = project_root / "Workflow" / agent_name
    
    if not workflow_dir.exists():
        return []
    
    workflows = []
    for workflow_file in workflow_dir.glob("*.md"):
        # Skip templates and non-workflow files
        if workflow_file.name.lower().startswith("template") or workflow_file.name.lower().startswith("quality"):
            continue
            
        try:
            with open(workflow_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                workflow_id = None
                description = "No description"
                purpose_found = False
                
                for i, line in enumerate(lines[:20]):
                    line = line.strip()
                    if line.startswith("**ID**:"):
                        workflow_id = line.split(":", 1)[1].strip()
                    elif line.startswith("**Description**:"):
                        description = line.split(":", 1)[1].strip()
                    elif line.startswith("## Purpose"):
                        purpose_found = True
                        # Get next line as description if no description field found
                        if i + 1 < len(lines):
                            description = lines[i + 1].strip()
                        # Don't break, continue to check for ID field
                    elif purpose_found and not description:
                        # If we found Purpose but description is still empty, try the next few lines
                        if i + 1 < len(lines) and lines[i + 1].strip():
                            description = lines[i + 1].strip()
                
                if not workflow_id:
                    workflow_id = workflow_file.stem
                
                # If description is still empty, use a default
                if not description or description == "No description":
                    description = f"Workflow for {agent_name}"
                
                workflows.append({
                    "id": workflow_id,
                    "name": workflow_file.stem,
                    "description": description,
                    "file": str(workflow_file.relative_to(project_root)).replace("\\", "/")
                })
        except Exception as e:
            # Skip files that can't be read
            continue
    
    return workflows

def main():
    """Main skill function."""
    try:
        # Read current configuration
        config = read_agent_config()
        current_agent = config.get("current_agent", "Architect")
        
        # Log session closure
        log_session_closure(current_agent)
        
        # Update configuration to reset to Architect
        config["current_agent"] = "Architect"
        config["last_updated"] = datetime.now().isoformat()
        config["session_count"] = config.get("session_count", 0) + 1
        
        # Write updated configuration
        write_agent_config(config)
        
        # Get Architect workflows for the skill to present
        architect_workflows = get_agent_workflows("Architect")
        
        # Output as JSON for programmatic use by the skill
        output = {
            "session_closed": True,
            "current_agent": "Architect",
            "architect_workflows": architect_workflows,
            "selection_format": "numbered"
        }
        print(json.dumps(output, indent=2))
        
    except Exception as e:
        print(f"Error closing session: {str(e)}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()