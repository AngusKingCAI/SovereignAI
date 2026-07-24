#!/usr/bin/env python3
"""
Comprehensive hook system test suite.
Tests all configured hooks for proper functionality and integration.
"""

import subprocess
import json
import sys
from pathlib import Path

def run_hook_test(hook_path, event_data, expected_exit_code=0):
    """Run a hook with test data and check exit code."""
    try:
        # Convert event data to JSON string
        input_data = json.dumps(event_data)
        
        # Run the hook
        result = subprocess.run(
            ['python', hook_path],
            input=input_data,
            capture_output=True,
            text=True,
            timeout=30
        )
        
        success = result.returncode == expected_exit_code
        return {
            'success': success,
            'exit_code': result.returncode,
            'stdout': result.stdout,
            'stderr': result.stderr,
            'expected_exit_code': expected_exit_code
        }
    except subprocess.TimeoutExpired:
        return {
            'success': False,
            'exit_code': None,
            'stdout': '',
            'stderr': 'Hook timed out',
            'expected_exit_code': expected_exit_code
        }
    except Exception as e:
        return {
            'success': False,
            'exit_code': None,
            'stdout': '',
            'stderr': str(e),
            'expected_exit_code': expected_exit_code
        }

def test_session_start_hooks():
    """Test SessionStart hooks."""
    print("=== Testing SessionStart Hooks ===")
    
    hooks_dir = Path("C:/SovereignAI/Scripts/Governance/Hooks")
    
    # Test rule cache hook
    print("Testing rule_cache_hook.py...")
    result = run_hook_test(
        str(hooks_dir / "rule_cache_hook.py"),
        {"hook_event_name": "SessionStart"},
        expected_exit_code=0
    )
    
    if result['success']:
        print("[PASS] rule_cache_hook.py passed")
    else:
        print(f"[FAIL] rule_cache_hook.py failed: {result['stderr']}")
    
    # Test unified session logger
    print("Testing unified_session_logger.py...")
    result = run_hook_test(
        str(hooks_dir / "unified_session_logger.py"),
        {"hook_event_name": "SessionStart"},
        expected_exit_code=0
    )
    
    if result['success']:
        print("[PASS] unified_session_logger.py passed")
    else:
        print(f"[FAIL] unified_session_logger.py failed: {result['stderr']}")

def test_user_prompt_submit_hooks():
    """Test UserPromptSubmit hooks."""
    print("\n=== Testing UserPromptSubmit Hooks ===")
    
    hooks_dir = Path("C:/SovereignAI/Scripts/Governance/Hooks")
    
    # Test chat capture hook
    print("Testing chat_capture_hook.py...")
    result = run_hook_test(
        str(hooks_dir / "chat_capture_hook.py"),
        {
            "hook_event_name": "UserPromptSubmit",
            "prompt": "Test user message",
            "session_id": "test-session-123"
        },
        expected_exit_code=0
    )
    
    if result['success']:
        print("[PASS] chat_capture_hook.py passed")
    else:
        print(f"[FAIL] chat_capture_hook.py failed: {result['stderr']}")

def test_pre_tool_use_hooks():
    """Test PreToolUse hooks."""
    print("\n=== Testing PreToolUse Hooks ===")
    
    hooks_dir = Path("C:/SovereignAI/Scripts/Governance/Hooks")
    
    # Test block_destructive.py with safe command
    print("Testing block_destructive.py (safe command)...")
    result = run_hook_test(
        str(hooks_dir / "block_destructive.py"),
        {
            "hook_event_name": "PreToolUse",
            "tool_name": "exec",
            "tool_input": {"command": "echo hello"}
        },
        expected_exit_code=0
    )
    
    if result['success']:
        print("[PASS] block_destructive.py (safe) passed")
    else:
        print(f"[FAIL] block_destructive.py (safe) failed: {result['stderr']}")
    
    # Test block_destructive.py with destructive command
    print("Testing block_destructive.py (destructive command)...")
    result = run_hook_test(
        str(hooks_dir / "block_destructive.py"),
        {
            "hook_event_name": "PreToolUse",
            "tool_name": "exec",
            "tool_input": {"command": "rm -rf /tmp/test"}
        },
        expected_exit_code=2  # Should block with exit code 2
    )
    
    if result['success']:
        print("[PASS] block_destructive.py (destructive) passed")
    else:
        print(f"[FAIL] block_destructive.py (destructive) failed: {result['stderr']}")
    
    # Test tool_permission_check.py with allowed path
    print("Testing tool_permission_check.py (allowed path)...")
    result = run_hook_test(
        str(hooks_dir / "tool_permission_check.py"),
        {
            "hook_event_name": "PreToolUse",
            "tool_name": "write",
            "file_path": "C:/SovereignAI/test.txt"
        },
        expected_exit_code=0
    )
    
    if result['success']:
        print("[PASS] tool_permission_check.py (allowed) passed")
    else:
        print(f"[FAIL] tool_permission_check.py (allowed) failed: {result['stderr']}")
    
    # Test tool_permission_check.py with blocked path
    print("Testing tool_permission_check.py (blocked path)...")
    result = run_hook_test(
        str(hooks_dir / "tool_permission_check.py"),
        {
            "hook_event_name": "PreToolUse",
            "tool_name": "write",
            "file_path": "C:/Windows/test.txt"
        },
        expected_exit_code=2  # Should block with exit code 2
    )
    
    if result['success']:
        print("[PASS] tool_permission_check.py (blocked) passed")
    else:
        print(f"[FAIL] tool_permission_check.py (blocked) failed: {result['stderr']}")

def test_post_tool_use_hooks():
    """Test PostToolUse hooks."""
    print("\n=== Testing PostToolUse Hooks ===")
    
    hooks_dir = Path("C:/SovereignAI/Scripts/Governance/Hooks")
    
    # Test transcript_monitor.py
    print("Testing transcript_monitor.py...")
    result = run_hook_test(
        str(hooks_dir / "transcript_monitor.py"),
        {
            "hook_event_name": "PostToolUse",
            "transcript_path": "C:/SovereignAI/test_transcript.jsonl"
        },
        expected_exit_code=0
    )
    
    if result['success']:
        print("[PASS] transcript_monitor.py passed")
    else:
        print(f"[FAIL] transcript_monitor.py failed: {result['stderr']}")
    
    # Test tool_audit_logger.py
    print("Testing tool_audit_logger.py...")
    result = run_hook_test(
        str(hooks_dir / "tool_audit_logger.py"),
        {
            "hook_event_name": "PostToolUse",
            "tool_name": "read",
            "tool_input": {"file_path": "test.txt"},
            "tool_result": {"success": True}
        },
        expected_exit_code=0
    )
    
    if result['success']:
        print("[PASS] tool_audit_logger.py passed")
    else:
        print(f"[FAIL] tool_audit_logger.py failed: {result['stderr']}")

def test_session_end_hooks():
    """Test SessionEnd hooks."""
    print("\n=== Testing SessionEnd Hooks ===")
    
    hooks_dir = Path("C:/SovereignAI/Scripts/Governance/Hooks")
    
    # Test unified session logger (SessionEnd)
    print("Testing unified_session_logger.py (SessionEnd)...")
    result = run_hook_test(
        str(hooks_dir / "unified_session_logger.py"),
        {"hook_event_name": "SessionEnd"},
        expected_exit_code=0
    )
    
    if result['success']:
        print("[PASS] unified_session_logger.py (SessionEnd) passed")
    else:
        print(f"[FAIL] unified_session_logger.py (SessionEnd) failed: {result['stderr']}")

def test_rule_cache_accessor():
    """Test rule cache accessor functionality."""
    print("\n=== Testing Rule Cache Accessor ===")
    
    hooks_dir = Path("C:/SovereignAI/Scripts/Governance/Hooks")
    
    # Test rule cache accessor
    print("Testing rule_cache_accessor.py...")
    result = subprocess.run(
        ['python', str(hooks_dir / "rule_cache_accessor.py")],
        capture_output=True,
        text=True,
        timeout=30
    )
    
    if result.returncode == 0:
        print("[PASS] rule_cache_accessor.py passed")
    else:
        print(f"[FAIL] rule_cache_accessor.py failed: {result['stderr']}")

def main():
    """Run comprehensive hook system tests."""
    print("=== Comprehensive Hook System Test Suite ===\n")
    
    try:
        test_session_start_hooks()
        test_user_prompt_submit_hooks()
        test_pre_tool_use_hooks()
        test_post_tool_use_hooks()
        test_session_end_hooks()
        test_rule_cache_accessor()
        
        print("\n=== Hook System Test Suite Complete ===")
        print("All critical hooks have been tested")
        
    except Exception as e:
        print(f"Test suite error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()