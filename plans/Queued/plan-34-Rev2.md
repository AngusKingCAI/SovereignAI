Depends on: Plan 33 (Agent Lifecycle), Plan 22 (EventBus), Plan 24 (Graph Memory)
Vision principles: P1 (Core sacred), P2 (Pluggable), P9 (Observability), P13 (Strong and robust)
AR rules: AR1, AR2, AR8
OR rules: UOR-1, UOR-2
Open questions resolved: DD-34.1, DD-34.2, DD-34.3, DD-34.4
**Revision**: Rev2

## S0 — Opening

S0.1: Run `/open`
S0.2: Read `AGENTS.md` in full
S0.3: Read plan header AR rules from `.agent/executor/ARCHITECTURE.md`. Read plan header OR rules from `.agent/executor/OR_RULES.md`.
S0.4: Check `.agent/shared/DEBT.md` for deferred items.

## S1 — Librarian Event Handler (DEBT-6)

S1.1: Add `handle_event(self, event: TaskEvent)` to `app/sovereignai/librarian/librarian.py`
S1.2: Subscribe to: `task.created`, `task.updated`, `task.completed` via Plan 22 EventBus
S1.3: On `task.completed`: extract entities, update knowledge graph via `GraphMemoryBackend`
S1.4: Per AR2: Librarian queries memory backends directly; workers query Librarian, not backends
S1.5: Event processing idempotency: track processed event IDs to prevent duplicate processing
S1.6: Test: `pytest app/sovereignai/tests/test_librarian_events.py -v`

## S2 — Episodic Event Consumer

S2.1: Create `app/sovereignai/memory/episodic_consumer.py` — `EpisodicEventConsumer`
S2.2: Subscribes to all `orchestrator.*` and `messaging.*` events
S2.3: Structured event format: wide events pattern with high cardinality, high dimensionality, context-rich fields
S2.4: Persists to episodic memory: event type, timestamp, correlation_id, summary (not raw payload)
S2.5: Event sampling strategy: full fidelity for error events and business-critical transactions, sampling for high-volume info events
S2.6: Retention: configurable via `BehaviorSettings.conversation_retention_days` (Plan 28)
S2.7: Consumer lag monitoring: track processing time, error rates, and consumer lag for backpressure detection
S2.8: Dead-letter queue: failed events sent to DLQ for manual inspection and replay capability
S2.9: Test: `pytest app/sovereignai/tests/test_episodic_consumer.py -v`

## S3 — Cross-Task Persistent Graph Memory (DEBT-9)

S3.1: Create `app/sovereignai/memory/persistent_graph.py` — `PersistentGraphMemory`
S3.2: File-backed SQLite (`graph_memory.db`, separate file) using Plan 24 TaskGraphCache pattern
S3.3: SQLite configuration: enable WAL mode for concurrent access, set appropriate journal mode
S3.4: Shared across all tasks: entities, relations, provenance
S3.5: Merge strategy: new task graph merged into persistent graph via entity deduplication (name+type match)
S3.6: Conflict resolution: use SQLite's built-in ON CONFLICT clauses or UPSERT for transactional consistency; newer timestamp wins as fallback
S3.7: Indexing strategy: explicit indexes on entity names, types, and timestamps for query performance
S3.8: Merge conflict logging: log merge conflicts via TraceEmitter per AR8 with operational guidance
S3.9: Test: `pytest app/sovereignai/tests/test_persistent_graph.py -v`

## S4 — Integration

S4.1: Librarian uses `PersistentGraphMemory` for cross-task knowledge; `TaskGraphCache` for per-task ephemeral
S4.2: On agent startup (Plan 33), load persistent graph into memory; on shutdown, flush to disk with explicit close
S4.3: EventBus wiring: `task.completed` → Librarian.handle_event → PersistentGraphMemory.merge
S4.4: SQLite flush coordination: Plan 33's shutdown sequence calls Plan 34's flush operation before closing SQLite
S4.5: Event schema evolution: implement schema registry for backward compatibility as event schemas change over time
S4.6: Test: `pytest app/sovereignai/tests/test_librarian_integration.py -v`

## S5 — API Exposure

S5.1: GET `/api/v1/memory/graph` — query persistent graph (entity search, relation traversal)
S5.2: GET `/api/v1/memory/episodic` — query episodic event log (time range, event type filter)
S5.3: Web DTOs per AR14; no core types returned
S5.4: Test: `pytest app/web/tests/test_memory_api.py -v`

## S6 — AR Checks

S6.1: Add `check_librarian_no_backend_direct.py` — verify workers query Librarian, not memory backends
S6.2: Add `check_graph_memory_persistence.py` — verify file-backed mode used for persistent graph
S6.3: Add `check_consumer_idempotency.py` — verify event consumer implements idempotency patterns
S6.4: Add `check_dead_letter_queue.py` — verify failed events sent to DLQ for replay
S6.5: Run `pytest .agent/executor/tests/test_document_hygiene.py -v`

## Closing

Run `/close`
