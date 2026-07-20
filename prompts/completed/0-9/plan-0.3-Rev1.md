# Plan 0.3 — Prompt-0.3 Cleanup (Venv Path + Repo Hygiene)

**Special plan**: Pre-Plan 1 cleanup. Fixes the venv activation gap (S1.6/S1.7 from prompt-0.2 were skipped), updates all workflow files to use absolute venv paths instead of relying on `source activate`, and removes the Rev-suffixed plan files that were accidentally committed in prompt-0.2. No architectural work — mechanical only. Skips Round Table review (per AI_HANDOFF.md scan-prompt exemption).

Depends on: prompt-0.2
Vision principles: none (mechanical cleanup — no architectural impact)
Open questions resolved: none

---

## S0 — Opening

**S0.1** — Run `/open` workflow from `.devin/workflows/open.md`. Verify previous tag (`prompt-0.2`) exists on origin:

```bash
git fetch origin
git ls-remote --tags origin
```

Confirm `prompt-0.2` appears in the output. If missing, STOP — Plan 0.2 did not complete.

Confirm working copy is clean and on `main`:

```bash
git status -s
git branch --show-current
```

If dirty (excluding governance docs/plan files) or not on `main`, STOP.

**S0.2** — Read `AGENTS.md` in full. Note that OR22's always-on subset (OR5, OR6, OR15, OR16, OR34, AR5, AR16, AR21) applies to every edit in this plan. Note OR44 (workflow files are structured markdown — Edit tool only, never sed) — this plan edits all 4 workflow files, so OR44 is critical. Note OR45 (project-local venv) — this plan refines OR45 to use absolute paths instead of `source activate`.

**S0.3** — Add OR46 to `AGENTS.md`. Commit before any other step.

Append the following rule to the Operational Rules section of `AGENTS.md`, after OR45 and before the "Landmines that have graduated to rules" section. Use the Edit tool (not shell append — OR7).

> OR46. Workflow commands use absolute venv paths, not `source activate`. Git Bash on Windows does not reliably persist `source .venv/Scripts/activate` across separate command invocations in the same session — `which python` may show the venv path but `which pip` still shows the system path, or vice versa. To avoid this inconsistency, all workflow files (`.devin/workflows/open.md`, `verify.md`, `close.md`, `scan.md`) and all plan steps that invoke Python tools must use absolute paths: `.venv/Scripts/python.exe -m pytest`, `.venv/Scripts/ruff.exe`, `.venv/Scripts/mypy.exe`, `.venv/Scripts/bandit.exe`, `.venv/Scripts/pip-audit.exe`, `.venv/Scripts/vulture.exe`, `.venv/Scripts/detect-secrets.exe`. The Executor may still run `source .venv/Scripts/activate` at session start for interactive convenience, but workflow files and plan steps must not depend on activation persisting. If `.venv/` does not exist, create it per OR45 before running any command. (Source: L30 — prompt-0.2 execution, `source .venv/Scripts/activate` did not persist; Executor fell back to absolute paths `.venv/Scripts/python.exe` for all subsequent commands.)

Do **not** add an entry to the landmine-to-rule table at the bottom of `AGENTS.md` for OR46 yet — L30 is captured at S6 of this plan, and the table update happens at S6.4 (after LANDMINES.md is updated).

Commit (use multiple `-m` flags per OR42):

```bash
git add AGENTS.md
git commit -m "docs: add OR46 for prompt-0.3" -m "Workflow commands use absolute venv paths (.venv/Scripts/python.exe, etc.) not source activate. Captures L30 from prompt-0.2 execution where source activate did not persist in Git Bash on Windows."
```

After edit, run `/verify`.

---

## S1 — Update OR45 to Reflect Absolute-Path Approach

### S1.1 — Revise OR45 text

OR45 (added in prompt-0.2) currently says to use `source .venv/Scripts/activate`. Per OR46 (added at S0.3 above) and L30, this approach doesn't reliably persist. Update OR45 to reference OR46.

Edit `AGENTS.md`. Find OR45 (line ~208 per prompt-0.2 verification). Use the Edit tool with exact `old_str`/`new_str` (per OR44 — never sed).

Old text (the relevant portion of OR45 to update — the activation instruction):
```
The Executor activates the venv at the start of every plan (after S0.1, before any `python` or `pip` command) using `source .venv/Scripts/activate` (Git Bash on Windows). If the venv does not exist, the Executor creates it via `py -3.11 -m venv .venv` then runs `pip install -e .[dev]` to populate dev dependencies. The system `python` and `pip` on PATH may point to different installations (e.g., hermes-agent's venv vs. Python 3.11 main install) — never assume they share site-packages. The venv ensures `python` and `pip` resolve to the same interpreter. `.venv/` is gitignored (per `.gitignore` added in prompt-0) — it is never committed.
```

New text:
```
The Executor creates the venv at project setup (one-time) via `py -3.11 -m venv .venv` then runs `.venv/Scripts/pip.exe install -e .[dev]` to populate dev dependencies. If the venv already exists, this step is skipped. The system `python` and `pip` on PATH may point to different installations (e.g., hermes-agent's venv vs. Python 3.11 main install) — never assume they share site-packages. Per OR46, all workflow commands and plan steps use absolute venv paths (`.venv/Scripts/python.exe`, `.venv/Scripts/pip.exe`, etc.) rather than relying on `source .venv/Scripts/activate` (which does not reliably persist in Git Bash on Windows per L30). The Executor may still run `source .venv/Scripts/activate` at session start for interactive convenience, but workflow files must not depend on activation persisting. `.venv/` is gitignored (per `.gitignore` added in prompt-0) — it is never committed.
```

After edit, run `/verify`.

---

## S2 — Update `/open` Workflow (S1.6 from prompt-0.2 — was skipped)

### S2.1 — Add venv verification step

Edit `.devin/workflows/open.md` (use Edit tool per OR44 — never sed). Insert a new step 3 between current step 2 (clean working copy) and step 3 (read AGENTS.md). The new step verifies the venv exists and creates it if not.

Old text (current steps 2-3):
```
2. Confirm working copy is clean and on main:
   ```
   git status -s | tail -n 10
   git branch --show-current
   ```
   If dirty (excluding governance docs/plan files) or not on main, STOP.

3. Read `AGENTS.md` in full.
```

New text (steps 2-4, with venv verification inserted):
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
```

Note: this also renumbers the subsequent steps (current step 3 → 4, step 4 → 5, step 5 → 6, step 6 → 7). Update the step numbers accordingly:

Old text (steps 4-6):
```
4. Add any new rules the plan specifies to `AGENTS.md`. Commit:
   ```
   git add AGENTS.md
   git commit -m "docs: add rules for prompt-{N}"
   ```

5. Check for untracked governance docs or plan files:
   ```
   git status -s | grep -E "AGENTS.md|AI_HANDOFF.md|PLANS.md|CHANGELOG.md|LANDMINES.md|DECISIONS.md|CONTEXT.md|DEBT.md|project-vision|prompts/"
   ```
   If any found, commit separately:
   ```
   git add <files>
   git commit -m "docs: cleanup pre-prompt-{N}"
   git tag docs-cleanup-{N}
   ```

6. Proceed to plan body (S1 onward). Run `/verify` after each file edit.
```

New text (steps 5-7):
```
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

After all edits, run `/verify`.

---

## S3 — Update `/verify` Workflow

### S3.1 — Update python commands to use venv

Edit `.devin/workflows/verify.md` (use Edit tool per OR44). The current step 1 uses `python -c "..."` for syntax checks. Update to use `.venv/Scripts/python.exe -c "..."`.

Old text (step 1):
```
1. Syntax check the edited file:
   - Python: `python -c "import ast; ast.parse(open('<file>.py').read())"`
   - JSON: `python -c "import json; json.load(open('<file>'))"`
   - YAML: `python -c "import yaml; yaml.safe_load(open('<file>'))"`
   - TOML: `python -c "import tomllib; tomllib.load(open('<file>', 'rb'))"`
   - Markdown: skip
   
   If syntax error, STOP. Fix before proceeding.
```

New text:
```
1. Syntax check the edited file (use absolute venv path per OR46):
   - Python: `.venv/Scripts/python.exe -c "import ast; ast.parse(open('<file>.py').read())"`
   - JSON: `.venv/Scripts/python.exe -c "import json; json.load(open('<file>'))"`
   - YAML: `.venv/Scripts/python.exe -c "import yaml; yaml.safe_load(open('<file>'))"` (requires PyYAML — install via `.venv/Scripts/pip.exe install pyyaml` if missing)
   - TOML: `.venv/Scripts/python.exe -c "import tomllib; tomllib.load(open('<file>', 'rb'))"`
   - Markdown: skip
   
   If syntax error, STOP. Fix before proceeding.
```

### S3.2 — Update ruff command to use venv

Old text (step 2):
```
2. Run ruff on the edited file:
   ```
   ruff check <file>
   ```
   If auto-fixable, apply `ruff check --fix <file>` and re-verify. If not auto-fixable, STOP.
```

New text:
```
2. Run ruff on the edited file (use absolute venv path per OR46):
   ```
   .venv/Scripts/ruff.exe check <file>
   ```
   If auto-fixable, apply `.venv/Scripts/ruff.exe check --fix <file>` and re-verify. If not auto-fixable, STOP.
```

After all edits, run `/verify`.

---

## S4 — Update `/close` Workflow (S1.7 from prompt-0.2 — was skipped)

### S4.1 — Add venv prerequisite note

Edit `.devin/workflows/close.md` (use Edit tool per OR44). Add a prerequisite note at the top of the Steps section.

Old text (top of Steps section, after the N/A handling note):
```
## Steps

**N/A handling**: When a step's result is N/A (e.g., no Python code to test, no new landmines discovered), the Executor runs the step, observes the N/A result, and reports it in the final summary (step 20). The Executor does NOT skip the step. Skipping steps because "the result would be N/A" is an OR34 violation. The only steps that may be skipped are those explicitly marked "skip if N/A" in this workflow file.

1. Run full test suite:
```

New text:
```
## Steps

**Prerequisite**: The project-local venv (`.venv/`) must exist and be functional before running any step in this workflow. The venv is verified at `/open` step 3 (per OR45). If the venv does not exist, STOP and run `/open` first. Per OR46, all commands below use absolute venv paths (`.venv/Scripts/python.exe`, `.venv/Scripts/ruff.exe`, etc.) — do not rely on `source .venv/Scripts/activate` (it does not reliably persist in Git Bash on Windows per L30).

**N/A handling**: When a step's result is N/A (e.g., no Python code to test, no new landmines discovered), the Executor runs the step, observes the N/A result, and reports it in the final summary (step 20). The Executor does NOT skip the step. Skipping steps because "the result would be N/A" is an OR34 violation. The only steps that may be skipped are those explicitly marked "skip if N/A" in this workflow file.

1. Run full test suite:
```

### S4.2 — Update step 1 (pytest) to use venv

Old text (step 1):
```
1. Run full test suite:
   ```
   python -m pytest tests/ -vvv
   ```
   If any test fails, STOP.
```

New text:
```
1. Run full test suite (use absolute venv path per OR46):
   ```
   .venv/Scripts/python.exe -m pytest tests/ -vvv
   ```
   If any test fails, STOP. If pytest reports "no tests ran" and the plan was supposed to add tests, STOP — test collection may have failed silently.
```

### S4.3 — Update step 2 (ruff) to use venv

Old text (step 2):
```
2. Run ruff (full repo):
   ```
   ruff check . 2>&1 | tail -n 3
   ```
   If errors, STOP.
```

New text:
```
2. Run ruff (full repo, use absolute venv path per OR46):
   ```
   .venv/Scripts/ruff.exe check . 2>&1 | tail -n 3
   ```
   If errors, STOP.
```

### S4.4 — Update step 3 (mypy) to use venv

Old text (step 3):
```
3. Run mypy:
   - At scan prompts (5, 10, 15...): `mypy . --ignore-missing-imports`
   - At regular prompts: `mypy <files-edited-this-plan> --ignore-missing-imports`
   
   Pipe through `tail -n 3`. If errors, STOP.
```

New text:
```
3. Run mypy (use absolute venv path per OR46):
   - At scan prompts (5, 10, 15...): `.venv/Scripts/mypy.exe . --ignore-missing-imports`
   - At regular prompts: `.venv/Scripts/mypy.exe <files-edited-this-plan> --ignore-missing-imports`
   
   Pipe through `tail -n 3`. If errors, STOP.
```

### S4.5 — Update step 4 (bandit) to use venv

Old text (step 4):
```
4. Run bandit:
   ```
   bandit -r . -ll --exclude .venv,venv,env,.git,node_modules,__pycache__,build,dist,.tox,.eggs,.pytest_cache 2>&1 | tail -n 5
   ```
   If findings, STOP.
```

New text:
```
4. Run bandit (use absolute venv path per OR46):
   ```
   .venv/Scripts/bandit.exe -r . -ll --exclude .venv,venv,env,.git,node_modules,__pycache__,build,dist,.tox,.eggs,.pytest_cache 2>&1 | tail -n 5
   ```
   If findings, STOP.
```

### S4.6 — Update step 5 (pip-audit) to use venv

Old text (step 5):
```
5. Run pip-audit:
   ```
   pip-audit --strict 2>&1 | tail -n 5
   ```
   If CVEs, STOP.
```

New text:
```
5. Run pip-audit (use absolute venv path per OR46; scan requirements file only per OR39):
   ```
   .venv/Scripts/pip-audit.exe --strict --requirement txt/requirements.txt 2>&1 | tail -n 5
   ```
   If CVEs, STOP.
```

Note: this also fixes a residual issue from prompt-0.2 — the `/close` workflow's step 5 still said `pip-audit --strict` (environment scan) instead of `pip-audit --strict --requirement txt/requirements.txt` (requirements file scan per OR39). The workflow file was never updated to match OR39's requirement.

### S4.7 — Update step 6 (vulture) to use venv

Old text (step 6):
```
6. Run vulture:
   ```
   vulture . --min-confidence 80 --exclude .venv,venv,env,.git,node_modules,__pycache__,build,dist,.tox,.eggs,.pytest_cache,.mypy_cache,.ruff_cache,htmlcov 2>&1 | tail -n 5
   ```
   Compare against `txt/vulture-whitelist.txt`. If new findings, STOP.
```

New text:
```
6. Run vulture (use absolute venv path per OR46):
   ```
   .venv/Scripts/vulture.exe . --min-confidence 80 --exclude .venv,venv,env,.git,node_modules,__pycache__,build,dist,.tox,.eggs,.pytest_cache,.mypy_cache,.ruff_cache,htmlcov 2>&1 | tail -n 5
   ```
   Compare against `txt/vulture-whitelist.txt`. If new findings, STOP.
```

### S4.8 — Update step 7 (detect-secrets) to use venv

Old text (step 7):
```
7. Run detect-secrets:
   ```
   detect-secrets scan --baseline txt/.secrets.baseline
   ```
   If exit code != 0, STOP — a new secret was introduced. Either update the baseline (if false positive) or remove the secret. Do not commit until this passes.
```

New text:
```
7. Run detect-secrets (use absolute venv path per OR46):
   ```
   .venv/Scripts/detect-secrets.exe scan --baseline txt/.secrets.baseline
   ```
   If exit code != 0, STOP — a new secret was introduced. Either update the baseline (if false positive, use `.venv/Scripts/detect-secrets.exe audit txt/.secrets.baseline` per OR40) or remove the secret. Do not commit until this passes.
```

After all edits, run `/verify`.

---

## S5 — Update `/scan` Workflow

### S5.1 — Update step 1 (scan tools) to use venv

Edit `.devin/workflows/scan.md` (use Edit tool per OR44). Update all tool invocations to use absolute venv paths.

Old text (step 1):
```
1. Run all scan tools in full, one at a time (parallel execution corrupts output streams):
   - `python -m pytest tests/ -vvv` (full verbose, no piping)
   - `ruff check . 2>&1 | tail -n 3`
   - `mypy . --ignore-missing-imports 2>&1 | tail -n 3` (full repo at scan prompts)
   - `bandit -r . -ll --exclude .venv,venv,env,.git,node_modules,__pycache__,build,dist,.tox,.eggs,.pytest_cache 2>&1 | tail -n 5`
   - `pip-audit --strict 2>&1 | tail -n 5`
   - `vulture . --min-confidence 80 --exclude .venv,venv,env,.git,node_modules,__pycache__,build,dist,.tox,.eggs,.pytest_cache,.mypy_cache,.ruff_cache,htmlcov 2>&1 | tail -n 5` (compare against `txt/vulture-whitelist.txt`)
   - `detect-secrets scan --baseline txt/.secrets.baseline`
   - Custom AR static analysis checks (same as `/close` step 8)
   - **Auto-discovered tools**: any test suite or static analysis tool configured in `pyproject.toml`, `pytest.ini`, `.pre-commit-config.yaml`, or similar. Run them all automatically.
   
   If any tool reports new findings, STOP.
```

New text:
```
1. Run all scan tools in full, one at a time (parallel execution corrupts output streams per OR3). Use absolute venv paths per OR46:
   - `.venv/Scripts/python.exe -m pytest tests/ -vvv` (full verbose, no piping)
   - `.venv/Scripts/ruff.exe check . 2>&1 | tail -n 3`
   - `.venv/Scripts/mypy.exe . --ignore-missing-imports 2>&1 | tail -n 3` (full repo at scan prompts)
   - `.venv/Scripts/bandit.exe -r . -ll --exclude .venv,venv,env,.git,node_modules,__pycache__,build,dist,.tox,.eggs,.pytest_cache 2>&1 | tail -n 5`
   - `.venv/Scripts/pip-audit.exe --strict --requirement txt/requirements.txt 2>&1 | tail -n 5` (scan requirements file only per OR39)
   - `.venv/Scripts/vulture.exe . --min-confidence 80 --exclude .venv,venv,env,.git,node_modules,__pycache__,build,dist,.tox,.eggs,.pytest_cache,.mypy_cache,.ruff_cache,htmlcov 2>&1 | tail -n 5` (compare against `txt/vulture-whitelist.txt`)
   - `.venv/Scripts/detect-secrets.exe scan --baseline txt/.secrets.baseline`
   - Custom AR static analysis checks (same as `/close` step 8)
   - **Auto-discovered tools**: any test suite or static analysis tool configured in `pyproject.toml`, `pytest.ini`, `.pre-commit-config.yaml`, or similar. Run them all automatically.
   
   If any tool reports new findings, STOP.
```

### S5.2 — Update step 6 (final pytest) to use venv

Old text (step 6):
```
6. Run full test suite (final confirmation after any fixes from steps 2-5):
   ```
   python -m pytest tests/ -vvv
   ```
```

New text:
```
6. Run full test suite (final confirmation after any fixes from steps 2-5, use absolute venv path per OR46):
   ```
   .venv/Scripts/python.exe -m pytest tests/ -vvv
   ```
```

### S5.3 — Update step 7 (coverage) to use venv

Old text (step 7):
```
7. Verify coverage hasn't dropped >5% from baseline:
   ```
   python -m pytest tests/ --cov=. --cov-report=term 2>&1 | tail -n 10
   ```
```

New text:
```
7. Verify coverage hasn't dropped >5% from baseline (use absolute venv path per OR46):
   ```
   .venv/Scripts/python.exe -m pytest tests/ --cov=. --cov-report=term 2>&1 | tail -n 10
   ```
```

After all edits, run `/verify`.

---

## S6 — Append Landmine L30 to LANDMINES.md

### S6.1 — Read current LANDMINES.md

Read `LANDMINES.md` to confirm the last landmine number. Per prompt-0.2, the latest entries are L28-L29. New landmines continue from L30.

### S6.2 — Append L30

Use the Edit tool to append the following entry to `LANDMINES.md`, after the L29 entry and before the "Process for capturing new landmines (L30+)" section (note: the section header text needs updating too — see S6.3):

```markdown
## L30 — source .venv/Scripts/activate does not persist in Git Bash on Windows
**Trigger**: prompt-0.2, S1.4, Executor ran `source .venv/Scripts/activate` then `which python` returned the venv path but `which pip` returned the system path (`/c/Users/King/AppData/Local/Programs/Python/Python311/Scripts/pip`). Activation did not reliably persist across separate command invocations.
**Impact**: Executor fell back to absolute paths (`.venv/Scripts/python.exe`, `.venv/Scripts/pip.exe`) for all subsequent commands. This worked but required verbose command syntax. If `/open` workflow relied on `source activate` (as prompt-0.2's S1.6 originally specified but was skipped), every subsequent plan would hit the same activation issue.
**Graduated to**: OR46 (workflow commands use absolute venv paths, not source activate).
```

After edit, run `/verify`.

### S6.3 — Update LANDMINES.md header

Update the header line to reflect the new landmine range. Use the Edit tool.

Old text:
```
Append-only. Selected landmines (L1–L9, L11, L12, L17) inherited from sovereign-ai (predecessor project) — these are the entries referenced in `AGENTS.md`'s landmine-to-rule table. L10, L13–L16, L18–L23 were not graduated to rules in SovereignAI and are not carried forward. SovereignAI-specific landmines L24–L27 captured during Plan 0 execution; L28–L29 captured during prompt-0.1 execution. New landmines for SovereignAI continue from L30.
```

New text:
```
Append-only. Selected landmines (L1–L9, L11, L12, L17) inherited from sovereign-ai (predecessor project) — these are the entries referenced in `AGENTS.md`'s landmine-to-rule table. L10, L13–L16, L18–L23 were not graduated to rules in SovereignAI and are not carried forward. SovereignAI-specific landmines L24–L27 captured during Plan 0 execution; L28–L29 captured during prompt-0.1 execution; L30 captured during prompt-0.2 execution. New landmines for SovereignAI continue from L31.
```

### S6.4 — Update "Process for capturing new landmines" section header

The section at the bottom of LANDMINES.md says "(L30+)" — update to "(L31+)":

Old text:
```
## Process for capturing new landmines (L30+)
```

New text:
```
## Process for capturing new landmines (L31+)
```

### S6.5 — Update landmine-to-rule table in AGENTS.md

In `AGENTS.md`, find the "Landmines that have graduated to rules" table. Append 1 new row after L29:

Old text (last row of the table):
```
| L29 | OR45 | python and pip resolve to different interpreters on Windows |
```

New text:
```
| L29 | OR45 | python and pip resolve to different interpreters on Windows |
| L30 | OR46 | source .venv/Scripts/activate does not persist in Git Bash on Windows |
```

After edit, run `/verify`.

---

## S7 — Verify prompts/ Directory State

### S7.1 — Verify Rev files are present

Per AI_HANDOFF.md line 58 (`Plan files: C:/SovereignAI/prompts/plan-{N}-Rev{n}.md`) and line 96 (`All Revs are kept forever — no deletion. The prompts/ directory accumulates the full history.`), the `prompts/` directory should contain Rev-suffixed plan files for every revision ever drafted.

Read-only verification:
```bash
ls prompts/
```

Expected files (at minimum):
- `prompts/plan-0.md` (Plan 0 Rev3 content — renamed during prompt-0.1; see S7.2 note below)
- `prompts/plan-0.1-Rev1.md` (committed in prompt-0.2)
- `prompts/plan-0.2-Rev1.md` (committed in prompt-0.2)
- `prompts/plan-0.3-Rev1.md` (this plan — will be copied by user per handoff line 108)

If any expected file is missing, STOP and report.

### S7.2 — Note: `prompts/plan-0.md` naming inconsistency

**Observation** (no action this plan): `prompts/plan-0.md` lacks a Rev suffix, while `prompts/plan-0.1-Rev1.md` and `prompts/plan-0.2-Rev1.md` have Rev suffixes. Per AI_HANDOFF.md line 58, the canonical format is `plan-{N}-Rev{n}.md` — so `plan-0.md` should arguably be `plan-0-Rev3.md` (its actual revision).

This inconsistency was introduced in prompt-0.1 when the user (following my incorrect advice) renamed `plan-0-Rev3.md` → `plan-0.md`. Two options for a future cleanup plan:
- (a) Rename `prompts/plan-0.md` → `prompts/plan-0-Rev3.md` (aligns with handoff line 58)
- (b) Leave as-is and accept `plan-0.md` as the "final executed version" while Rev files represent in-progress drafts (aligns with handoff line 108's "Copy `plan-{N}-Rev{n}.md` to `C:/SovereignAI/prompts/plan-{N}.md`")

The handoff has internally conflicting guidance on this point (line 58 says Rev suffix; line 108 says strip suffix on copy). User should decide which interpretation is canonical before Plan 1 starts. **Do not act on this in Plan 0.3** — it's an observation for the user to resolve, not a mechanical fix.

### S7.3 — Note: `prompts/plan-0-Rev2.md` was deleted in prompt-0.1

**Observation** (no action this plan): In prompt-0.1, I incorrectly advised deleting `prompts/plan-0-Rev2.md` (along with renaming Rev3 → plan-0.md and deleting the brief). Per handoff line 96 ("All Revs are kept forever — no deletion"), this deletion was wrong. The file is preserved in git history (commit `724fe07` and earlier) and can be restored via `git show 724fe07^:prompts/plan-0-Rev2.md > prompts/plan-0-Rev2.md` if the user wants it back.

The brief deletion (`prompts/plan-0-brief.md`) was correct — per handoff line 92, briefs live in `/home/z/my-project/download/`, not in `prompts/`.

**Do not act on this in Plan 0.3** — restoration is a user decision. Noted here for completeness.

---

## S8 — Update CHANGELOG.md

Use the Edit tool to append a new entry to the END of `CHANGELOG.md` (per OR12 — append to end only, never insert at top):

```markdown
## prompt-0.3 — Venv path + workflow file cleanup

**Date**: 2026-06-28
**Plan file**: prompts/plan-0.3-Rev1.md

**Files changed**:
- AGENTS.md (added OR46; revised OR45 to reference OR46; updated landmine-to-rule table with L30)
- .devin/workflows/open.md (added step 3: venv verification + creation if missing; renumbered subsequent steps)
- .devin/workflows/verify.md (updated python and ruff commands to use .venv/Scripts/ absolute paths)
- .devin/workflows/close.md (added venv prerequisite note; updated steps 1-7 to use .venv/Scripts/ absolute paths; fixed step 5 pip-audit to use --requirement per OR39)
- .devin/workflows/scan.md (updated steps 1, 6, 7 to use .venv/Scripts/ absolute paths)
- LANDMINES.md (appended L30; updated header; updated process section header)

**Results**:
- Tests: N/A (no code, no tests/test_*.py files)
- Ruff: 0 errors
- Mypy: N/A (no Python code)
- Bandit: 0 findings
- pip-audit: 0 CVEs (txt/requirements.txt still empty)
- Vulture: N/A (no Python code)
- Detect-secrets: pass (baseline unchanged)

**Notes**:
- Mechanical cleanup plan addressing issues discovered during prompt-0.2 execution.
- 1 new OR rule: OR46 (workflow commands use absolute venv paths, not source activate).
- 1 new landmine: L30 (source activate does not persist in Git Bash on Windows).
- Workflow files: all 4 (.devin/workflows/open.md, verify.md, close.md, scan.md) updated to use .venv/Scripts/python.exe, .venv/Scripts/ruff.exe, etc. instead of relying on PATH.
- /close step 5 fix: pip-audit now uses --requirement txt/requirements.txt per OR39 (was previously environment scan — residual issue from prompt-0.2).
- /open step 3 added: verifies .venv/ exists, creates it if missing.
- No prompts/ files deleted — Rev-suffixed plan files (plan-0.1-Rev1.md, plan-0.2-Rev1.md) are kept per AI_HANDOFF.md line 96 ("All Revs are kept forever — no deletion. The prompts/ directory accumulates the full history.").
- Observation (no action): prompts/plan-0.md lacks Rev suffix while plan-0.1-Rev1.md and plan-0.2-Rev1.md have suffixes. Handoff has internally conflicting guidance (line 58 says Rev suffix; line 108 says strip suffix on copy). User should decide which interpretation is canonical before Plan 1 starts.
- No Round Table review (scan-prompt exemption per AI_HANDOFF.md).
```

After edit, run `/verify`.

---

## S9 — Update PLANS.md

Use the Edit tool. Two edits:

### S9.1 — Add prompt-0.3 row to Completed Prompts table

Append a new row to the "Completed Prompts" table:

```
| prompt-0.3 | `prompt-0.3` | Venv path + repo hygiene cleanup — OR46, L30, workflow files use absolute venv paths | N/A | 0 | N/A | 2026-06-28 |
```

### S9.2 — Verify Active Plan and Next-5-Prompt Queue

Read-only verification:
- Active Plan should still show "Plan 1 — awaiting execution." If not, STOP and report.
- Next-5-Prompt Queue should still show Plan 1 in slot 1 with "▶️ Active" status. If not, STOP and report.

After all edits, run `/verify`.

---

## S10 — Commit and Tag Prompt-0.3

**STOP condition**: If any `/verify` step failed, STOP and report before committing.

1. Stage all changes (note: AGENTS.md was committed at S0.3; the OR45 revision at S1.1 and landmine-to-rule table update at S6.5 are separate edits that ARE in this commit). Verify `.venv/` is NOT staged (`.gitignore` should prevent it):

   ```bash
   git add -A
   git status -s | tail -n 20
   ```

   Verify the staged files match the expected changes:
- Modified: `.devin/workflows/open.md`, `.devin/workflows/verify.md`, `.devin/workflows/close.md`, `.devin/workflows/scan.md`, `AGENTS.md` (OR45 revision + landmine-to-rule table), `LANDMINES.md`, `CHANGELOG.md`, `PLANS.md`
- NOT staged: `.venv/` (gitignored)
- NOT staged: `prompts/plan-0.1-Rev1.md`, `prompts/plan-0.2-Rev1.md` (kept per handoff line 96 — "All Revs are kept forever")

   If `.venv/` appears in staged files, STOP — `.gitignore` is broken. Run `git reset .venv/` and verify `.gitignore` contains `.venv/`.

2. Commit (use multiple `-m` flags per OR42):

   ```bash
   git commit -m "prompt-0.3: Venv path + workflow file cleanup" -m "Workflow files: all 4 (.devin/workflows/open.md, verify.md, close.md, scan.md) updated to use .venv/Scripts/python.exe, .venv/Scripts/ruff.exe, etc. instead of relying on PATH. /open step 3 added: verifies .venv/ exists, creates it if missing. /close step 5 fix: pip-audit now uses --requirement txt/requirements.txt per OR39." -m "Landmines: appended L30 (source activate does not persist in Git Bash on Windows); updated landmine-to-rule table." -m "No prompts/ files deleted — Rev-suffixed plan files are kept per AI_HANDOFF.md line 96 (All Revs are kept forever)."
   ```

3. Tag:

   ```bash
   git tag prompt-0.3
   git tag --list prompt-0.3
   ```

   If empty, STOP.

4. Push:

   ```bash
   git push origin main
   git push origin prompt-0.3
   ```

5. Verify tag on origin:

   ```bash
   git ls-remote --tags origin
   ```

   Confirm `prompt-0.3` appears in the output. If missing, STOP.

---

## Closing

Run `/close` workflow from `.devin/workflows/close.md`. **Run all 21 steps** — do not skip any step even if its result is N/A. Per the N/A handling note, N/A results are reported in the final summary (step 20), not used as a reason to skip subsequent steps.

**Prerequisite**: The venv must exist before running `/close` (per the new prerequisite note added at S4.1). The venv was created in prompt-0.2 and should still exist at `.venv/`. If `/open` step 3 (added at S2.1) was run correctly, the venv is verified. If not, run `.venv/Scripts/pip.exe install -e .[dev]` to ensure dev deps are installed.

**Expected results**:
- Tests: N/A (no `tests/test_*.py` files — `tests/` contains only `.gitkeep`)
- Ruff: 0 errors
- Mypy: N/A (no `.py` files in `sovereignai/`)
- Bandit: 0 findings
- pip-audit: 0 CVEs (scanned `txt/requirements.txt` only per OR39 — file is still empty)
- Vulture: N/A (no Python code)
- Detect-secrets: pass (baseline unchanged — no new files with potential secrets)
- Custom AR checks: N/A (no `sovereignai/` Python files yet)

**Key verification**: All `/close` steps must use `.venv/Scripts/python.exe`, `.venv/Scripts/ruff.exe`, etc. (per OR46). If any step uses bare `python` or `ruff`, STOP — the workflow file edits didn't take effect.

After `/close` completes, create `logs/execution-log-prompt-0.3.md` with header template (per `/close` step 14). User will paste execution log content.

**Reminder**: Step 21 (`taskkill //F //IM bash.exe`) is mandatory. Do not skip.

---

## Files WILL Create

- `logs/execution-log-prompt-0.3.md` (created by `/close` step 14)

## Files WILL Edit

- `AGENTS.md` (add OR46 at S0.3 — committed separately; revise OR45 at S1.1 — committed in main prompt-0.3 commit; update landmine-to-rule table at S6.5 — committed in main prompt-0.3 commit)
- `.devin/workflows/open.md` (add step 3 venv verification at S2.1; renumber steps 4-6 → 5-7)
- `.devin/workflows/verify.md` (update python and ruff commands to absolute venv paths at S3.1-S3.2)
- `.devin/workflows/close.md` (add venv prerequisite note at S4.1; update steps 1-7 to absolute venv paths at S4.2-S4.8)
- `.devin/workflows/scan.md` (update steps 1, 6, 7 to absolute venv paths at S5.1-S5.3)
- `LANDMINES.md` (append L30 at S6.2; update header at S6.3; update process section header at S6.4)
- `CHANGELOG.md` (append prompt-0.3 entry at S8)
- `PLANS.md` (add prompt-0.3 row at S9.1)

## Files WILL Delete

(none — Rev-suffixed plan files in prompts/ are kept per AI_HANDOFF.md line 96)

## Files WILL NOT Edit

- `AI_HANDOFF.md` (no changes needed)
- `AGENTS.md` rule text (beyond S0.3 OR46 addition, S1.1 OR45 revision, and S6.5 landmine-to-rule table update — no other edits)
- `.devin/workflows/` rule text (beyond the venv-path updates in S2-S5 — no other edits)
- `documents/project-vision-Rev5.md` (locked — no edits)
- `documents/project-vision-Rev1.md` through `Rev4.md` (archived — do not touch)
- `documents/SovereignAI_Architecture_Decisions.md` (archived — DECISIONS.md at root is the live ADR)
- `documents/plan-1-4-scope-*.md` (archived — Plan 1–4 scope split is locked)
- `documents/round-table-vision-Rev*-brief.md` (archived — vision review is complete)
- `documents/handoff-prompt.md` (archived — AGENTS.md Rev2 fixes are locked)
- `documents/AGENTS-roundtable-brief.md` (archived)
- `prompts/plan-0.md` (kept as-is — see S7.2 observation about naming inconsistency; user decision pending)
- `prompts/plan-0.1-Rev1.md` (kept as-is — Rev files preserved per handoff line 96)
- `prompts/plan-0.2-Rev1.md` (kept as-is — Rev files preserved per handoff line 96)
- `README.md`, `.gitignore` (no changes — content is stable from prompt-0)
- `txt/requirements.txt`, `txt/vulture-whitelist.txt`, `txt/.secrets.baseline` (no changes — infrastructure is stable)
- `pyproject.toml` (no changes — ruff config already fixed in prompt-0.2)
- `.pre-commit-config.yaml` (no changes — bandit exclusions already set in prompt-0.1)
- All `.gitkeep` files (no changes — directories are stable)
- `DECISIONS.md`, `DEBT.md` (no new decisions or deferred items this plan)

---

*Plan 0.3 — Prompt-0.3 Cleanup. Rev1. Architect draft. Skips Round Table review per AI_HANDOFF.md scan-prompt exemption (mechanical cleanup, no architectural decisions).*
