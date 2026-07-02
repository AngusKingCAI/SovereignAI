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

OR14. [Mandatory] Read AGENTS.md in full once per session before first edit. All rules mandatory. Mental subset: OR4, OR5, OR9, OR10, OR11, OR20, AR5, AR12, AR17, OR40, OR41, OR54, OR57-OR66.

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

OR25. [Mandatory] detect-secrets scan uses `--exclude-files` (not `--exclude`). Audit via `detect-secrets audit`, never manual JSON edit.

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

OR40. [Mandatory] /close mandatory and atomic. All steps or STOP. Conditional steps marked "N/A — <reason>" in log. Never silently skipped.

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

OR51. [Mandatory] Deliverables ship in full or defer per item. Deferred items in exec log + close report + DEBT.md with target plan. Silent drop = STOP.

OR52. [Mandatory] "Already done" claims require executed verification — a logged command + exit code. Reading code is NOT verification.

OR53. [Mandatory] Test/mypy/static-analysis failures: no "pre-existing" exemption. Fix, DEBT with target plan, or User authorization. "Coverage: N/A" = STOP.

OR54. [Mandatory] Skipped tests carry `# TODO(prompt-N): reason`. ≥3 consecutive skipped prompts = fix, delete, or escalate.

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

OR68. [Mandatory] ServiceProvider/DatabaseProvider: health_check() returns typed dataclass; __init__ no I/O — lazy in start()/list_models().

OR69. [Mandatory] Models panel and Hardware panel must consume capability API only — no direct DatabaseRegistry/ServiceRegistry/HardwareProbe imports from web/.

OR70. [Mandatory] Adapter manifests declare `routing_priority` int. Routes ascending (lower = higher priority). Default 1000. Reserved 0-999.

OR71. [Mandatory] Diagnostic harness tests real end-to-end AI workflow: load → use → unload per stage. Mocks verify code paths; harness verifies system.

OR72. [Mandatory] TUI is a first-class UI consuming the same capability API as the WebUI. TUI panels must display real backend state, not placeholder text.

OR73. [Mandatory] CHANGELOG append at /close step 12: new `## prompt-N — <title>` section at END (oldest at top). Header + metadata (Date/Plan file/Tests/Coverage) + ≥1 scope bullet. Verbatim entry echoed in exec log (not just `+N`). check_changelog.py enforces at step 17.5: exit≠0 = STOP. Edit tagged entry = STOP per OR51.

OR74. [Mandatory] TUI panel switching must use ContentSwitcher (from textual.widgets) or TabbedContent — never manual add_class/removeClass('hidden'). Import path: textual.widgets.ContentSwitcher (NOT textual.containers).

OR75. [Mandatory] Execution log at /close: Devin writes header + `## Devin Chat` section with `[PASTE DEVIN CHAT HERE]` marker + structured S0-S5 summary with verbatim CHANGELOG echo. User pastes chat. Devin must NOT fabricate chat content. Manual Architect check (not script-enforced).

OR78. [Mandatory] Plan files are frozen during execution. Only allowed: (a) move to prompts/completed/ at /close step 17; (b) split >120-line plans into decimal sub-plans IF each sub-plan runs /open and /close independently, preserves all S0-Sn steps verbatim, and partitions WILL-edit list. Editing executable code, steps, or WILL-edit entries = STOP per OR19. Incomplete WILL-edit list = STOP; request Architect-issued Rev.

OR77. [Mandatory] Dependency discipline: every new import in production code requires the package in txt/requirements.txt. Every new dev/test import requires the package in pyproject.toml [project.optional-dependencies] dev. check_dependencies.py enforces at /open and /close. Missing dep = STOP. Run pip install -e .[dev] after any requirements.txt change.

OR79. [Mandatory] All tests have a 30s timeout via pytest-timeout (pyproject.toml addopts = --timeout=30 --timeout-method=thread). Per-test override via @pytest.mark.timeout(N). Stalled test = FAILED (not hung). Investigate root cause per OR18; do not re-run without fix.

OR80. [Mandatory] AR/OR rules in AGENTS.md must use minimal tokens whilst maintaining functionality. Constraint + consequence only; context belongs in LANDMINES.md. check_rule_conciseness.py flags rules >400 chars for review (advisory, not blocking). Hard limit: no rule >600 chars.

OR81. [Mandatory] MCP usage: Devin queries Context7 before using any library API unfamiliar or updated since training cutoff. Devin invokes Snyk MCP scan at /close for plans touching txt/requirements.txt or security-sensitive code. Reduces hallucinated APIs (P20.4 ContentSwitcher ImportError) and catches CVEs earlier (P20.5 diskcache).

OR76. [Mandatory] sailogs/ contains per-run JSONL trace logs named YYYY-MM-DD_HH-MM-SS.log. One file per process run. FileTraceSubscriber writes every TraceEmitter event. sailogs/*.log gitignored. No rotation — user archives/deletes manually.

---

See `LANDMINES.md` for failure patterns linked to rules.
