#!/usr/bin/env python3
"""
Agent Documentation Completeness Hook - PostToolUse
Validates AGENTS.md files against Agents/AGENTS_TEMPLATE.md for required sections
Automatically validates agent documentation completeness
"""

import json
import sys
import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple

# Project root
PROJECT_ROOT = Path("C:/SovereignAI")

# Required industry-standard sections for AGENTS.md
REQUIRED_INDUSTRY_SECTIONS = [
    "Agent Name",
    "Purpose",
    "Setup Commands",
    "Code Style",
    "Testing",
    "Boundaries",
    "Security Considerations",
    "Integration Points"
]

# Required SovereignAI framework extensions
REQUIRED_SOVEREIGNAI_EXTENSIONS = [
    "Constitutional Framework",
    "Scope Boundaries",
    "Git Operations Restrictions"
]


def load_agent_template() -> Optional[str]:
    """Load agent template for comparison."""
    template_file = PROJECT_ROOT / "Agents" / "AGENTS_TEMPLATE.md"
    if template_file.exists():
        try:
            with open(template_file, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            print(f"Error loading agent template: {e}", file=sys.stderr)
    return None


def validate_agents_structure(content: str) -> Tuple[bool, List[str]]:
    """Validate AGENTS.md structure against template requirements."""
    issues = []
    
    # Check for required industry-standard sections
    for section in REQUIRED_INDUSTRY_SECTIONS:
        # Look for section headers (### or ## level)
        pattern = rf"^#{1,3}\s*{re.escape(section)}\s*$"
        if not re.search(pattern, content, re.MULTILINE | re.IGNORECASE):
            issues.append(f"Missing required industry-standard section: {section}")
    
    # Check for required SovereignAI framework extensions
    for extension in REQUIRED_SOVEREIGNAI_EXTENSIONS:
        pattern = rf"^#{1,3}\s*{re.escape(extension)}\s*$"
        if not re.search(pattern, content, re.MULTILINE | re.IGNORECASE):
            issues.append(f"Missing required SovereignAI framework extension: {extension}")
    
    # Check for Boundaries section using Always/Ask First/Never pattern
    boundaries_section = re.search(r"Boundaries", content, re.IGNORECASE)
    if boundaries_section:
        boundaries_content = content[boundaries_section.start():]
        if not re.search(r"Always|Ask First|Never", boundaries_content, re.IGNORECASE):
            issues.append("Boundaries section must use Always/Ask First/Never pattern")
    
    # Check for placeholders
    if "{placeholder}" in content or "{PLACEHOLDER}" in content:
        issues.append("Found placeholder text that should be replaced")
    
    # Check file length (industry standard: 60-300 lines)
    line_count = len(content.split('\n'))
    if line_count < 60:
        issues.append(f"AGENTS.md too short ({line_count} lines), industry standard is 60-300 lines")
    elif line_count > 300:
        issues.append(f"AGENTS.md too long ({line_count} lines), industry standard is 60-300 lines")
    
    return len(issues) == 0, issues


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
        
        # Only validate write operations on AGENTS.md files
        if tool_name != "write":
            print(json.dumps({"hookSpecificOutput": {"hookEventName": "PostToolUse"}}))
            sys.exit(0)
        
        file_path = tool_input.get("file_path", "")
        
        if not file_path or "AGENTS.md" not in file_path:
            print(json.dumps({"hookSpecificOutput": {"hookEventName": "PostToolUse"}}))
            sys.exit(0)
        
        # For write operations, validate the content being written
        if "content" in tool_input:
            content = tool_input["content"]
            is_valid, issues = validate_agents_structure(content)
            
            if not is_valid:
                # Log validation failure but don't block (PostToolUse is non-blocking)
                warning_message = "Agent documentation completeness check failed: " + "; ".join(issues)
                print(f"WARNING: {warning_message}", file=sys.stderr)
                
                # Return with additional context about validation issues
                output = {
                    "hookSpecificOutput": {
                        "hookEventName": "PostToolUse",
                        "additionalContext": f"⚠️ Documentation validation: {len(issues)} issues found - {warning_message}"
                    }
                }
                print(json.dumps(output))
                sys.exit(0)
        
        print(json.dumps({"hookSpecificOutput": {"hookEventName": "PostToolUse"}}))
        sys.exit(0)
        
    except Exception as e:
        print(f"Agent documentation completeness error: {e}", file=sys.stderr)
        print(json.dumps({"hookSpecificOutput": {"hookEventName": "PostToolUse"}}))
        sys.exit(1)


if __name__ == "__main__":
    main()