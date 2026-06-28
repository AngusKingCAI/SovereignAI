# Plan 0.4 — Prompt-0.4 Cleanup (Mypy Filtering + Kill Bash at Start)

**Special plan**: Pre-Plan 1 cleanup. Fixes N3 (mypy fails when edited files include markdown) and N2 (Executor skips kill bash at end of `/close`). Adds kill bash at START of `/open` to clean orphaned processes from previous sessions, while keeping kill bash at END of `/close` for current session cleanup. No architectural work — mechanical only. Skips Round Table review (per AI_HANDOFF.md scan-prompt exemption).

Depends on: prompt-0.3
Vision principles: none (mechanical cleanup — no architectural impact)
Open questions resolved: none

---

## S0 — Opening

**S0.1** — Run `/open` workflow from `.devin/workflows/open.md`. Verify previous tag (`prompt-0.3`) exists on origin:

```bash
git fetch origin
git ls-remote --tags origin
```

Confirm `prompt-0.3` appears in the output. If missing, STOP — Plan 0.3 did not complete.

Confirm working copy is clean and on `main`:

```bash
git status -s
git branch --show-current
```

If dirty (excluding governance docs/plan files) or not on `main`, STOP.

**S0.2** — Read `AGENTS.md` in full. Note that OR22's always-on subset (OR5, OR6, OR15, OR16, OR34, AR5, AR16, AR21) applies to every edit in this plan. Note OR44 (workflow files are structured markdown — Edit tool only, never sed) — this plan edits workflow files, so OR44 is critical. Note OR46 (absolute venv paths) — all commands in this plan use `.venv/Scripts/` paths.

**S0.3** — Add OR47 to `AGENTS.md`. Commit before any other step.

Append the following rule to the Operational Rules section of `AGENTS.md`, after OR46 and before the "Landmines that have graduated to rules" section. Use the Edit tool (not shell append — OR7).

> OR47. Mypy is invoked on `.py` files only — never markdown, YAML, TOML, or other non-Python files. When `/close` step 3 or `/scan` step 1 runs mypy on "files edited this plan," the Executor must filter the file list to `.py` files only. If no `.py` files were edited this plan, mypy is N/A — report "N/A (no Python files edited)" in the final summary and continue to the next step. Do NOT pass markdown or other non-Python files to mypy — it will fail with "Duplicate module named __main__" or similar errors. The canonical invocation pattern is: `git diff --name-only HEAD~1 | grep '\.py$' | xargs .venv/Scripts/mypy.exe --ignore-missing-imports` (or the explicit file list filtered to `.py` files). At scan prompts (5, 10, 15...), `mypy .` scans the whole repo and naturally skips non-Python files — no filtering needed. (Source: L31 — prompt-0.3 execution, Executor ran mypy on `AGENTS.md CHANGELOG.md LANDMINES.md PLANS.md .devin/workflows/*.md prompts/*.md` and got "Duplicate module named __main__" error; Executor skipped mypy entirely, which would also skip Python files if any existed.)

Do **not** add an entry to the landmine-to-rule table at the bottom of `AGENTS.md` for OR47 yet — L31 is captured at S4 of this plan, and the table update happens at S4.4 (after LANDMINES.md is updated).

Commit (use multiple `-m` flags per OR42):

```bash
git add AGENTS.md
git commit -m "docs: add OR47 for prompt-0.4" -m "Mypy is invoked on .py files only — never markdown or other non-Python files. Captures L31 from prompt-0.3 execution where mypy was run on markdown files and failed with Duplicate module named __main__."
```

After edit, run `/verify`.

---

## S1 — Update `/open` Workflow: Add Kill Bash at Start

### S1.1 — Add kill bash as new step 1

Edit `.devin/workflows/open.md` (use Edit tool per OR44 — never sed). Insert a new step 1 before the current step 1 (tag verification). The new step kills orphaned bash.exe processes from previous sessions.

Old text (current step 1):
```
1. Verify previous plan's tag on origin:
   ```
   git fetch origin
   git ls-remote --tags origin | grep "prompt-{N-1}"
   ```
   If missing, STOP. Skip if Plan 1.
```

New text (new step 1 + renumbered step 2):
```
1. Kill orphaned bash.exe processes from previous sessions (Windows-specific):
   ```
   taskkill //F //IM bash.exe 2>&1 || true
   ```
   This kills all `bash.exe` processes, including the current session. The Executor's agent process is not affected — it spawns a fresh bash session for the next command automatically. This step cleans up orphans from previous sessions that may have crashed, been interrupted, or skipped `/close` step 21. The `|| true` ensures the workflow continues even if no bash.exe processes are running (taskkill exits non-zero when no processes match). Do NOT skip this step — orphaned bash processes accumulate across sessions and consume system resources.
   
   Note: a second `taskkill //F //IM bash.exe` runs at `/close` step 21 to clean up the current session's bash processes. Both are mandatory.

2. Verify previous plan's tag on origin:
   ```
   git fetch origin
   git ls-remote --tags origin | grep "prompt-{N-1}"
   ```
   If missing, STOP. Skip if Plan 1.
```

### S1.2 — Renumber subsequent steps

The current steps 2-7 become steps 3-8. Update each step number.

Old text (steps 2-7):
```
2. Confirm working copy is clean and on main:
   ```
   git status -s | tail -n 10
   git branch --show-current
   ```
   If dirty (excluding governance docs/plan files) or not on main, STOP.

3. Verify the project-local venv exists (per OR45). If `.venv/` does not exist, create it and install dev dependencies:
   ```
   if [ ! -d ".venv" ]; then
     py -3.11 -m venv .venv
     .venv/Scripts/pip.exe install -e .[dev]
   fi
   ```
   Verify the venv is functional:
   ```
   .venv/Scripts/python.exe --version
   .venv/Scripts/pip.exe --version
   ```
   Both commands must succeed. If either fails, STOP and report — the venv is broken and must be recreated (`rm -rf .venv && py -3.11 -m venv .venv && .venv/Scripts/pip.exe install -e .[dev]`).
   
   Note: per OR46, all subsequent commands in this plan and in `/close` use absolute venv paths (`.venv/Scripts/python.exe`, `.venv/Scripts/ruff.exe`, etc.). Do not rely on `source .venv/Scripts/activate` — it does not reliably persist in Git Bash on Windows (L30).

4. Read `AGENTS.md` in full.

5. Add any new rules the plan specifies to `AGENTS.md`. Commit:
   ```
   git add AGENTS.md
   git commit -m "docs: add rules for prompt-{N}"
   ```

6. Check for untracked governance docs or plan files:
   ```
   git status -s | grep -E "AGENTS.md|AI_HANDOFF.md|PLANS.md|CHANGELOG.md|LANDMINES.md|DECISIONS.md|CONTEXT.md|DEBT.md|project-vision|prompts/"
   ```
   If any found, commit separately:
   ```
   git add <files>
   git commit -m "docs: cleanup pre-prompt-{N}"
   git tag docs-cleanup-{N}
   ```

7. Proceed to plan body (S1 onward). Run `/verify` after each file edit.
```

New text (steps 3-8):
```
3. Confirm working copy is clean and on main:
   ```
   git status -s | tail -n 10
   git branch --show-current
   ```
   If dirty (excluding governance docs/plan files) or not on main, STOP.

4. Verify the project-local venv exists (per OR45). If `.venv/` does not exist, create it and install dev dependencies:
   ```
   if [ ! -d ".venv" ]; then
     py -3.11 -m venv .venv
     .venv/Scripts/pip.exe install -e .[dev]
   fi
   ```
   Verify the venv is functional:
   ```
   .venv/Scripts/python.exe --version
   .venv/Scripts/pip.exe --version
   ```
   Both commands must succeed. If either fails, STOP and report — the venv is broken and must be recreated (`rm -rf .venv && py -3.11 -m venv .venv && .venv/Scripts/pip.exe install -e .[dev]`).
   
   Note: per OR46, all subsequent commands in this plan and in `/close` use absolute venv paths (`.venv/Scripts/python.exe`, `.venv/Scripts/ruff.exe`, etc.). Do not rely on `source .venv/Scripts/activate` — it does not reliably persist in Git Bash on Windows (L30).

5. Read `AGENTS.md` in full.

6. Add any new rules the plan specifies to `AGENTS.md`. Commit:
   ```
   git add AGENTS.md
   git commit -m "docs: add rules for prompt-{N}"
   ```

7. Check for untracked governance docs or plan files:
   ```
   git status -s | grep -E "AGENTS.md|AI_HANDOFF.md|PLANS.md|CHANGELOG.md|LANDMINES.md|DECISIONS.md|CONTEXT.md|DEBT.md|project-vision|prompts/"
   ```
   If any found, commit separately:
   ```
   git add <files>
   git commit -m "docs: cleanup pre-prompt-{N}"
   git tag docs-cleanup-{N}
   ```

8. Proceed to plan body (S1 onward). Run `/verify` after each file edit.
```

After all edits, run `/verify`.

---

## S2 — Update `/close` Step 3: Mypy File Filtering (N3 fix)

### S2.1 — Add .py file filtering to mypy step

Edit `.devin/workflows/close.md` (use Edit tool per OR44). Update step 3 to filter edited files to `.py` only per OR47.

Old text (step 3):
```
3. Run mypy (use absolute venv path per OR46):
   - At scan prompts (5, 10, 15...): `.venv/Scripts/mypy.exe . --ignore-missing-imports`
   - At regular prompts: `.venv/Scripts/mypy.exe <files-edited-this-plan> --ignore-missing-imports`
   
   Pipe through `tail -n 3`. If errors, STOP.
```

New text:
```
3. Run mypy on Python files only (per OR47 — never pass markdown or other non-Python files to mypy):
   - At scan prompts (5, 10, 15...): `.venv/Scripts/mypy.exe . --ignore-missing-imports` (scans whole repo, naturally skips non-Python files)
   - At regular prompts: filter edited files to `.py` only, then run mypy:
     ```
     EDITED_PY_FILES=$(git diff --name-only HEAD~1 | grep '\.py$' | tr '\n' ' ')
     if [ -n "$EDITED_PY_FILES" ]; then
       .venv/Scripts/mypy.exe $EDITED_PY_FILES --ignore-missing-imports 2>&1 | tail -n 3
     else
       echo "mypy: N/A (no Python files edited this plan)"
     fi
     ```
     If no `.py` files were edited, mypy is N/A — report "N/A (no Python files edited)" in the final summary (step 20) and continue to step 4. Do NOT pass markdown or other non-Python files to mypy — it will fail with "Duplicate module named __main__" or similar errors (L31).
   
   If mypy reports errors on `.py` files, STOP.
```

After edit, run `/verify`.

---

## S3 — Update `/close` Step 21: Stronger Mandatory Language (N2 fix)

### S3.1 — Strengthen step 21 language

Edit `.devin/workflows/close.md`. Update step 21 to make it clearer that the plan is NOT complete until step 21 runs. The current language says "mandatory even for docs-only plans" but the Executor still treats the final summary (step 20) as the natural stopping point.

Old text (step 21):
```
21. Close Git Bash sessions (Windows-specific). This step is mandatory even for docs-only plans — do not skip:
   ```
   taskkill //F //IM bash.exe
   ```
   No output expected. Kills all `bash.exe` processes including the current session. This is the final step — no further commands will execute.
   If any prior step was skipped because its result was N/A (e.g., no Python code to test), this step still runs. N/A results are reported in the final summary (step 20), not used as a reason to skip subsequent steps.
```

New text:
```
21. Close Git Bash sessions (Windows-specific). **STOP CONDITION: the plan is NOT complete until this step executes.** Do not report "Plan X Complete" in step 20's final summary until step 21 has run. If you find yourself about to end the session after step 20, STOP — you have not finished. Run step 21 now:
   ```
   taskkill //F //IM bash.exe 2>&1 || true
   ```
   The `|| true` ensures the step succeeds even if no bash.exe processes are running. This kills all `bash.exe` processes including the current session — no further commands will execute after this step. 
   
   This step is mandatory for ALL plans, including docs-only plans. N/A results from prior steps (e.g., "Tests: N/A") do NOT make this step N/A — this step always runs. A second `taskkill` runs at the START of the next plan's `/open` step 1 to clean up any orphans if this step was somehow skipped.
```

After edit, run `/verify`.

---

## S4 — Append Landmine L31 to LANDMINES.md

### S4.1 — Read current LANDMINES.md

Read `LANDMINES.md` to confirm the last landmine number. Per prompt-0.3, the latest entry is L30. New landmines continue from L31.

### S4.2 — Append L31

Use the Edit tool to append the following entry to `LANDMINES.md`, after the L30 entry and before the "Process for capturing new landmines (L31+)" section (note: the section header text needs updating too — see S4.3):

```markdown
## L31 — Mypy fails when passed markdown or other non-Python files
**Trigger**: prompt-0.3, `/close` step 3, Executor ran `mypy AGENTS.md CHANGELOG.md LANDMINES.md PLANS.md .devin/workflows/*.md prompts/*.md --ignore-missing-imports` and got "Duplicate module named __main__" error.
**Impact**: Executor skipped mypy entirely with "N/A (no Python code)." This was technically correct for prompt-0.3 (no Python files existed), but the pattern would skip mypy on real Python files in Plan 1+ if any markdown files were also edited. Plan 1 will edit both Python files (sovereignai/*.py) and markdown files (PLANS.md, CHANGELOG.md) — passing all to mypy would fail on the markdown files.
**Graduated to**: OR47 (mypy is invoked on .py files only — never markdown, YAML, TOML, or other non-Python files).
```

After edit, run `/verify`.

### S4.3 — Update LANDMINES.md header

Update the header line to reflect the new landmine range. Use the Edit tool.

Old text:
```
Append-only. Selected landmines (L1–L9, L11, L12, L17) inherited from sovereign-ai (predecessor project) — these are the entries referenced in `AGENTS.md`'s landmine-to-rule table. L10, L13–L16, L18–L23 were not graduated to rules in SovereignAI and are not carried forward. SovereignAI-specific landmines L24–L27 captured during Plan 0 execution; L28–L29 captured during prompt-0.1 execution; L30 captured during prompt-0.2 execution. New landmines for SovereignAI continue from L31.
```

New text:
```
Append-only. Selected landmines (L1–L9, L11, L12, L17) inherited from sovereign-ai (predecessor project) — these are the entries referenced in `AGENTS.md`'s landmine-to-rule table. L10, L13–L16, L18–L23 were not graduated to rules in SovereignAI and are not carried forward. SovereignAI-specific landmines L24–L27 captured during Plan 0 execution; L28–L29 captured during prompt-0.1 execution; L30 captured during prompt-0.2 execution; L31 captured during prompt-0.3 execution. New landmines for SovereignAI continue from L32.
```

### S4.4 — Update "Process for capturing new landmines" section header

Old text:
```
## Process for capturing new landmines (L31+)
```

New text:
```
## Process for capturing new landmines (L32+)
```

### S4.5 — Update landmine-to-rule table in AGENTS.md

In `AGENTS.md`, find the "Landmines that have graduated to rules" table. Append 1 new row after L30:

Old text (last row of the table):
```
| L30 | OR46 | source .venv/Scripts/activate does not persist in Git Bash on Windows |
```

New text:
```
| L30 | OR46 | source .venv/Scripts/activate does not persist in Git Bash on Windows |
| L31 | OR47 | Mypy fails when passed markdown or other non-Python files |
```

After edit, run `/verify`.

---

## S5 — Update CHANGELOG.md

Use the Edit tool to append a new entry to the END of `CHANGELOG.md` (per OR12 — append to end only, never insert at top):

```markdown
## prompt-0.4 — Mypy filtering + kill bash at start

**Date**: 2026-06-28
**Plan file**: prompts/plan-0.4-Rev1.md

**Files changed**:
- AGENTS.md (added OR47; updated landmine-to-rule table with L31)
- .devin/workflows/open.md (added step 1: kill orphaned bash.exe processes from previous sessions; renumbered subsequent steps 2-8)
- .devin/workflows/close.md (updated step 3: mypy filters to .py files only per OR47; updated step 21: stronger mandatory language with STOP CONDITION)
- LANDMINES.md (appended L31; updated header; updated process section header)

**Results**:
- Tests: N/A (no code, no tests/test_*.py files)
- Ruff: 0 errors
- Mypy: N/A (no .py files edited this plan — per OR47, mypy is not invoked on markdown files)
- Bandit: 0 findings
- pip-audit: 0 CVEs (txt/requirements.txt still empty)
- Vulture: N/A (no Python code)
- Detect-secrets: pass (baseline unchanged)

**Notes**:
- Mechanical cleanup plan addressing issues discovered during prompt-0.3 execution.
- 1 new OR rule: OR47 (mypy is invoked on .py files only — never markdown or other non-Python files).
- 1 new landmine: L31 (mypy fails when passed markdown files).
- /open workflow: added step 1 (kill orphaned bash.exe from previous sessions). Subsequent steps renumbered 2-8. Kill bash at start cleans orphans from crashed/interrupted previous sessions; kill bash at /close step 21 cleans current session. Both are mandatory.
- /close step 3 fix: mypy now filters edited files to .py only via `git diff --name-only HEAD~1 | grep '\.py$'`. If no .py files were edited, mypy is N/A.
- /close step 21 fix: stronger language — "STOP CONDITION: the plan is NOT complete until this step executes. Do not report 'Plan X Complete' until step 21 has run."
- No Round Table review (scan-prompt exemption per AI_HANDOFF.md).
```

After edit, run `/verify`.

---

## S6 — Update PLANS.md

Use the Edit tool. Two edits:

### S6.1 — Add prompt-0.4 row to Completed Prompts table

Append a new row to the "Completed Prompts" table:

```
| prompt-0.4 | `prompt-0.4` | Mypy filtering + kill bash at start — OR47, L31, /open step 1 kill orphans, /close step 3 mypy .py filter, /close step 21 stronger language | N/A | 0 | N/A | 2026-06-28 |
```

### S6.2 — Verify Active Plan and Next-5-Prompt Queue

Read-only verification:
- Active Plan should still show "Plan 1 — awaiting execution." If not, STOP and report.
- Next-5-Prompt Queue should still show Plan 1 in slot 1 with "▶️ Active" status. If not, STOP and report.

After all edits, run `/verify`.

---

## S7 — Commit and Tag Prompt-0.4

**STOP condition**: If any `/verify` step failed, STOP and report before committing.

1. Stage all changes (note: AGENTS.md was committed at S0.3; the landmine-to-rule table update at S4.5 is a separate edit that IS in this commit). Verify `.venv/` is NOT staged:

   ```bash
   git add -A
   git status -s | tail -n 20
   ```

   Verify the staged files match the expected changes:
   - Modified: `.devin/workflows/open.md`, `.devin/workflows/close.md`, `AGENTS.md` (landmine-to-rule table), `LANDMINES.md`, `CHANGELOG.md`, `PLANS.md`
   - NOT staged: `.venv/` (gitignored)
   - NOT staged: `prompts/plan-0.1-Rev1.md`, `prompts/plan-0.2-Rev1.md`, `prompts/plan-0.3-Rev1.md` (kept per handoff line 96 — no deletions)

   If `.venv/` appears in staged files, STOP — `.gitignore` is broken.

2. Commit (use multiple `-m` flags per OR42):

   ```bash
   git commit -m "prompt-0.4: Mypy filtering + kill bash at start" -m "Mypy: /close step 3 now filters edited files to .py only per OR47. If no .py files were edited, mypy is N/A. Prevents 'Duplicate module named __main__' error when markdown files are passed to mypy." -m "Kill bash: /open step 1 added — kills orphaned bash.exe processes from previous sessions. /close step 21 strengthened with STOP CONDITION language — plan is NOT complete until step 21 runs." -m "Landmines: appended L31 (mypy fails on markdown files); updated landmine-to-rule table." -m "No prompts/ files deleted — Rev-suffixed plan files kept per AI_HANDOFF.md line 96."
   ```

3. Tag:

   ```bash
   git tag prompt-0.4
   git tag --list prompt-0.4
   ```

   If empty, STOP.

4. Push:

   ```bash
   git push origin main
   git push origin prompt-0.4
   ```

5. Verify tag on origin:

   ```bash
   git ls-remote --tags origin
   ```

   Confirm `prompt-0.4` appears in the output. If missing, STOP.

---

## Closing

Run `/close` workflow from `.devin/workflows/close.md`. **Run all 21 steps** — do not skip any step even if its result is N/A.

**Prerequisite**: The venv must exist before running `/close` (verified at `/open` step 4 per the renumbered workflow). If the venv does not exist, STOP and run `/open` first.

**Expected results**:
- Tests: N/A (no `tests/test_*.py` files)
- Ruff: 0 errors
- Mypy: N/A (no `.py` files edited this plan — per OR47, mypy is not invoked on markdown files; the new step 3 logic handles this automatically)
- Bandit: 0 findings
- pip-audit: 0 CVEs (scanned `txt/requirements.txt` only per OR39)
- Vulture: N/A (no Python code)
- Detect-secrets: pass (baseline unchanged)
- Custom AR checks: N/A (no `sovereignai/` Python files yet)

**Key verifications**:
1. `/close` step 3 (mypy) must use the new `.py`-filtering logic. If the Executor runs mypy on markdown files, STOP — the workflow file edit didn't take effect.
2. `/close` step 21 (kill bash) must run. If the Executor stops after step 20's final summary, the user will prompt — but the new STOP CONDITION language should prevent this.

After `/close` completes, create `logs/execution-log-prompt-0.4.md` with header template (per `/close` step 14). User will paste execution log content.

**Reminder**: Step 21 (`taskkill //F //IM bash.exe`) is mandatory. The plan is NOT complete until it runs. Do not report "Plan 0.4 Complete" until step 21 has executed.

---

## Files WILL Create

- `logs/execution-log-prompt-0.4.md` (created by `/close` step 14)

## Files WILL Edit

- `AGENTS.md` (add OR47 at S0.3 — committed separately; update landmine-to-rule table at S4.5 — committed in main prompt-0.4 commit)
- `.devin/workflows/open.md` (add step 1 kill bash at S1.1; renumber steps 2-7 → 3-8 at S1.2)
- `.devin/workflows/close.md` (update step 3 mypy filtering at S2.1; strengthen step 21 language at S3.1)
- `LANDMINES.md` (append L31 at S4.2; update header at S4.3; update process section header at S4.4)
- `CHANGELOG.md` (append prompt-0.4 entry at S5)
- `PLANS.md` (add prompt-0.4 row at S6.1)

## Files WILL Delete

(none — Rev-suffixed plan files in prompts/ are kept per AI_HANDOFF.md line 96)

## Files WILL NOT Edit

- `AI_HANDOFF.md` (no changes needed)
- `AGENTS.md` rule text (beyond S0.3 OR47 addition and S4.5 landmine-to-rule table update — no other edits)
- `.devin/workflows/verify.md` (no changes — already uses venv paths from prompt-0.3)
- `.devin/workflows/scan.md` (no changes — already uses venv paths from prompt-0.3; mypy at scan prompts uses `mypy .` which naturally skips non-Python files)
- `documents/project-vision-Rev5.md` (locked — no edits)
- `documents/project-vision-Rev1.md` through `Rev4.md` (archived — do not touch)
- `documents/SovereignAI_Architecture_Decisions.md` (archived — DECISIONS.md at root is the live ADR)
- `documents/plan-1-4-scope-*.md` (archived — Plan 1–4 scope split is locked)
- `documents/round-table-vision-Rev*-brief.md` (archived — vision review is complete)
- `documents/handoff-prompt.md` (archived — AGENTS.md Rev2 fixes are locked)
- `documents/AGENTS-roundtable-brief.md` (archived)
- `prompts/plan-0.md` (kept as-is)
- `prompts/plan-0.1-Rev1.md` (kept as-is — Rev files preserved per handoff line 96)
- `prompts/plan-0.2-Rev1.md` (kept as-is — Rev files preserved per handoff line 96)
- `prompts/plan-0.3-Rev1.md` (kept as-is — Rev files preserved per handoff line 96)
- `README.md`, `.gitignore` (no changes — content is stable from prompt-0)
- `txt/requirements.txt`, `txt/vulture-whitelist.txt`, `txt/.secrets.baseline` (no changes — infrastructure is stable)
- `pyproject.toml` (no changes — ruff config already fixed in prompt-0.2)
- `.pre-commit-config.yaml` (no changes — bandit exclusions already set in prompt-0.1)
- All `.gitkeep` files (no changes — directories are stable)
- `DECISIONS.md`, `DEBT.md` (no new decisions or deferred items this plan)

---

*Plan 0.4 — Prompt-0.4 Cleanup. Rev1. Architect draft. Skips Round Table review per AI_HANDOFF.md scan-prompt exemption (mechanical cleanup, no architectural decisions).*
