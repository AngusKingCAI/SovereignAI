Depends on: Scan 15 (prompt-15.1 cleanup)
Vision principles: P9 (observability by default), P11 (DI only, no globals), P8 (UIs separate processes)
Open questions resolved: none

## S0 — Opening
- S0.1: Run /open (verify tag prompt-15.1 on origin, clean tree on main, venv OK)
- S0.2: Read AGENTS.md in full
- S0.2.5: Re-read AGENTS.md if S0.3 adds rules
- S0.3: Add OR66 (Logs panel must consume /api/traces SSE only — no direct TraceEmitter import from web/), commit before coding

## S1 — AR check scripts
- S1.1: Create scripts/ar_checks/check_tracing.py — AST walker over sovereignai/ flagging functions with side effects (disk writes via open()/os.*, DI container mutation, EventBus.publish/subscribe, adapter method calls, subprocess.*, socket/requests/urllib, sqlite3 write ops, self.x = instance mutation) AND no trace.emit() OR allowlisted wrapper call in body. Allowlist: configurable list in scripts/ar_checks/check_tracing_allowlist.txt (one function name per line; default empty). Exemptions: `__init__` ONLY if body contains field assignment only (no I/O, no publish, no adapter calls); `@property` getters inspected same as methods (setters never exempt). No "pure query" exemption. Exit≠0 on violation.
- S1.2: Create scripts/ar_checks/check_placeholders.py — grep scan for `TODO`, `FIXME`, `XXX`, `NotImplementedError`, `pass  # placeholder` in sovereignai/, web/, adapters/, skills/, databases/, services/. In tests/: flag `NotImplementedError` and `pass  # placeholder` only (TODO/FIXME allowed in tests per OR54). Exempt: scripts/, txt/. Exit≠0 on hit.
- S1.3: Create scripts/ar_checks/spec_match.py — mechanical gate. (a) Extract "WILL edit" paths from current plan file using regex `r'^\s*[-*]\s+`?([\w./-]+\.[a-zA-Z0-9]+)'` for list-item code-fence paths, plus "WILL edit UI elements:" block parser. (b) Derive baseline tag from plan's `Depends on:` field (resolve to newest matching tag on origin). (c) `git diff --name-only {baseline}..HEAD` must contain every WILL-edit path (no missing), and every diff path must appear in some plan's WILL list OR be in allowlist: AGENTS.md, LANDMINES.md, PLANS.md, DEBT.md, DECISIONS.md, CHANGELOG.md, .devin/workflows/*, tests/**, documents/plan-*-report.md. Exit≠0 on mismatch.
- S1.4: Run all three scripts as discovery step against current repo. If violations found: log them, add remediation sub-steps before claiming clean. If 0 violations: log "discovery clean".
- S1.5: Add tests/test_ar_checks.py — synthetic violator + clean file for each script. Include test: function calling allowlisted wrapper (e.g., `_trace_emit()`) passes.

## S2 — Correlation ID propagation (OR62) + TraceEmitter live event source
- S2.1: Edit sovereignai/shared/types.py — add `_current_correlation_id: ContextVar[UUID | None]`, `bind_correlation_id(cid: UUID) -> Token`, `current_correlation_id() -> UUID | None`, `reset_correlation_id(token: Token)`.
- S2.2: Edit sovereignai/shared/trace_emitter.py — (a) emit() falls back to current_correlation_id() before generating fresh UUID if caller omits correlation_id; (b) add `collections.deque(maxlen=500)` ring buffer `self._recent_events`; (c) emit() appends to deque; (d) add `recent_events() -> list[TraceEvent]` returning list(deque); (e) add `subscribe_callback(callback: Callable[[TraceEvent], None]) -> Callable[[], None]` that registers callback and returns an unsubscribe function. Callbacks invoked on each emit() (used by SSE endpoint).
- S2.3: Edit sovereignai/shared/capability_api.py submit_task() — at entry: `existing = current_correlation_id(); if existing is None: cid = new_correlation_id(); token = bind_correlation_id(cid)`. In finally block: `if existing is None: reset_correlation_id(token)`. Pass cid to TaskStateMachine.submit(). Nested calls inherit parent id (no rebind when existing is not None).
- S2.4: Run /verify on each. Add tests/test_correlation_id.py covering: emit() picks up contextvar; submit_task() binds fresh when none, inherits when present, resets on exit; nested submit_task() inherits parent id; recent_events() returns last 500; subscribe_callback() receives live events and unsubscribe stops them.
- S2.5: Run `pytest tests/test_correlation_id.py tests/test_trace_emitter.py tests/test_capability_api.py -vvv`.

## S3 — Logs panel as 10th sidebar tab
WILL edit UI elements:
- web/templates/index.html: add `<li data-panel="logs">Logs</li>` after Options; add `<section id="panel-logs" class="panel">` with filter bar (level select, component select, search input, pause/resume button) + events table (timestamp, level, component, correlation_id, message).
- web/static/app.js: add `loadLogsPanel()` subscribing to `/api/traces/stream` SSE; seed table from `/api/traces/history`; append live events; honor filters; add `toggleLogsPause()`.
- web/static/styles.css: add `.panel-logs`, `.logs-table`, level colors (INFO grey, WARN amber #CC8400 for AA contrast, ERROR red, DEBUG muted).
- web/main.py: add `GET /api/traces/history` returning `trace.recent_events()` as list[TraceEventDTO]; add `GET /api/traces/stream` SSE endpoint that calls `trace.subscribe_callback()` to receive live events and yields TraceEventDTO JSON frames to the client. Generator must close on client-disconnect (standard ASGI pattern) and call the returned unsubscribe function.
- web/schemas.py: add `TraceEventDTO` (timestamp, level, component, correlation_id, message).
- S3.1: Edit web/templates/index.html per WILL list.
- S3.2: Edit web/static/app.js per WILL list.
- S3.3: Edit web/static/styles.css per WILL list.
- S3.4: Edit web/schemas.py then web/main.py per WILL list (both endpoints).
- S3.5: Run /verify after each edit. Add tests/test_logs_panel.py covering: GET /api/traces/history returns 200 with list; GET /api/traces/stream returns 200 SSE; SSE subscription receives live events (verify subscribe_callback wired); filters honored client-side.

## S4 — Mechanical enforcement in close.md
- S4.1: Edit .devin/workflows/close.md step 8 — add check_tracing.py and check_placeholders.py to AR checks command list.
- S4.2: Edit .devin/workflows/close.md step 16 — keep mechanical-only spec_match.py gate.
- S4.3: Run /verify on close.md.

## Closing
- Run /close (full suite, coverage ≥90% per OR43, all AR checks including new scripts, browser smoke test on Logs panel with screenshots to logs/screenshots/prompt-16/, spec_match.py, commit, tag prompt-16, push).
