#!/usr/bin/env python3
"""
Test Hook Script: Validate hook configuration

This script tests the hook system by validating:
1. Hook configuration file format
2. Hook scripts exist and are executable
3. Hook scripts return expected exit codes
"""

import sys
import json
import os
from pathlib import Path

def test_hook_config():
    """Test hook configuration file"""
    print("Testing hook configuration...")
    
    config_path = Path(".devin/hooks.v1.json")
    if not config_path.exists():
        print(f"[FAIL] Hook configuration file not found: {config_path}")
        return False
    
    try:
        with open(config_path, 'r') as f:
            config = json.load(f)
        
        print(f"[PASS] Hook configuration file loaded successfully")
        
        # Check required hooks
        required_hooks = ["PreToolUse", "PostToolUse", "SessionStart", "SessionEnd"]
        for hook in required_hooks:
            if hook not in config:
                print(f"[FAIL] Required hook not found: {hook}")
                return False
            print(f"[PASS] Hook '{hook}' defined in configuration")
        
        return True
    except json.JSONDecodeError as e:
        print(f"[FAIL] Hook configuration file invalid JSON: {e}")
        return False

def test_hook_scripts():
    """Test hook scripts exist and are executable"""
    print("\nTesting hook scripts...")
    
    hooks_dir = Path(".Planner/scripts/hooks")
    if not hooks_dir.exists():
        print(f"[FAIL] Hooks directory not found: {hooks_dir}")
        return False
    
    hook_scripts = {
        "PreToolUse": ["pretooluse_plan_write.py"],
        "PostToolUse": ["posttooluse_plan_write.py"],
        "SessionStart": ["session_start.py"],
        "SessionEnd": ["session_end.py"]
    }
    
    all_passed = True
    for hook_type, scripts in hook_scripts.items():
        for script in scripts:
            script_path = hooks_dir / script
            if not script_path.exists():
                print(f"[FAIL] Hook script not found: {script_path}")
                all_passed = False
            else:
                print(f"[PASS] Hook script exists: {script_path}")
    
    return all_passed

def test_hook_execution():
    """Test hook scripts can be executed"""
    print("\nTesting hook script execution...")
    
    hooks_dir = Path(".Planner/scripts/hooks")
    test_scripts = ["session_start.py", "session_end.py"]
    
    all_passed = True
    for script in test_scripts:
        script_path = hooks_dir / script
        if script_path.exists():
            try:
                result = os.system(f"python {script_path}")
                if result == 0:
                    print(f"[PASS] Hook script executed successfully: {script}")
                else:
                    print(f"[FAIL] Hook script returned non-zero exit code: {script} (exit code: {result})")
                    all_passed = False
            except Exception as e:
                print(f"[FAIL] Hook script execution failed: {script} (error: {e})")
                all_passed = False
    
    return all_passed

def main():
    print("=" * 60)
    print("Hook System Test Suite")
    print("=" * 60)
    
    tests = [
        ("Hook Configuration", test_hook_config),
        ("Hook Scripts Exist", test_hook_scripts),
        ("Hook Script Execution", test_hook_execution)
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
    
    for test_name, result in results:
        status = "[PASS]" if result else "[FAIL]"
        print(f"{status}: {test_name}")
    
    all_passed = all(result for _, result in results)
    print("=" * 60)
    
    if all_passed:
        print("[PASS] All hook system tests passed")
        sys.exit(0)
    else:
        print("[FAIL] Some hook system tests failed")
        sys.exit(1)

if __name__ == "__main__":
    main()