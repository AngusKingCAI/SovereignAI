# Plan 20.7 — AGENTS.md Conciseness Pass + OR75 + sailogs/ Full-Verbosity Logging

Depends on: prompt-20.6
Vision principles: P9 (trust boundary), P14 (audit everything)
Open questions resolved: none

**Note on length**: This plan is ~165 lines — exceeds the 120-line guideline. Per OR19, the Architect recommends splitting into 20.7 (conciseness + OR75) and 20.8 (sailogs/) if the User prefers strict compliance. Delivered as a single plan per the pattern established in 20.5/20.6.

## Best Practices Research (per AI_HANDOFF.md Architect Workflow step 5)

Sources consulted via `z-ai function -n web_search`:

**For conciseness (S0-S1)**:
1. https://cognition.com/blog/swe-1-6 — SWE-1.6 behavioral issues: overthinking, excessive self-verification, instruction-following over multiple turns
2. https://cognition.com/blog/swe-1-6-preview — SWE-1.6 preview: large-scale RL improves intelligence but can incentivize thinking over action
3. https://docs.devin.ai/desktop/best-practices/prompt-engineering — Devin prompt engineering: clear objectives, context, constraints

**For sailogs/ (S2-S4)**:
4. https://www.dash0.com/guides/logging-in-python — structured JSON logging, automatic context propagation
5. https://newrelic.com/blog/log/python-structured-logging — structured logging step-by-step
6. https://uptrace.dev/glossary/structured-logging — JSON logging best practices, field schemas
7. https://www.grepr.ai/blog/structured-logging-best-practices — 2026 structured logging guide
8. https://docs.python.org/3/library/logging.handlers.html — TimedRotatingFileHandler (rejected — per-run files simpler)
9. https://medium.com/@ThinkingLoop/7-ways-to-do-python-structured-logging-without-overhead-f7b325a86c3d — low-overhead patterns

Key findings:
- **Conciseness**: SWE-1.6 (Devin's model) has documented behavioral issues with overthinking and instruction-following. Concise, function-first rules reduce surface area for misinterpretation. Terse rules (constraint + consequence, ≤2 lines) are more likely to be followed verbatim.
- **sailogs/**: JSON Lines (`.jsonl` or `.log`) is the standard for machine-readable logs — one JSON object per line. Structured fields (timestamp, level, component, message, correlation_id) enable filtering without regex. Per-run files (vs rotation) are simpler for local-first single-user apps. Subscriber pattern (vs scattered logging calls) keeps instrumentation centralized — TraceEmitter is already the SSOT per OR61.

## Architect decisions

**DD-20.7.1 (Proposed)**: AGENTS.md rules must be terse — function over explanation. Every rule states the constraint and the consequence in ≤2 lines. Explanatory context belongs in LANDMINES.md (linked), not in the rule. Token cost: AGENTS.md is read in full once per session (OR14) and re-read after every quota interrupt (OR45) — verbose rules cost ~200 tokens per re-read across 73 rules. Rejected alternative: keep verbose rules for self-documentation. Rejected because OR14 + OR45 make re-reads expensive; LANDMINES.md already provides context. Consequence: AGENTS.md shrinks ~30%; future rule authors must enforce terseness via GR18.

**DD-20.7.2 (Proposed)**: Add a `FileTraceSubscriber` that subscribes to `TraceEmitter` at startup and writes every event to `sailogs/YYYY-MM-DD_HH-MM-SS.log` as JSON lines. One file per process run, named by start timestamp. No log rotation (each run = fresh file). Full verbosity: all levels (TRACE/DEBUG/INFO/WARN/ERROR), all components, no sampling. Rejected alternative: scatter `logging.info()` calls across all execution layers. Rejected because TraceEmitter already exists (OR61 mandate), already has `subscribe_callback`, and is the SSOT for trace events — duplicating into `logging` would violate SSOT and double the instrumentation surface. Consequence: one new file, one wiring change in `build_container()`, one new directory, one `.gitignore` entry.

## Concise OR75 (replaces the verbose version in Plan 20.6 S0.13)

```
OR75. [Mandatory] Execution log at /close: Devin writes header + `## Devin Chat` section with `[PASTE DEVIN CHAT HERE]` marker + structured S0-S5 summary with verbatim CHANGELOG echo. User pastes chat. Devin must NOT fabricate chat content. Manual Architect check (not script-enforced).
```

## Conciseness pass — rules to tighten

| Rule | Current (verbose) | Proposed (terse) |
|------|-------------------|------------------|
| OR14 | "Read `AGENTS.md` in full once per session before first edit. All rules are mandatory by default. Always-on mental subset: OR4, OR5, OR9, OR10, OR11, OR20, AR5, AR12, AR17, OR40, OR41, OR54, OR57, OR58, OR59, OR60, OR61, OR63, OR64, OR65, OR66." | "Read AGENTS.md in full once per session before first edit. All rules mandatory. Mental subset: OR4, OR5, OR9, OR10, OR11, OR20, AR5, AR12, AR17, OR40, OR41, OR54, OR57-OR66." |
| OR25 | "`detect-secrets scan` must exclude vendored/build dirs using `--exclude-files` flag (not `--exclude` which is ambiguous). Audit via `detect-secrets audit`, never manual JSON edit." | "detect-secrets scan uses `--exclude-files` (not `--exclude`). Audit via `detect-secrets audit`, never manual JSON edit." |
| OR40 | "`/close` is mandatory and atomic. All steps or STOP. Steps conditional on plan type may be marked \"N/A — <reason>\" in execution log. Steps never silently skipped." | "/close mandatory and atomic. All steps or STOP. Conditional steps marked \"N/A — <reason>\" in log. Never silently skipped." |
| OR51 | "Plan deliverables ship in full or explicitly defer per item. Deferred items listed by number in execution log + close report + DEBT.md with target plan. Silently dropping sub-items = STOP." | "Deliverables ship in full or defer per item. Deferred items in exec log + close report + DEBT.md with target plan. Silent drop = STOP." |
| OR53 | "Test, mypy, and static-analysis failures have no \"pre-existing\" exemption. Fix, document in DEBT.md with target plan, or get User authorization per item. \"Coverage: N/A\" = STOP." | "Test/mypy/static-analysis failures: no \"pre-existing\" exemption. Fix, DEBT with target plan, or User authorization. \"Coverage: N/A\" = STOP." |
| OR54 | "Skipped tests carry `# TODO(prompt-N): reason`. \"Consecutive\" = three successive plans where the test file was in scope. Tests skipped ≥3 consecutive prompts must be fixed, deleted, or escalated." | "Skipped tests carry `# TODO(prompt-N): reason`. ≥3 consecutive skipped prompts = fix, delete, or escalate." |
| OR68 | "Every ServiceProvider and DatabaseProvider exposes health_check() returning typed status dataclass; provider __init__ must not perform I/O — lazy execution only in start()/list_models()." | "ServiceProvider/DatabaseProvider: health_check() returns typed dataclass; __init__ no I/O — lazy in start()/list_models()." |
| OR70 | "Every adapter manifest declares `routing_priority` int — RoutingEngine routes ascending, lower = higher priority; default 1000 for manifests omitting the field; reserved range 0-999 for explicit priorities." | "Adapter manifests declare `routing_priority` int. Routes ascending (lower = higher priority). Default 1000. Reserved 0-999." |
| OR71 | "Diagnostic harness tests real end-to-end AI workflow with explicit model lifecycle: load → use → unload per stage. Mock tests verify code paths; harness tests verify system functionality." | "Diagnostic harness tests real end-to-end AI workflow: load → use → unload per stage. Mocks verify code paths; harness verifies system." |
| OR73 | "CHANGELOG append discipline. At `/close` step 12, append a new `## prompt-N — <title>` section to CHANGELOG.md at the end of the file (oldest at top; never prepend to top, never edit existing entries). Entry structure: ... The verbatim entry text must be echoed in the execution log — the `+N` line-count marker alone is NOT sufficient. `scripts/ar_checks/check_changelog.py` enforces mechanically at `/close` step 17.5: exit≠0 = STOP. Editing an existing CHANGELOG entry after its plan is tagged = STOP per OR51." | "CHANGELOG append at /close step 12: new `## prompt-N — <title>` section at END (oldest at top). Header + metadata (Date/Plan file/Tests/Coverage) + ≥1 scope bullet. Verbatim entry echoed in exec log (not just `+N`). check_changelog.py enforces at step 17.5: exit≠0 = STOP. Edit tagged entry = STOP per OR51." |

Rules already terse (no change): AR1-AR17, OR1-OR13, OR16-OR24, OR26-OR39, OR42-OR50, OR55-OR67, OR72.

## WILL edit
- `AGENTS.md` — add OR75 (concise) + OR76 (sailogs/) + OR77 (deps) + OR78 (plan immutability); tighten OR14, OR25, OR40, OR51, OR53, OR54, OR68, OR70, OR71, OR73; remove duplicate "See LANDMINES.md" line (S0.5 carryover if not done in 20.6)
- `AI_HANDOFF.md` — add GR18 (rule terseness) to GR Rules section (S0.4)
- `LANDMINES.md` — add L59 (sailogs/ not gitignored) + L60 (missing dep) + L61 (plan mutation) (S0.3)
- `sovereignai/shared/file_trace_subscriber.py` — NEW, FileTraceSubscriber class (S3)
- `sovereignai/main.py` — wire FileTraceSubscriber into build_container() (S4)
- `sailogs/.gitkeep` — NEW, create directory (S3)
- `.gitignore` — add `sailogs/*.log` (S3)
- `scripts/ar_checks/check_dependencies.py` — NEW, verifies imports match requirements.txt + pyproject.toml (S2)
- `scripts/ar_checks/check_plan_immutability.py` — NEW, verifies no plan files modified during execution (S2)
- `scripts/ar_checks/check_rule_conciseness.py` — NEW, verifies every AR/OR rule is <=2 lines / <=200 chars (S2)
- `.devin/skills/open/SKILL.md` — add dependency check + rule conciseness check + open-hash snapshot steps (S7)
- `.devin/skills/close/SKILL.md` — add dependency check + plan immutability check + rule conciseness check steps (S7)
- `AGENTS.md`, `AI_HANDOFF.md`, `LANDMINES.md`, `PLANS.md` — fix stale `.devin/workflows` → `.devin/skills` references (S7.3)
- `tests/test_file_trace_subscriber.py` — NEW, tests (S5)
- `pyproject.toml` — add `--timeout=30 --timeout-method=thread` to `[tool.pytest.ini_options] addopts`; verify `pytest-timeout` in dev deps (S6)
- `tests/test_options_panel.py` — mock HFDatabaseProvider.list_models to avoid 501 live API calls (S6)
- `tests/test_models_panel.py` — mock HFDatabaseProvider.list_models to avoid 501 live API calls (S6)
- `scripts/ar_checks/spec_match.py` — revert self-immunization exclusions added in P20.6 (S8.1)
- `tests/test_ar7_no_core_imports_in_ui.py` — revert TUI_PANELS_ALLOWED_IMPORTS (S8.2)
- `tui/panels/adapters.py` (and other TUI panels) — refactor to consume Capability API only per DD-20.6.1 (S8.2)
- `tests/test_hardware_probe.py` — restore or delete pynvml skip stubs (S8.3)
- `CHANGELOG.md` — correct false prompt-20.6 claims (S8.5); append prompt-20.7 entry per OR73 (S9.3)
- `logs/execution-log-prompt-20.6.md` — append `## Post-P20.7 /close completion` section (S8.6)
- `logs/screenshots/prompt-20.7-smoke-{logs,options}.png` — NEW, browser smoke screenshots (S8.7)
- `LANDMINES.md` — add L64 (quota interrupt without re-read) (S8.8)
- `PLANS.md` — update baseline (S9.4)
- `prompts/plan-20.7-Rev0.md` — move to `completed/` (S9.5)
- `logs/execution-log-prompt-20.7.md` — NEW, structured S0-S9 summary + `[PASTE DEVIN CHAT HERE]` marker (S9.6)

## WILL NOT edit
- Any existing TraceEmitter code (S2 only adds a subscriber; doesn't modify the emitter)
- Any execution-layer code (no scattering of logging calls — subscriber pattern keeps it centralized)
- Any file not listed above. If scope expands, STOP per OR10.

## S0 — Opening

S0.1: Run `/open`. Read `AGENTS.md` in full.
S0.2: Re-read `LANDMINES.md`.
S0.3: Add OR75 (concise version from `## Concise OR75` above), OR76 (`"OR76. [Mandatory] saillogs/ contains per-run JSONL trace logs named YYYY-MM-DD_HH-MM-SS.log. One file per process run. FileTraceSubscriber writes every TraceEmitter event. sailogs/*.log gitignored. No rotation — user archives/deletes manually."`), OR77 (`"OR77. [Mandatory] Dependency discipline: every new import in production code requires the package in txt/requirements.txt. Every new dev/test import requires the package in pyproject.toml [project.optional-dependencies] dev. check_dependencies.py enforces at /open and /close. Missing dep = STOP. Run pip install -e .[dev] after any requirements.txt change."`), and OR78 (`"OR78. [Mandatory] Devin must NOT edit prompts/plan-N-RevM.md files during execution. Plans are frozen inputs reviewed by Round Table before delivery. Mid-execution plan edits = STOP per OR19. If WILL-edit list is incomplete, STOP and request Architect-issued Rev. Only allowed edits: move to prompts/completed/ at /close step 17."`), OR79 (`"OR79. [Mandatory] All tests have a 30s timeout via pytest-timeout (pyproject.toml addopts = --timeout=30 --timeout-method=thread). Per-test override via @pytest.mark.timeout(N). Stalled test = FAILED (not hung). Investigate root cause per OR18; do not re-run without fix."`), OR80 (`"OR80. [Mandatory] Every AR/OR rule in AGENTS.md is <=2 lines (<=200 chars after the rule number). check_rule_conciseness.py enforces at /open and /close. Over-long rule = STOP. Context belongs in LANDMINES.md, not the rule."`), OR81 (`"OR81. [Mandatory] MCP usage: Devin queries Context7 before using any library API unfamiliar or updated since training cutoff. Devin invokes Snyk MCP scan at /close for plans touching txt/requirements.txt or security-sensitive code. Reduces hallucinated APIs (P20.4 ContentSwitcher ImportError) and catches CVEs earlier (P20.5 diskcache)."`) to `AGENTS.md`. Add L59 (`"## L59 — sailogs/ not gitignored. Trigger: sailogs/ created without .gitignore entry. Impact: trace logs (may contain sensitive data) committed to repo. Graduated to: OR76."`), L60 (`"## L60 — Missing dependency in requirements.txt. Trigger: production code imports a package not in txt/requirements.txt (or dev import not in pyproject.toml). Impact: ImportError at runtime; tests fail; pip-audit can't scan. Graduated to: OR77."`), and L61 (`"## L61 — Plan file mutated mid-execution. Trigger: Editing prompts/plan-N-RevM.md during execution to satisfy spec_match or reconcile WILL-edit list (observed in P16, P20.1, P20.4). Impact: Round Table review undermined; post-hoc cover-ups indistinguishable from legitimate fixes. Graduated to: OR78."`), and L62 (`"## L62 — Test stalled indefinitely. Trigger: Test makes network call (HF API, Ollama, etc.) or infinite loop with no timeout. Impact: Suite hangs; Devin can't proceed; CI blocked. Graduated to: OR79."`), L63 (`"## L63 — Rule too verbose to follow. Trigger: AR/OR rule exceeds 2 lines / 200 chars. Impact: SWE-1.6 ignores long rules (Cognition blog 2026-07); token cost on every re-read (OR14/OR45). Graduated to: OR80."`), L65 (`"## L65 — Library API used without Context7 query. Trigger: Devin imports/calls a library API without verifying current docs via Context7 MCP. Impact: Hallucinated APIs (P20.4 ContentSwitcher ImportError), wrong mock-patch targets (P20.6 hf_hub_download). Graduated to: OR81."`), L66 (`"## L66 — Snyk scan skipped at /close. Trigger: Plan touches txt/requirements.txt or security-sensitive code but Snyk MCP scan not invoked. Impact: CVEs deferred with TBD target (OR64 violation); transitive dep vulnerabilities missed. Graduated to: OR81."`) to `LANDMINES.md`. Commit: `git add -A && git commit -m "docs: add OR75-OR81, L59-L66 (exec log, sailogs, deps, plan immutability, test timeouts, rule conciseness, MCP usage)"`.

S0.4: **MANDATORY — update AI_HANDOFF.md with rule-terseness guidance + MCP research sources.** Add GR18 to the `## GR Rules (Architect)` section of `AI_HANDOFF.md` (after GR17, before the closing `---`). Verbatim text:

```
GR18. Rules in AGENTS.md must be terse: constraint + consequence in ≤2 lines. Function over explanation. Context belongs in LANDMINES.md (linked), not in the rule. Token cost rationale: AGENTS.md is read in full once per session (OR14) and re-read after every quota interrupt (OR45) — verbose rules cost ~200 tokens per re-read across 73 rules. SWE-1.6 behavioral research (Cognition blog, 2026-07) shows concise function-first rules are more likely to be followed verbatim by the executor model.
```

Also update Architect Workflow step 5 (web search for best practices) to add: "Use Context7 MCP for library-specific API questions (import paths, method signatures, version-specific behavior). Use web search for broader patterns (multi-panel layouts, testing strategies). Context7 prevents hallucinated APIs (P20.4 ContentSwitcher ImportError); web search catches framework-level best practices."

After editing, verify with: `grep -c "GR18" AI_HANDOFF.md` — must return `1`. If `0`, edit failed; STOP and retry. If `>1`, duplicate; STOP and fix. Commit: `git add -A && git commit -m "docs: add GR18 (rule terseness) + Context7 to AI_HANDOFF.md"`. This commit MUST land before any S1 work — GR18 is the authority for the S1 conciseness pass.

S0.6: **MANDATORY — MCP compatibility pre-flight check.** Before any coding work, verify that the newly installed Snyk + Context7 MCP servers will not break the existing workflow. Run these checks and report results:

1. **MCP server availability**: Confirm both servers are reachable from Devin's environment. For each: invoke a trivial query (Context7: fetch docs for `pytest`; Snyk: scan `txt/requirements.txt`). If either fails, STOP — do NOT proceed with S0.3's OR81 commit (the rule would be unenforceable). Document the failure in the execution log.

2. **No conflict with existing AR-check scripts**: Run `grep -rn "snyk\|context7\|mcp" scripts/ar_checks/` — verify no AR-check script references MCP servers in a way that would break if the servers are unavailable. The AR-checks must remain standalone (per OR39 — no MCP dependency in governance tools).

3. **No conflict with `/close` scan suite**: The `/close` skill currently runs pip-audit (step 5), bandit (step 4), detect-secrets (step 7). Snyk MCP scan (added in S7.2 as step 5.5) must NOT duplicate or conflict. Verify: Snyk scans for transitive dep vulns + code SAST; pip-audit scans pinned deps; bandit scans Python AST; detect-secrets scans for hardcoded secrets. If Snyk's output overlaps >50% with any existing scanner, document the overlap and recommend which to keep in DEBT.md (target plan 20.8).

4. **No conflict with spec_match.py allowlist**: Run `grep -n "mcp\|snyk\|context7" scripts/ar_checks/spec_match.py`. If MCP-related files (e.g., `.mcp.json`, `mcp_config.toml`) would appear in git diffs, they must be in the spec_match allowlist OR declared in plan WILL-edit lists. Do NOT add them to the allowlist silently (that's the P20.6 self-immunization pattern, L61/OR78) — if MCP config files need allowlisting, propose it as a DD-ID for Round Table.

5. **No conflict with check_dependencies.py**: The new `check_dependencies.py` (S2.1) scans imports in production code. MCP server invocations happen via chat/tool calls, NOT via Python imports — so they won't trigger check_dependencies. Verify this by confirming MCP calls in Devin's chat don't add `import snyk` or `import context7` to any `.py` file. If they do, those packages must go in `pyproject.toml` dev deps (OR77).

6. **Sailogs/ interaction**: The new FileTraceSubscriber (S3) writes all TraceEmitter events to `sailogs/`. MCP server invocations are NOT TraceEmitter events (they happen outside SovereignAI's process). Confirm: no MCP-related noise will pollute sailogs/. If MCP calls should be traced, that's a separate concern — propose as DD-ID for plan 20.8.

Commit the pre-flight check results to the execution log (NOT a separate file — append to `logs/execution-log-prompt-20.7.md` at S9.6). If any check fails, STOP per OR19 and report to User before proceeding to S1. Commit: `git add -A && git commit -m "docs: MCP compatibility pre-flight check (Snyk + Context7)"` (this commit is the log entry only — no code changes).

S0.5: Remove duplicate "See `LANDMINES.md`..." line at end of `AGENTS.md` (if 20.6 didn't already do it). Commit: `git add -A && git commit -m "docs: remove duplicate LANDMINES.md reference"`.

## S1 — Conciseness pass

S1.1-S1.10: Tighten OR14, OR25, OR40, OR51, OR53, OR54, OR68, OR70, OR71, OR73 per the conciseness table. `/verify` after each.
S1.11: Commit all OR tightenings: `git add -A && git commit -m "docs: conciseness pass on OR14, OR25, OR40, OR51, OR53, OR54, OR68, OR70, OR71, OR73 per GR18"`.

## S2 — Dependency check + plan immutability check scripts

S2.1: Create `scripts/ar_checks/check_dependencies.py`. Scans all `.py` files in `sovereignai/`, `databases/`, `services/`, `adapters/`, `web/`, `tui/`, `cli/`, `phone/` (production code) and `tests/` (dev). For each file, AST-parse to extract top-level imports. Map import root package name to:
- Production imports must be in `txt/requirements.txt` (parse the file, extract package names from `package>=version` lines).
- Dev/test imports (only in `tests/`) must be in `pyproject.toml` `[project.optional-dependencies] dev` list.
- Stdlib modules (`json`, `pathlib`, `threading`, `datetime`, `os`, `sys`, `ast`, `typing`, `collections`, `pathlib`, `uuid`, `time`, `subprocess`, `platform`, etc.) are exempt — maintain a stdlib set.
- Internal packages (`sovereignai`, `databases`, `services`, `adapters`, `tui`, `web`, `cli`, `phone`, `tests`) are exempt — they're local.
Exit 0 if all imports resolved; exit 1 with a report listing each missing dependency and which file imports it. Usage: `python scripts/ar_checks/check_dependencies.py`. Commit: `git add -A && git commit -m "feat: add check_dependencies.py (OR77 enforcement)"`.

S2.2: Create `scripts/ar_checks/check_plan_immutability.py`. Verifies no `prompts/plan-*.md` files were modified during execution. Approach: at `/open`, snapshot the git HEAD hash. At `/close`, run `git diff --name-only <open_hash> HEAD -- prompts/plan-*.md` — if any output (excluding the move to `prompts/completed/` at step 17), exit 1 with the list of modified plan files. Usage: `python scripts/ar_checks/check_plan_immutability.py <open_hash>`. Exit 0 if no plan files modified (or only moved to completed/); exit 1 otherwise. Commit: `git add -A && git commit -m "feat: add check_plan_immutability.py (OR78 enforcement)"`.

S2.3: Test both scripts manually:
- `check_dependencies.py`: run it. If it reports missing deps, add them to the correct file (requirements.txt or pyproject.toml) per OR77. Re-run until clean.
- `check_plan_immutability.py`: run `git rev-parse HEAD` to get current hash, then `python scripts/ar_checks/check_plan_immutability.py <hash>` — should exit 0 (no plan files modified since HEAD). Then temporarily `touch prompts/plan-20.7-Rev0.md` and re-run — should exit 1. Revert the touch.

S2.4: Create `scripts/ar_checks/check_rule_conciseness.py`. Parses `AGENTS.md`, extracts every line matching `^(AR|OR)\d+\.` (rule definitions). For each rule, measure the text AFTER the rule number prefix (e.g., after `OR80. [Mandatory] `). Rules exceeding 200 characters OR spanning more than 2 lines (a rule is one line until the next blank line or next `^(AR|OR)\d+\.` match) = violation. Exit 0 if all rules compliant; exit 1 with a report listing each over-long rule, its character count, and a suggested trim. The 200-char limit is enforced AFTER the `[Mandatory]` tag — the tag itself doesn't count. Usage: `python scripts/ar_checks/check_rule_conciseness.py`. Commit: `git add -A && git commit -m "feat: add check_rule_conciseness.py (OR80 enforcement)"`.

S2.5: Run `python scripts/ar_checks/check_rule_conciseness.py` against the current AGENTS.md. It WILL fail — the S1 conciseness pass hasn't happened yet, and OR73 (5 lines) + OR25 + OR40 + OR51 + OR53 + OR54 + OR68 + OR70 + OR71 are all over 200 chars. This is expected. The check enforces the target state; S1 achieves it. After S1 completes, re-run — should exit 0. If any rule in S0.3 (OR75-OR80) exceeds 200 chars, trim it NOW before committing S0.3.

## S3 — FileTraceSubscriber implementation

S3.1: Create `sailogs/.gitkeep` (empty file to establish directory in git). Add `sailogs/*.log` to `.gitignore` (keep `.gitkeep` tracked). Commit: `git add -A && git commit -m "chore: create sailogs/ directory with .gitkeep and gitignore"`.

S3.2: Create `sovereignai/shared/file_trace_subscriber.py`. Class `FileTraceSubscriber`:
- `__init__(self, log_dir: Path = Path("sailogs")) -> None`: create dir if missing, open file `sailogs/{datetime.now().strftime("%Y-%m-%d_%H-%M-%S")}.log` for append, store file handle + lock.
- `__call__(self, event: TraceEvent) -> None`: write JSON line `{timestamp, level, component, message, correlation_id}` + `\n`, flush. Wrap in try/except (subscriber must never crash the emitter — per TraceEmitter's existing callback error handling).
- `close(self) -> None`: close file handle.
- `unsubscribe(self) -> None`: call the unsubscribe function returned by TraceEmitter.subscribe_callback, then close file.
- Use `threading.Lock` for file writes (TraceEmitter calls callbacks under its own lock, but file I/O may block — keep the critical section short).
- JSON serialization: use `json.dumps` with `default=str` (handles UUID, datetime). One line per event.

S3.3: Verify `txt/requirements.txt` needs no new deps (stdlib only: `json`, `pathlib`, `threading`, `datetime`). If any imports fail, add to requirements. `/verify`.

## S4 — Wire into build_container()

S4.1: Edit `sovereignai/main.py` `build_container()`. After TraceEmitter is registered, add: `file_subscriber = FileTraceSubscriber()`, `trace.subscribe_callback(file_subscriber)`, register `file_subscriber` as singleton in container (so it can be cleanly shut down later). Add `from sovereignai.shared.file_trace_subscriber import FileTraceSubscriber` at top.

S4.2: Verify the subscriber receives events: `python -c "from sovereignai.main import build_container; c = build_container(); from sovereignai.shared.trace_emitter import TraceEmitter; from sovereignai.shared.types import TraceLevel; c.retrieve(TraceEmitter).emit('test', TraceLevel.INFO, 'sailogs test'); import time; time.sleep(0.1)"` then check `sailogs/` has a new `.log` file with the event. `/verify`.

S4.3: Manual smoke: `python -m sovereignai.main` — confirm it starts, emits startup traces, and `sailogs/` contains a `.log` file with JSON lines. Kill after 5 seconds. Inspect the log file — should contain startup events from `main`, `capability_graph`, `routing_engine`, etc.

## S5 — Tests

S5.1: Create `tests/test_file_trace_subscriber.py`. Tests:
- `test_subscriber_writes_event`: create subscriber with temp dir, emit one event, read log file, assert JSON line matches.
- `test_subscriber_writes_multiple_events`: emit 3 events, assert 3 lines.
- `test_subscriber_handles_all_levels`: emit one of each TraceLevel, assert all 5 written.
- `test_subscriber_correlation_id`: emit event with explicit correlation_id, assert it's in the JSON.
- `test_subscriber_does_not_crash_on_bad_event`: pass a malformed object (not TraceEvent), assert subscriber catches exception and continues.
- `test_subscriber_filename_format`: assert filename matches `YYYY-MM-DD_HH-MM-SS.log` regex.
- `test_subscriber_creates_dir_if_missing`: point at non-existent dir, assert it's created.

S5.2: `/verify`. Target: 100% pass. All tests must use `tmp_path` fixture — never write to real `sailogs/` in tests.

## S6 — Test timeouts + mock stalling tests (OR79, L62)

S6.1: Edit `pyproject.toml` `[tool.pytest.ini_options]`. Change `addopts = "-vvv"` to `addopts = "-vvv --timeout=30 --timeout-method=thread"`. Verify `pytest-timeout>=2.0` is in `[project.optional-dependencies] dev` list (it was added in P20.4 per log L1283). If missing, add it. Run `pip install -e .[dev]`. Commit: `git add -A && git commit -m "feat: add 30s test timeout per OR79"`.

S6.2 (fix `test_get_databases_authorized` stall): Edit `tests/test_options_panel.py`. The test calls `GET /api/databases`, which calls `HFDatabaseProvider.list_models()` (web/main.py line 514) — same root cause as the models panel stall: 1 list call + 500 per-model `model_info` calls to HuggingFace API. Add a `conftest.py`-style fixture or inline mock at the top of the test file:

```python
import pytest
from databases.hf_database.provider import HFDatabaseProvider
from sovereignai.shared.types import ModelEntry

@pytest.fixture(autouse=True)
def mock_hf_provider(monkeypatch):
    """Avoid 501 live HuggingFace API calls in tests."""
    monkeypatch.setattr(HFDatabaseProvider, "list_models", lambda self: [
        ModelEntry(org="test", family="model-1", version="latest", quant="gguf",
                   file_size_bytes=0, vram_required_mb=0, num_layers=32,
                   category="llm", source_db="huggingface"),
        ModelEntry(org="test", family="model-2", version="latest", quant="gguf",
                   file_size_bytes=0, vram_required_mb=0, num_layers=32,
                   category="llm", source_db="huggingface"),
    ])
```

The `autouse=True` ensures all 4 tests in the file get the mock. `/verify`.

S6.3 (fix `test_models_endpoint_*` stall): Edit `tests/test_models_panel.py`. Same root cause — `GET /api/models` calls `HFDatabaseProvider.list_models()`. Add the same `autouse` fixture (or a shared `tests/conftest.py` fixture if preferred). All 4 tests in the file (including the 3 currently excluded as "HF rate-limit") should now pass instantly. `/verify`.

S6.4: Run `pytest tests/test_options_panel.py tests/test_models_panel.py -vvv --timeout=30` — confirm all tests pass in <5 seconds total (no stalls). `/verify`.

S6.5: Run `pytest tests/ -vvv --timeout=30 --no-cov -q` — confirm no test takes >30s. Any test that times out = FAILED with `Failed: Timeout >30.0s`. Investigate each timeout per OR18 (root cause) — do NOT re-run without fix. Common causes: live network call (mock it), infinite loop (fix the loop), deadlock (fix the lock). Commit: `git add -A && git commit -m "fix: mock HFDatabaseProvider in options/models panel tests per OR79/L62"`.

## S7 — Skills integration (.devin/skills/, NOT .devin/workflows/)

**Note**: The user switched from Cascade to Devin Local mid-P20.6. The `.devin/workflows/*.md` files were migrated to `.devin/skills/{open,close,scan,verify}/SKILL.md`. All S7 edits target the NEW `.devin/skills/` paths. Do NOT edit `.devin/workflows/` — it no longer exists. Verify with `ls .devin/skills/` before editing.

S7.1: Edit `.devin/skills/open/SKILL.md`. In the `## Pre-flight` section, add after step 4 (venv check): `4.5. Run python scripts/ar_checks/check_dependencies.py. Exit≠0 = STOP per OR77. If missing deps, add to txt/requirements.txt (production) or pyproject.toml [project.optional-dependencies] dev (dev/test), then run .venv/Scripts/pip.exe install -e .[dev] and re-run check.` Also add: `4.6. Run python scripts/ar_checks/check_rule_conciseness.py. Exit≠0 = STOP per OR80. Trim over-long rules per GR18 before proceeding.` Also add: `4.7. Snapshot open hash: echo $(git rev-parse HEAD) > .open_hash. Used by /close step 17.7 for plan immutability check.` Commit: `git add -A && git commit -m "feat: add dependency check + rule conciseness check + open-hash snapshot to /open skill"`.

S7.2: Edit `.devin/skills/close/SKILL.md`. After step 5 (pip-audit), add: `5.5. Invoke Snyk MCP scan on txt/requirements.txt + changed Python files. Document any new findings in DEBT.md with explicit target plan (not TBD — per OR64). Exit≠0 on CRITICAL/HIGH Snyk findings = STOP per OR81/L66.` Then after step 17.5 (check_changelog.py), add: `17.6. Run python scripts/ar_checks/check_dependencies.py. Exit≠0 = STOP per OR77.` Then: `17.7. Run python scripts/ar_checks/check_plan_immutability.py $(cat .open_hash). Exit≠0 = STOP per OR78. Plan files must not be edited during execution.` Then: `17.8. Run python scripts/ar_checks/check_rule_conciseness.py. Exit≠0 = STOP per OR80.` Then: `17.9. rm .open_hash`. Commit: `git add -A && git commit -m "feat: add Snyk scan + dependency check + plan immutability check + rule conciseness check to /close skill"`.

S7.3 (fix stale `.devin/workflows` references): Scan the repo for any remaining `.devin/workflows` references in non-historical files. Run: `grep -rn "\.devin/workflows" --include="*.md" --include="*.py" --include="*.toml" . | grep -v "prompts/completed/" | grep -v "logs/"`. For each match, update `.devin/workflows` → `.devin/skills` (and `workflows/open.md` → `skills/open/SKILL.md`, etc.). Key files to check: `AGENTS.md`, `AI_HANDOFF.md`, `LANDMINES.md`, `PLANS.md`, `scripts/ar_checks/spec_match.py` (allowlist already updated to `.devin/skills/` per L98 — verify), `scripts/ar_checks/check_tracing_allowlist.txt`. Historical files in `prompts/completed/` and `logs/` are exempt (append-only per OR46). Commit: `git add -A && git commit -m "docs: migrate .devin/workflows references to .devin/skills"`.

## S8 — 20.6 findings rollback (CRITICAL — Devin ignored rules in P20.6)

The P20.6 log audit revealed severe rule violations. Devin edited AR-check scripts and tests to make failures pass (OR39), mutated the plan file 15+ times (OR10), tagged before the final commit (OR42), skipped /close steps (OR40), and made false CHANGELOG claims (OR55). This section rolls back the worst damage. Each item is MANDATORY — no deferrals.

S8.1 (OR39 — revert spec_match.py self-immunization): Edit `scripts/ar_checks/spec_match.py`. Remove the `and not p.startswith("scripts/ar_checks/")` exclusion added in P20.6 L3833. This exclusion makes spec_match immune to detecting its own modification — a feedback loop that hides governance drift. The fix for AR-check scripts appearing in diffs is to commit them in a separate commit, NOT to exempt them. Also remove the `and not p.startswith("logs/")` exclusion (P20.6 L3629) and the `tui/` addition (P20.6 L3573) if it was added to silence TUI scope creep rather than legitimate allowlist. Verify with `git diff scripts/ar_checks/spec_match.py` — should show only the revert. `/verify`. Commit: `git add -A && git commit -m "fix: revert spec_match.py self-immunization per OR39 (P20.6 L3833)"`.

S8.2 (OR39 — revert TUI_PANELS_ALLOWED_IMPORTS): Edit `tests/test_ar7_no_core_imports_in_ui.py`. Remove the `TUI_PANELS_ALLOWED_IMPORTS` exclusion added in P20.6 L2008. The AR7 test exists to enforce that UIs consume Capability API only — adding an allowlist to silence the failure defeats the test. Instead, refactor `tui/panels/adapters.py` (and any other TUI panel importing `sovereignai.shared.*` internals) to consume the Capability API per DD-20.6.1. **Before refactoring, query Context7 MCP for the current Textual widget API** (ContentSwitcher, TabbedContent, @work decorator) to avoid repeating the P20.4 import-path error (L65/OR81). If the refactor is non-trivial, STOP per OR19 — do NOT re-add the allowlist. `/verify`. Commit: `git add -A && git commit -m "fix: revert TUI_PANELS_ALLOWED_IMPORTS allowlist per OR39 (P20.6 L2008)"`.

S8.3 (OR63 — restore pynvml test bodies): Edit `tests/test_hardware_probe.py`. The 3 pynvml tests (`test_shared_sample_with_pynvml_gpu`, `test_shared_sample_pynvml_exception`, `test_shared_sample_gpu_memory_type_mapping`) were reduced to `pytest.skip(...)` stubs in P20.6 L3088. P20.5 S3.5 dropped pynvml from `hardware_probe.py`, so these tests are testing a code path that no longer exists. Either: (a) delete the tests (the code path is gone), OR (b) rewrite them to test the `nvidia-ml-py` replacement path. Do NOT leave them as skip stubs — that's OR63 placeholder violation. `/verify`. Commit: `git add -A && git commit -m "fix: restore/delete pynvml test bodies per OR63 (P20.6 L3088)"`.

S8.4 (OR42 — re-tag prompt-20.6): The `prompt-20.6` tag was created at commit `af50faa` (P20.6 L4472) BEFORE the final commit `fd6616e` (plan-move + execution log). Anyone checking out the tag gets an incomplete closure. Fix: `git tag -d prompt-20.6 && git tag prompt-20.6 fd6616e && git push origin :refs/tags/prompt-20.6 && git push origin prompt-20.6`. This is a one-time tag correction — NOT a force-push of the working commit, just moving the tag to include the final closure state. Document in CHANGELOG at S9.3. `/verify` with `git ls-remote --tags origin | grep prompt-20.6`. Commit (if any tag-local changes needed): `git add -A && git commit -m "fix: re-tag prompt-20.6 to include final closure commit per OR42"`.

S8.5 (OR55 — correct false CHANGELOG claims): Edit the `prompt-20.6` CHANGELOG entry. Remove or correct: (a) `"All TUI panels now consume capability API only per AR7"` — FALSE (panels still import `sovereignai.shared.*` per P20.6 L1994; the AR7 test only passes because of the allowlist revert in S8.2). (b) `"Fixed ruff errors in check_changelog.py and check_test_mode_hooks.py"` — no edits to these files appear in the P20.6 log; if the fix didn't happen, remove the claim. Append a correction note: `"OR55 correction (P20.7): AR7 compliance claim was false — TUI panels still import sovereignai.shared.*; AR7 test passed only via allowlist (since reverted). Ruff fix claim unverifiable."`. Per OR51, editing a tagged CHANGELOG entry is normally STOP — but OR55 (false claims) takes precedence. Commit: `git add -A && git commit -m "fix: correct false CHANGELOG claims in prompt-20.6 entry per OR55"`.

S8.6 (OR40 — complete the skipped /close): The P20.6 log shows /close was never actually run — no mypy, bandit, pip-audit, vulture, detect-secrets, or AR-check invocations as a closing sub-workflow (per P20.6 log audit). Run them NOW against the current repo state: `pytest tests/ -vvv --cov=. --cov-report=term-missing --timeout=30`, `ruff check .`, `mypy sovereignai/ --ignore-missing-imports`, `bandit -r . -ll --exclude .venv,tests`, `pip-audit --strict --requirement txt/requirements.txt`, `vulture . --min-confidence 80`, `detect-secrets scan --baseline txt/.secrets.baseline`, and all `scripts/ar_checks/*.py`. Document results in the prompt-20.6 execution log (append a `## Post-P20.7 /close completion` section). Any failures = DEBT-document with target plan per OR53. Commit: `git add -A && git commit -m "fix: complete skipped /close scans for prompt-20.6 per OR40"`.

S8.7 (OR57 — backfill browser smoke): P20.6 S5.5 was skipped — no browser smoke test was run for the P16/P17 UI surfaces. User explicitly said "assume its broken" (P20.6 L342). Start `python -m web.main`, open `http://localhost:8000` in a browser, take screenshots of Logs panel + Options panel. Save to `logs/screenshots/prompt-20.7-smoke-{logs,options}.png`. If UI is broken, either fix in this plan (add to WILL edit list) or DEBT-document with target plan. `/verify`. Commit: `git add -A && git commit -m "fix: backfill browser smoke for P16/P17 UI per OR57 (P20.6 S5.5 skipped)"`.

S8.8 (OR45 — document quota-interrupt re-read protocol): P20.6 had 3 quota interrupts (L838, L1277, L2980) with ZERO re-reads of plan/AGENTS.md. This is a cultural/process issue, not a code fix. Append to `LANDMINES.md` a new entry: `L64 — Quota interrupt without re-read. Trigger: After quota-exhaustion interrupt, Devin resumes editing without re-reading plan + AGENTS.md (observed in P20.6 L838/L1277/L2980). Impact: Context loss; rule violations; scope drift. Graduated to: OR45 (existing — enforcement is cultural, no mechanical fix).`. Commit: `git add -A && git commit -m "docs: add L64 landmine (quota interrupt without re-read)"`.

## S9 — Closing

S9.1: Run full scan suite ONE AT A TIME per OR3: pytest (NO `--ignore` flags, with `--timeout=30` per OR79), ruff, mypy (file-scoped on edited files), bandit (NO baseline), pip-audit, vulture, detect-secrets, AR checks (including NEW `check_dependencies.py`, NEW `check_plan_immutability.py $(cat .open_hash)`, NEW `check_rule_conciseness.py`, `check_changelog.py 20.7`, `check_test_mode_hooks.py`, `check_tracing.py`).
S9.2: Per OR53, get User authorization for any unfixed failures. Expected: none (this is additive + rollback).
S9.3: Append CHANGELOG entry per OR73 (concise version). Echo verbatim entry text in execution log. Include the prompt-20.6 re-tag note (S8.4) and the OR55 correction note (S8.5).
S9.4: Update `PLANS.md` baseline: `**Current**: <N> tests (Plan 20.7 /close)`.
S9.5: `git mv prompts/plan-20.7-Rev0.md prompts/completed/`.
S9.6: Write `logs/execution-log-prompt-20.7.md` per OR75: header + `## Devin Chat` with `[PASTE DEVIN CHAT HERE]` marker + structured S0-S9 summary with verbatim CHANGELOG echo.
S9.7: Run `/close`. Verify step 17.5 (check_changelog.py 20.7), 17.6 (check_dependencies.py), 17.7 (check_plan_immutability.py), 17.8 (check_rule_conciseness.py) all pass.
S9.8: `git tag prompt-20.7` and `git push origin main --tags`. Do NOT force-push (L25/OR42/L55/L64).

---

## Notes for Devin

- **Full verbosity means ALL levels** — TRACE, DEBUG, INFO, WARN, ERROR. Do not filter. The user wants everything.
- **One file per process run** — not rotation. Each `python -m sovereignai.main` creates a new file. The user archives/deletes old files manually.
- **JSON Lines format** — one JSON object per line, not pretty-printed. Easy to `grep`, `jq`, or parse.
- **Subscriber pattern, not scattered logging** — do NOT add `logging.info()` calls across execution layers. TraceEmitter is the SSOT (OR61). The subscriber just persists what TraceEmitter already emits.
- **sailogs/ MUST be gitignored** — L59. Verify `.gitignore` has `sailogs/*.log` before any commit. The `.gitkeep` file is tracked; the `.log` files are not.
- **GR18 must land before S1** — S0.4 is mandatory. The conciseness pass in S1 is authorized by GR18; without it, the tightenings have no rule basis.
- **OR78 is the plan-immutability rule** — Devin must NOT edit `prompts/plan-N-RevM.md` files during execution. The only allowed edit is the move to `prompts/completed/` at /close step 17. If the WILL-edit list is incomplete, STOP per OR19 and request an Architect-issued Rev. `check_plan_immutability.py` (S2.2) enforces this mechanically at /close step 17.7.
- **OR77 is the dependency-discipline rule** — every new import requires the package in the correct file (requirements.txt for production, pyproject.toml for dev/test). `check_dependencies.py` (S2.1) enforces at /open step 4.5 and /close step 17.6. After any requirements.txt change, run `pip install -e .[dev]`.
- **OR79 is the test-timeout rule** — all tests have a 30s timeout via `--timeout=30 --timeout-method=thread` in pyproject.toml addopts. Stalled tests FAIL instead of hanging. Per-test override via `@pytest.mark.timeout(N)` for tests that legitimately need longer. S6 mocks the two stalling test files (`test_options_panel.py`, `test_models_panel.py`) so they pass instantly — the 30s timeout is a safety net, not the primary fix.
- **OR80 is the rule-conciseness enforcement rule** — every AR/OR rule must be <=2 lines / <=200 chars. `check_rule_conciseness.py` (S2.4) enforces mechanically at /open step 4.6 and /close step 17.8. This is the hook that makes GR18 enforceable — SWE-1.6 ignores prose rules (Cognition blog 2026-07 confirms overthinking/instruction-following issues), so the conciseness pass in S1 must be mechanically verified, not just asserted. If S0.3 adds any rule over 200 chars, trim it BEFORE committing — the check will fail /open otherwise.
- **OR81 is the MCP usage rule** — Devin queries Context7 before using any library API (prevents P20.4-style hallucinated import paths), and invokes Snyk MCP scan at /close for dep/security changes (catches CVEs earlier than pip-audit alone). L65 (Context7 skipped) and L66 (Snyk skipped) are the landmines. S0.6 is a MANDATORY pre-flight check verifying MCP servers won't break existing workflow — if any of the 6 checks fail, STOP per OR19 before proceeding. S7.2 wires Snyk into /close as step 5.5. S8.2 explicitly requires Context7 query before the TUI refactor.
