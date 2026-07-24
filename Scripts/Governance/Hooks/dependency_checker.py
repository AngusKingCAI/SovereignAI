#!/usr/bin/env python3
"""
Dependency Checking Hook - PreToolUse
Validates that dependencies are properly declared and available
"""

import json
import sys
import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple

# Project root
PROJECT_ROOT = Path("C:/SovereignAI")

# Common dependency patterns
PYTHON_DEPENDENCY_PATTERNS = [
    r"import\s+([a-zA-Z_][a-zA-Z0-9_]*)",
    r"from\s+([a-zA-Z_][a-zA-Z0-9_]*)"
]

JAVASCRIPT_DEPENDENCY_PATTERNS = [
    r"require\(['\"]([^'\"]+)['\"]\)",
    r"import\s+.*from\s+['\"]([^'\"]+)['\"]"
]


def extract_dependencies(content: str, file_type: str) -> List[str]:
    """Extract dependencies from content based on file type."""
    dependencies = []
    
    if file_type == "python":
        for pattern in PYTHON_DEPENDENCY_PATTERNS:
            matches = re.findall(pattern, content)
            dependencies.extend(matches)
    elif file_type == "javascript":
        for pattern in JAVASCRIPT_DEPENDENCY_PATTERNS:
            matches = re.findall(pattern, content)
            dependencies.extend(matches)
    
    # Filter out standard library imports
    standard_libs = {"os", "sys", "json", "re", "path", "datetime", "uuid", "typing"}
    dependencies = [dep for dep in dependencies if dep not in standard_libs]
    
    return list(set(dependencies))  # Remove duplicates


def check_dependency_declaration(dependencies: List[str], file_path: str) -> Tuple[bool, List[str]]:
    """Check if dependencies are properly declared."""
    issues = []
    
    # Check for requirements.txt or package.json
    project_root = PROJECT_ROOT
    requirements_file = project_root / "requirements.txt"
    package_json = project_root / "package.json"
    
    # This is a simplified check - actual implementation would be more sophisticated
    if requirements_file.exists():
        try:
            with open(requirements_file, 'r', encoding='utf-8') as f:
                declared_deps = f.read()
            
            for dep in dependencies:
                if dep.lower() not in declared_deps.lower():
                    issues.append(f"Dependency '{dep}' not found in requirements.txt")
        except Exception:
            pass
    
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
        
        # Only validate write operations on dependency-related files
        if tool_name != "write":
            print(json.dumps({"hookSpecificOutput": {"hookEventName": "PreToolUse"}}))
            sys.exit(0)
        
        file_path = tool_input.get("file_path", "")
        
        if not file_path:
            print(json.dumps({"hookSpecificOutput": {"hookEventName": "PreToolUse"}}))
            sys.exit(0)
        
        # Determine file type
        file_type = "python" if file_path.endswith(".py") else "javascript" if file_path.endswith(".js") else None
        
        if not file_type:
            print(json.dumps({"hookSpecificOutput": {"hookEventName": "PreToolUse"}}))
            sys.exit(0)
        
        # For write operations, validate dependencies
        if "content" in tool_input:
            content = tool_input["content"]
            dependencies = extract_dependencies(content, file_type)
            
            if dependencies:
                is_valid, issues = check_dependency_declaration(dependencies, file_path)
                
                if not is_valid:
                    # Log warning but don't block (PostToolUse is non-blocking)
                    warning_message = "Dependency check failed: " + "; ".join(issues)
                    print(f"WARNING: {warning_message}", file=sys.stderr)
                    
                    output = {
                        "hookSpecificOutput": {
                            "hookEventName": "PreToolUse",
                            "additionalContext": f"⚠️ Dependency check: {len(issues)} undeclared dependencies - {warning_message}"
                        }
                    }
                    print(json.dumps(output))
                    sys.exit(0)
        
        print(json.dumps({"hookSpecificOutput": {"hookEventName": "PreToolUse"}}))
        sys.exit(0)
        
    except Exception as e:
        print(f"Dependency checking error: {e}", file=sys.stderr)
        print(json.dumps({"hookSpecificOutput": {"hookEventName": "PreToolUse"}}))
        sys.exit(1)


if __name__ == "__main__":
    main()