# AGENTS.md

**AR** = Architecture Rules · **OR** = Operational Rules. Ambiguous → read `LANDMINES.md`. Authority: `principles.md`.

---

## Architecture Rules

AR1. Owner ↔ Orchestrator only. Chain: Orchestrator → Manager → Worker. Bypass allowed for single-Worker, single-capability, no-state tasks. All Owner-facing output routes through Orchestrator.

AR2. Workers query Librarian directly for memory. No component queries a memory backend directly.

AR3. All model inference routes through Adapters. No component loads weights or calls inference endpoints directly.

AR4. No component references another by hard-coded name. Discovery via capability graph. Exemptions: `main.py`, tests, manifests.

AR5. External MCP servers wrapped as adapters before use. No direct MCP calls.

AR6. Adapters register tools in capability graph at startup. Failed health check = graceful typed error, not silent.

AR7. Workers circuit-break: >50 errors in 10s = unload. No auto-restart.

AR8. All traces/logs to local SSD via TraceEmitter. No external telemetry. Ever.

AR9. All skill authoring methods produce identical output: manifest + code + DAG.

AR10. External components copied to local disk before use. No runtime remote-only calls.

AR11. No docstrings in Python source. Use clear function/class/variable names instead. Ruff D103 disabled. Code must be self-documenting.

AR12. FastAPI web app runs as separate process. Imports from `sovereignai/` only via public API surface.

AR13. SSE auth via HTTP session cookie. No query-param tokens.

AR14. Web-layer DTOs in `web/schemas.py`. Core types never returned directly from HTTP.

AR15. Adapters declare `health_check()`. Failed check = DEGRADED status, not skipped.

AR16. Capability classes have conformance tests. Fail-closed for first-party, fail-open for third-party. <100ms each, cached per `(component_id, content_hash)`.

AR17. Contract tests verify backward compatibility. Failure blocks build.

AR18. Property-based tests run every commit. CI gate blocker.

AR19. Memory backends pluggable via CapabilityGraph. Not hardcoded.

AR20. Crash recovery: check `~/.sovereignai/.shutdown_marker`. Skip if exists. Mark non-terminal tasks FAILED. Wrapped in try/except.

AR21. Durable backends use atomic writes. SQLite = WAL + transactions. JSON = temp + `os.replace()`. Locks never force-acquired.

AR22. Universal Tracing Mandate. Every function with side effects emits ≥1 trace event. `check_tracing.py` classifies mechanically — self-declared exemptions rejected.

AR23. Correlation IDs propagate from entry point through all downstream calls via context var.

AR24. Logs panel must consume /api/traces SSE only — no direct TraceEmitter import from web/.

AR25. databases/ and services/ are root-level packages, never nested in sovereignai/.

AR26. ServiceProvider/DatabaseProvider: health_check() returns typed dataclass; __init__ no I/O — lazy in start()/list_models().

AR27. Models panel and Hardware panel must consume capability API only — no direct DatabaseRegistry/ServiceRegistry/HardwareProbe imports from web/.

AR28. Adapter manifests declare `routing_priority` int. Routes ascending (lower = higher priority). Default 1000. Reserved 0-999.

AR29. Diagnostic harness tests real end-to-end AI workflow: load → use → unload per stage. Mocks verify code paths; harness verifies system.

AR30. TUI is a first-class UI consuming the same capability API as the WebUI. TUI panels must display real backend state, not placeholder text.

---

## Operational Rules

OR1. File-scoped mypy only. Never `mypy .` except at scan prompts.

OR2. Run scan tools ONE AT A TIME. Parallel execution corrupts output.

OR3. Never use `replace_all`. Edit each occurrence individually.

OR4. Structured-markdown edits (AGENTS.md, AI_HANDOFF.md, plans, CHANGELOG, workflow files) use Edit tool only. Never `sed` or redirection.

OR5. CHANGELOG.md and LANDMINES.md append-only. Never insert at top or edit existing entries.

OR6. Pre-declare scope before editing. List files WILL edit and will NOT edit.

OR7. Never mix naive/aware datetime. Use `datetime.now(timezone.utc)`.

OR8. Temp files in dedicated temp dir, not repo root. Delete after consuming. Check for strays before `git add`.

OR9. Every new implementation has corresponding test file with passing tests.

OR10. Test deletion is scope deviation. STOP if specified test can't pass.

OR11. Never re-run failing test without fixing root cause.

OR12. Never `git commit --no-verify`. Fix hook issues.

OR13. Never exclude files from hooks to bypass errors. STOP if out-of-scope.

OR14. Runtime deps in `txt/requirements.txt` only. Dev/test tools in `pyproject.toml` only.

OR15. Never edit AR check scripts or tests to make failure pass.

OR16. Backend + UI in same plan. No backend without UI surface (unless explicitly deferred).

OR17. Deliverables ship in full or defer per item. Deferred items in exec log + close report + DEBT.md with target plan. Silent drop = STOP.

OR18. "Already done" claims require executed verification — a logged command + exit code. Reading code is NOT verification.

OR19. Test/mypy/static-analysis failures: no "pre-existing" exemption. Fix, DEBT with target plan, or User authorization. "Coverage: N/A" = STOP.

OR20. Skipped tests carry `# TODO(prompt-N): reason`. ≥3 consecutive skipped prompts = fix, delete, or escalate.

OR21. HTML/CSS/JS syntax validation before tests. Failure = STOP.

OR22. Tests use real-shape fixtures. No simplified shapes that hide production bugs.

OR23. Stray-file pre-commit scan: `git status -s` after `git add -A`.

OR24. User-authorized exceptions need target plan documentation. "Deferred to next prompt" without plan number = STOP.

OR25. All tests have a 30s timeout via pytest-timeout (pyproject.toml addopts = --timeout=30 --timeout-method=thread). Per-test override via @pytest.mark.timeout(N). Stalled test = FAILED (not hung).

OR26. Follow skill workflows systematically. Never skip steps or pick-and-choose based on perceived relevance. Execute all steps in sequence as designed.

---

See `LANDMINES.md` for failure patterns linked to rules.
