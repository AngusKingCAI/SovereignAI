# Governance/GovernanceScripts/Validation/check_constitution_consistency.py
# Frontmatter: id: check_constitution_consistency, version: 1.0.0, owner: SovereignAI, updated: 2026-08-02, purpose: Check that every Policy Card's constitutional_basis references a valid principle, agent: all, persona: governance
#!/usr/bin/env python3
"""Check that every Policy Card's constitutional_basis references a valid principle."""
import sys
import yaml
from pathlib import Path

CONSTITUTION = Path.cwd() / "Governance" / "constitution.yaml"
POLICY_CARDS_DIR = Path.cwd() / "Governance" / "Policy-cards"

def main():
    # Load constitution to get valid principle IDs
    constitution = yaml.safe_load(CONSTITUTION.read_text())
    valid_principles = {p["id"] for p in constitution.get("principles", [])}
    
    errors = []
    
    for card_file in POLICY_CARDS_DIR.rglob("*.yaml"):
        card = yaml.safe_load(card_file.read_text())
        basis = card.get("constitutional_basis")
        
        if basis and basis not in valid_principles:
            errors.append(
                f"{card_file}: constitutional_basis '{basis}' does not exist in constitution.yaml"
            )
    
    if errors:
        print("X Constitution consistency check failed:")
        for error in errors:
            print(f"  - {error}")
        sys.exit(1)
    
    print("All Policy Cards reference valid constitutional principles")
    sys.exit(0)

if __name__ == "__main__":
    main()
