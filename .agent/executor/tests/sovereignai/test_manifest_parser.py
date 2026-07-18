from __future__ import annotations

from pathlib import Path

import pytest
from sovereignai.shared.manifest_parser import ManifestParseError, parse_manifest
from sovereignai.shared.types import CapabilityCategory


def test_parse_valid_manifest(tmp_path: Path) -> None:
    manifest_file = tmp_path / 'test.toml'
    manifest_content = (  # noqa: E501
        'component_id = "TestAdapter"\nversion = "1.0.0"\n'
        'author = "test-author"\ncontent_hash = "sha256:abc123"\n\n'
        '[[provides]]\ncategory = "model_inference"\n'
        'name = "text_generation"\nversion = "1.0.0"\npriority = 10\n'
    )
    manifest_file.write_text(manifest_content)
    manifest = parse_manifest(manifest_file)
    assert manifest.component_id == 'TestAdapter'
    assert manifest.version == '1.0.0'
    assert manifest.author == 'test-author'
    assert manifest.content_hash == 'sha256:abc123'
    assert len(manifest.provides) == 1
    assert manifest.provides[0].category == CapabilityCategory.MODEL_INFERENCE
    assert manifest.provides[0].name == 'text_generation'
    assert manifest.provides[0].version == '1.0.0'
    assert manifest.provides[0].priority == 10
    assert len(manifest.requires) == 0

def test_parse_missing_file_raises(tmp_path: Path) -> None:
    with pytest.raises(ManifestParseError) as exc_info:
        parse_manifest(tmp_path / 'nonexistent.toml')
    assert 'Manifest file not found' in str(exc_info.value)

def test_parse_missing_required_field_raises(tmp_path: Path) -> None:  # noqa: E501
    manifest_file = tmp_path / 'test.toml'
    manifest_content = (  # noqa: E501
        'component_id = "TestAdapter"\nversion = "1.0.0"\n'
        '# Missing author and content_hash\n'
    )
    manifest_file.write_text(manifest_content)
    with pytest.raises(ManifestParseError) as exc_info:
        parse_manifest(manifest_file)
    assert 'missing required fields' in str(exc_info.value)

def test_parse_invalid_category_raises(tmp_path: Path) -> None:
    manifest_file = tmp_path / 'test.toml'
    manifest_content = (  # noqa: E501
        'component_id = "TestAdapter"\nversion = "1.0.0"\n'
        'author = "test-author"\ncontent_hash = "sha256:abc123"\n\n'
        '[[provides]]\ncategory = "invalid_category"\n'
        'name = "text_generation"\nversion = "1.0.0"\n'
    )
    manifest_file.write_text(manifest_content)
    with pytest.raises(ManifestParseError) as exc_info:
        parse_manifest(manifest_file)
    assert 'invalid category' in str(exc_info.value)

def test_parse_provides_with_priority(tmp_path: Path) -> None:
    manifest_file = tmp_path / 'test.toml'
    manifest_content = (  # noqa: E501
        'component_id = "TestAdapter"\nversion = "1.0.0"\n'
        'author = "test-author"\ncontent_hash = "sha256:abc123"\n\n'
        '[[provides]]\ncategory = "model_inference"\n'
        'name = "text_generation"\nversion = "1.0.0"\npriority = 5\n\n'
        '[[provides]]\ncategory = "tool"\nname = "calculator"\n'
        'version = "1.0.0"\n# priority omitted, should default to 0\n'
    )
    manifest_file.write_text(manifest_content)
    manifest = parse_manifest(manifest_file)
    assert len(manifest.provides) == 2
    assert manifest.provides[0].priority == 5
    assert manifest.provides[1].priority == 0

def test_parse_requires_empty_when_omitted(tmp_path: Path) -> None:
    manifest_file = tmp_path / 'test.toml'
    manifest_content = (  # noqa: E501
        'component_id = "TestAdapter"\nversion = "1.0.0"\n'
        'author = "test-author"\ncontent_hash = "sha256:abc123"\n\n'
        '[[provides]]\ncategory = "model_inference"\n'
        'name = "text_generation"\nversion = "1.0.0"\n'
    )
    manifest_file.write_text(manifest_content)
    manifest = parse_manifest(manifest_file)
    assert manifest.requires == ()

def test_parse_missing_capability_field_raises(tmp_path: Path) -> None:
    manifest_file = tmp_path / 'test.toml'
    manifest_content = (  # noqa: E501
        'component_id = "TestAdapter"\nversion = "1.0.0"\n'
        'author = "test-author"\ncontent_hash = "sha256:abc123"\n\n'
        '[[provides]]\ncategory = "model_inference"\n'
        'name = "text_generation"\n# missing version\n'
    )
    manifest_file.write_text(manifest_content)
    with pytest.raises(ManifestParseError) as exc_info:
        parse_manifest(manifest_file)
    assert 'missing required field' in str(exc_info.value)

def test_parse_invalid_priority_raises(tmp_path: Path) -> None:
    manifest_file = tmp_path / 'test.toml'
    manifest_content = (  # noqa: E501
        'component_id = "TestAdapter"\nversion = "1.0.0"\n'
        'author = "test-author"\ncontent_hash = "sha256:abc123"\n\n'
        '[[provides]]\ncategory = "model_inference"\n'
        'name = "text_generation"\nversion = "1.0.0"\npriority = "high"\n'
    )
    manifest_file.write_text(manifest_content)
    with pytest.raises(ManifestParseError) as exc_info:
        parse_manifest(manifest_file)
    assert 'invalid priority' in str(exc_info.value)
