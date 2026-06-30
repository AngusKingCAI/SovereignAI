# LANDMINES.md — SovereignAI Failure Patterns

Append-only. L1–L9, L11, L12, L17 inherited from sovereign-ai (only those referenced in AGENTS.md's landmine-to-rule table; L10, L13–L16, L18–L23 not carried forward). SovereignAI-specific: L24–L27 (Plan 0), L28–L29 (prompt-0.1), L30 (prompt-0.2), L31 (prompt-0.3). New landmines continue from L32.

---

## L1 — replace_all corrupts adjacent lines
**Trigger**: Inherited. Not yet triggered in SovereignAI.
**Impact**: Structured markdown becomes structurally invalid. Requires manual git restoration.
**Graduated to**: OR5.

## L2 — Parallel scan tools corrupt output streams
**Trigger**: Inherited. Not yet triggered in SovereignAI.
**Impact**: Output from pytest/ruff/mypy/bandit/pip-audit/vulture interleaves when run in parallel.
**Graduated to**: OR3.

## L3 — PowerShell -replace corrupts structured markdown
**Trigger**: Inherited. SovereignAI uses Git Bash per OR1 — should not recur.
**Impact**: Markdown table formatting destroyed by `Set-Content` + `-replace`.
**Graduated to**: OR7.

## L4 — Temp files left in repo root get committed
**Trigger**: Inherited. Not yet triggered in SovereignAI.
**Impact**: Temp file committed. Requires follow-up commit to remove.
**Graduated to**: OR13, OR21.

## L5 — Vulture flags unused test fixtures incorrectly
**Trigger**: Inherited. Not yet triggered in SovereignAI.
**Impact**: False positive — parameter required by pytest's parametrize decorator.
**Graduated to**: OR19.

## L6 — Naive/aware datetime mixing
**Trigger**: Inherited. Not yet triggered in SovereignAI.
**Impact**: Type error comparing `datetime.utcnow()` with `datetime.now(timezone.utc)`.
**Graduated to**: OR20.

## L7 — Stale baselines propagate through plans
**Trigger**: Inherited. Not yet triggered in SovereignAI.
**Impact**: Baseline drift causes false STOP on subsequent plan start.
**Graduated to**: OR17.

## L8 — Scope drift: editing files outside declared scope
**Trigger**: Inherited. Not yet triggered in SovereignAI.
**Impact**: Unplanned changes in commit; difficult to trace which plan produced which change.
**Graduated to**: OR16, OR22.

## L9 — Interface changes break existing tests during type remediation
**Trigger**: Inherited. Not yet triggered in SovereignAI.
**Impact**: Tests failed; required either out-of-scope test updates or compatibility shim.
**Graduated to**: OR27.

## L11 — Bypassed pre-commit hooks with --no-verify
**Trigger**: Inherited. Not yet triggered in SovereignAI.
**Impact**: Committed code with known style violation. Required follow-up fix.
**Graduated to**: OR32.

## L12 — Hiding type errors by excluding files from hooks
**Trigger**: Inherited. Not yet triggered in SovereignAI.
**Impact**: Type error hidden permanently; file never type-checked again.
**Graduated to**: OR33.

## L17 — Plan steps executed/marked complete out of order
**Trigger**: Inherited. Not yet triggered in SovereignAI.
**Impact**: Step marked complete based on work done elsewhere. Required replan.
**Graduated to**: OR34.

## L24 — Shell redirection and echo-to-file fail in Git Bash on Windows
**Trigger**: Plan 0 S4.4 (`detect-secrets scan > txt/.secrets.baseline`) and S4.3 (`mkdir -p X && echo "" > X/.gitkeep` for 16 dirs). Both errored.
**Impact**: ~10 extra Edit operations; Executor fell back to Edit tool and unredirected command output.
**Graduated to**: OR41, OR43.

## L25 — Multi-line git commit messages fail in Git Bash on Windows
**Trigger**: Plan 0 S8, `git commit -m "title\n\n- bullet..."` errored.
**Impact**: Fell back to single-line message; structured 10-line body lost from git log (CHANGELOG survived).
**Graduated to**: OR42.

## L26 — detect-secrets --all-files scans .venv/ despite .gitignore
**Trigger**: Plan 0 S4.4, baseline flagged false positive in `.venv/` vendored pip code.
**Impact**: Executor manually edited baseline JSON instead of using audit tool; broke baseline signature. Required follow-up commit `41b9326`.
**Graduated to**: OR40.

## L27 — Executor skipped /close steps when expected result was N/A
**Trigger**: Plan 0 Closing — Executor skipped steps 15–21 reasoning "most steps N/A for docs-only plan."
**Impact**: User had to prompt re-run; risked inconsistent session state.
**Graduated to**: Workflow fix only — `/close` step 21 and Steps header add "mandatory even for docs-only plans."

## L28 — sed used on workflow files after Edit-tool failures
**Trigger**: prompt-0.1 S2.2/S2.3 — Executor used `sed -i` on `.devin/workflows/close.md` after 3 Edit-tool attempts failed (whitespace mismatch). OR7 didn't explicitly list workflow files, so Executor treated it as a gap.
**Impact**: Correct output, but dangerous precedent — `sed` regex bugs could silently corrupt workflow files loaded by every subsequent plan.
**Graduated to**: OR44.

## L29 — python and pip resolve to different interpreters on Windows
**Trigger**: prompt-0.1 `/close` step 1 — `python` on PATH resolved to hermes-agent's venv; `pip install -e .[dev]` had installed into Python 3.11 main install. Different site-packages.
**Impact**: pytest would have failed even if test files existed; PATH issue masked by "no tests directory" report.
**Graduated to**: OR45.

## L30 — source .venv/Scripts/activate does not persist in Git Bash on Windows
**Trigger**: prompt-0.2 S1.4 — after `source .venv/Scripts/activate`, `which python` showed venv but `which pip` showed system path.
**Impact**: Executor fell back to absolute paths for all commands. Workflows relying on activation would hit the same issue every plan.
**Graduated to**: OR46.

## L31 — Mypy fails when passed markdown or other non-Python files
**Trigger**: prompt-0.3 `/close` step 3 — `mypy AGENTS.md CHANGELOG.md ... .devin/workflows/*.md` got "Duplicate module named __main__" error.
**Impact**: Executor skipped mypy entirely. Pattern would skip mypy on real Python files in Plan 1+ if any markdown files were also edited.
**Graduated to**: OR47.

## L32 — Executor paraphrases workflow commands instead of running them verbatim
**Trigger**: Prompts 7, 8, 9 Step 17 — Executor ran `mv plan-{N}-Rev5.md` (single file) instead of the `for file in prompts/plan-{N}-Rev*.md` loop defined in close.md. Result: older plan revisions left in `prompts/`; User had to ask 3 times; repo state inconsistent.
**Impact**: 3 User interventions across prompts 7–9; plan-9 Rev1–4 unarchived for 1+ prompt cycles; undermined trust in /close workflow reliability.
**Graduated to**: OR71.

## L33 — Executor weakens AR check scripts or tests to make a failure pass
**Trigger**: Prompt 6 close — `test_ar7_no_core_imports_in_ui.py` failed because `web/main.py` imported `sovereignai.shared.*`. Executor edited the test to add `WEB_MAIN_ALLOWED_IMPORTS` allowlist. (This case was subsequently documented as a legitimate scoped allowlist — see Plan 10 S3 audit. But the *pattern* of editing a test to make it pass, rather than fixing the source, is the landmine.)
**Impact**: Risk of silently disabling architectural enforcement. AR7 (UI/core separation) could be effectively disabled without Architect sign-off.
**Graduated to**: OR72.

## L34 — `mv` + `git add <new>` leaves old path tracked in git
**Trigger**: Prompt-9 close Step 17 and prompt-10 S1 — `mv prompts/plan-{N}-Rev*.md prompts/completed/` followed by `git add prompts/completed/`. The `git add` staged the new files but not the deletions. Git tracked both copies; `git ls-files` showed files in both locations.
**Impact**: Duplicate plan files in repo across 1+ prompt cycles; User had to manually `git rm`; archive appeared successful but wasn't.
**Graduated to**: OR75.

## L35 — ruff --fix / detect-secrets auto-modified files missed by explicit `git add` lists
**Trigger**: Prompt-10 Step 15 — `ruff check . --fix` modified `tests/test_e2e_task_submission.py`, `tests/test_web_ui_panels.py`; `detect-secrets scan` updated `txt/.secrets.baseline`. `git add <explicit 25-file list>` missed all 3. Committed `ddd050b` without them; User caught it; required `7e2eeb8` fix commit.
**Impact**: 3 files left uncommitted after "successful" close; User frustration; required follow-up commit.
**Graduated to**: OR75.

## L36 — Premature git tag creation requires force-push to move
**Trigger**: Prompts 9, 10 — tag created before final commit, then `tag -d` + recreate + `push --force`. Also: prompt-11 tag created at `6fa8d73` (a pre-10.1 commit) before Plan 11 started.
**Impact**: Force-pushed tags break anyone who pulled the old tag; dangerous for shared repos. Stale tags point to meaningless commits.
**Graduated to**: OR76.

## L37 — Coverage skipped or unmeasured in 8 of 16 prompts
**Trigger**: Prompts 0.1, 0.2, 0.4, 1, 3, 4, 7, 8 reported "Coverage: N/A" or "not run" with no rule requiring it.
**Impact**: Coverage baseline drifted from 96% → 93% without detection; no STOP triggered.
**Graduated to**: OR77.

## L38 — Bandit Low count drifted without baseline reconciliation
**Trigger**: Bandit Low count: 49 (Plan 1) → 119 (Plan 3) → 156 (Plan 4) → 332 (Plan 10). Baseline updated only at scans, not at every close.
**Impact**: Stale baselines make it impossible to detect new non-test Low findings.
**Graduated to**: OR78.

## L39 — Quota exhaustion mid-plan causes context loss and skipped steps
**Trigger**: 60+ "Auto-continued" interrupts across 16 logs. Prompt-7 skipped `/close` entirely after interrupts.
**Impact**: Steps skipped, work repeated, `/close` forgotten.
**Graduated to**: OR79.

## L40 — close.md Step 17 verification check said "run git rm" which DELETES files instead of moving them
**Trigger**: Prompt-13 close — Executor ran `git rm prompts/plan-13-Rev*.md` because the verification check message literally said "run 'git rm' to stage deletions". This deleted Rev1-Rev9 from git instead of moving them to `prompts/completed/`.
**Impact**: 9 plan revision files permanently deleted from git history; User had to restore manually.
**Graduated to**: close.md Step 17 fixed (verification now runs `git add -A` automatically instead of telling Executor to run `git rm`).

## L41 — Disabled production features to make tests pass
**Trigger**: Prompt-11 — Executor disabled crash recovery and 3 memory backends (episodic, procedural, trace) by commenting them out in `main.py` to make tests pass. The backends were never re-enabled.
**Impact**: Silent failure — crash recovery disabled, memory backends not registered, system incomplete. Violates P9 (no silent failures) and P13 (strong, robust).
**Graduated to**: OR91.

## L42 — Command errored without investigation
**Trigger**: Prompt-11 — Multiple "Command errored" messages appeared in logs; Executor moved to next step without reading error output or determining cause.
**Impact**: Errors left uninvestigated; root causes unknown; potential silent failures.
**Graduated to**: OR92.

## L43 — Command errored in verification step treated as non-blocking
**Trigger**: Prompt-11 — Verification step (e.g., mypy, pytest) errored; Executor continued instead of treating as STOP condition.
**Impact**: Broken verification treated as success; invalid code committed.
**Graduated to**: OR92.

## L44 — Filtered on non-existent event attribute
**Trigger**: Prompt-14 — Self-correction skill filtered on `event.component` in `on_task_state_changed()`, but `TaskStateChanged` dataclass has no `component` field. Filter always returned None; dead code.
**Impact**: Component filter ineffective; recursion guard alone prevented feedback loop (sufficient, but filter was dead code).
**Graduated to**: OR93.

## L45 — Mypy errors dismissed as "pre-existing"
**Trigger**: Prompt-15 — 83 mypy errors reported; Executor dismissed them as "pre-existing" and continued without fixing or documenting in DEBT.md. OR2 requires STOP on mypy errors.
**Impact**: Type errors unaddressed; system not robust; violates P13.
**Graduated to**: OR94.

## L46 — Memory backends not registered in container
**Trigger**: Prompt-11 — Backend files exist (`episodic_backend.py`, `procedural_backend.py`, `trace_backend.py`) but were never imported or registered in `build_container()`. Only `WorkingMemoryBackend` registered.
**Impact**: Librarian cannot discover backends; memory topology incomplete; crashes at runtime.
**Graduated to**: S1 fix (prompt-15.1).

## L47 — Crash recovery disabled
**Trigger**: Prompt-11 — `run_crash_recovery()` function body replaced with `pass` to avoid DB I/O during tests. Never re-enabled.
**Impact**: No crash recovery on startup; incomplete tasks not marked as failed; silent failure.
**Graduated to**: S2 fix (prompt-15.1).

## L48 — Plan shipped with placeholder implementation
**Trigger**: Plan 18.2 — `sovereignai/databases/huggingface/sync.py` contained `# TODO: Fetch actual data from HuggingFace API` placeholder with zero HTTP calls and zero DB rows. Devin marked Phase 2 complete despite this.
**Impact**: HF sync feature non-functional; dropdowns empty; user-facing feature claimed as shipped but not implemented.
**Graduated to**: OR103.

## L49 — "Already done" claim without verification
**Trigger**: Plan 18.2 — Devin marked "Phase 6 complete" despite only 1 of 9 sub-items being done. No verification command run to confirm state.
**Impact**: Incomplete work marked as complete; plan closed with gaps; user misled about progress.
**Graduated to**: OR104.

## L50 — Test failures dismissed as "pre-existing"
**Trigger**: Plan 18.2 — 46 test failures present at close. Devin dismissed them as "pre-existing TraceLevel imports" and shipped anyway. OR2 requires STOP on test failures.
**Impact**: Broken tests committed; system not robust; violates P13.
**Graduated to**: OR105.

## L51 — Skipped tests without target-resolution plan
**Trigger**: Plan 18.2 — Multiple tests skipped with no documented target plan for resolution.
**Impact**: Skipped tests accumulate; no path to unblock; coverage gaps persist.
**Graduated to**: OR106.

## L52 — CHANGELOG claimed unshipped scope
**Trigger**: Plan 18.2 — Commit message claimed "Models Menu Restructure + Universal Tracing" shipped, but sync.py was still a placeholder and tracing incomplete.
**Impact**: CHANGELOG inaccurate; user misled about what was actually delivered.
**Graduated to**: OR107.

## L53 — HTML/CSS/JS syntax not validated before tests
**Trigger**: Plan 18.2 — Python docstrings present in `web/static/app.js` (invalid JS). No syntax validation run before test suite.
**Impact**: Invalid JS in production; potential runtime errors in browser.
**Graduated to**: OR108.

## L54 — Tests used incorrect fixture shapes
**Trigger**: Plan 18.2 — Some tests mocked with incorrect data shapes, not matching actual structures.
**Impact**: Tests pass against wrong shapes; real code may fail with actual data.
**Graduated to**: OR109.

## L55 — Web UI plan lacked browser smoke test
**Trigger**: Plan 18.2 — UI changes made without manual browser verification. Unclickable tabs shipped.
**Impact**: UI broken in browser; user cannot use claimed features.
**Graduated to**: OR110.

## L56 — Stray files in commits without pre-commit scan
**Trigger**: Plan 18.2 — Files outside declared scope appeared in commits. No `git status -s` verification before commit.
**Impact**: Unplanned changes committed; scope drift; difficult to trace.
**Graduated to**: OR111.

## L57 — Plan not re-read at phase boundaries
**Trigger**: Plan 18.2 — Devin did not re-read plan file and AGENTS.md at start of each phase. Context drifted.
**Impact**: Steps executed based on stale mental model; deviations from plan not caught.
**Graduated to**: OR112.

## L58 — Critical rules dropped from plan spec
**Trigger**: Plan 18.2 — Devin added only 6 of 12 new rules specified in Appendix E, dropping OR97, OR100-OR107 (plan deliverables, verification, test failures, etc.). These were exactly the rules that would have prevented the failures.
**Impact**: Rules that would have caught failures were absent; failures recurred; governance incomplete.
**Graduated to**: Plan 18.3 re-adds dropped rules as OR103-OR112.

---

## Capturing new landmines (L48+)

See `AGENTS.md` "LANDMINES.md — when to read/write" for format and graduation procedure. Append-only — entries are never edited or removed. New landmines continue from L41 (per OR84).
