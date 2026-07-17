# AGENTS.md

**AR** = Architecture Rules · **OR** = Operational Rules.
Ambiguous → read `LANDMINES.md`. Extended rules → `AGENTS_EXTENDED.md`.
Authority: `PRINCIPLES.md`.

---

## Hard Architecture Rules (AR1–AR15)

AR1. Owner ↔ Orchestrator only. Chain: Orchestrator → Manager → Worker. Bypass allowed for single-Worker, single-capability, no-state tasks.

AR2. Workers query Librarian directly for memory. No component queries a memory backend directly.

AR3. All model inference routes through Adapters. No component loads weights or calls inference endpoints directly.

AR4. No component references another by hard-coded name. Discovery via capability graph. Exemptions: `main.py`, tests, manifests.

AR5. External MCP servers wrapped as adapters before use. No direct MCP calls.

AR6. Adapters register tools in capability graph at startup. Failed health check = graceful typed error, not silent.

AR7. Workers circuit-break: >50 errors in 10s = unload. No auto-restart.

AR8. All traces/logs to local SSD via TraceEmitter. No external telemetry. Ever.

AR9. All skill authoring methods produce identical output: manifest + code + DAG.

AR10. External components copied to local disk before use. No runtime remote-only calls.

AR11. No docstrings (D103 disabled). Self-documenting names required.

AR12. FastAPI web app runs as separate process. Imports from `sovereignai/` only via public API surface.

AR13. SSE auth via HTTP session cookie. No query-param tokens.

AR14. Web-layer DTOs in `web/schemas.py`. Core types never returned directly from HTTP.

AR15. Adapters declare `health_check()`. Failed check = DEGRADED status, not skipped.

---

## Hard Operational Rules (OR1–OR30)

OR1. Read `AGENTS.md` at session start. Read `AGENTS_EXTENDED.md` on-demand when ambiguous.

OR2. Every plan: `/open` → execute → `/close`. No skipping, no partial runs.

OR3. STOP on any failure. No "helpful" workarounds. No arguing with user instructions.

OR4. `/close` is atomic: verify → commit → tag → push. Verification happens BEFORE tag. No exceptions.

OR5. Before git tag: RUN `scripts/verify_close.py`. Exit 0 = proceed. Exit 1 = STOP. Do not explain, justify, or suggest alternatives. STOP is the only valid response.

OR6. CHANGELOG prepend only. Latest prompt at top. Never append. Script-enforced via verify_close.py.

OR7. Plan files moved to `prompts/completed/` before tag. Glob: `plan-{N}-Rev*.md`. Script-enforced via verify_close.py.

OR8. Execution log blank template only, <500 bytes. Script-enforced via verify_close.py.

OR9. Execute plan steps in strict numerical order. No reordering. No marking complete based on work done elsewhere.

OR10. Never delete prompt files (execution logs, plan files). Permanent history.

OR11. Never delete content from governance documents. Only add. Historical context preserved.

OR12. Non-scan plans: scoped tests via `scripts/get_scoped_tests.py`. Scan plans (5,10,15…): full suite.

OR13. Coverage ≥90% at `/close`. No exemptions.

OR14. All AR check scripts run in `/close`. Any failure = STOP.

OR15. Pre-commit hooks run before every commit. No `--no-verify`.

OR16. Ruff, mypy, bandit, pip-audit, vulture, detect-secrets run in `/close`. Any failure = STOP.

OR17. Snyk MCP scan on requirements + changed files. CRITICAL/HIGH = STOP.

OR18. UI changes: DOM verification + screenshot capture before commit.

OR19. Spec match script validates plan vs implementation. Exit≠0 = STOP.

OR20. Skipped tests carry `# TODO(prompt-N): reason`. ≥3 consecutive skipped prompts = fix, delete, or escalate.

OR21. HTML/CSS/JS syntax validation before tests. Failure = STOP.

OR22. Tests use real-shape fixtures. No simplified shapes.

OR23. Stray-file pre-commit scan: `git status -s` after `git add -A`.

OR24. User-authorized exceptions need target plan documentation. "Deferred to next prompt" without plan number = STOP.

OR25. All tests have 30s timeout via pytest-timeout. Stalled test = FAILED.

OR26. Follow skill workflows systematically. Never skip steps or pick-and-choose.

OR27. Untracked plan files are valid plans awaiting commit. Treat same as tracked. Never delete as "cleanup."

OR28. Governance docs: only add, never edit/remove. Prepend-only for LANDMINES.md.

OR29. Scoped test resolution via `scripts/get_scoped_tests.py`. Empty scope + .py changes = STOP.

OR30. Follow instructions literally. Restrictive terms ('only', 'never', 'must', 'no content') = exact compliance. If instruction seems incorrect, STOP and ask. Do not argue. Do not "be helpful" by overriding.

---

See `LANDMINES.md` for failure patterns. See `AGENTS_EXTENDED.md` for AR16–AR30 and OR31–OR63.
