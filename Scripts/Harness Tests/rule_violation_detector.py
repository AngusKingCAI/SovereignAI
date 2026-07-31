#!/usr/bin/env python3
"""
PostToolUse hook to detect rule violations and inject context for user decision.

This script:
1. Receives PostToolUse event data via stdin
2. Checks for common rule violations (SSOT, file placement, etc.)
3. If violations found, injects additionalContext about the violation
4. Returns JSON output with violation details for agent to handle
"""

import json
import sys
from pathlib import Path

def check_ssot_violation(file_path_str: str) -> list:
    """Check for SSOT violations like index.md files."""
    violations = []
    
    if not file_path_str:
        return violations
        
    file_path = Path(file_path_str)
    file_name = file_path.name.lower()
    
    # Check for index.md violations
    if "index.md" in file_name:
        # Allow only in specific locations (historical logs)
        allowed_locations = ["logs/", "logs/.archived/"]
        file_str = str(file_path).lower()
        
        if not any(loc in file_str for loc in allowed_locations):
            violations.append({
                "type": "SSOT Violation",
                "rule": "Never create index.md files",
                "file": str(file_path),
                "description": "index.md files violate SSOT principles. Use STRUCTURE.md as the single source of truth."
            })
    
    return violations

def check_file_placement_violation(file_path_str: str) -> list:
    """Check for file placement violations."""
    violations = []
    
    if not file_path_str:
        return violations
        
    file_path = Path(file_path_str)
    
    # Check for files in wrong directories
    # Example: test files in App/ directory
    if "App/" in str(file_path) and ("test" in file_path.name.lower()):
        violations.append({
            "type": "File Placement Violation",
            "rule": "Place IDE harness tests in Scripts/Harness Tests/ only",
            "file": str(file_path),
            "description": "Test files should be in Scripts/Harness Tests/, not App/ directory."
        })
    
    return violations

def detect_violations(tool_name: str, tool_input: dict) -> list:
    """Detect rule violations based on tool and input."""
    violations = []
    
    # Only check write/edit operations
    if tool_name not in ["write", "edit"]:
        return violations
    
    file_path = tool_input.get("file_path", "")
    
    # Check for various violations
    violations.extend(check_ssot_violation(file_path))
    violations.extend(check_file_placement_violation(file_path))
    
    return violations

def main():
    """Main hook logic."""
    try:
        # Read event data from stdin
        input_data = json.load(sys.stdin)
        
        tool_name = input_data.get("tool_name", "")
        tool_input = input_data.get("tool_input", {})
        
        # Detect violations
        violations = detect_violations(tool_name, tool_input)
        
        if violations:
            # Format violation message for additionalContext
            violation_messages = []
            for violation in violations:
                violation_messages.append(
                    f"RULE VIOLATION DETECTED: {violation['type']}\n"
                    f"Rule: {violation['rule']}\n"
                    f"File: {violation['file']}\n"
                    f"Description: {violation['description']}\n"
                    f"Please ask user: [Allow violation] or [Deny and cleanup]?"
                )
            
            context_text = "\n\n".join(violation_messages)
            
            # Return additionalContext for next turn
            output = {
                "hookSpecificOutput": {
                    "hookEventName": "PostToolUse",
                    "additionalContext": context_text
                }
            }
            
            print(json.dumps(output))
        else:
            # No violations, return empty/allow
            print(json.dumps({}))
            
    except Exception as e:
        # Log error but don't block
        error_output = {
            "hookSpecificOutput": {
                "hookEventName": "PostToolUse", 
                "additionalContext": f"Rule violation detector error: {str(e)}"
            }
        }
        print(json.dumps(error_output))
        sys.exit(0)  # Don't block on errors

if __name__ == "__main__":
    main()