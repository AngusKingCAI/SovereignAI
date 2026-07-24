#!/usr/bin/env python3
"""
Plan structure validation hook for PreToolUse.
Validates plan structure using deterministic parsing instead of LLM analysis.
"""

import sys
import json
import re
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))
from hook_utils import get_verbosity, should_print, show_hook_header, show_hook_result, show_hook_error, show_hook_error_details

def validate_plan_structure(file_path):
    """Validate plan structure using deterministic parsing."""
    try:
        with open(file_path) as f:
            content = f.read()
    except Exception as e:
        return False, f"Could not read plan file: {e}"
    
    # Check for required header fields
    required_header_fields = [
        "Workflow Name",
        "Description", 
        "Status",
        "Template Compliance"
    ]
    
    missing_fields = []
    for field in required_header_fields:
        if f"**{field}**:" not in content:
            missing_fields.append(field)
    
    if missing_fields:
        return False, f"Missing required header fields: {missing_fields}"
    
    # Check for required sections
    required_sections = [
        "Purpose",
        "Scope",
        "Gate Enforcement", 
        "Workflow Steps"
    ]
    
    missing_sections = []
    for section in required_sections:
        if f"## {section}" not in content:
            missing_sections.append(section)
    
    if missing_sections:
        return False, f"Missing required sections: {missing_sections}"
    
    # Check Scope section has Included/Excluded subsections
    if "## Scope" in content:
        scope_section = content.split("## Scope")[1].split("##")[0] if "##" in content.split("## Scope")[1] else content.split("## Scope")[1]
        if "### Included" not in scope_section or "### Excluded" not in scope_section:
            return False, "Scope section must have Included/Excluded subsections"
    
    # Check Gate Enforcement section
    if "## Gate Enforcement" in content:
        gate_section = content.split("## Gate Enforcement")[1].split("##")[0] if "##" in content.split("## Gate Enforcement")[1] else content.split("## Gate Enforcement")[1]
        if "GATE PATTERN" not in gate_section and "EVERY STEP HAS A GATE" not in gate_section:
            return False, "Gate Enforcement section must specify gate pattern"
    
    # Check Workflow Steps section
    if "## Workflow Steps" in content:
        steps_section = content.split("## Workflow Steps")[1]
        # Check for at least one step
        if not re.search(r'### Step \d+', steps_section):
            return False, "Workflow Steps section must contain at least one step"
    
    # Check for proper markdown formatting
    if not re.search(r'^# ', content, re.MULTILINE):
        return False, "Plan must have proper markdown heading structure"
    
    return True, "Plan structure validation passed"

def main():
    """Main plan structure validation logic."""
    verbosity = get_verbosity()
    show_hook_header("Plan Structure Validation", verbosity)
    
    # Get hook environment from stdin
    try:
        data = sys.stdin.read()
        if data:
            env_vars = json.loads(data)
        else:
            env_vars = {}
    except:
        env_vars = {}
    
    # Extract file path from tool input
    tool_input = env_vars.get('tool_input', {})
    file_path = tool_input.get('file_path', '')
    
    if not file_path:
        show_hook_result("No file path provided, allowing operation", success=True, verbosity=verbosity)
        return 0
    
    # Check if this is a plan file (in Workflow/Planner/ or similar)
    file_path = Path(file_path)
    if 'Plan' not in file_path.name and 'plan' not in file_path.name.lower():
        show_hook_result(f"File {file_path.name} is not a plan file, skipping validation", success=True, verbosity=verbosity)
        return 0
    
    # Validate plan structure
    allowed, message = validate_plan_structure(file_path)
    
    show_hook_result(f"Validation result: {message}", success=allowed, verbosity=verbosity)
    
    if not allowed:
        show_hook_error("Plan structure validation failed - operation blocked", verbosity)
        show_hook_error_details(f"Plan structure validation failed - operation blocked", verbosity)
        # Return permission decision to block
        output = {
            "hookSpecificOutput": {
                "hookEventName": "PreToolUse",
                "permissionDecision": "deny",
                "permissionDecisionReason": message
            }
        }
        print(json.dumps(output, indent=2))
        return 2  # Block the operation
    
    show_hook_result("Plan structure validation passed", success=True, verbosity=verbosity)
    return 0  # Allow the operation

if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except Exception as e:
        print(f"Error in plan structure validation: {e}", file=sys.stderr)
        sys.exit(1)
