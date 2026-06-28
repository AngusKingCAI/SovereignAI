"""Tests for manifest parser."""
from __future__ import annotations

from pathlib import Path

import pytest

from sovereignai.shared.manifest_parser import ManifestParseError, parse_manifest
from sovereignai.shared.types import CapabilityCategory


def test_parse_valid_manifest(tmp_path: Path) -> None:
    """Parse a well-formed TOML manifest and return correct ComponentManifest."""
    manifest_file = tmp_path / "test.toml"
    manifest_file.write_text(
        """component_id = "TestAdapter"
version = "1.0.0"
author = "test-author"
content_hash = "sha256:abc123"

[[provides]]
category = "model_inference"
name = "text_generation"
version = "1.0.0"
priority = 10
"""
    )
    manifest = parse_manifest(manifest_file)
    assert manifest.component_id == "TestAdapter"
    assert manifest.version == "1.0.0"
    assert manifest.author == "test-author"
    assert manifest.content_hash == "sha256:abc123"
    assert len(manifest.provides) == 1
    assert manifest.provides[0].category == CapabilityCategory.MODEL_INFERENCE
    assert manifest.provides[0].name == "text_generation"
    assert manifest.provides[0].version == "1.0.0"
    assert manifest.provides[0].priority == 10
    assert len(manifest.requires) == 0


def test_parse_missing_file_raises(tmp_path: Path) -> None:
    """Raise ManifestParseError when manifest file does not exist."""
    with pytest.raises(ManifestParseError) as exc_info:
        parse_manifest(tmp_path / "nonexistent.toml")
    assert "Manifest file not found" in str(exc_info.value)


def test_parse_missing_required_field_raises(tmp_path: Path) -> None:
    """Raise ManifestParseError when required top-level field is missing."""
    manifest_file = tmp_path / "test.toml"
    manifest_file.write_text(
        """component_id = "TestAdapter"
version = "1.0.0"
# Missing author and content_hash
"""
    )
    with pytest.raises(ManifestParseError) as exc_info:
        parse_manifest(manifest_file)
    assert "missing required fields" in str(exc_info.value)


def test_parse_invalid_category_raises(tmp_path: Path) -> None:
    """Raise ManifestParseError when capability category is invalid."""
    manifest_file = tmp_path / "test.toml"
    manifest_file.write_text(
        """component_id = "TestAdapter"
version = "1.0.0"
author = "test-author"
content_hash = "sha256:abc123"

[[provides]]
category = "invalid_category"
name = "text_generation"
version = "1.0.0"
"""
    )
    with pytest.raises(ManifestParseError) as exc_info:
        parse_manifest(manifest_file)
    assert "invalid category" in str(exc_info.value)


def test_parse_provides_with_priority(tmp_path: Path) -> None:
    """Parse manifest with priority field; default to 0 when omitted."""
    manifest_file = tmp_path / "test.toml"
    manifest_file.write_text(
        """component_id = "TestAdapter"
version = "1.0.0"
author = "test-author"
content_hash = "sha256:abc123"

[[provides]]
category = "model_inference"
name = "text_generation"
version = "1.0.0"
priority = 5

[[provides]]
category = "tool"
name = "calculator"
version = "1.0.0"
# priority omitted, should default to 0
"""
    )
    manifest = parse_manifest(manifest_file)
    assert len(manifest.provides) == 2
    assert manifest.provides[0].priority == 5
    assert manifest.provides[1].priority == 0


def test_parse_requires_empty_when_omitted(tmp_path: Path) -> None:
    """Parse manifest without requires[] key; requires should be empty tuple."""
    manifest_file = tmp_path / "test.toml"
    manifest_file.write_text(
        """component_id = "TestAdapter"
version = "1.0.0"
author = "test-author"
content_hash = "sha256:abc123"

[[provides]]
category = "model_inference"
name = "text_generation"
version = "1.0.0"
"""
    )
    manifest = parse_manifest(manifest_file)
    assert manifest.requires == ()


def test_parse_missing_capability_field_raises(tmp_path: Path) -> None:
    """Raise ManifestParseError when capability entry is missing required field."""
    manifest_file = tmp_path / "test.toml"
    manifest_file.write_text(
        """component_id = "TestAdapter"
version = "1.0.0"
author = "test-author"
content_hash = "sha256:abc123"

[[provides]]
category = "model_inference"
name = "text_generation"
# missing version
"""
    )
    with pytest.raises(ManifestParseError) as exc_info:
        parse_manifest(manifest_file)
    assert "missing required field" in str(exc_info.value)


def test_parse_invalid_priority_raises(tmp_path: Path) -> None:
    """Raise ManifestParseError when priority is not an integer (Finding 12)."""
    manifest_file = tmp_path / "test.toml"
    manifest_file.write_text(
        """component_id = "TestAdapter"
version = "1.0.0"
author = "test-author"
content_hash = "sha256:abc123"

[[provides]]
category = "model_inference"
name = "text_generation"
version = "1.0.0"
priority = "high"
"""
    )
    with pytest.raises(ManifestParseError) as exc_info:
        parse_manifest(manifest_file)
    assert "invalid priority" in str(exc_info.value)
