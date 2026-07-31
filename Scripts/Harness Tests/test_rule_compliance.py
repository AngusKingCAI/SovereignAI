#!/usr/bin/env python3
"""
Test script to verify agent compliance with their rules.

This script tests:
1. Agents reference correct rule file locations
2. Key architectural principles are followed
3. SSOT compliance is maintained
4. Governance file references are accurate
"""

import re
import sys
from pathlib import Path
from typing import Dict, List, Tuple

def test_governance_file_references() -> bool:
    """Test that governance files reference correct .devin/rules/ locations."""
    governance_files = [
        "AGENTS.md",
        "STRUCTURE.md",
        ".devin/rules/architect.md",
        ".devin/rules/reviewer.md"
    ]
    
    all_compliant = True
    
    for file_path in governance_files:
        file = Path(file_path)
        if not file.exists():
            print(f"⚠️  SKIP: {file_path} does not exist")
            continue
            
        try:
            with open(file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Check for old Rules/ references
            old_rules_pattern = r'Rules/\{Agent\}/\{Agent\}_Rules\.md|Rules/[A-Z][a-z]+/[A-Z][a-z]+_Rules\.md'
            old_matches = re.findall(old_rules_pattern, content)
            
            if old_matches:
                print(f"[FAIL] {file_path} contains old Rules/ references: {old_matches}")
                all_compliant = False
            else:
                print(f"[PASS] {file_path} has no old Rules/ references")
            
            # Check for correct .devin/rules/ references
            if ".devin/rules/" in content:
                print(f"[PASS] {file_path} references .devin/rules/")
            else:
                print(f"[WARN] {file_path} may not reference .devin/rules/")
                
        except Exception as e:
            print(f"[FAIL] Error reading {file_path}: {e}")
            all_compliant = False
    
    return all_compliant

def test_workflow_file_references() -> bool:
    """Test that workflow files reference correct rule locations."""
    workflow_dir = Path("Workflow")
    
    if not workflow_dir.exists():
        print("[SKIP] Workflow/ directory does not exist")
        return True
    
    all_compliant = True
    workflow_files = list(workflow_dir.rglob("*.md"))
    
    for workflow_file in workflow_files:
        try:
            with open(workflow_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Check for old Rules/ references
            old_rules_pattern = r'Rules/\{Agent\}/\{Agent\}_Rules\.md|Rules/[A-Z][a-z]+/[A-Z][a-z]+_Rules\.md'
            old_matches = re.findall(old_rules_pattern, content)
            
            if old_matches:
                print(f"[FAIL] {workflow_file.relative_to(Path.cwd())} contains old Rules/ references")
                all_compliant = False
                
        except Exception as e:
            print(f"[WARN] Error reading {workflow_file}: {e}")
    
    if all_compliant:
        print(f"[PASS] All {len(workflow_files)} workflow files have correct rule references")
    
    return all_compliant

def test_ssot_compliance() -> bool:
    """Test SSOT compliance - no redundant index files."""
    violations = []
    
    # Check for index.md files
    index_files = list(Path(".").rglob("index.md")) + list(Path(".").rglob("INDEX.md"))
    
    # Allow only in specific locations (historical logs)
    allowed_locations = ["Logs/", "Logs/.Archived/"]
    
    for index_file in index_files:
        file_str = str(index_file)
        if not any(loc in file_str for loc in allowed_locations):
            violations.append(index_file)
    
    if violations:
        print(f"[FAIL] Found index.md files outside allowed locations: {violations}")
        return False
    else:
        print("[PASS] No index.md files in prohibited locations")
    
    # Check that STRUCTURE.md exists and is referenced
    structure_file = Path("STRUCTURE.md")
    if not structure_file.exists():
        print("[FAIL] STRUCTURE.md does not exist (SSOT violation)")
        return False
    else:
        print("[PASS] STRUCTURE.md exists as SSOT for file placement")
    
    return True

def test_agent_rules_lowercase_naming() -> bool:
    """Test that .devin/rules/ files follow lowercase naming convention."""
    rules_dir = Path(".devin/rules")
    
    if not rules_dir.exists():
        print("[FAIL] .devin/rules/ directory does not exist")
        return False
    
    all_compliant = True
    rule_files = list(rules_dir.glob("*.md"))
    
    for rule_file in rule_files:
        # Check if filename is lowercase
        if rule_file.name != rule_file.name.lower():
            print(f"[FAIL] {rule_file.name} does not follow lowercase naming convention")
            all_compliant = False
        else:
            print(f"[PASS] {rule_file.name} follows lowercase naming")
    
    return all_compliant

def test_architect_rule_compliance() -> bool:
    """Test specific architect rule compliance."""
    architect_rules = Path(".devin/rules/architect.md")
    
    if not architect_rules.exists():
        print("[FAIL] .devin/rules/architect.md does not exist")
        return False
    
    try:
        with open(architect_rules, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check for critical rule about not creating index.md files
        if "Never create index.md files" in content:
            print("[PASS] Architect rules prohibit index.md creation")
        else:
            print("[WARN] Architect rules may not explicitly prohibit index.md creation")
        
        # Check for SSOT compliance rule
        if "SSOT" in content:
            print("[PASS] Architect rules reference SSOT principles")
        else:
            print("[WARN] Architect rules may not reference SSOT")
            
        return True
        
    except Exception as e:
        print(f"[FAIL] Error reading architect rules: {e}")
        return False

def main():
    """Run all compliance tests."""
    print("=" * 60)
    print("Testing Agent Rule Compliance")
    print("=" * 60)
    
    tests = [
        ("Governance File References", test_governance_file_references),
        ("Workflow File References", test_workflow_file_references),
        ("SSOT Compliance", test_ssot_compliance),
        ("Agent Rules Lowercase Naming", test_agent_rules_lowercase_naming),
        ("Architect Rule Compliance", test_architect_rule_compliance)
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n{test_name}:")
        print("-" * 40)
        result = test_func()
        results.append((test_name, result))
    
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "[PASS]" if result else "[FAIL]"
        print(f"{status}: {test_name}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n[SUCCESS] All compliance tests passed!")
        return 0
    else:
        print(f"\n[WARNING] {total - passed} test(s) failed")
        return 1

if __name__ == "__main__":
    sys.exit(main())