Depends on: prompt-21, Plan 22, Plan 23 (P24-E — explicit transitive dep)
Vision principles: P1 (core sacred), P2 (pluggable), P5 (wire as you go), P7 (modular), P9 (observability)
Open questions resolved: Q-24.1 through Q-24.4

Rev 15 patches P24-O (HIGH): `execute_task()` called `self.build_context()` without required `task` argument — `TypeError` at runtime. Fixed.

S0.5 research: Symbol map (tree-sitter + PageRank) is 200 lines vs 800 for semantic index. Diff-based editing with search/replace + line-range hint. SQLite adjacency + recursive CTE need no new deps. tree-sitter-python has pre-compiled Windows wheels.

## S0 — Opening

S0.0 — Not resuming. Skip.
S0.1 — Run /open. Verify `prompt-21`, `prompt-22`, `prompt-23` tags (P24-E — explicit). Working copy clean.
S0.2 — Read AGENTS.md.
S0.3 — Check `.agent/executor/suggestions/` per OOR-1. At drafting: empty.
S0.4 — Check `.agent/shared/DEBT.md`. At drafting: no items relevant. Note: S5 will add new DEBT.md entry at /close.
S0.5 — **Verified (P24-C)**: `DD-21.7.1`, `DD-21.9.1`, `DD-21.10.1`, `DD-21.12.1` do NOT exist in `prompts/completed/plan-21-rev11.md` or `DECISIONS.md`. ALL parenthetical DD-21.x.x citations REMOVED. **Verified (P24-L)**: `SkillManifestRegistry` does NOT exist in repo. `SkillDiscovery` (at `app/sovereignai/skills/discovery.py`) is the existing class — has `scan(paths)` and `get_skill_index() -> dict[str, tuple[CapabilityCategory, str]]`. Use `SkillDiscovery` not `SkillManifestRegistry`. **Verified**: `SkillSession` exists at `app/sovereignai/skills/session.py` — constructor takes NO arguments (`SkillSession()`, not `SkillSession(task_id=...)`).

## Plan Body

### S1 — Create DepartmentManager base in app/sovereignai/managers/base.py
- Bounded pipeline: two deterministic stages (build_context, validate) around one non-deterministic stage (spawn_worker).
- ONE ReAct Worker per task (local design choice — no DD citation).
- `execute_task` spawns isolated ReAct Worker per call; concurrent tasks do not share Worker state or circuit-breaker counters.
- DepartmentManager is stateless — all caches scoped per `execute_task()` call.
- Constructor: `__init__(self, container: DIContainer)`. Stored as `self._container` (P24-L, N4 — explicit).
- Validation catches Worker false positives. Abstract: `validate(self, deliverable) -> ValidationResult`.
- Abstract: `execute_task(task) -> Deliverable`, `build_context(task) -> dict | None`. Catches `SymbolMapUnavailableError`: emit `trace.department.context_build_failed`, return None.

### S2 — Create CodingManager in app/sovereignai/managers/coding.py (P24-A, P24-B, P24-L, N3, N4)
- Extends DepartmentManager. Constructor: `__init__(self, container: DIContainer, project_root: Path | None = None)`. Calls `super().__init__(container)`; stores `self._project_root`.
- Pipeline: read context → spawn ReAct Worker (file ops) → validate (tests exist).
- Emits trace events per stage via TraceEmitterWrapper. Uses existing TaskStateMachine.
- Inherits `SymbolMapUnavailableError` catch from base.
- `build_context()` override: retrieve SymbolMap via `self._container.retrieve(SymbolMap)`, call `symbol_map.index(self._project_root)`, return dict. If `SymbolMapUnavailableError`: return None.
- **`execute_task()` fixed (P24-A, P24-B, P24-L, N3, N4)**:
  ```python
  async def execute_task(self, task):
      ctx = self.build_context(task)  # P24-O: pass task argument
      if ctx is None:
          log.warning('Symbol context unavailable (degraded mode), proceeding without symbol ranking')
      graph_memory = self._container.retrieve(TaskGraphCache)  # N4: self._container, not bare container
      try:
          skill_discovery = self._container.retrieve(SkillDiscovery)  # P24-L: SkillDiscovery, not SkillManifestRegistry
          skill_index = skill_discovery.get_skill_index()  # P24-L: get_skill_index(), not get_tools('coding')
          tools = [manifest for skill_id, (cat, name) in skill_index.items()
                   for manifest in [self._container.retrieve(CapabilityGraph).get_manifest(skill_id)]
                   if cat == CapabilityCategory.SKILL]
          session = SkillSession()  # P24-L: no args
          task_description = task.description if hasattr(task, 'description') else str(task)  # N3
          worker = self._container.retrieve(ReActLoopFactory)
          result = await worker.run(task_description, tools, session, context=ctx, memory=graph_memory)
      finally:
          graph_memory.close()  # P24-B — fires even if retrieve(ReActLoopFactory) throws
      return result
  ```
- `ctx=None` warning logged BEFORE worker spawn.

### S3 — Create file_edit skill in app/skills/official/file_edit/ (P24-H, P24-M)
- Search/replace with optional line-range hint (local design choice — no DD citation).
- Parser validates hint against search text. If search text matches multiple locations and hint missing/invalid: return `ToolErrorObservation(retryable=True)` requesting disambiguating hint.
- **ReActLoop integration (P24-H, P24-M)**: Plan 23 S6 owns the per-tool retry counter and second-ambiguity escalation. file_edit skill only emits the retryable error. Counter resets to 0 on successful edit (no error returned).
- Fallback to pure search/replace only when search text is unique and hint missing.
- Manifest + skill.py + DAG JSON (AR9). Trivial 1-node DAG.
- Auto-discovered by `SkillDiscovery.scan()` per Plan 21 S7. Add assertion to `test_file_edit_skill.py`.

### S4 — Create SymbolMap in app/sovereignai/indexing/symbol_map.py (P24-D)
- Wrap tree-sitter imports in `try/except ImportError`. In `except` block: **log `logger.error("tree-sitter-python is not installed; SymbolMap will operate in DEGRADED mode")` (P24-D)** before setting `_TREE_SITTER_AVAILABLE = False`. Also emit `trace.symbol_map.degraded` trace event at startup.
- `SymbolMap.__init__` checks flag. If unavailable: `health_check()` returns DEGRADED, `query()` raises `SymbolMapUnavailableError`.
- Tree-sitter extracts definitions/references. Hand-rolled PageRank ranks symbols by relevance.
- No embeddings, no vector store (local design choice — no DD citation).
- Constructor: `__init__(self, project_root: Path | None = None)`. If provided, `self.index(project_root)`.
- Methods: `index(project_root)`, `query(task_description, budget=1024)`.
- Add `tree-sitter-python` to `app/txt/requirements.txt`. Dependency discipline enforced by `ar_checks/check_dependencies.py`.
- Caches index per-call. Re-indexing O(n). If exceeds 30s, log warning. Future: incremental indexing (DEBT.md).
- Tests: `test_symbol_map_tree_sitter.py`, `test_symbol_map_degraded.py` (verifies ERROR log + trace event + DEGRADED health_check, P24-D).
- Latency test: `test_symbol_map_latency_budget.py`. Warmup + 5-run median ≤2000ms. Env-based skip per landmine M5: `if not os.environ.get('RUN_SLOW_TESTS'): pytest.skip('Set RUN_SLOW_TESTS=1 to enable')`. All timings in failure output (DD-24.11.4).

### S5 — Create TaskGraphCache in app/sovereignai/memory/graph_backend.py (P23-A contract)
- SQLite adjacency tables: `entities (id, type, attributes)`, `relations (source, target, relation)`.
- **Locked signature (P23-A)**: `query(entity_id: str, depth: int = 2) -> list[dict]`. Recursive CTE. Return type `list[dict]` matches GraphMemory Protocol exactly.
- No new dependencies — `sqlite3` is Python stdlib.
- Constructor: `__init__(self, db_path: Path | str = ':memory:')`. Default `:memory:` for per-task ephemeral. File-backed mode (caller supplies `db_path`) is configurability.
- Per-task ephemeral scratch space, NOT persistent cross-task memory. Cross-task persistent graph memory deferred (DEBT.md entry at /close).
- Fresh instance per task (registered as factory).
- `close()`: closes SQLite connection. Idempotent via `_closed` flag (DD-24.11.2).

### S6 — Wire in app/sovereignai/main.py build_container()
- Register CodingManager in DI container.
- Register TaskGraphCache as FACTORY: `register_factory(TaskGraphCache, lambda: TaskGraphCache())`.
- Register SymbolMap as FACTORY: `register_factory(SymbolMap, lambda: SymbolMap())`.
- Register in CapabilityGraph with ComponentManifest if needed.

### S7 — Create web endpoints in app/web/main.py
- `/api/departments` GET → `DepartmentListDTO`. `/api/departments/{dept}/tasks` POST → `DepartmentTaskResponseDTO`. `/api/indexing/symbols` GET → `SymbolMapResponseDTO` (call `health_check()` first; if DEGRADED return 503; otherwise `query()` and handle `SymbolMapUnavailableError` with 503). DTOs in `app/web/schemas.py`.

### S8 — Update TUI workers panel in app/tui/panels/workers.py
- WILL edit: `workers.py` — show department managers, ReAct Worker status per task. WILL NOT edit: other panels.
- Query CapabilityAPI. Follow `compose()` → `on_mount()` → `_load_data()` pattern.

### S9 — Tests in .agent/executor/tests/sovereignai/ (P24-G, P24-K, P24-L)
- `test_department_manager.py`: pipeline stages, validation catch, concurrent tasks isolated, **"Task B's fresh SymbolMap correctly re-indexes file changes made by Task A" (P24-K)**, `test_department_manager_handles_symbol_map_unavailable`, **`test_execute_task_uses_skill_discovery_not_registry` (P24-L)**, **`test_execute_task_passes_task_to_build_context` (P24-O — verifies no TypeError on build_context call)**.
- `test_file_edit_skill.py`: search/replace + hint, fallback, multi-match ambiguity rejection, retry counter integration with Plan 23 S6 (P24-H, P24-M — counter resets on success). Assert skill appears in discovered list.
- `test_symbol_map.py`: extraction + ranking, no-embedding, empty-project no-crash, single-file ranking.
- `test_symbol_map_tree_sitter.py`: tree-sitter path.
- `test_symbol_map_degraded.py` (P24-D): ERROR log + trace event + DEGRADED health_check when tree-sitter missing.
- `test_symbol_map_latency_budget.py`: warmup + 5-run median ≤2000ms.
- `test_graph_memory.py`: traversal + persistence, recursive CTE, `test_task_graph_cache_close_idempotent`, **`test_task_graph_cache_satisfies_graph_memory_protocol` (P23-A — named assertion `isinstance(TaskGraphCache(), GraphMemory)`)**.
- `test_department_full_cycle.py` (P24-G): wires mock DepartmentManager → ReActLoop → SkillRunner (file_search) → EventBus → Librarian. Runtime guard checks imports AND `hasattr(Librarian, 'handle_event')`; skip if Librarian subscription unavailable.
- `test_departments_api.py`: list departments, submit task, symbol map query.

### S10 — Landmine compliance
- M1: `sovereignai.*` imports. M2: update `WEB_MAIN_ALLOWED_IMPORTS` + `TUI_ALLOWED_IMPORTS` for `app/web/main.py` + `app/tui/panels/workers.py`. M3: update `spec_match.py` ALLOWLIST for `app/sovereignai/{managers,indexing,memory/graph_backend.py}` + `app/skills/official/file_edit/`. M4: tests in `tests/sovereignai/`.

### S11 — Run /verify after each edit. Run /close per VOR-2.
- At /close step 12, add DD-24.11.1, DD-24.11.2, DD-24.11.3, DD-24.11.4 to `.agent/shared/DECISIONS.md` as Proposed (N5 — explicit list, no ranges).
- At /close step 12, add DEBT.md entry: "Cross-task persistent graph memory — target plan TBD".
