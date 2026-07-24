#!/usr/bin/env python3
"""
Comprehensive hook audit script.
Tests all hooks in Scripts/Governance/Hooks for basic functionality.
"""

import subprocess
import json
import sys
from pathlib import Path

def test_hook_syntax(hook_path):
    """Test if hook has valid Python syntax."""
    try:
        result = subprocess.run(
            ['python', '-m', 'py_compile', str(hook_path)],
            capture_output=True,
            text=True,
            timeout=10
        )
        return result.returncode == 0, result.stderr
    except Exception as e:
        return False, str(e)

def test_hook_execution(hook_path, test_data):
    """Test if hook can execute with basic test data."""
    try:
        input_data = json.dumps(test_data)
        result = subprocess.run(
            ['python', str(hook_path)],
            input=input_data,
            capture_output=True,
            text=True,
            timeout=30
        )
        return result.returncode in [0, 2], result.stderr, result.stdout
    except subprocess.TimeoutExpired:
        return False, "Hook timed out", ""
    except Exception as e:
        return False, str(e), ""

def audit_hooks():
    """Audit all hooks in the hooks directory."""
    hooks_dir = Path("C:/SovereignAI/Scripts/Governance/Hooks")
    hook_files = list(hooks_dir.glob("*.py"))
    
    # Exclude utility files and test files
    excluded = ['hook_utils.py', 'rule_cache_accessor.py', 'test_*.py']
    hook_files = [f for f in hook_files if not any(f.name.startswith(ex) or f.name == ex for ex in excluded)]
    
    print(f"=== Hook Audit Report ===")
    print(f"Found {len(hook_files)} hooks to audit\n")
    
    results = {
        'valid_syntax': [],
        'invalid_syntax': [],
        'executable': [],
        'non_executable': [],
        'needs_stdin': []
    }
    
    for hook_file in hook_files:
        hook_name = hook_file.name
        print(f"Auditing: {hook_name}")
        
        # Test syntax
        syntax_ok, syntax_error = test_hook_syntax(hook_file)
        if not syntax_ok:
            print(f"  [FAIL] Syntax error: {syntax_error}")
            results['invalid_syntax'].append(hook_name)
            continue
        
        print(f"  [OK] Valid syntax")
        results['valid_syntax'].append(hook_name)
        
        # Test execution with basic SessionStart data
        test_data = {"hook_event_name": "SessionStart"}
        exec_ok, exec_error, exec_output = test_hook_execution(hook_file, test_data)
        
        if exec_ok:
            print(f"  [OK] Executable")
            results['executable'].append(hook_name)
        else:
            print(f"  [WARN] Execution issue: {exec_error}")
            results['non_executable'].append(hook_name)
            
            # Check if it needs specific stdin data
            if "stdin" in exec_error.lower() or "json" in exec_error.lower():
                results['needs_stdin'].append(hook_name)
        
        print()
    
    # Print summary
    print("=== Audit Summary ===")
    print(f"Valid syntax: {len(results['valid_syntax'])}")
    print(f"Invalid syntax: {len(results['invalid_syntax'])}")
    print(f"Executable: {len(results['executable'])}")
    print(f"Non-executable: {len(results['non_executable'])}")
    print(f"Needs specific stdin: {len(results['needs_stdin'])}")
    
    if results['invalid_syntax']:
        print(f"\nHooks with syntax errors:")
        for hook in results['invalid_syntax']:
            print(f"  - {hook}")
    
    if results['non_executable']:
        print(f"\nHooks with execution issues:")
        for hook in results['non_executable']:
            print(f"  - {hook}")
    
    return results

if __name__ == "__main__":
    try:
        results = audit_hooks()
        sys.exit(0 if len(results['invalid_syntax']) == 0 else 1)
    except Exception as e:
        print(f"Audit error: {e}")
        sys.exit(1)