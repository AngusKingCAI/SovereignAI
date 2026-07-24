#!/usr/bin/env python3
"""
Log File Organization Hook - PostToolUse
Automatically organizes log files into proper directory structure with timestamps
"""

import json
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, Optional

# Project root
PROJECT_ROOT = Path("C:/SovereignAI")


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


def organize_log_file(file_path: str, agent_type: str) -> Optional[str]:
    """Organize log file into proper directory structure."""
    log_path = PROJECT_ROOT / file_path
    
    if not log_path.exists():
        return None
    
    # Determine target directory based on file type
    if "session" in file_path.lower():
        target_dir = PROJECT_ROOT / "Logs" / agent_type / "Sessions"
    elif "gate" in file_path.lower():
        target_dir = PROJECT_ROOT / "Logs" / agent_type / "Gates"
    elif "conversation" in file_path.lower():
        target_dir = PROJECT_ROOT / "Logs" / agent_type / "Conversations"
    else:
        target_dir = PROJECT_ROOT / "Logs" / agent_type
    
    target_dir.mkdir(parents=True, exist_ok=True)
    
    # Generate timestamped filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    original_name = log_path.name
    new_name = f"{timestamp}_{original_name}"
    
    target_path = target_dir / new_name
    
    # Move file to organized location
    try:
        log_path.rename(target_path)
        return str(target_path.relative_to(PROJECT_ROOT))
    except Exception as e:
        print(f"Error organizing log file: {e}", file=sys.stderr)
        return None


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
        
        # Only organize write operations on Logs/ files
        if tool_name != "write":
            print(json.dumps({"hookSpecificOutput": {"hookEventName": "PostToolUse"}}))
            sys.exit(0)
        
        file_path = tool_input.get("file_path", "")
        
        if not file_path or "Logs/" not in file_path:
            print(json.dumps({"hookSpecificOutput": {"hookEventName": "PostToolUse"}}))
            sys.exit(0)
        
        # Get current agent
        agent_type = get_current_agent()
        
        # Organize the log file
        organized_path = organize_log_file(file_path, agent_type)
        
        if organized_path:
            output = {
                "hookSpecificOutput": {
                    "hookEventName": "PostToolUse",
                    "additionalContext": f"Log file organized to: {organized_path}"
                }
            }
            print(json.dumps(output))
        else:
            print(json.dumps({"hookSpecificOutput": {"hookEventName": "PostToolUse"}}))
        
        sys.exit(0)
        
    except Exception as e:
        print(f"Log file organization error: {e}", file=sys.stderr)
        print(json.dumps({"hookSpecificOutput": {"hookEventName": "PostToolUse"}}))
        sys.exit(1)


if __name__ == "__main__":
    main()