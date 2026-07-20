Depends on: Plan 33 (Agent Lifecycle), Plan 22 (EventBus), Plan 24 (Graph Memory)
Vision principles: P1 (Core sacred), P2 (Pluggable), P9 (Observability), P13 (Strong and robust)
AR rules: AR1, AR2, AR8
OR rules: UOR-1, UOR-2
Open questions resolved: DD-34.1, DD-34.2, DD-34.3, DD-34.4, DD-34.5, DD-34.6, DD-34.7
**Revision**: Rev16

## Executor Manifest

**Plan**: 34
**Phases**: 6 (S1–S6; S0 excluded from count)
**Deliverables**:
| Phase | Deliverable | Verification |
|-------|-------------|--------------|
| S1 | `app/sovereignai/librarian/librarian.py` event handler | `pytest app/sovereignai/tests/test_librarian_events.py -v` passes |
| S2 | `app/sovereignai/memory/episodic_consumer.py` | `pytest app/sovereignai/tests/test_episodic_consumer.py -v` passes |
| S3 | `app/sovereignai/memory/persistent_graph.py` + `MemoryGateway` | `pytest app/sovereignai/tests/test_persistent_graph.py -v` passes |
| S4 | Integration: Librarian + MemoryGateway + EventBus wiring | `pytest app/sovereignai/tests/test_librarian_integration.py -v` passes |
| S5 | API exposure via Orchestrator facade | `pytest app/web/tests/test_memory_api.py -v` passes |
| S6 | AR check scripts + document hygiene | `pytest .agent/executor/tests/test_document_hygiene.py -v` passes |

**Coverage target**: ≥90%
**Forbidden actions**: Do not modify `AI_HANDOFF.md`, `AGENTS.md`, `PRINCIPLES.md`, `OR_RULES.md`, `PLANS.md`, `DEBT.md`.
**Commit message**: `feat(memory): add persistent graph memory, episodic consumer, and librarian event handler`

## S0 — Opening

S0.1: Run `/open`
S0.2: Read `AGENTS.md` in full. Read plan header AR rules from `.agent/executor/ARCHITECTURE.md`. Read plan header OR rules from `.agent/executor/OR_RULES.md`.
S0.3: Check `.agent/shared/DEBT.md` for deferred items.
S0.4: **Prerequisite check**: verify Plan 22 TaskEvent schema includes monotonic `event_sequence` per task. Programmatic check: `python -c 'from app.sovereignai.messaging.schemas import TaskEvent; assert hasattr(TaskEvent, "event_sequence")'`. Record prerequisite as AGENTS.md trace entry per invariant #12: "S0.4 prerequisite: PLAN22_EVENT_SEQUENCE=present|absent". This is written to the execution trace (trace-plan-34.jsonl), not a separate log file. If missing → use fallback dedup key `(task_id, event_type, correlation_id)` per S4.3 branch. No Plan 22 modification required.

## S1 — Librarian Event Handler (DEBT-6)

S1.1: Add `handle_event(self, event: TaskEvent)` to `app/sovereignai/librarian/librarian.py`
S1.2: Subscribe to: `task.created`, `task.updated`, `task.completed`, `task.failed`, `task.deleted` via Plan 22 EventBus. Prerequisite: `event_sequence` per S0.4.
S1.3: On `task.completed`: extract entities, update knowledge graph via `MemoryGateway` (injected, not imported directly). MemoryGateway proxies to `PersistentGraphMemory`.
S1.4: On `task.failed`: rollback via `MemoryGateway.rollback(task_id: str) -> bool`. Returns `True` if merge in-progress and rolled back; `False` if already committed or no transaction. `merge()` wraps inserts/updates in single `aiosqlite` transaction after `async with lock:`. `asyncio.Lock` ensures one merge at a time. `rollback(task_id)` acquires same lock, checks for active transaction owned by task_id, executes ROLLBACK if in-progress (returns True), returns False if committed. In-memory transaction tracking: `_active_task_id: Optional[str]` (set to task_id when merge begins, cleared on commit/rollback). `_in_transaction: bool` (True during merge). Both set within `async with lock:` block. `rollback(task_id)` checks `_active_task_id == task_id and _in_transaction`. v1 limitation: `rollback(task_id)` cannot interrupt an in-progress `merge()` holding the asyncio.Lock; it waits for merge completion, then returns False (committed). Log WARN with task_id. Operator review in v2 via `/api/orchestrator/memory/conflicts`. Accept inconsistency in v1. **v1 rollback limitation — operator guidance**: If rollback(task_id) returns False (merge committed before rollback request), operators may review conflicts at GET /api/orchestrator/memory/conflicts. In v1, resolution_status is always "unresolved" and manual DB edits are not supported. v2 will provide resolution API endpoint.
S1.5: On `task.deleted`: garbage-collect from per-task ephemeral storage only. Persistent graph entities are shared cross-task and NOT deleted. Provenance reference counting deferred to v2.
S1.6: Per AR2: Librarian is the sole core-side consumer of memory backends (via MemoryGateway injection); workers query Librarian, not backends directly.
S1.7: Test: `pytest app/sovereignai/tests/test_librarian_events.py -v` — `test_task_completed_updates_graph`, `test_task_failed_rollback_in_progress`, `test_task_failed_post_commit_returns_false`, `test_task_deleted_ephemeral_only`, `test_rollback_blocks_on_unrelated_task_merge_lock`, `test_merge_relation_src_and_dst_rewritten`, `test_merge_relation_dedup_after_reattachment`, `test_merge_self_loop_handling`

## S2 — Episodic Event Consumer

S2.1: Create `app/sovereignai/memory/episodic_consumer.py` — `EpisodicEventConsumer`
S2.2: Subscribes to all `orchestrator.*` and `messaging.*` events
S2.3: Persists: event type, timestamp, correlation_id, summary (truncated 500 chars, `VARCHAR(500)`); no raw payload
S2.4: Retention: configurable via `BehaviorSettings.episodic_retention_days` (separate from `conversation_retention_days`). `EpisodicEventConsumer` has explicit `start()` and `stop()` methods. `start()` creates and stores the pruning task handle; `stop()` sets internal stop_event. Integration with lifecycle: Plan 33 S2 shutdown hook calls `consumer.stop()` before `MemoryGateway.flush()`. Pruning errors: log ERROR, continue (do not terminate consumer). **Cooperative shutdown**: consumer.stop() sets internal stop_event. The pruning loop checks stop_event at the start of each iteration. If stop_event is set, interrupt only the 1h sleep (via Event.set()), let any active prune transaction finish, then exit the loop. Do NOT use asyncio.Task.cancel() directly — this can inject cancellation into an active transaction. Add test: test_stop_during_active_prune_waits_for_commit, test_stop_event_interrupts_sleep_only. Background prune: `EpisodicEventConsumer.prune()` runs every 1h; deletes rows where `timestamp < now() - retention_days`. Exposed for testing. **EpisodicEventConsumer lifecycle hooks**: Register consumer.start() as non-critical startup hook and consumer.stop() as non-critical shutdown hook in Plan 33's HookRegistry (S4.2). consumer.stop() must complete BEFORE the critical MemoryGateway.flush() shutdown hook. Register these in S4.2 integration section. Add tests: test_consumer_start_registered_as_hook, test_consumer_stop_completes_before_flush.
S2.5: Test: `pytest app/sovereignai/tests/test_episodic_consumer.py -v` — `test_event_persisted`, `test_summary_truncated_500`, `test_retention_config`, `test_prune_scheduling_starts_on_start`, `test_prune_cancels_on_stop`, `test_prune_deletes_expired_records`, `test_prune_retention_boundary`

## S3 — Cross-Task Persistent Graph Memory (DEBT-9)

S3.1: Create `app/sovereignai/memory/persistent_graph.py` — `PersistentGraphMemory`; DI-owned singleton. Owned exclusively by `MemoryGateway` in `app/sovereignai/memory/gateway.py`.
S3.2: File-backed SQLite (`graph_memory.db`, separate file) using Plan 24 pattern; `PRAGMA journal_mode=WAL`, `busy_timeout=5000`. **v1**: single-process, single-asyncio-loop, aiosqlite (single connection, serialized by asyncio.Lock). Multi-process deferred to v2.
S3.3: Shared across tasks: entities, relations, provenance; lazy hydration. Performance budget: p99 < 500ms at 100k entities / 500k relations. Indexes: `(src_id, type)`, `(dst_id, type)`, `(type, name)`. MemoryGateway LRU query cache: TTL 1s, max 100 entries. Write-through invalidation on `merge()`. **Cache invalidation race**: in-flight query during invalidation may return stale data; acceptable for v1 — cache TTL is 1s. Query key hash: `hashlib.sha256(json.dumps([query_type, *sorted(params.items())], sort_keys=True, default=str).encode()).hexdigest()`.
S3.4: Merge strategy: entity dedup by name+type match. On collision: store both candidate UUIDs in `merge_conflicts` table; **newer timestamp wins for entity attributes**; both UUIDs preserved. **Canonical entity**: UUID with newer timestamp. **Tiebreaker**: identical timestamps → lexicographically smaller UUID wins. Timestamp source: server-assigned at merge time (`datetime.now(timezone.utc).isoformat()`). NOT adapter-supplied, NOT task-supplied. This ensures monotonic timestamps within a single-process server. **v1 limitation**: assumes single server clock; multi-server deployments would need clock synchronization. Relations re-attached atomically within merge transaction:
    ```sql
    UPDATE relations SET src_id = :canonical WHERE src_id = :non_canonical;
    UPDATE relations SET dst_id = :canonical WHERE dst_id = :non_canonical;
    DELETE FROM relations WHERE rowid NOT IN (
      SELECT MIN(rowid) FROM relations
      GROUP BY src_id, dst_id, type
    ) AND (src_id = :canonical OR dst_id = :canonical);
    ```
    Log re-linked count for both src and dst directions. Deduplicate relations after reattachment (delete duplicates keeping lowest rowid). Dedup covers **both directions**: relations where `src_id = :canonical` AND relations where `dst_id = :canonical` after reattachment. This ensures no duplicates are missed when two relations had different src but same dst that converged after reattachment. Self-loop handling: if canonical UUID appears as both src and dst after reattachment, retain the self-loop (it represents a valid reflexive relation). **Repeat-merge**: existing conflict record updated (newer candidate wins); no duplicate. **Operator resolution** via `/api/orchestrator/memory/conflicts` — v1: `resolution_status = "unresolved"` always.
S3.5: Conflict exposure: `GET /api/orchestrator/memory/conflicts` returns `MergeConflictDTO[]` sorted by `first_observed_at` descending. `resolution_status` field values: `"unresolved" | "suppressed_by_dedup"`. Paginated response, max_page_size=500, supports offset/limit per Plan 31 S4.2 AuditPage pattern.
S3.6: Write serialization: `asyncio.Lock` around `merge()`. Loop binding: `self._creation_loop` set to `None` in `__init__`; actual loop captured on first async operation (`load()` or `merge()`). Assert non-None at first use. **Loop mismatch failure**: raise `RuntimeError(f"MemoryGateway created on loop {self._creation_loop}, called from loop {asyncio.get_running_loop()}")` with WARN log. This is a programmer-error condition — callers should NOT catch it; treat as terminal. **Loop guarantee for flush**: `flush()` must be invoked from the same loop as `load()` and `merge()`. Plan 34 S4.2 registers the flush hook with Plan 33's HookRegistry, which executes hooks on the core process's event loop (same loop as `load()`). If the lifecycle manager runs on a different loop, the flush hook must be wrapped in `asyncio.run_coroutine_threadsafe()` — verify in integration test `test_flush_same_loop_as_load`.
S3.7: Test: `pytest app/sovereignai/tests/test_persistent_graph.py -v` — `test_merge_name_type_dedup`, `test_canonical_uuid_newer_wins`, `test_repeat_merge_updates_conflict`, `test_loop_mismatch_raises_runtime_error`, `test_cache_invalidation_on_merge`
S3.8: Benchmark test: `pytest app/sovereignai/tests/test_graph_memory_benchmark.py -v`. Two-tier benchmark gates:
    - **Normal execution gate** (S6.5, `small_scale` marker): 10k entities, 50k relations. Assert p99 < 50ms. This is the per-PR requirement. Expected runtime: <30s on CI hardware. If benchmark exceeds 60s, flag for review.
    - **Full benchmark** (requires `RUN_GRAPH_BENCHMARK=1` env var): 100k entities, 500k relations. Assert p99 < 500ms. This is the CI/nightly requirement.
    Scaling model: 10k p99 < 50ms is the normal gate; 100k benchmark runs only when explicitly enabled. Report: data size, host class, p50/p95/p99_ms. **Measurement methodology**: Use time.perf_counter() to measure each individual query latency. Collect N=100 samples per benchmark run. Compute p50/p95/p99 using statistics.quantiles (stdlib). Output structured log: BENCHMARK_RESULT size={N} host={class} p50={x}ms p95={y}ms p99={z}ms. Data generation time: <5s for 10k entities; <60s for 100k entities.

## S4 — Integration

S4.1: Librarian uses `MemoryGateway` for cross-task knowledge; `TaskGraphCache` for per-task ephemeral. MemoryGateway sole owner of PGM; no direct access outside MemoryComposer.
S4.2: Register lifecycle hooks (Plan 33 S2): startup = `MemoryGateway.load()` (non-critical, sets `is_ready()=True` on completion), shutdown = `MemoryGateway.flush()` (critical, sets `is_ready()=False`). Plan 34 is the **sole owner** of memory lifecycle hook registration. Plan 33 S5.1 defines the nullable protocol; Plan 34 registers the concrete hooks. Plan 33's composition test verifies registration: `assert memory_gateway in hook_registry.startup_hooks`. **Loop binding ownership**: If HookRegistry executes hooks on a different loop than MemoryGateway's creation loop, Plan 34's hook registration MUST wrap flush() in asyncio.run_coroutine_threadsafe(coro, target_loop). Plan 33's HookRegistry executes all hooks on the core process's main loop (same loop as load()). Plan 34 verifies same-loop execution in test_flush_same_loop_as_load. The wrapping responsibility belongs to Plan 34's registration code, not Plan 33's HookRegistry.
S4.3: EventBus wiring: `task.completed` → Librarian → MemoryGateway.merge (asyncio Lock). **Dedup** (branches on S0.4 outcome): **Primary branch** (event_sequence exists): dedup key `(task_id, event_type, event_sequence)`, monotonic per task. **Fallback branch** (no event_sequence): dedup key `(task_id, event_type, correlation_id)`. Collision: skip if key matches existing. Dedup store: SQLite table `merge_dedup(task_id TEXT, event_type TEXT, dedup_key TEXT, first_seen_at TEXT, PRIMARY KEY(task_id, event_type, dedup_key))` with 24h TTL. Dedup record inserted in same transaction as graph merge (atomic). On overflow (max 10k entries): evict oldest by `first_seen_at`, log WARN. Overflow counter: log every 100 skips.
S4.4: Test: `pytest app/sovereignai/tests/test_librarian_integration.py -v` — `test_task_completed_end_to_end`, `test_dedup_primary_branch_event_sequence`, `test_dedup_fallback_branch_correlation_id`, `test_dedup_persistent_across_restart`: (a) Create EpisodicEventConsumer, start(), emit event, assert dedup record exists. (b) consumer.stop(), await completion. (c) Create new EpisodicEventConsumer with same DB path, start(). (d) Emit duplicate event. (e) Assert merge NOT called (verify via mock call count). (f) Assert dedup table still contains original record; `test_overflow_evicts_oldest`, `test_overflow_counter_logged_every_100`

## S5 — API Exposure (AR1 Compliant)

S5.1: GET `/api/orchestrator/memory/graph` — query persistent graph via Orchestrator facade (entity search, relation traversal). Orchestrator facade delegates memory queries to Librarian, which uses MemoryGateway. Orchestrator does NOT import or receive MemoryGateway directly. DI injects MemoryGateway into Librarian (Plan 34 S4.1); Orchestrator calls Librarian methods for memory operations. One-directional: MemoryGateway → Librarian → Orchestrator facade. **Query limitations**: p99 < 500ms at 100k scale; no cross-task join queries in v1; single-tenant only. When `MemoryGateway` resolves to `None` (still loading), Plan 31 S3.6 returns 503 with `MemoryNotReadyResponse`. Plan 34 does not re-register routes; it only activates the backend service. Routes exist from Plan 31; backend binds via MemoryComposer.
S5.2: GET `/api/orchestrator/memory/episodic` — episodic event log via Orchestrator facade (time range, event type filter)
S5.3: GET `/api/orchestrator/memory/conflicts` — list merge conflicts. DTOs per Plan 31 S1.2 canonical names. Fields per `MergeConflictDTO`: `conflict_id, entity_name, entity_type, canonical_uuid, candidate_uuids: list[str], first_observed_at: str` (ISO 8601), `resolution_status: str`. Sorted descending by `first_observed_at`. Paginated response, max_page_size=500, supports offset/limit per Plan 31 S4.2 AuditPage pattern.
S5.4: Web DTOs per AR14: all names from Plan 31 S1.2 authoritative inventory. Plan 34 MUST use Plan 31 names. No core types returned.
S5.5: Test: `pytest app/web/tests/test_memory_api.py -v` — `test_graph_query_returns_dto`, `test_memory_not_ready_503`, `test_conflicts_sorted_fresh_first`, `test_episodic_time_range_filter`, `test_conflicts_pagination_offset_limit`, `test_conflicts_max_page_size_500`, `test_conflicts_stable_ordering`, `test_conflicts_resolution_status_dto_valid`

Plan 31 owns the Web-layer test (`test_memory_not_ready_503` verifying HTTP 503 + `MemoryNotReadyResponse` body). Plan 34 owns the backend test (`test_memory_is_ready_returns_true_after_load`, `test_memory_is_ready_returns_false_after_flush`). No overlap.

## S6 — AR Checks

S6.1: Add `check_librarian_no_backend_direct.py` — scan `app/sovereignai/workers/` for direct imports of `app/sovereignai/memory/persistent_graph.py` or `app/sovereignai/memory/gateway.py`. Workers MUST query Librarian, not memory backends. Audit target modules: all files under `app/sovereignai/workers/`.
S6.2: Add `check_graph_memory_persistence.py` — verify file-backed mode
S6.3: Add `check_memory_gateway_ownership.py` — verify MemoryGateway sole owner of PGM
S6.4: Add `check_memory_gateway_onedirectional.py` — verify gateway does not import/invoke Orchestrator
S6.5: Run `pytest .agent/executor/tests/test_document_hygiene.py -v AND pytest app/sovereignai/tests/test_graph_memory_benchmark.py -v -k small_scale. Both must pass as closing gate. **Coverage closing gate**: `pytest --cov=app/sovereignai/librarian --cov=app/sovereignai/memory --cov-report=term-missing app/sovereignai/tests/ -v --cov-fail-under=90`. Runs after document hygiene and benchmark as additional gate.

## Closing

Run `/close`