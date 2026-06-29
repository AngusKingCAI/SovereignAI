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

---

## Capturing new landmines (L41+)

See `AGENTS.md` "LANDMINES.md — when to read/write" for format and graduation procedure. Append-only — entries are never edited or removed. New landmines continue from L41 (per OR84).
