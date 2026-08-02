# Plan 10.3 — Governance Condensation + Numbering Policy

**Special plan**: Governance patch. Applies the 3 accepted condensation merges from Claude's review + establishes a numbering policy that handles gaps without breaking 53 plan files + 17 logs that cite existing numbers. No new features. No new architecture. Skips Round Table (mechanical governance).

Depends on: prompt-10.2
Vision principles: none (mechanical governance — no architectural impact)
Open questions resolved: none

---

## S0 — Opening

**S0.1** — Run `/open` workflow from `.devin/workflows/open.md`. Verify `prompt-10.2` tag exists on origin (`6e7edc9`). Confirm clean working copy on `main`. Activate venv (OR45).

**S0.2** — Read `AGENTS.md` in full. Note OR71 (verbatim commands), OR75/OR80 (`git add -A` for all commits).

**S0.3** — Add 2 new rules + 1 new landmine. These address the OR80 violations observed in prompt-10.2 (8 explicit `git add` lines despite the rule) and establish the numbering policy.

- **OR83.** `git add -A` is the ONLY allowed staging command. Never use `git add <filename>`, `git add <file1> <file2>`, or `git add <directory>/` — these are OR80/OR75 violations even when the Executor thinks it knows which files changed. The only exception: `git add -A` after a `git rm` (the `git rm` already staged the deletion; `git add -A` stages any remaining changes). After every `git add -A`, run `git status -s` to verify the staging area is clean (no unstaged lines). Source: OR80 (clarified — prompt-10.2 had 8 violations).

- **OR84.** Rule and landmine numbers are NEVER renumbered. Existing numbers (AR1–AR21, OR1–OR82, L1–L39, D1–D5) are frozen — they are cited by value in 53 completed plan files, 17 execution logs, and 4 workflow files. Renumbering would break thousands of cross-references. Gaps from retired slots (AR8; OR10, OR11, OR36, OR38, OR51, OR53; L10, L13–L16, L18–L23) are documented in the "Retired slots" block at the top of AGENTS.md and are NOT reused. New rules continue from OR85; new landmines from L40; new decisions from D6. Source: numbering policy (prompt-10.3).

- **OR85.** Governance doc condensation merges document the retired slot in the "Retired slots" block with a one-line reason and a pointer to the merged rule. Example: `OR36 — merged into OR35 (prompt-10.3)`. The merged rule's source citation is updated to include the retired rule's landmine sources. Source: OR84 (clarified).

Commit: `docs: add OR83-OR85 for prompt-10.3`

---

## S1 — Condensation Merge 1: OR35 + OR36 → OR35

**File**: `AGENTS.md`

Per the condensation analysis (Claude review + Architect verification), OR35 (git-specific output minimization) and OR36 (general bash output minimization) overlap and can merge cleanly.

**Old** (OR35 + OR36, ~13 lines):
```markdown
OR35. Use token-efficient git commands:
- `git status -s` not `git status`
- `git diff --stat` not `git diff` (full diff only when line changes are needed)
- `git log --oneline -N` never bare `git log`
- Pipe through `tail -n N` to truncate
- If full output is needed, note why before running

### Git Bash output discipline
OR36. Minimize Git Bash output:
- Pipe through `tail -n N` (default N=5) unless more is needed
- Chain multi-command verifications with `;`; capture only final summary line
- Never run a command producing >20 lines without truncation
- Pre-commit hooks: `2>&1 | tail -n 10`; if hook fails, re-run without truncation for full output
- **pytest**: always full verbose `-vvv`, no `-q`, no `--tb=short`, no piping to `tail` (full output required for hangs/stuck tests/failure details)
- ruff/mypy: `| tail -n 3` (you only need the error count)
```

**New** (merged OR35, ~9 lines):
```markdown
OR35. Minimize command output. Pipe through `tail -n N` (default N=5) unless full output is needed. Never run a command producing >20 lines without truncation. Specifics:
- git: `git status -s` not `git status`; `git diff --stat` not `git diff` (full diff only when line changes needed); `git log --oneline -N` never bare `git log`
- ruff/mypy: `| tail -n 3` (you only need the error count)
- pre-commit hooks: `2>&1 | tail -n 10`; if hook fails, re-run without truncation for full output
- pytest: always full verbose `-vvv`, no `-q`, no `--tb=short`, no piping (full output required for hangs/stuck tests/failure details)
- Chain multi-command verifications with `;`; capture only final summary line
- If full output is needed, note why before running

> **OR36 permanently retired** — merged into OR35 (prompt-10.3). See OR35 for the unified output-minimization rule.
```

**Update the Landmines→Rules table**: L24 and L28 currently reference "OR41, OR43" — no change needed (OR41 and OR43 are not affected by this merge). But check: does any table row reference OR36? If so, update to OR35.

---

## S2 — Condensation Merge 2: OR9 + OR10 + OR11 → OR9

**File**: `AGENTS.md`

Per the condensation analysis, OR9 (tag every prompt), OR10 (verify tag before push), OR11 (verify tag after push) are 3 stages of one operation.

**Old** (OR9 + OR10 + OR11, 3 rules):
```markdown
OR9. Tag EVERY prompt. Even docs-only plans must have `git tag prompt-{N}`.

OR10. Tag verification before push: `git tag --list prompt-{N}`. If empty, tag wasn't created.

OR11. Post-push verification (mandatory): `git ls-remote --tags origin | grep "prompt-{N}"`. If empty, push failed.
```

**New** (merged OR9, 1 rule with 3 sub-clauses):
```markdown
OR9. Tag every prompt at `/close` step 16, and verify at two stages:
- **Before create**: `git tag --list prompt-{N}` must be empty (premature-tag check per OR76). If not empty, STOP — do not force-push.
- **Create**: `git tag prompt-{N}`. Even docs-only plans must be tagged.
- **Post-push verify (mandatory)**: `git ls-remote --tags origin | grep "prompt-{N}"`. If empty, push failed — STOP.

> **OR10 and OR11 permanently retired** — merged into OR9 (prompt-10.3).
```

**Saves**: ~2 lines. OR10 and OR11 slots retired.

---

## S3 — Consolidate Retired Slots Block

**File**: `AGENTS.md`

Currently there are 2 inline retired-slot call-outs (AR8 at line 28, OR38 at line 165). After S1 and S2, OR36, OR10, OR11 are also retired. Replace the inline call-outs with one consolidated block near the top.

**Location**: After the header (after line 5, before `## Architecture Rules`).

**Add**:
```markdown
> **Retired slots** (do not reuse — per OR84): AR8 (AR7 covers it), OR10 (merged into OR9, prompt-10.3), OR11 (merged into OR9, prompt-10.3), OR36 (merged into OR35, prompt-10.3), OR38 (plan files kept forever), OR51 (never assigned), OR53 (never assigned).
```

**Remove** the 2 inline call-outs:
- Line 28: `> **AR8 permanently retired** — AR7 already enforces this; do not reuse slot AR8.`
- Line 165: `> **OR38 permanently retired** — all plan files kept forever; do not reuse slot.`

---

## S4 — LANDMINES.md Footer → Pointer

**File**: `LANDMINES.md`

The "Capturing new landmines (L34+)" footer duplicates the "LANDMINES.md — when to read/write" block in AGENTS.md. Replace the footer with a pointer.

**Old** (footer, ~10 lines):
```markdown
## Capturing new landmines (L34+)

At `/close` step 11, append:
```markdown
## L{n} — <one-line title>
**Trigger**: <Plan #, step, command/file/context>
**Impact**: <What broke>
```
Trigger and impact only. No narrative, no cross-references, no proposed fixes.
```

**New** (pointer, 3 lines):
```markdown
## Capturing new landmines (L40+)

See `AGENTS.md` "LANDMINES.md — when to read/write" for format and graduation procedure. Append-only — entries are never edited or removed. New landmines continue from L40 (per OR84).
```

---

## S5 — Update Landmines→Rules Table

**File**: `AGENTS.md` (the "Landmines → Rules" table near the bottom)

Update rows that referenced retired rules:

| Landmine | Old rule ref | New rule ref |
|---|---|---|
| L24 | OR41, OR43 | OR41, OR43 (unchanged — these aren't retired) |
| L25 | OR42 | OR42 (unchanged) |
| L26 | OR40 | OR40 (unchanged — OR81 is a new rule about the audit tool, not a replacement) |

Add rows for L36–L39 (added in prompt-10.2 but may not be in the table yet):
```markdown
| L36 | OR76 | Premature git tag creation requires force-push to move |
| L37 | OR77 | Coverage skipped or unmeasured |
| L38 | OR78 | Bandit Low count drifted without baseline reconciliation |
| L39 | OR79 | Quota exhaustion mid-plan causes context loss |
```

---

## S6 — Update AGENTS.md "when to read" Subset References

**File**: `AGENTS.md`

OR22 lists the always-on subset: "OR5, OR6, OR15, OR16, OR34, AR5, AR16, AR21." Verify none of these were retired by S1/S2. (None were — OR5, OR6, OR15, OR16, OR34 are all unaffected.) No change needed, but verify and note in the execution log.

---

## S7 — Update PLANS.md Baselines + Reconciliation Note

**File**: `PLANS.md`

### S7.1 — Add reconciliation note
```
**Plan 10.3**: Baseline → 169 tests. Delta: 0 — governance condensation patch, no test changes.
```

### S7.2 — Update "Last updated" line
```
**Last updated**: 2026-06-29 (prompt-10.3)
```

### S7.3 — Add note about numbering policy
In the "Key Document Cross-References" table or a new note section, add:
```
**Numbering policy** (per OR84): Rule and landmine numbers are frozen — never renumbered. Gaps from retired slots are documented in AGENTS.md's "Retired slots" block. New rules continue from OR85; new landmines from L40.
```

---

## S8 — Run Full Verification

Per `/close` steps 1–8 (re-read close.md fresh per OR71). **Per OR83, use `git add -A` for ALL commits — no explicit `git add <file>` lists.**

### S8.1 — Tests with coverage (per OR77)
```bash
.venv/Scripts/python.exe -m pytest tests/ -vvv --cov=. --cov-report=term-missing
```
Expected: 169 passed, 3 skipped, coverage ≥93%. If coverage <88%, STOP.

### S8.2 — Ruff
```bash
.venv/Scripts/ruff.exe check . 2>&1 | tail -n 3
```
Expected: 0 errors.

### S8.3 — Mypy (full repo)
```bash
.venv/Scripts/mypy.exe . --ignore-missing-imports 2>&1 | tail -n 5
```
Expected: 0 errors.

### S8.4 — Bandit
```bash
.venv/Scripts/bandit.exe -r . -ll --exclude .venv,venv,env,.git,node_modules,__pycache__,build,dist,.tox,.eggs,.pytest_cache 2>&1 | tail -n 5
```
Expected: 332 Low (B101). If count changed >20% without test count change, STOP (per OR78).

### S8.5 — pip-audit
```bash
.venv/Scripts/pip-audit.exe --strict --requirement txt/requirements.txt 2>&1 | tail -n 5
```
Expected: 0 CVEs.

### S8.6 — Vulture
```bash
.venv/Scripts/vulture.exe . --min-confidence 80 --exclude .venv,venv,env,.git,node_modules,__pycache__,build,dist,.tox,.eggs,.pytest_cache,.mypy_cache,.ruff_cache,htmlcov 2>&1 | tail -n 5
```
Expected: 0 new findings.

### S8.7 — detect-secrets (per OR81)
```bash
.venv/Scripts/detect-secrets.exe scan --baseline txt/.secrets.baseline
```
Expected: exit 0.

### S8.8 — Custom AR checks
```bash
.venv/Scripts/python.exe scripts/ar_checks/no_globals.py sovereignai/
.venv/Scripts/python.exe scripts/ar_checks/constructor_arg_cap.py sovereignai/ --max-args 15
.venv/Scripts/python.exe scripts/ar_checks/no_context_bags.py sovereignai/
.venv/Scripts/python.exe scripts/ar_checks/docstring_discipline.py sovereignai/
.venv/Scripts/python.exe scripts/ar_checks/no_hardcoded_component_names.py web/ cli/ tui/ phone/
.venv/Scripts/python.exe scripts/ar_checks/ui_does_not_touch_core.py
```
All must pass.

### S8.9 — Verify no broken rule citations

After the merges, grep for any remaining references to retired rules:
```bash
# Should return only the "Retired slots" block and the retired-slot call-outs in S1/S2
grep -n "OR10\b\|OR11\b\|OR36\b" AGENTS.md
# Verify OR22's always-on subset doesn't reference retired rules
grep -n "OR5, OR6, OR15, OR16, OR34" AGENTS.md
```

If any active rule text (not a retired-slot notice) references OR10, OR11, or OR36, STOP — update the reference to the merged rule (OR9 or OR35).

---

## STOP Conditions

- If any test/static analysis tool in S8 fails, STOP.
- If coverage <88%, STOP (per OR77).
- If `git status -s` after any `git add -A` shows unstaged changes, STOP (per OR80/OR83).
- If `git tag --list prompt-10.3` returns output BEFORE Step 16 (premature tag), STOP (per OR76).
- If S8.9 finds active rule text referencing retired rules (OR10, OR11, OR36), STOP and fix before committing.

---

## Files WILL Edit

- `AGENTS.md` (S0.3 — add OR83–OR85; S1 — merge OR35+OR36; S2 — merge OR9+OR10+OR11; S3 — retired slots block; S5 — update Landmines→Rules table; S6 — verify OR22 subset)
- `LANDMINES.md` (S4 — replace footer with pointer)
- `PLANS.md` (S7 — reconciliation note, last-updated, numbering policy note)

## Files WILL NOT Edit

- Any source file in `sovereignai/`
- Any test file
- Any AR check script
- `txt/.secrets.baseline`
- `txt/requirements.txt`
- `project-vision-Rev5.md`
- Execution logs (logs are append-only history — never edit past citations)
- Completed plan files (prompts/completed/ — never edit past citations)

---

## Closing

Run `/close`. Tag: `prompt-10.3`.

**Critical per OR83**: Every `git commit` MUST use `git add -A` — no `git add <file>` lists. This is the rule that prompt-10.2 violated 8 times.

**Critical per OR76**: Before `git tag prompt-10.3`, verify `git tag --list prompt-10.3` is empty.

**Critical per OR71**: Re-read `.devin/workflows/close.md` in full before running `/close`.

After `prompt-10.3` completes, the governance docs are condensed (~20 lines saved), the numbering policy is established (OR84 — never renumber), and the repo is ready for Plan 11. The Executor copies `prompts/plan-11-Rev3.md` to `prompts/plan-11.md` and begins.

---

## Adjudication Summary

This patch addresses:
1. **OR80 enforcement gap**: OR83 clarifies that `git add -A` is the ONLY allowed staging command (prompt-10.2 had 8 violations)
2. **Numbering policy**: OR84 freezes all existing numbers (53 plan files + 17 logs cite them); OR85 documents merge procedure
3. **Condensation**: OR35+OR36 merged, OR9+OR10+OR11 merged, retired-slots consolidated, LANDMINES footer → pointer (~20 lines saved)
4. **Claude's rejected suggestions**: OR40/41/43/44 NOT merged (distinct enforceable content); AR10 NOT folded into AR2 (Claude misread — 4 distinct architectural concerns)

Not addressed (out of scope — would break historical citations):
- Renumbering existing rules to close gaps (OR38, OR51, OR53 gaps remain; L10, L13–L16, L18–L23 gaps remain). Per OR84, these gaps are permanent.
- Editing execution logs to update old rule citations (logs are append-only history).
