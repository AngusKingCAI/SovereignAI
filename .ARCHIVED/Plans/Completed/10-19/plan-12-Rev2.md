Depends on: prompt-10 (Scan 10) — revised from `prompt-11` per Rev2 F-42. Plan 12's compatibility matrix is a standalone JSON file; it does not use any Plan 11 memory backend. The actual code dependencies are the manifest parser (Plan 2, prompt-2) and the capability graph (Plan 2, prompt-2), both already complete. The linear chain 11→12 is kept for batch cohesion but is not a hard code dependency.

Vision principles: P2 (pluggable), P8 (contracts), P14 (provenance)
Open questions resolved: Q8 (versioning — full negotiation, not just MVP)

---

## S0 — Opening

S0.1 — Run `/open`. Verify prompt-11 tag exists on origin (if Plan 11 has executed; if Plan 11 and Plan 12 are being executed in batch order, prompt-11 must be present). Confirm working copy is clean and on `main`.

S0.2 — Read `AGENTS.md` in full.

S0.3 — Add new rules (revised from Rev1 per Round Table adjudication):
- **OR57**: Core components (EventBus, CapabilityGraph, TaskStateMachine, etc.) use strict versioning — incompatible versions prevent startup. Plugins (skills, adapters) use lenient versioning — incompatible versions are disabled with a WARN trace. A component manifest without a `version` field is treated as `"0.0.0"` and passes all checks (migration window for pre-Plan-12 manifests). Source: Plan 12 Rev2 (F-6, F-25).
- **OR58**: "Latest wins" applies ONLY to cosmetic attributes (description, author, icon). Contract attributes (input_schema, output_schema, capability names) are never auto-upgraded. "Latest" is defined as: highest SemVer. If two plugins declare the same cosmetic attribute at the same version, the first-registered plugin wins (registration order is deterministic per `build_container()`). Source: Plan 12 Rev2 (F-38).
- **OR59**: The compatibility matrix is stored in `~/.sovereignai/compatibility.json` and updated whenever a new component is registered. The file uses atomic writes (temp file + `os.replace`), includes a `schema_version` field (currently `1`), and is pruned to the last 1000 entries (LRU by `tested_at`). If the file is corrupted on startup, the system logs a WARN, renames the corrupted file to `compatibility.json.corrupted.{timestamp}`, and rebuilds the matrix from scratch with `"unknown"` statuses. Source: Plan 12 Rev2 (F-19).
- **OR67**: The VersionNegotiator raises a typed `FatalIncompatibilityError` (subclass of `Exception` with a plain-English `message` field listing the incompatible components), not `SystemExit`. The composition root catches this, emits an ERROR trace, and surfaces the message to the user via stderr (if headless) or the CapabilityAPI (if the web server started). The process exits with code 1 only after the user acknowledges or a 30-second timeout. Source: Plan 12 Rev2 (F-12).

Commit: `docs: add OR57-OR59, OR67 for prompt-12`

---

## Plan Body

### S1 — Create sovereignai/versioning/semver.py

Semantic version parser and comparator. (Unchanged from Rev1 — no findings against S1.)

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
- `parse(version_str: str) -> SemVer`: Parse "1.2.3", "1.2.3-alpha", "1.2.3+build". Raises `ValueError` on invalid input.
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
- `negotiate() -> NegotiationResult`: Iterate all registered components, check version compatibility. Returns a result object; does NOT raise or call `SystemExit` (per Rev2 OR67).
- `_check_core_compatibility() -> list[Incompatibility]`: Strict check — any incompatible core component → added to `fatal_incompatibilities`. A core component with no version field is treated as `"0.0.0"` and passes.
- `_check_plugin_compatibility() -> list[Incompatibility]`: Lenient check — incompatible plugins → added to `disabled_plugins` with a WARN trace.
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

**`FatalIncompatibilityError`** (per Rev2 OR67):
```python
class FatalIncompatibilityError(Exception):
    """Raised when core components declare incompatible versions and the system cannot start safely."""
    def __init__(self, incompatibilities: list[Incompatibility]) -> None:
        self.incompatibilities = incompatibilities
        messages = [f"  - {inc.component_a} v{inc.version_a} vs {inc.component_b} v{inc.version_b}: {inc.reason}" for inc in incompatibilities]
        super().__init__("Fatal version incompatibilities detected:\n" + "\n".join(messages))
```

### S3 — Create sovereignai/versioning/compatibility_matrix.py

Compatibility matrix — records tested version combinations.

**Storage**: `~/.sovereignai/compatibility.json`

**Schema** (per Rev2 OR59 — added `schema_version`, atomic write, pruning):
```json
{
  "schema_version": 1,
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
- `record(component_a, version_a, component_b, version_b, status)`: Add entry. Uses atomic write (temp file + `os.replace`). If `len(entries) > 1000`, prune oldest by `tested_at`.
- `is_tested(component_a, version_a, component_b, version_b) -> bool`: Check if combination was tested.
- `get_status(component_a, version_a, component_b, version_b) -> str`: Return "compatible", "incompatible", "unknown".
- `_atomic_write(path, data)`: Same pattern as procedural memory backend (Plan 11 S3).
- `_load_with_recovery(path) -> dict`: If `json.load()` raises, rename to `.corrupted.{timestamp}`, log WARN, return `{"schema_version": 1, "entries": []}`.

### S4 — Update ManifestParser to validate version strings

Add to `ManifestParser.parse()`:
```python
# Validate version field (per Rev2 F-6 — graceful migration for pre-existing manifests)
version_str = data.get("version")
if version_str is None:
    version = SemVer.parse("0.0.0")  # Migration window: treat missing as 0.0.0
    trace.emit(component="manifest_parser", level=TraceLevel.WARN,
               message=f"Manifest {component_id} has no version field; treating as 0.0.0. Add a version field to suppress this warning.")
else:
    version = SemVer.parse(version_str)  # Raises ValueError if invalid
```

**Note**: The existing `manifest_parser.py` already requires `version` and `content_hash` at line 50 (`if not all([component_id, version, author, content_hash])`). This S4 step relaxes that — if `version` is missing, default to `"0.0.0"` instead of raising. Update the existing check to: `if not all([component_id, author, content_hash]): raise ...` (drop `version` from the required list; default it).

### S5 — Update main.py to run negotiation on startup

After all components are registered (per Rev2 OR67 — typed exception, not SystemExit):
```python
# 16. Version negotiator
from sovereignai.versioning.negotiator import VersionNegotiator, FatalIncompatibilityError
negotiator = VersionNegotiator(capability_graph=container.retrieve(CapabilityGraph), trace=trace)
result = negotiator.negotiate()

if not result.can_start:
    # Emit ERROR trace (NOTE: TraceLevel has no CRITICAL — use ERROR, the highest level)
    trace.emit(
        component="versioning",
        level=TraceLevel.ERROR,
        message=f"Fatal incompatibilities: {[str(i) for i in result.fatal_incompatibilities]}",
    )
    # Raise typed exception — composition root catches and surfaces to user
    raise FatalIncompatibilityError(result.fatal_incompatibilities)

for warning in result.warnings:
    trace.emit(component="versioning", level=TraceLevel.WARN, message=warning)

# Remove disabled plugins from the graph entirely (per Rev2 F-34)
graph = container.retrieve(CapabilityGraph)
for plugin_id in result.disabled_plugins:
    graph.remove(plugin_id)  # New method — see S6
    trace.emit(component="versioning", level=TraceLevel.WARN,
               message=f"Plugin {plugin_id} disabled due to version incompatibility.")

container.register_singleton(VersionNegotiator, negotiator)
```

**Composition root error handling** (in `main.py`, wrapping `build_container()`):
```python
def main() -> None:
    try:
        container = build_container()
        # ... start web server ...
    except FatalIncompatibilityError as e:
        # Surface to user via stderr (headless) or a minimal error page (if web server can start)
        print(f"SovereignAI cannot start:\n{e}", file=sys.stderr)
        sys.exit(1)
```

**Note on `TraceLevel.CRITICAL`**: Rev1 S5 used `TraceLevel.CRITICAL` which does not exist in the current enum (`sovereignai/shared/types.py` defines only TRACE/DEBUG/INFO/WARN/ERROR). Rev2 uses `TraceLevel.ERROR` (the highest existing level). Do NOT add a CRITICAL level to the enum — that would be a core change for no architectural benefit.

### S6 — Update CapabilityGraph to remove disabled plugins entirely

Per Rev2 F-34 — disabled plugins are removed from the graph, not marked as "present but skipped." This prevents any query method from accidentally invoking a disabled plugin.

Add to `CapabilityGraph`:
```python
def remove(self, component_id: ComponentId) -> None:
    """Remove a component from the graph entirely. Used by the version negotiator to disable incompatible plugins."""
    # Remove from all capability indexes
    for cap_list in self._capabilities_by_category.values():
        self._capabilities_by_category[cap_list.category] = [
            entry for entry in cap_list if entry.component_id != component_id
        ]
    # Remove from component registry
    self._components.pop(component_id, None)
```

This is an edit to `sovereignai/shared/capability_graph.py` (core). Per P1, this requires justification: the negotiator needs a way to disable incompatible plugins, and "remove entirely" is simpler and safer than "mark as disabled and filter in every query method." The alternative (filtering in `find_providers()` only) leaves other query methods (`find_provider` singular, `list_capabilities`) as bypass vectors. Removing entirely is the correct minimal fix.

### S7 — Tests

- `tests/test_semver.py`: Test parsing, comparison, compatibility, bumping, invalid input rejection.
- `tests/test_version_negotiator.py`: Test strict core check, lenient plugin check, dependency graph building, missing-version migration (0.0.0 default), `FatalIncompatibilityError` raised (not SystemExit).
- `tests/test_compatibility_matrix.py`: Test recording, querying, atomic write (kill mid-write does not corrupt), corruption recovery, pruning at 1000 entries, schema_version field.
- `tests/test_manifest_version_validation.py`: Test invalid version strings rejected, missing version defaults to 0.0.0 with WARN.
- `tests/test_negotiator_disabled_removal.py`: Test that disabled plugins are removed from the graph (not just marked), and no query method can invoke them.

---

## STOP Conditions

- If version negotiation takes more than 1 second on startup (with the current component count of ~15), STOP. Revisit caching if component count grows past 50 — see DEBT.md note.
- If a core component passes strict check but is actually incompatible (behavioral, not version), STOP — this is a manifest authoring bug, not a negotiator bug. Document in LANDMINES.md.
- If `FatalIncompatibilityError` is not caught by the composition root (process crashes with stack trace instead of clean error message), STOP.
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
- `tests/test_negotiator_disabled_removal.py`

## Files WILL Edit

- `sovereignai/shared/manifest_parser.py` (relax version requirement — default to "0.0.0" if missing)
- `sovereignai/shared/capability_graph.py` (add `remove()` method — minimal core addition, justified in S6)
- `sovereignai/main.py` (add negotiation step, FatalIncompatibilityError handling, composition root try/except)

## Files WILL NOT Edit

- Any other file in `sovereignai/shared/` (core is sacred per P1 — only `manifest_parser.py` and `capability_graph.py` are edited, with justification)
- `AGENTS.md` (except S0.3)

---

## Closing

Run `/close`. Tag: `prompt-12`. Update CHANGELOG, PLANS.md.

## Adjudication summary (Rev1 → Rev2)

Findings addressed: F-6 (missing version defaults to 0.0.0), F-12 (typed FatalIncompatibilityError, not SystemExit), F-19 (atomic write, schema_version, pruning, corruption recovery), F-25 (false-startup-failure angle — missing version passes), F-34 (disabled plugins removed from graph entirely), F-37 (STOP threshold note — caching deferred to DEBT.md if component count grows), F-38 ("latest" = highest SemVer, tie-break by registration order), F-42 (dependency changed to prompt-10).

Findings rejected: F-25 philosophical angle (hybrid versioning is vision-endorsed per Q8 resolution), F-51 (component-level versioning is correct for v1; capability-level is over-engineering), F-52 (STOP thresholds are calibrated).

DEBT.md additions: Add "Version negotiation caching" — trigger: component count >50; target: future plan.
