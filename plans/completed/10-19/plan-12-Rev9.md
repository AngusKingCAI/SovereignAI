Depends on: prompt-11 (batch ordering — Plan 11 executes first; Plan 12 does not code-depend on Plan 11 per F-42)

Vision principles: P2 (pluggable), P8 (contracts), P14 (provenance)
Open questions resolved: Q8 (versioning — full negotiation)

---

## S0 — Opening

S0.1 — Run `/open`. Verify prompt-11 tag exists on origin (if Plan 11 has not yet executed, verify prompt-10.5 instead and note the batch ordering). Confirm working copy is clean and on `main`.

S0.2 — Read `AGENTS.md` in full. Note the governance rules added in prompts 10.1–10.3 (these apply to this plan's execution and close):
- OR71 (run workflow commands verbatim — re-read `close.md` fresh, do not paraphrase)
- OR75/OR80/OR83 (`git add -A` for ALL commits — no explicit `git add <file>` lists; after every `git add -A`, run `git status -s` to verify staging is clean)
- OR76 (no premature tags — verify `git tag --list prompt-12` is empty before creating)
- OR77 (coverage mandatory at `/close` — STOP if >5% drop from baseline; current baseline: 94%, floor: 89%)
- OR78 (bandit reconciliation — update PLANS.md Low count at every `/close` where tests were added)
- OR82 (never `git mv` — use `mv` + `git add -A` + verify `git ls-files`)

S0.3 — Add new rules (revised from Rev2 per Round Table re-review):
- **OR57** (revised): Core components (EventBus, CapabilityGraph, TaskStateMachine, etc.) use strict versioning — incompatible versions prevent startup. Plugins use lenient versioning — incompatible versions are disabled with a WARN trace. A component is classified as "core" if its manifest declares `core = true` AND it is installed inside the `sovereignai/` package directory; otherwise it is a plugin. Per Rev5 F13: the `core = true` field is IGNORED for components installed outside the sovereignai package (e.g., `~/.sovereignai/plugins/`) — a third-party plugin setting `core = true` is still classified as a plugin. A core component manifest without a `version` field is an error (rejects registration); a plugin manifest without `version` defaults to `"0.0.0"` and passes. Source: Plan 12 Rev3 (N10, N21) + Rev5 (F13).
- **OR58**: "Latest wins" applies ONLY to cosmetic attributes. "Latest" = highest SemVer; ties broken by registration order (first-registered wins). Source: Plan 12 Rev2 (F-38).
- **OR59** (revised): The compatibility matrix is stored in `~/.sovereignai/compatibility.json`, updated on registration, uses atomic writes (`os.replace`), includes `schema_version`, prunes to last 1000 entries, and records `content_hash_a`/`content_hash_b` per entry. On startup, if a component's current `content_hash` differs from the hash in a matrix entry, that entry is invalidated (treated as "unknown"). If the file is corrupted, the system restores from the last `.backup` file (written on every successful `record()`); if no backup exists, rebuilds with "unknown" statuses treated as permissive (startup proceeds, re-test on next registration). Source: Plan 12 Rev3 (N4, N16).
- **OR67** (revised): The VersionNegotiator raises a typed `FatalIncompatibilityError`. The composition root catches this, emits an ERROR trace, and prints the message to stderr. The process exits with code 1: after a 30-second countdown by default (interactive mode); immediately if the `--no-wait` CLI flag is passed. Per Rev5 F7: `sys.stdin.isatty()` is NOT used as a hard gate (it returns False in IDE terminals like PyCharm/VS Code). If `isatty()` is False, print a hint suggesting `--no-wait` but still wait the 30s. Source: Plan 12 Rev3 (N7) + Rev5 (F7).

Commit: `docs: add OR57-OR59, OR67 for prompt-12`

---

## Plan Body

### S1 — Create sovereignai/versioning/semver.py

(Unchanged from Rev2.)

### S2 — Create sovereignai/versioning/negotiator.py

(Revised per Rev3 N10 — core/plugin classification via manifest field.)

**Constructor**: `(capability_graph, trace)` — unchanged.

**Methods**:
- `negotiate() -> NegotiationResult`: Iterate all registered components. For each, check `manifest.core` (default `False` if absent). Core components → `_check_core_compatibility()` (strict, fatal on mismatch). Plugins → `_check_plugin_compatibility()` (lenient, disable on mismatch). **Per Rev6 F4 + Rev7 + Rev9**: after EACH compatibility check (both success AND failure), call `self._matrix.record(...)` to buffer the result. After all pairs are checked, call `self._matrix.flush()` to batch-write. Code sample:

```python
def negotiate(self) -> NegotiationResult:
    fatal_incompatibilities = []
    disabled_plugins = []
    for component in self._all_components():
        for other in self._all_components():
            if component.component_id >= other.component_id:
                continue  # Avoid duplicate pairs
            result = self._check_pair(component, other)
            # Rev9 H1: record BOTH compatible and incompatible results
            self._matrix.record(
                component_a=component.component_id, version_a=component.version,
                content_hash_a=component.content_hash,
                component_b=other.component_id, version_b=other.version,
                content_hash_b=other.content_hash,
                status="compatible" if result.compatible else "incompatible",
            )
            if not result.compatible:
                if component.is_core or other.is_core:
                    fatal_incompatibilities.append(result)
                else:
                    disabled_plugins.append(component.component_id)
    self._matrix.flush()  # Rev9: batch-write all buffered entries at once
    return NegotiationResult(can_start=not fatal_incompatibilities, ...)
```
- `_check_core_compatibility() -> list[Incompatibility]`: Strict. A core component without a `version` field is an error (added to `fatal_incompatibilities` with reason "core component missing version field").
- `_check_plugin_compatibility() -> list[Incompatibility]`: Lenient. A plugin without `version` defaults to `"0.0.0"` and passes.
- `_build_dependency_graph() -> dict`: Unchanged.

**`FatalIncompatibilityError`** (unchanged from Rev2).

### S3 — Create sovereignai/versioning/compatibility_matrix.py

(Revised per Rev3 N4 — content_hash tracking; N16 — backup file.)

**Storage**: `~/.sovereignai/compatibility.json` + `~/.sovereignai/compatibility.json.backup`

**Schema** (REVISED per N4 — added content_hash fields):
```json
{
  "schema_version": 1,
  "entries": [
    {
      "component_a": "capability_api",
      "version_a": "1.2.0",
      "content_hash_a": "sha256:abc123...",
      "component_b": "websearch_skill",
      "version_b": "0.5.0",
      "content_hash_b": "sha256:def456...",
      "tested_at": "2026-06-29T12:00:00Z",
      "status": "compatible"
    }
  ]
}
```

**Methods**:
- `record(component_a, version_a, content_hash_a, component_b, version_b, content_hash_b, status)`: **Rev9**: Appends to an in-memory buffer (does NOT write to disk immediately). The buffer is flushed by `flush()`. This prevents write-storm during startup with many plugins.
- `flush() -> None`: **Rev9**: Writes all buffered entries to `compatibility.json` atomically (temp + `os.replace`), then validates the loaded JSON before copying to `.backup` (per F11). Called once at the end of `negotiate()` after all pairs are checked.
- `is_tested(...) -> bool`: Check if combination was tested AND both content_hashes match current component hashes. If content_hash differs, return False (stale entry — N4).
- `get_status(...) -> str`: Return "compatible", "incompatible", "unknown".
- `_load_with_recovery(path) -> dict` (REVISED per N16): If `json.load()` raises on `compatibility.json`, try `compatibility.json.backup`. If backup also fails, rename corrupted file, log WARN, return `{"schema_version": 1, "entries": []}`. When the matrix is empty (rebuilt), all statuses are "unknown" — the negotiator treats "unknown" as permissive (allows startup; re-tests on next registration).

### S4 — Update ManifestParser to validate version strings

(Revised per Rev3 N21 — core components must have version; plugins default to 0.0.0.)

```python
# Validate version field (per Rev3 N21 + Rev6 F13)
version_str = data.get("version")
# F13: core=true is only respected for components inside the sovereignai package directory.
# Third-party plugins setting core=true are still classified as plugins.
import sovereignai
from pathlib import Path
sovereignai_pkg_dir = Path(sovereignai.__file__).resolve().parent
manifest_dir = path.resolve().parent
is_inside_sovereignai = manifest_dir.is_relative_to(sovereignai_pkg_dir)
is_core = data.get("core", False) and is_inside_sovereignai

# Rev8: set _source_path on the manifest so conformance gate can check first-party status
# (Plan 13 S11 uses getattr(manifest, '_source_path', '') for first-party detection)
manifest._source_path = str(path)

if version_str is None:
    if is_core:
        # Core components MUST have an explicit version
        raise ManifestParseError(
            f"Core component {component_id} is missing required 'version' field"
        )
    else:
        # Plugins default to 0.0.0
        version = SemVer.parse("0.0.0")
        trace.emit(component="manifest_parser", level=TraceLevel.WARN,
                   message=f"Plugin {component_id} has no version field; treating as 0.0.0")
else:
    version = SemVer.parse(version_str)
```

Also: existing `manifest_parser.py` line 50 requires `version` AND `content_hash`. Update to: `if not all([component_id, author, content_hash]): raise ...` (drop `version` from required list — handled per core/plugin above).

### S5 — Update main.py to run negotiation on startup

(Revised per Rev3 N7 — non-interactive detection; N11 — remove from DI container.)

```python
import sys

# 16. Version negotiator
from sovereignai.versioning.negotiator import VersionNegotiator, FatalIncompatibilityError
negotiator = VersionNegotiator(capability_graph=container.retrieve(CapabilityGraph), trace=trace)
result = negotiator.negotiate()

if not result.can_start:
    trace.emit(component="versioning", level=TraceLevel.ERROR,
               message=f"Fatal incompatibilities: {[str(i) for i in result.fatal_incompatibilities]}")
    raise FatalIncompatibilityError(result.fatal_incompatibilities)

for warning in result.warnings:
    trace.emit(component="versioning", level=TraceLevel.WARN, message=warning)

# Remove disabled plugins from BOTH the graph AND the DI container (per Rev3 N11)
graph = container.retrieve(CapabilityGraph)
for plugin_id, plugin_class in result.disabled_plugins_with_classes:
    graph.remove(plugin_id)
    container.remove(plugin_class)  # New method — see S6
    trace.emit(component="versioning", level=TraceLevel.WARN,
               message=f"Plugin {plugin_id} disabled due to version incompatibility; removed from graph and container")

container.register_singleton(VersionNegotiator, negotiator)
```

**Composition root error handling** (REVISED per N7):
```python
def main() -> None:
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--no-wait", action="store_true", help="Exit immediately on fatal errors (for CI)")
    args = parser.parse_args()

    try:
        container = build_container()
        # ... start web server ...
    except FatalIncompatibilityError as e:
        print(f"SovereignAI cannot start:\n{e}", file=sys.stderr)
        # F7: 30s countdown is DEFAULT. --no-wait skips it. isatty() is a HINT, not a hard gate.
        if args.no_wait:
            sys.exit(1)
        if not sys.stdin.isatty():
            print("(Non-interactive terminal detected. Pass --no-wait to exit immediately.)", file=sys.stderr)
        import time
        time.sleep(30)
        sys.exit(1)
```

**`TraceLevel.CRITICAL` note** (unchanged from Rev2): does not exist; use `TraceLevel.ERROR`.

### S6 — Update CapabilityGraph + DIContainer to remove disabled plugins

(Revised per Rev3 N11 — also remove from DI container.)

**`CapabilityGraph.remove(component_id)`** (unchanged from Rev2).

**`DIContainer.remove(component_type)`** (NEW per N11):
```python
def remove(self, component_type: type) -> None:
    """Remove a registered singleton. Used by the version negotiator to disable incompatible plugins.

    Per Rev6 F5: also unsubscribes all event handlers registered by this component.
    Per Rev9: DIContainer.__init__ must accept event_bus and trace as constructor args
    (stored as self._event_bus and self._trace) so remove() can access them.
    """
    with self._lock:
        instance = self._singletons.pop(component_type, None)
    if instance is not None and hasattr(self, '_event_bus') and self._event_bus is not None:
        component_id = getattr(instance, 'component_id', None) or getattr(instance, '_component_id', None)
        subscriber_id = component_id if component_id else id(instance)
        self._event_bus.unsubscribe_all(subscriber_id=subscriber_id)
        if hasattr(self, '_trace') and self._trace is not None:
            self._trace.emit(
                component="container",
                level=TraceLevel.WARN,
                message=f"Removed {component_type} from container and unsubscribed all its event handlers",
            )
```

This is an edit to `sovereignai/shared/container.py` (core). Per P1, justified: without removing the disabled plugin from the container, code that retrieves by class still gets a live instance — the "disabled" plugin can still execute. This is a minimal, correct fix. **Rev9**: DIContainer.__init__ must accept `event_bus` and `trace` as constructor args so `remove()` can access them.

**`NegotiationResult`** updated to include `disabled_plugins_with_classes: list[tuple[ComponentId, type]]` so the composition root can remove both the graph entry and the container entry.

### S7 — Tests

(Updated per Rev3 changes.)

- `tests/test_semver.py`: Unchanged.
- `tests/test_version_negotiator.py`: Test strict core check, lenient plugin check, **core/plugin classification via `core = true` field (N10)**, **missing version on core = error (N21)**, missing version on plugin = 0.0.0, FatalIncompatibilityError raised.
- `tests/test_compatibility_matrix.py`: Test recording, querying, atomic write, corruption recovery via backup, pruning, **content_hash invalidation (N4)**, **backup file restore (N16)**.
- `tests/test_manifest_version_validation.py`: Test invalid version rejected, missing version on core = error, missing version on plugin = 0.0.0.
- `tests/test_negotiator_disabled_removal.py`: Test disabled plugins removed from **both graph AND container (N11)**.
- `tests/test_fatal_error_noninteractive.py` (new): Test that FatalIncompatibilityError exits immediately when `sys.stdin.isatty()` is False or `--no-wait` is passed (N7).

---

## STOP Conditions

- If version negotiation takes more than 1 second on startup, STOP.
- If a core component passes strict check but is actually incompatible (behavioral), STOP.
- If `FatalIncompatibilityError` is not caught by the composition root, STOP.
- If a disabled plugin is still retrievable from the DI container after `container.remove()`, STOP (N11).
- If a core component manifest without `version` passes registration, STOP (N21).
- If coverage drops below 89% (5% drop from 94% baseline), STOP (per OR77).
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
- `tests/test_fatal_error_noninteractive.py` (new per N7)

## Files WILL Edit

- `sovereignai/shared/manifest_parser.py` (relax version requirement — core vs plugin handling)
- `sovereignai/shared/capability_graph.py` (add `remove()` method)
- `sovereignai/shared/container.py` (add `remove()` method — per N11)
- `sovereignai/main.py` (negotiation, FatalIncompatibilityError handling, `--no-wait` flag, non-interactive detection, container.remove for disabled plugins)

## Files WILL NOT Edit

- Any other file in `sovereignai/shared/`
- `AGENTS.md` (except S0.3)

---

## Closing

Run `/close`. Tag: `prompt-12`. Update CHANGELOG, PLANS.md.

## Adjudication summary (Rev2 → Rev3)

New findings addressed: N4 (content_hash invalidation), N7 (non-interactive exit), N10 (core/plugin classification via `core = true`), N11 (container.remove), N16 (backup file restore + permissive unknown), N21 (core version required).
