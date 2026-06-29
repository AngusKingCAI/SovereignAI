# Plan 15 — Scan 15 (Third Whole-Repo Scan)

**Special plan**: Scan prompt — mechanical verification of the full Plans 11–14 batch. No new features. No new architecture. Fixes only. Skips Round Table (per User veto for this section — UI/functional iteration phase).

Depends on: prompt-14
Vision principles: none (mechanical scan — no architectural impact)
Open questions resolved: none

---

## S0 — Opening

**S0.1** — Run `/open`. Verify `prompt-14` tag exists on origin. Confirm clean working copy on `main`. Activate venv (OR45).

**S0.2** — Read `AGENTS.md` in full. Note OR71 (verbatim commands), OR75/OR80/OR83 (`git add -A`), OR76 (no premature tags), OR77 (coverage mandatory, floor 89%), OR78 (bandit reconciliation), OR82 (never `git mv`).

**S0.3** — Add one new rule:
- **OR86 — Backend + UI in the same plan.** Any plan that adds a backend capability (new component, new memory backend, new adapter, new worker, new skill) MUST also add the corresponding `/api/` endpoint in `web/main.py` and update the relevant panel in `web/templates/index.html` + `web/static/app.js`. A backend capability without a UI surface is incomplete. Exception: plans that explicitly defer UI to a named future plan (documented in the plan's Closing section). Source: UI structure questionnaire (prompt-15).

Commit: `docs: add OR86 for prompt-15`

---

## S1 — Fix close.md Step 17 (git rm → git add -A)

**File**: `.devin/workflows/close.md`

Apply the fix from `close-md-step17-fix-L40.md` (available in `/home/z/my-project/download/`).

**Find** the verification block in Step 17:
```bash
# Also verify git no longer tracks the old paths (per L34 — catches mv+add-not-rm bug)
tracked_old=$(git ls-files 'prompts/plan-{N}-Rev*.md' | wc -l)
if [ "$tracked_old" -gt 0 ]; then
  echo "STOP: git still tracks $tracked_old plan-{N}-Rev*.md files in prompts/ — run 'git rm' to stage deletions"
  git ls-files 'prompts/plan-{N}-Rev*.md'
  STOP
fi
```

**Replace with**:
```bash
# Also verify git no longer tracks the old paths (per L34 — catches mv+add-not-rm bug)
# Per L40 fix: do NOT use 'git rm' — it DELETES files. Use 'git add -A' to stage the renames.
tracked_old=$(git ls-files 'prompts/plan-{N}-Rev*.md' | wc -l)
if [ "$tracked_old" -gt 0 ]; then
  echo "git still tracks $tracked_old plan-{N}-Rev*.md files in prompts/ — running 'git add -A' to stage the moves"
  git add -A
  tracked_old=$(git ls-files 'prompts/plan-{N}-Rev*.md' | wc -l)
  if [ "$tracked_old" -gt 0 ]; then
    echo "STOP: git STILL tracks $tracked_old plan-{N}-Rev*.md files in prompts/ after git add -A — manual investigation needed"
    git ls-files 'prompts/plan-{N}-Rev*.md'
    STOP
  fi
fi
```

---

## S2 — Add L40 to LANDMINES.md

Append after L39:
```markdown
## L40 — close.md Step 17 verification check said "run git rm" which DELETES files instead of moving them
**Trigger**: Prompt-13 close — Executor ran `git rm prompts/plan-13-Rev*.md` because the verification check message literally said "run 'git rm' to stage deletions". This deleted Rev1-Rev9 from git instead of moving them to `prompts/completed/`.
**Impact**: 9 plan revision files permanently deleted from git history; User had to restore manually.
**Graduated to**: close.md Step 17 fixed (verification now runs `git add -A` automatically instead of telling Executor to run `git rm`).
```

Update "Capturing new landmines" footer from `L40+` to `L41+`.

---

## S3 — Run All Scan Tools

Per `/scan` workflow step 1. Run each tool separately (OR3). Re-read `close.md` fresh (OR71).

### S3.1 — Tests with coverage
```bash
.venv/Scripts/python.exe -m pytest tests/ -vvv --cov=. --cov-report=term-missing
```
Expected: 320 tests, 9 skipped, coverage ≥89%. If coverage <89%, STOP (per OR77).

### S3.2 — Ruff
```bash
.venv/Scripts/ruff.exe check . 2>&1 | tail -n 3
```

### S3.3 — Mypy (full repo)
```bash
.venv/Scripts/mypy.exe . --ignore-missing-imports 2>&1 | tail -n 5
```

### S3.4 — Bandit
```bash
.venv/Scripts/bandit.exe -r . -ll --exclude .venv,venv,env,.git,node_modules,__pycache__,build,dist,.tox,.eggs,.pytest_cache 2>&1 | tail -n 5
```
Expected: ~636 Low (B101), 2 Medium (B615 — HuggingFace, `#nosec` added). Update PLANS.md baseline per OR78.

### S3.5 — pip-audit
```bash
.venv/Scripts/pip-audit.exe --strict --requirement txt/requirements.txt 2>&1 | tail -n 5
```

### S3.6 — Vulture
```bash
.venv/Scripts/vulture.exe . --min-confidence 80 --exclude .venv,venv,env,.git,node_modules,__pycache__,build,dist,.tox,.eggs,.pytest_cache,.mypy_cache,.ruff_cache,htmlcov 2>&1 | tail -n 5
```

### S3.7 — detect-secrets
```bash
.venv/Scripts/detect-secrets.exe scan --baseline txt/.secrets.baseline
```

### S3.8 — Custom AR checks
```bash
.venv/Scripts/python.exe scripts/ar_checks/no_globals.py sovereignai/
.venv/Scripts/python.exe scripts/ar_checks/constructor_arg_cap.py sovereignai/ --max-args 15
.venv/Scripts/python.exe scripts/ar_checks/no_context_bags.py sovereignai/
.venv/Scripts/python.exe scripts/ar_checks/docstring_discipline.py sovereignai/
.venv/Scripts/python.exe scripts/ar_checks/no_hardcoded_component_names.py web/ cli/ tui/ phone/
.venv/Scripts/python.exe scripts/ar_checks/ui_does_not_touch_core.py
```

---

## S4 — Governance Scans

### S4.1 — Verify no git rm instruction remains in close.md
```bash
grep -c "git rm" .devin/workflows/close.md
# Expected: 0
```

### S4.2 — Verify all plan-13/14 Rev files are in completed/
```bash
for p in 11 12 13 14; do
  echo "plan-$p:"
  echo "  in prompts/: $(git ls-files "prompts/plan-$p-Rev*.md" | wc -l)"
  echo "  in completed/: $(git ls-files "prompts/completed/plan-$p-Rev*.md" | wc -l)"
done
```
Expected: 0 in prompts/, all in completed/.

### S4.3 — Update PLANS.md
- Update Test Baseline (320 tests)
- Update Coverage (91%)
- Update Bandit baseline (636 Low, 2 Medium)
- Update "Last updated" to prompt-15
- Set Active Plan: None — awaiting UI/functional batch
- Populate next-5-queue:
  | Slot | Plan | Description | Depends on | Status |
  |---|---|---|---|---|
  | 1 | Plan 16 | Logging & observability — fix Log Drawer, add Orchestrator "thinking", verify trace persistence | Scan 15 | ⏳ Pending |
  | 2 | Plan 17 | Memory panel API + UI wiring | Plan 16 | ⏳ Pending |
  | 3 | Plan 18 | Tasks panel — active/scheduled/completed tabs + task detail + manual task creation | Plan 17 | ⏳ Pending |
  | 4 | Plan 19 | Tools panel — list + run tools with input schema forms | Plan 18 | ⏳ Pending |
  | 5 | Scan 20 | Fourth whole-repo scan | Plan 19 | ⏳ Pending |

### S4.4 — Scan CHANGELOG.md
Verify prompts 11, 12, 13, 14 all have entries.

### S4.5 — Vision principle audit
For each of the 14 principles, verify codebase complies. If any violated, STOP.

### S4.6 — DEBT.md review
Check trigger conditions for deferred items. Flag any whose triggers are met.

---

## S5 — Run `/close`

Per OR71, re-read `close.md` fresh. Per OR83, use `git add -A` for all commits. Per OR76, verify tag doesn't exist before creating.

**Critical**: This is the first close using the FIXED Step 17 (no `git rm`). Verify that plan-15 Rev files are moved to `completed/` correctly — no deletions.

---

## STOP Conditions

- If coverage <89%, STOP (per OR77).
- If `grep -c "git rm" .devin/workflows/close.md` returns >0 after S1, STOP.
- If any scan tool fails, STOP.
- If any vision principle violated, STOP.

---

## Files WILL Edit

- `.devin/workflows/close.md` (S1 — fix Step 17 verification)
- `LANDMINES.md` (S2 — add L40)
- `AGENTS.md` (S0.3 — add OR86)
- `PLANS.md` (S4.3 — update baselines, queue)
- `CHANGELOG.md` (S4.4 — add prompt-15 entry)

## Files WILL NOT Edit

- Any source file in `sovereignai/`
- Any test file
- `txt/requirements.txt`
- `project-vision-Rev5.md`

---

## Closing

Run `/close`. Tag: `prompt-15`.

After Scan 15 completes, the next batch is UI/functional:
- **Plan 16**: Logging & observability (Log Drawer fix → Orchestrator "thinking" → trace persistence → REST trace API)
- **Plan 17**: Memory panel API + UI
- **Plan 18**: Tasks panel (3 tabs + detail + manual creation)
- **Plan 19**: Tools panel (list + run)

Round Table is vetoed for this batch. GLM drafts initial prompts, then Devin iterates directly and reports back when working or stuck.
