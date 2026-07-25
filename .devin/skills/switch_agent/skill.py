#!/usr/bin/env python3
"""
Agent Switcher Skill - Switch between different agents using interactive selection
"""

import json
import os
from pathlib import Path
from datetime import datetime
import sys

def get_project_root():
    """Get project root directory."""
    return Path("C:/SovereignAI")

def get_available_agents():
    """Get list of available agents from Agents/ directory."""
    project_root = get_project_root()
    agents_dir = project_root / "Agents"
    
    if not agents_dir.exists():
        return []
    
    # Get all subdirectories in Agents/ (including Architect)
    agents = []
    for agent_dir in agents_dir.iterdir():
        if agent_dir.is_dir():
            # Check for AGENTS.md in the agent directory or use project root AGENTS.md for Architect
            if agent_dir.name == "Architect":
                agents_file = project_root / "AGENTS.md"
            else:
                agents_file = agent_dir / "AGENTS.md"
            
            if agents_file.exists():
                # Read first line for description
                with open(agents_file, 'r', encoding='utf-8') as f:
                    first_line = f.readline().strip()
                    if first_line.startswith("# "):
                        description = first_line[2:].strip()
                    elif first_line.startswith("---"):
                        # Skip YAML frontmatter
                        for line in f:
                            if line.strip() == "---":
                                break
                        first_line = f.readline().strip()
                        if first_line.startswith("# "):
                            description = first_line[2:].strip()
                        else:
                            description = agent_dir.name
                    else:
                        description = agent_dir.name
                
                # Get available workflows for this agent
                workflows = get_agent_workflows(agent_dir.name)
                
                agents.append({
                    "name": agent_dir.name,
                    "description": description,
                    "workflows": workflows
                })
    
    return agents

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

def switch_agent(agent_name, workflow_id=None):
    """Switch to specified agent and optionally select a workflow."""
    # Get available agents
    available_agents = get_available_agents()
    available_names = [a['name'] for a in available_agents]
    
    if agent_name not in available_names:
        print(f"Error: Agent '{agent_name}' not available. Available agents: {', '.join(available_names)}")
        return False
    
    # Read current configuration
    config = read_agent_config()
    current_agent = config.get("current_agent", "Architect")
    
    # Update configuration
    config["current_agent"] = agent_name
    config["last_updated"] = datetime.now().isoformat()
    config["session_count"] = config.get("session_count", 0) + 1
    
    # Write updated configuration
    write_agent_config(config)
    
    # Log the switch
    log_agent_switch(current_agent, agent_name, workflow_id)
    
    print(f"Switched from {current_agent} to {agent_name}")
    
    if workflow_id:
        print(f"Loading {agent_name} workflow: {workflow_id}...")
    else:
        print(f"Loading {agent_name}...")
    
    return True

def log_agent_switch(from_agent, to_agent, workflow_id=None):
    """Log agent switch to Architect log file."""
    project_root = get_project_root()
    logs_dir = project_root / "Logs" / "Architect"
    
    # Ensure directory exists
    logs_dir.mkdir(parents=True, exist_ok=True)
    
    # Create log file with timestamp
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    log_file = logs_dir / f"{timestamp}.md"
    
    with open(log_file, 'w', encoding='utf-8') as f:
        f.write(f"# Agent Switch Log\n\n")
        f.write(f"## Agent Switch\n")
        f.write(f"- From Agent: {from_agent}\n")
        f.write(f"- To Agent: {to_agent}\n")
        if workflow_id:
            f.write(f"- Selected Workflow: {workflow_id}\n")
        f.write(f"- Timestamp: {datetime.now().isoformat()}\n")
        f.write(f"- Reason: User invoked /switch\n")

def main():
    """Main skill function - outputs available agents and workflows for interactive selection."""
    try:
        # Get available agents with their workflows
        available_agents = get_available_agents()
        
        if not available_agents:
            print("No agents available for switching.")
            return
        
        # Read current configuration
        config = read_agent_config()
        current_agent = config.get("current_agent", "Architect")
        
        # Output as JSON for programmatic use by the skill
        output = {
            "current_agent": current_agent,
            "available_agents": available_agents,
            "selection_format": "numbered"
        }
        print(json.dumps(output, indent=2))
        
    except Exception as e:
        print(f"Error: {str(e)}", file=sys.stderr)
        sys.exit(1)

def show_agent_workflows(agent_name):
    """Show available workflows for a specific agent."""
    try:
        workflows = get_agent_workflows(agent_name)
        
        if not workflows:
            print(f"No workflows available for agent '{agent_name}'.")
            return
        
        # Output as JSON for programmatic use
        output = {
            "agent": agent_name,
            "workflows": workflows,
            "selection_format": "numbered"
        }
        print(json.dumps(output, indent=2))
        
    except Exception as e:
        print(f"Error: {str(e)}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == "workflows" and len(sys.argv) > 2:
            # Show workflows for a specific agent
            agent_name = sys.argv[2]
            show_agent_workflows(agent_name)
        elif command == "switch" and len(sys.argv) > 2:
            # Switch to specified agent
            agent_name = sys.argv[2]
            workflow_id = sys.argv[3] if len(sys.argv) > 3 else None
            success = switch_agent(agent_name, workflow_id)
            sys.exit(0 if success else 1)
        else:
            # Legacy: direct agent name (assume switch)
            agent_name = sys.argv[1]
            workflow_id = sys.argv[2] if len(sys.argv) > 2 else None
            success = switch_agent(agent_name, workflow_id)
            sys.exit(0 if success else 1)
    else:
        # Show available agents with workflows
        main()