#!/usr/bin/env python3
"""
Integration test for hook system - simulates real project context
"""

import subprocess
import json
import sys
from pathlib import Path

def test_session_start():
    """Test SessionStart hook with real project context."""
    print("Testing SessionStart hook...")
    
    # Simulate SessionStart event
    event_data = {"hook_event_name": "SessionStart"}
    event_json = json.dumps(event_data)
    
    result = subprocess.run(
        ["python", "C:/SovereignAI/Scripts/Gating/Hooks/session_init.py"],
        input=event_json,
        capture_output=True,
        text=True
    )
    
    print(f"Exit code: {result.returncode}")
    print(f"Output: {result.stdout}")
    if result.stderr:
        print(f"Errors: {result.stderr}")
    
    # Check if session context was created
    session_context_file = Path("C:/SovereignAI/Logs/Architect/Gating/session-context.json")
    if session_context_file.exists():
        print("✅ Session context file created")
        with open(session_context_file) as f:
            context = json.load(f)
            print(f"Session ID: {context.get('session_id')}")
            print(f"Current Phase: {context.get('current_phase')}")
    else:
        print("❌ Session context file not created")
    
    return result.returncode == 0

def test_pre_tool_use_allowed():
    """Test PreToolUse hook with allowed operation."""
    print("\nTesting PreToolUse hook with allowed operation (read)...")
    
    # Simulate PreToolUse event for read operation
    event_data = {
        "tool_name": "read",
        "tool_input": {"file_path": "C:/SovereignAI/AGENTS.md"}
    }
    event_json = json.dumps(event_data)
    
    result = subprocess.run(
        ["python", "C:/SovereignAI/Scripts/Gating/Hooks/tool_permission_check.py"],
        input=event_json,
        capture_output=True,
        text=True
    )
    
    print(f"Exit code: {result.returncode}")
    print(f"Output: {result.stdout}")
    if result.stderr:
        print(f"Errors: {result.stderr}")
    
    if result.returncode == 0:
        print("✅ Read operation allowed in phase 0")
    else:
        print("❌ Read operation blocked unexpectedly")
    
    return result.returncode == 0

def test_pre_tool_use_forbidden():
    """Test PreToolUse hook with forbidden operation."""
    print("\nTesting PreToolUse hook with forbidden operation (edit App/)...")
    
    # Simulate PreToolUse event for forbidden operation
    event_data = {
        "tool_name": "edit",
        "tool_input": {"file_path": "C:/SovereignAI/App/test.py"}
    }
    event_json = json.dumps(event_data)
    
    result = subprocess.run(
        ["python", "C:/SovereignAI/Scripts/Gating/Hooks/tool_permission_check.py"],
        input=event_json,
        capture_output=True,
        text=True
    )
    
    print(f"Exit code: {result.returncode}")
    print(f"Output: {result.stdout}")
    if result.stderr:
        print(f"Errors: {result.stderr}")
    
    if result.returncode == 2:
        print("✅ Edit operation on App/ correctly blocked")
    else:
        print("❌ Edit operation on App/ not blocked as expected")
    
    return result.returncode == 2

def test_post_tool_use():
    """Test PostToolUse hook logging."""
    print("\nTesting PostToolUse hook logging...")
    
    # Simulate PostToolUse event
    event_data = {
        "tool_name": "read",
        "tool_input": {"file_path": "C:/SovereignAI/AGENTS.md"},
        "tool_result": {"success": true}
    }
    event_json = json.dumps(event_data)
    
    result = subprocess.run(
        ["python", "C:/SovereignAI/Scripts/Gating/Hooks/operation_logger.py"],
        input=event_json,
        capture_output=True,
        text=True
    )
    
    print(f"Exit code: {result.returncode}")
    print(f"Output: {result.stdout}")
    if result.stderr:
        print(f"Errors: {result.stderr}")
    
    # Check if audit trail was updated
    audit_log_file = Path("C:/SovereignAI/Logs/Architect/Gating/audit-trail.log")
    if audit_log_file.exists():
        print("✅ Audit trail updated")
        with open(audit_log_file) as f:
            log_content = f.read()
            print(f"Recent log entries: {log_content[-200:]}")
    else:
        print("❌ Audit trail not updated")
    
    return result.returncode == 0

def test_session_end():
    """Test SessionEnd hook finalization."""
    print("\nTesting SessionEnd hook finalization...")
    
    # Simulate SessionEnd event
    event_data = {"hook_event_name": "SessionEnd"}
    event_json = json.dumps(event_data)
    
    result = subprocess.run(
        ["python", "C:/SovereignAI/Scripts/Gating/Hooks/session_finalization.py"],
        input=event_json,
        capture_output=True,
        text=True
    )
    
    print(f"Exit code: {result.returncode}")
    print(f"Output: {result.stdout}")
    if result.stderr:
        print(f"Errors: {result.stderr}")
    
    # Check if session summary was created
    session_context_file = Path("C:/SovereignAI/Logs/Architect/Gating/session-context.json")
    if session_context_file.exists():
        with open(session_context_file) as f:
            context = json.load(f)
            session_id = context.get('session_id')
            summary_file = Path(f"C:/SovereignAI/Logs/Architect/Gating/session-{session_id}.json")
            if summary_file.exists():
                print("✅ Session summary file created")
            else:
                print("❌ Session summary file not created")
    else:
        print("❌ Session context file not found")
    
    return result.returncode == 0

def main():
    """Run all integration tests."""
    print("=" * 60)
    print("HOOK SYSTEM INTEGRATION TEST")
    print("=" * 60)
    
    results = []
    
    # Test all hooks in sequence
    results.append(("SessionStart", test_session_start()))
    results.append(("PreToolUse (allowed)", test_pre_tool_use_allowed()))
    results.append(("PreToolUse (forbidden)", test_pre_tool_use_forbidden()))
    results.append(("PostToolUse", test_post_tool_use()))
    results.append(("SessionEnd", test_session_end()))
    
    # Print summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    
    for test_name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{test_name}: {status}")
    
    all_passed = all(result[1] for result in results)
    
    if all_passed:
        print("\n🎉 All integration tests passed!")
        print("\nNEXT STEPS:")
        print("1. Restart Devin CLI to load the hooks from .devin/hooks.v1.json")
        print("2. Use /hooks command in Devin CLI to verify hooks are loaded")
        print("3. Perform real operations in the project to test hooks in actual context")
        return 0
    else:
        print("\n❌ Some integration tests failed")
        return 1

if __name__ == "__main__":
    sys.exit(main())
