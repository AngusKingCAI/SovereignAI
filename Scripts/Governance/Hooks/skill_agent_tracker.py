#!/usr/bin/env python3
"""
Skill agent tracker hook for PreToolUse.
Tracks skill invocations and updates agent configuration to maintain persistent agent state.
"""

import sys
import json
import os
from pathlib import Path
from datetime import datetime

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))
from hook_utils import get_verbosity, should_print, show_hook_header, show_hook_result

def update_agent_config(agent_name):
    """Update agent configuration file with current agent."""
    config_file = Path("C:/SovereignAI/.devin/agent_config.json")
    
    if not config_file.exists():
        # Create default config
        default_config = {
            "default_agent": "Architect",
            "current_agent": agent_name,
            "last_updated": datetime.now().isoformat(),
            "session_count": 0
        }
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(default_config, f, indent=2)
        return True
    
    try:
        with open(config_file, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        config['current_agent'] = agent_name
        config['last_updated'] = datetime.now().isoformat()
        
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2)
        
        return True
    except Exception as e:
        return False

def detect_skill_from_command(command):
    """Detect skill invocation from command."""
    # Check for skill tool invocation
    skill_patterns = {
        'architect': 'architect',
        'executor': 'executor', 
        'planner': 'planner',
        'researcher': 'researcher',
        'reviewer': 'reviewer'
    }
    
    command_lower = command.lower()
    for skill_name, pattern in skill_patterns.items():
        if pattern in command_lower:
            return skill_name.capitalize()
    
    return None

def main():
    """Main skill agent tracker logic."""
    verbosity = get_verbosity()
    show_hook_header("Skill Agent Tracker", verbosity)
    
    # Get hook environment from stdin
    try:
        data = sys.stdin.read()
        if data:
            env_vars = json.loads(data)
        else:
            env_vars = {}
    except:
        env_vars = {}
    
    # Extract tool information
    tool_name = env_vars.get('tool_name', '')
    tool_input = env_vars.get('tool_input', {})
    
    # Check if this is a skill invocation
    detected_agent = None
    
    if tool_name == 'skill':
        # Direct skill invocation
        skill_name = tool_input.get('skill', '')
        if skill_name:
            detected_agent = skill_name.capitalize()
    elif tool_name == 'exec':
        # Check command for skill invocation
        command = tool_input.get('command', '')
        detected_agent = detect_skill_from_command(command)
    
    if detected_agent:
        # Update agent configuration
        success = update_agent_config(detected_agent)
        
        if success:
            os.environ['DEVIN_CURRENT_AGENT'] = detected_agent
            show_hook_result(f"Agent updated to: {detected_agent}", success=True, verbosity=verbosity)
        else:
            show_hook_result("Failed to update agent configuration", success=False, verbosity=verbosity)
    else:
        # No skill detected, continue with current agent
        show_hook_result("No skill change detected", success=True, verbosity=verbosity)
    
    return 0

if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except Exception as e:
        print(f"Error in skill agent tracker: {e}", file=sys.stderr)
        sys.exit(1)
