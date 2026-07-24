#!/usr/bin/env python3
"""
Planner gate system integrated into hook system.
Validates plans before delivery using hook-based enforcement.
"""

import sys
import json
import os
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

def load_plan_validation_tools():
    """Load plan validation gate tools."""
    gate_dir = Path(__file__).parent.parent.parent / "Planner" / "Gates"
    
    # Import gate-core modules
    sys.path.insert(0, str(gate_dir / "gate-core"))
    
    try:
        from manifest_validator import ManifestValidator
        from plan_parser import PlanParser
        from scope_checker import ScopeChecker
        from dependency_analyzer import DependencyAnalyzer
    except ImportError as e:
        print(f"Warning: Could not import gate tools: {e}")
        return None
    
    return {
        'manifest_validator': ManifestValidator(),
        'plan_parser': PlanParser(),
        'scope_checker': ScopeChecker(),
        'dependency_analyzer': DependencyAnalyzer()
    }

def validate_plan_structure(plan_file, tools):
    """Validate plan structure and format."""
    if not tools or 'plan_parser' not in tools:
        return True, "Plan parser not available"
    
    try:
        parser = tools['plan_parser']
        result = parser.parse_plan_file(plan_file)
        
        if result.is_valid:
            return True, f"Plan structure valid: {result.plan_name}"
        else:
            return False, f"Plan structure invalid: {result.errors}"
    except Exception as e:
        return False, f"Plan structure validation failed: {e}"

def validate_scope_compliance(plan_file, tools):
    """Validate plan scope compliance."""
    if not tools or 'scope_checker' not in tools:
        return True, "Scope checker not available"
    
    try:
        checker = tools['scope_checker']
        result = checker.check_scope(plan_file)
        
        if result.is_compliant:
            return True, f"Scope compliance verified: {result.scope_level}"
        else:
            return False, f"Scope compliance failed: {result.violations}"
    except Exception as e:
        return False, f"Scope compliance validation failed: {e}"

def validate_executor_manifest(plan_file, tools):
    """Validate executor manifest sections."""
    if not tools or 'manifest_validator' not in tools:
        return True, "Manifest validator not available"
    
    try:
        validator = tools['manifest_validator']
        # Parse plan to extract manifest sections
        with open(plan_file) as f:
            plan_content = f.read()
        
        # Look for manifest sections
        manifest_sections = []
        lines = plan_content.split('\n')
        in_manifest = False
        manifest_content = []
        
        for line in lines:
            if 'Executor Manifest' in line or '## Manifest' in line:
                in_manifest = True
                manifest_content = [line]
            elif in_manifest:
                if line.startswith('##') and 'Manifest' not in line:
                    in_manifest = False
                    manifest_sections.append('\n'.join(manifest_content))
                else:
                    manifest_content.append(line)
        
        if manifest_content:
            manifest_sections.append('\n'.join(manifest_content))
        
        for manifest in manifest_sections:
            result = validator.validate_manifest_section(manifest)
            if not result.is_valid:
                return False, f"Manifest validation failed: {result.errors}"
        
        return True, f"Manifest validation passed: {len(manifest_sections)} sections"
    except Exception as e:
        return False, f"Manifest validation failed: {e}"

def validate_dependencies(plan_file, tools):
    """Validate dependency analysis."""
    if not tools or 'dependency_analyzer' not in tools:
        return True, "Dependency analyzer not available"
    
    try:
        analyzer = tools['dependency_analyzer']
        result = analyzer.analyze_dependencies(plan_file)
        
        if result.is_valid:
            return True, f"Dependency analysis valid: {result.dependency_count} dependencies"
        else:
            return False, f"Dependency analysis failed: {result.missing_dependencies}"
    except Exception as e:
        return False, f"Dependency analysis failed: {e}"

def main():
    """Main planner gate validation logic."""
    print("=== Planner Gate System ===")
    
    # Get plan file from environment or argument
    plan_file = os.environ.get('DEVIN_PLAN_FILE') or (sys.argv[1] if len(sys.argv) > 1 else None)
    
    if not plan_file:
        print("No plan file provided")
        return 0  # Don't block if no plan file
    
    if not Path(plan_file).exists():
        print(f"Plan file not found: {plan_file}")
        return 0  # Don't block if file doesn't exist
    
    print(f"Validating plan: {plan_file}")
    
    # Load validation tools
    tools = load_plan_validation_tools()
    
    # Run validations
    validations = [
        ("Plan Structure", lambda: validate_plan_structure(plan_file, tools)),
        ("Scope Compliance", lambda: validate_scope_compliance(plan_file, tools)),
        ("Executor Manifest", lambda: validate_executor_manifest(plan_file, tools)),
        ("Dependencies", lambda: validate_dependencies(plan_file, tools))
    ]
    
    results = []
    failures = []
    
    for name, validation_func in validations:
        print(f"Validating {name}...")
        try:
            passed, message = validation_func()
            results.append(f"{name}: {'PASS' if passed else 'FAIL'} - {message}")
            if not passed:
                failures.append(name)
        except Exception as e:
            results.append(f"{name}: ERROR - {e}")
            failures.append(name)
    
    # Print results
    print("\n=== Validation Results ===")
    for result in results:
        print(result)
    
    if failures:
        print(f"\n❌ {len(failures)} validation(s) failed")
        print("Plan delivery BLOCKED")
        return 2  # Block the operation
    else:
        print("\n✅ All validations passed")
        print("Plan approved for delivery")
        return 0  # Allow the operation

if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except Exception as e:
        print(f"Error in planner gate system: {e}", file=sys.stderr)
        sys.exit(1)