# Scripts/Rules/Validation/check_coverage.py
# id: check_coverage, version: 1.0.0, owner: SovereignAI, updated: 2026-08-02, purpose: Check rule coverage, agent: all, persona: governance
#!/usr/bin/env python3
"""Check rule coverage for governance files."""
import sys
import yaml
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent
RULES_DIR = PROJECT_ROOT / "Rules"

def main():
    # Check that all rules have test cases
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
                print(f"! {rule_id}: requires ≥2 test_cases, found {len(test_cases)}")
                sys.exit(1)
        except Exception as e:
            print(f"! {rule_file.name}: error checking coverage: {e}")
            sys.exit(1)
    
    print("All rules have adequate test coverage")
    sys.exit(0)

if __name__ == "__main__":
    main()