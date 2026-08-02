Depends on: prompt-11
Vision principles: P2 (pluggable), P8 (contracts), P14 (provenance)
Open questions resolved: Q8 (versioning — full negotiation, not just MVP)

---

## S0 — Opening

S0.1 — Run `/open`. Verify prompt-11 tag exists on origin. Confirm working copy is clean and on `main`.

S0.2 — Read `AGENTS.md` in full.

S0.3 — Add new rules:
- **OR57**: Core components (EventBus, CapabilityGraph, TaskStateMachine, etc.) use strict versioning — incompatible versions prevent startup. Plugins (skills, adapters) use lenient versioning — incompatible versions are disabled with a warning. Source: Plan 12.
- **OR58**: "Latest wins" applies ONLY to cosmetic attributes (description, author, icon). Contract attributes (input_schema, output_schema, capability names) are never auto-upgraded. Source: Plan 12.
- **OR59**: The compatibility matrix is stored in `~/.sovereignai/compatibility.json` and updated whenever a new component is registered. It records which versions of which components have been tested together. Source: Plan 12.

Commit: `docs: add OR57-OR59 for prompt-12`

---

## Plan Body

### S1 — Create sovereignai/versioning/semver.py

Semantic version parser and comparator.

**Dataclass**:
```python
@dataclass(frozen=True)
class SemVer:
    major: int
    minor: int
    patch: int
    prerelease: str = ""
    build: str = ""
```

**Methods**:
- `parse(version_str: str) -> SemVer`: Parse "1.2.3", "1.2.3-alpha", "1.2.3+build".
- `is_compatible_with(other: SemVer) -> bool`: Strict semver compatibility — same major, minor >= other.minor.
- `__lt__`, `__le__`, `__gt__`, `__ge__`, `__eq__`: Total ordering.
- `bump_major()`, `bump_minor()`, `bump_patch()`: Return new SemVer (immutable).

### S2 — Create sovereignai/versioning/negotiator.py

Capability negotiator — runs at startup after all components are registered.

**Constructor**:
```python
def __init__(
    self,
    capability_graph: CapabilityGraph,
    trace: TraceEmitter,
) -> None:
```

**Methods**:
- `negotiate() -> NegotiationResult`: Iterate all registered components, check version compatibility.
- `_check_core_compatibility() -> list[Incompatibility]`: Strict check — any incompatible core component → fatal.
- `_check_plugin_compatibility() -> list[Incompatibility]`: Lenient check — incompatible plugins → warning + disable.
- `_build_dependency_graph() -> dict`: Map component_id → {version, dependencies, capabilities}.

**NegotiationResult**:
```python
@dataclass
class NegotiationResult:
    can_start: bool
    fatal_incompatibilities: list[Incompatibility]
    disabled_plugins: list[ComponentId]
    warnings: list[str]
```

### S3 — Create sovereignai/versioning/compatibility_matrix.py

Compatibility matrix — records tested version combinations.

**Storage**: `~/.sovereignai/compatibility.json`

**Schema**:
```json
{
  "entries": [
    {
      "component_a": "capability_api",
      "version_a": "1.2.0",
      "component_b": "websearch_skill",
      "version_b": "0.5.0",
      "tested_at": "2026-06-29T12:00:00Z",
      "status": "compatible"
    }
  ]
}
```

**Methods**:
- `record(component_a, version_a, component_b, version_b, status)`: Add entry.
- `is_tested(component_a, version_a, component_b, version_b) -> bool`: Check if combination was tested.
- `get_status(component_a, version_a, component_b, version_b) -> str`: Return "compatible", "incompatible", "unknown".

### S4 — Update ManifestParser to validate version strings

Add to `ManifestParser.parse()`:
```python
# Validate version field
SemVer.parse(manifest.version)  # Raises ValueError if invalid
```

### S5 — Update main.py to run negotiation on startup

After all components are registered:
```python
# 15. Version negotiator
from sovereignai.versioning.negotiator import VersionNegotiator
negotiator = VersionNegotiator(capability_graph=container.retrieve(CapabilityGraph), trace=trace)
result = negotiator.negotiate()
if not result.can_start:
    trace.emit(TraceLevel.CRITICAL, "versioning", f"Fatal incompatibilities: {result.fatal_incompatibilities}")
    raise SystemExit(1)
for warning in result.warnings:
    trace.emit(TraceLevel.WARN, "versioning", warning)
container.register_singleton(VersionNegotiator, negotiator)
```

### S6 — Update CapabilityGraph to filter disabled plugins

If a plugin is disabled by the negotiator, it remains in the graph but is marked with `status="disabled"`. The `find_providers()` method skips disabled components unless explicitly requested.

### S7 — Tests

- `tests/test_semver.py`: Test parsing, comparison, compatibility, bumping.
- `tests/test_version_negotiator.py`: Test strict core check, lenient plugin check, dependency graph building.
- `tests/test_compatibility_matrix.py`: Test recording, querying, JSON file integrity.
- `tests/test_manifest_version_validation.py`: Test invalid version strings rejected.

---

## STOP Conditions

- If version negotiation takes more than 1 second on startup, STOP.
- If a core component passes strict check but is actually incompatible, STOP.
- If any test fails, STOP.

---

## Files WILL Create

- `sovereignai/versioning/semver.py`
- `sovereignai/versioning/negotiator.py`
- `sovereignai/versioning/compatibility_matrix.py`
- `sovereignai/versioning/__init__.py`
- `tests/test_semver.py`
- `tests/test_version_negotiator.py`
- `tests/test_compatibility_matrix.py`
- `tests/test_manifest_version_validation.py`

## Files WILL Edit

- `sovereignai/shared/manifest_parser.py` (add version validation)
- `sovereignai/shared/capability_graph.py` (filter disabled plugins)
- `sovereignai/main.py` (add negotiation step)

## Files WILL NOT Edit

- Any other file in `sovereignai/shared/`
- `AGENTS.md` (except S0.3)

---

## Closing

Run `/close`. Tag: `prompt-12`. Update CHANGELOG, PLANS.md.
