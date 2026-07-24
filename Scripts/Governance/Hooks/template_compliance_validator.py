#!/usr/bin/env python3
"""
Template Compliance Validation Hook - PreToolUse
Validates workflow files against Workflow/Workflow_Template.md structure
Automatically enforces template compliance before allowing writes
"""

import json
import sys
import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple

# Project root
PROJECT_ROOT = Path("C:/SovereignAI")

# Required sections for workflow template
REQUIRED_WORKFLOW_SECTIONS = [
    "Header",
    "Purpose", 
    "Scope",
    "Gate Enforcement",
    "Workflow Steps",
    "Workflow Logging",
    "Workflow Closure",
    "Quality Metrics"
]

# Required header fields
REQUIRED_HEADER_FIELDS = [
    "Title",
    "File",
    "Workflow Name", 
    "Description",
    "Status",
    "Template Compliance"
]


def load_template() -> Optional[str]:
    """Load workflow template for comparison."""
    template_file = PROJECT_ROOT / "Workflow" / "Workflow_Template.md"
    if template_file.exists():
        try:
            with open(template_file, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            print(f"Error loading template: {e}", file=sys.stderr)
    return None


def validate_workflow_structure(content: str) -> Tuple[bool, List[str]]:
    """Validate workflow file structure against template requirements."""
    issues = []
    
    # Check for required header fields
    for field in REQUIRED_HEADER_FIELDS:
        # Look for field in content (case-insensitive)
        pattern = rf"^\*\*{field}\*\*:|^{field}:"
        if not re.search(pattern, content, re.MULTILINE | re.IGNORECASE):
            issues.append(f"Missing required header field: {field}")
    
    # Check for required sections
    for section in REQUIRED_WORKFLOW_SECTIONS:
        # Look for section headers (### or ## level)
        pattern = rf"^#{1,3}\s*{re.escape(section)}\s*$"
        if not re.search(pattern, content, re.MULTILINE | re.IGNORECASE):
            issues.append(f"Missing required section: {section}")
    
    # Check for Template Compliance field in header
    if "Template Compliance" not in content and "template compliance" not in content.lower():
        issues.append("Missing 'Template Compliance' field in header")
    
    # Check for Gate Enforcement section before Workflow Steps
    gate_enforcement = re.search(r"Gate Enforcement", content, re.IGNORECASE)
    workflow_steps = re.search(r"Workflow Steps", content, re.IGNORECASE)
    
    if gate_enforcement and workflow_steps:
        if gate_enforcement.start() > workflow_steps.start():
            issues.append("Gate Enforcement section must come before Workflow Steps")
    
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
        
        # Only validate write and edit operations on Workflow/ files
        if tool_name not in ["write", "edit"]:
            print(json.dumps({"hookSpecificOutput": {"hookEventName": "PreToolUse"}}))
            sys.exit(0)
        
        file_path = tool_input.get("file_path", "")
        
        if not file_path or "Workflow/" not in file_path:
            print(json.dumps({"hookSpecificOutput": {"hookEventName": "PreToolUse"}}))
            sys.exit(0)
        
        # For write operations, validate the content being written
        if tool_name == "write" and "content" in tool_input:
            content = tool_input["content"]
            is_valid, issues = validate_workflow_structure(content)
            
            if not is_valid:
                error_message = "Template compliance validation failed: " + "; ".join(issues)
                output = {
                    "hookSpecificOutput": {
                        "hookEventName": "PreToolUse",
                        "permissionDecision": "deny",
                        "permissionDecisionReason": error_message
                    }
                }
                print(json.dumps(output))
                sys.exit(2)
        
        # For edit operations, we can't easily validate without the full content
        # Allow but log a warning
        if tool_name == "edit":
            print(json.dumps({"hookSpecificOutput": {"hookEventName": "PreToolUse"}}))
            sys.exit(0)
        
        print(json.dumps({"hookSpecificOutput": {"hookEventName": "PreToolUse"}}))
        sys.exit(0)
        
    except Exception as e:
        print(f"Template compliance validator error: {e}", file=sys.stderr)
        print(json.dumps({"hookSpecificOutput": {"hookEventName": "PreToolUse"}}))
        sys.exit(1)


if __name__ == "__main__":
    main()