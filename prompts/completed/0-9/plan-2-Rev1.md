# Plan 2 — Discovery Layer (Manifest Parser, Capability Graph, ICapabilityIndex)

**Batch**: 2 of 4 (Plans 1–4 are drafted together; shared context brief at `plan-1-4-batch-Rev1-context-brief.md`)

Depends on: prompt-1
Vision principles: 1 (sacred core), 2 (pluggable), 3 (no provider lock-in), 5 (wire as you go), 7 (modular core), 9 (observability), 11 (DI, no globals), 12 (plain-English docstrings), 13 (strong, robust)
Open questions resolved: Q1 (adapter contract — manifest format), Q2 (skill discovery — directory scan + manifest), Q8 (MVP — full versioning deferred per DEBT)

---

## S0 — Opening

**S0.1** — Run `/open` workflow. Verify `prompt-1` tag exists on origin. Confirm clean working copy on `main`. Activate venv (OR45).

**S0.2** — Read `AGENTS.md` in full. Note always-on subset. Note AR9 (no hard-coded component names — capability graph is the discovery path; only `main.py` and tests are exempt), AR13 (skills consume tools via capability graph — relevant when Plan 2's manifest schema is consumed by future skills), AR15 (adapters register tools at startup — Plan 2's capability graph is where they register).

**S0.3** — No new AR/OR rules this plan. Proceed to S1.

---

## Architectural Context

Per the locked scope adjudication:

- **A5** — Plan 2 ships `ICapabilityIndex` as a locked named protocol. Plan 4 imports only this protocol — never core internals. A static-import test in Plan 4 confirms AR7 compliance.
- Plan 2 depends on Plan 1's `shared/types.py` for manifest and capability types.
- Plan 2 does NOT include the routing engine (moved to Plan 3 per A1 — routing engine needs Lifecycle Manager from Plan 3 to know component status).

**Key constraints:**
- AR9: No hard-coded component names at runtime. Capability graph is the discovery path.
- AR15: At startup every adapter calls the capability graph to register each tool it exposes.
- Q1 resolution: capability-based discovery via static manifest (TOML) declaring capability categories plus a protocol/interface.
- Q2 resolution: hybrid — directory scan on startup discovers manifests; unit of skill is a directory.
- Q8 resolution: MVP only — semantic versioning on manifest, capability negotiation deferred (DEBT item).

---

## S1 — Extend `shared/types.py` with Capability Types

### S1.1 — Add capability domain types to `shared/types.py`

Append to `sovereignai/shared/types.py` (use Edit tool — never sed per OR7/OR44):

```python
# ============================================================================
# Capability types (used by manifest parser + capability graph in Plan 2)
# ============================================================================

class CapabilityCategory(str, Enum):
    """Category of capability a component provides.
    
    Adapters declare model categories; skills declare tool categories;
    memory backends declare storage categories. The capability graph
    routes requests to components based on these declarations.
    """
    MODEL_INFERENCE = "model_inference"      # adapters: OpenAI, Ollama, etc.
    TOOL = "tool"                            # skills: websearch, calculator
    MEMORY = "memory"                        # backends: Postgres, Qdrant
    COMMUNICATION = "communication"          # gateways: voice, IM


@dataclass(frozen=True)
class CapabilityDeclaration:
    """Single capability a component claims to provide.
    
    Frozen so declarations can be safely shared and compared across
    threads. The priority field lets the routing engine (Plan 3)
    pick the highest-priority provider when multiple components
    satisfy the same capability.
    """
    category: CapabilityCategory
    name: str                 # e.g. "text_generation", "websearch", "vector_search"
    version: str              # semver, e.g. "1.0.0" (Q8 MVP — full negotiation deferred)
    priority: int = 0         # higher = preferred; routing engine picks max


@dataclass(frozen=True)
class ComponentManifest:
    """Parsed manifest declaring what a component provides and needs.
    
    Read from a TOML file at startup (per Q1 resolution: static manifest
    declaring capability categories plus a protocol/interface). Frozen
    so manifests are immutable once loaded.
    """
    component_id: ComponentId            # e.g. "OpenAIAdapter", "WebSearchSkill"
    version: str                          # component semver, e.g. "1.2.0"
    provides: tuple[CapabilityDeclaration, ...]   # capabilities this component offers
    requires: tuple[CapabilityDeclaration, ...]   # capabilities this component needs (empty for Plan 2 MVP)
    author: str                           # provenance — who built it (P14)
    content_hash: str                     # provenance — verified on install (P14)
```

After edit, run `/verify`. Run existing tests to confirm no regressions:
```bash
.venv/Scripts/python.exe -m pytest tests/ -vvv
```

---

## S2 — Capability Manifest Parser

### S2.1 — Create `sovereignai/shared/manifest_parser.py`

Per Q1: static manifest in TOML format. Per Q2: directory scan discovers manifests at startup.

```python
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
from typing import List

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


def _parse_caps(raw: List[dict], path: Path) -> List[CapabilityDeclaration]:
    """Convert raw TOML capability entries into frozen CapabilityDeclaration objects.

    Args:
        raw: List of dicts from the TOML file's provides[] or requires[].
        path: Manifest path, used for error messages.

    Returns:
        List of CapabilityDeclaration instances.

    Raises:
        ManifestParseError: If any entry is missing fields or has an
            invalid category.
    """
    result: List[CapabilityDeclaration] = []
    for i, entry in enumerate(raw):
        try:
            category = CapabilityCategory(entry["category"])
        except (KeyError, ValueError) as exc:
            raise ManifestParseError(
                f"Manifest {path} entry {i} has invalid category: {exc}"
            ) from exc
        result.append(CapabilityDeclaration(
            category=category,
            name=entry["name"],
            version=str(entry["version"]),
            priority=int(entry.get("priority", 0)),
        ))
    return result
```

After creating, run `/verify`.

### S2.2 — Create `tests/test_manifest_parser.py`

Required tests:

1. **`test_parse_valid_manifest`** — well-formed TOML produces correct ComponentManifest
2. **`test_parse_missing_file_raises`** — nonexistent path raises ManifestParseError
3. **`test_parse_missing_required_field_raises`** — TOML without `component_id` raises
4. **`test_parse_invalid_category_raises`** — `category = "unknown"` raises
5. **`test_parse_provides_with_priority`** — priority defaults to 0 when omitted
6. **`test_parse_requires_empty_when_omitted`** — no `requires[]` key → empty tuple

Use `pytest` fixtures with `tmp_path` to create test manifest files.

After tests pass, run `/verify`.

---

## S3 — Capability Graph (with `ICapabilityIndex` Protocol)

### S3.1 — Create `sovereignai/shared/capability_graph.py`

Per A5: ships `ICapabilityIndex` as a locked named protocol. Per AR9: no hard-coded component names — discovery routes through the graph. Per AR15: adapters register tools at startup via the graph.

```python
"""In-memory index of registered components and their capabilities.

Per AR9: components are discovered by capability, not by hard-coded
name. The graph is the single source of truth for what the system
can do at any given moment (per AR15).

Per A5: ships ICapabilityIndex as a locked named protocol. Plan 4
imports only this protocol — never the concrete CapabilityGraph
class. This enforces AR7 (UIs consume the protocol, not core
internals).
"""
from __future__ import annotations

from threading import Lock
from typing import Dict, List, Protocol, Tuple

from sovereignai.shared.types import (
    CapabilityCategory,
    CapabilityDeclaration,
    ComponentId,
    ComponentManifest,
)


class ICapabilityIndex(Protocol):
    """Locked query interface for the capability graph.

    Plan 4's Capability API imports ONLY this protocol — never the
    concrete CapabilityGraph class. This enforces AR7 (UIs are
    separate processes consuming the Capability API; they never
    reach into core internals).

    Any component that needs to query capabilities should depend on
    this protocol, not on CapabilityGraph directly. The DI container
    (Plan 1) registers the concrete graph against this protocol.
    """

    def find_providers(self, category: CapabilityCategory,
                       name: str) -> Tuple[ComponentId, CapabilityDeclaration]:
        """Return all components that provide a given capability, sorted by priority.

        Args:
            category: The capability category to search.
            name: The specific capability name (e.g. "text_generation").

        Returns:
            Tuple of (component_id, declaration) pairs, highest priority
            first. Empty tuple if no providers registered.
        """
        ...

    def list_all_components(self) -> Tuple[ComponentManifest, ...]:
        """Return manifests for every registered component.

        Returns:
            Tuple of ComponentManifest instances. Empty if nothing
            registered.
        """
        ...


class CapabilityGraph:
    """In-memory index mapping capabilities to the components that provide them.

    The graph is populated at startup by the Composition Root: each
    adapter/skill/backend's manifest is parsed and registered. The
    graph implements ICapabilityIndex so callers can depend on the
    protocol, not the concrete class.
    """

    def __init__(self) -> None:
        """Create an empty capability graph with no registered components."""
        # Map (category, name) -> list of (component_id, declaration)
        self._index: Dict[Tuple[CapabilityCategory, str],
                          List[Tuple[ComponentId, CapabilityDeclaration]]] = {}
        # Map component_id -> manifest (for list_all_components)
        self._manifests: Dict[ComponentId, ComponentManifest] = {}
        self._lock = Lock()

    def register(self, manifest: ComponentManifest) -> None:
        """Add a component's manifest to the graph so its capabilities become discoverable.

        Args:
            manifest: Frozen ComponentManifest parsed from the
                component's manifest.toml file.
        """
        with self._lock:
            self._manifests[manifest.component_id] = manifest
            for cap in manifest.provides:
                key = (cap.category, cap.name)
                self._index.setdefault(key, []).append(
                    (manifest.component_id, cap)
                )
                # Keep sorted by priority descending
                self._index[key].sort(key=lambda x: -x[1].priority)

    def find_providers(self, category: CapabilityCategory,
                       name: str) -> Tuple[ComponentId, CapabilityDeclaration]:
        """Return all components that provide a given capability, sorted by priority.

        Args:
            category: The capability category to search.
            name: The specific capability name.

        Returns:
            Tuple of (component_id, declaration) pairs, highest priority
            first. Empty tuple if no providers registered.
        """
        with self._lock:
            key = (category, name)
            return tuple(self._index.get(key, []))

    def list_all_components(self) -> Tuple[ComponentManifest, ...]:
        """Return manifests for every registered component.

        Returns:
            Tuple of ComponentManifest instances. Empty if nothing
            registered.
        """
        with self._lock:
            return tuple(self._manifests.values())
```

**Verify:**
- `ICapabilityIndex` is a `Protocol` (locked named output per A5)
- `CapabilityGraph` implements the protocol
- Thread-safe (Lock around `_index` and `_manifests`)
- No hard-coded component names (AR9)
- Every `def` has a docstring (AR21)

After creating, run `/verify`.

### S3.2 — Create `tests/test_capability_graph.py`

Required tests:

1. **`test_register_single_component_findable`** — register manifest with one capability, find_providers returns it
2. **`test_register_multiple_providers_sorted_by_priority`** — two providers, higher priority returned first
3. **`test_find_providers_empty_when_no_match`** — capability not registered, returns empty tuple
4. **`test_list_all_components_returns_all_manifests`** — register 3, list returns 3
5. **`test_list_all_components_empty_when_nothing_registered`** — fresh graph, returns empty tuple
6. **`test_protocol_compliance`** — `isinstance(graph, ICapabilityIndex)` returns True (Protocol structural typing)

After tests pass, run `/verify`.

---

## S4 — Example Manifests (Test Fixtures)

### S4.1 — Create `tests/fixtures/manifests/` directory with example manifests

These serve as both test fixtures and documentation for component authors. Create 3 example manifests:

**`tests/fixtures/manifests/openai_adapter.toml`**:
```toml
component_id = "OpenAIAdapter"
version = "1.0.0"
author = "sovereignai-team"
content_hash = "sha256:example-openai-hash"

[[provides]]
category = "model_inference"
name = "text_generation"
version = "1.0.0"
priority = 10

[[provides]]
category = "model_inference"
name = "embeddings"
version = "1.0.0"
priority = 10
```

**`tests/fixtures/manifests/websearch_skill.toml`**:
```toml
component_id = "WebSearchSkill"
version = "0.5.0"
author = "sovereignai-team"
content_hash = "sha256:example-websearch-hash"

[[provides]]
category = "tool"
name = "websearch"
version = "1.0.0"
priority = 5

[[requires]]
category = "model_inference"
name = "text_generation"
version = "1.0.0"
priority = 0
```

**`tests/fixtures/manifests/postgres_backend.toml`**:
```toml
component_id = "PostgresBackend"
version = "1.2.0"
author = "sovereignai-team"
content_hash = "sha256:example-postgres-hash"

[[provides]]
category = "memory"
name = "relational"
version = "1.0.0"
priority = 8

[[provides]]
category = "memory"
name = "full_text"
version = "1.0.0"
priority = 6
```

These are referenced by `tests/test_manifest_parser.py` and `tests/test_capability_graph.py`.

After creating, run `/verify`.

---

## S5 — Extend Composition Root (`main.py`)

### S5.1 — Add capability graph registration to `build_container()`

Per A3: Composition Root is incremental. Extend `sovereignai/main.py`'s `build_container()` to register the CapabilityGraph after the EventBus.

Old text (end of `build_container()`):
```python
    # 2. EventBus — depends on TraceEmitter, singleton
    bus = EventBus(trace=trace)
    container.register_singleton(EventBus, bus)

    return container
```

New text:
```python
    # 2. EventBus — depends on TraceEmitter, singleton
    bus = EventBus(trace=trace)
    container.register_singleton(EventBus, bus)

    # 3. CapabilityGraph — no dependencies, singleton (Plan 2)
    # Registered against ICapabilityIndex protocol so Plan 4's Capability
    # API can depend on the protocol, not the concrete class (per A5).
    from sovereignai.shared.capability_graph import (
        CapabilityGraph,
        ICapabilityIndex,
    )
    graph = CapabilityGraph()
    container.register_singleton(CapabilityGraph, graph)
    container.register_singleton(ICapabilityIndex, graph)

    return container
```

After edit, run `/verify`.

### S5.2 — Update `tests/test_composition_root.py`

Add tests for the new capability graph wiring:

7. **`test_capability_graph_registered`** — retrieve CapabilityGraph from container, not None
8. **`test_icapability_index_registered`** — retrieve ICapabilityIndex from container, returns the same graph instance
9. **`test_capability_graph_is_singleton`** — retrieve twice, same instance

(Tests 1-5 from Plan 1 still pass — verify no regressions.)

After tests pass, run `/verify`.

---

## S6 — Update PLANS.md Baseline

### S6.1 — Update Test Baseline

Plan 2 adds tests. New total: 22 (Plan 1) + 6 (manifest parser) + 6 (capability graph) + 3 (composition root extensions) = **37 tests**.

Update the Test Baseline section in `PLANS.md` accordingly. (The exact count will be confirmed at `/close`.)

### S6.2 — Add DEBT entry for Q8 full versioning

Per A: Q8 MVP only in Plan 2; full versioning/capability negotiation deferred.

Append to `DEBT.md`:
```markdown
## Deferred: Full Q8 versioning / capability negotiation

**Deferred at**: prompt-2 (per Plan 1-4 scope adjudication)
**Reason**: Plan 2 ships Q8 MVP only — manifests declare semver versions, but no capability negotiation (resolving incompatible versions at startup) is implemented.
**Trigger condition**: When a second adapter version is needed and two components declare incompatible versions of the same capability.
**Target plan**: TBD (post Plan 2).
```

After edit, run `/verify`.

---

## S7 — Update CHANGELOG.md

Append to `CHANGELOG.md`:

```markdown
## prompt-2 — Discovery layer (manifest parser, capability graph, ICapabilityIndex)

**Date**: {YYYY-MM-DD}
**Plan file**: prompts/plan-2-Rev1.md

**Files changed**:
- sovereignai/shared/types.py (extended: CapabilityCategory, CapabilityDeclaration, ComponentManifest)
- sovereignai/shared/manifest_parser.py (new — TOML parser, validates required fields)
- sovereignai/shared/capability_graph.py (new — in-memory index, ICapabilityIndex protocol)
- sovereignai/main.py (extended: registers CapabilityGraph against ICapabilityIndex)
- tests/fixtures/manifests/openai_adapter.toml (new — example fixture)
- tests/fixtures/manifests/websearch_skill.toml (new — example fixture)
- tests/fixtures/manifests/postgres_backend.toml (new — example fixture)
- tests/test_manifest_parser.py (new — 6 tests)
- tests/test_capability_graph.py (new — 6 tests)
- tests/test_composition_root.py (extended — 3 new tests for graph wiring)
- DEBT.md (added Q8 full versioning deferral)
- PLANS.md (updated test baseline)

**Results**:
- Tests: 37 passed (22 from Plan 1 + 15 new)
- Ruff: 0 errors
- Mypy: 0 errors (file-scoped per OR47)
- Bandit: 0 findings
- pip-audit: 0 CVEs (no new runtime deps)
- Vulture: 0 findings
- Detect-secrets: pass

**Notes**:
- Q1 (adapter contract) resolved: TOML manifest declaring capability categories.
- Q2 (skill discovery) resolved: directory scan at startup reads manifest.toml files.
- Q8 (versioning MVP) resolved: semver on manifests; full negotiation deferred (DEBT).
- ICapabilityIndex protocol shipped as locked named output (per A5). Plan 4 will import only this protocol.
- No new runtime dependencies (uses stdlib tomllib).
```

After edit, run `/verify`.

---

## S8 — Commit and Tag Prompt-2

**STOP condition**: If any `/verify` failed, STOP.

1. Stage all changes:
   ```bash
   git add -A
   git status -s | tail -n 30
   ```

2. Commit (multiple `-m` per OR42):
   ```bash
   git commit -m "prompt-2: Discovery layer — manifest parser, capability graph, ICapabilityIndex" -m "shared/types.py: extended with CapabilityCategory, CapabilityDeclaration, ComponentManifest (frozen dataclasses)." -m "shared/manifest_parser.py: TOML parser, validates required fields, raises ManifestParseError on malformed input." -m "shared/capability_graph.py: in-memory index + ICapabilityIndex Protocol (locked named output per A5). Plan 4 imports only the protocol." -m "main.py: extended to register CapabilityGraph against ICapabilityIndex." -m "Tests: 15 new (6 manifest_parser + 6 capability_graph + 3 composition_root). Total: 37." -m "Q1, Q2, Q8 (MVP) resolved. Q8 full negotiation deferred to DEBT."
   ```

3. Tag, push, verify:
   ```bash
   git tag prompt-2
   git push origin main
   git push origin prompt-2
   git ls-remote --tags origin | grep "prompt-2"
   ```

---

## Closing

Run `/close` workflow (all 21 steps). Expected:
- Tests: 37 passed
- Ruff: 0 errors
- Mypy: 0 errors (file-scoped to Plan 2 `.py` files per OR47)
- Bandit: 0 findings
- pip-audit: 0 CVEs
- Vulture: 0 findings
- Detect-secrets: pass

**Key verifications**:
- `ICapabilityIndex` is a `Protocol` (A5)
- `CapabilityGraph` implements it (verified by `test_protocol_compliance`)
- No hard-coded component names at runtime (AR9)
- Manifest parser validates required fields (Q1)
- Capability graph sorts providers by priority (Q4 prep for Plan 3)

After `/close`, create `logs/execution-log-prompt-2.md`. User pastes log, then asks Executor to commit/push.

**Reminder**: Step 21 (kill bash) mandatory.

---

## Files WILL Create

- `sovereignai/shared/manifest_parser.py`
- `sovereignai/shared/capability_graph.py`
- `tests/fixtures/manifests/openai_adapter.toml`
- `tests/fixtures/manifests/websearch_skill.toml`
- `tests/fixtures/manifests/postgres_backend.toml`
- `tests/test_manifest_parser.py`
- `tests/test_capability_graph.py`
- `logs/execution-log-prompt-2.md` (created by `/close`)

## Files WILL Edit

- `sovereignai/shared/types.py` (append capability types at S1.1)
- `sovereignai/main.py` (extend `build_container()` at S5.1)
- `tests/test_composition_root.py` (add 3 new tests at S5.2)
- `DEBT.md` (add Q8 deferral at S6.2)
- `PLANS.md` (update test baseline at S6.1; add prompt-2 row at `/close`)
- `CHANGELOG.md` (append prompt-2 entry at S7)

## Files WILL NOT Edit

- `AGENTS.md`, `AI_HANDOFF.md`, `.devin/workflows/*.md` (stable)
- `documents/*` (archived)
- `prompts/*` (no changes to existing plan files)
- `pyproject.toml`, `.pre-commit-config.yaml`, `.gitignore`, `README.md`, `txt/*` (stable)
- All `.gitkeep` files
- `DECISIONS.md`, `LANDMINES.md` (no new decisions/landmines unless execution surfaces them)

---

*Plan 2 — Discovery Layer. Rev1. Architect draft. Part of Plans 1-4 batch — Round Table reviews alongside plan-1, plan-3, plan-4, and the shared context brief.*
