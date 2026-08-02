# Scripts/Rules/Validation/validate_policy_cards.py
# Frontmatter: id: validate_policy_cards, version: 1.0.0, owner: SovereignAI, updated: 2026-08-02, purpose: Validate Policy Cards against their JSON Schema, agent: all, persona: governance
#!/usr/bin/env python3
"""Validate Policy Cards against their JSON Schema."""
import sys
import yaml
import jsonschema
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent
POLICY_CARDS_DIR = Path.cwd() / "Rules"
SCHEMA = Path.cwd() / "Rules" / "Schemas" / "policy-card.schema.json"

def main():
    schema = yaml.safe_load(SCHEMA.read_text())
    errors = []
    
    for card_file in POLICY_CARDS_DIR.rglob("*.yaml"):
        try:
            card = yaml.safe_load(card_file.read_text())
            jsonschema.validate(card, schema)
        except jsonschema.ValidationError as e:
            errors.append(f"{card_file}: {e.message}")
        except Exception as e:
            errors.append(f"{card_file}: {e}")
    
    if errors:
        print("X Policy Card validation failed:")
        for error in errors:
            print(f"  - {error}")
        sys.exit(1)
    
    print("All Policy Cards validate against schema")
    sys.exit(0)

if __name__ == "__main__":
    main()
