#!/usr/bin/env python3
"""
Configuration Validation Hook - PreToolUse
Validates JSON structure, required fields, and configuration integrity
"""

import json
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple

# Project root
PROJECT_ROOT = Path("C:/SovereignAI")

# Required fields for different config types
CONFIG_REQUIREMENTS = {
    "phase_permissions.json": {
        "required_keys": ["phase_0", "phase_1", "phase_2", "phase_3", "phase_4", "phase_5"],
        "phase_structure": ["name", "allowed_tools", "allowed_file_operations", "forbidden_operations", "required_completions", "description"]
    },
    "governance_rules.json": {
        "required_keys": ["governance_rules", "hook_configuration"],
        "optional_keys": ["file_protection", "operation_restrictions"]
    }
}


def validate_json_structure(content: str) -> Tuple[bool, Optional[str]]:
    """Validate JSON structure."""
    try:
        json.loads(content)
        return True, None
    except json.JSONDecodeError as e:
        return False, f"Invalid JSON: {e}"


def validate_config_requirements(content: str, config_name: str) -> Tuple[bool, List[str]]:
    """Validate configuration requirements."""
    issues = []
    
    try:
        config_data = json.loads(content)
        
        # Get requirements for this config type
        requirements = CONFIG_REQUIREMENTS.get(config_name, {})
        
        # Check required top-level keys
        for key in requirements.get("required_keys", []):
            if key not in config_data:
                issues.append(f"Missing required key: {key}")
        
        # Check phase structure if applicable
        phase_structure = requirements.get("phase_structure", [])
        if phase_structure:
            for phase_key, phase_data in config_data.items():
                if phase_key.startswith("phase_"):
                    for field in phase_structure:
                        if field not in phase_data:
                            issues.append(f"Phase {phase_key} missing field: {field}")
        
    except Exception as e:
        issues.append(f"Configuration validation error: {e}")
    
    return len(issues) == 0, issues


def main():
    """Main hook execution."""
    try:
        # Read event data from stdin
        input_data = json.loads(sys.stdin.read())
        hook_event = input_data.get("hook_event_name", "PreToolUse")
        
        if hook_event != "PreToolUse":
            print(json.dumps({"hookSpecificOutput": {"hookEventName": hook_event}}))
            sys.exit(0)
        
        tool_name = input_data.get("tool_name", "")
        tool_input = input_data.get("tool_input", {})
        
        # Only validate write operations on Config/ files
        if tool_name != "write":
            print(json.dumps({"hookSpecificOutput": {"hookEventName": "PreToolUse"}}))
            sys.exit(0)
        
        file_path = tool_input.get("file_path", "")
        
        if not file_path or "Config/" not in file_path:
            print(json.dumps({"hookSpecificOutput": {"hookEventName": "PreToolUse"}}))
            sys.exit(0)
        
        # Determine config name from file path
        config_name = Path(file_path).name
        
        # For write operations, validate the content being written
        if "content" in tool_input:
            content = tool_input["content"]
            
            # Validate JSON structure
            is_valid_json, json_error = validate_json_structure(content)
            if not is_valid_json:
                output = {
                    "hookSpecificOutput": {
                        "hookEventName": "PreToolUse",
                        "permissionDecision": "deny",
                        "permissionDecisionReason": json_error
                    }
                }
                print(json.dumps(output))
                sys.exit(2)
            
            # Validate configuration requirements
            is_valid_config, config_issues = validate_config_requirements(content, config_name)
            if not is_valid_config:
                error_message = "Configuration validation failed: " + "; ".join(config_issues)
                output = {
                    "hookSpecificOutput": {
                        "hookEventName": "PreToolUse",
                        "permissionDecision": "deny",
                        "permissionDecisionReason": error_message
                    }
                }
                print(json.dumps(output))
                sys.exit(2)
        
        print(json.dumps({"hookSpecificOutput": {"hookEventName": "PreToolUse"}}))
        sys.exit(0)
        
    except Exception as e:
        print(f"Configuration validation error: {e}", file=sys.stderr)
        print(json.dumps({"hookSpecificOutput": {"hookEventName": "PreToolUse"}}))
        sys.exit(1)


if __name__ == "__main__":
    main()