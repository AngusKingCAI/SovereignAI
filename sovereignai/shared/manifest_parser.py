from __future__ import annotations

import tomllib
from pathlib import Path

from sovereignai.shared.types import (
    CapabilityCategory,
    CapabilityDeclaration,
    ComponentManifest,
)


class ManifestParseError(Exception):
    pass


def parse_manifest(path: Path) -> ComponentManifest:
    if not path.exists():
        raise ManifestParseError(f"Manifest file not found: {path}")
    with path.open("rb") as f:
        data = tomllib.load(f)

    # Support both flat format (component_id at root) and [component] table format.
    # The [component] table is idiomatic TOML and used by all real manifest files;
    # flat format is used by tests for simplicity. Unwrap if needed.
    if "component" in data and isinstance(data["component"], dict):
        data = {**data["component"], **{k: v for k, v in data.items() if k != "component"}}

    # Required top-level fields (now flat after unwrap)
    component_id = data.get("component_id")
    version_str = data.get("version")
    author = data.get("author")
    content_hash = data.get("content_hash")
    if not all([component_id, author, content_hash]):
        raise ManifestParseError(
            f"Manifest {path} missing required fields "
            f"(component_id, author, content_hash)"
        )

    # Wrap as ComponentId (NewType — requires explicit construction per Finding 4)
    from sovereignai.shared.types import ComponentId
    # Type narrowing: mypy knows these are str after the all() check above
    assert isinstance(component_id, str)
    assert isinstance(author, str)
    assert isinstance(content_hash, str)
    component_id = ComponentId(component_id)

    # Validate version field (per Rev3 N21 + Rev6 F13)
    # F13: core=true is only respected for components inside the sovereignai package directory.
    # Third-party plugins setting core=true are still classified as plugins.
    import sovereignai
    sovereignai_pkg_dir = Path(sovereignai.__file__).resolve().parent
    manifest_dir = path.resolve().parent
    is_inside_sovereignai = manifest_dir.is_relative_to(sovereignai_pkg_dir)
    is_core = data.get("core", False) and is_inside_sovereignai

    # Rev8: set _source_path on the manifest so conformance gate can check first-party status
    # (Plan 13 S11 uses getattr(manifest, '_source_path', '') for first-party detection)
    # We'll set this as an attribute on the manifest after construction


    if version_str is None:
        if is_core:
            # Core components MUST have an explicit version
            raise ManifestParseError(
                f"Core component {component_id} is missing required 'version' field"
            )
        else:
            # Plugins default to 0.0.0
            version = "0.0.0"
        # Note: we don't emit a trace here because TraceEmitter may not be available
        # during manifest parsing (this happens before DI container is built)
    else:
        assert isinstance(version_str, str)
        version = version_str

    # Parse provides[] and requires[]
    provides = tuple(_parse_caps(data.get("provides", []), path))
    requires = tuple(_parse_caps(data.get("requires", []), path))

    manifest = ComponentManifest(
        component_id=component_id,
        version=version,
        author=author,
        content_hash=content_hash,
        provides=provides,
        requires=requires,
        core=is_core,
        _source_path=str(path),
    )

    return manifest


def _parse_caps(raw: list[dict], path: Path) -> list[CapabilityDeclaration]:
    result: list[CapabilityDeclaration] = []
    for i, entry in enumerate(raw):
        # Validate required fields per Finding 2
        for required_field in ("category", "name", "version"):
            if required_field not in entry or not entry[required_field]:
                raise ManifestParseError(
                    f"Manifest {path} entry {i} missing required field "
                    f"{required_field!r}"
                )
        try:
            category = CapabilityCategory(entry["category"])
        except ValueError as exc:
            raise ManifestParseError(
                f"Manifest {path} entry {i} has invalid category "
                f"{entry['category']!r}: {exc}"
            ) from exc
        result.append(CapabilityDeclaration(
            category=category,
            name=str(entry["name"]),
            version=str(entry["version"]),
            priority=_parse_priority(entry.get("priority", 0), i, path),
        ))
    return result


def _parse_priority(raw: object, entry_index: int, path: Path) -> int:
    try:
        # Type narrowing: cast to int-compatible types for mypy
        if not isinstance(raw, (int, str, bool)):
            raise TypeError(f"Priority must be int or str, got {type(raw).__name__}")
        return int(raw)  # type: ignore[arg-type]
    except (TypeError, ValueError) as exc:
        raise ManifestParseError(
            f"Manifest {path} entry {entry_index} has invalid priority "
            f"{raw!r}: must be an integer"
        ) from exc
