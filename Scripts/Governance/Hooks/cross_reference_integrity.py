#!/usr/bin/env python3
"""
Cross-Reference Integrity Hook - PostToolUse
Validates that file references between Rules/, Workflow/, Agents/ are valid
Automatically checks cross-reference integrity for infrastructure files
"""

import json
import sys
import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple

# Project root
PROJECT_ROOT = Path("C:/SovereignAI")

# Valid reference patterns
VALID_REFERENCE_PATTERNS = [
    r"Rules/[A-Za-z]+/[A-Za-z_]+\.md",
    r"Workflow/[A-Za-z]+/[A-Za-z_]+\.md", 
    r"Agents/[A-Za-z]+/AGENTS\.md",
    r"Scripts/[A-Za-z]+/[A-Za-z_]+\.py",
    r"Docs/[A-Za-z]+/[A-Za-z_]+\.md"
]


def extract_references(content: str) -> List[str]:
    """Extract file references from content."""
    references = []
    
    # Match markdown file references
    markdown_refs = re.findall(r'\[(.*?)\]\(([^)]+\.md)\)', content)
    for _, ref in markdown_refs:
        references.append(ref)
    
    # Match inline file paths
    path_refs = re.findall(r'([A-Za-z/]+/[A-Za-z_]+\.(md|py|json))', content)
    for ref, _ in path_refs:
        references.append(ref)
    
    # Match code block file references
    code_refs = re.findall(r'`([^`]+\.(md|py|json))`', content)
    for ref, _ in code_refs:
        references.append(ref)
    
    return references


def validate_reference_exists(reference: str) -> bool:
    """Check if a referenced file exists."""
    # Convert reference to absolute path
    ref_path = PROJECT_ROOT / reference
    return ref_path.exists()


def validate_cross_references(content: str, file_path: str) -> Tuple[bool, List[str]]:
    """Validate cross-references in content."""
    issues = []
    
    references = extract_references(content)
    
    for ref in references:
        # Skip external references (http://, https://, etc.)
        if ref.startswith(('http://', 'https://', '#')):
            continue
            
        # Check if reference exists
        if not validate_reference_exists(ref):
            issues.append(f"Broken reference: {ref}")
    
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
        
        # Only validate write and edit operations on infrastructure files
        if tool_name not in ["write", "edit"]:
            print(json.dumps({"hookSpecificOutput": {"hookEventName": "PostToolUse"}}))
            sys.exit(0)
        
        file_path = tool_input.get("file_path", "")
        
        # Only check infrastructure files
        if not file_path or not any(prefix in file_path for prefix in ["Rules/", "Workflow/", "Agents/", "Scripts/", "Docs/"]):
            print(json.dumps({"hookSpecificOutput": {"hookEventName": "PostToolUse"}}))
            sys.exit(0)
        
        # For write operations, validate the content being written
        if tool_name == "write" and "content" in tool_input:
            content = tool_input["content"]
            is_valid, issues = validate_cross_references(content, file_path)
            
            if not is_valid:
                # Log validation failure but don't block (PostToolUse is non-blocking)
                warning_message = "Cross-reference integrity check failed: " + "; ".join(issues)
                print(f"WARNING: {warning_message}", file=sys.stderr)
                
                output = {
                    "hookSpecificOutput": {
                        "hookEventName": "PostToolUse",
                        "additionalContext": f"⚠️ Cross-reference check: {len(issues)} broken references - {warning_message}"
                    }
                }
                print(json.dumps(output))
                sys.exit(0)
        
        print(json.dumps({"hookSpecificOutput": {"hookEventName": "PostToolUse"}}))
        sys.exit(0)
        
    except Exception as e:
        print(f"Cross-reference integrity error: {e}", file=sys.stderr)
        print(json.dumps({"hookSpecificOutput": {"hookEventName": "PostToolUse"}}))
        sys.exit(1)


if __name__ == "__main__":
    main()