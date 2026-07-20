Depends on: Plan 26 (Orchestrator), Plan 22 (EventBus), Plan 24 (DepartmentManager registry, audit database)
Vision principles: P8 (UIs are separate processes), P11 (Quality), P14 (Modularity)
Open questions resolved: DD-27.1
**Revision**: Rev5

## S0 — Opening

S0.0: Clone latest repo. Verify Plan 26 completed.
S0.1: Run `/open`
S0.2: Read `AGENTS.md`, `PRINCIPLES.md`
S0.3: Read `.agent/architect/documents/SovereignAI_Cross_Department_Messaging_Design_v1.0.md`
S0.4: Run baseline: `pytest app/sovereignai/tests/test_orchestrator_*.py -v`

## S1 — Message Schema

S1.1: Create `app/sovereignai/messaging/schema.py` — `CrossDepartmentMessage` dataclass
S1.2: Fields: sender, recipient, payload, correlation_id, timestamp, message_type
S1.3: Enum: `MessageType = REQUEST | RESPONSE | NOTIFICATION | ERROR`
S1.4: Test: `pytest app/sovereignai/tests/test_messaging_schema.py -v`

## S2 — InterDepartmentBus

S2.1: Create `app/sovereignai/messaging/bus.py` — `InterDepartmentBus`
S2.2: Wrap Plan 22's EventBus with department-aware routing
S2.3: Whitelist: sourced from `DepartmentManager.registry` (Plan 24 S2), read-only at init, default deny
S2.4: Test: `pytest app/sovereignai/tests/test_messaging_bus.py -v`

## S3 — Department Subscriptions

S3.1: Create `app/sovereignai/messaging/adapter.py` — `DepartmentMessagingAdapter`
S3.2: Wraps existing Plan 24 DepartmentManager instances, registers handlers without modifying Plan 24 code
S3.3: Handler signature: `async def handle_message(msg: CrossDepartmentMessage) -> CrossDepartmentMessage | None`
S3.4: Auto-reply with correlation_id for REQUEST/RESPONSE pattern
S3.5: Test: `pytest app/sovereignai/tests/test_messaging_handlers.py -v`

## S4 — Security & Audit

S4.1: Log all messages to SQLite audit table in `messaging_audit.db` (separate file, WAL mode) — fields: sender, recipient, type, timestamp, correlation_id, status, error_class, payload_byte_length; payload redacted with `**REDACTED**`. No credentials or raw payload text retained.
S4.2: Rate limiting: in-memory dict with 1-minute sliding window, max 100 messages/minute per pair; state ephemeral (restart resets). Documented as availability safeguard only — not a security boundary. For multi-instance deployments, migrate to shared store (Redis) in v2.
S4.3: Circuit breaker: if recipient fails 5x (timeout 30s, exception, or no response), emit `messaging.circuit.open` to Orchestrator
S4.4: Test: `pytest app/sovereignai/tests/test_messaging_security.py -v`

## S5 — Integration

S5.1: Orchestrator uses InterDepartmentBus for multi-department tasks
S5.2: Example: "Research this and code it" → ResearchManager → CodingManager → Orchestrator
S5.3: Test: `pytest app/sovereignai/tests/test_messaging_integration.py -v`

## S6 — AR Checks

S6.1: Add `check_messaging_whitelist_enforced.py` — verify no unauthorized cross-dept messages
S6.2: Add `check_messaging_no_department_manager_subclass.py` — verify no subclassing, monkey-patching (`setattr`), or private member imports of Plan 24 managers
S6.3: Run `pytest .agent/executor/tests/test_document_hygiene.py -v`

## Closing

Run `/close`
