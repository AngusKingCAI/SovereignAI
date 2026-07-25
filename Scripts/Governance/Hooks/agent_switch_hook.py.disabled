#!/usr/bin/env python3
"""
Agent switching hook for UserPromptExpansion.
Automatically detects agent switching commands in user messages and updates configuration without using model tokens.
"""

import sys
import json
import os
import re
from pathlib import Path
from datetime import datetime

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))
from hook_utils import get_verbosity, should_print, show_hook_header, show_hook_result, show_hook_error

# Available agents
AVAILABLE_AGENTS = {
    "architect": "Architect",
    "executor": "Executor", 
    "planner": "Planner",
    "researcher": "Researcher",
    "reviewer": "Reviewer"
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
        return False

def detect_agent_switch(prompt):
    """Detect agent switching commands in user prompt."""
    # Pattern: /agent [agent-name]
    agent_pattern = r'/agent\s+(\w+)'
    match = re.search(agent_pattern, prompt.lower())
    
    if match:
        agent_name = match.group(1)
        if agent_name in AVAILABLE_AGENTS:
            return AVAILABLE_AGENTS[agent_name]
    
    return None

def switch_agent(new_agent):
    """Switch to specified agent."""
    config = load_agent_config()
    old_agent = config.get('current_agent', 'Architect')
    
    if new_agent == old_agent:
        return True, f"Already using {new_agent}"
    
    config['current_agent'] = new_agent
    
    if save_agent_config(config):
        # Update environment variables
        os.environ['DEVIN_CURRENT_AGENT'] = new_agent
        os.environ['DEVIN_CURRENT_SKILL'] = new_agent.lower()
        
        # Log to session file if available
        session_file = os.environ.get('DEVIN_SESSION_FILE')
        if session_file:
            try:
                session_file_path = Path(session_file)
                if session_file_path.exists():
                    with open(session_file_path, 'a', encoding='utf-8') as f:
                        f.write(f"\n## Agent Switch (Hook-Based)\n")
                        f.write(f"**Timestamp**: {datetime.now().isoformat()}\n")
                        f.write(f"**New Agent**: {new_agent}\n")
                        f.write(f"**Previous Agent**: {old_agent}\n")
                        f.write(f"**Method**: Hook-based automatic detection\n")
                        f.write("---\n")
            except Exception as e:
                pass
        
        return True, f"Switched from {old_agent} to {new_agent}"
    else:
        return False, "Failed to update agent configuration"

def main():
    """Main agent switching hook logic."""
    verbosity = get_verbosity()
    show_hook_header("Agent Switching Hook", verbosity)
    
    # Get hook environment from stdin
    try:
        data = sys.stdin.read()
        if data:
            env_vars = json.loads(data)
        else:
            env_vars = {}
    except:
        env_vars = {}
    
    # Extract user prompt from UserPromptExpansion event
    # UserPromptExpansion has original_input and expanded_prompt
    original_input = env_vars.get('original_input', '')
    expanded_prompt = env_vars.get('expanded_prompt', '')
    
    # Check both original_input and expanded_prompt for agent switching command
    prompt_to_check = original_input if original_input else expanded_prompt
    
    # Detect agent switching command
    new_agent = detect_agent_switch(prompt_to_check)
    
    if new_agent:
        # Perform agent switch
        success, message = switch_agent(new_agent)
        
        show_hook_result(f"Agent switch: {message}", success=success, verbosity=verbosity)
        
        if success:
            # Return hook specific output to inform the agent
            hook_output = {
                "hookSpecificOutput": {
                  "hookEventName": "UserPromptExpansion",
                  "additionalContext": f"Agent switched to {new_agent}."
                }
            }
            print(json.dumps(hook_output))
        
        return 0
    
    return 0

if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except Exception as e:
        print(f"Error in agent switching hook: {e}", file=sys.stderr)
        sys.exit(1)
