# Plan 0.1 — Prompt-0.1 Cleanup (Post-Execution Fix-Up)

**Special plan**: Pre-Plan 1 cleanup. Fixes repo hygiene, workflow file, and landmine capture issues discovered during Plan 0's execution. No architectural work — mechanical only. Skips Round Table review (per AI_HANDOFF.md scan-prompt exemption).

Depends on: prompt-0
Vision principles: none (mechanical cleanup — no architectural impact)
Open questions resolved: none

---

## S0 — Opening

**S0.1** — Run `/open` workflow from `.devin/workflows/open.md`. Verify previous tag (`prompt-0`) exists on origin:

```bash
git fetch origin
git ls-remote --tags origin | grep "prompt-0"
```

If `prompt-0` is missing from origin, STOP — Plan 0 did not complete.

Confirm working copy is clean and on `main`:

```bash
git status -s
git branch --show-current
```

If dirty (excluding governance docs/plan files) or not on `main`, STOP.

**S0.2** — Read `AGENTS.md` in full. Note that OR22's always-on subset (OR5, OR6, OR15, OR16, OR34, AR5, AR16, AR21) applies to every edit in this plan. Note the new OR40–OR43 (added at S0.3 below) addressing shell/tooling issues observed in Plan 0's execution — these become part of the always-on mental check going forward.

**S0.3** — Add 4 new rules to `AGENTS.md`. Commit before any other step.

Append the following rules to the Operational Rules section of `AGENTS.md`, after OR39 and before the "Landmines that have graduated to rules" section. Use the Edit tool (not shell append — OR7).

> OR40. `detect-secrets scan` must exclude vendored and build directories. `detect-secrets` does not honor `.gitignore` by default — it scans every file on disk. When generating or refreshing `txt/.secrets.baseline`, always pass `--exclude` with patterns matching `.gitignore`:
>
> ```bash
> detect-secrets scan --all-files --exclude '.venv,venv,env,build,dist,node_modules,__pycache__,.git,.tox,.eggs,.pytest_cache,.mypy_cache,.ruff_cache,htmlcov,*.egg-info' > txt/.secrets.baseline
> ```
>
> After generating the baseline, run `detect-secrets audit txt/.secrets.baseline` interactively to review any remaining false positives. Do NOT manually edit the baseline JSON to remove findings — manual edits break the baseline's signature and cause `detect-secrets scan --baseline` to fail on subsequent runs. The audit tool is the only sanctioned way to mark false positives. (Source: L26 — Plan 0 execution, Executor manually edited JSON instead of using audit tool, required follow-up commit `41b9326` to fix.)

> OR41. Use the Edit tool to create empty files (`.gitkeep`, `__init__.py`), not shell `echo "" > path`. Git Bash on Windows does not reliably handle `echo "" > path/to/file` for paths with forward slashes inside `&&` chains — the command errors silently or produces a file at an unexpected location. The Edit tool with `filepath="path/to/file"` and minimal `new_str` content (e.g., a single newline) is the canonical way to create empty files in this repo. For directory creation, `mkdir -p path/to/dir` works reliably; combine with a separate Edit-tool call to create the `.gitkeep` file inside it. (Source: L24 — Plan 0 execution, all 16 `mkdir -p X && echo "" > X/.gitkeep` commands errored; Executor fell back to Edit tool successfully.)

> OR42. Multi-line git commit messages use multiple `-m` flags, not embedded newlines. Git Bash on Windows interprets embedded newlines in `git commit -m "title\n\nbody"` quoted strings inconsistently — the command may error or silently produce a single-line message. Use `git commit -m "title" -m "body paragraph 1" -m "body paragraph 2"` instead. Each `-m` flag becomes a separate paragraph in the commit message. For bullet-list bodies, put each bullet on its own line within a single `-m` argument using literal newlines typed in the shell (not `\n` escape sequences). (Source: L25 — Plan 0 execution, multi-line commit message errored; Executor fell back to single-line message, losing the structured body.)

> OR43. Shell redirection (`>`, `>>`) for tool output is unreliable in Git Bash on Windows — use `tee` or run without redirection and capture via Edit. When a tool's output needs to be written to a file (e.g., `detect-secrets scan > file.json`), prefer `tool args | tee file.json` (writes to both terminal and file), or run the tool without redirection and use the Edit tool to write the captured output to the target file. This applies to any command producing >1KB of output that needs file capture. Small outputs (e.g., `echo "OK" > flag.txt`) are exempt — `echo` redirection is reliable. (Source: L24 — Plan 0 execution, `detect-secrets scan --all-files > txt/.secrets.baseline` errored; Executor fell back to running without redirect, then Edit.)

Do **not** add entries to the landmine-to-rule table at the bottom of `AGENTS.md` for OR40–OR43 yet — the landmines L24–L27 are captured at S3 of this plan, and the table update happens at S3.4 (after LANDMINES.md is updated).

Commit:
```bash
git add AGENTS.md
git commit -m "docs: add OR40-OR43 for prompt-0.1" -m "Shell/tooling issues observed during Plan 0 execution: detect-secrets excludes (OR40), Edit tool for empty files (OR41), multi-line commit via -m -m (OR42), tee instead of redirect (OR43)."
```

After edit, run `/verify`.

---

## S1 — Repo Hygiene Fixes

### S1.1 — Delete `prompts/plan-0-Rev2.md`

Per AI_HANDOFF.md, the repo's `prompts/` directory should contain `prompts/plan-0.md` (no revision suffix). Rev files live in `/home/z/my-project/download/`. Having `prompts/plan-0-Rev2.md` and `prompts/plan-0-Rev3.md` in the repo creates ambiguity about which is canonical.

Use the Edit tool to delete — actually, deletion requires `git rm`. Use bash for the deletion (file deletion is not a structured-markdown edit, so OR7 doesn't apply):

```bash
git rm prompts/plan-0-Rev2.md
```

After deletion, run `/verify` (skip syntax check — deletion has no content to verify, but report the deletion).

### S1.2 — Rename `prompts/plan-0-Rev3.md` → `prompts/plan-0.md`

```bash
git mv prompts/plan-0-Rev3.md prompts/plan-0.md
```

After rename, run `/verify`.

### S1.3 — Delete `prompts/plan-0-brief.md`

The Rev1 brief is no longer needed — Round Table review is complete, and Plan 0 is locked at Rev3 (now `prompts/plan-0.md`). Per AI_HANDOFF.md, briefs are not preserved in the repo; they live in the Architect's workspace.

```bash
git rm prompts/plan-0-brief.md
```

After deletion, run `/verify`.

### S1.4 — Update PLANS.md plan-1 reference

In `PLANS.md`, find the line:
```
Plan 1 file: prompts/plan-1-Rev1.md (to be created by Architect, copied by User)
```

Change to:
```
Plan 1 file: prompts/plan-1.md (to be created by Architect, copied by User)
```

Per AI_HANDOFF.md canonical naming: `prompts/plan-{N}.md` (no Rev suffix in the repo). Rev suffixes live in the Architect's `/home/z/my-project/download/` workspace.

After edit, run `/verify`.

---

## S2 — Workflow File Fixes

### S2.1 — Fix `/close` step 8: `core/` → `sovereignai/`

In `.devin/workflows/close.md` step 8, the custom AR checks reference `core/` but the actual package is `sovereignai/` (per Plan 0's directory structure). Use the Edit tool to fix each reference:

Old text:
```
8. Run custom static analysis checks (AR rules). Each is a separate command. STOP on any violation:
   - No globals in `core/`
   - Constructor arg cap (15) in `core/`
   - No context bags in `core/`
   - Docstring verb-first, ≥10 words on first line
   - No hard-coded component names in `web/`, `cli/`, `tui/`, `phone/`
   - UI changes don't touch `core/` (check `git diff --name-only HEAD~1`)
```

New text:
```
8. Run custom static analysis checks (AR rules). Each is a separate command. STOP on any violation:
   - No globals in `sovereignai/`
   - Constructor arg cap (15) in `sovereignai/`
   - No context bags in `sovereignai/`
   - Docstring verb-first, ≥10 words on first line
   - No hard-coded component names in `web/`, `cli/`, `tui/`, `phone/`
   - UI changes don't touch `sovereignai/` (check `git diff --name-only HEAD~1`)
```

After edit, run `/verify`.

### S2.2 — Fix `/close` step 21: add mandatory note

In `.devin/workflows/close.md` step 21, add an explicit "mandatory even for docs-only plans" note. This addresses L27 — the Executor skipped steps 15-21 during Plan 0 reasoning "most steps are N/A."

Old text:
```
21. Close Git Bash sessions (Windows-specific):
   ```
   taskkill //F //IM bash.exe
   ```
   No output expected. Kills all `bash.exe` processes including the current session. This is the final step — no further commands will execute.
```

New text:
```
21. Close Git Bash sessions (Windows-specific). This step is mandatory even for docs-only plans — do not skip:
   ```
   taskkill //F //IM bash.exe
   ```
   No output expected. Kills all `bash.exe` processes including the current session. This is the final step — no further commands will execute. If any prior step was skipped because its result was N/A (e.g., no Python code to test), this step still runs. N/A results are reported in the final summary (step 20), not used as a reason to skip subsequent steps.
```

After edit, run `/verify`.

### S2.3 — Fix `/close` step 3: clarify "N/A" handling

In `.devin/workflows/close.md`, add a note at the top of the Steps section clarifying that N/A steps are reported, not skipped. Insert after the "## Steps" header:

Old text:
```
## Steps

1. Run full test suite:
```

New text:
```
## Steps

**N/A handling**: When a step's result is N/A (e.g., no Python code to test, no new landmines discovered), the Executor runs the step, observes the N/A result, and reports it in the final summary (step 20). The Executor does NOT skip the step. Skipping steps because "the result would be N/A" is an OR34 violation. The only steps that may be skipped are those explicitly marked "skip if N/A" in this workflow file.

1. Run full test suite:
```

After edit, run `/verify`.

---

## S3 — Append Landmines L24–L27 to LANDMINES.md

### S3.1 — Read current LANDMINES.md

Read `LANDMINES.md` to confirm the last landmine number. Per Plan 0, the inherited landmines are L1–L9, L11, L12, L17 (12 entries). New SovereignAI landmines start at L24 per the header.

### S3.2 — Append L24, L25, L26, L27

Use the Edit tool to append the following entries to `LANDMINES.md`, after the L17 entry and before the "Process for capturing new landmines (L24+)" section:

```markdown
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
**Graduated to**: No new rule — workflow file fix only (S2.2 and S2.3 add explicit "mandatory even for docs-only plans" language to `/close` step 21 and the Steps section header).
```

After edit, run `/verify`.

### S3.3 — Update LANDMINES.md header

Update the header line to reflect the new landmine range. Use the Edit tool.

Old text:
```
Append-only. Selected landmines (L1–L9, L11, L12, L17) inherited from sovereign-ai (predecessor project) — these are the entries referenced in `AGENTS.md`'s landmine-to-rule table. L10, L13–L16, L18–L23 were not graduated to rules in SovereignAI and are not carried forward. New landmines for SovereignAI start at L24.
```

New text:
```
Append-only. Selected landmines (L1–L9, L11, L12, L17) inherited from sovereign-ai (predecessor project) — these are the entries referenced in `AGENTS.md`'s landmine-to-rule table. L10, L13–L16, L18–L23 were not graduated to rules in SovereignAI and are not carried forward. SovereignAI-specific landmines L24–L27 captured during Plan 0 execution. New landmines for SovereignAI continue from L28.
```

After edit, run `/verify`.

### S3.4 — Update landmine-to-rule table in AGENTS.md

In `AGENTS.md`, find the "Landmines that have graduated to rules" table. Append 4 new rows:

Old text (last row of the table):
```
| L17 | OR34 | Plan steps executed/marked complete out of order |
```

New text:
```
| L17 | OR34 | Plan steps executed/marked complete out of order |
| L24 | OR41, OR43 | Shell redirection and echo-to-file fail in Git Bash on Windows |
| L25 | OR42 | Multi-line git commit messages fail in Git Bash on Windows |
| L26 | OR40 | detect-secrets --all-files scans .venv/ despite .gitignore |
| L27 | (workflow fix only — /close step 21 + Steps header) | Executor skipped /close steps when expected result was N/A |
```

Note: this edit happens at S3.4 (after S3.2 and S3.3 update LANDMINES.md), not at S0.3 (when OR40–OR43 were added to AGENTS.md). The landmine-to-rule table cross-references landmine numbers, so the landmines must exist in LANDMINES.md before the table is updated. Per OR34, this is a sequential dependency — S0.3 adds the rules, S3 captures the landmines, S3.4 cross-references them.

After edit, run `/verify`.

---

## S4 — Update CHANGELOG.md

Use the Edit tool to append a new entry to the END of `CHANGELOG.md` (per OR12 — append to end only, never insert at top):

```markdown
## prompt-0.1 — Post-execution cleanup

**Date**: 2026-06-28
**Plan file**: prompts/plan-0.1-Rev1.md

**Files changed**:
- AGENTS.md (added OR40, OR41, OR42, OR43; updated landmine-to-rule table with L24–L27)
- .devin/workflows/close.md (fixed core/ -> sovereignai/ in step 8; added "mandatory even for docs-only plans" note to step 21; added N/A handling note to Steps header)
- LANDMINES.md (appended L24, L25, L26, L27; updated header to reflect new range)
- PLANS.md (fixed plan-1 file reference: plan-1-Rev1.md -> plan-1.md; state update)
- prompts/plan-0-Rev2.md (deleted)
- prompts/plan-0-Rev3.md (renamed to prompts/plan-0.md)
- prompts/plan-0-brief.md (deleted — Round Table review complete, brief not preserved in repo)

**Results**:
- Tests: N/A (no code)
- Ruff: N/A (no Python code)
- Mypy: N/A (no Python code)
- Bandit: N/A (no Python code)
- pip-audit: 0 CVEs (txt/requirements.txt unchanged from prompt-0 — still empty)
- Vulture: N/A (no Python code)
- Detect-secrets: pass (baseline unchanged from prompt-0)

**Notes**:
- Mechanical cleanup plan addressing issues discovered during Plan 0 execution.
- 4 new OR rules (OR40–OR43) capture shell/tooling workarounds observed in Git Bash on Windows.
- 4 new landmines (L24–L27) record the specific failure patterns from Plan 0.
- Workflow file fixes: /close step 8 references sovereignai/ instead of core/; /close step 21 and Steps header clarify N/A handling.
- Repo hygiene: prompts/ directory now contains only prompts/plan-0.md (canonical name per AI_HANDOFF.md).
- No Round Table review (scan-prompt exemption per AI_HANDOFF.md).
```

After edit, run `/verify`.

---

## S5 — Update PLANS.md

Use the Edit tool. Two edits:

### S5.1 — Add prompt-0.1 row to Completed Prompts table

Append a new row to the "Completed Prompts" table:

```
| prompt-0.1 | `prompt-0.1` | Post-execution cleanup — OR40-OR43, L24-L27, workflow fixes, repo hygiene | N/A | N/A | N/A | 2026-06-28 |
```

### S5.2 — Update "Last updated" line

Change the "Last updated" line at the top to today's date.

### S5.3 — Verify Active Plan and Next-5-Prompt Queue

Read-only verification:
- Active Plan should still show "Plan 1 — awaiting execution." (set during Plan 0's S7). If not, STOP and report.
- Next-5-Prompt Queue should still show Plan 1 in slot 1 with "🔜 Ready to draft" status. If not, STOP and report.

After all edits, run `/verify`.

---

## S6 — Commit and Tag Prompt-0.1

**STOP condition**: If any `/verify` step failed, STOP and report before committing.

1. Stage all changes (note: AGENTS.md was already committed at S0.3, so it won't be in this commit — but the AGENTS.md landmine-to-rule table update at S3.4 is a separate edit that IS in this commit):
   ```bash
   git add -A
   git status -s | tail -n 20
   ```
   Verify the staged files match the expected changes:
   - Modified: `.devin/workflows/close.md`, `AGENTS.md` (landmine-to-rule table only — OR40-OR43 already committed at S0.3), `LANDMINES.md`, `PLANS.md`, `CHANGELOG.md`
   - Deleted: `prompts/plan-0-Rev2.md`, `prompts/plan-0-brief.md`
   - Renamed: `prompts/plan-0-Rev3.md` → `prompts/plan-0.md`

   If anything unexpected is staged, STOP.

2. Commit (use multiple `-m` flags per OR42 — do NOT use embedded newlines):
   ```bash
   git commit -m "prompt-0.1: Post-execution cleanup" -m "Repo hygiene: deleted prompts/plan-0-Rev2.md and prompts/plan-0-brief.md, renamed prompts/plan-0-Rev3.md to prompts/plan-0.md per AI_HANDOFF.md canonical naming." -m "Workflow fixes: /close step 8 references sovereignai/ instead of core/; step 21 and Steps header clarify N/A handling (mandatory even for docs-only plans)." -m "Landmines: appended L24-L27 to LANDMINES.md; updated landmine-to-rule table in AGENTS.md." -m "PLANS.md: added prompt-0.1 row to Completed Prompts; fixed plan-1 file reference."
   ```

3. Tag:
   ```bash
   git tag prompt-0.1
   git tag --list prompt-0.1
   ```
   If empty, STOP.

4. Push:
   ```bash
   git push origin main
   git push origin prompt-0.1
   ```

5. Verify tag on origin:
   ```bash
   git ls-remote --tags origin
   ```
   Confirm `prompt-0.1` appears in the output. If missing, STOP.

---

## Closing

Run `/close` workflow from `.devin/workflows/close.md`. **Run all 21 steps** — do not skip any step even if its result is N/A. Per the new note added at S2.3, N/A results are reported in the final summary (step 20), not used as a reason to skip subsequent steps.

**Expected results**:
- Tests: N/A (no code, no `tests/test_*.py` files)
- Ruff: N/A (no Python code)
- Mypy: N/A (no Python code)
- Bandit: N/A (no Python code)
- pip-audit: 0 CVEs (scanned `txt/requirements.txt` only per OR39 — file is still empty, unchanged from prompt-0)
- Vulture: N/A (no Python code)
- Detect-secrets: pass (baseline unchanged from prompt-0 — no new files with potential secrets)
- Custom AR checks: N/A (no `sovereignai/` Python files yet — note: `/close` step 8 now references `sovereignai/` instead of `core/` per S2.1 fix, so the check will trivially pass with no files to scan)

After `/close` completes, create `logs/execution-log-prompt-0.1.md` with header template (per `/close` step 14). User will paste execution log content.

**Reminder**: Step 21 (`taskkill //F //IM bash.exe`) is mandatory. Do not skip. Per the new note added at S2.2, this step runs even for docs-only plans.

---

## Files WILL Create

- `logs/execution-log-prompt-0.1.md` (created by `/close` step 14)

## Files WILL Edit

- `AGENTS.md` (add OR40–OR43 at S0.3 — committed separately; update landmine-to-rule table at S3.4 — committed in main prompt-0.1 commit)
- `.devin/workflows/close.md` (fix `core/` → `sovereignai/` at S2.1; add mandatory note to step 21 at S2.2; add N/A handling note to Steps header at S2.3)
- `LANDMINES.md` (append L24–L27 at S3.2; update header at S3.3)
- `CHANGELOG.md` (append prompt-0.1 entry at S4)
- `PLANS.md` (add prompt-0.1 row at S5.1; update date at S5.2)

## Files WILL Delete

- `prompts/plan-0-Rev2.md` (S1.1 — superseded by prompts/plan-0.md)
- `prompts/plan-0-brief.md` (S1.3 — Round Table review complete, brief not preserved in repo per AI_HANDOFF.md)

## Files WILL Rename

- `prompts/plan-0-Rev3.md` → `prompts/plan-0.md` (S1.2 — canonical naming per AI_HANDOFF.md)

## Files WILL NOT Edit

- `AI_HANDOFF.md` (no changes needed — `.devin/` path is canonical, no other references need fixing)
- `AGENTS.md` rule text (beyond S0.3 OR40–OR43 addition and S3.4 landmine-to-rule table update — no other edits)
- `.devin/workflows/open.md` (already fixed in prompt-0)
- `.devin/workflows/verify.md` (no issues found)
- `.devin/workflows/scan.md` (no issues found)
- `documents/project-vision-Rev5.md` (locked — no edits)
- `documents/project-vision-Rev1.md` through `Rev4.md` (archived — do not touch)
- `documents/SovereignAI_Architecture_Decisions.md` (archived — DECISIONS.md at root is the live ADR)
- `documents/plan-1-4-scope-*.md` (archived — Plan 1–4 scope split is locked)
- `documents/round-table-vision-Rev*-brief.md` (archived — vision review is complete)
- `documents/handoff-prompt.md` (archived — AGENTS.md Rev2 fixes are locked)
- `documents/AGENTS-roundtable-brief.md` (archived)
- `prompts/plan-0.md` (the renamed file — content unchanged from Rev3)
- `pyproject.toml`, `txt/requirements.txt`, `.pre-commit-config.yaml`, `txt/vulture-whitelist.txt`, `txt/.secrets.baseline` (no changes — infrastructure is stable from prompt-0)
- `README.md`, `.gitignore` (no changes — content is stable from prompt-0)
- All `.gitkeep` files in directory structure (no changes — directories are stable from prompt-0)
- `DECISIONS.md`, `DEBT.md` (no new decisions or deferred items this plan)

---

*Plan 0.1 — Prompt-0.1 Cleanup. Rev1. Architect draft. Skips Round Table review per AI_HANDOFF.md scan-prompt exemption (mechanical cleanup, no architectural decisions).*
