# Plan 0.2 — Prompt-0.2 Cleanup (Environment + Doc Drift Fix-Up)

**Special plan**: Pre-Plan 1 cleanup. Fixes environment PATH mismatch, ruff config deprecation, PLANS.md doc drift, and captures the `sed`-on-workflow-files violation observed during prompt-0.1's execution. No architectural work — mechanical only. Skips Round Table review (per AI_HANDOFF.md scan-prompt exemption).

Depends on: prompt-0.1
Vision principles: none (mechanical cleanup — no architectural impact)
Open questions resolved: none

---

## S0 — Opening

**S0.1** — Run `/open` workflow from `.devin/workflows/open.md`. Verify previous tag (`prompt-0.1`) exists on origin:

```bash
git fetch origin
git ls-remote --tags origin
```

Confirm `prompt-0.1` appears in the output. If missing, STOP — Plan 0.1 did not complete.

Confirm working copy is clean and on `main`:

```bash
git status -s
git branch --show-current
```

If dirty (excluding governance docs/plan files) or not on `main`, STOP.

**S0.2** — Read `AGENTS.md` in full. Note that OR22's always-on subset (OR5, OR6, OR15, OR16, OR34, AR5, AR16, AR21) applies to every edit in this plan. Note OR40–OR43 (added in prompt-0.1) addressing shell/tooling issues — OR44 (added at S0.3 below) extends OR7's structured-markdown scope to include workflow files.

**S0.3** — Add OR44 to `AGENTS.md`. Commit before any other step.

Append the following rule to the Operational Rules section of `AGENTS.md`, after OR43 and before the "Landmines that have graduated to rules" section. Use the Edit tool (not shell append — OR7).

> OR44. Workflow files (`.devin/workflows/*.md`) are structured markdown — OR7 applies. Edits to `open.md`, `verify.md`, `close.md`, `scan.md` must use the Edit tool with exact `old_str`/`new_str` pairs, never `sed`, `Set-Content`, or shell redirection. If the Edit tool fails to match (typically due to whitespace or line-ending differences), the Executor must: (a) re-read the target file to confirm exact current content, (b) retry the Edit tool with a smaller, more targeted `old_str` (e.g., a single line rather than a multi-line block), (c) if still failing, STOP and report — do NOT fall back to `sed` or other shell-based text manipulation. Workflow files are loaded and parsed by the Executor at every plan's `/open` and `/close` — silent corruption from a `sed` regex bug would break every subsequent plan. (Source: L28 — prompt-0.1 execution, Executor used `sed -i` on `.devin/workflows/close.md` after 3 Edit-tool failures, producing correct output but establishing a dangerous precedent.)

Do **not** add an entry to the landmine-to-rule table at the bottom of `AGENTS.md` for OR44 yet — L28 is captured at S5 of this plan, and the table update happens at S5.4 (after LANDMINES.md is updated).

Commit (use multiple `-m` flags per OR42):

```bash
git add AGENTS.md
git commit -m "docs: add OR44 for prompt-0.2" -m "Workflow files (.devin/workflows/*.md) are structured markdown — OR7 applies. Captures L28 from prompt-0.1 execution where sed was used on close.md after Edit-tool failures."
```

After edit, run `/verify`.

---

## S1 — Diagnose and Fix Python Path Mismatch (N5)

### S1.1 — Diagnose

**Problem**: During prompt-0.1 execution, `python -m pytest tests/ -vvv` failed with `No module named pytest` because `python` on PATH resolves to `C:\Users\King\AppData\Local\hermes\hermes-agent\venv\Scripts\python.exe` (hermes-agent's venv), but `pip install -e .[dev]` installed dev tools into `C:\Users\King\AppData\Local\Programs\Python\Python311\Lib\site-packages` (the main Python 3.11 install). The two Pythons don't share site-packages.

**Diagnosis commands** (run these to confirm the mismatch — output goes to execution log):

```bash
which python
which pip
which py
python --version
pip --version
py --version 2>&1 || echo "py launcher not available"
python -c "import sys; print(sys.executable); print(sys.path)" 2>&1 | tail -n 5
pip --version
```

Record the output in the execution log. The expected mismatch: `python` points to hermes-agent venv, `pip` points to Python 3.11 main install.

### S1.2 — Decision: project-local venv vs. explicit path

Per `project-vision-Rev5.md` P4 (local-first) and the single-developer constraint, the cleanest fix is a **project-local venv** at `C:/SovereignAI/.venv/`. This:
- Isolates SovereignAI's dependencies from hermes-agent and the main Python install
- Makes `python` and `pip` resolve to the same interpreter when the venv is activated
- Is standard Python practice (PEP 405)
- Already covered by `.gitignore` (added in prompt-0 — `.venv/` is ignored)

**Alternative considered**: Document an explicit Python path (e.g., `C:/Users/King/AppData/Local/Programs/Python/Python311/python.exe`) in the workflow files. Rejected because: (a) hardcodes a machine-specific path into repo files, (b) breaks if the user reinstalls Python or moves to a different machine, (c) the workflow files reference `python -m pytest` not the absolute path — changing every reference is invasive.

### S1.3 — Create project-local venv

```bash
py -3.11 -m venv .venv
```

If `py` launcher is not available, use the explicit path:

```bash
"C:/Users/King/AppData/Local/Programs/Python/Python311/python.exe" -m venv .venv
```

If both fail, STOP and report — Python 3.11 is required per `pyproject.toml`'s `requires-python = ">=3.11"`.

### S1.4 — Activate venv and reinstall dev dependencies

Activate the venv (Git Bash on Windows uses `source`):

```bash
source .venv/Scripts/activate
```

Verify activation:

```bash
which python
which pip
python --version
```

Both `python` and `pip` should now resolve to `.venv/Scripts/`. If not, STOP and report.

Reinstall dev dependencies into the venv:

```bash
pip install -e .[dev]
```

Verify all dev tools are installed and accessible:

```bash
python -m pytest --version
python -m ruff --version
python -m mypy --version
python -m bandit --version
python -m pip_audit --version
python -m vulture --version
python -m detect_secrets --version
python -m pre_commit --version
```

If any tool reports "No module named X", STOP and report.

### S1.5 — Document venv activation requirement in AGENTS.md

Add a new operational rule OR45 to `AGENTS.md` (after OR44, before the "Landmines that have graduated to rules" section):

> OR45. Project-local venv at `.venv/` is the canonical Python environment. The Executor activates the venv at the start of every plan (after S0.1, before any `python` or `pip` command) using `source .venv/Scripts/activate` (Git Bash on Windows). If the venv does not exist, the Executor creates it via `py -3.11 -m venv .venv` then runs `pip install -e .[dev]` to populate dev dependencies. The system `python` and `pip` on PATH may point to different installations (e.g., hermes-agent's venv vs. Python 3.11 main install) — never assume they share site-packages. The venv ensures `python` and `pip` resolve to the same interpreter. `.venv/` is gitignored (per `.gitignore` added in prompt-0) — it is never committed. (Source: L29 — prompt-0.1 execution, `python -m pytest` failed because `python` resolved to hermes-agent venv while `pip install -e .[dev]` installed into Python 3.11 main install.)

Commit (separate from S0.3 — OR44 and OR45 are different rules):

```bash
git add AGENTS.md
git commit -m "docs: add OR45 for prompt-0.2" -m "Project-local venv at .venv/ is the canonical Python environment. Captures L29 from prompt-0.1 execution where python and pip resolved to different interpreters."
```

After edit, run `/verify`.

### S1.6 — Update `/open` workflow to activate venv

Edit `.devin/workflows/open.md` (use Edit tool per OR44 — never `sed`). Add a new step between current step 2 (clean working copy) and step 3 (read AGENTS.md):

Old text (steps 2-3):
```
2. Confirm working copy is clean and on master:
   ```
   git status -s | tail -n 10
   git branch --show-current
   ```
   If dirty (excluding governance docs/plan files) or not on master, STOP.

3. Read `AGENTS.md` in full.
```

New text (steps 2-4, with venv activation inserted):
```
2. Confirm working copy is clean and on main:
   ```
   git status -s | tail -n 10
   git branch --show-current
   ```
   If dirty (excluding governance docs/plan files) or not on main, STOP.

3. Activate the project-local venv (per OR45):
   ```
   source .venv/Scripts/activate
   ```
   If `.venv/` does not exist, create it and install dev dependencies:
   ```
   py -3.11 -m venv .venv
   source .venv/Scripts/activate
   pip install -e .[dev]
   ```
   Verify activation:
   ```
   which python
   which pip
   ```
   Both should resolve to `.venv/Scripts/`. If not, STOP and report.

4. Read `AGENTS.md` in full.
```

Note: this also fixes the `master` → `main` reference in step 2 (already fixed in `open.md` during prompt-0, but verify it's still `main` — if `open.md` was reverted or has residual `master` references, fix them here too).

After edit, run `/verify`.

### S1.7 — Update `/close` workflow to assume venv is active

Edit `.devin/workflows/close.md`. The `/close` workflow's commands (`python -m pytest`, `ruff check`, `mypy`, `bandit`, `pip-audit`, `vulture`, `detect-secrets`) all assume `python` and `pip` are on PATH and point to the correct interpreter. Per OR45, the venv is activated at `/open` step 3 and stays active through `/close`. No command changes needed — but add a note at the top of the Steps section.

Old text (top of Steps section, after the N/A handling note added in prompt-0.1):
```
## Steps

**N/A handling**: When a step's result is N/A...
```

New text:
```
## Steps

**Prerequisite**: The project-local venv (`.venv/`) must be active before running any step in this workflow. The venv is activated at `/open` step 3 (per OR45). If the venv is not active, STOP and run `source .venv/Scripts/activate` first.

**N/A handling**: When a step's result is N/A...
```

After edit, run `/verify`.

---

## S2 — Fix Ruff Config Deprecation Warning (N6)

### S2.1 — Update `pyproject.toml`

Edit `pyproject.toml`. The current `[tool.ruff.pydocstyle]` section is deprecated — modern ruff wants it under `[tool.ruff.lint.pydocstyle]`.

Old text:
```toml
[tool.ruff.lint]
select = ["E", "F", "W", "D", "I", "N", "UP", "B", "C4", "SIM"]
# D100 (missing module docstring) and D104 (missing package docstring) are
# excluded because empty __init__.py files in the scaffold don't need
# docstrings yet. AR21 covers def/async def docstrings (D103) — that's the
# enforced rule. Revisit at Plan 1 when __init__.py files get content.
ignore = ["D100", "D104"]

[tool.ruff.pydocstyle]
convention = "google"
```

New text:
```toml
[tool.ruff.lint]
select = ["E", "F", "W", "D", "I", "N", "UP", "B", "C4", "SIM"]
# D100 (missing module docstring) and D104 (missing package docstring) are
# excluded because empty __init__.py files in the scaffold don't need
# docstrings yet. AR21 covers def/async def docstrings (D103) — that's the
# enforced rule. Revisit at Plan 1 when __init__.py files get content.
ignore = ["D100", "D104"]

[tool.ruff.lint.pydocstyle]
convention = "google"
```

After edit, run `/verify` (TOML syntax check per `/verify` step 1).

### S2.2 — Verify ruff no longer warns

```bash
ruff check . 2>&1 | tail -n 5
```

The deprecation warning should be gone. If it persists, the config change didn't take effect — re-read `pyproject.toml` to confirm the edit landed, then retry. If still warning, STOP and report.

---

## S3 — Fix PLANS.md Doc Drift (N3, N4)

### S3.1 — Fix "Key Document Cross-References" landmine range (N3)

Edit `PLANS.md`. In the "Key Document Cross-References" section:

Old text:
```
- **Known failure patterns** → `LANDMINES.md` (append-only; L1–L23 inherited from sovereign-ai predecessor)
```

New text:
```
- **Known failure patterns** → `LANDMINES.md` (append-only; L1–L9, L11, L12, L17 inherited from sovereign-ai predecessor; L24+ SovereignAI-specific)
```

After edit, run `/verify`.

### S3.2 — Fix "Baseline Reconciliation Notes" wording (N4)

Edit `PLANS.md`. In the "Baseline Reconciliation Notes" section:

Old text:
```
*No plans executed yet. Baselines will be established at Plan 1 `/close` and recorded here. Each entry follows this format:*
```

New text:
```
*No code plans executed yet (prompt-0 and prompt-0.1 were docs-only). Test and static-analysis baselines will be established at Plan 1 `/close` and recorded here. Each entry follows this format:*
```

After edit, run `/verify`.

### S3.3 — Update "Last updated" line

Edit `PLANS.md`:

Old text:
```
**Last updated**: 2026-06-28
```

New text:
```
**Last updated**: 2026-06-28 (prompt-0.2)
```

(Or today's date if different — use the actual execution date.)

After edit, run `/verify`.

---

## S4 — Verify Static Analysis Baselines Post-Fix

After S1-S3 are complete, run all static analysis tools to confirm the fixes didn't break anything and to capture the pre-Plan-1 baseline state:

```bash
python -m pytest tests/ -vvv 2>&1 | tail -n 10
ruff check . 2>&1 | tail -n 3
mypy sovereignai/ --ignore-missing-imports 2>&1 | tail -n 3
bandit -r . -ll --exclude .venv,venv,env,.git,node_modules,__pycache__,build,dist,.tox,.eggs,.pytest_cache 2>&1 | tail -n 5
pip-audit --strict --requirement txt/requirements.txt 2>&1 | tail -n 5
vulture . --min-confidence 80 --exclude .venv,venv,env,.git,node_modules,__pycache__,build,dist,.tox,.eggs,.pytest_cache,.mypy_cache,.ruff_cache,htmlcov 2>&1 | tail -n 5
detect-secrets scan --baseline txt/.secrets.baseline 2>&1 | tail -n 3
```

**Expected results** (all should pass / report N/A):
- pytest: N/A (no `tests/test_*.py` files — `tests/` contains only `.gitkeep`)
- ruff: 0 errors (deprecation warning gone)
- mypy: N/A (no `.py` files in `sovereignai/`)
- bandit: 0 findings
- pip-audit: 0 CVEs (`txt/requirements.txt` is empty)
- vulture: N/A (no Python code)
- detect-secrets: pass (baseline unchanged)

If any tool fails, STOP and report. The `python -m pytest` command should now work because the venv is active (per S1.4) — this is the key verification that N5 is fixed.

Record the actual output in the execution log. These become the pre-Plan-1 baseline values that Plan 1's `/close` will compare against.

---

## S5 — Append Landmine L28, L29 to LANDMINES.md

### S5.1 — Read current LANDMINES.md

Read `LANDMINES.md` to confirm the last landmine number. Per prompt-0.1, the latest entries are L24-L27. New landmines continue from L28.

### S5.2 — Append L28, L29

Use the Edit tool to append the following entries to `LANDMINES.md`, after the L27 entry and before the "Process for capturing new landmines (L28+)" section (note: the section header text needs updating too — see S5.3):

```markdown
## L28 — sed used on workflow files after Edit-tool failures
**Trigger**: prompt-0.1, S2.2 and S2.3, Executor used `sed -i` on `.devin/workflows/close.md` after 3 Edit-tool attempts failed due to whitespace mismatch.
**Impact**: The `sed` commands produced correct output (verified post-execution), but the precedent is dangerous — `sed` regex bugs could silently corrupt workflow files loaded by every subsequent plan's `/open` and `/close`. OR7 listed structured-markdown files but did not explicitly include `.devin/workflows/*.md`, so the Executor interpreted the gap as "OR7 doesn't apply to workflow files."
**Graduated to**: OR44 (workflow files are structured markdown — OR7 applies; if Edit tool fails, STOP and report, do not fall back to sed).

## L29 — python and pip resolve to different interpreters on Windows
**Trigger**: prompt-0.1, `/close` step 1, `python -m pytest tests/ -vvv` failed with `No module named pytest`. Diagnosis: `python` on PATH resolved to `C:\Users\King\AppData\Local\hermes\hermes-agent\venv\Scripts\python.exe` (hermes-agent's venv), but `pip install -e .[dev]` (run during prompt-0) installed dev tools into `C:\Users\King\AppData\Local\Programs\Python\Python311\Lib\site-packages` (the main Python 3.11 install). The two Pythons don't share site-packages.
**Impact**: `/close` step 1 (pytest) would have failed even if test files existed. The Executor reported "Tests: N/A (no tests directory exists)" — technically true, but masked the underlying PATH issue. Plan 1's first `/close` would have hit the same wall.
**Graduated to**: OR45 (project-local venv at `.venv/` is the canonical Python environment; activate before any python/pip command).
```

After edit, run `/verify`.

### S5.3 — Update LANDMINES.md header

Update the header line to reflect the new landmine range. Use the Edit tool.

Old text:
```
Append-only. Selected landmines (L1–L9, L11, L12, L17) inherited from sovereign-ai (predecessor project) — these are the entries referenced in `AGENTS.md`'s landmine-to-rule table. L10, L13–L16, L18–L23 were not graduated to rules in SovereignAI and are not carried forward. SovereignAI-specific landmines L24–L27 captured during Plan 0 execution. New landmines for SovereignAI continue from L28.
```

New text:
```
Append-only. Selected landmines (L1–L9, L11, L12, L17) inherited from sovereign-ai (predecessor project) — these are the entries referenced in `AGENTS.md`'s landmine-to-rule table. L10, L13–L16, L18–L23 were not graduated to rules in SovereignAI and are not carried forward. SovereignAI-specific landmines L24–L27 captured during Plan 0 execution; L28–L29 captured during prompt-0.1 execution. New landmines for SovereignAI continue from L30.
```

### S5.4 — Update "Process for capturing new landmines" section header

The section at the bottom of LANDMINES.md says "(L24+)" — update to "(L30+)":

Old text:
```
## Process for capturing new landmines (L24+)
```

New text:
```
## Process for capturing new landmines (L30+)
```

### S5.5 — Update landmine-to-rule table in AGENTS.md

In `AGENTS.md`, find the "Landmines that have graduated to rules" table. Append 2 new rows after L27:

Old text (last row of the table):
```
| L27 | (workflow fix only — /close step 21 + Steps header) | Executor skipped /close steps when expected result was N/A |
```

New text:
```
| L27 | (workflow fix only — /close step 21 + Steps header) | Executor skipped /close steps when expected result was N/A |
| L28 | OR44 | sed used on workflow files after Edit-tool failures |
| L29 | OR45 | python and pip resolve to different interpreters on Windows |
```

After edit, run `/verify`.

---

## S6 — Update CHANGELOG.md

Use the Edit tool to append a new entry to the END of `CHANGELOG.md` (per OR12 — append to end only, never insert at top):

```markdown
## prompt-0.2 — Environment + doc drift cleanup

**Date**: 2026-06-28
**Plan file**: prompts/plan-0.2-Rev1.md

**Files changed**:
- AGENTS.md (added OR44, OR45; updated landmine-to-rule table with L28, L29)
- .devin/workflows/open.md (added venv activation step 3 per OR45; fixed master->main in step 2 if still present)
- .devin/workflows/close.md (added venv prerequisite note to Steps section)
- pyproject.toml (fixed ruff config: [tool.ruff.pydocstyle] -> [tool.ruff.lint.pydocstyle])
- PLANS.md (fixed landmine range in cross-references; fixed baseline notes wording; updated date)
- LANDMINES.md (appended L28, L29; updated header; updated process section header)
- .venv/ (created — gitignored, not committed)

**Results**:
- Tests: N/A (no code, no tests/test_*.py files)
- Ruff: 0 errors (deprecation warning resolved)
- Mypy: N/A (no Python code)
- Bandit: 0 findings
- pip-audit: 0 CVEs (txt/requirements.txt still empty)
- Vulture: N/A (no Python code)
- Detect-secrets: pass (baseline unchanged)

**Notes**:
- Mechanical cleanup plan addressing issues discovered during prompt-0.1 execution.
- 2 new OR rules: OR44 (workflow files are structured markdown — OR7 applies), OR45 (project-local venv at .venv/ is canonical Python environment).
- 2 new landmines: L28 (sed on workflow files), L29 (python/pip PATH mismatch).
- Environment fix: created .venv/ via `py -3.11 -m venv .venv`, installed dev deps via `pip install -e .[dev]`. Verified `python -m pytest --version` works (no more "No module named pytest").
- Ruff config fix: moved [tool.ruff.pydocstyle] to [tool.ruff.lint.pydocstyle] per ruff deprecation warning.
- PLANS.md doc drift fix: landmine range updated to reflect L24-L29; baseline notes wording clarified.
- No Round Table review (scan-prompt exemption per AI_HANDOFF.md).
```

After edit, run `/verify`.

---

## S7 — Update PLANS.md

Use the Edit tool. Two edits:

### S7.1 — Add prompt-0.2 row to Completed Prompts table

Append a new row to the "Completed Prompts" table:

```
| prompt-0.2 | `prompt-0.2` | Environment + doc drift cleanup — OR44-OR45, L28-L29, venv setup, ruff config fix | N/A | 0 | N/A | 2026-06-28 |
```

### S7.2 — Verify Active Plan and Next-5-Prompt Queue

Read-only verification:
- Active Plan should still show "Plan 1 — awaiting execution." If not, STOP and report.
- Next-5-Prompt Queue should still show Plan 1 in slot 1 with "▶️ Active" status. If not, STOP and report.

After all edits, run `/verify`.

---

## S8 — Commit and Tag Prompt-0.2

**STOP condition**: If any `/verify` step failed, STOP and report before committing.

1. Stage all changes (note: AGENTS.md was committed at S0.3 and S1.5; the landmine-to-rule table update at S5.5 is a separate edit that IS in this commit). Verify `.venv/` is NOT staged (`.gitignore` should prevent it):

   ```bash
   git add -A
   git status -s | tail -n 20
   ```

   Verify the staged files match the expected changes:
   - Modified: `.devin/workflows/open.md`, `.devin/workflows/close.md`, `AGENTS.md` (landmine-to-rule table only — OR44 and OR45 already committed at S0.3 and S1.5), `pyproject.toml`, `PLANS.md`, `CHANGELOG.md`, `LANDMINES.md`
   - NOT staged: `.venv/` (gitignored)

   If `.venv/` appears in staged files, STOP — `.gitignore` is broken. Run `git reset .venv/` and verify `.gitignore` contains `.venv/`.

2. Commit (use multiple `-m` flags per OR42):

   ```bash
   git commit -m "prompt-0.2: Environment + doc drift cleanup" -m "Environment: created .venv/ via py -3.11 -m venv; installed dev deps via pip install -e .[dev]. Verified python -m pytest works (fixes L29 — python/pip PATH mismatch on Windows)." -m "Workflow files: /open step 3 activates venv per OR45; /close Steps section adds venv prerequisite note." -m "Ruff config: [tool.ruff.pydocstyle] -> [tool.ruff.lint.pydocstyle] per ruff deprecation warning." -m "Landmines: appended L28 (sed on workflow files), L29 (python/pip PATH mismatch); updated landmine-to-rule table." -m "PLANS.md: fixed landmine range in cross-references; fixed baseline notes wording."
   ```

3. Tag:

   ```bash
   git tag prompt-0.2
   git tag --list prompt-0.2
   ```

   If empty, STOP.

4. Push:

   ```bash
   git push origin main
   git push origin prompt-0.2
   ```

5. Verify tag on origin:

   ```bash
   git ls-remote --tags origin
   ```

   Confirm `prompt-0.2` appears in the output. If missing, STOP.

---

## Closing

Run `/close` workflow from `.devin/workflows/close.md`. **Run all 21 steps** — do not skip any step even if its result is N/A. Per the N/A handling note added in prompt-0.1, N/A results are reported in the final summary (step 20), not used as a reason to skip subsequent steps.

**Prerequisite**: The venv must be active before running `/close` (per the new prerequisite note added at S1.7). If the venv is not active, run `source .venv/Scripts/activate` first.

**Expected results**:
- Tests: N/A (no `tests/test_*.py` files — `tests/` contains only `.gitkeep`)
- Ruff: 0 errors (deprecation warning resolved by S2.1)
- Mypy: N/A (no `.py` files in `sovereignai/`)
- Bandit: 0 findings
- pip-audit: 0 CVEs (scanned `txt/requirements.txt` only — file is still empty)
- Vulture: N/A (no Python code)
- Detect-secrets: pass (baseline unchanged — no new files with potential secrets)
- Custom AR checks: N/A (no `sovereignai/` Python files yet — `/close` step 8 references `sovereignai/` per prompt-0.1 fix)

**Key verification**: `python -m pytest --version` (run as part of `/close` step 1) must succeed without "No module named pytest" error. This confirms N5 is fixed and Plan 1 can run `/close` step 1 successfully once test files exist.

After `/close` completes, create `logs/execution-log-prompt-0.2.md` with header template (per `/close` step 14). User will paste execution log content.

**Reminder**: Step 21 (`taskkill //F //IM bash.exe`) is mandatory. Do not skip.

---

## Files WILL Create

- `.venv/` (S1.3 — created via `py -3.11 -m venv .venv`; gitignored, NOT committed)
- `logs/execution-log-prompt-0.2.md` (created by `/close` step 14)

## Files WILL Edit

- `AGENTS.md` (add OR44 at S0.3 — committed separately; add OR45 at S1.5 — committed separately; update landmine-to-rule table at S5.5 — committed in main prompt-0.2 commit)
- `.devin/workflows/open.md` (add venv activation step 3 at S1.6; verify step 2 says `main` not `master`)
- `.devin/workflows/close.md` (add venv prerequisite note to Steps section at S1.7)
- `pyproject.toml` (move `[tool.ruff.pydocstyle]` to `[tool.ruff.lint.pydocstyle]` at S2.1)
- `PLANS.md` (fix landmine range at S3.1; fix baseline notes wording at S3.2; update date at S3.3; add prompt-0.2 row at S7.1)
- `CHANGELOG.md` (append prompt-0.2 entry at S6)
- `LANDMINES.md` (append L28, L29 at S5.2; update header at S5.3; update process section header at S5.4)

## Files WILL NOT Edit

- `AI_HANDOFF.md` (no changes needed)
- `AGENTS.md` rule text (beyond S0.3 OR44 addition, S1.5 OR45 addition, and S5.5 landmine-to-rule table update — no other edits)
- `.devin/workflows/verify.md` (no issues found)
- `.devin/workflows/scan.md` (no issues found)
- `documents/project-vision-Rev5.md` (locked — no edits)
- `documents/project-vision-Rev1.md` through `Rev4.md` (archived — do not touch)
- `documents/SovereignAI_Architecture_Decisions.md` (archived — DECISIONS.md at root is the live ADR)
- `documents/plan-1-4-scope-*.md` (archived — Plan 1–4 scope split is locked)
- `documents/round-table-vision-Rev*-brief.md` (archived — vision review is complete)
- `documents/handoff-prompt.md` (archived — AGENTS.md Rev2 fixes are locked)
- `documents/AGENTS-roundtable-brief.md` (archived)
- `prompts/plan-0.md` (locked — Plan 0 is complete)
- `README.md`, `.gitignore` (no changes — content is stable from prompt-0)
- `txt/requirements.txt`, `txt/vulture-whitelist.txt`, `txt/.secrets.baseline` (no changes — infrastructure is stable)
- `.pre-commit-config.yaml` (no changes — bandit exclusions already set in prompt-0.1)
- All `.gitkeep` files (no changes — directories are stable)
- `DECISIONS.md`, `DEBT.md` (no new decisions or deferred items this plan)

---

*Plan 0.2 — Prompt-0.2 Cleanup. Rev1. Architect draft. Skips Round Table review per AI_HANDOFF.md scan-prompt exemption (mechanical cleanup, no architectural decisions).*
