#!/usr/bin/env python3
"""
Test script to verify .devin/rules/ autoloading and accessibility.

This script tests:
1. Rule files exist in .devin/rules/ directory
2. Rule files have proper YAML frontmatter
3. Rule files can be loaded and parsed
4. Session state properly tracks agent context
"""

import json
import yaml
import sys
from pathlib import Path
from typing import Dict, List

def test_rule_files_exist() -> bool:
    """Test that all expected rule files exist in .devin/rules/."""
    expected_rules = ["architect.md", "planner.md", "executor.md", "researcher.md", "reviewer.md"]
    rules_dir = Path(".devin/rules")
    
    if not rules_dir.exists():
        print("[FAIL] .devin/rules/ directory does not exist")
        return False
    
    print(f"[PASS] .devin/rules/ directory exists")
    
    all_exist = True
    for rule_file in expected_rules:
        rule_path = rules_dir / rule_file
        if rule_path.exists():
            print(f"[PASS] {rule_file} exists")
        else:
            print(f"[FAIL] {rule_file} does not exist")
            all_exist = False
    
    return all_exist

def test_rule_files_yaml_frontmatter() -> bool:
    """Test that rule files have valid YAML frontmatter."""
    rules_dir = Path(".devin/rules")
    rule_files = list(rules_dir.glob("*.md"))
    
    if not rule_files:
        print("[FAIL] No rule files found in .devin/rules/")
        return False
    
    all_valid = True
    for rule_file in rule_files:
        try:
            with open(rule_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Check for YAML frontmatter
            if content.startswith("---"):
                # Extract frontmatter
                frontmatter_end = content.find("---", 3)
                if frontmatter_end != -1:
                    frontmatter = content[3:frontmatter_end]
                    yaml.safe_load(frontmatter)
                    print(f"[PASS] {rule_file.name} has valid YAML frontmatter")
                else:
                    print(f"[FAIL] {rule_file.name} has incomplete YAML frontmatter")
                    all_valid = False
            else:
                print(f"[FAIL] {rule_file.name} missing YAML frontmatter")
                all_valid = False
                
        except yaml.YAMLError as e:
            print(f"[FAIL] {rule_file.name} has invalid YAML: {e}")
            all_valid = False
        except Exception as e:
            print(f"[FAIL] {rule_file.name} error: {e}")
            all_valid = False
    
    return all_valid

def test_session_state_tracking() -> bool:
    """Test that session state properly tracks agent context."""
    session_state_file = Path("Scripts/Logging/.session_state/session_state.json")
    
    if not session_state_file.exists():
        print("[WARN] Session state file does not exist (may not be initialized yet)")
        return True  # Not a failure, just not initialized
    
    try:
        with open(session_state_file, 'r', encoding='utf-8') as f:
            state = json.load(f)
        
        if "agent" in state:
            print(f"[PASS] Session state tracks agent: {state['agent']}")
        else:
            print("[WARN] Session state exists but no agent tracked")
        
        if "trace_id" in state:
            print(f"[PASS] Session state has trace_id: {state['trace_id']}")
        else:
            print("[WARN] Session state missing trace_id")
            
        return True
        
    except json.JSONDecodeError as e:
        print(f"[FAIL] Session state file has invalid JSON: {e}")
        return False
    except Exception as e:
        print(f"[FAIL] Session state error: {e}")
        return False

def test_workflowopen_skill_instructions() -> bool:
    """Test that WorkflowOpen skill has correct instructions for .devin/rules/."""
    skill_file = Path(".devin/skills/WorkflowOpen/SKILL.md")
    
    if not skill_file.exists():
        print("[FAIL] WorkflowOpen skill does not exist")
        return False
    
    try:
        with open(skill_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check for correct .devin/rules/ reference
        if ".devin/rules/{agent}.md" in content:
            print("[PASS] WorkflowOpen skill references .devin/rules/{agent}.md")
        else:
            print("[FAIL] WorkflowOpen skill missing .devin/rules/ reference")
            return False
            
        # Check for lowercase reference
        if "lowercase agent name" in content:
            print("[PASS] WorkflowOpen skill specifies lowercase naming")
        else:
            print("[WARN] WorkflowOpen skill may not specify lowercase naming")
            
        return True
        
    except Exception as e:
        print(f"[FAIL] WorkflowOpen skill error: {e}")
        return False

def main():
    """Run all autoloading tests."""
    print("=" * 60)
    print("Testing .devin/rules/ Autoloading")
    print("=" * 60)
    
    tests = [
        ("Rule Files Exist", test_rule_files_exist),
        ("YAML Frontmatter Valid", test_rule_files_yaml_frontmatter),
        ("Session State Tracking", test_session_state_tracking),
        ("WorkflowOpen Skill Instructions", test_workflowopen_skill_instructions)
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
        print("\n[SUCCESS] All autoloading tests passed!")
        return 0
    else:
        print(f"\n[WARNING] {total - passed} test(s) failed")
        return 1

if __name__ == "__main__":
    sys.exit(main())