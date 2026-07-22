#!/usr/bin/env python3
"""Tool Description Standardization Script

Updates all hard gate scripts with standardized tool descriptions
per Anthropic best practices for agent tool design.
"""

import os
import re
from pathlib import Path

# Standardized tool descriptions for each hard gate
TOOL_DESCRIPTIONS = {
    "hg1_requirements_complete.py": """#!/usr/bin/env python3
"""
Tool: HG-1 Requirements Complete Validation

WHEN TO USE: Phase 1, after requirements are assessed, before plan drafting

WHAT IT CHECKS: Latest plan file has dependencies, vision principles, context section, 
no vague terms (TBD/TBA/TODO), specific step sections (S1, S2...), and compliance indicators.

INPUTS: None (auto-discovers latest plan in plans/ directory)

OUTPUTS:
- Exit 0: Gate HG-1 PASS: {plan_name} requirements complete
- Exit 1: Gate HG-1 FAIL: {list of specific issues}

FAILURE RECOVERY: Fix listed issues in plan file, re-run this script.
Do NOT proceed to Phase 2 until exit 0.

DEPENDENCIES: plans/ directory must exist with at least one plan-*.md file
""",
    
    "hg2_scope_defined.py": """#!/usr/bin/env python3
"""
Tool: HG-2 Scope Defined Validation

WHEN TO USE: Phase 1, after requirements assessment, before plan drafting

WHAT IT CHECKS: Plan has clear scope boundaries (in-scope paths, out-of-scope items, 
forbidden actions), no scope creep, and explicit scope limitations.

INPUTS: None (auto-discovers latest plan in plans/ directory)

OUTPUTS:
- Exit 0: Gate HG-2 PASS: Plan scope clearly defined
- Exit 1: Gate HG-2 FAIL: {list of scope issues}

FAILURE RECOVERY: Add scope section with clear boundaries, re-run this script.
Do NOT proceed to Phase 2 until exit 0.

DEPENDENCIES: plans/ directory must exist with at least one plan-*.md file
""",
    
    "hg3_dependencies_feasible.py": """#!/usr/bin/env python3
"""
Tool: HG-3 Dependencies Feasible Validation

WHEN TO USE: Phase 1, after requirements assessment, before plan drafting

WHAT IT CHECKS: Plan dependencies are feasible, no circular dependencies, no impossible 
requirements, and dependencies can be satisfied with available resources.

INPUTS: None (auto-discovers latest plan in plans/ directory)

OUTPUTS:
- Exit 0: Gate HG-3 PASS: Dependencies are feasible
- Exit 1: Gate HG-3 FAIL: {list of dependency issues}

FAILURE RECOVERY: Fix dependency issues, remove circular dependencies, re-run this script.
Do NOT proceed to Phase 2 until exit 0.

DEPENDENCIES: plans/ directory must exist with at least one plan-*.md file
""",
    
    "hg4_sections_complete.py": """#!/usr/bin/env python3
"""
Tool: HG-4 Sections Complete Validation

WHEN TO USE: Phase 4, after plan drafting, before quality gates

WHAT IT CHECKS: Plan has all required sections (Context, Architecture, Dependencies, 
Implementation, Testing, Deployment, Rollback, Maintenance) with sufficient content.

INPUTS: None (auto-discovers latest plan in plans/ directory)

OUTPUTS:
- Exit 0: Gate HG-4 PASS: All required sections present and complete
- Exit 1: Gate HG-4 FAIL: {list of missing or incomplete sections}

FAILURE RECOVERY: Add missing sections or expand incomplete sections, re-run this script.
Do NOT proceed to Phase 5 until exit 0.

DEPENDENCIES: plans/ directory must exist with at least one plan-*.md file
""",
    
    "hg5_language_clear.py": """#!/usr/bin/env python3
"""
Tool: HG-5 Language Clear Validation

WHEN TO USE: Phase 4, after plan drafting, before quality gates

WHAT IT CHECKS: Plan uses clear, unambiguous language per technical writing best practices.
No vague terms, weak verbs, or ambiguous phrasing that could lead to misinterpretation.

INPUTS: None (auto-discovers latest plan in plans/ directory)

OUTPUTS:
- Exit 0: Gate HG-5 PASS: Plan language is clear and unambiguous
- Exit 1: Gate HG-5 FAIL: {list of language clarity issues}

FAILURE RECOVERY: Improve language clarity, remove vague terms, re-run this script.
Do NOT proceed to Phase 5 until exit 0.

DEPENDENCIES: plans/ directory must exist with at least one plan-*.md file
""",
    
    "hg6_landmines_screened.py": """#!/usr/bin/env python3
"""
Tool: HG-6 Landmines Screened Validation

WHEN TO USE: Phase 4, after plan drafting, before quality gates

WHAT IT CHECKS: Plan is screened against governance landmines (security, architecture, 
process, compliance) from PATTERN_LIBRARY.md. No blocking landmines present.

INPUTS: None (auto-discovers latest plan in plans/ directory)

OUTPUTS:
- Exit 0: Gate HG-6 PASS: No blocking landmines present
- Exit 1: Gate HG-6 FAIL: {list of blocking landmines detected}

FAILURE RECOVERY: Address blocking landmines, add mitigation strategies, re-run this script.
Do NOT proceed to Phase 5 until exit 0.

DEPENDENCIES: plans/ directory must exist with at least one plan-*.md file, PATTERN_LIBRARY.md
""",
    
    "hg7_compliance_lines_present.py": """#!/usr/bin/env python3
"""
Tool: HG-7 Compliance Lines Present Validation

WHEN TO USE: Phase 5, after plan finalization, before Round Table

WHAT IT CHECKS: Plan has compliance indicators for all major sections and phases.
Each phase and deliverable has corresponding compliance line.

INPUTS: None (auto-discovers latest plan in plans/ directory)

OUTPUTS:
- Exit 0: Gate HG-7 PASS: All compliance lines present
- Exit 1: Gate HG-7 FAIL: {list of missing compliance lines}

FAILURE RECOVERY: Add missing compliance lines to plan sections, re-run this script.
Do NOT proceed to Phase 6 until exit 0.

DEPENDENCIES: plans/ directory must exist with at least one plan-*.md file
""",
    
    "hg8_paths_valid.py": """#!/usr/bin/env python3
"""
Tool: HG-8 Paths Valid Validation

WHEN TO USE: Phase 5, after plan finalization, before Round Table

WHAT IT CHECKS: All paths are repo-relative (per PR2), no absolute paths, no invalid 
path references, and path separators are consistent (forward slashes).

INPUTS: None (auto-discovers latest plan in plans/ directory)

OUTPUTS:
- Exit 0: Gate HG-8 PASS: All paths are repo-relative and valid
- Exit 1: Gate HG-8 FAIL: {list of path validation issues}

FAILURE RECOVERY: Fix path references to be repo-relative, re-run this script.
Do NOT proceed to Phase 6 until exit 0.

DEPENDENCIES: plans/ directory must exist with at least one plan-*.md file
""",
    
    "hg9_manifest_complete.py": """#!/usr/bin/env python3
"""
Tool: HG-9 Manifest Complete Validation

WHEN TO USE: Phase 5, after plan finalization, before Round Table

WHAT IT CHECKS: Executor Manifest is complete with all required components (Success Criteria, 
Exit Conditions, Phase definitions, Deliverable definitions, Gate definitions).

INPUTS: None (auto-discovers latest plan in plans/ directory)

OUTPUTS:
- Exit 0: Gate HG-9 PASS: Executor Manifest is complete
- Exit 1: Gate HG-9 FAIL: {list of missing manifest components}

FAILURE RECOVERY: Complete missing manifest components, re-run this script.
Do NOT proceed to Phase 6 until exit 0.

DEPENDENCIES: plans/ directory must exist with at least one plan-*.md file
""",
    
    "hg10_critical_findings_addressed.py": """#!/usr/bin/env python3
"""
Tool: HG-10 Critical Findings Addressed Validation

WHEN TO USE: Phase 6, after Round Table review, before plan delivery

WHAT IT CHECKS: All CRITICAL severity findings from Round Table database are addressed.
No unaddressed CRITICAL findings exist in the database.

INPUTS: None (queries Round Table database for unaddressed CRITICAL findings)

OUTPUTS:
- Exit 0: Gate HG-10 PASS: All CRITICAL findings are addressed
- Exit 1: Gate HG-10 FAIL: {list of unaddressed CRITICAL findings}

FAILURE RECOVERY: Address CRITICAL findings in plan, update database status, re-run this script.
Do NOT deliver plan until exit 0.

DEPENDENCIES: Round Table database with findings data, database_manager.py
""",
    
    "hg11_high_findings_addressed.py": """#!/usr/bin/env python3
"""
Tool: HG-11 High Findings Addressed Validation

WHEN TO USE: Phase 6, after Round Table review, before plan delivery

WHAT IT CHECKS: All HIGH severity findings from Round Table database are addressed.
No unaddressed HIGH findings exist in the database.

INPUTS: None (queries Round Table database for unaddressed HIGH findings)

OUTPUTS:
- Exit 0: Gate HG-11 PASS: All HIGH findings are addressed
- Exit 1: Gate HG-11 FAIL: {list of unaddressed HIGH findings}

FAILURE RECOVERY: Address HIGH findings in plan, update database status, re-run this script.
Do NOT deliver plan until exit 0.

DEPENDENCIES: Round Table database with findings data, database_manager.py
""",
    
    "hg12_no_blocking_landmines.py": """#!/usr/bin/env python3
"""
Tool: HG-12 No Blocking Landmines Validation

WHEN TO USE: Phase 6, after Round Table review, before plan delivery

WHAT IT CHECKS: No blocking landmine findings from Round Table database exist.
Blocking landmines would prevent plan execution.

INPUTS: None (queries Round Table database for blocking landmine findings)

OUTPUTS:
- Exit 0: Gate HG-12 PASS: No blocking landmines present
- Exit 1: Gate HG-12 FAIL: {list of blocking landmines detected}

FAILURE RECOVERY: Address blocking landmines, add mitigation strategies, re-run this script.
Do NOT deliver plan until exit 0.

DEPENDENCIES: Round Table database with findings data, database_manager.py
""",
    
    "hg13_manifest_present.py": """#!/usr/bin/env python3
"""
Tool: HG-13 Manifest Present Validation

WHEN TO USE: Phase 6, after Round Table review, before plan delivery

WHAT IT CHECKS: Executor Manifest section exists in plan and is present.
This is different from HG-9 which checks completeness - this checks existence.

INPUTS: None (auto-discovers latest plan in plans/ directory)

OUTPUTS:
- Exit 0: Gate HG-13 PASS: Executor Manifest is present
- Exit 1: Gate HG-13 FAIL: Executor Manifest is missing

FAILURE RECOVERY: Add Executor Manifest section to plan, re-run this script.
Do NOT deliver plan until exit 0.

DEPENDENCIES: plans/ directory must exist with at least one plan-*.md file
""",
    
    "hg14_plan_structure_pr6.py": """#!/usr/bin/env python3
"""
Tool: HG-14 Plan Structure PR6 Validation

WHEN TO USE: Phase 2, after plan structure design, before plan drafting

WHAT IT CHECKS: Plan structure follows PR6 requirements (header, manifest, phases, 
deliverables, proper section ordering, PR rule references, compliance indicators).

INPUTS: None (auto-discovers latest plan in plans/ directory)

OUTPUTS:
- Exit 0: Gate HG-14 PASS: Plan structure follows PR6 requirements
- Exit 1: Gate HG-14 FAIL: {list of structure validation issues}

FAILURE RECOVERY: Fix plan structure issues, re-run this script.
Do NOT proceed to Phase 3 until exit 0.

DEPENDENCIES: plans/ directory must exist with at least one plan-*.md file
""",
    
    "hg15_path_verification_pr2.py": """#!/usr/bin/env python3
"""
Tool: HG-15 Path Verification PR2 Validation

WHEN TO USE: Phase 3, after plan drafting, before plan finalization

WHAT IT CHECKS: All paths are repo-relative per PR2 requirements. No absolute paths, 
no invalid path references, consistent path separators.

INPUTS: None (auto-discovers latest plan in plans/ directory)

OUTPUTS:
- Exit 0: Gate HG-15 PASS: All paths are repo-relative per PR2
- Exit 1: Gate HG-15 FAIL: {list of path verification issues}

FAILURE RECOVERY: Fix path references to be repo-relative, re-run this script.
Do NOT proceed to Phase 4 until exit 0.

DEPENDENCIES: plans/ directory must exist with at least one plan-*.md file
"""
}

def update_tool_description(file_path, new_description):
    """Update the docstring in a Python file with standardized tool description."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Find and replace the docstring
        # Match from #!/usr/bin/env python3 to the end of the docstring
        pattern = r'#!/usr/bin/env python3\n""".*?"""'
        if re.search(pattern, content, re.DOTALL):
            content = re.sub(pattern, new_description.strip(), content, count=1, flags=re.DOTALL)
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            return True, f"Updated {file_path.name}"
        else:
            return False, f"No docstring pattern found in {file_path.name}"
            
    except Exception as e:
        return False, f"Error updating {file_path.name}: {e}"

def main():
    """Update all hard gate scripts with standardized tool descriptions."""
    hard_gates_dir = Path(".Planner/scripts/hard_gates")
    
    if not hard_gates_dir.exists():
        print(f"Hard gates directory not found: {hard_gates_dir}")
        return 1
    
    updated_count = 0
    failed_count = 0
    
    for script_file in hard_gates_dir.glob("hg*.py"):
        if script_file.name in TOOL_DESCRIPTIONS:
            success, message = update_tool_description(script_file, TOOL_DESCRIPTIONS[script_file.name])
            if success:
                print(f"OK: {message}")
                updated_count += 1
            else:
                print(f"FAIL: {message}")
                failed_count += 1
        else:
            print(f"WARN: No tool description defined for {script_file.name}")
    
    print(f"\nUpdated {updated_count} scripts, {failed_count} failed")
    return 0 if failed_count == 0 else 1

if __name__ == "__main__":
    import sys
    sys.exit(main())