# scripts/validation/lint_ssot_duplicates.py
#!/usr/bin/env python3
"""SSOT dedup linter — flags duplicate rule statements across Policy Cards."""
import hashlib
import sys
import yaml
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
# Use current working directory for POLICY_CARDS_DIR to support testing
POLICY_CARDS_DIR = Path.cwd() / "governance" / "policy-cards"

def main():
    statements = {}  # hash -> [(file, rule_id)]
    
    for card_file in POLICY_CARDS_DIR.rglob("*.yaml"):
        card = yaml.safe_load(card_file.read_text())
        statement = card.get("rule", {}).get("statement", "")
        if not statement:
            continue
        # Normalize: lowercase, strip whitespace
        normalized = " ".join(statement.lower().split())
        h = hashlib.md5(normalized.encode()).hexdigest()
        statements.setdefault(h, []).append((card_file, card.get("id", "?")))
    
    duplicates = {h: locs for h, locs in statements.items() if len(locs) > 1}
    
    if duplicates:
        print("X SSOT violations found - rule statements duplicated across cards:")
        for h, locs in duplicates.items():
            print(f"\n  Duplicate statement (hash {h[:8]}):")
            for filepath, rule_id in locs:
                print(f"    - {rule_id} in {filepath}")
        print("\nUse 'refines:' to reference a shared rule instead of duplicating it.")
        sys.exit(1)
    
    print("No SSOT violations - all rule statements are unique")
    sys.exit(0)

if __name__ == "__main__":
    main()
