#!/usr/bin/env python3
"""
Template compliance checking hook for PostToolUse.
Validates template compliance using deterministic parsing instead of LLM analysis.
"""

import sys
import json
import re
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))
from hook_utils import get_verbosity, should_print, show_hook_header, show_hook_result, show_hook_error, show_hook_error_details

def check_agents_template_compliance(file_path):
    """Check AGENTS.md template compliance using deterministic parsing."""
    project_root = Path("C:/SovereignAI")
    template_path = project_root / "Agents" / "AGENTS_TEMPLATE.md"
    
    if not template_path.exists():
        return True, "AGENTS_TEMPLATE.md not found, skipping validation"
    
    # Read the template to extract required sections
    with open(template_path) as f:
        template_content = f.read()
    
    # Extract required sections from template
    required_sections = []
    section_pattern = r'## (\w+(?: \w+)*)'
    
    for match in re.finditer(section_pattern, template_content):
        required_sections.append(match.group(1))
    
    # Read the target file
    with open(file_path) as f:
        file_content = f.read()
    
    # Check for required sections
    missing_sections = []
    for section in required_sections:
        if f"## {section}" not in file_content:
            missing_sections.append(section)
    
    # Check for industry-standard sections
    industry_standard_sections = [
        "Purpose",
        "Setup Commands", 
        "Code Style",
        "Testing",
        "Boundaries",
        "Security Considerations",
        "Integration Points"
    ]
    
    missing_industry_sections = []
    for section in industry_standard_sections:
        if f"## {section}" not in file_content:
            missing_industry_sections.append(section)
    
    # Check for SovereignAI framework extensions
    framework_extensions = [
        "Constitutional Framework",
        "Scope Boundaries",
        "Git Operations Restrictions"
    ]
    
    missing_framework_sections = []
    for section in framework_extensions:
        if f"## {section}" not in file_content:
            missing_framework_sections.append(section)
    
    # Check for placeholders
    if "{placeholder}" in file_content.lower() or "{placeholder" in file_content:
        return False, "File contains placeholder text that must be replaced"
    
    # Check Boundaries section uses Always/Ask First/Never pattern
    if "## Boundaries" in file_content:
        boundaries_section = file_content.split("## Boundaries")[1].split("##")[0]
        if not all(pattern in boundaries_section for pattern in ["Always", "Ask First", "Never"]):
            return False, "Boundaries section must use Always/Ask First/Never pattern"
    
    # Compile results
    violations = []
    if missing_sections:
        violations.append(f"Missing template sections: {missing_sections}")
    if missing_industry_sections:
        violations.append(f"Missing industry-standard sections: {missing_industry_sections}")
    if missing_framework_sections:
        violations.append(f"Missing framework extensions: {missing_framework_sections}")
    
    if violations:
        return False, f"Template compliance violations: {', '.join(violations)}"
    
    return True, "AGENTS.md template compliance verified"

def check_workflow_template_compliance(file_path):
    """Check workflow template compliance using deterministic parsing."""
    project_root = Path("C:/SovereignAI")
    template_path = project_root / "Workflow" / "Workflow_Template.md"
    
    if not template_path.exists():
        return True, "Workflow_Template.md not found, skipping validation"
    
    # Read the template to extract required sections
    with open(template_path) as f:
        template_content = f.read()
    
    # Extract required sections from template
    required_sections = []
    section_pattern = r'## (\w+(?: \w+)*)'
    
    for match in re.finditer(section_pattern, template_content):
        required_sections.append(match.group(1))
    
    # Read the target file
    with open(file_path) as f:
        file_content = f.read()
    
    # Check for required sections
    missing_sections = []
    for section in required_sections:
        if f"## {section}" not in file_content:
            missing_sections.append(section)
    
    # Check for critical workflow sections
    critical_sections = [
        "Purpose",
        "Scope",
        "Gate Enforcement",
        "Workflow Steps",
        "Quality Metrics"
    ]
    
    missing_critical_sections = []
    for section in critical_sections:
        if f"## {section}" not in file_content:
            missing_critical_sections.append(section)
    
    # Check header metadata
    header_required = ["Workflow Name", "Description", "Status", "Template Compliance"]
    missing_header_fields = []
    for field in header_required:
        if f"**{field}**:" not in file_content:
            missing_header_fields.append(field)
    
    # Check Gate Enforcement is before Workflow Steps
    if "## Gate Enforcement" in file_content and "## Workflow Steps" in file_content:
        gate_enforcement_pos = file_content.index("## Gate Enforcement")
        workflow_steps_pos = file_content.index("## Workflow Steps")
        if gate_enforcement_pos > workflow_steps_pos:
            return False, "Gate Enforcement section must be positioned before Workflow Steps"
    
    # Compile results
    violations = []
    if missing_sections:
        violations.append(f"Missing template sections: {missing_sections}")
    if missing_critical_sections:
        violations.append(f"Missing critical sections: {missing_critical_sections}")
    if missing_header_fields:
        violations.append(f"Missing header fields: {missing_header_fields}")
    
    if violations:
        return False, f"Workflow template compliance violations: {', '.join(violations)}"
    
    return True, "Workflow template compliance verified"

def main():
    """Main template compliance checking logic."""
    verbosity = get_verbosity()
    show_hook_header("Template Compliance Checking", verbosity)
    
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
        show_hook_result("No file path provided, skipping validation", success=True, verbosity=verbosity)
        return 0
    
    file_path = Path(file_path)
    
    # Determine which template to check based on file location
    if file_path.name == 'AGENTS.md' or file_path.parent.name in ['Architect', 'Executor', 'Planner', 'Researcher', 'Reviewer']:
        allowed, message = check_agents_template_compliance(file_path)
    elif file_path.parent.name == 'Workflow' or 'Workflow' in str(file_path.parent):
        allowed, message = check_workflow_template_compliance(file_path)
    else:
        show_hook_result(f"File {file_path.name} doesn't require template validation", success=True, verbosity=verbosity)
        return 0
    
    show_hook_result(f"Validation result: {message}", success=allowed, verbosity=verbosity)
    
    if not allowed:
        show_hook_error("Template compliance check failed - violation logged", verbosity)
        show_hook_error_details(f"Template compliance check failed - violation logged", verbosity)
        # Log violation but don't block (PostToolUse)
        show_hook_result("Operation allowed but marked for remediation", success=True, verbosity=verbosity)
        return 0  # Don't block operation (it already completed)
    
    show_hook_result("Template compliance verified", success=True, verbosity=verbosity)
    return 0  # Don't block operation (it already completed)

if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except Exception as e:
        print(f"Error in template compliance checking: {e}", file=sys.stderr)
        sys.exit(1)
