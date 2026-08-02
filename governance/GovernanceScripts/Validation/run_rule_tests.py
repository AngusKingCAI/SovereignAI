# Governance/GovernanceScripts/Validation/run_rule_tests.py
# Frontmatter: id: run_rule_tests, version: 1.0.0, owner: SovereignAI, updated: 2026-08-02, purpose: Run every Policy Card's test_cases against its check function, agent: all, persona: governance
#!/usr/bin/env python3
"""Run every Policy Card's test_cases against its check function."""
import sys
import yaml
import json
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent
POLICY_CARDS_DIR = PROJECT_ROOT / "Governance" / "Policy-cards"

def main():
    total_pass = 0
    total_fail = 0
    failures = []
    
    for card_file in POLICY_CARDS_DIR.rglob("*.yaml"):
        card = yaml.safe_load(card_file.read_text())
        card_id = card.get("id", "?")
        test_cases = card.get("test_cases", [])
        
        if len(test_cases) < 2:
            failures.append(f"{card_id}: requires ≥2 test_cases, found {len(test_cases)}")
            total_fail += 1
            continue
        
        for tc in test_cases:
            # Run the check function against the test input
            result = run_check(card, tc["input"])
            expected = tc["expected"]
            if result == expected:
                total_pass += 1
            else:
                failures.append(
                    f"{card_id} / {tc['name']}: expected {expected}, got {result}"
                )
                total_fail += 1
    
    print(f"Rule tests: {total_pass} passed, {total_fail} failed")
    if failures:
        print("\nFailures:")
        for f in failures:
            print(f"  - {f}")
        sys.exit(1)
    print("All rule tests passed")
    sys.exit(0)

def run_check(card, test_input):
    """Run the card's check against test_input. Returns pass/fail/deny/allow."""
    # Implementation depends on check type — delegates to enforcement module
    import sys
    sys.path.insert(0, str(Path(__file__).parent.parent))
    from enforcement.evaluator import evaluate_rule
    
    check_type = card.get("check", {}).get("type")
    
    # Build appropriate tool call shape based on check type
    if check_type == "deny_command":
        tool_call = {"tool": "exec", "input": {"command": test_input}}
    elif check_type == "path_pattern":
        tool_call = {"tool": "write", "input": {"file_path": test_input}}
    elif check_type == "require_field":
        # For require_field, test_input should be a file path - read the file content
        test_file = Path(test_input)
        if test_file.exists():
            content = test_file.read_text()
        else:
            content = test_input  # Use as-is if file doesn't exist
        tool_call = {"tool": "write", "input": {"content": content}}
    elif check_type == "yaml_field":
        # For yaml_field, test_input should be a file path - read the file content
        test_file = Path(test_input)
        if test_file.exists():
            content = test_file.read_text()
        else:
            content = test_input  # Use as-is if file doesn't exist
        tool_call = {"tool": "write", "input": {"content": content}}
    elif check_type == "regex":
        tool_call = {"tool": "exec", "input": {"command": test_input}}
    elif check_type == "json_schema":
        # For json_schema, test_input should be JSON
        try:
            json_input = json.loads(test_input) if isinstance(test_input, str) else test_input
            tool_call = {"tool": "test", "input": json_input}
        except:
            tool_call = {"tool": "test", "input": {}}
    elif check_type == "custom_function":
        # For custom_function, pass as-is
        tool_call = {"tool": "test", "input": {"data": test_input}}
    else:
        # Default fallback
        tool_call = {"tool": "test", "input": {"command": test_input}}
    
    result = evaluate_rule(card, tool_call)
    return "deny" if result["decision"] == "deny" else "allow"

if __name__ == "__main__":
    main()
