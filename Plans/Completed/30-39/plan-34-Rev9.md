Depends on: Plan 33 (Agent Lifecycle), Plan 22 (EventBus), Plan 24 (Graph Memory)
Vision principles: P1 (Core sacred), P2 (Pluggable), P9 (Observability), P13 (Strong and robust)
AR rules: AR1, AR2, AR8
OR rules: UOR-1, UOR-2
Open questions resolved: DD-34.1, DD-34.2, DD-34.3, DD-34.4, DD-34.5, DD-34.6, DD-34.7
Optional forward dependency: Plan 31 (Web API) — Plan 34 registers memory endpoints; Plan 31 owns DTO inventory.
**Revision**: Rev9

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
S0.4: Verify Plan 22 TaskEvent schema includes `event_sequence: int` (monotonic per task). If missing: document fallback — subscriber dedup uses `(task_id, event_type, correlation_id)`, cross-subscriber dedup becomes impossible. Record outcome in execution log.

## S1 — Librarian Event Handler (DEBT-6)

S1.1: Add `handle_event(self, event: TaskEvent)` to `app/sovereignai/librarian/librarian.py`
S1.2: Subscribe to: `task.created`, `task.updated`, `task.completed`, `task.failed`, `task.deleted` via Plan 22 EventBus. Dedup key per S0.4 outcome.
S1.3: On `task.completed`: extract entities, update knowledge graph via `MemoryGateway` (injected, not imported directly). MemoryGateway proxies to `PersistentGraphMemory`.
S1.4: On `task.failed`: rollback **only if merge is in-progress** (transaction not yet committed). `merge()` wraps all inserts/updates in a single `aiosqlite` transaction entered **after** `async with lock:`. On failure mid-merge, transaction rolled back, graph returns to pre-merge state. **Post-commit rollback not supported in v1**: if `task.failed` arrives after a prior `task.completed` already committed the merge, log warning `lifecycle.merge.rollback_impossible` and do NOT modify shared graph state. Documented v1 limitation.
S1.5: On `task.deleted`: garbage-collect entities from that task's **per-task ephemeral storage only**. Persistent graph entities are shared cross-task knowledge and NOT deleted on task deletion. Provenance-based reference counting deferred to v2.
S1.6: Per AR2: Librarian queries memory backends directly; workers query Librarian, not backends
S1.7: Test: `pytest app/sovereignai/tests/test_librarian_events.py -v`

## S2 — Episodic Event Consumer

S2.1: Create `app/sovereignai/memory/episodic_consumer.py` — `EpisodicEventConsumer`
S2.2: Subscribes to all `orchestrator.*` and `messaging.*` events
S2.3: Persists to episodic memory: event type, timestamp, correlation_id, summary (truncated to 500 chars, enforced by schema `VARCHAR(500)`); no raw payload
S2.4: Retention: configurable via `BehaviorSettings.episodic_retention_days` (separate from `conversation_retention_days`)
S2.5: Test: `pytest app/sovereignai/tests/test_episodic_consumer.py -v`

## S3 — Cross-Task Persistent Graph Memory (DEBT-9)

S3.1: Create `app/sovereignai/memory/persistent_graph.py` — `PersistentGraphMemory`; DI-owned singleton, not global. Owned exclusively by `MemoryGateway` in `app/sovereignai/memory/gateway.py`.
S3.2: File-backed SQLite (`graph_memory.db`, separate file) using Plan 24 TaskGraphCache pattern; `PRAGMA journal_mode=WAL`, `PRAGMA busy_timeout=5000`. **v1 access model**: single-process, single-asyncio-loop.
S3.3: Shared across all tasks: entities, relations, provenance; lazy hydration. Query performance budget: p99 < 500ms at 100k entities / 500k relations. Index strategy: `(src_id, type)`, `(dst_id, type)`, `(type, name)`. MemoryGateway LRU query cache: max 100 entries, TTL 1s, write-through invalidation on `merge()`. **Cache key**: `hashlib.sha256(json.dumps([query_type, *sorted(params.items())], sort_keys=True, default=str).encode()).hexdigest()` — deterministic across restarts. First query triggers lazy load.
S3.4: Merge strategy: name+type dedup. On collision, store both UUIDs + provenance in `merge_conflicts` table; newer timestamp wins for attributes. **Conflict retention**: prune on startup, delete conflicts older than `BehaviorSettings.conflict_retention_days` (default 90). Expose via `GET /api/orchestrator/memory/conflicts`.
S3.5: Write serialization: `asyncio.Lock` around `merge()`. Store `self._creation_loop = asyncio.get_running_loop()` in `MemoryGateway.__init__`; assert `asyncio.get_running_loop() is self._creation_loop` at lock acquisition — raises `RuntimeError` with both loop IDs on mismatch. Lock acquired via `async with lock:` with `try/finally` for cancellation safety.
S3.6: Test: `pytest app/sovereignai/tests/test_persistent_graph.py -v`
S3.7: Test: `pytest app/sovereignai/tests/test_graph_memory_query_latency.py -v` — `@pytest.mark.benchmark`; session-scoped fixture in `conftest.py` inserts 100k entities + 500k relations. Confirm p99 ≤ 500ms. Per-PR: `@pytest.mark.small_scale` with 10k. CI: small_scale default; benchmark only with `RUN_GRAPH_BENCHMARK=1`.

## S4 — Integration

S4.1: Librarian uses `MemoryGateway` for cross-task knowledge; `TaskGraphCache` for per-task ephemeral. MemoryGateway is sole owner of PersistentGraphMemory; no direct PGM access outside MemoryComposer.
S4.2: Register lifecycle hooks (Plan 33 S2): startup = `MemoryGateway.load()` (non-critical — 503 until loaded), shutdown = `MemoryGateway.flush()` (critical — flush failure marks stage FAILED, continues remaining teardown).
S4.3: EventBus wiring: `task.completed` → Librarian.handle_event → MemoryGateway.merge. Subscriber dedup: each subscriber maintains own dedup `OrderedDict` (max 10k entries, LRU eviction by insertion order). Key: `(task_id, event_type, event_sequence)` (or S0.4 fallback). **TTL**: on each dedup check, prune entries older than 24h. On overflow (10k hit, oldest still <24h): log WARN, skip insertion, let event pass through (consumer must handle idempotently). `event_sequence` per S0.4 outcome.
S4.4: Test: `pytest app/sovereignai/tests/test_librarian_integration.py -v`

## S5 — API Exposure (AR1 Compliant)

S5.1: GET `/api/orchestrator/memory/graph` — query via Orchestrator facade (entity search, relation traversal); Orchestrator delegates to MemoryGateway (not direct Librarian import). One-directional: gateway exposes read/query to Orchestrator; does not invoke Orchestrator. Query limits: p99 < 500ms, no cross-task joins in v1, single-tenant only. **Performance note**: documented in response header `X-Query-Ms`.
S5.2: GET `/api/orchestrator/memory/episodic` — time range, event type filter
S5.3: GET `/api/orchestrator/memory/conflicts` — unresolved merge conflicts (resolution_status = PENDING). `MergeConflictDTO` schema: `{task_id, entity_name, entity_type, candidate_uuids: [older, newer], older_timestamp, newer_timestamp, resolution_status}`. v1 always PENDING; operator review via CLI/future admin UI.
S5.4: Web DTOs per AR14 (canonical names per Plan 31 S1.2): `GraphEntityDTO`, `GraphRelationDTO`, `GraphQueryRequest`, `GraphQueryResponse`, `EpisodicEventDTO`, `EpisodicQueryRequest`, `EpisodicQueryResponse`, `MergeConflictDTO`; no core types. Plan 31 S1.2 inventory is authoritative — Plan 34 MUST use those names.
S5.5: Test: `pytest app/web/tests/test_memory_api.py -v`

## S6 — AR Checks

S6.1: Add `check_librarian_no_backend_direct.py` — verify workers query Librarian, not backends
S6.2: Add `check_graph_memory_persistence.py` — verify file-backed mode
S6.3: Add `check_memory_gateway_ownership.py` — verify MemoryGateway sole owner of PGM
S6.4: Add `check_memory_gateway_onedirectional.py` — verify gateway does not invoke Orchestrator
S6.5: Run `pytest .agent/executor/tests/test_document_hygiene.py -v`

## Closing

Run `/close`
