# Scripts/Rules/Validation/validate_rules.py
# id: validate_rules, version: 1.0.0, owner: SovereignAI, updated: 2026-08-02, purpose: Validate rule YAML structure, agent: all, persona: governance
#!/usr/bin/env python3
"""Validate rule YAML structure and basic compliance."""
import sys
import yaml
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent
RULES_DIR = PROJECT_ROOT / "Rules"

def validate_rule_structure(rule_file: Path):
    """Validate basic rule structure."""
    try:
        with open(rule_file, 'r', encoding='utf-8') as f:
            rule = yaml.safe_load(f)
        
        # Required fields
        required_fields = ["id", "version", "tier", "severity", "agent", "domain", "constitutional_basis", "rule", "enforceable_via", "check"]
        missing = [f for f in required_fields if f not in rule]
        if missing:
            return False, f"Missing required fields: {', '.join(missing)}"
        
        # Check structure
        check = rule["check"]
        if "params" not in check:
            return False, "Missing 'check.params'"
        
        # Check for standardized required fields
        params = check["params"]
        if "target_tools" not in params:
            return False, "Missing required field 'check.params.target_tools'"
        if "message" not in params:
            return False, "Missing required field 'check.params.message'"
        
        # Check rule section fields
        rule_section = rule["rule"]
        if "statement" not in rule_section:
            return False, "Missing required field 'rule.statement'"
        if "rationale" not in rule_section:
            return False, "Missing required field 'rule.rationale'"
        
        return True, "Valid"
    except yaml.YAMLError as e:
        return False, f"YAML parsing error: {e}"
    except Exception as e:
        return False, f"Error: {e}"

def main():
    errors = []
    
    # Validate all YAML files in Rules directory
    for rule_file in RULES_DIR.rglob("*.yaml"):
        # Skip non-rule files and templates
        if rule_file.name in ["constitution.yaml", "rule-index.yaml"]:
            continue
        if "Templates" in rule_file.parts:
            continue
        
        valid, message = validate_rule_structure(rule_file)
        if not valid:
            errors.append(f"{rule_file.relative_to(PROJECT_ROOT)}: {message}")
    
    if errors:
        print("X Rule validation failed:")
        for error in errors:
            print(f"  - {error}")
        sys.exit(1)
    
    print("All rules validated successfully")
    sys.exit(0)

if __name__ == "__main__":
    main()