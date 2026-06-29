# Plan 10.2 — Governance Patch: Rule Gap Fixes + Premature Tag Cleanup

**Special plan**: Governance/cleanup patch (prompt-0.1 through prompt-10.1 pattern). Adds 7 new OR rules + 4 new landmines identified by scanning all 16 execution logs (prompts 0–10.1). Removes a premature `prompt-11` tag. No new features. No new architecture. Skips Round Table (mechanical governance + rules from log-scan diagnosis).

Depends on: prompt-10.1
Vision principles: none (mechanical governance — no architectural impact)
Open questions resolved: none

---

## S0 — Opening

**S0.1** — Run `/open` workflow from `.devin/workflows/open.md`. Verify `prompt-10.1` tag exists on origin (`6db588d`). Confirm clean working copy on `main`. Activate venv (OR45).

**S0.2** — Read `AGENTS.md` in full. Note OR71 (verbatim commands), OR75 (`git add -A` for all commits — OR80 below broadens this), OR80 (added this plan).

**S0.3** — Add 7 new rules. These address failure patterns found by scanning all 16 execution logs (see `rule-gap-analysis.md` for full evidence).

- **OR76.** Create `git tag prompt-{N}` only after the final code commit is made and verified. Never create a tag pointing at a placeholder or intermediate commit. If a tag was created prematurely, `git tag -d prompt-{N}` locally, complete the work, then create the tag at the final commit. Never `git push origin prompt-{N} --force` to move a tag — if a tag was pushed prematurely, STOP and report to the User; the User decides whether to force-push or accept the stale tag. Source: L36.

- **OR77.** Coverage is measured at every `/close` for plans that touch Python source files. Run `python -m pytest tests/ --cov=. --cov-report=term-missing` as part of Step 1 (or as a new Step 1.5 — see S3 below). If coverage dropped >5% from the PLANS.md baseline, STOP. If coverage is "N/A" for a plan that edited `.py` files, STOP. Docs-only plans (no `.py` edits) may report "N/A" with a one-line reason. Update PLANS.md coverage baseline at every `/close` where coverage was measured. Source: L37.

- **OR78.** Update the Bandit baseline in PLANS.md at every `/close` where tests were added or removed. The B101 (assert_used) count grows with test count — this is expected. Record the actual count, not a stale number. If the count changed by >20% from the PLANS.md baseline without a corresponding test count change, STOP and investigate (may indicate a new non-test Low finding). Source: L38.

- **OR79.** If a plan session is interrupted by quota exhaustion, model timeout, or session reset, the Executor MUST re-read the plan file (`prompts/plan-{N}.md`) and `AGENTS.md` in full before continuing. The Executor must also review the TODO list and verify the last completed step. Do not resume from a cached mental model — context may have been lost. If the interrupt happened mid-`/close`, re-read `.devin/workflows/close.md` fresh (per OR71) and verify which step was last completed before resuming. Source: L39.

- **OR80.** `git add -A` is mandatory for EVERY commit, not just `/close` steps 15 and 18. This includes governance patches made during the plan body (S0.3 rule commits, mid-plan fixes, workflow patches, L32-L33 landmine additions). After `git add -A`, run `git status -s` to verify the staging area is clean. Never use `git add <file1> <file2> ...` — explicit lists miss auto-fixes, deletions, and untracked files. OR75 applies to all commits, not just close-workflow commits. Source: OR75 (clarified and broadened).

- **OR81.** The `.secrets.baseline` file is never edited manually. To remove a false positive, run `detect-secrets audit txt/.secrets.baseline` (interactive tool) — never open the JSON in an editor. Manual edits break the baseline's signature and cause false "new secrets detected" results. If `detect-secrets audit` is unavailable or fails, STOP and report — do not fall back to manual editing. Source: L26 (promoted to rule).

- **OR82.** Never use `git mv` — it errors unreliably in Git Bash on Windows. Use plain `mv` to move files, then `git add -A` (per OR75/OR80) to stage both the new paths and the deletions of the old paths. Verify with `git ls-files '<old-path-glob>'` that git no longer tracks the old paths. Source: L34 (clarified).

Commit: `docs: add OR76-OR82 for prompt-10.2`

---

## S1 — Remove Premature `prompt-11` Tag

**Critical cleanup.** The `prompt-11` tag currently points to commit `6fa8d73` ("Remove outdated document files from documents directory") — a commit that has nothing to do with Plan 11. The tag was created prematurely (before Plan 11 even started) and is now behind `prompt-10.1`. Plan 11 has NOT been started by the Executor (only `prompts/plan-11-Rev3.md` exists; no `prompts/plan-11.md`).

Per OR76, this tag must be removed. When the Executor actually starts Plan 11, it will create a new `prompt-11` tag at the correct final commit.

### S1.1 — Delete the tag locally and on origin

```bash
# Verify the tag points to the wrong commit
git rev-parse prompt-11
# Expected: 6fa8d73... (the "Remove outdated document files" commit — NOT a Plan 11 commit)

# Delete locally
git tag -d prompt-11

# Delete on origin
git push origin :refs/tags/prompt-11
```

### S1.2 — Verify deletion

```bash
git tag --list prompt-11
# Expected: empty
git ls-remote --tags origin | grep "prompt-11"
# Expected: empty
```

If either command returns output, STOP — the tag was not fully deleted. Report to User.

### S1.3 — Commit the tag deletion (no file changes, but record in execution log)

The tag deletion is a remote operation, not a file change. No commit needed. Record in the execution log: "Removed premature prompt-11 tag (pointed to 6fa8d73, a pre-10.1 commit). Will be re-created when Plan 11 actually completes."

---

## S2 — Add L36–L39 to LANDMINES.md

**File**: `LANDMINES.md`

Append after L35:
```markdown
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
```

**Commit** (per OR80 — use `git add -A`):
```bash
git add -A
git status -s  # Verify only LANDMINES.md is staged
git commit -m "docs: add L36-L39 to LANDMINES.md (prompt-10.2)"
```

---

## S3 — Update close.md: Coverage Step + Tag Hardening

**File**: `.devin/workflows/close.md`

### S3.1 — Add coverage to Step 1 (per OR77)

**Old** (Step 1):
```markdown
**Step 1 — Tests**
```
.venv/Scripts/python.exe -m pytest tests/ -vvv
```
STOP on any failure. STOP if "no tests ran" and the plan was supposed to add tests (silent collection failure).
```

**New**:
```markdown
**Step 1 — Tests (with coverage)**
```
.venv/Scripts/python.exe -m pytest tests/ -vvv --cov=. --cov-report=term-missing
```
STOP on any failure. STOP if "no tests ran" and the plan was supposed to add tests (silent collection failure).

**Coverage check (per OR77)**: Record the coverage %. Compare against PLANS.md baseline. If coverage dropped >5% from baseline, STOP. If this plan edited `.py` files and coverage is "N/A" or unavailable, STOP. Update PLANS.md coverage baseline in Step 10. Docs-only plans (no `.py` edits) may report "N/A" with a one-line reason.
```

### S3.2 — Harden Step 16 (Tag) per OR76

**Old** (Step 16):
```markdown
**Step 16 — Tag**
```
git tag prompt-{N}
git tag --list prompt-{N}
```
STOP if tag not listed.
```

**New**:
```markdown
**Step 16 — Tag (per OR76 — only after final commit is verified)**
```
# Verify the tag does not already exist (prevents premature-tag force-push)
git tag --list prompt-{N}
# If the above returns output, STOP — tag already exists. Report to User. Do NOT delete and recreate.
# If empty, create the tag at the current (final) commit:
git tag prompt-{N}
git tag --list prompt-{N}
```
STOP if tag not listed. STOP if tag already existed before this step (premature tag — report to User, do not force-push).
```

### S3.3 — Update Step 8 (Bandit) to reference OR78

**Old** (Step 4 — Bandit, last line):
```
STOP on findings.
```

**New**:
```
STOP on findings. Update the Bandit Low (B101) count in PLANS.md at Step 10 (per OR78). If the count changed >20% without a corresponding test count change, STOP and investigate.
```

**Commit** (per OR80):
```bash
git add -A
git status -s
git commit -m "docs: close.md adds coverage step (OR77), tag hardening (OR76), bandit reconciliation (OR78) — prompt-10.2"
```

---

## S4 — Update PLANS.md Baselines

**File**: `PLANS.md`

### S4.1 — Update Static Analysis Baseline to reflect current state

After S5 (verification) runs, update:
- **Bandit**: 332 Low (B101) — already current from prompt-10
- **Coverage**: 93% — already current from prompt-10.1
- Add a note: "Bandit count reconciled at every /close per OR78. Coverage measured at every /close per OR77."

### S4.2 — Add Baseline Reconciliation Note

```
**Plan 10.2**: Baseline → 169 tests. Delta: 0 — governance patch, no test changes.
```

**Commit** (per OR80):
```bash
git add -A
git status -s
git commit -m "docs: update PLANS.md baselines for prompt-10.2"
```

---

## S5 — Run Full Verification

Per `/close` steps 1–8 (re-read close.md fresh per OR71). Run each tool separately. **Per OR80, use `git add -A` for all commits in this plan — no explicit file lists.**

### S5.1 — Tests with coverage (per new OR77 / Step 1)
```bash
.venv/Scripts/python.exe -m pytest tests/ -vvv --cov=. --cov-report=term-missing
```
Expected: 169 passed, 3 skipped, coverage ≥93%. If coverage <88% (5% drop from 93% baseline), STOP.

### S5.2 — Ruff
```bash
.venv/Scripts/ruff.exe check . 2>&1 | tail -n 3
```
Expected: 0 errors.

### S5.3 — Mypy (full repo)
```bash
.venv/Scripts/mypy.exe . --ignore-missing-imports 2>&1 | tail -n 5
```
Expected: 0 errors.

### S5.4 — Bandit
```bash
.venv/Scripts/bandit.exe -r . -ll --exclude .venv,venv,env,.git,node_modules,__pycache__,build,dist,.tox,.eggs,.pytest_cache 2>&1 | tail -n 5
```
Expected: 332 Low (B101) — unchanged from prompt-10 (no tests added this plan). If count changed >20% without test count change, STOP (per OR78).

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

### S5.7 — detect-secrets (per OR81 — never manually edit baseline)
```bash
.venv/Scripts/detect-secrets.exe scan --baseline txt/.secrets.baseline
```
Expected: exit 0. If exit != 0, run `detect-secrets audit txt/.secrets.baseline` — do NOT edit the JSON manually.

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

### S5.9 — Verify premature prompt-11 tag is gone
```bash
git tag --list prompt-11
# Expected: empty
git ls-remote --tags origin | grep "prompt-11"
# Expected: empty
```
If either returns output, STOP — the premature tag was not removed.

---

## STOP Conditions

- If `git tag --list prompt-11` returns output after S1 (tag not deleted), STOP.
- If `git ls-remote --tags origin | grep prompt-11` returns output after S1 (tag not deleted on origin), STOP.
- If any test/static analysis tool in S5 fails, STOP.
- If coverage <88% (5% drop from 93% baseline), STOP (per OR77).
- If Bandit Low count changed >20% from 332 without test count change, STOP (per OR78).
- If `git status -s` after any `git add -A` shows unstaged changes, STOP (per OR80).
- If `git tag --list prompt-{N}` returns output BEFORE Step 16 (premature tag exists), STOP (per OR76).

---

## Files WILL Edit

- `AGENTS.md` (S0.3 — add OR76–OR82)
- `LANDMINES.md` (S2 — add L36–L39)
- `.devin/workflows/close.md` (S3 — coverage step, tag hardening, bandit reconciliation)
- `PLANS.md` (S4 — baseline notes, reconciliation entry)

## Files WILL NOT Edit

- Any source file in `sovereignai/`
- Any test file
- Any AR check script
- `txt/.secrets.baseline` (per OR81 — never manually edit)
- `txt/requirements.txt`
- `project-vision-Rev5.md`

---

## Closing

Run `/close`. Tag: `prompt-10.2`.

**Critical per OR76**: Before creating `git tag prompt-10.2`, verify `git tag --list prompt-10.2` returns empty. If it returns output, STOP — do not delete and recreate. Report to User.

**Critical per OR80**: Every `git commit` in this plan (S0.3, S2, S3, S4, and `/close` steps 15/18) MUST use `git add -A` + `git status -s` verification. No explicit `git add <file>` lists.

**Critical per OR71**: Re-read `.devin/workflows/close.md` in full before running `/close`. The file was edited in S3 of this plan — do not use a cached version.

After `prompt-10.2` completes, the repo is clean and fully governed. Plan 11 can start — the Executor copies `prompts/plan-11-Rev3.md` to `prompts/plan-11.md` and begins. The premature `prompt-11` tag is gone; a new one will be created at the correct commit when Plan 11 completes.

---

## Adjudication Summary

This patch addresses:
1. **Premature tag cleanup**: `prompt-11` tag pointing to `6fa8d73` removed (S1)
2. **7 new rules**: OR76 (no premature tags), OR77 (coverage mandatory), OR78 (bandit reconciliation), OR79 (quota-exhaustion re-read), OR80 (`git add -A` for all commits), OR81 (detect-secrets audit only), OR82 (never `git mv`)
3. **4 new landmines**: L36 (premature tag), L37 (coverage skipped), L38 (bandit drift), L39 (quota context loss)
4. **close.md hardening**: coverage step (OR77), tag existence check (OR76), bandit reconciliation note (OR78)

Not addressed (out of scope — deferred):
- Coverage gap analysis (which files/paths are uncovered) — deferred to Plan 13 (test framework)
- Full PII filter (deferred to DEBT.md — Plan 14)
- Cross-process GPU lock (deferred to DEBT.md — Plan 14)
