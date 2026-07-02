# AGENTS.md

**AR** = Architecture Rules · **OR** = Operational Rules. Ambiguous → read `LANDMINES.md`. Authority: `principles.md`.

---

## Architecture Rules

AR1. [Mandatory] Owner ↔ Orchestrator only. Chain: Orchestrator → Manager → Worker. Bypass allowed for single-Worker, single-capability, no-state tasks. All Owner-facing output routes through Orchestrator.

AR2. [Mandatory] Workers query Librarian directly for memory. No component queries a memory backend directly.

AR3. [Mandatory] All model inference routes through Adapters. No component loads weights or calls inference endpoints directly.

AR4. [Mandatory] No global mutable state. All shared state in `shared/container.py`. DI only.

AR5. [Mandatory] No constructor takes >15 args (excluding self). Split the class or use a typed config dataclass.

AR6. [Mandatory] No context objects, untyped dicts, or `**kwargs` across component boundaries. Every parameter typed with single purpose.

AR7. [Mandatory] UI processes consume Capability API only. No imports from `orchestrator/`, `managers/`, `workers/`, `librarian/`, `adapters/`, `skills/`.

AR8. [Mandatory] No component references another by hard-coded name. Discovery via capability graph. Exemptions: `main.py`, tests, manifests.

AR9. [Mandatory] Skills consume tools via capability graph. No direct adapter imports.

AR10. [Mandatory] External MCP servers wrapped as adapters before use. No direct MCP calls.

AR11. [Mandatory] Adapters register tools in capability graph at startup. Failed health check = graceful typed error, not silent.

AR12. [Mandatory] Workers circuit-break: >50 errors in 10s = unload. No auto-restart.

AR13. [Mandatory] All traces/logs to local SSD via TraceEmitter. No external telemetry. Ever.

AR14. [Mandatory] Managers temporary by default (per-task). Workers always fine-tuned specialists.

AR15. [Mandatory] All skill authoring methods produce identical output: manifest + code + DAG.

AR16. [Mandatory] External components copied to local disk before use. No runtime remote-only calls.

AR17. [Mandatory] No docstrings in Python source. Use clear function/class/variable names instead. Ruff D103 disabled. Code must be self-documenting.

---

## Operational Rules

OR1. [Mandatory] Git Bash only. Use `grep`, `cat`, `sed`, `awk`, `head`, `tail`, `touch`, `ls`, `wc`, `xargs`.

OR2. [Mandatory] File-scoped mypy only. Never `mypy .` except at scan prompts.

OR3. [Mandatory] Run scan tools ONE AT A TIME. Parallel execution corrupts output.

OR4. [Mandatory] Never use `replace_all`. Edit each occurrence individually.

OR5. [Mandatory] Syntax check after every file edit, before tests: `python -c "import ast; ast.parse(open('<file>').read())"`.

OR6. [Mandatory] Structured-markdown edits (AGENTS.md, AI_HANDOFF.md, plans, CHANGELOG, workflow files) use Edit tool only. Never `sed` or redirection.

OR7. [Mandatory] Append to END only. Never insert at top.

OR8. [Mandatory] Temp-file pattern for appends. Delete temp after.

OR9. [Mandatory] Pre-declare scope before editing. List files WILL edit and will NOT edit.

OR10. [Mandatory] HARD STOP on scope expansion. Don't edit outside declared scope.

OR11. [Mandatory] Full suite MUST pass before tagging.

OR12. [Mandatory] Never mix naive/aware datetime. Use `datetime.now(timezone.utc)`.

OR13. [Mandatory] Temp files in dedicated temp dir, not repo root. Delete after consuming. Check for strays before `git add`.

OR14. [Mandatory] Read `AGENTS.md` in full once per session before first edit. All rules are mandatory by default. Always-on mental subset: OR4, OR5, OR9, OR10, OR11, OR20, AR5, AR12, AR17, OR40, OR41, OR54, OR57, OR58, OR59, OR60, OR61, OR63, OR64, OR65, OR66.

OR15. [Mandatory] Every new implementation has corresponding test file with passing tests.

OR16. [Mandatory] Test deletion is scope deviation. STOP if specified test can't pass.

OR17. [Mandatory] Zero output is data, not success. Re-run with confirmation command.

OR18. [Mandatory] Never re-run failing test without root cause.

OR19. [Mandatory] If plan step impossible as written, STOP immediately.

OR20. [Mandatory] Never `git commit --no-verify`. Fix hook issues.

OR21. [Mandatory] Never exclude files from hooks to bypass errors. STOP if out-of-scope.

OR22. [Mandatory] Execute plan steps in strict numerical order. Don't jump ahead.

OR23. [Mandatory] Minimize command output. `tail -n N` (default 5) unless full needed. Never >20 lines without truncation. pytest exempt (always `-vvv`).

OR24. [Mandatory] Runtime deps in `txt/requirements.txt` only. Dev/test tools in `pyproject.toml` only.

OR25. [Mandatory] `detect-secrets scan` must exclude vendored/build dirs using `--exclude-files` flag (not `--exclude` which is ambiguous). Audit via `detect-secrets audit`, never manual JSON edit.

OR26. [Mandatory] Edit tool for empty files, not `echo "" >`.

OR27. [Mandatory] Multi-line commits use multiple `-m` flags, not embedded newlines.

OR28. [Mandatory] Shell redirection for >1KB output unreliable. Use `tee` or Edit tool.

OR29. [Mandatory] Project-local venv at `.venv/`. Create via `py -3.11 -m venv .venv`. Absolute paths in all commands. No `source activate`.

OR30. [Mandatory] Mypy on `.py` files only.

OR31. [Mandatory] FastAPI web app runs as separate process. Imports from `sovereignai/` only via public API surface.

OR32. [Mandatory] SSE auth via HTTP session cookie. No query-param tokens.

OR33. [Mandatory] Web-layer DTOs in `web/schemas.py`. Core types never returned directly from HTTP.

OR34. [Mandatory] Adapters declare `health_check()`. Failed check = DEGRADED status, not skipped.

OR35. [Mandatory] Capability classes have conformance tests. Fail-closed for first-party, fail-open for third-party. <100ms each, cached per `(component_id, content_hash)`.

OR36. [Mandatory] Contract tests verify backward compatibility. Failure blocks build.

OR37. [Mandatory] Property-based tests run every commit. CI gate blocker.

OR38. [Mandatory] Run workflow commands verbatim. Re-read workflow files fresh each run.

OR39. [Mandatory] Never edit AR check scripts or tests to make failure pass.

OR40. [Mandatory] `/close` is mandatory and atomic. All steps or STOP. Steps conditional on plan type may be marked "N/A — <reason>" in execution log. Steps never silently skipped.

OR41. [Mandatory] `git add -A` is the ONLY staging command for ALL commits. No explicit file lists. Verify with `git status -s` after.

OR42. [Mandatory] Tag only after final commit verified. Never force-push a tag.

OR43. [Mandatory] Coverage ≥90% at `/close` for `.py`-editing plans. N/A = STOP. >5% drop = STOP.

OR44. [Mandatory] Update Bandit baseline in PLANS.md at every `/close` where tests added/removed.

OR45. [Mandatory] After quota interrupt, re-read plan + AGENTS.md before continuing.

OR46. [Mandatory] Rule/landmine numbers never renumbered. Gaps permanent. (Rev 9 was the one-time reset.)

OR47. [Mandatory] Backend + UI in same plan. No backend without UI surface (unless explicitly deferred).

OR48. [Mandatory] Memory backends pluggable via CapabilityGraph. Not hardcoded.

OR49. [Mandatory] Crash recovery: check `~/.sovereignai/.shutdown_marker`. Skip if exists. Mark non-terminal tasks FAILED. Wrapped in try/except.

OR50. [Mandatory] Durable backends use atomic writes. SQLite = WAL + transactions. JSON = temp + `os.replace()`. Locks never force-acquired.

OR51. [Mandatory] Plan deliverables ship in full or explicitly defer per item. Deferred items listed by number in execution log + close report + DEBT.md with target plan. Silently dropping sub-items = STOP.

OR52. [Mandatory] "Already done" claims require executed verification — a logged command + exit code. Reading code is NOT verification.

OR53. [Mandatory] Test, mypy, and static-analysis failures have no "pre-existing" exemption. Fix, document in DEBT.md with target plan, or get User authorization per item. "Coverage: N/A" = STOP.

OR54. [Mandatory] Skipped tests carry `# TODO(prompt-N): reason`. "Consecutive" = three successive plans where the test file was in scope. Tests skipped ≥3 consecutive prompts must be fixed, deleted, or escalated.

OR55. [Mandatory] CHANGELOG must not claim unshipped scope.

OR56. [Mandatory] HTML/CSS/JS syntax validation before tests. Failure = STOP.

OR57. [Mandatory] Web UI plans require browser smoke test at `/close`. Screenshots to execution log.

OR58. [Mandatory] Tests use real-shape fixtures. No simplified shapes that hide production bugs.

OR59. [Mandatory] Stray-file pre-commit scan: `git status -s` after `git add -A`.

OR60. [Mandatory] Re-read plan at start of each phase. Don't rely on cached mental model.

OR61. [Mandatory] Universal Tracing Mandate. Every function with side effects emits ≥1 trace event. `check_tracing.py` classifies mechanically — self-declared exemptions rejected.

OR62. [Mandatory] Correlation IDs propagate from entry point through all downstream calls via context var.

OR63. [Mandatory] Placeholder code must not ship as "complete". `check_placeholders.py` enforces at `/close`. Legitimate `# TODO` requires DEBT.md entry per OR51.

OR64. [Mandatory] User-authorized exceptions need target plan documentation. "Deferred to next prompt" without plan number = STOP.

OR65. [Mandatory] Post-execution spec-match review mandatory. At `/close` step 16, run `spec_match.py` — mechanical gate. Exit≠0 = STOP.

OR66. [Mandatory] Logs panel must consume /api/traces SSE only — no direct TraceEmitter import from web/.

OR67. [Mandatory] databases/ and services/ are root-level packages, never nested in sovereignai/.

OR68. [Mandatory] Every ServiceProvider and DatabaseProvider exposes health_check() returning typed status dataclass; provider __init__ must not perform I/O — lazy execution only in start()/list_models().

OR69. [Mandatory] Models panel and Hardware panel must consume capability API only — no direct DatabaseRegistry/ServiceRegistry/HardwareProbe imports from web/.

OR70. [Mandatory] Every adapter manifest declares `routing_priority` int — RoutingEngine routes ascending, lower = higher priority; default 1000 for manifests omitting the field; reserved range 0-999 for explicit priorities.

OR71. [Mandatory] Diagnostic harness tests real end-to-end AI workflow with explicit model lifecycle: load → use → unload per stage. Mock tests verify code paths; harness tests verify system functionality.

OR72. [Mandatory] TUI is a first-class UI consuming the same capability API as the WebUI. TUI panels must display real backend state, not placeholder text.

OR73. [Mandatory] CHANGELOG append discipline. At `/close` step 12, append a new `## prompt-N — <title>` section to CHANGELOG.md at the end of the file (oldest at top; never prepend to top, never edit existing entries). Entry structure: `## prompt-N — <title>` header, then metadata lines (`**Date**:`, `**Plan file**:`, `**Tests**:`, `**Coverage**:`), then a bullet list of shipped scope (≥1 bullet). The verbatim entry text must be echoed in the execution log — the `+N` line-count marker alone is NOT sufficient. `scripts/ar_checks/check_changelog.py` enforces mechanically at `/close` step 17.5: exit≠0 = STOP. Editing an existing CHANGELOG entry after its plan is tagged = STOP per OR51.

OR74. [Mandatory] TUI panel switching must use ContentSwitcher (from textual.widgets) or TabbedContent — never manual add_class/removeClass('hidden'). Import path: textual.widgets.ContentSwitcher (NOT textual.containers).

OR75. [Mandatory] Execution log file at /close must be ≥500 lines OR contain a '## Session Incomplete' marker. check_changelog.py enforces. Prevents 102-line stubs passing the gate (observed in P20.5 commit d7679e7).

---

See `LANDMINES.md` for failure patterns linked to rules.
