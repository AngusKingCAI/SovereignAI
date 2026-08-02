# Governance/GovernanceScripts/Validation/generate_rule_index.py
# Frontmatter: id: generate_rule_index, version: 1.0.0, owner: SovereignAI, updated: 2026-08-02, purpose: Generate compact rule index from Policy Cards, agent: all, persona: governance
#!/usr/bin/env python3
"""Generate compact rule index from Policy Cards."""
import yaml
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent
POLICY_CARDS_DIR = PROJECT_ROOT / "Governance" / "Policy-cards"
RULE_INDEX = PROJECT_ROOT / "Governance" / "rule-index.yaml"

def main():
    # Load all Policy Cards
    rules = []
    for card_file in POLICY_CARDS_DIR.rglob("*.yaml"):
        card = yaml.safe_load(card_file.read_text())
        rules.append({
            "id": card.get("id"),
            "summary": card.get("rule", {}).get("statement", "")[:100],  # Truncate to 100 chars
            "severity": card.get("severity")
        })
    
    # Sort by ID
    rules.sort(key=lambda x: x["id"])
    
    # Generate compact index
    index = {
        "agent": "all",  # Or specific agent if needed
        "total_rules": len(rules),
        "rules": rules
    }
    
    # Write index
    RULE_INDEX.write_text(yaml.dump(index, default_flow_style=False))
    print(f"Rule index generated: {RULE_INDEX}")
    print(f"  Total rules: {len(rules)}")

if __name__ == "__main__":
    main()
