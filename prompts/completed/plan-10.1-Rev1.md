# Plan 10.1 — Post-Scan-10 Cleanup Patch

**Special plan**: Governance/cleanup patch (prompt-0.1 through prompt-0.4 pattern). Fixes open defects from prompt-10 close that must be resolved before starting Plan 11. No new features. No new architecture. Skips Round Table review (mechanical fixes + one rule from prior diagnosis).

Depends on: prompt-10
Vision principles: none (mechanical cleanup — no architectural impact)
Open questions resolved: none

---

## S0 — Opening

**S0.1** — Run `/open` workflow from `.devin/workflows/open.md`. Verify `prompt-10` tag exists on origin (`ddd050b`). Confirm clean working copy on `main`. Activate venv (OR45).

**S0.2** — Read `AGENTS.md` in full. Note OR71 (run workflow commands verbatim — applies to this patch too), OR74 (workflow files are Architect-authored — this patch's close.md edits are Architect-directed via this plan).

**S0.3** — Add one new rule:
- **OR75 — Stage all changes with `git add -A`; verify with `git status` before every commit.** Before every `git commit` in `/close` (steps 15 and 18), run `git status -s` to see ALL modified/deleted/new files, then `git add -A` to stage them all (including auto-fixes from ruff `--fix`/detect-secrets AND deletions from `mv` operations). Do not use explicit `git add <file1> <file2> ...` lists — they miss auto-fixed files and `mv` deletions. After `git add -A`, run `git status -s` again to verify the staging area is clean (all changes staged, no unstaged lines). If any unstaged changes remain, STOP. Source: L34, L35.

Commit: `docs: add OR75 for prompt-10.1`

---

## S1 — Fix Open Defect: Remove Duplicate Plan-9 Files

**This is the critical carryover from prompt-9 that Scan 10 S1 failed to fully fix.** The `b00ee51` commit staged the new copies in `prompts/completed/` but never staged the deletions from `prompts/`. Git still tracks both copies. Per OR71, run verbatim:

```bash
git rm prompts/plan-9-Rev1.md prompts/plan-9-Rev2.md prompts/plan-9-Rev3.md prompts/plan-9-Rev4.md
```

**Verify** (per OR75 — the new rule):
```bash
git status -s
# Expected: 4 lines showing "D  prompts/plan-9-Rev1.md" etc. (staged deletions)
git ls-files 'prompts/plan-9-Rev*.md'
# Expected: EMPTY — no files tracked in prompts/ anymore
git ls-files 'prompts/completed/plan-9-Rev*.md'
# Expected: 5 files (Rev1, Rev2, Rev3, Rev4, Rev5)
```

If `git ls-files 'prompts/plan-9-Rev*.md'` returns any files after the `git rm`, STOP — the deletion didn't stage. Report to User.

**Commit** (per OR75 — use `git add -A`, not explicit paths):
```bash
git add -A
git status -s  # Verify only the 4 deletions are staged
git commit -m "fix: remove duplicate plan-9 Rev1-4 from prompts/ (b00ee51 staged new copies but not deletions)"
```

---

## S2 — Fix PLANS.md Staleness

**File**: `PLANS.md`

### S2.1 — Fix test baseline label

**Old** (line 27):
```
**Current**: 169 tests (Plan 9 `/close`)
```
**New**:
```
**Current**: 169 tests (Plan 10 `/close`)
```

### S2.2 — Update coverage baseline

The prompt-10 log reports "Coverage: 93%". The PLANS.md baseline still says "96% | Plan 5". Update to reflect the current measured state.

**Old** (line 53):
```
| **Coverage** | 96% | Plan 5 | 568 statements, 22 missed. Gaps: main.py (smoke), capability_api.py (error paths), lifecycle_manager.py (error paths), manifest_parser.py (error path), types.py (unused error classes) |
```
**New**:
```
| **Coverage** | 93% | Plan 10 | Dropped from 96% (Plan 5) as codebase grew through Plans 6–10 without proportional test additions. Gaps to address in Plans 11–14: memory backends, versioning, conformance framework, Education department. Target: 90% floor (Plan 13 STOP condition). |
```

### S2.3 — Add Baseline Reconciliation Note

Add to the Baseline Reconciliation Notes section:
```
**Plan 10**: Baseline → 169 tests. Delta: 0 — see CHANGELOG prompt-10.
```
(Test count unchanged from Plan 9 — Scan 10 is mechanical, adds no tests.)

**Commit**:
```bash
git add -A
git status -s  # Verify only PLANS.md is staged
git commit -m "docs: fix PLANS.md staleness — test baseline label, coverage baseline (prompt-10.1)"
```

---

## S3 — Add L34 and L35 to LANDMINES.md

**File**: `LANDMINES.md`

Append after L33:
```markdown
## L34 — `mv` + `git add <new>` leaves old path tracked in git
**Trigger**: Prompt-9 close Step 17 and prompt-10 S1 — `mv prompts/plan-{N}-Rev*.md prompts/completed/` followed by `git add prompts/completed/`. The `git add` staged the new files but not the deletions. Git tracked both copies; `git ls-files` showed files in both locations.
**Impact**: Duplicate plan files in repo across 1+ prompt cycles; User had to manually `git rm`; archive appeared successful but wasn't.
**Graduated to**: OR75.

## L35 — ruff --fix / detect-secrets auto-modified files missed by explicit `git add` lists
**Trigger**: Prompt-10 Step 15 — `ruff check . --fix` modified `tests/test_e2e_task_submission.py`, `tests/test_web_ui_panels.py`; `detect-secrets scan` updated `txt/.secrets.baseline`. `git add <explicit 25-file list>` missed all 3. Committed `ddd050b` without them; User caught it; required `7e2eeb8` fix commit.
**Impact**: 3 files left uncommitted after "successful" close; User frustration; required follow-up commit.
**Graduated to**: OR75.
```

**Commit**:
```bash
git add -A
git status -s
git commit -m "docs: add L34-L35 to LANDMINES.md (prompt-10.1)"
```

---

## S4 — Fix close.md: `git add -A` + `git ls-files` Verification

**File**: `.devin/workflows/close.md`

### S4.1 — Step 15: change explicit `git add` to `git add -A` + verification

**Old** (line 142–144):
```markdown
git add <files-changed-this-plan>
git commit -m "{plan title} (prompt-{N})" -m "{multi-line description}"
```
**New**:
```markdown
# Per OR75: stage ALL changes (catches auto-fixes, deletions, new files)
git add -A
# Verify staging area is clean — no unstaged changes remain
git status -s
# If any lines appear above, STOP — unstaged changes exist
git commit -m "{plan title} (prompt-{N})" -m "{multi-line description}"
```

### S4.2 — Step 18: change explicit `git add` to `git add -A`

**Old** (line 175):
```markdown
git add CHANGELOG.md PLANS.md LANDMINES.md DEBT.md prompts/completed/
```
**New**:
```markdown
# Per OR75: stage ALL changes (catches governance docs + archived plan deletions + any auto-fixes)
git add -A
git status -s  # Verify staging area is clean
```

### S4.3 — Step 17: strengthen verification to check git index, not just filesystem

The current Step 17 verification (added in Scan 10 S2.1) checks `ls prompts/plan-{N}-Rev*.md` (filesystem). But after `mv`, the filesystem shows 0 files even though git still tracks the old paths. Add a `git ls-files` check.

**Add** after the existing `remaining=$(ls ...)` verification block:
```markdown
# Also verify git no longer tracks the old paths (per L34 — catches mv+add-not-rm bug)
tracked_old=$(git ls-files 'prompts/plan-{N}-Rev*.md' | wc -l)
if [ "$tracked_old" -gt 0 ]; then
  echo "STOP: git still tracks $tracked_old plan-{N}-Rev*.md files in prompts/ — run 'git rm' to stage deletions"
  git ls-files 'prompts/plan-{N}-Rev*.md'
  STOP
fi
```

**Commit**:
```bash
git add -A
git status -s
git commit -m "docs: close.md uses git add -A + git ls-files verification (OR75, L34) — prompt-10.1"
```

---

## S5 — Run Full Verification

Per `/close` steps 1–8 (re-read close.md fresh per OR71). Run each tool separately:

### S5.1 — Tests
```bash
.venv/Scripts/python.exe -m pytest tests/ -vvv
```
Expected: 169 passed, 3 skipped. If any test fails, STOP.

### S5.2 — Ruff
```bash
.venv/Scripts/ruff.exe check . 2>&1 | tail -n 3
```
Expected: 0 errors. If errors, STOP.

### S5.3 — Mypy (full repo — patch prompt, but small scope)
```bash
.venv/Scripts/mypy.exe . --ignore-missing-imports 2>&1 | tail -n 3
```
Expected: 0 errors.

### S5.4 — Bandit
```bash
.venv/Scripts/bandit.exe -r . -ll --exclude .venv,venv,env,.git,node_modules,__pycache__,build,dist,.tox,.eggs,.pytest_cache 2>&1 | tail -n 5
```
Expected: 0 findings above Low. Low (B101) expected — count per OR4.

### S5.5 — pip-audit
```bash
.venv/Scripts/pip-audit.exe --strict --requirement txt/requirements.txt 2>&1 | tail -n 5
```
Expected: 0 CVEs.

### S5.6 — Vulture
```bash
.venv/Scripts/vulture.exe . --min-confidence 80 --exclude .venv,venv,env,.git,node_modules,__pycache__,build,dist,.tox,.eggs,.pytest_cache,.mypy_cache,.ruff_cache,htmlcov 2>&1 | tail -n 5
```
Expected: 0 new findings.

### S5.7 — detect-secrets
```bash
.venv/Scripts/detect-secrets.exe scan --baseline txt/.secrets.baseline
```
Expected: exit 0.

### S5.8 — Custom AR checks
```bash
.venv/Scripts/python.exe scripts/ar_checks/no_globals.py sovereignai/
.venv/Scripts/python.exe scripts/ar_checks/constructor_arg_cap.py sovereignai/ --max-args 15
.venv/Scripts/python.exe scripts/ar_checks/no_context_bags.py sovereignai/
.venv/Scripts/python.exe scripts/ar_checks/docstring_discipline.py sovereignai/
.venv/Scripts/python.exe scripts/ar_checks/no_hardcoded_component_names.py web/ cli/ tui/ phone/
.venv/Scripts/python.exe scripts/ar_checks/ui_does_not_touch_core.py
```
All must pass. Per OR72 — do NOT edit these scripts to make failures pass.

### S5.9 — Final verification: no duplicates anywhere

```bash
# Verify no plan file exists in both prompts/ and prompts/completed/
for p in 0 0.1 0.2 0.3 0.4 1 2 3 4 5 6 7 8 9 10; do
  for r in Rev1 Rev2 Rev3 Rev4 Rev5 Rev6 Rev7 Rev8; do
    if git ls-files --error-unmatch "prompts/plan-$p-$r.md" 2>/dev/null >/dev/null && git ls-files --error-unmatch "prompts/completed/plan-$p-$r.md" 2>/dev/null >/dev/null; then
      echo "DUPLICATE STILL EXISTS: plan-$p-$r"
    fi
  done
done
# Expected: no output
```

If any duplicates remain, STOP.

---

## STOP Conditions

- If `git rm` in S1 fails or `git ls-files` still shows plan-9 Rev1-4 in `prompts/` after, STOP.
- If any test/static analysis tool in S5 fails, STOP.
- If S5.9 finds any duplicate plan files, STOP.
- If `git status -s` after any `git add -A` shows unstaged changes, STOP (OR75 violation).

---

## Files WILL Edit

- `AGENTS.md` (S0.3 — add OR75)
- `LANDMINES.md` (S3 — add L34, L35)
- `.devin/workflows/close.md` (S4 — Steps 15, 17, 18 use `git add -A` + `git ls-files` verification)
- `PLANS.md` (S2 — fix test baseline label, coverage baseline, add reconciliation note)

## Files WILL NOT Edit

- Any source file in `sovereignai/`
- Any test file
- Any AR check script
- `txt/requirements.txt`
- `project-vision-Rev5.md`

---

## Closing

Run `/close`. Tag: `prompt-10.1`. Update CHANGELOG, PLANS.md.

**Critical per OR75**: every `git commit` in this plan's `/close` MUST use `git add -A` + `git status` verification — including the close workflow's own Step 15 and Step 18. Do NOT use explicit `git add <files>` lists.

**Critical per OR71**: re-read `.devin/workflows/close.md` in full before running `/close`. The file was edited in S4 of this plan — do not use a cached version.

After `prompt-10.1` completes, the repo is clean and the Plans 11–14 Rev3 batch can start. The Rev3 files are in `prompts/plan-{11,12,13,14}-Rev3.md` — copy each to `prompts/plan-{N}.md` (drop Rev suffix) when the Executor starts each plan.

---

## Adjudication Summary

This patch addresses:
1. **Critical open defect**: plan-9 Rev1-4 duplicated in `prompts/` and `prompts/completed/` (S1)
2. **Root cause fix**: OR75 (`git add -A` + `git status`) prevents both the duplicate-tracking bug (L34) and the missed-auto-fix bug (L35) (S0.3, S4)
3. **PLANS.md staleness**: test baseline label, coverage baseline (S2)
4. **close.md hardening**: Steps 15/18 use `git add -A`; Step 17 verification checks `git ls-files` not just `ls` (S4)

Not addressed (out of scope — deferred):
- Premature `prompt-10` tag at `3c70b34` (cosmetic; tag was correctly moved to `ddd050b` via force-push; no action needed)
- Coverage drop to 93% (will be addressed by Plans 11–14 adding tests for memory/versioning/conformance/education)
