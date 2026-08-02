# Governance/Tests/unit/test_constitution.py
import pytest
import yaml
import jsonschema
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
CONSTITUTION = PROJECT_ROOT / "Governance" / "constitution.yaml"
SCHEMA = PROJECT_ROOT / "Governance" / "Schemas" / "constitution.schema.json"

@pytest.fixture
def constitution():
    return yaml.safe_load(CONSTITUTION.read_text())

@pytest.fixture
def schema():
    return yaml.safe_load(SCHEMA.read_text())

def test_constitution_matches_schema(constitution, schema):
    """The constitution must validate against its JSON Schema."""
    jsonschema.validate(constitution, schema)

def test_tier_hierarchy_is_complete(constitution):
    """All 4 constitutional tiers must be present and in precedence order."""
    tiers = [t["name"] for t in constitution["hierarchy"]]
    assert tiers == ["safety", "ethics", "compliance", "helpfulness"], \
        f"Tier hierarchy is {tiers}, expected the 4-tier precedence order"

def test_overrides_reference_valid_tiers(constitution):
    """Every tier's overrides list must reference tiers that exist."""
    valid_tiers = {t["name"] for t in constitution["hierarchy"]}
    for tier in constitution["hierarchy"]:
        for overridden in tier.get("overrides", []):
            assert overridden in valid_tiers, \
                f"Tier '{tier['name']}' overrides '{overridden}' which does not exist"

def test_principle_ids_are_unique(constitution):
    """Every principle ID must be unique and match the ID pattern."""
    import re
    ids = [p["id"] for p in constitution["principles"]]
    assert len(ids) == len(set(ids)), "Duplicate principle IDs found"
    for pid in ids:
        assert re.match(r"^[A-Z]+-[0-9]{3}$", pid), \
            f"Principle ID '{pid}' does not match pattern ^[A-Z]+-[0-9]{3}$"

def test_every_principle_has_enforceable_via(constitution):
    """Every principle must declare how it is enforced."""
    valid = {"hook", "validator", "both", "prompt"}
    for p in constitution["principles"]:
        assert p.get("enforceable_via") in valid, \
            f"Principle {p['id']} has invalid enforceable_via: {p.get('enforceable_via')}"
