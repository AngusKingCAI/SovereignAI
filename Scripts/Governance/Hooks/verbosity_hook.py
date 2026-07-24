#!/usr/bin/env python3
"""
Verbosity control hook for UserPromptExpansion.
Automatically detects verbosity control commands and updates configuration without using model tokens.
"""

import sys
import json
import re
from pathlib import Path
from datetime import datetime

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))
from hook_utils import get_verbosity, should_print, show_hook_header, show_hook_result, show_hook_error

# Valid verbosity levels
VALID_LEVELS = ["quiet", "minimal", "normal", "verbose"]

def load_verbosity_config():
    """Load verbosity configuration."""
    verbosity_file = Path(".devin/verbosity.json")
    
    if not verbosity_file.exists():
        return {
            "verbosity": "normal",
            "timestamp": datetime.now().isoformat()
        }
    
    try:
        with open(verbosity_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        return {
            "verbosity": "normal",
            "timestamp": datetime.now().isoformat()
        }

def save_verbosity_config(config):
    """Save verbosity configuration."""
    verbosity_file = Path(".devin/verbosity.json")
    
    try:
        config["timestamp"] = datetime.now().isoformat()
        with open(verbosity_file, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2)
        return True
    except Exception as e:
        return False

def detect_verbosity_command(prompt):
    """Detect verbosity control commands in user prompt."""
    # Pattern: /Verbosity [level] or /verbosity [level]
    verbosity_pattern = r'/Verbosity\s+(\w+)'
    match = re.search(verbosity_pattern, prompt)
    
    if match:
        level = match.group(1).lower()
        if level in VALID_LEVELS:
            return level
    
    return None

def show_verbosity_info(current_level):
    """Show current verbosity level and behavior."""
    level_descriptions = {
        "quiet": "Only critical errors and security violations shown",
        "minimal": "Pass/fail results and failures shown", 
        "normal": "Full hook output with all operations (default)",
        "verbose": "Detailed execution information for debugging"
    }
    
    info = f"Current verbosity: {current_level} - {level_descriptions.get(current_level, 'Unknown')}"
    return info

def set_verbosity(new_level):
    """Set verbosity level."""
    config = load_verbosity_config()
    old_level = config.get('verbosity', 'normal')
    
    if new_level == old_level:
        return True, f"Already using {new_level}"
    
    config['verbosity'] = new_level
    
    if save_verbosity_config(config):
        return True, f"Verbosity changed from {old_level} to {new_level}"
    else:
        return False, "Failed to update verbosity configuration"

def main():
    """Main verbosity control hook logic."""
    verbosity = get_verbosity()
    show_hook_header("Verbosity Control Hook", verbosity)
    
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
    
    # Check both original_input and expanded_prompt for verbosity command
    prompt_to_check = original_input if original_input else expanded_prompt
    
    # Detect verbosity control command
    new_level = detect_verbosity_command(prompt_to_check)
    
    if new_level:
        # Perform verbosity change
        success, message = set_verbosity(new_level)
        
        show_hook_result(f"Verbosity change: {message}", success=success, verbosity=verbosity)
        
        if success:
            # Show verbosity info
            info = show_verbosity_info(new_level)
            
            # Return hook specific output to inform the agent
            hook_output = {
                "hookSpecificOutput": {
                  "hookEventName": "UserPromptExpansion",
                  "additionalContext": f"{info}. Valid levels: quiet, minimal, normal, verbose"
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
        print(f"Error in verbosity control hook: {e}", file=sys.stderr)
        sys.exit(1)
