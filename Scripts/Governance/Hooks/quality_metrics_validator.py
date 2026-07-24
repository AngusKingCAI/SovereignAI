#!/usr/bin/env python3
"""
Quality metrics validation hook for PostToolUse.
Validates quality metrics using deterministic measurements instead of LLM analysis.
"""

import sys
import json
import re
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))
from hook_utils import get_verbosity, should_print, show_hook_header, show_hook_result, show_hook_error, show_hook_error_details

def validate_quality_metrics(file_path):
    """Validate quality metrics using deterministic measurements."""
    try:
        with open(file_path) as f:
            content = f.read()
    except Exception as e:
        return False, f"Could not read file: {e}"
    
    # Check for Quality Metrics section
    if "## Quality Metrics" not in content:
        return True, "No Quality Metrics section found - validation not required"
    
    # Extract Quality Metrics section
    quality_section = content.split("## Quality Metrics")[1].split("##")[0] if "##" in content.split("## Quality Metrics")[1] else content.split("## Quality Metrics")[1]
    
    # Check for required metric categories
    required_categories = [
        "Quality",
        "Token Cost", 
        "Efficiency"
    ]
    
    missing_categories = []
    for category in required_categories:
        if f"## {category}" not in quality_section:
            missing_categories.append(category)
    
    if missing_categories:
        return False, f"Quality Metrics missing required categories: {missing_categories}"
    
    # Check Quality subsections
    if "## Quality" in quality_section:
        quality_subsection = quality_section.split("## Quality")[1].split("##")[0] if "##" in quality_section.split("## Quality")[1] else quality_section.split("## Quality")[1]
        
        required_quality_subsections = [
            "Determinism",
            "Observability",
            "Testability",
            "Architectural Soundness"
        ]
        
        missing_quality_subsections = []
        for subsection in required_quality_subsections:
            if f"### {subsection}" not in quality_subsection:
                missing_quality_subsections.append(subsection)
        
        if missing_quality_subsections:
            return False, f"Quality section missing subsections: {missing_quality_subsections}"
    
    # Check Token Cost subsections
    if "## Token Cost" in quality_section:
        token_subsection = quality_section.split("## Token Cost")[1].split("##")[0] if "##" in quality_section.split("## Token Cost")[1] else quality_section.split("## Token Cost")[1]
        
        required_token_subsections = [
            "Context Efficiency",
            "Model Selection",
            "Caching Strategy",
            "Reasoning Overhead"
        ]
        
        missing_token_subsections = []
        for subsection in required_token_subsections:
            if f"### {subsection}" not in token_subsection:
                missing_token_subsections.append(subsection)
        
        if missing_token_subsections:
            return False, f"Token Cost section missing subsections: {missing_token_subsections}"
    
    # Check Efficiency subsections
    if "## Efficiency" in quality_section:
        efficiency_subsection = quality_section.split("## Efficiency")[1] if "##" in quality_section.split("## Efficiency")[1] else quality_section.split("## Efficiency")[1]
        
        required_efficiency_subsections = [
            "Parallelization",
            "Latency Optimization",
            "Resource Utilization"
        ]
        
        missing_efficiency_subsections = []
        for subsection in required_efficiency_subsections:
            if f"### {subsection}" not in efficiency_subsection:
                missing_efficiency_subsections.append(subsection)
        
        if missing_efficiency_subsections:
            return False, f"Efficiency section missing subsections: {missing_efficiency_subsections}"
    
    # Check for validation criteria in each subsection
    validation_pattern = r'\*Validation:\*'
    if not re.search(validation_pattern, quality_section):
        return False, "Quality Metrics missing validation criteria"
    
    # Check for point values (indicating scoring)
    point_pattern = r'\(\d+\s+points\)'
    if not re.search(point_pattern, quality_section):
        return False, "Quality Metrics missing point values"
    
    return True, "Quality metrics validation passed"

def main():
    """Main quality metrics validation logic."""
    verbosity = get_verbosity()
    show_hook_header("Quality Metrics Validation", verbosity)
    
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
        show_hook_result("No file path provided, skipping quality metrics validation", success=True, verbosity=verbosity)
        return 0
    
    file_path = Path(file_path)
    
    # Check if this is a workflow file (quality metrics are typically in workflows)
    if 'Workflow' not in str(file_path) and 'workflow' not in str(file_path).lower():
        show_hook_result(f"File {file_path.name} is not a workflow file, skipping quality metrics validation", success=True, verbosity=verbosity)
        return 0
    
    # Validate quality metrics
    allowed, message = validate_quality_metrics(file_path)
    
    show_hook_result(f"Validation result: {message}", success=allowed, verbosity=verbosity)
    
    if not allowed:
        show_hook_error("Quality metrics validation failed - violation logged", verbosity)
        show_hook_error_details(f"Quality metrics validation failed - violation logged", verbosity)
        # Log violation but don't block (PostToolUse)
        show_hook_result("Operation allowed but quality metrics marked for remediation", success=True, verbosity=verbosity)
        return 0  # Don't block operation (it already completed)
    
    show_hook_result("Quality metrics validation passed", success=True, verbosity=verbosity)
    return 0  # Don't block operation (it already completed)

if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except Exception as e:
        print(f"Error in quality metrics validation: {e}", file=sys.stderr)
        sys.exit(1)
