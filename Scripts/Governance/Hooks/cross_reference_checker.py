#!/usr/bin/env python3
"""
Cross-reference integrity checking hook for PostToolUse.
Validates cross-references using deterministic graph analysis instead of LLM analysis.
"""

import sys
import json
import re
from pathlib import Path
from collections import defaultdict

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))
from hook_utils import get_verbosity, should_print, show_hook_header, show_hook_result, show_hook_error, show_hook_error_details

def check_cross_references(file_path):
    """Check cross-references using deterministic graph analysis."""
    project_root = Path("C:/SovereignAI")
    
    # Build reference graph from project files
    reference_graph = defaultdict(set)
    
    # Scan AGENTS.md files for references
    agents_dir = project_root / "Agents"
    if agents_dir.exists():
        for agent_file in agents_dir.glob("*/AGENTS.md"):
            try:
                with open(agent_file) as f:
                    content = f.read()
                
                # Extract file references (simple pattern)
                file_refs = re.findall(r'[A-Z][a-z]*/[A-Z][a-z_]*\.md', content)
                for ref in file_refs:
                    if ref != agent_file.name:
                        reference_graph[agent_file.name].add(ref)
            except:
                pass
    
    # Scan workflow files for references
    workflow_dir = project_root / "Workflow"
    if workflow_dir.exists():
        for workflow_file in workflow_dir.glob("*/*.md"):
            try:
                with open(workflow_file) as f:
                    content = f.read()
                
                # Extract file references
                file_refs = re.findall(r'[A-Z][a-z]*/[A-Z][a-z_]*\.md', content)
                for ref in file_refs:
                    if ref != workflow_file.name:
                        reference_graph[workflow_file.name].add(ref)
            except:
                pass
    
    # Check for orphaned references
    orphaned_refs = []
    for source_file, refs in reference_graph.items():
        for ref in refs:
            # Check if referenced file exists
            ref_path = project_root / ref.replace('/', '\\')
            if not ref_path.exists():
                orphaned_refs.append(f"{source_file} -> {ref}")
    
    # Check naming consistency
    naming_inconsistencies = []
    agent_names = set()
    
    if agents_dir.exists():
        for agent_dir in agents_dir.iterdir():
            if agent_dir.is_dir():
                agent_names.add(agent_dir.name)
    
    # Check if AGENTS.md files use consistent agent naming
    for agent_name in agent_names:
        agents_md = agents_dir / agent_name / "AGENTS.md"
        if agents_md.exists():
            try:
                with open(agents_md) as f:
                    content = f.read()
                
                # Check if agent name in content matches directory name
                if agent_name.lower() not in content.lower():
                    naming_inconsistencies.append(f"AGENTS.md in {agent_name}/ may have inconsistent naming")
            except:
                pass
    
    # Compile results
    violations = []
    if orphaned_refs:
        violations.append(f"Orphaned references: {orphaned_refs}")
    if naming_inconsistencies:
        violations.append(f"Naming inconsistencies: {naming_inconsistencies}")
    
    if violations:
        return False, f"Cross-reference integrity violations: {', '.join(violations)}"
    
    return True, "Cross-reference integrity verified"

def main():
    """Main cross-reference checking logic."""
    verbosity = get_verbosity()
    show_hook_header("Cross-Reference Integrity Checking", verbosity)
    
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
        show_hook_result("No file path provided, skipping cross-reference check", success=True, verbosity=verbosity)
        return 0
    
    file_path = Path(file_path)
    
    # Only check AGENTS.md and workflow files for cross-references
    if file_path.name != 'AGENTS.md' and 'Workflow' not in str(file_path):
        show_hook_result(f"File {file_path.name} doesn't require cross-reference checking", success=True, verbosity=verbosity)
        return 0
    
    # Check cross-references
    allowed, message = check_cross_references(file_path)
    
    show_hook_result(f"Check result: {message}", success=allowed, verbosity=verbosity)
    
    if not allowed:
        show_hook_error("Cross-reference integrity check failed - violation logged", verbosity)
        show_hook_error_details(f"Cross-reference integrity check failed - violation logged", verbosity)
        # Log violation but don't block (PostToolUse)
        show_hook_result("Operation allowed but cross-references marked for remediation", success=True, verbosity=verbosity)
        return 0  # Don't block operation (it already completed)
    
    show_hook_result("Cross-reference integrity verified", success=True, verbosity=verbosity)
    return 0  # Don't block operation (it already completed)

if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except Exception as e:
        print(f"Error in cross-reference checking: {e}", file=sys.stderr)
        sys.exit(1)
