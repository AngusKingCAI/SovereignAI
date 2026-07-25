#!/usr/bin/env python3
"""
File naming convention validation hook for PreToolUse.
Validates file naming conventions before file operations.
"""

import sys
import json
import re
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))
from hook_utils import get_verbosity, should_print, show_hook_header, show_hook_result, show_hook_error, show_hook_error_details

def validate_file_naming(file_path):
    """Validate file naming conventions."""
    project_root = Path("C:/SovereignAI")
    
    # Define naming conventions
    naming_rules = {
        # AGENTS.md files
        r'AGENTS\.md$': 'Agent documentation files must be uppercase AGENTS.md',
        
        # Rule files: {Agent}_Rules.md
        r'.*_Rules\.md$': 'Rule files must follow {Agent}_Rules.md pattern',
        
        # Workflow files: {Agent}_{Workflow_Name}.md
        r'.*_.*\.md$': 'Workflow files should follow {Agent}_{Workflow_Name}.md pattern',
        
        # Log files: {component}-{YYYY-MM-DD}.jsonl
        r'.*\d{4}-\d{2}-\d{2}\.jsonl$': 'Log files should follow {component}-{YYYY-MM-DD}.jsonl pattern',
        
        # State files: phase-{N}-state.json
        r'phase-\d+-state\.json$': 'State files must follow phase-{N}-state.json pattern',
        
        # Directory naming: PascalCase
        r'^[A-Z][a-zA-Z0-9]*$': 'Directories should use PascalCase'
    }
    
    file_path = Path(file_path)
    file_name = file_path.name
    
    # Check specific naming patterns based on location
    relative_path = file_path.relative_to(project_root) if file_path.is_relative_to(project_root) else file_path
    
    # AGENTS.md validation
    if file_name != 'AGENTS.md' and file_path.parent.name in ['Architect', 'Executor', 'Planner', 'Researcher', 'Reviewer']:
        if file_name.endswith('.md'):
            return False, f"Agent documentation files must be named AGENTS.md, got {file_name}"
    
    # Rule files validation
    if file_path.parent.name == 'Rules' or 'Rules' in str(file_path.parent):
        if file_name.endswith('.md') and not file_name.endswith('_Rules.md'):
            return False, f"Rule files must follow {{Agent}}_Rules.md pattern, got {file_name}"
    
    # Workflow files validation
    if file_path.parent.name == 'Workflow' or 'Workflow' in str(file_path.parent):
        if file_name.endswith('.md') and not re.match(r'^[A-Z][a-z]*_[A-Z].*\.md$', file_name):
            return False, f"Workflow files should follow {{Agent}}_{{Workflow_Name}}.md pattern, got {file_name}"
    
    # State files validation
    if file_path.parent.name == 'Gates':
        if file_name.startswith('phase-') and not re.match(r'^phase-\d+-state\.json$', file_name):
            return False, f"State files must follow phase-{{N}}-state.json pattern, got {file_name}"
    
    # Directory naming validation (for directory creation)
    if file_path.is_dir():
        if not re.match(r'^[A-Z][a-zA-Z0-9]*$', file_name):
            return False, f"Directories should use PascalCase, got {file_name}"
    
    return True, "File naming validation passed"

def main():
    """Main file naming validation logic."""
    verbosity = get_verbosity()
    show_hook_header("File Naming Convention Validation", verbosity)
    
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
    
    # Validate file naming
    allowed, message = validate_file_naming(file_path)
    
    show_hook_result(f"Validation result: {message}", success=allowed, verbosity=verbosity)
    
    if not allowed:
        show_hook_error("File naming validation failed - operation blocked", verbosity)
        show_hook_error_details(f"File naming validation failed - operation blocked", verbosity)
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
    
    show_hook_result("File naming validation passed", success=True, verbosity=verbosity)
    return 0  # Allow the operation

if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except Exception as e:
        print(f"Error in file naming validation: {e}", file=sys.stderr)
        sys.exit(1)
