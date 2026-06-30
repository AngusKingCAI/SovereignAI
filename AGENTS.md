# AGENTS.md

**AR** = Architecture Rules · **OR** = Operational Rules. Ambiguous → read `LANDMINES.md`. Authority: `project-vision-Rev5.md` (locked).

---

## Architecture Rules

AR1. Owner ↔ Orchestrator only. Chain: Orchestrator → Manager → Worker. Bypass allowed for single-Worker, single-capability, no-state tasks. All Owner-facing output routes through Orchestrator.

AR2. Workers query Librarian directly for memory. No component queries a memory backend directly.

AR3. All model inference routes through Adapters. No component loads weights or calls inference endpoints directly.

AR4. No global mutable state. All shared state in `shared/container.py`. DI only — no `@inject`, no auto-wiring, no module-level mutable variables, no monkey-patching.

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

AR17. Every `def`/`async def` has a docstring. First line: verb-first, ≥10 words, no jargon. Enforced via Ruff D103 + custom check.

---

## Operational Rules

### Environment
OR1. Git Bash only. Use `grep`, `cat`, `sed`, `awk`, `head`, `tail`, `touch`, `ls`, `wc`, `xargs`.

OR2. File-scoped mypy only. Never `mypy .` except at scan prompts (5, 10, 15…).

OR3. Run scan tools ONE AT A TIME. Parallel execution corrupts output.

### Edit discipline
OR4. Never use `replace_all`. Edit each occurrence individually.

OR5. Syntax check after every file edit, before tests: `python -c "import ast; ast.parse(open('<file>').read())"`.

OR6. Structured-markdown edits (AGENTS.md, AI_HANDOFF.md, plans, CHANGELOG) use Edit tool only. Never `sed` or redirection.

### Git discipline
OR7. Tag at `/close` step 19. Verify before create (`git tag --list prompt-{N}` empty) and after push (`git ls-remote --tags origin | grep prompt-{N}`).

OR8. Append to END only. Never insert at top.

OR9. Temp-file pattern for appends. Delete temp after.

OR10. ≤15 lines per CHANGELOG entry.

### Scope
OR11. Pre-declare scope before editing. List files WILL edit and will NOT edit.

OR12. HARD STOP on scope expansion. Don't edit outside declared scope.

### Tests
OR13. Full suite MUST pass before tagging.

OR14. Never mix naive/aware datetime. Use `datetime.now(timezone.utc)`. Never `datetime.utcnow()` or bare `datetime.now()`.

OR15. Temp files in dedicated temp dir, not repo root. Delete after consuming. Check for strays before `git add`.

### Always-on
OR16. Read `AGENTS.md` in full once per session before first edit. Always-on mental subset: OR4, OR5, OR11, OR12, OR13, OR24, AR5, AR12, AR17, OR44, OR45, OR58, OR59, OR60, OR63, OR66, OR67, OR68, OR70, OR73.

### Implementation
OR17. Every new implementation has corresponding test file with passing tests.

OR18. Test deletion is scope deviation. STOP if specified test can't pass.

### Command execution
OR19. Zero output is data, not success. Re-run with confirmation command.

OR20. Never re-run failing test without root cause.

OR21. If plan step impossible as written, STOP immediately.

OR22. Never `git commit --no-verify`. Fix hook issues.

OR23. Never exclude files from hooks to bypass errors. STOP if out-of-scope.

OR24. Execute plan steps in strict numerical order. Don't jump ahead.

OR25. Minimize command output. `tail -n N` (default 5) unless full needed. Never >20 lines without truncation. pytest exempt (always `-vvv`).

### Dependencies
OR26. Runtime deps in `txt/requirements.txt` only. Dev tools in `pyproject.toml [project.optional-dependencies] dev`.

OR27. `detect-secrets scan` must exclude vendored/build dirs. Audit via `detect-secrets audit`, never manual JSON edit.

OR28. Edit tool for empty files, not `echo "" >`.

OR29. Multi-line commits use multiple `-m` flags, not embedded newlines.

OR30. Shell redirection for >1KB output unreliable. Use `tee` or Edit tool.

OR31. Workflow files = structured markdown. Edit tool only, never `sed`.

OR32. Project-local venv at `.venv/`. Create via `py -3.11 -m venv .venv`.

OR33. Absolute venv paths in all commands. No `source activate`.

OR34. Mypy on `.py` files only.

### Web
OR35. FastAPI web app runs as separate process. Imports from `sovereignai/` only via public API surface.

OR36. SSE auth via HTTP session cookie. No query-param tokens.

OR37. Web-layer DTOs in `web/schemas.py`. Core types never returned directly from HTTP.

OR38. Adapters declare `health_check()`. Failed check = DEGRADED status, not skipped.

### Conformance
OR39. Capability classes have conformance tests. Fail-closed for first-party, fail-open for third-party. <100ms each, cached per `(component_id, content_hash)`.

OR40. Contract tests verify backward compatibility. Failure blocks build.

OR41. Property-based tests run every commit. CI gate blocker.

OR42. Test deps (`hypothesis`, `pytest-cov`) in `pyproject.toml` only.

### Close workflow
OR43. Run workflow commands verbatim. Re-read workflow files fresh each run.

OR44. Never edit AR check scripts or tests to make failure pass.

OR45. `/close` is mandatory and atomic. All steps or STOP. Steps conditional on plan type may be marked "N/A — <reason>" in execution log. Steps never silently skipped.

OR46. `git add -A` for ALL commits. Verify with `git status -s` after.

OR47. Tag only after final commit verified. Never force-push a tag.

OR48. Coverage ≥89% at `/close` for `.py`-editing plans. N/A = STOP. >5% drop = STOP.

OR49. Update Bandit baseline in PLANS.md at every `/close` where tests added/removed.

OR50. After quota interrupt, re-read plan + AGENTS.md before continuing.

OR51. `git add -A` is the ONLY staging command. No explicit file lists.

OR52. Rule/landmine numbers never renumbered. Gaps permanent. (This rule prevents future renumbering — the current renumber is a one-time event.)

OR53. Backend + UI in same plan. No backend without UI surface (unless explicitly deferred).

### Memory
OR54. Memory backends pluggable via CapabilityGraph. Not hardcoded.

OR55. SQLite backends own separate files. Procedural = JSON. Working = in-process.

OR56. Crash recovery: check `~/.sovereignai/.shutdown_marker`. Skip if exists. Mark non-terminal tasks FAILED. Wrapped in try/except.

OR57. Durable backends use atomic writes. SQLite = WAL + transactions. JSON = temp + `os.replace()`. Locks never force-acquired.

### Workflow optimization (post-18.3)
OR58. Plan deliverables ship in full or explicitly defer per item. Deferred items listed by number in execution log + close report + DEBT.md with target plan. Silently dropping sub-items = STOP.

OR59. "Already done" claims require executed verification (test, curl, script, browser action). Reading code is NOT verification.

OR60. Test, mypy, and static-analysis failures have no "pre-existing" exemption. Fix, document in DEBT.md with target plan, or get User authorization per item. "Coverage: N/A" = STOP.

OR61. Skipped tests carry `# TODO(prompt-N): reason`. "Consecutive" = three successive plans where the test file was in scope. Tests skipped ≥3 consecutive prompts must be fixed, deleted, or escalated.

OR62. CHANGELOG must not claim unshipped scope. If Phase 6 shipped only tab nav, say so.

OR63. HTML/CSS/JS syntax validation before tests. HTML: `python -c "from html.parser import HTMLParser; HTMLParser().feed(open('<file>').read())"`. JS: `node --check <file>`. CSS: tinycss2. Failure = STOP.

OR64. Web UI plans require browser smoke test at `/close`. Screenshots + DOM snapshots to execution log. "Manual verification available" without doing it = STOP.

OR65. Tests use real-shape fixtures. No simplified shapes that hide production bugs.

OR66. Stray-file pre-commit scan: `git status -s` after `git add -A`. Verify no unintended files staged.

OR67. Re-read plan at start of each phase. Don't rely on cached mental model.

OR68. Universal Tracing Mandate. Every function with side effects emits ≥1 trace event. "Side effects" = any of: file I/O, network calls, subprocess, DB mutation, exception handling, state mutation. "Pure" = no I/O, no mutation, no exceptions (mechanically: function body contains only `return` of a computed value). Abstract/dunder/dataclass-init/property exempt. `check_tracing.py` classifies mechanically — self-declared exemptions rejected.

OR69. Correlation IDs propagate from entry point through all downstream calls via context var.

OR70. Placeholder code must not ship as "complete". Mechanically enforced via AST check in `/close`: `# TODO`, `# FIXME`, `# HACK`, `# XXX`, `# NAIVE`, `# TEMP`, `# placeholder`, `# stub`, `# In a real implementation`, `# NotImplemented`, `pass`-only bodies, `...`-only bodies, `raise NotImplementedError`, empty function bodies, trivial returns (`return None`/`[]`/`{}`/`""`/`0`/`False` as sole body line — exempt: `@property`, `__init__`, functions with `# INTENTIONAL` comment), `cast(Any, ...)`. Detection via `scripts/ar_checks/check_placeholders.py` (AST-based). Note: syntactic floor — semantic placeholders caught by OR73 spec-match review. Legitimate `# TODO` for deferred work allowed only if matched against DEBT.md entry per OR58 — `check_placeholders.py` cross-references DEBT.md before STOPping.

OR71. User-authorized exceptions need target plan documentation. "Deferred to next prompt" without plan number = STOP.

OR72. `check_tracing.py` AR check enforces OR68. Exit 0 required.

OR73. Post-execution spec-match review mandatory. At `/close` step 16, run `scripts/ar_checks/spec_match.py` — mechanical gate. Exit≠0 = STOP. Checks: regex-extract `\bOR\d+\b` from plan text, diff against AGENTS.md OR list, run `check_placeholders.py` on diff-scoped files, verify test result file exists + non-empty, verify screenshot files exist + >1KB, verify file list matches plan scope, detect scope contraction. If Claude available, also paste plan + full git diff + test results + screenshots for semantic review — `match=false` or any array non-empty = STOP. Both layers must pass.

---

## Landmines → Rules

| L | Rule | Problem |
|---|------|---------|
| L1 | OR4 | replace_all corrupts adjacent lines |
| L2 | OR3 | Parallel scan tools corrupt output |
| L3 | OR6 | PowerShell -replace corrupts markdown |
| L4 | OR9 | Temp files in repo root get committed |
| L5 | OR44 | Vulture flags unused fixtures |
| L6 | OR14 | Naive/aware datetime mixing |
| L7 | close.md step 13 | Stale baselines propagate |
| L8 | OR12, OR16 | Scope drift |
| L9 | OR17 | Interface changes break tests |
| L10 | OR22 | Bypassed hooks with --no-verify |
| L11 | OR23 | Excluding files from hooks |
| L12 | OR24 | Steps out of order |
| L13 | OR28, OR30 | Shell redirection fails in Git Bash |
| L14 | OR29 | Multi-line commits fail in Git Bash |
| L15 | OR27 | detect-secrets scans .venv |
| L16 | OR45 | Skipped /close steps |
| L17 | OR31 | sed on workflow files |
| L18 | OR32 | python/pip different interpreters |
| L19 | OR33 | source activate doesn't persist |
| L20 | OR34 | Mypy on non-Python files |
| L21 | OR43 | Paraphrased workflow commands |
| L22 | OR44 | Weakened tests to pass |
| L23 | OR46 | mv + git add leaves old path tracked |
| L24 | OR46 | Auto-fixed files missed by explicit add |
| L25 | OR47 | Premature tag |
| L26 | OR48 | Coverage skipped/unmeasured |
| L27 | OR49 | Bandit count drifted |
| L28 | OR50 | Quota exhaustion context loss |
| L29 | close.md fix | git rm deleted files |
| L30 | OR54, OR60 | Disabled production features to pass tests |
| L31 | OR19 | Command errored without investigation |
| L32 | OR21 | Command errored in verification treated as non-blocking |
| L33 | OR68 | Filtered on non-existent event attribute |
| L34 | OR60 | Mypy errors dismissed as "pre-existing" |
| L35 | OR54 | Memory backends not registered in container |
| L36 | OR56 | Crash recovery disabled |
| L37 | OR58 | Plan shipped with placeholder |
| L38 | OR59 | "Already done" without verification |
| L39 | OR60 | Test failures dismissed as "pre-existing" |
| L40 | OR61 | Skipped tests without target plan |
| L41 | OR62 | CHANGELOG claimed unshipped scope |
| L42 | OR63 | HTML/CSS/JS not validated |
| L43 | OR65 | Tests used incorrect fixture shapes |
| L44 | OR64 | Web UI lacked browser smoke test |
| L45 | OR66 | Stray files in commits |
| L46 | OR73 | Critical rules dropped from plan spec |

---

## LANDMINES.md — when to read/write

**Read**: Architect before new plans · Executor on-demand if rule ambiguous.

**Write** at `/close` step 14.6. Format:
```
## L{n} — <title>
**Trigger**: <plan, step, command/file>
**Impact**: <what broke>
```
Append-only. Never edit or remove.
