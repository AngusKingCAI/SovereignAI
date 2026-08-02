Depends on: Scan 15 (prompt-15.1 cleanup)
Vision principles: P9 (observability by default), P11 (DI only, no globals), P8 (UIs separate processes)
Open questions resolved: none

## S0 — Opening
- S0.1: Run /open (verify tag prompt-15.1 on origin, clean tree on main, venv OK)
- S0.2: Read AGENTS.md in full
- S0.2.5: Re-read AGENTS.md if S0.3 adds rules
- S0.3: Add OR66 (Logs panel must consume /api/traces SSE only — no direct TraceEmitter import from web/), commit before coding

## S1 — AR check scripts (close.md already references these; create the missing files)
- S1.1: Create scripts/ar_checks/check_tracing.py — AST walker over sovereignai/ flagging any function with side effects (writes to disk, mutates DI container, calls EventBus.publish, calls adapter method) AND no trace.emit() in body. Exemptions: __init__, @property, pure queries (return-only). Exit≠0 on violation.
- S1.2: Create scripts/ar_checks/check_placeholders.py — grep scan for `TODO`, `FIXME`, `XXX`, `NotImplementedError`, `pass  # placeholder` in sovereignai/, web/, adapters/, skills/, databases/, services/. Exempt: tests/, scripts/, txt/. Exit≠0 on hit.
- S1.3: Create scripts/ar_checks/spec_match.py — mechanical gate: extract every "WILL edit" file path from prompts/plan-{N}-Rev{n}.md (current plan), then `git diff --name-only prompt-{N-1}..HEAD` must contain every WILL-edit path (no missing), and every diff path must appear in some plan's WILL list OR be a governance/test file (allowlist: AGENTS.md, LANDMINES.md, PLANS.md, DEBT.md, DECISIONS.md, CHANGELOG.md, .devin/workflows/*, tests/**, documents/plan-*-report.md). Exit≠0 on mismatch.
- S1.4: Run /verify on each. Run all three scripts. Expect 0 violations against current repo.
- S1.5: Add tests/test_ar_checks.py — synthetic violator + clean file for each script.

## S2 — Correlation ID propagation (OR62 already in AGENTS.md; implement the mechanism)
- S2.1: Edit sovereignai/shared/types.py — add `_current_correlation_id: ContextVar[UUID | None]`, `bind_correlation_id(cid: UUID) -> Token[UUID | None]`, `current_correlation_id() -> UUID | None`, `reset_correlation_id(token: Token)`.
- S2.2: Edit sovereignai/shared/trace_emitter.py TraceEmitter.emit() — if caller omits correlation_id, fall back to current_correlation_id() before generating fresh UUID.
- S2.3: Edit sovereignai/shared/capability_api.py submit_task() — bind fresh correlation_id at entry via `with` or try/finally reset; pass to TaskStateMachine.submit().
- S2.4: Run /verify on each. Add tests/test_correlation_id.py covering: emit() picks up contextvar; submit_task() binds and resets on exit; nested submit_task() inherits parent id.
- S2.5: Run `pytest tests/test_correlation_id.py tests/test_trace_emitter.py tests/test_capability_api.py -vvv`.

## S3 — Logs panel as 10th sidebar tab
WILL edit UI elements:
- web/templates/index.html: add `<li data-panel="logs">Logs</li>` to sidebar nav after Options; add `<section id="panel-logs" class="panel">` containing: filter bar (level select, component select, search input, pause/resume button), events table (timestamp, level, component, correlation_id, message).
- web/static/app.js: add `loadLogsPanel()` subscribing to `/api/traces/stream` SSE; append events to table; honor filters; add `toggleLogsPause()`.
- web/static/styles.css: add `.panel-logs`, `.logs-table`, level color coding (INFO grey, WARN amber, ERROR red, DEBUG muted).
- web/main.py: add `GET /api/traces/history` returning last 500 TraceEmitter events as JSON list (DTO in web/schemas.py).
- web/schemas.py: add `TraceEventDTO` (timestamp, level, component, correlation_id, message).
- S3.1: Edit web/templates/index.html per WILL list.
- S3.2: Edit web/static/app.js per WILL list.
- S3.3: Edit web/static/styles.css per WILL list.
- S3.4: Edit web/schemas.py then web/main.py per WILL list.
- S3.5: Run /verify after each edit. Add tests/test_logs_panel.py covering: GET /api/traces/history returns 200 with list; SSE subscription receives events; filters honored client-side.

## S4 — Mechanical enforcement in close.md
- S4.1: Edit .devin/workflows/close.md step 8 — confirm check_tracing.py and check_placeholders.py are in the AR checks command list (already referenced; ensure executable).
- S4.2: Edit .devin/workflows/close.md step 16 — keep mechanical-only spec_match.py gate. No LLM layer.
- S4.3: Run /verify on close.md.

## Closing
- Run /close (full suite, coverage ≥90%, all AR checks including new scripts, browser smoke test on Logs panel with screenshots to logs/screenshots/prompt-16/, spec_match.py, commit, tag prompt-16, push).
