Depends on: Plan 22, Plan 23
Vision principles: P1 (core sacred), P2 (pluggable), P5 (wire as you go), P7 (modular), P9 (observability)
Open questions resolved: Q-24.1 (DIContainer factory semantics)

S0.4 best practices: Symbol map (Tree-sitter + PageRank) is 200 lines vs 800 for semantic index. Diff-based editing with search/replace + line-range hint balances token efficiency and robustness. SQLite adjacency tables + recursive CTE require no new dependencies. tree-sitter-python provides pre-compiled wheels for all major platforms including Windows; no build toolchain required. tree-sitter is a transitive dependency, not listed separately in requirements.txt.

## S0 — Opening

S0.1 — Run /open. Verify Plan 22 and Plan 23 tags exist on origin. Working copy clean on main.
S0.2 — Read AGENTS.md in full.
S0.3 — No new rules for this plan.

## Plan Body

### S1 — Create DepartmentManager base in sovereignai/managers/base.py
- Bounded pipeline with two deterministic stages (build_context, validate) around one non-deterministic stage (spawn_worker). The pipeline's overall outcome is bounded, not deterministic.
- ONE ReAct Worker per task (clear ownership, DD-21.7.1).
- DepartmentManager.execute_task spawns an isolated ReAct Worker instance per call; concurrent tasks do not share Worker state or circuit-breaker counters.
- DepartmentManager is stateless — all caches (SymbolMap, GraphMemoryBackend) are scoped per execute_task() call, not shared across calls. SymbolMap is instantiated fresh per call; no cross-call cache or generation counter is retained.
- Constructor: __init__(self, container: DIContainer). Stores the container for per-task factory retrieval. The container is injected at composition root (P11 DI only).
- Validation catches Worker false positives (e.g., claims success without tests). Abstract method: validate(self, deliverable) -> ValidationResult.
- Abstract method: execute_task(task) -> Deliverable.
- Catches SymbolMapUnavailableError in build_context(): emit trace.department.context_build_failed event, return Deliverable(status='degraded', warning='SymbolMap unavailable — code indexing disabled. Install tree-sitter-python for full functionality.', context=empty_symbol_context). Do not fail the task — let the Worker proceed without symbol context.

### S2 — Create CodingManager in sovereignai/managers/coding.py
- Extends DepartmentManager.
- Pipeline: read context -> spawn ReAct Worker (file ops) -> validate (tests exist).
- Emits trace events per stage via injected TraceEmitter.
- Uses existing TaskStateMachine for task lifecycle.
- Inherits SymbolMapUnavailableError catch from base DepartmentManager.
- ReAct Worker receives symbol context via task payload. If context is empty (degraded mode), Worker omits symbol-ranking section from its prompt but continues with file operations. No special error handling needed — the Worker never expects a specific symbol-context format.
- Spawns isolated ReAct Worker per task via container.retrieve(ReActLoopFactory)() (Plan 22 S9 registers ReActLoop as factory, not singleton). Each call gets a fresh instance with its own retry counters and circuit-breaker state.

### S3 — Create file_edit skill in skills/official/file_edit/
- Search/replace with optional line-range hint (DD-21.9.1).
- Parser validates hint against search text. If search text matches multiple locations and hint is missing/invalid, return ToolErrorObservation(retryable=True) requesting a disambiguating hint rather than editing the first match.
- Fallback to pure search/replace applies only when search text is unique and hint is missing.
- Manifest + skill.py + DAG JSON (AR9). Trivial 1-node DAG: {nodes: [{id: 'root', type: 'tool', name: 'file_edit'}], edges: []}.
- Auto-discovered by SkillDiscovery.scan() per Plan 21 S7. Add assertion to test_file_edit_skill.py that the skill appears in the discovered skill list.

### S4 — Create SymbolMap in sovereignai/indexing/symbol_map.py
- Wrap tree-sitter imports in try/except ImportError; set _TREE_SITTER_AVAILABLE flag. SymbolMap.__init__ checks the flag; if unavailable, health_check() returns DEGRADED and query() raises SymbolMapUnavailableError.
- Tree-sitter extracts definitions/references from Python files. Hand-rolled PageRank ranks symbols by relevance to current task.
- No embeddings, no vector store (DD-21.10.1).
- Constructor: __init__(self, project_root: Path | None = None). If project_root provided, call self.index(project_root) during initialization.
- Methods: index(project_root), query(task_description, budget=1024).
- Add tree-sitter-python to txt/requirements.txt (OR14). tree-sitter is a transitive dependency; do not list separately. tree-sitter-python provides pre-compiled wheels for all major platforms including Windows — no build toolchain required.
- SymbolMap caches its index per-call. Re-indexing cost is O(n) in file count. If re-indexing exceeds 30 seconds, log a warning. Future: add incremental indexing (DEBT.md).
- Test both paths: test_symbol_map_tree_sitter.py and test_symbol_map_degraded.py (verifies health_check returns DEGRADED when tree-sitter missing). Add test_symbol_map_latency_budget.py: runs a warmup re-index (discarded), then measures 3 consecutive re-index runs. Budget is met if median is ≤2000ms. If test fails, failure message includes all 3 timings to distinguish startup noise from steady-state regression.

### S5 — Create GraphMemoryBackend in sovereignai/memory/graph_backend.py
- SQLite adjacency tables: entities (id, type, attributes), relations (source, target, relation).
- Recursive CTE for traversal: query(entity_id, depth=2).
- No new dependencies — SQLite already required (DD-21.12.1).
- Constructor takes no args. Fresh instance per task (registered as factory, not singleton).

### S6 — Wire in main.py build_container()
- Register CodingManager in DI container.
- Register GraphMemoryBackend as FACTORY (not singleton) via DIContainer.register_factory(GraphMemoryBackend, lambda: GraphMemoryBackend()). Fresh instance per retrieve().
- Register SymbolMapFactory as DIContainer.register_factory(SymbolMapFactory, lambda: SymbolMap()). DepartmentManager calls container.retrieve(SymbolMapFactory) to get a fresh SymbolMap instance, then calls instance.index(project_root) before querying. No second callable invocation.
- Register in existing CapabilityGraph (sovereignai/shared/capability_graph.py) with ComponentManifest if needed for discovery. Does not change existing default backend selection.

### S7 — Create web endpoints in web/main.py
- /api/departments GET: list departments. Returns DepartmentListDTO.
- /api/departments/{dept}/tasks POST: submit department task. Returns DepartmentTaskResponseDTO.
- /api/indexing/symbols GET: query symbol map. Returns SymbolMapResponseDTO. Call symbol_map.health_check() first; if DEGRADED return 503 with SymbolMapStatusDTO(status="DEGRADED"); otherwise call query() and handle SymbolMapUnavailableError with 503.
- DTOs in web/schemas.py.

### S8 — Update TUI workers panel (tui/panels/workers.py)
- WILL edit: workers.py — show department managers, ReAct Worker status per task.
- WILL NOT edit: other panels.
- Query CapabilityAPI for department list + active worker count.
- Follow compose() -> on_mount() -> _load_data() pattern.

### S9 — Create tests
- test_department_manager.py: pipeline stages, validation catch, concurrent tasks isolated, changes from Task A visible to Task B's fresh SymbolMap, test_department_manager_handles_symbol_map_unavailable (verifies degraded fallback).
- test_file_edit_skill.py: search/replace + hint, fallback, multi-match ambiguity rejection. Assert skill appears in discovered list.
- test_symbol_map.py: extraction + ranking, no-embedding, empty-project no-crash, single-file ranking.
- test_symbol_map_tree_sitter.py: tree-sitter path.
- test_symbol_map_degraded.py: health_check returns DEGRADED when tree-sitter missing.
- test_symbol_map_latency_budget.py: warmup + 3-run median ≤2000ms.
- test_graph_memory.py: traversal + persistence, recursive CTE.
- test_department_full_cycle.py: wires mock DepartmentManager -> ReActLoop -> SkillRunner (file_search) -> EventBus -> Librarian. Verifies single task completes, emits structured events, Librarian stores at least one Observation. Use pytest.mark.skipif(not all_deps_present(), reason='Requires Plans 21-24') where all_deps_present checks for sovereignai/agent/react.py, sovereignai/shared/event_bus.py (extended), and sovereignai/managers/coding.py. Remove skipif after all plans land.
- test_departments_api.py: list departments endpoint, submit task endpoint, symbol map query endpoint.

### S10 — Run /verify after each edit. Run /close.
