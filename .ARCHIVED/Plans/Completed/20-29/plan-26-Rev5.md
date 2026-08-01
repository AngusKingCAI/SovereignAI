Depends on: Plans 22-24, Plan 28 (Options, soft runtime dependency — S3.4 reads BehaviorSettings with fallback)
Vision principles: P8 (UIs are separate processes), P11 (Quality), P14 (Modularity)
Open questions resolved: DD-26.6, DD-26.7, DD-26.8
**Revision**: Rev5

## S0 — Opening

S0.0: Clone latest repo. Verify Plans 22-24 completed.
S0.1: Run `/open`
S0.2: Read `AGENTS.md`, `PRINCIPLES.md`
S0.3: Read `.agent/architect/documents/SovereignAI_Orchestrator_Spec.md`
S0.4: Run baseline tests: `pytest app/sovereignai/tests/ -x --tb=short`

## S1 — IntentClassifier

S1.1: Create `app/sovereignai/orchestrator/classifier.py` — `IntentClassifier` Protocol
S1.2: Implement `RuleBasedClassifier` (keywords → department routing)
S1.3: Implement `LLMClassifier` — takes `llm_client: LLMClientProtocol` via DI, 10s timeout, fallback to `RuleBasedClassifier` on timeout/error
S1.4: Fallback: unknown intent → Orchestrator emits `orchestrator.clarification_needed` event to Owner via EventBus
S1.5: Test: `pytest app/sovereignai/tests/test_orchestrator_classifier.py -v`

## S2 — DepartmentRouter

S2.1: Create `app/sovereignai/orchestrator/router.py` — `DepartmentRouter`
S2.2: Map classifier outputs to department Manager instances (from Plan 24 registry)
S2.3: Handle department lifecycle: init on first use, graceful shutdown
S2.4: Test: `pytest app/sovereignai/tests/test_orchestrator_router.py -v`

## S3 — ConversationState

S3.1: Create `app/sovereignai/orchestrator/state.py` — `ConversationState` dataclass
S3.2: Track: message history, active department, pending clarifications, session metadata
S3.3: Persist to SQLite (`orchestrator_state.db`, separate file) using Plan 24's WAL+asyncio pattern
S3.4: Retention: auto-purge sessions older than `conversation_retention_days` (default 7). Read from Plan 28 BehaviorSettings at startup via `OptionsBackend.get('conversation_retention_days')` if Plan 28 available. Fallback: catch `ImportError`, `AttributeError`, `KeyError`, `sqlite3.Error`, `ValueError`, `TypeError`, or `None` return — use default 7 and log `plan_28_behavior_settings_unavailable` with `error_class=type(e).__name__`. Startup MUST NOT fail. Purge task wraps `sqlite3.DatabaseError` in `try/except`, logs at ERROR, continues main loop. After 3 consecutive purge failures, emit `orchestrator.purge.failing` event with last error class; reset counter on first success. Configuration loaded at startup; refresh on `options.changed` event. Purge uses current effective value; does not retroactively alter timestamps.
S3.5: Test: `pytest app/sovereignai/tests/test_orchestrator_state.py -v`

## S4 — OrchestratorFacade

S4.1: Create `app/sovereignai/orchestrator/facade.py` — `Orchestrator` class
S4.2: Create `app/sovereignai/orchestrator/__init__.py` — re-export `Orchestrator` from `facade.py` only; no logic. Do NOT re-export persistence internals.
S4.3: Compose: classifier + router + state + result translator
S4.4: Method: `async def handle_message(self, user_message: str) -> str`
S4.5: Result translator: department output → human-readable (no raw JSON to Owner)
S4.6: Test: `pytest app/sovereignai/tests/test_orchestrator_facade.py -v`

## S5 — Integration with EventBus

S5.1: Subscribe Orchestrator to `owner.message.received` events (Plan 22 EventBus schema)
S5.2: Publish `orchestrator.response.ready` and `orchestrator.clarification_needed` events
S5.3: Test: `pytest app/sovereignai/tests/test_orchestrator_events.py -v`

## S6 — AR Checks

S6.1: Add `check_orchestrator_no_react.py` — verify Orchestrator never imports ReActLoop
S6.2: Add `check_orchestrator_single_entry.py` — verify only Orchestrator talks to Owner
S6.3: Run `pytest .agent/executor/tests/test_document_hygiene.py -v`

## Closing

Run `/close`
