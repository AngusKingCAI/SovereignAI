Depends on: prompt-21, Plan 22, Plan 23 (P24-E — explicit transitive dep)
Vision principles: P1 (core sacred), P2 (pluggable), P5 (wire as you go), P7 (modular), P9 (observability)
Open questions resolved: Q-24.1 through Q-24.4

S0.5 research: Symbol map (tree-sitter + PageRank) is 200 lines vs 800 for semantic index. Diff-based editing with search/replace + line-range hint balances token efficiency and robustness. SQLite adjacency + recursive CTE need no new deps. tree-sitter-python has pre-compiled Windows wheels.

## S0 — Opening

S0.0 — Not resuming. Skip.
S0.1 — Run /open. Verify `prompt-21`, `prompt-22`, `prompt-23` tags (P24-E — explicit). Working copy clean.
S0.2 — Read AGENTS.md.
S0.3 — Check `.agent/executor/suggestions/` per OOR-1. At drafting: empty.
S0.4 — Check `.agent/shared/DEBT.md`. At drafting: no items relevant. Note: S5 will add new DEBT.md entry at /close.
S0.5 — **Verified (P24-C)**: `DD-21.7.1`, `DD-21.9.1`, `DD-21.10.1`, `DD-21.12.1` do NOT exist in `prompts/completed/plan-21-rev11.md` or `.agent/shared/DECISIONS.md`. ALL parenthetical DD-21.x.x citations REMOVED from this plan. The design decisions themselves (one worker per task, line-range hint, no embeddings, sqlite for graph) are restated without citation — they are local Plan 24 design choices, not inherited decisions.

## Plan Body

### S1 — Create DepartmentManager base in app/sovereignai/managers/base.py
- Bounded pipeline: two deterministic stages (build_context, validate) around one non-deterministic stage (spawn_worker).
- ONE ReAct Worker per task (local design choice — no DD citation).
- `execute_task` spawns isolated ReAct Worker per call; concurrent tasks do not share Worker state or circuit-breaker counters.
- DepartmentManager is stateless — all caches (SymbolMap, TaskGraphCache) scoped per `execute_task()` call.
- Constructor: `__init__(self, container: DIContainer)`. Container injected at composition root (P11 DI only).
- Validation catches Worker false positives. Abstract: `validate(self, deliverable) -> ValidationResult`.
- Abstract: `execute_task(task) -> Deliverable`, `build_context(task) -> dict | None`. Catches `SymbolMapUnavailableError`: emit `trace.department.context_build_failed`, return None. Do not fail task.

### S2 — Create CodingManager in app/sovereignai/managers/coding.py (P24-A, P24-B)
- Extends DepartmentManager. Constructor: `__init__(self, container: DIContainer, project_root: Path | None = None)`.
- Pipeline: read context → spawn ReAct Worker (file ops) → validate (tests exist).
- Emits trace events per stage via TraceEmitterWrapper. Uses existing TaskStateMachine.
- Inherits `SymbolMapUnavailableError` catch from base.
- `build_context()` override: retrieve SymbolMap via `container.retrieve(SymbolMap)`, call `symbol_map.index(self._project_root)`, return dict with ranked symbols. If `SymbolMapUnavailableError`: fall back to base (return None).
- **`execute_task()` fixed (P24-A, P24-B)**:
  ```python
  async def execute_task(self, task):
      ctx = self.build_context()
      if ctx is None:
          log.warning('Symbol context unavailable (degraded mode), proceeding without symbol ranking')
      graph_memory = container.retrieve(TaskGraphCache)
      try:
          tools = container.retrieve(SkillManifestRegistry).get_tools('coding')  # P24-A
          session = SkillSession(task_id=task.id)  # P24-A
          worker = container.retrieve(ReActLoopFactory)
          result = await worker.run(task_description, tools, session, context=ctx, memory=graph_memory)
      finally:
          graph_memory.close()  # P24-B — fires even if retrieve(ReActLoopFactory) throws
      return result
  ```
- `ctx=None` warning logged BEFORE worker spawn.
- Spawns isolated Worker per task. Passes `graph_memory` as `memory` parameter (NOT in context dict).

### S3 — Create file_edit skill in app/skills/official/file_edit/ (P24-H)
- Search/replace with optional line-range hint (local design choice — no DD citation).
- Parser validates hint against search text. If search text matches multiple locations and hint missing/invalid: return `ToolErrorObservation(retryable=True)` requesting disambiguating hint.
- **ReActLoop integration (P24-H)**: tool-error handler tracks per-step retry counter for `file_edit`. On second consecutive retryable ambiguity for same file, append explicit instruction: "You must provide a line-range hint to disambiguate."
- Fallback to pure search/replace only when search text is unique and hint missing.
- Manifest + skill.py + DAG JSON (AR9). Trivial 1-node DAG.
- Auto-discovered by `SkillDiscovery.scan()` per Plan 21 S7. Add assertion to `test_file_edit_skill.py`.

### S4 — Create SymbolMap in app/sovereignai/indexing/symbol_map.py (P24-D)
- Wrap tree-sitter imports in `try/except ImportError`. In `except` block: **log `logger.error("tree-sitter-python is not installed; SymbolMap will operate in DEGRADED mode")` (P24-D)** before setting `_TREE_SITTER_AVAILABLE = False`. Also emit `trace.symbol_map.degraded` trace event at startup.
- `SymbolMap.__init__` checks flag. If unavailable: `health_check()` returns DEGRADED, `query()` raises `SymbolMapUnavailableError`.
- Tree-sitter extracts definitions/references from Python files. Hand-rolled PageRank ranks symbols by relevance.
- No embeddings, no vector store (local design choice — no DD citation).
- Constructor: `__init__(self, project_root: Path | None = None)`. If provided, call `self.index(project_root)` during init. If None, skip.
- Methods: `index(project_root)`, `query(task_description, budget=1024)`.
- Add `tree-sitter-python` to `app/txt/requirements.txt`. Dependency discipline enforced by `ar_checks/check_dependencies.py`.
- Caches index per-call. Re-indexing O(n) in file count. If re-indexing exceeds 30s, log warning. Future: incremental indexing (DEBT.md).
- Tests: `test_symbol_map_tree_sitter.py`, `test_symbol_map_degraded.py` (verifies `health_check` returns DEGRADED + ERROR log + trace event when tree-sitter missing, P24-D).
- Latency test: `test_symbol_map_latency_budget.py`. Warmup + 5-run median ≤2000ms. Env-based skip per landmine M5: `if not os.environ.get('RUN_SLOW_TESTS'): pytest.skip('Set RUN_SLOW_TESTS=1 to enable')`. All timings in failure output (DD-24.11.4).

### S5 — Create TaskGraphCache in app/sovereignai/memory/graph_backend.py (P23-A contract)
- SQLite adjacency tables: `entities (id, type, attributes)`, `relations (source, target, relation)`.
- **Locked signature (P23-A — must match Plan 23 S2.3 Protocol exactly)**: `query(entity_id: str, depth: int = 2) -> list[dict]`. Recursive CTE for traversal. Return type `list[dict]` matches GraphMemory Protocol.
- No new dependencies — `sqlite3` is Python stdlib.
- Constructor: `__init__(self, db_path: Path | str = ':memory:')`. Default `:memory:` for per-task ephemeral storage. File-backed mode (caller supplies `db_path`) is the configurability path — no hardcoded paths.
- Per-task ephemeral scratch space, NOT persistent cross-task memory. Cross-task persistent graph memory deferred (DEBT.md entry at /close).
- Fresh instance per task (registered as factory, not singleton).
- `close()`: closes SQLite connection. Idempotent via `_closed` flag (DD-24.11.2). Called by `execute_task()` in finally block.

### S6 — Wire in app/sovereignai/main.py build_container()
- Register CodingManager in DI container.
- Register TaskGraphCache as FACTORY: `DIContainer.register_factory(TaskGraphCache, lambda: TaskGraphCache())`. Fresh per retrieve().
- Register SymbolMap as FACTORY: `DIContainer.register_factory(SymbolMap, lambda: SymbolMap())`. DepartmentManager retrieves, then calls `instance.index(project_root)`.
- Register in CapabilityGraph with ComponentManifest if needed.

### S7 — Create web endpoints in app/web/main.py
- `/api/departments` GET → `DepartmentListDTO`. `/api/departments/{dept}/tasks` POST → `DepartmentTaskResponseDTO`. `/api/indexing/symbols` GET → `SymbolMapResponseDTO` (call `health_check()` first; if DEGRADED return 503; otherwise `query()` and handle `SymbolMapUnavailableError` with 503). DTOs in `app/web/schemas.py`.

### S8 — Update TUI workers panel in app/tui/panels/workers.py
- WILL edit: `workers.py` — show department managers, ReAct Worker status per task. WILL NOT edit: other panels.
- Query CapabilityAPI for department list + active worker count. Follow `compose()` → `on_mount()` → `_load_data()` pattern.

### S9 — Tests in .agent/executor/tests/sovereignai/ (P24-G, P24-K)
- `test_department_manager.py`: pipeline stages, validation catch, concurrent tasks isolated, **"Task B's fresh SymbolMap correctly re-indexes file changes made by Task A" (P24-K — renamed from ambiguous phrasing)**, `test_department_manager_handles_symbol_map_unavailable`.
- `test_file_edit_skill.py`: search/replace + hint, fallback, multi-match ambiguity rejection, retry counter (P24-H). Assert skill appears in discovered list.
- `test_symbol_map.py`: extraction + ranking, no-embedding, empty-project no-crash, single-file ranking.
- `test_symbol_map_tree_sitter.py`: tree-sitter path.
- `test_symbol_map_degraded.py` (P24-D): ERROR log + trace event + DEGRADED health_check when tree-sitter missing.
- `test_symbol_map_latency_budget.py`: warmup + 5-run median ≤2000ms.
- `test_graph_memory.py`: traversal + persistence, recursive CTE, `test_task_graph_cache_close_idempotent`, **`test_task_graph_cache_satisfies_graph_memory_protocol` (P23-A — named assertion `isinstance(TaskGraphCache(), GraphMemory)`)**.
- `test_department_full_cycle.py` (P24-G): wires mock DepartmentManager → ReActLoop → SkillRunner (file_search) → EventBus → Librarian. Runtime guard checks imports AND `hasattr(Librarian, 'handle_event')`; skip if Librarian subscription unavailable. Verifies single task completes, emits structured events.
- `test_departments_api.py`: list departments, submit task, symbol map query.

### S10 — Landmine compliance
- M1: `sovereignai.*` imports. M2: update `WEB_MAIN_ALLOWED_IMPORTS` + `TUI_ALLOWED_IMPORTS` for `app/web/main.py` + `app/tui/panels/workers.py`. M3: update `spec_match.py` ALLOWLIST for `app/sovereignai/{managers,indexing,memory/graph_backend.py}` + `app/skills/official/file_edit/`. M4: tests in `tests/sovereignai/`.

### S11 — Run /verify after each edit. Run /close per VOR-2.
- At /close step 12, add DD-24.11.1 through DD-24.11.4 to `.agent/shared/DECISIONS.md` as Proposed.
- At /close step 12, add DEBT.md entry: "Cross-task persistent graph memory — target plan TBD".
