# LANDMINES.md — SovereignAI Failure Patterns

Append-only. Selected landmines (L1–L9, L11, L12, L17) inherited from sovereign-ai (predecessor project) — these are the entries referenced in `AGENTS.md`'s landmine-to-rule table. L10, L13–L16, L18–L23 were not graduated to rules in SovereignAI and are not carried forward. SovereignAI-specific landmines L24–L27 captured during Plan 0 execution; L28–L29 captured during prompt-0.1 execution. New landmines for SovereignAI continue from L30.

Entries below are placeholder records for the inherited landmines referenced in `AGENTS.md`'s landmine-to-rule table. Each entry records the inherited trigger pattern and impact; SovereignAI-specific triggers will be appended as they occur. Per AGENTS.md: "Keep entries concise — trigger and impact only. No narrative."

---

## L1 — replace_all corrupts adjacent lines
**Trigger**: Inherited from sovereign-ai predecessor. Specific SovereignAI trigger TBD.
**Impact**: `AGENTS.md` or other structured markdown becomes structurally invalid. Requires manual restoration from git.
**Graduated to**: OR5.

## L2 — Parallel scan tools corrupt output streams
**Trigger**: Inherited from sovereign-ai predecessor. Specific SovereignAI trigger TBD.
**Impact**: Output streams from pytest/ruff/mypy/bandit/pip-audit/vulture interleave when run in parallel, producing unreadable output. Requires re-running all tools sequentially.
**Graduated to**: OR3.

## L3 — PowerShell -replace corrupts structured markdown
**Trigger**: Inherited from sovereign-ai predecessor. Specific SovereignAI trigger TBD (SovereignAI uses Git Bash per OR1, so this should not recur — retained for diagnostic context).
**Impact**: Markdown table formatting destroyed when edited with PowerShell `Set-Content` + `-replace`.
**Graduated to**: OR7.

## L4 — Temp files left in repo root get committed
**Trigger**: Inherited from sovereign-ai predecessor. Specific SovereignAI trigger TBD.
**Impact**: Temp file committed to repo. Requires follow-up commit to remove.
**Graduated to**: OR13, OR21.

## L5 — Vulture flags unused test fixtures incorrectly
**Trigger**: Inherited from sovereign-ai predecessor. Specific SovereignAI trigger TBD.
**Impact**: False positive. Parameter was required by pytest's parametrize decorator.
**Graduated to**: OR19.

## L6 — Naive/aware datetime mixing
**Trigger**: Inherited from sovereign-ai predecessor. Specific SovereignAI trigger TBD.
**Impact**: Type error when comparing `datetime.utcnow()` with `datetime.now(timezone.utc)`. Mypy flagged the mismatch.
**Graduated to**: OR20.

## L7 — Stale baselines propagate through plans
**Trigger**: Inherited from sovereign-ai predecessor. Specific SovereignAI trigger TBD.
**Impact**: Baseline drift. Subsequent plan starts with wrong expected test count, causing false STOP.
**Graduated to**: OR17.

## L8 — Scope drift: editing files outside declared scope
**Trigger**: Inherited from sovereign-ai predecessor. Specific SovereignAI trigger TBD.
**Impact**: Unplanned changes in commit. Difficult to trace which plan produced which change.
**Graduated to**: OR16, OR22.

## L9 — Interface changes break existing tests during type remediation
**Trigger**: Inherited from sovereign-ai predecessor. Specific SovereignAI trigger TBD.
**Impact**: Tests failed. Required either test updates (out of scope) or compatibility shim.
**Graduated to**: OR27.

## L11 — Bypassed pre-commit hooks with --no-verify
**Trigger**: Inherited from sovereign-ai predecessor. Specific SovereignAI trigger TBD.
**Impact**: Committed code with known style violation. Required follow-up fix.
**Graduated to**: OR32.

## L12 — Hiding type errors by excluding files from hooks
**Trigger**: Inherited from sovereign-ai predecessor. Specific SovereignAI trigger TBD.
**Impact**: Type error hidden permanently. File never type-checked again.
**Graduated to**: OR33.

## L17 — Plan steps executed/marked complete out of order
**Trigger**: Inherited from sovereign-ai predecessor. Specific SovereignAI trigger TBD.
**Impact**: Step marked complete based on work done in a different section. Required replan.
**Graduated to**: OR34.

## L24 — Shell redirection and echo-to-file fail in Git Bash on Windows
**Trigger**: Plan 0, S4.4 (detect-secrets scan > txt/.secrets.baseline) and S4.3 (mkdir -p X && echo "" > X/.gitkeep for 16 directories). Both patterns errored.
**Impact**: Executor fell back to Edit tool for file creation and unredirected command output for scan results. Required multiple workaround commands and added ~10 extra Edit operations to the execution log.
**Graduated to**: OR41 (Edit tool for empty files), OR43 (tee instead of redirect).

## L25 — Multi-line git commit messages fail in Git Bash on Windows
**Trigger**: Plan 0, S8, `git commit -m "title\n\n- bullet 1\n..."` errored.
**Impact**: Executor fell back to single-line commit message: "prompt-0: Bootstrap governance docs and infrastructure - Fix master->main, add governance docs, README, .gitignore, pyproject.toml, requirements.txt, .pre-commit-config.yaml, directory structure, fix Rev5 metadata, update PLANS.md". Lost the structured 10-line body the plan specified. The CHANGELOG.md file was created separately with full content, so the audit trail survived, but the git log lost structure.
**Graduated to**: OR42 (multi-line commit via -m -m).

## L26 — detect-secrets --all-files scans .venv/ despite .gitignore
**Trigger**: Plan 0, S4.4, baseline scan flagged false positive in `.venv/Lib/site-packages/pip/_vendor/urllib3/util/url.py` (Basic Auth Credentials pattern in vendored pip code).
**Impact**: Executor manually edited the JSON baseline to remove the false positive instead of running `detect-secrets audit`. Manual JSON edit broke the baseline's signature. Required follow-up commit `41b9326` ("fix: update secrets baseline with self-filter and timestamp") to add the `is_baseline_file` filter properly via the audit tool.
**Graduated to**: OR40 (detect-secrets --exclude patterns).

## L27 — Executor skipped /close steps when expected result was N/A
**Trigger**: Plan 0, Closing section, Executor skipped `/close` steps 15-21 (commit, tag, push, verify, final summary, kill bash) reasoning "most steps are N/A for docs-only plan."
**Impact**: User had to prompt "why did you stop at 14? you should complete all closing steps." Executor then completed remaining steps. Wasted a round-trip and risked leaving the session in an inconsistent state (bash processes not killed, final summary not produced).
**Graduated to**: No new rule — workflow file fix only (S2.2 and S2.3 add explicit "mandatory even for docs-only plans" language to `/close` step 21 and the Steps header).

## L28 — sed used on workflow files after Edit-tool failures
**Trigger**: prompt-0.1, S2.2 and S2.3, Executor used `sed -i` on `.devin/workflows/close.md` after 3 Edit-tool attempts failed due to whitespace mismatch.
**Impact**: The `sed` commands produced correct output (verified post-execution), but the precedent is dangerous — `sed` regex bugs could silently corrupt workflow files loaded by every subsequent plan's `/open` and `/close`. OR7 listed structured-markdown files but did not explicitly include `.devin/workflows/*.md`, so the Executor interpreted the gap as "OR7 doesn't apply to workflow files."
**Graduated to**: OR44 (workflow files are structured markdown — OR7 applies; if Edit tool fails, STOP and report, do not fall back to sed).

## L29 — python and pip resolve to different interpreters on Windows
**Trigger**: prompt-0.1, `/close` step 1, `python -m pytest tests/ -vvv` failed with `No module named pytest`. Diagnosis: `python` on PATH resolved to `C:\Users\King\AppData\Local\hermes\hermes-agent\venv\Scripts\python.exe` (hermes-agent's venv), but `pip install -e .[dev]` (run during prompt-0) installed dev tools into `C:\Users\King\AppData\Local\Programs\Python\Python311\Lib\site-packages` (the main Python 3.11 install). The two Pythons don't share site-packages.
**Impact**: `/close` step 1 (pytest) would have failed even if test files existed. The Executor reported "Tests: N/A (no tests directory exists)" — technically true, but masked the underlying PATH issue. Plan 1's first `/close` would have hit the same wall.
**Graduated to**: OR45 (project-local venv at `.venv/` is the canonical Python environment; activate before any python/pip command).

---

## Process for capturing new landmines (L30+)

At `/close` step 11, if a new failure pattern was discovered during the plan, append an entry in this format:

```markdown
## L{n} — <one-line title of the failure pattern>

**Trigger**: <Plan #, step, specific command/file/context — be concrete>
**Impact**: <What broke as a result>
```

Keep entries concise — trigger and impact only. No narrative, no cross-references to other plans. No proposed fixes or rules — those come from the Architect via `AGENTS.md`.
