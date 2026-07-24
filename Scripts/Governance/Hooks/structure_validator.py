#!/usr/bin/env python3
"""
Structure Validator Hook - PreToolUse
Validates directory structure and file naming conventions before file operations
Blocks violations of IDE architecture rules automatically
"""

import json
import sys
import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple

# Project root
PROJECT_ROOT = Path("C:/SovereignAI")

# IDE Architecture Rules for file naming and structure
FILE_NAMING_RULES = {
    "agent_files": {
        "pattern": r"^AGENTS\.md$",
        "allowed_locations": ["Agents/", "Agents/Architect/", "Agents/Planner/", "Agents/Executor/", "Agents/Researcher/", "Agents/Reviewer/"],
        "description": "Agent documentation files must be AGENTS.md (uppercase)"
    },
    "rule_files": {
        "pattern": r"^[A-Z][a-zA-Z]+_Rules\.md$",
        "allowed_locations": ["Rules/", "Rules/Architect/", "Rules/Planner/", "Rules/Executor/", "Rules/Researcher/", "Rules/Reviewer/"],
        "description": "Rule files must follow {Agent}_Rules.md pattern"
    },
    "workflow_files": {
        "pattern": r"^[A-Z][a-zA-Z]+_[A-Z][a-zA-Z_]+\.md$",
        "allowed_locations": ["Workflow/", "Workflow/Architect/", "Workflow/Planner/", "Workflow/Executor/", "Workflow/Researcher/", "Workflow/Reviewer/"],
        "description": "Workflow files must follow {Agent}_{Workflow_Name}.md pattern"
    },
    "log_files": {
        "pattern": r".*\.jsonl$",
        "allowed_locations": ["Logs/"],
        "description": "Log files must use .jsonl extension"
    }
}

# Directory naming rules
DIRECTORY_RULES = {
    "pascal_case": {
        "pattern": r"^[A-Z][a-zA-Z0-9]*$",
        "description": "Directory names must use PascalCase"
    },
    "mandatory_directories": [
        "Agents", "Rules", "Workflow", "Scripts", "Logs", "Docs"
    ],
    "forbidden_root_directories": [
        "App", "node_modules", ".git"
    ]
}


def validate_file_name(file_path: str) -> Tuple[bool, Optional[str]]:
    """Validate file name against naming conventions."""
    file_name = Path(file_path).name
    
    # Check against file naming rules
    for rule_type, rule_config in FILE_NAMING_RULES.items():
        pattern = rule_config["pattern"]
        if re.match(pattern, file_name):
            # Check if location is allowed
            allowed_locations = rule_config["allowed_locations"]
            if not any(file_path.startswith(loc) for loc in allowed_locations):
                return False, f"File {file_name} matches {rule_type} pattern but is not in allowed location: {allowed_locations}"
            return True, None
    
    # If no pattern matches, check if it's in a restricted directory
    for rule_type, rule_config in FILE_NAMING_RULES.items():
        allowed_locations = rule_config["allowed_locations"]
        if any(file_path.startswith(loc) for loc in allowed_locations):
            return False, f"File {file_name} is in {rule_type} directory but doesn't match naming pattern: {rule_config['pattern']}"
    
    return True, None


def validate_directory_name(dir_path: str) -> Tuple[bool, Optional[str]]:
    """Validate directory name against PascalCase convention."""
    dir_name = Path(dir_path).name
    
    # Skip validation for system directories starting with dot
    if dir_name.startswith('.'):
        return True, None
    
    # Check PascalCase pattern
    pattern = DIRECTORY_RULES["pascal_case"]["pattern"]
    if not re.match(pattern, dir_name):
        return False, f"Directory {dir_name} must use PascalCase (pattern: {pattern})"
    
    return True, None


def validate_against_mandatory_structure(file_path: str) -> Tuple[bool, Optional[str]]:
    """Ensure operation doesn't violate mandatory directory structure."""
    # Check if trying to create directory at root level
    path_parts = Path(file_path).parts
    if len(path_parts) == 1 and PROJECT_ROOT / file_path == PROJECT_ROOT / file_path:
        # Root level operation
        mandatory_dirs = DIRECTORY_RULES["mandatory_directories"]
        forbidden_dirs = DIRECTORY_RULES["forbidden_root_directories"]
        
        if file_path in forbidden_dirs:
            return False, f"Cannot operate on forbidden root directory: {file_path}"
    
    return True, None


def main():
    """Main hook execution."""
    try:
        # Read event data from stdin
        input_data = json.loads(sys.stdin.read())
        hook_event = input_data.get("hook_event_name", "PreToolUse")
        
        if hook_event != "PreToolUse":
            # Only process PreToolUse events
            print(json.dumps({"hookSpecificOutput": {"hookEventName": hook_event}}))
            sys.exit(0)
        
        tool_name = input_data.get("tool_name", "")
        tool_input = input_data.get("tool_input", {})
        
        # Only validate write and edit operations
        if tool_name not in ["write", "edit"]:
            print(json.dumps({"hookSpecificOutput": {"hookEventName": "PreToolUse"}}))
            sys.exit(0)
        
        file_path = tool_input.get("file_path", "")
        
        if not file_path:
            print(json.dumps({"hookSpecificOutput": {"hookEventName": "PreToolUse"}}))
            sys.exit(0)
        
        # Convert to relative path from project root
        try:
            full_path = Path(file_path)
            if full_path.is_absolute():
                relative_path = str(full_path.relative_to(PROJECT_ROOT))
            else:
                relative_path = file_path
        except:
            relative_path = file_path
        
        # Perform validations
        validations = [
            validate_file_name(relative_path),
            validate_against_mandatory_structure(relative_path)
        ]
        
        # Check directory names in path
        path_parts = Path(relative_path).parts[:-1]  # Exclude file name
        for part in path_parts:
            dir_valid, dir_error = validate_directory_name(part)
            if not dir_valid:
                validations.append((False, dir_error))
        
        # Check if any validation failed
        for is_valid, error_msg in validations:
            if not is_valid:
                # Block the operation with exit code 2
                output = {
                    "hookSpecificOutput": {
                        "hookEventName": "PreToolUse",
                        "permissionDecision": "deny",
                        "permissionDecisionReason": f"Structure validation failed: {error_msg}"
                    }
                }
                print(json.dumps(output))
                sys.exit(2)
        
        # All validations passed
        print(json.dumps({"hookSpecificOutput": {"hookEventName": "PreToolUse"}}))
        sys.exit(0)
        
    except Exception as e:
        print(f"Structure validator error: {e}", file=sys.stderr)
        # Return empty output on error (non-blocking)
        print(json.dumps({"hookSpecificOutput": {"hookEventName": "PreToolUse"}}))
        sys.exit(1)


if __name__ == "__main__":
    main()