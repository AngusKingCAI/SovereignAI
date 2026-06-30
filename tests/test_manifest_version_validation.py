from pathlib import Path

import pytest

from sovereignai.shared.manifest_parser import ManifestParseError, parse_manifest


def test_core_component_with_version_passes() -> None:
    import sovereignai
    sovereignai_path = Path(sovereignai.__file__).resolve().parent
    manifest_path = sovereignai_path / 'test_core_with_version.toml'
    manifest_content = '\ncomponent_id = "test_core"\nversion = "1.0.0"\nauthor = "test"\ncontent_hash = "abc123"\ncore = true\n\n[[provides]]\ncategory = "model_inference"\nname = "text_generation"\nversion = "1.0.0"\npriority = 0\n'
    manifest_path.write_text(manifest_content)
    manifest = parse_manifest(manifest_path)
    assert manifest.component_id == 'test_core'
    assert manifest.version == '1.0.0'
    assert manifest.core is True
    if manifest_path.exists():
        manifest_path.unlink()

def test_core_component_without_version_fails() -> None:
    import sovereignai
    sovereignai_path = Path(sovereignai.__file__).resolve().parent
    manifest_path = sovereignai_path / 'test_core_no_version.toml'
    manifest_content = '\ncomponent_id = "test_core"\nauthor = "test"\ncontent_hash = "abc123"\ncore = true\n\n[[provides]]\ncategory = "model_inference"\nname = "text_generation"\nversion = "1.0.0"\npriority = 0\n'
    manifest_path.write_text(manifest_content)
    with pytest.raises(ManifestParseError, match="missing required 'version' field"):
        parse_manifest(manifest_path)
    if manifest_path.exists():
        manifest_path.unlink()

def test_plugin_without_version_defaults() -> None:
    manifest_path = Path(__file__).parent / 'fixtures' / 'manifests' / 'test_plugin_no_version.toml'
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_content = '\ncomponent_id = "test_plugin"\nauthor = "test"\ncontent_hash = "abc123"\n\n[[provides]]\ncategory = "tool"\nname = "websearch"\nversion = "1.0.0"\npriority = 0\n'
    manifest_path.write_text(manifest_content)
    manifest = parse_manifest(manifest_path)
    assert manifest.component_id == 'test_plugin'
    assert manifest.version == '0.0.0'
    assert manifest.core is False
    manifest_path.unlink()

def test_plugin_with_version_passes() -> None:
    fixtures_dir = Path(__file__).parent / 'fixtures' / 'manifests'
    manifest_path = fixtures_dir / 'test_plugin_with_version.toml'
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_content = '\ncomponent_id = "test_plugin"\nversion = "2.0.0"\nauthor = "test"\ncontent_hash = "abc123"\n\n[[provides]]\ncategory = "tool"\nname = "websearch"\nversion = "1.0.0"\npriority = 0\n'
    manifest_path.write_text(manifest_content)
    manifest = parse_manifest(manifest_path)
    assert manifest.component_id == 'test_plugin'
    assert manifest.version == '2.0.0'
    assert manifest.core is False
    manifest_path.unlink()

def test_plugin_outside_sovereignai_with_core_true() -> None:
    manifest_path = Path(__file__).parent / 'fixtures' / 'manifests' / 'test_external_core.toml'
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_content = '\ncomponent_id = "external_plugin"\nversion = "1.0.0"\nauthor = "test"\ncontent_hash = "abc123"\ncore = true\n\n[[provides]]\ncategory = "tool"\nname = "websearch"\nversion = "1.0.0"\npriority = 0\n'
    manifest_path.write_text(manifest_content)
    manifest = parse_manifest(manifest_path)
    assert manifest.component_id == 'external_plugin'
    assert manifest.core is False
    manifest_path.unlink()

def test_invalid_version_format_raises() -> None:
    manifest_path = Path(__file__).parent / 'fixtures' / 'manifests' / 'test_invalid_version.toml'
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_content = '\ncomponent_id = "test_plugin"\nversion = "not.a.version"\nauthor = "test"\ncontent_hash = "abc123"\n\n[[provides]]\ncategory = "tool"\nname = "websearch"\nversion = "1.0.0"\npriority = 0\n'
    manifest_path.write_text(manifest_content)
    manifest = parse_manifest(manifest_path)
    assert manifest.version == 'not.a.version'
    manifest_path.unlink()
