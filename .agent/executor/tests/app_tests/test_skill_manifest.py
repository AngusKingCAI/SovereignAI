from __future__ import annotations

import sys
from pathlib import Path

import pytest
from sovereignai.shared.types import CapabilityCategory
from sovereignai.skills.manifest import SkillManifest


def test_manifest_parsing() -> None:
    test_root = Path(__file__).parent.parent.parent.parent.parent
    manifest_path = test_root / "app/sovereignai/skills/official/file_read/manifest.toml"
    if not manifest_path.exists():
        pytest.skip(f"Manifest file not found: {manifest_path}")

    manifest = SkillManifest.from_toml(manifest_path)

    assert manifest.id == "file_read"
    assert manifest.name == "File Read"
    assert manifest.version == "1.0.0"
    assert len(manifest.capabilities) == 1
    assert manifest.capabilities[0].category == CapabilityCategory.SKILL


def test_no_import_guarantee() -> None:
    modules_before = set(sys.modules.keys())

    test_root = Path(__file__).parent.parent.parent.parent.parent
    manifest_path = test_root / "app/sovereignai/skills/official/file_read/manifest.toml"
    if not manifest_path.exists():
        pytest.skip(f"Manifest file not found: {manifest_path}")

    from sovereignai.skills.manifest import SkillManifest
    SkillManifest.from_toml(manifest_path)

    modules_after = set(sys.modules.keys())
    new_modules = modules_after - modules_before

    # defusedxml may be loaded, but skill modules should not be
    allowlist = set(sys.stdlib_module_names) if hasattr(sys, "stdlib_module_names") else set()
    allowlist.add("defusedxml")

    unexpected_modules = new_modules - allowlist
    assert not unexpected_modules, f"Unexpected modules loaded: {unexpected_modules}"


def test_dag_parse_simple() -> None:
    test_root = Path(__file__).parent.parent.parent.parent.parent
    manifest_path = test_root / "app/sovereignai/skills/official/file_read/manifest.toml"
    if not manifest_path.exists():
        pytest.skip(f"Manifest file not found: {manifest_path}")

    manifest = SkillManifest.from_toml(manifest_path)
    assert manifest.dag_dependencies == []


def test_dag_parse_missing_optional() -> None:
    # Test that optional DAG dependencies are handled gracefully
    test_root = Path(__file__).parent.parent.parent.parent.parent
    manifest_path = test_root / "app/sovereignai/skills/official/file_read/manifest.toml"
    if not manifest_path.exists():
        pytest.skip(f"Manifest file not found: {manifest_path}")

    manifest = SkillManifest.from_toml(manifest_path)
    # dag_dependencies is optional and defaults to empty list
    assert isinstance(manifest.dag_dependencies, list)


def test_to_component_manifest_mapping() -> None:
    test_root = Path(__file__).parent.parent.parent.parent.parent
    manifest_path = test_root / "app/sovereignai/skills/official/file_read/manifest.toml"
    if not manifest_path.exists():
        pytest.skip(f"Manifest file not found: {manifest_path}")

    skill_manifest = SkillManifest.from_toml(manifest_path)
    component_manifest = skill_manifest.to_component_manifest()

    assert str(component_manifest.component_id) == "file_read"
    assert component_manifest.version == "1.0.0"
    # Category is stored in provides field
    assert len(component_manifest.provides) == 1
    assert component_manifest.provides[0].category == CapabilityCategory.SKILL

    # Check metadata mapping
    assert "dependencies" in component_manifest.metadata
    assert "memory_hints" in component_manifest.metadata
    assert component_manifest.metadata["dependencies"] == skill_manifest.dependencies
    assert component_manifest.metadata["memory_hints"] == skill_manifest.memory_integration_hints
