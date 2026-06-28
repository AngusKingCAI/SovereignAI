"""Parse component manifests from TOML files into frozen dataclasses.

Per Q1 resolution: manifests are static TOML files declaring capability
categories. The parser reads a manifest file, validates its structure,
and produces a frozen ComponentManifest instance.

Per Q2 resolution: the parser is invoked by a directory scan at startup
(not by decorators or entry points). Each component directory contains
a manifest.toml file.
"""
from __future__ import annotations

import tomllib
from pathlib import Path

from sovereignai.shared.types import (
    CapabilityCategory,
    CapabilityDeclaration,
    ComponentManifest,
)


class ManifestParseError(Exception):
    """Raised when a manifest file is missing required fields or has invalid values."""


def parse_manifest(path: Path) -> ComponentManifest:
    """Read a single TOML manifest file and return a frozen ComponentManifest.

    Args:
        path: Path to the manifest.toml file.

    Returns:
        Frozen ComponentManifest with all declared capabilities.

    Raises:
        ManifestParseError: If the file is missing, malformed, or lacks
            required fields.
    """
    if not path.exists():
        raise ManifestParseError(f"Manifest file not found: {path}")
    with path.open("rb") as f:
        data = tomllib.load(f)

    # Required top-level fields
    component_id = data.get("component_id")
    version = data.get("version")
    author = data.get("author")
    content_hash = data.get("content_hash")
    if not all([component_id, version, author, content_hash]):
        raise ManifestParseError(
            f"Manifest {path} missing required fields "
            f"(component_id, version, author, content_hash)"
        )

    # Wrap as ComponentId (NewType — requires explicit construction per Finding 4)
    from sovereignai.shared.types import ComponentId
    component_id = ComponentId(component_id)

    # Parse provides[] and requires[]
    provides = tuple(_parse_caps(data.get("provides", []), path))
    requires = tuple(_parse_caps(data.get("requires", []), path))

    return ComponentManifest(
        component_id=component_id,
        version=version,
        author=author,
        content_hash=content_hash,
        provides=provides,
        requires=requires,
    )


def _parse_caps(raw: list[dict], path: Path) -> list[CapabilityDeclaration]:
    """Convert raw TOML capability entries into frozen CapabilityDeclaration objects.

    Args:
        raw: List of dicts from the TOML file's provides[] or requires[].
        path: Manifest path, used for error messages.

    Returns:
        List of CapabilityDeclaration instances.

    Raises:
        ManifestParseError: If any entry is missing fields (category,
            name, version) or has an invalid category. Per Finding 2,
            all required fields are validated before construction.
    """
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
    """Convert a raw priority value to an integer, raising ManifestParseError on invalid input.

    Per Finding 12 (Rev3): wraps the int() conversion so a non-integer
    priority (e.g. "high") raises ManifestParseError instead of an
    unhandled ValueError.

    Args:
        raw: The raw value from the TOML file (int, str, or other).
        entry_index: Index of the capability entry, for error messages.
        path: Manifest path, for error messages.

    Returns:
        The priority as an integer.

    Raises:
        ManifestParseError: If the value cannot be converted to int.
    """
    try:
        return int(raw)
    except (TypeError, ValueError) as exc:
        raise ManifestParseError(
            f"Manifest {path} entry {entry_index} has invalid priority "
            f"{raw!r}: must be an integer"
        ) from exc
