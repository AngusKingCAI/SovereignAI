Depends on: Plan 22, Plan 23
Vision principles: P1 (core sacred), P2 (pluggable), P5 (wire as you go), P7 (modular), P9 (observability)
Open questions resolved: Q-24.1 (DIContainer factory semantics), Q-24.2 (GraphMemoryBackend wiring), Q-24.3 (build_context return type), Q-24.4 (ephemeral graph memory scope)

S0.5 research: Symbol map (Tree-sitter + PageRank) is 200 lines vs 800 for semantic index. Diff-based editing with search/replace + line-range hint balances token efficiency and robustness. SQLite adjacency tables + recursive CTE require no new dependencies. tree-sitter-python provides pre-compiled wheels for all major platforms including Windows; no build toolchain required.

## S0 — Opening

S0.0 — Not resuming (third plan in queue). Skip resume check.
S0.1 — Run /open. Verify `prompt-22` and `prompt-23` tags exist on origin. Working copy clean on main.
S0.2 — Read AGENTS.md in full.
S0.3 — Check `.agent/executor/suggestions/` per OOR-1. At drafting: empty.
S0.4 — Check `.agent/shared/DEBT.md`. At drafting: no items relevant. Note: S5 will add new DEBT.md entry for cross-task persistent graph memory at /close.
S0.5 — Research findings documented in plan header above.

## Plan Body

### S1 — Create DepartmentManager base in app/sovereignai/managers/base.py
- Bounded pipeline with two deterministic stages (build_context, validate) around one non-deterministic stage (spawn_worker).
- ONE ReAct Worker per task (DD-21.7.1 — verify citation exists in Plan 21 text; if not, remove).
- `DepartmentManager.execute_task` spawns isolated ReAct Worker per call; concurrent tasks do not share Worker state or circuit-breaker counters.
- DepartmentManager is stateless — all caches (SymbolMap, TaskGraphCache) scoped per `execute_task()` call.
- Constructor: `__init__(self, container: DIContainer)`. Stores container for per-task factory retrieval. Container injected at composition root (P11 DI only).
- Validation catches Worker false positives (e.g., claims success without tests). Abstract method: `validate(self, deliverable) -> ValidationResult`.
- Abstract methods: `execute_task(task) -> Deliverable`, `build_context(task) -> dict | None`. Returns symbol context as dict, or None. Catches `SymbolMapUnavailableError`: emit `trace.department.context_build_failed`, return None. Do not fail the task.
- Document: Base `DepartmentManager.execute_task()` passes context dict to Worker. Context dict contains only symbol-context payload; memory backends passed via `memory` parameter (see S2).

### S2 — Create CodingManager in app/sovereignai/managers/coding.py
- Extends DepartmentManager.
- Constructor: `__init__(self, container: DIContainer, project_root: Path | None = None)`. Calls `super().__init__(container)`, stores `self._project_root`.
- Pipeline: read context -> spawn ReAct Worker (file ops) -> validate (tests exist).
- Emits trace events per stage via injected TraceEmitterWrapper.
- Uses existing TaskStateMachine for task lifecycle.
- Inherits `SymbolMapUnavailableError` catch from base.
- `build_context()` override: retrieves SymbolMap via `container.retrieve(SymbolMap)`, calls `symbol_map.index(self._project_root)`, returns dict with ranked symbols. If `SymbolMapUnavailableError`, falls back to base class behavior (return None).
- `execute_task()` sequence with explicit try/finally (DD-24.11.1):
  ```python
  async def execute_task(self, task):
      ctx = self.build_context()
      if ctx is None:
          log.warning('Symbol context unavailable (degraded mode), proceeding without symbol ranking')
      worker = container.retrieve(ReActLoopFactory)
      graph_memory = container.retrieve(TaskGraphCache)
      try:
          result = await worker.run(task_description, tools, session, context=ctx, memory=graph_memory)
      finally:
          graph_memory.close()
      return result
  ```
- Spawns isolated ReAct Worker per task via `container.retrieve(ReActLoopFactory)`. Returns instance directly, no trailing ().
- Retrieves TaskGraphCache per task. Passes to Worker as `memory` parameter (NOT in context dict).
- The `ctx=None` warning logged BEFORE worker spawn (DD-24.11.3).

### S3 — Create file_edit skill in app/skills/official/file_edit/
- Search/replace with optional line-range hint (DD-21.9.1 — verify citation exists in Plan 21 text; if not, remove).
- Parser validates hint against search text. If search text matches multiple locations and hint missing/invalid, return `ToolErrorObservation(retryable=True)` requesting disambiguating hint.
- Fallback to pure search/replace applies only when search text is unique and hint missing.
- Manifest + skill.py + DAG JSON (AR9). Trivial 1-node DAG: `{nodes: [{id: 'root', type: 'tool', name: 'file_edit'}], edges: []}`.
- Auto-discovered by SkillDiscovery.scan() per Plan 21 S7. Add assertion to `test_file_edit_skill.py` that skill appears in discovered list.

### S4 — Create SymbolMap in app/sovereignai/indexing/symbol_map.py
- Wrap tree-sitter imports in try/except ImportError; set `_TREE_SITTER_AVAILABLE` flag. `SymbolMap.__init__` checks flag; if unavailable, `health_check()` returns DEGRADED, `query()` raises `SymbolMapUnavailableError`.
- Tree-sitter extracts definitions/references from Python files. Hand-rolled PageRank ranks symbols by relevance.
- No embeddings, no vector store (DD-21.10.1 — verify citation exists in Plan 21 text; if not, remove).
- Constructor: `__init__(self, project_root: Path | None = None)`. If provided, call `self.index(project_root)` during initialization. If None, skip — caller must call `index()` explicitly.
- Methods: `index(project_root)`, `query(task_description, budget=1024)`.
- Add `tree-sitter-python` to `app/txt/requirements.txt`. Dependency discipline enforced by `.agent/executor/scripts/ar_checks/check_dependencies.py`. tree-sitter is transitive dependency; do not list separately. tree-sitter-python provides pre-compiled wheels for Windows — no build toolchain.
- SymbolMap caches index per-call. Re-indexing cost O(n) in file count. If re-indexing exceeds 30 seconds, log warning. Future: incremental indexing (DEBT.md).
- Tests: `test_symbol_map_tree_sitter.py` and `test_symbol_map_degraded.py` (verifies `health_check` returns DEGRADED when tree-sitter missing).
- Latency test: `test_symbol_map_latency_budget.py`. Methodology: warmup run (discarded), then 5-run median of `SymbolMap(project_root=test_path)` construction+auto-index time. Budget: median ≤2000ms. Use env-based skip per landmine M5: `if not os.environ.get('RUN_SLOW_TESTS'): pytest.skip('Set RUN_SLOW_TESTS=1 to enable latency test')`. Capture all individual timings in failure output (DD-24.11.4).

### S5 — Create TaskGraphCache in app/sovereignai/memory/graph_backend.py
- SQLite adjacency tables: `entities (id, type, attributes)`, `relations (source, target, relation)`.
- Recursive CTE for traversal: `query(entity_id: str, depth: int = 2) -> list[dict]`. Return type matches GraphMemory Protocol (Plan 23 S2.3).
- No new dependencies — `sqlite3` is Python stdlib.
- Constructor: `__init__(self, db_path: Path | str = ':memory:')`. Default `:memory:` for per-task ephemeral storage. Document: TaskGraphCache is per-task ephemeral scratch space, NOT persistent cross-task memory. Cross-task persistent graph memory deferred (DEBT.md entry at /close: "Cross-task persistent graph memory — target plan TBD").
- Fresh instance per task (registered as factory, not singleton).
- `close()` method: closes SQLite connection. Idempotent via `_closed` flag (DD-24.11.2):
  ```python
  def close(self) -> None:
      if self._closed:
          return
      self._closed = True
      try:
          self._conn.close()
      except sqlite3.ProgrammingError:
          pass
  ```
- Called by `DepartmentManager.execute_task()` in finally block.

### S6 — Wire in app/sovereignai/main.py build_container()
- Register CodingManager in DI container.
- Register TaskGraphCache as FACTORY via `DIContainer.register_factory(TaskGraphCache, lambda: TaskGraphCache())`. Fresh instance per retrieve().
- Register SymbolMap as FACTORY via `DIContainer.register_factory(SymbolMap, lambda: SymbolMap())`. DepartmentManager calls `container.retrieve(SymbolMap)`, then `instance.index(project_root)`. Returns instance directly.
- Register in existing CapabilityGraph with ComponentManifest if needed for discovery. Does not change existing default backend selection.

### S7 — Create web endpoints in app/web/main.py
- `/api/departments` GET: list departments. Returns `DepartmentListDTO`.
- `/api/departments/{dept}/tasks` POST: submit department task. Returns `DepartmentTaskResponseDTO`.
- `/api/indexing/symbols` GET: query symbol map. Returns `SymbolMapResponseDTO`. Call `symbol_map.health_check()` first; if DEGRADED return 503 with `SymbolMapStatusDTO(status="DEGRADED")`; otherwise call `query()` and handle `SymbolMapUnavailableError` with 503.
- DTOs in `app/web/schemas.py`.

### S8 — Update TUI workers panel in app/tui/panels/workers.py
- WILL edit: `workers.py` — show department managers, ReAct Worker status per task.
- WILL NOT edit: other panels.
- Query CapabilityAPI for department list + active worker count.
- Follow `compose()` -> `on_mount()` -> `_load_data()` pattern.

### S9 — Create tests in .agent/executor/tests/sovereignai/
- `test_department_manager.py`: pipeline stages, validation catch, concurrent tasks isolated, changes from Task A visible to Task B's fresh SymbolMap, `test_department_manager_handles_symbol_map_unavailable`.
- `test_file_edit_skill.py`: search/replace + hint, fallback, multi-match ambiguity rejection. Assert skill appears in discovered list.
- `test_symbol_map.py`: extraction + ranking, no-embedding, empty-project no-crash, single-file ranking.
- `test_symbol_map_tree_sitter.py`: tree-sitter path.
- `test_symbol_map_degraded.py`: health_check returns DEGRADED when tree-sitter missing.
- `test_symbol_map_latency_budget.py`: warmup + 5-run median ≤2000ms, all timings in failure output.
- `test_graph_memory.py`: traversal + persistence within same instance, recursive CTE, `test_task_graph_cache_close_idempotent`.
- `test_department_full_cycle.py`: wires mock DepartmentManager -> ReActLoop -> SkillRunner (file_search) -> EventBus -> Librarian. Verifies single task completes, emits structured events, Librarian stores at least one Observation. Runtime guard inside test body: `try: import sovereignai.agent.react; import sovereignai.shared.event_bus; import sovereignai.managers.coding; except ImportError: pytest.skip('Requires Plans 21-23')`.
- `test_departments_api.py`: list departments endpoint, submit task endpoint, symbol map query endpoint.

### S10 — Landmine compliance
- M1: All imports use `sovereignai.*` package path.
- M2: Update `WEB_MAIN_ALLOWED_IMPORTS` and `TUI_ALLOWED_IMPORTS` in `.agent/executor/tests/sovereignai/test_ar7_no_core_imports_in_ui.py` for new imports in `app/web/main.py` and `app/tui/panels/workers.py`.
- M3: Update `ALLOWLIST` in `.agent/executor/scripts/ar_checks/spec_match.py` for new paths: `app/sovereignai/managers/`, `app/sovereignai/indexing/`, `app/sovereignai/memory/graph_backend.py`, `app/skills/official/file_edit/`.
- M4: All test files in `.agent/executor/tests/sovereignai/`.

### S11 — Run /verify after each edit. Run /close per VOR-2.
- At /close step 12, add DD-24.11.1 through DD-24.11.4 to `.agent/shared/DECISIONS.md` as Proposed status.
- At /close step 12, add DEBT.md entry: "Cross-task persistent graph memory — target plan TBD".
