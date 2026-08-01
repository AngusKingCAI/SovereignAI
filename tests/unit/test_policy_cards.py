# tests/unit/test_policy_cards.py
import pytest
import yaml
import jsonschema
import hashlib
import json
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
CARDS_DIR = PROJECT_ROOT / "governance" / "policy-cards"
SCHEMA = PROJECT_ROOT / "governance" / "schemas" / "policy-card.schema.json"

def load_all_cards():
    """Fixture: load every Policy Card in the repo."""
    return [(f, yaml.safe_load(f.read_text())) for f in CARDS_DIR.rglob("*.yaml")]

def test_all_cards_match_schema():
    """Every Policy Card must validate against the JSON Schema."""
    schema = yaml.safe_load(SCHEMA.read_text())
    cards = load_all_cards()
    assert len(cards) > 0, "No Policy Cards found - harness is empty"
    for card_file, card in cards:
        try:
            jsonschema.validate(card, schema)
        except jsonschema.ValidationError as e:
            pytest.fail(f"{card_file} fails schema validation: {e.message}")

def test_every_card_has_minimum_test_cases():
    """Every card must have >=2 test cases (schema-enforced, but verify)."""
    for card_file, card in load_all_cards():
        tc = card.get("test_cases", [])
        assert len(tc) >= 2, \
            f"{card_file} has {len(tc)} test cases, minimum is 2"

def test_no_duplicate_rule_statements():
    """SSOT: no two cards may have the same rule.statement (normalized)."""
    statements = {}
    for card_file, card in load_all_cards():
        stmt = card.get("rule", {}).get("statement", "")
        normalized = " ".join(stmt.lower().split())
        h = hashlib.md5(normalized.encode()).hexdigest()
        if h in statements:
            pytest.fail(
                f"SSOT violation: '{card.get('id')}' in {card_file} duplicates "
                f"'{statements[h][1]}' in {statements[h][0]}"
            )
        statements[h] = (card_file, card.get("id"))

def test_refines_references_resolve():
    """If a card has 'refines:', the referenced card ID must exist."""
    all_ids = {card["id"] for _, card in load_all_cards() if "id" in card}
    for card_file, card in load_all_cards():
        if "refines" in card:
            assert card["refines"] in all_ids, \
                f"{card_file} refines '{card['refines']}' which does not exist"
