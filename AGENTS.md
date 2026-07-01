# AGENTS.md

**AR** = Architecture Rules · **OR** = Operational Rules. Ambiguous → read `LANDMINES.md`. Authority: `principles.md`.

---

## Architecture Rules

AR1. Owner ↔ Orchestrator only. Chain: Orchestrator → Manager → Worker. Bypass allowed for single-Worker, single-capability, no-state tasks. All Owner-facing output routes through Orchestrator.

AR2. Workers query Librarian directly for memory. No component queries a memory backend directly.

AR3. All model inference routes through Adapters. No component loads weights or calls inference endpoints directly.

AR4. No global mutable state. All shared state in `shared/container.py`. DI only.

AR5. No constructor takes >15 args (excluding self). Split the class or use a typed config dataclass.

AR6. No context objects, untyped dicts, or `**kwargs` across component boundaries. Every parameter typed with single purpose.

AR7. UI processes consume Capability API only. No imports from `orchestrator/`, `managers/`, `workers/`, `librarian/`, `adapters/`, `skills/`.

AR8. No component references another by hard-coded name. Discovery via capability graph. Exemptions: `main.py`, tests, manifests.

AR9. Skills consume tools via capability graph. No direct adapter imports.

AR10. External MCP servers wrapped as adapters before use. No direct MCP calls.

AR11. Adapters register tools in capability graph at startup. Failed health check = graceful typed error, not silent.

AR12. Workers circuit-break: >50 errors in 10s = unload. No auto-restart.

AR13. All traces/logs to local SSD via TraceEmitter. No external telemetry. Ever.

AR14. Managers temporary by default (per-task). Workers always fine-tuned specialists.

AR15. All skill authoring methods produce identical output: manifest + code + DAG.

AR16. External components copied to local disk before use. No runtime remote-only calls.

AR17. No docstrings in Python source. Use clear function/class/variable names instead. Ruff D103 disabled. Code must be self-documenting.

---

## Operational Rules

OR1. Git Bash only. Use `grep`, `cat`, `sed`, `awk`, `head`, `tail`, `touch`, `ls`, `wc`, `xargs`.

OR2. File-scoped mypy only. Never `mypy .` except at scan prompts.

OR3. Run scan tools ONE AT A TIME. Parallel execution corrupts output.

OR4. Never use `replace_all`. Edit each occurrence individually.

OR5. Syntax check after every file edit, before tests: `python -c "import ast; ast.parse(open('<file>').read())"`.

OR6. Structured-markdown edits (AGENTS.md, AI_HANDOFF.md, plans, CHANGELOG, workflow files) use Edit tool only. Never `sed` or redirection.

OR7. Append to END only. Never insert at top.

OR8. Temp-file pattern for appends. Delete temp after.

OR9. Pre-declare scope before editing. List files WILL edit and will NOT edit.

OR10. HARD STOP on scope expansion. Don't edit outside declared scope.

OR11. Full suite MUST pass before tagging.

OR12. Never mix naive/aware datetime. Use `datetime.now(timezone.utc)`.

OR13. Temp files in dedicated temp dir, not repo root. Delete after consuming. Check for strays before `git add`.

OR14. Read `AGENTS.md` in full once per session before first edit. Always-on mental subset: OR4, OR5, OR9, OR10, OR11, OR20, AR5, AR12, AR17, OR40, OR41, OR54, OR57, OR58, OR59, OR60, OR61, OR63, OR64, OR65, OR66.

OR15. Every new implementation has corresponding test file with passing tests.

OR16. Test deletion is scope deviation. STOP if specified test can't pass.

OR17. Zero output is data, not success. Re-run with confirmation command.

OR18. Never re-run failing test without root cause.

OR19. If plan step impossible as written, STOP immediately.

OR20. Never `git commit --no-verify`. Fix hook issues.

OR21. Never exclude files from hooks to bypass errors. STOP if out-of-scope.

OR22. Execute plan steps in strict numerical order. Don't jump ahead.

OR23. Minimize command output. `tail -n N` (default 5) unless full needed. Never >20 lines without truncation. pytest exempt (always `-vvv`).

OR24. Runtime deps in `txt/requirements.txt` only. Dev/test tools in `pyproject.toml` only.

OR25. `detect-secrets scan` must exclude vendored/build dirs using `--exclude-files` flag (not `--exclude` which is ambiguous). Audit via `detect-secrets audit`, never manual JSON edit.

OR26. Edit tool for empty files, not `echo "" >`.

OR27. Multi-line commits use multiple `-m` flags, not embedded newlines.

OR28. Shell redirection for >1KB output unreliable. Use `tee` or Edit tool.

OR29. Project-local venv at `.venv/`. Create via `py -3.11 -m venv .venv`. Absolute paths in all commands. No `source activate`.

OR30. Mypy on `.py` files only.

OR31. FastAPI web app runs as separate process. Imports from `sovereignai/` only via public API surface.

OR32. SSE auth via HTTP session cookie. No query-param tokens.

OR33. Web-layer DTOs in `web/schemas.py`. Core types never returned directly from HTTP.

OR34. Adapters declare `health_check()`. Failed check = DEGRADED status, not skipped.

OR35. Capability classes have conformance tests. Fail-closed for first-party, fail-open for third-party. <100ms each, cached per `(component_id, content_hash)`.

OR36. Contract tests verify backward compatibility. Failure blocks build.

OR37. Property-based tests run every commit. CI gate blocker.

OR38. Run workflow commands verbatim. Re-read workflow files fresh each run.

OR39. Never edit AR check scripts or tests to make failure pass.

OR40. `/close` is mandatory and atomic. All steps or STOP. Steps conditional on plan type may be marked "N/A — <reason>" in execution log. Steps never silently skipped.

OR41. `git add -A` is the ONLY staging command for ALL commits. No explicit file lists. Verify with `git status -s` after.

OR42. Tag only after final commit verified. Never force-push a tag.

OR43. Coverage ≥90% at `/close` for `.py`-editing plans. N/A = STOP. >5% drop = STOP.

OR44. Update Bandit baseline in PLANS.md at every `/close` where tests added/removed.

OR45. After quota interrupt, re-read plan + AGENTS.md before continuing.

OR46. Rule/landmine numbers never renumbered. Gaps permanent. (Rev 9 was the one-time reset.)

OR47. Backend + UI in same plan. No backend without UI surface (unless explicitly deferred).

OR48. Memory backends pluggable via CapabilityGraph. Not hardcoded.

OR49. Crash recovery: check `~/.sovereignai/.shutdown_marker`. Skip if exists. Mark non-terminal tasks FAILED. Wrapped in try/except.

OR50. Durable backends use atomic writes. SQLite = WAL + transactions. JSON = temp + `os.replace()`. Locks never force-acquired.

OR51. Plan deliverables ship in full or explicitly defer per item. Deferred items listed by number in execution log + close report + DEBT.md with target plan. Silently dropping sub-items = STOP.

OR52. "Already done" claims require executed verification — a logged command + exit code. Reading code is NOT verification.

OR53. Test, mypy, and static-analysis failures have no "pre-existing" exemption. Fix, document in DEBT.md with target plan, or get User authorization per item. "Coverage: N/A" = STOP.

OR54. Skipped tests carry `# TODO(prompt-N): reason`. "Consecutive" = three successive plans where the test file was in scope. Tests skipped ≥3 consecutive prompts must be fixed, deleted, or escalated.

OR55. CHANGELOG must not claim unshipped scope.

OR56. HTML/CSS/JS syntax validation before tests. Failure = STOP.

OR57. Web UI plans require browser smoke test at `/close`. Screenshots to execution log.

OR58. Tests use real-shape fixtures. No simplified shapes that hide production bugs.

OR59. Stray-file pre-commit scan: `git status -s` after `git add -A`.

OR60. Re-read plan at start of each phase. Don't rely on cached mental model.

OR61. Universal Tracing Mandate. Every function with side effects emits ≥1 trace event. `check_tracing.py` classifies mechanically — self-declared exemptions rejected.

OR62. Correlation IDs propagate from entry point through all downstream calls via context var.

OR63. Placeholder code must not ship as "complete". `check_placeholders.py` enforces at `/close`. Legitimate `# TODO` requires DEBT.md entry per OR51.

OR64. User-authorized exceptions need target plan documentation. "Deferred to next prompt" without plan number = STOP.

OR65. Post-execution spec-match review mandatory. At `/close` step 16, run `spec_match.py` — mechanical gate. Exit≠0 = STOP.

OR66. Logs panel must consume /api/traces SSE only — no direct TraceEmitter import from web/.

OR67. databases/ and services/ are root-level packages, never nested in sovereignai/.

OR68. Every ServiceProvider and DatabaseProvider exposes health_check() returning typed status dataclass; provider __init__ must not perform I/O — lazy execution only in start()/list_models().

OR69. Models panel and Hardware panel must consume capability API only — no direct DatabaseRegistry/ServiceRegistry/HardwareProbe imports from web/.

OR70. Every adapter manifest declares `routing_priority` int — RoutingEngine routes ascending, lower = higher priority; default 1000 for manifests omitting the field; reserved range 0-999 for explicit priorities.

OR71. Diagnostic harness tests real end-to-end AI workflow with explicit model lifecycle: load → use → unload per stage. Mock tests verify code paths; harness tests verify system functionality.

OR72. TUI is a first-class UI consuming the same capability API as the WebUI. TUI panels must display real backend state, not placeholder text.

---

See `LANDMINES.md` for failure patterns linked to rules.
