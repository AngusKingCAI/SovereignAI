"""Test manifest version validation (core vs plugin)."""

from pathlib import Path

import pytest

from sovereignai.shared.manifest_parser import ManifestParseError, parse_manifest


def test_core_component_with_version_passes() -> None:
    """Parse a core component with explicit version (passes)."""
    # Create a temporary manifest file inside sovereignai package
    import sovereignai
    sovereignai_path = Path(sovereignai.__file__).resolve().parent
    manifest_path = sovereignai_path / "test_core_with_version.toml"

    manifest_content = """
component_id = "test_core"
version = "1.0.0"
author = "test"
content_hash = "abc123"
core = true

[[provides]]
category = "model_inference"
name = "text_generation"
version = "1.0.0"
priority = 0
"""
    manifest_path.write_text(manifest_content)

    # This should pass (inside sovereignai package)
    manifest = parse_manifest(manifest_path)

    assert manifest.component_id == "test_core"
    assert manifest.version == "1.0.0"
    assert manifest.core is True

    # Cleanup
    if manifest_path.exists():
        manifest_path.unlink()


def test_core_component_without_version_fails() -> None:
    """Parse a core component without version field (fails)."""
    # Create a temporary manifest file inside sovereignai package
    import sovereignai
    sovereignai_path = Path(sovereignai.__file__).resolve().parent
    manifest_path = sovereignai_path / "test_core_no_version.toml"

    manifest_content = """
component_id = "test_core"
author = "test"
content_hash = "abc123"
core = true

[[provides]]
category = "model_inference"
name = "text_generation"
version = "1.0.0"
priority = 0
"""
    manifest_path.write_text(manifest_content)

    # This should fail (core component missing version)
    with pytest.raises(ManifestParseError, match="missing required 'version' field"):
        parse_manifest(manifest_path)

    # Cleanup
    if manifest_path.exists():
        manifest_path.unlink()


def test_plugin_without_version_defaults() -> None:
    """Parse a plugin without version field (defaults to 0.0.0)."""
    # Create a temporary manifest file outside sovereignai package
    manifest_path = Path(__file__).parent / "fixtures" / "manifests" / "test_plugin_no_version.toml"
    manifest_path.parent.mkdir(parents=True, exist_ok=True)

    manifest_content = """
component_id = "test_plugin"
author = "test"
content_hash = "abc123"

[[provides]]
category = "tool"
name = "websearch"
version = "1.0.0"
priority = 0
"""
    manifest_path.write_text(manifest_content)

    # This should pass (plugin defaults to 0.0.0)
    manifest = parse_manifest(manifest_path)

    assert manifest.component_id == "test_plugin"
    assert manifest.version == "0.0.0"
    assert manifest.core is False

    # Cleanup
    manifest_path.unlink()


def test_plugin_with_version_passes() -> None:
    """Parse a plugin with explicit version (passes)."""
    fixtures_dir = Path(__file__).parent / "fixtures" / "manifests"
    manifest_path = fixtures_dir / "test_plugin_with_version.toml"
    manifest_path.parent.mkdir(parents=True, exist_ok=True)

    manifest_content = """
component_id = "test_plugin"
version = "2.0.0"
author = "test"
content_hash = "abc123"

[[provides]]
category = "tool"
name = "websearch"
version = "1.0.0"
priority = 0
"""
    manifest_path.write_text(manifest_content)

    manifest = parse_manifest(manifest_path)

    assert manifest.component_id == "test_plugin"
    assert manifest.version == "2.0.0"
    assert manifest.core is False

    # Cleanup
    manifest_path.unlink()


def test_plugin_outside_sovereignai_with_core_true() -> None:
    """Parse a plugin outside sovereignai with core=true (treated as plugin)."""
    manifest_path = Path(__file__).parent / "fixtures" / "manifests" / "test_external_core.toml"
    manifest_path.parent.mkdir(parents=True, exist_ok=True)

    manifest_content = """
component_id = "external_plugin"
version = "1.0.0"
author = "test"
content_hash = "abc123"
core = true

[[provides]]
category = "tool"
name = "websearch"
version = "1.0.0"
priority = 0
"""
    manifest_path.write_text(manifest_content)

    # Should be treated as plugin (core=true ignored outside sovereignai)
    manifest = parse_manifest(manifest_path)

    assert manifest.component_id == "external_plugin"
    assert manifest.core is False  # Ignored because outside sovereignai

    # Cleanup
    manifest_path.unlink()


def test_invalid_version_format_raises() -> None:
    """Parse manifest with invalid version format (raises)."""
    manifest_path = Path(__file__).parent / "fixtures" / "manifests" / "test_invalid_version.toml"
    manifest_path.parent.mkdir(parents=True, exist_ok=True)

    manifest_content = """
component_id = "test_plugin"
version = "not.a.version"
author = "test"
content_hash = "abc123"

[[provides]]
category = "tool"
name = "websearch"
version = "1.0.0"
priority = 0
"""
    manifest_path.write_text(manifest_content)

    # Version parsing happens later in negotiator, so this should pass parser
    # (parser just stores the string)
    manifest = parse_manifest(manifest_path)

    assert manifest.version == "not.a.version"

    # Cleanup
    manifest_path.unlink()
