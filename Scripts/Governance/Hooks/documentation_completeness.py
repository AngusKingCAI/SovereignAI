#!/usr/bin/env python3
"""
Documentation completeness verification hook for PostToolUse.
Verifies documentation completeness using file system checks instead of LLM analysis.
"""

import sys
import json
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))
from hook_utils import get_verbosity, should_print, show_hook_header, show_hook_result, show_hook_error, show_hook_error_details

def verify_documentation_completeness(file_path):
    """Verify documentation completeness using file system checks."""
    project_root = Path("C:/SovereignAI")
    
    # Define required documentation structure
    required_structure = {
        "Agents": {
            "must_have_agents_md": True,
            "check_subdirectories": True
        },
        "Rules": {
            "must_have_rules": True,
            "check_subdirectories": True
        },
        "Workflow": {
            "must_have_workflows": True,
            "check_subdirectories": True
        }
    }
    
    file_path = Path(file_path)
    
    # If this is an AGENTS.md file, check agent documentation completeness
    if file_path.name == 'AGENTS.md':
        agent_dir = file_path.parent
        
        # Check for corresponding rules and workflows
        agent_name = agent_dir.name
        rules_dir = project_root / "Rules" / agent_name
        workflow_dir = project_root / "Workflow" / agent_name
        
        violations = []
        
        if not rules_dir.exists():
            violations.append(f"Missing Rules directory for {agent_name}")
        
        if not workflow_dir.exists():
            violations.append(f"Missing Workflow directory for {agent_name}")
        
        # Check for at least one rule file
        if rules_dir.exists():
            rule_files = list(rules_dir.glob("*.md"))
            if not rule_files:
                violations.append(f"No rule files found in {agent_name}/Rules/")
        
        # Check for at least one workflow file
        if workflow_dir.exists():
            workflow_files = list(workflow_dir.glob("*.md"))
            if not workflow_files:
                violations.append(f"No workflow files found in {agent_name}/Workflow/")
        
        if violations:
            return False, f"Documentation incomplete for {agent_name}: {', '.join(violations)}"
        
        return True, f"Documentation completeness verified for {agent_name}"
    
    # If this is a rule file, check corresponding AGENTS.md and workflow
    if file_path.name.endswith('_Rules.md'):
        agent_name = file_path.stem.replace('_Rules', '')
        
        agents_md = project_root / "Agents" / agent_name / "AGENTS.md"
        workflow_dir = project_root / "Workflow" / agent_name
        
        violations = []
        
        if not agents_md.exists():
            violations.append(f"Missing AGENTS.md for {agent_name}")
        
        if not workflow_dir.exists():
            violations.append(f"Missing Workflow directory for {agent_name}")
        
        if violations:
            return False, f"Documentation incomplete for {agent_name}: {', '.join(violations)}"
        
        return True, f"Documentation completeness verified for {agent_name}"
    
    # If this is a workflow file, check corresponding AGENTS.md and rules
    if file_path.parent.name == 'Workflow':
        agent_name = file_path.parent.name
        
        agents_md = project_root / "Agents" / agent_name / "AGENTS.md"
        rules_dir = project_root / "Rules" / agent_name
        
        violations = []
        
        if not agents_md.exists():
            violations.append(f"Missing AGENTS.md for {agent_name}")
        
        if not rules_dir.exists():
            violations.append(f"Missing Rules directory for {agent_name}")
        
        if violations:
            return False, f"Documentation incomplete for {agent_name}: {', '.join(violations)}"
        
        return True, f"Documentation completeness verified for {agent_name}"
    
    # If not a documentation file, skip
    return True, "File does not require documentation completeness check"

def main():
    """Main documentation completeness verification logic."""
    verbosity = get_verbosity()
    show_hook_header("Documentation Completeness Verification", verbosity)
    
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
        show_hook_result("No file path provided, skipping documentation completeness check", success=True, verbosity=verbosity)
        return 0
    
    # Verify documentation completeness
    allowed, message = verify_documentation_completeness(file_path)
    
    show_hook_result(f"Verification result: {message}", success=allowed, verbosity=verbosity)
    
    if not allowed:
        show_hook_error("Documentation completeness check failed - violation logged", verbosity)
        show_hook_error_details(f"Documentation completeness check failed - violation logged", verbosity)
        # Log violation but don't block (PostToolUse)
        show_hook_result("Operation allowed but documentation marked for remediation", success=True, verbosity=verbosity)
        return 0  # Don't block operation (it already completed)
    
    show_hook_result("Documentation completeness verified", success=True, verbosity=verbosity)
    return 0  # Don't block operation (it already completed)

if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except Exception as e:
        print(f"Error in documentation completeness verification: {e}", file=sys.stderr)
        sys.exit(1)
