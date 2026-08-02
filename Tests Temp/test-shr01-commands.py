#!/usr/bin/env python3
"""Test SHR-01 safety commands rule."""
import sys
import json
from pathlib import Path

# Add Scripts/Rules to path
sys.path.insert(0, str(Path(__file__).parent.parent / "Scripts" / "Rules"))

from Enforcement.evaluator import evaluate_rule

# Load rule
import yaml
rule_file = Path(__file__).parent.parent / "Rules" / "Shared" / "SHR-01-safety-commands.yaml"
rule = yaml.safe_load(rule_file.read_text())

# Test cases
test_cases = [
    {"command": "rm -rf /tmp/test", "expected": "deny"},
    {"command": "rm single_file.txt", "expected": "deny"},
    {"command": "git restore file.txt", "expected": "deny"},
    {"command": "git fetch origin", "expected": "deny"},
    {"command": "git push origin main --force", "expected": "deny"},
    {"command": "echo 'safe command'", "expected": "allow"},
    {"command": "ls -la", "expected": "allow"},
]

print("Testing SHR-01 Safety Commands Rule:")
for i, test in enumerate(test_cases, 1):
    tool_call = {"tool": "exec", "input": {"command": test["command"]}}
    result = evaluate_rule(rule, tool_call)
    status = "✓" if result["decision"] == test["expected"] else "✗"
    print(f"  {status} Test {i}: {test['command']} - Expected: {test['expected']}, Got: {result['decision']}")
    if result["decision"] != test["expected"]:
        print(f"     Reason: {result.get('reason', 'N/A')}")

print("\nSHR-01 tests complete")
