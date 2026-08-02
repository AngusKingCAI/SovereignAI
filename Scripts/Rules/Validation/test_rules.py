# Scripts/Rules/Validation/test_rules.py
# id: test_rules, version: 1.0.0, owner: SovereignAI, updated: 2026-08-02, purpose: Test rule evaluation, agent: all, persona: governance
#!/usr/bin/env python3
"""Test rule evaluation against defined test cases."""
import sys
import yaml
import json
import os
from pathlib import Path
import io

# Set UTF-8 encoding for stdout
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent
RULES_DIR = PROJECT_ROOT / "Rules"

def main():
    total_pass = 0
    total_fail = 0
    failures = []
    
    for rule_file in RULES_DIR.rglob("*.yaml"):
        # Skip non-rule files and templates
        if rule_file.name in ["constitution.yaml", "rule-index.yaml"]:
            continue
        if "Templates" in rule_file.parts:
            continue
        
        try:
            rule = yaml.safe_load(rule_file.read_text())
            rule_id = rule.get("id", "?")
            test_cases = rule.get("test_cases", [])
            
            if len(test_cases) < 2:
                failures.append(f"{rule_id}: requires ≥2 test_cases, found {len(test_cases)}")
                total_fail += 1
                continue
            
            for tc in test_cases:
                result = evaluate_rule(rule, tc["input"])
                expected = tc["expected"]
                
                # Map expected values to decision values
                expected_decision = "deny" if expected in ["fail", "deny"] else "allow"
                actual_decision = result["decision"]
                
                if actual_decision == expected_decision:
                    total_pass += 1
                else:
                    failures.append(
                        f"{rule_id} / {tc.get('name', 'unnamed')}: expected {expected}, got {actual_decision}"
                    )
                    total_fail += 1
        except Exception as e:
            failures.append(f"{rule_file.name}: error during testing: {e}")
            total_fail += 1
    
    print(f"Rule tests: {total_pass} passed, {total_fail} failed")
    if failures:
        print("\nFailures:")
        for f in failures:
            print(f"  - {f}")
        sys.exit(1)
    print("All rule tests passed")
    sys.exit(0)

def evaluate_rule(rule, test_input):
    """Evaluate rule against test input."""
    # Import evaluator
    rules_dir = Path(__file__).parent.parent
    sys.path.insert(0, str(rules_dir))
    from Enforcement.evaluator import evaluate_rule as evaluator_evaluate_rule
    
    # Build appropriate tool call based on rule ID
    rule_id = rule.get("id", "")
    
    # Map rule IDs to expected file names
    if rule_id == "SHR-01":
        tool_call = {"tool": "exec", "input": {"command": test_input}}
    elif rule_id == "SHR-02":
        tool_call = {"tool": "edit", "input": {"content": test_input, "file_path": "test.md"}}
    elif rule_id == "SHR-03":
        tool_call = {"tool": "write", "input": {"file_path": "Rules/test.md", "content": test_input}}
    elif rule_id == "SHR-04":
        tool_call = {"tool": "write", "input": {"file_path": test_input}}
    elif rule_id == "ARR-01":
        tool_call = {"tool": "write", "input": {"file_path": test_input}}
    else:
        tool_call = {"tool": "test", "input": {"command": test_input}}
    
    # Set environment for testing
    os.environ["HOOK_EVENT"] = "PreToolUse"
    os.environ["ACTIVE_AGENT"] = "architect"
    
    return evaluator_evaluate_rule(rule, tool_call)

if __name__ == "__main__":
    main()