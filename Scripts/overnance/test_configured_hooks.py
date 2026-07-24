#!/usr/bin/env python3
"""
Test currently configured hooks in hooks.v1.json.
"""

import subprocess
import json
import sys
from pathlib import Path

def test_hook(hook_path, test_data, expected_exit_codes=[0, 2]):
    """Test a hook with specific data."""
    try:
        input_data = json.dumps(test_data)
        result = subprocess.run(
            ['python', hook_path],
            input=input_data,
            capture_output=True,
            text=True,
            timeout=30
        )
        success = result.returncode in expected_exit_codes
        return success, result.returncode, result.stderr, result.stdout
    except subprocess.TimeoutExpired:
        return False, None, "Hook timed out", ""
    except Exception as e:
        return False, None, str(e), ""

def main():
    """Test all configured hooks."""
    print("=== Testing Configured Hooks ===\n")
    
    hooks_dir = Path("C:/SovereignAI/Scripts/Governance/Hooks")
    
    # SessionStart hooks
    print("SessionStart Hooks:")
    session_start_data = {"hook_event_name": "SessionStart"}
    
    hooks_to_test = [
        ("rule_cache_hook.py", session_start_data, [0]),
        ("unified_session_logger.py", session_start_data, [0]),
    ]
    
    for hook_name, test_data, expected_codes in hooks_to_test:
        hook_path = hooks_dir / hook_name
        success, exit_code, stderr, stdout = test_hook(str(hook_path), test_data, expected_codes)
        status = "[PASS]" if success else "[FAIL]"
        print(f"  {status} {hook_name} (exit: {exit_code})")
        if not success:
            print(f"    Error: {stderr}")
    
    # UserPromptSubmit hooks
    print("\nUserPromptSubmit Hooks:")
    user_prompt_data = {
        "hook_event_name": "UserPromptSubmit",
        "prompt": "Test message",
        "session_id": "test-123"
    }
    
    hook_path = hooks_dir / "chat_capture_hook.py"
    success, exit_code, stderr, stdout = test_hook(str(hook_path), user_prompt_data, [0])
    status = "[PASS]" if success else "[FAIL]"
    print(f"  {status} chat_capture_hook.py (exit: {exit_code})")
    if not success:
        print(f"    Error: {stderr}")
    
    # PreToolUse hooks
    print("\nPreToolUse Hooks:")
    
    # Test block_destructive with safe command
    safe_exec_data = {
        "hook_event_name": "PreToolUse",
        "tool_name": "exec",
        "tool_input": {"command": "echo hello"}
    }
    hook_path = hooks_dir / "block_destructive.py"
    success, exit_code, stderr, stdout = test_hook(str(hook_path), safe_exec_data, [0])
    status = "[PASS]" if success else "[FAIL]"
    print(f"  {status} block_destructive.py (safe) (exit: {exit_code})")
    if not success:
        print(f"    Error: {stderr}")
    
    # Test block_destructive with destructive command
    destructive_exec_data = {
        "hook_event_name": "PreToolUse",
        "tool_name": "exec",
        "tool_input": {"command": "rm -rf /tmp/test"}
    }
    success, exit_code, stderr, stdout = test_hook(str(hook_path), destructive_exec_data, [2])
    status = "[PASS]" if success else "[FAIL]"
    print(f"  {status} block_destructive.py (destructive) (exit: {exit_code})")
    if not success:
        print(f"    Error: {stderr}")
    
    # Test tool_permission_check with allowed path
    allowed_data = {
        "hook_event_name": "PreToolUse",
        "tool_name": "write",
        "file_path": "C:/SovereignAI/test.txt"
    }
    hook_path = hooks_dir / "tool_permission_check.py"
    success, exit_code, stderr, stdout = test_hook(str(hook_path), allowed_data, [0])
    status = "[PASS]" if success else "[FAIL]"
    print(f"  {status} tool_permission_check.py (allowed) (exit: {exit_code})")
    if not success:
        print(f"    Error: {stderr}")
    
    # Test tool_permission_check with blocked path
    blocked_data = {
        "hook_event_name": "PreToolUse",
        "tool_name": "write",
        "file_path": "C:/Windows/test.txt"
    }
    success, exit_code, stderr, stdout = test_hook(str(hook_path), blocked_data, [2])
    status = "[PASS]" if success else "[FAIL]"
    print(f"  {status} tool_permission_check.py (blocked) (exit: {exit_code})")
    if not success:
        print(f"    Error: {stderr}")
    
    # PostToolUse hooks
    print("\nPostToolUse Hooks:")
    post_tool_data = {
        "hook_event_name": "PostToolUse",
        "tool_name": "read",
        "tool_input": {"file_path": "test.txt"},
        "tool_result": {"success": True}
    }
    
    hooks_to_test = [
        ("transcript_monitor.py", post_tool_data, [0]),
        ("tool_audit_logger.py", post_tool_data, [0]),
    ]
    
    for hook_name, test_data, expected_codes in hooks_to_test:
        hook_path = hooks_dir / hook_name
        success, exit_code, stderr, stdout = test_hook(str(hook_path), test_data, expected_codes)
        status = "[PASS]" if success else "[FAIL]"
        print(f"  {status} {hook_name} (exit: {exit_code})")
        if not success:
            print(f"    Error: {stderr}")
    
    # SessionEnd hooks
    print("\nSessionEnd Hooks:")
    session_end_data = {"hook_event_name": "SessionEnd"}
    
    hook_path = hooks_dir / "unified_session_logger.py"
    success, exit_code, stderr, stdout = test_hook(str(hook_path), session_end_data, [0])
    status = "[PASS]" if success else "[FAIL]"
    print(f"  {status} unified_session_logger.py (exit: {exit_code})")
    if not success:
        print(f"    Error: {stderr}")
    
    print("\n=== Hook Testing Complete ===")

if __name__ == "__main__":
    main()