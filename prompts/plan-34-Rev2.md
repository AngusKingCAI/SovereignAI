Depends on: Plan 33 (Agent Lifecycle), Plan 22 (EventBus), Plan 24 (Graph Memory)
Vision principles: P1 (Core sacred), P2 (Pluggable), P9 (Observability), P13 (Strong and robust)
AR rules: AR1, AR2, AR8
OR rules: UOR-1, UOR-2
Open questions resolved: DD-34.1, DD-34.2, DD-34.3, DD-34.4, DD-34.5, DD-34.6
**Revision**: Rev2

## S0 — Opening

S0.1: Run `/open`
S0.2: Read `AGENTS.md` in full
S0.3: Read plan header AR rules from `.agent/executor/ARCHITECTURE.md`. Read plan header OR rules from `.agent/executor/OR_RULES.md`.
S0.4: Check `.agent/shared/DEBT.md` for deferred items.

## S1 — Librarian Event Handler (DEBT-6)

S1.1: Add `handle_event(self, event: TaskEvent)` to `app/sovereignai/librarian/librarian.py`
S1.2: Subscribe to: `task.created`, `task.updated`, `task.completed`, `task.failed`, `task.deleted` via Plan 22 EventBus
S1.3: On `task.completed`: extract entities, update knowledge graph via `PersistentGraphMemory`
S1.4: On `task.failed`: rollback partial graph updates from that task
S1.5: On `task.deleted`: garbage-collect entities from that task
S1.6: Per AR2: Librarian queries memory backends directly; workers query Librarian, not backends
S1.7: Test: `pytest app/sovereignai/tests/test_librarian_events.py -v`

## S2 — Episodic Event Consumer

S2.1: Create `app/sovereignai/memory/episodic_consumer.py` — `EpisodicEventConsumer`
S2.2: Subscribes to all `orchestrator.*` and `messaging.*` events
S2.3: Persists to episodic memory: event type, timestamp, correlation_id, summary (truncated to 500 chars, no raw payload)
S2.4: Retention: configurable via `BehaviorSettings.episodic_retention_days` (separate from `conversation_retention_days`)
S2.5: Test: `pytest app/sovereignai/tests/test_episodic_consumer.py -v`

## S3 — Cross-Task Persistent Graph Memory (DEBT-9)

S3.1: Create `app/sovereignai/memory/persistent_graph.py` — `PersistentGraphMemory`
S3.2: File-backed SQLite (`graph_memory.db`, separate file) using Plan 24 TaskGraphCache pattern; `PRAGMA journal_mode=WAL`, `PRAGMA busy_timeout=5000`
S3.3: Shared across all tasks: entities, relations, provenance
S3.4: Merge strategy: new task graph merged into persistent graph via entity deduplication (name+type match). On collision, log conflict with both entity UUIDs; newer timestamp wins
S3.5: Conflict resolution: newer timestamp wins; log merge conflicts via TraceEmitter per AR8
S3.6: Write serialization: asyncio Lock around `merge()` to prevent concurrent SQLite writes
S3.7: Test: `pytest app/sovereignai/tests/test_persistent_graph.py -v`

## S4 — Integration

S4.1: Librarian uses `PersistentGraphMemory` for cross-task knowledge; `TaskGraphCache` for per-task ephemeral
S4.2: Register lifecycle hooks (Plan 33 S2): startup = `PersistentGraphMemory.load()`, shutdown = `PersistentGraphMemory.flush()`
S4.3: EventBus wiring: `task.completed` → Librarian.handle_event → PersistentGraphMemory.merge (with asyncio Lock)
S4.4: Test: `pytest app/sovereignai/tests/test_librarian_integration.py -v`

## S5 — API Exposure (AR1 Compliant)

S5.1: GET `/api/orchestrator/memory/graph` — query persistent graph via Orchestrator facade (entity search, relation traversal)
S5.2: GET `/api/orchestrator/memory/episodic` — query episodic event log via Orchestrator facade (time range, event type filter)
S5.3: Web DTOs per AR14; no core types returned
S5.4: Test: `pytest app/web/tests/test_memory_api.py -v`

## S6 — AR Checks

S6.1: Add `check_librarian_no_backend_direct.py` — verify workers query Librarian, not memory backends
S6.2: Add `check_graph_memory_persistence.py` — verify file-backed mode used for persistent graph
S6.3: Run `pytest .agent/executor/tests/test_document_hygiene.py -v`

## Closing

Run `/close`
