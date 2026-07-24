#!/usr/bin/env python3
"""
Agent selection skill implementation.
Simple agent switching using configuration file.
"""

import sys
import json
import os
from pathlib import Path
from datetime import datetime

# Available agents with descriptions
AVAILABLE_AGENTS = {
    "architect": {
        "name": "Architect",
        "description": "Design deterministic engineering infrastructure and harness systems for AI-driven software development",
        "scope": "Infrastructure design, directory structure, workflow definition, gate system design",
        "best_for": "Architectural decisions, infrastructure planning, governance rules"
    },
    "executor": {
        "name": "Executor", 
        "description": "Execute plans and implement application code with hook-based governance enforcement",
        "scope": "Application code implementation, plan execution, development tasks",
        "best_for": "Implementation work, code development, executing plans"
    },
    "planner": {
        "name": "Planner",
        "description": "Create plans for Executor execution with internal and external review",
        "scope": "Planning, workflow creation, task breakdown",
        "best_for": "Creating implementation plans, task organization"
    },
    "researcher": {
        "name": "Researcher",
        "description": "Perform external research and create design documents",
        "scope": "Research, documentation, design exploration",
        "best_for": "Research tasks, documentation, design research"
    },
    "reviewer": {
        "name": "Reviewer",
        "description": "Review execution logs and check against rules and gates",
        "scope": "Review, verification, compliance checking",
        "best_for": "Reviewing work, verification, compliance"
    }
}

def load_agent_config():
    """Load agent configuration."""
    config_file = Path(".devin/agent_config.json")
    
    if not config_file.exists():
        return {
            "default_agent": "Architect",
            "current_agent": "Architect",
            "last_updated": datetime.now().isoformat(),
            "session_count": 0
        }
    
    try:
        with open(config_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        return {
            "default_agent": "Architect",
            "current_agent": "Architect",
            "last_updated": datetime.now().isoformat(),
            "session_count": 0
        }

def save_agent_config(config):
    """Save agent configuration."""
    config_file = Path(".devin/agent_config.json")
    
    try:
        config["last_updated"] = datetime.now().isoformat()
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2)
        return True
    except Exception as e:
        print(f"Error saving agent configuration: {e}", file=sys.stderr)
        return False

def switch_agent(agent_name):
    """Switch to specified agent."""
    agent_key = agent_name.lower()
    
    if agent_key not in AVAILABLE_AGENTS:
        print(f"Error: Unknown agent '{agent_name}'", file=sys.stderr)
        print(f"Available agents: {', '.join(AVAILABLE_AGENTS.keys())}", file=sys.stderr)
        return False
    
    agent_info = AVAILABLE_AGENTS[agent_key]
    
    # Update configuration
    config = load_agent_config()
    config['current_agent'] = agent_info['name']
    
    if save_agent_config(config):
        # Update environment variables
        os.environ['DEVIN_CURRENT_AGENT'] = agent_info['name']
        os.environ['DEVIN_CURRENT_SKILL'] = agent_key
        
        print(f"Switched to: {agent_info['name']}")
        print(f"Description: {agent_info['description']}")
        print(f"Scope: {agent_info['scope']}")
        print(f"Best For: {agent_info['best_for']}")
        
        # Log to session file if available
        session_file = os.environ.get('DEVIN_SESSION_FILE')
        if session_file:
            try:
                session_file_path = Path(session_file)
                if session_file_path.exists():
                    with open(session_file_path, 'a', encoding='utf-8') as f:
                        f.write(f"\n## Agent Switch\n")
                        f.write(f"**Timestamp**: {datetime.now().isoformat()}\n")
                        f.write(f"**New Agent**: {agent_info['name']}\n")
                        f.write(f"**Previous Agent**: {config.get('default_agent', 'Architect')}\n")
                        f.write("---\n")
            except Exception as e:
                pass
        
        return True
    else:
        print("Error: Failed to update agent configuration", file=sys.stderr)
        return False

def main():
    """Main agent selection logic."""
    print("=== Agent Selection Skill ===")
    
    # Check if agent name provided as argument
    if len(sys.argv) > 1:
        agent_name = sys.argv[1]
        if switch_agent(agent_name):
            return 0
        else:
            return 1
    
    # No argument provided - this skill should use ask_user_question
    # The skill body will handle the interactive menu
    config = load_agent_config()
    current_agent = config.get('current_agent', 'Architect')
    
    print(f"Current Agent: {current_agent}")
    print("This skill should use ask_user_question to present the agent selection menu.")
    print("The skill implementation in SKILL.md will handle the interactive selection.")
    
    return 0

if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
