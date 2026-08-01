Depends on: Plan 33 (Agent Lifecycle), Plan 22 (EventBus), Plan 24 (Graph Memory)
Vision principles: P1 (Core sacred), P2 (Pluggable), P9 (Observability), P13 (Strong and robust)
AR rules: AR1, AR2, AR8
OR rules: UOR-1, UOR-2
Open questions resolved: DD-34.1, DD-34.2, DD-34.3, DD-34.4, DD-34.5, DD-34.6, DD-34.7
**Revision**: Rev12

## Executor Manifest

**Plan**: 34
**Phases**: 6 (S0–S6)
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
S0.4: **Prerequisite check**: verify Plan 22 TaskEvent schema includes monotonic `event_sequence` per task. Record outcome in execution log. If missing → use fallback dedup key `(task_id, event_type, correlation_id)` per S4.3 branch. No Plan 22 modification required.

## S1 — Librarian Event Handler (DEBT-6)

S1.1: Add `handle_event(self, event: TaskEvent)` to `app/sovereignai/librarian/librarian.py`
S1.2: Subscribe to: `task.created`, `task.updated`, `task.completed`, `task.failed`, `task.deleted` via Plan 22 EventBus. Prerequisite: `event_sequence` per S0.4.
S1.3: On `task.completed`: extract entities, update knowledge graph via `MemoryGateway` (injected, not imported directly). MemoryGateway proxies to `PersistentGraphMemory`.
S1.4: On `task.failed`: rollback via `MemoryGateway.rollback(task_id: str) -> bool`. Returns `True` if merge was in-progress (transaction not committed) and rolled back; returns `False` if already committed or no transaction. `merge()` wraps all inserts/updates in single `aiosqlite` transaction entered after `async with lock:`. `asyncio.Lock` ensures only one merge at a time. `rollback(task_id)` acquires same lock, checks for active transaction owned by task_id, executes ROLLBACK if in-progress (returns True), returns False if committed or no transaction. **Post-commit v1 limitation**: if `task.completed` already committed and `task.failed` arrives (out-of-order), rollback returns False, graph contains entities from failed task. Log WARN with task_id. Operator review in v2 via `/api/orchestrator/memory/conflicts`. Accept inconsistency in v1.
S1.5: On `task.deleted`: garbage-collect from per-task ephemeral storage only. Persistent graph entities are shared cross-task and NOT deleted. Provenance reference counting deferred to v2. Documented v1 limitation.
S1.6: Per AR2: Librarian is the sole core-side consumer of memory backends (via MemoryGateway injection); workers query Librarian, not backends directly.
S1.7: Test: `pytest app/sovereignai/tests/test_librarian_events.py -v` — `test_task_completed_updates_graph`, `test_task_failed_rollback_in_progress`, `test_task_failed_post_commit_returns_false`, `test_task_deleted_ephemeral_only`

## S2 — Episodic Event Consumer

S2.1: Create `app/sovereignai/memory/episodic_consumer.py` — `EpisodicEventConsumer`
S2.2: Subscribes to all `orchestrator.*` and `messaging.*` events
S2.3: Persists: event type, timestamp, correlation_id, summary (truncated 500 chars, `VARCHAR(500)`); no raw payload
S2.4: Retention: configurable via `BehaviorSettings.episodic_retention_days` (separate from `conversation_retention_days`)
S2.5: Test: `pytest app/sovereignai/tests/test_episodic_consumer.py -v` — `test_event_persisted`, `test_summary_truncated_500`, `test_retention_config`

## S3 — Cross-Task Persistent Graph Memory (DEBT-9)

S3.1: Create `app/sovereignai/memory/persistent_graph.py` — `PersistentGraphMemory`; DI-owned singleton. Owned exclusively by `MemoryGateway` in `app/sovereignai/memory/gateway.py`.
S3.2: File-backed SQLite (`graph_memory.db`, separate file) using Plan 24 pattern; `PRAGMA journal_mode=WAL`, `busy_timeout=5000`. **v1**: single-process, single-asyncio-loop, aiosqlite (single connection, serialized by asyncio.Lock). Multi-process deferred to v2.
S3.3: Shared across tasks: entities, relations, provenance; lazy hydration. Performance budget: p99 < 500ms at 100k entities / 500k relations. Indexes: `(src_id, type)`, `(dst_id, type)`, `(type, name)`. MemoryGateway LRU query cache: TTL 1s, max 100 entries. Write-through invalidation on `merge()`. **Cache invalidation race**: if a query is in-flight while `merge()` invalidates the cache, in-flight result may return stale data. This is acceptable for v1 — cache TTL is 1s, staleness window is bounded. No serialization of reads around cache invalidation. Query key hash: `hashlib.sha256(json.dumps([query_type, *sorted(params.items())], sort_keys=True, default=str).encode()).hexdigest()`. Note: `default=str` for safety; query params should be simple types.
S3.4: Merge strategy: entity dedup by name+type match. On collision: store both candidate UUIDs in `merge_conflicts` table; **newer timestamp wins for entity attributes**; both UUIDs preserved. **Canonical entity**: the UUID with the newer timestamp becomes the canonical record. **Tiebreaker**: identical timestamps → lexicographically smaller UUID wins. Existing/new relations re-attached atomically within merge transaction: `UPDATE relations SET src_id=canonical WHERE src_id=non_canonical; UPDATE relations SET dst_id=canonical WHERE dst_id=non_canonical`. Log re-linked count. **Repeat-merge behavior**: if same name+type collision seen again, existing conflict record is updated (newer candidate wins); no duplicate conflict created. **Operator resolution** via `/api/orchestrator/memory/conflicts` — v1: `resolution_status = "unresolved"` always (no resolution API until future plan).
S3.5: Conflict exposure: `GET /api/orchestrator/memory/conflicts` returns `MergeConflictDTO[]` sorted by `first_observed_at` descending (freshest first). Stale recede. `resolution_status` field values: `"unresolved" | "suppressed_by_dedup"`.
S3.6: Write serialization: `asyncio.Lock` around `merge()`. Store `self._creation_loop` in `__init__`; assert loop match at acquisition. **Loop mismatch failure**: raise `RuntimeError(f"MemoryGateway created on loop {self._creation_loop}, called from loop {asyncio.get_running_loop()}")` with WARN log. This is a programmer-error condition — callers should NOT catch it; treat as terminal. `async with lock:` + `try/finally` ensures release on cancellation.
S3.7: Test: `pytest app/sovereignai/tests/test_persistent_graph.py -v` — `test_merge_name_type_dedup`, `test_canonical_uuid_newer_wins`, `test_repeat_merge_updates_conflict`, `test_loop_mismatch_raises_runtime_error`, `test_cache_invalidation_on_merge`
S3.8: Benchmark test: `pytest app/sovereignai/tests/test_graph_memory_benchmark.py -v` — `@pytest.mark.benchmark`; bulk insert 100k entities/500k relations; realistic queries; p99 ≤ 500ms. Per-PR: `@pytest.mark.small_scale` (10k entities). CI: small_scale default; benchmark only with `RUN_GRAPH_BENCHMARK=1`. **Benchmark gate**: full 100k benchmark is quarterly/CI-scheduled activity outside plan execution scope; S6.5 closing gate requires only small_scale (10k). Report: data size, host class (CI/local/perf), p50_ms, p95_ms, p99_ms; assert p99 < 500ms at 100k scale.

## S4 — Integration

S4.1: Librarian uses `MemoryGateway` for cross-task knowledge; `TaskGraphCache` for per-task ephemeral. MemoryGateway sole owner of PGM; no direct access outside MemoryComposer.
S4.2: Register lifecycle hooks (Plan 33 S2): startup = `MemoryGateway.load()` (non-critical, sets `is_ready()=True` on completion), shutdown = `MemoryGateway.flush()` (critical, sets `is_ready()=False`).
S4.3: EventBus wiring: `task.completed` → Librarian → MemoryGateway.merge (asyncio Lock). **Dedup** (branches on S0.4 outcome):
  - **Primary branch** (event_sequence exists): dedup key `(task_id, event_type, event_sequence)`. `event_sequence` is monotonic per task.
  - **Fallback branch** (no event_sequence): dedup key `(task_id, event_type, correlation_id)`. Weaker guarantee: `correlation_id` may not be universally unique. Collision behavior: if key matches existing entry, skip. `event_sequence` absence recorded in execution log.
  - Shared: 24h TTL, max 10k entries per subscriber. On overflow: **evict oldest** (LRU) regardless of TTL validity. Log WARN if evicted entry was still valid. Prioritizes new event processing over dedup accuracy. Overflow counter: log every 100 skips (not per-skip) to prevent log spam.
S4.4: Test: `pytest app/sovereignai/tests/test_librarian_integration.py -v` — `test_task_completed_end_to_end`, `test_dedup_primary_branch_event_sequence`, `test_dedup_fallback_branch_correlation_id`, `test_overflow_evicts_oldest`, `test_overflow_counter_logged_every_100`

## S5 — API Exposure (AR1 Compliant)

S5.1: GET `/api/orchestrator/memory/graph` — query persistent graph via Orchestrator facade (entity search, relation traversal). Orchestrator delegates to `MemoryGateway` interface (not direct Librarian import). One-directional: gateway does not import Orchestrator. **Query limitations**: p99 < 500ms at 100k scale; no cross-task join queries in v1; single-tenant only. When `MemoryGateway` resolves to `None` (still loading), Plan 31 S3.6 returns 503 with `MemoryNotReadyResponse`.
S5.2: GET `/api/orchestrator/memory/episodic` — episodic event log via Orchestrator facade (time range, event type filter)
S5.3: GET `/api/orchestrator/memory/conflicts` — list merge conflicts. DTOs per Plan 31 S1.2 canonical names. Fields per `MergeConflictDTO`: `conflict_id, entity_name, entity_type, canonical_uuid, candidate_uuids: list[str], first_observed_at: str` (ISO 8601), `resolution_status: str`. Sorted descending by `first_observed_at`.
S5.4: Web DTOs per AR14: all names from Plan 31 S1.2 authoritative inventory. Plan 34 MUST use Plan 31 names. No core types returned.
S5.5: Test: `pytest app/web/tests/test_memory_api.py -v` — `test_graph_query_returns_dto`, `test_memory_not_ready_503`, `test_conflicts_sorted_fresh_first`, `test_episodic_time_range_filter`

## S6 — AR Checks

S6.1: Add `check_librarian_no_backend_direct.py` — verify workers query Librarian, not memory backends
S6.2: Add `check_graph_memory_persistence.py` — verify file-backed mode
S6.3: Add `check_memory_gateway_ownership.py` — verify MemoryGateway sole owner of PGM
S6.4: Add `check_memory_gateway_onedirectional.py` — verify gateway does not import/invoke Orchestrator
S6.5: Run `pytest .agent/executor/tests/test_document_hygiene.py -v`

## Closing

Run `/close`
