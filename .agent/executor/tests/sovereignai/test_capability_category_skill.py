from __future__ import annotations

import json

from sovereignai.shared.types import CapabilityCategory


def test_capability_category_skill_exists() -> None:
    assert hasattr(CapabilityCategory, "SKILL")
    assert CapabilityCategory.SKILL.value == "skill"


def test_capability_category_json_serializable() -> None:
    result = json.dumps(CapabilityCategory.SKILL)
    assert result == '"skill"'

    # Deserialize and verify
    deserialized = CapabilityCategory(json.loads(result))
    assert deserialized == CapabilityCategory.SKILL
