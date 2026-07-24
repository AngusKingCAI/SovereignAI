#!/usr/bin/env python3
"""
Verbosity control skill implementation.
Allows users to control hook output verbosity.
"""

import sys
import json
from pathlib import Path
from datetime import datetime

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
        print(f"Error saving verbosity configuration: {e}", file=sys.stderr)
        return False

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
    """Main verbosity control logic."""
    print("=== Verbosity Control Skill ===")
    
    # Check if level provided as argument
    if len(sys.argv) > 1:
        level = sys.argv[1].lower()
        if level in VALID_LEVELS:
            success, message = set_verbosity(level)
            print(message)
            if success:
                print(show_verbosity_info(level))
            return 0 if success else 1
        else:
            print(f"Error: Invalid verbosity level '{level}'", file=sys.stderr)
            print(f"Valid levels: {', '.join(VALID_LEVELS)}", file=sys.stderr)
            return 1
    
    # No argument provided - show current level and options
    config = load_verbosity_config()
    current_level = config.get('verbosity', 'normal')
    
    print(f"Current verbosity: {current_level}")
    print()
    print("Available levels:")
    for level in VALID_LEVELS:
        marker = " (current)" if level == current_level else ""
        print(f"  - {level}{marker}")
    print()
    print("Usage: /Verbosity [level]")
    print("Example: /Verbosity quiet")
    
    return 0

if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
