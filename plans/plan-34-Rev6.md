Depends on: Plan 33 (Agent Lifecycle), Plan 22 (EventBus), Plan 24 (Graph Memory)
Vision principles: P1 (Core sacred), P2 (Pluggable), P9 (Observability), P13 (Strong and robust)
AR rules: AR1, AR2, AR8
OR rules: UOR-1, UOR-2
Open questions resolved: DD-34.1, DD-34.2, DD-34.3, DD-34.4, DD-34.5, DD-34.6, DD-34.7
**Revision**: Rev6

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

**Governance files**: Do not modify `AI_HANDOFF.md`, `AGENTS.md`, `PRINCIPLES.md`, `OR_RULES.md`, `PLANS.md`, `DEBT.md`.
**Commit message**: `feat(memory): add persistent graph memory, episodic consumer, and librarian event handler`

## S0 — Opening

S0.1: Run `/open`
S0.2: Read `AGENTS.md` in full. Read `PRINCIPLES.md` in full.
S0.3: Read plan header AR rules from `.agent/executor/ARCHITECTURE.md`. Read plan header OR rules from `.agent/executor/OR_RULES.md`.
S0.4: Check `.agent/shared/DEBT.md` for deferred items.

## S1 — Librarian Event Handler (DEBT-6)

S1.1: Add `handle_event(self, event: TaskEvent)` to `app/sovereignai/librarian/librarian.py`
S1.2: Subscribe to: `task.created`, `task.updated`, `task.completed`, `task.failed`, `task.deleted` via Plan 22 EventBus
S1.3: On `task.completed`: extract entities, update knowledge graph via `MemoryGateway` (injected, not imported directly). MemoryGateway proxies to `PersistentGraphMemory`.
S1.4: On `task.failed`: rollback partial graph updates from that task
S1.5: On `task.deleted`: garbage-collect entities from that task's **per-task ephemeral storage only**. Persistent graph entities are shared cross-task knowledge and are NOT deleted on task deletion. Provenance-based reference counting deferred to v2. Documented v1 limitation: "Task deletion removes ephemeral task state only. Persistent graph entities accumulate until manual cleanup or v2 provenance tracking."
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
S3.2: File-backed SQLite (`graph_memory.db`, separate file) using Plan 24 TaskGraphCache pattern; `PRAGMA journal_mode=WAL`, `PRAGMA busy_timeout=5000`
S3.3: Shared across all tasks: entities, relations, provenance; lazy hydration (query on demand, not full load into memory). Query performance budget: p99 latency < 500ms at 100k entities / 500k relations. Index strategy: `(src_id, type)`, `(dst_id, type)`, `(type, name)`. MemoryGateway implements LRU query cache (TTL 1s, max 100 entries) to absorb TUI polling storms. First query triggers lazy load; subsequent queries hit cache or SQLite.
S3.4: Merge strategy: new task graph merged into persistent graph via entity deduplication (name+type match). On collision, log conflict with both entity UUIDs; newer timestamp wins
S3.5: Conflict resolution: newer timestamp wins; log merge conflicts via TraceEmitter per AR8
S3.6: Write serialization: `asyncio.Lock` around `merge()`; document loop-binding constraint (v1 single-loop only). Lock acquisition uses `try/finally` to ensure release on coroutine cancellation during shutdown. Documented: "The merge coroutine must use `async with lock:` or equivalent `try/finally` to prevent lock leak on cancellation."
S3.7: Test: `pytest app/sovereignai/tests/test_persistent_graph.py -v`
S3.8: Test: `pytest app/sovereignai/tests/test_graph_memory_query_latency.py -v` — insert 100k entities and 500k relations, run realistic queries (entity search, relation traversal), confirm p99 latency ≤ 500ms. If fixture generation is too slow for CI, document: "100k test validates performance budget; 10k test runs per-PR for correctness. Quarterly benchmark validates 100k scale."

## S4 — Integration

S4.1: Librarian uses `MemoryGateway` for cross-task knowledge; `TaskGraphCache` for per-task ephemeral. MemoryGateway is the single owner of PersistentGraphMemory; no direct PGM access outside MemoryGateway.
S4.2: Register lifecycle hooks (Plan 33 S2): startup = `MemoryGateway.load()` (non-critical — system starts without memory, routes return 503 until loaded), shutdown = `MemoryGateway.flush()` (critical — flush failure aborts shutdown stage)
S4.3: EventBus wiring: `task.completed` → Librarian.handle_event → MemoryGateway.merge (with asyncio Lock). Subscriber-side dedup: each subscriber (Librarian, EpisodicConsumer) maintains its own dedup set keyed by `(task_id, event_type, event_sequence)` with 24h TTL. `event_sequence` is monotonic per task, assigned by the event producer. Redelivery of same sequence is deduped; new sequence numbers pass through. No Plan 22 modification required.
S4.4: Test: `pytest app/sovereignai/tests/test_librarian_integration.py -v`

## S5 — API Exposure (AR1 Compliant)

S5.1: GET `/api/orchestrator/memory/graph` — query persistent graph via Orchestrator facade (entity search, relation traversal); Orchestrator delegates to `MemoryGateway` interface (not direct Librarian import). MemoryGateway defined in `app/sovereignai/memory/gateway.py`; owned by `MemoryComposer` per Plan 33 S5.3. One-directional: gateway exposes read/query API to Orchestrator; does not allow persistence layers to invoke Orchestrator.
S5.2: GET `/api/orchestrator/memory/episodic` — query episodic event log via Orchestrator facade (time range, event type filter)
S5.3: Web DTOs per AR14; no core types returned
S5.4: Test: `pytest app/web/tests/test_memory_api.py -v`

## S6 — AR Checks

S6.1: Add `check_librarian_no_backend_direct.py` — verify workers query Librarian, not memory backends
S6.2: Add `check_graph_memory_persistence.py` — verify file-backed mode used for persistent graph
S6.3: Add `check_memory_gateway_ownership.py` — verify MemoryGateway is sole owner of PGM, no direct PGM injection outside MemoryComposer
S6.4: Add `check_memory_gateway_onedirectional.py` — verify gateway does not import or invoke Orchestrator
S6.5: Run `pytest .agent/executor/tests/test_document_hygiene.py -v`

## Closing

Run `/close`
