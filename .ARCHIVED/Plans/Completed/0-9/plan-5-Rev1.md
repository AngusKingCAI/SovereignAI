# Plan 5 — Scan 5 (First Whole-Repo Scan)

**Special plan**: Scan prompt — mechanical verification of the full Plans 1-4 batch. No new features. No new architecture. Fixes only. If any scan reveals a structural problem requiring design decisions, STOP and report — do not guess. Skips Round Table review (per AI_HANDOFF.md scan-prompt exemption).

Depends on: prompt-4
Vision principles: none (mechanical scan — no architectural impact)
Open questions resolved: none

---

## S0 — Opening

**S0.1** — Run `/open` workflow from `.devin/workflows/open.md`. Verify `prompt-4` tag exists on origin. Confirm clean working copy on `main`. Activate venv (OR45).

**S0.2** — Read `AGENTS.md` in full. Note OR2 (file-scoped mypy except at scan prompts — full repo mypy here), OR3 (run scan tools ONE AT A TIME), OR22 always-on subset.

**S0.3** — No new rules this plan. Proceed to S1.

---

## S1 — Run All Scan Tools (Full Repo, One at a Time per OR3)

Per `/scan` workflow step 1. Run each tool separately — parallel execution corrupts output streams (OR3).

### S1.1 — Full test suite

```bash
.venv/Scripts/python.exe -m pytest tests/ -vvv
```

Expected: 107 tests passed (per PLANS.md baseline). If count differs, update PLANS.md baseline with actual number + reason.

If any test fails, STOP. Do not fix — report to the Architect.

### S1.2 — Ruff (full repo)

```bash
.venv/Scripts/ruff.exe check . 2>&1 | tail -n 3
```

Expected: 0 errors. If errors, STOP.

### S1.3 — Mypy (full repo — scan prompt per OR2)

```bash
.venv/Scripts/mypy.exe . --ignore-missing-imports 2>&1 | tail -n 5
```

Expected: 0 errors (or known accepted warnings). This is the first full-repo mypy run. If errors, document each one and fix mechanically (type annotations, `type: ignore` with comment). If any error requires a design decision, STOP and report.

### S1.4 — Bandit

```bash
.venv/Scripts/bandit.exe -r . -ll --exclude .venv,venv,env,.git,node_modules,__pycache__,build,dist,.tox,.eggs,.pytest_cache 2>&1 | tail -n 5
```

Expected: 0 findings above Low. Low findings (B101: assert_used in tests) are expected — 119 per Plan 3 baseline, likely ~150 after Plan 4. Count per OR4 (filter: `>> Issue: [B`). If new Medium/High findings, STOP.

### S1.5 — pip-audit

```bash
.venv/Scripts/pip-audit.exe --strict --requirement txt/requirements.txt 2>&1 | tail -n 5
```

Expected: 0 CVEs. If CVEs, STOP.

### S1.6 — Vulture

```bash
.venv/Scripts/vulture.exe . --min-confidence 80 --exclude .venv,venv,env,.git,node_modules,__pycache__,build,dist,.tox,.eggs,.pytest_cache,.mypy_cache,.ruff_cache,htmlcov 2>&1 | tail -n 5
```

Compare against `txt/vulture-whitelist.txt`. If new findings, STOP.

### S1.7 — detect-secrets

```bash
.venv/Scripts/detect-secrets.exe scan --baseline txt/.secrets.baseline
```

If exit code != 0, STOP.

### S1.8 — Custom AR checks (per /close step 8)

Run each check separately:

- No globals in `sovereignai/`: `grep -rn "^global " sovereignai/ 2>/dev/null || echo "No globals found"`
- Constructor arg cap (15) in `sovereignai/`: scan all `__init__` methods
- No context bags in `sovereignai/`: check for `**kwargs` or untyped dict params
- Docstring verb-first, ≥10 words on first line: scan all `def` in `sovereignai/`
- No hard-coded component names in `web/`, `cli/`, `tui/`, `phone/`: (currently empty, skip)
- UI changes don't touch `sovereignai/`: `git diff --name-only HEAD~4 | grep "^sovereignai/" | grep -E "^(web|cli|tui|phone)/"` (should be empty)

If any check fails, STOP.

---

## S2 — Scan LANDMINES.md

For any landmine without a corresponding rule in `AGENTS.md`, propose the missing rule via C9. 

Current landmine-to-rule table in AGENTS.md covers L1-L9, L11, L12, L17, L24-L31. Verify all are present.

---

## S3 — Scan CHANGELOG.md

Verify every plan in the completed batch (prompt-0 through prompt-4) has an entry. Verify the entries match the actual commits.

---

## S4 — Scan PLANS.md

Verify baselines are current:
- Test baseline: 107 (per prompt-4 /close)
- Ruff: 0 errors
- Mypy: 0 errors
- Bandit: ~150 Low (B101 assert_used in tests)
- pip-audit: 0 CVEs
- Vulture: 0 findings
- detect-secrets: pass

Verify next-5-queue reflects actual state:
- Slot 1: Scan 5 (this plan) — ▶️ Active
- Slot 2: Plan 6 — ⏳ Pending Scan 5
- Slot 3: Plan 7 — ⏳ Pending Plan 6
- Slot 4: Plan 8 — ⏳ Pending Plan 7
- Slot 5: Plan 9 — ⏳ Pending Plan 8

---

## S5 — Scan All Docstrings for Stale References

Check for references to removed/renamed modules. Fix stale references mechanically.

Specifically check:
- Any reference to `core/` (should be `sovereignai/` per prompt-0.1 fix)
- Any reference to `.windsurf/` (should be `.devin/` per user's manual fix)
- Any reference to `master` branch (should be `main`)
- Any reference to `dependency-injector` in AGENTS.md AR4 (deferred to DEBT — verify DEBT entry exists)

---

## S6 — Run Full Test Suite (Final Confirmation)

```bash
.venv/Scripts/python.exe -m pytest tests/ -vvv
```

If any test fails after fixes from S2-S5, STOP.

---

## S7 — Verify Coverage

```bash
.venv/Scripts/python.exe -m pytest tests/ --cov=. --cov-report=term 2>&1 | tail -n 10
```

Verify coverage hasn't dropped >5% from baseline. Since this is the first coverage measurement, record the baseline.

---

## S8 — Audit Against Vision Principles

For each of the 14 principles in `project-vision-Rev5.md`, verify the codebase complies. If any principle is violated, STOP — architectural violations require a regular plan with Round Table review, not a scan fix.

Key checks:
- P1 (sacred core): Verify only the 12 Core Scope components are in `sovereignai/shared/` — no business logic
- P7 (modular core): Verify fault isolation — kill any skill → system stays up (conceptual check, not runtime)
- P8 (UIs separate processes): Verify `web/`, `cli/`, `tui/`, `phone/` are empty (no UI code yet)
- P9 (observability): Verify every component emits traces via TraceEmitter
- P10 (no silent failures): Verify EventBus catches subscriber exceptions and logs at ERROR
- P11 (DI, no globals): Verify no `global` keyword in `sovereignai/`
- P12 (docstrings): Verify every `def` has a docstring with verb-first ≥10 words first line

---

## S9 — Audit Against Success Criteria

For each of the 40 success criteria in `project-vision-Rev5.md`, verify the codebase passes. If any criterion fails, STOP.

Key criteria to verify:
- Criterion 4 (acyclic dependency test): Verify import graph has no cycles
- Criterion 5 (no globals): `grep -rn "^global " sovereignai/` returns zero matches
- Criterion 6 (constructor arg cap): No class in `sovereignai/` has >15 constructor args
- Criterion 7 (no context bags): No class accepts `**kwargs` or untyped dict as constructor arg

---

## S10 — Review DEBT.md

For each deferred item, check if its trigger condition has been met. If yes, flag for the next plan.

Current DEBT items:
- AR4 amendment (remove dependency-injector reference) — trigger: next plan's S0.3
- Security Guard implementation — trigger: post Plan 4 ✓ (flag for Plans 6-9 batch)
- Cross-platform packaging — trigger: when core is stable
- Model loading/unloading — trigger: when local model adapters are wired
- Self-correction/learning loops — trigger: when skill framework is stable
- Relay server E2EE — trigger: when Plan 4's placeholder is merged ✓ (flag for dedicated plan)
- Durable persistence — trigger: when Plan 3's in-memory store is stable ✓ (flag for Plans 6-9 batch)
- Full Q8 versioning — trigger: when second adapter version is needed
- Memory abstraction implementation — trigger: when Librarian Registry is needed (post Plan 4) ✓ (flag)
- Circuit breaker auto-recovery heartbeat — trigger: when periodic heartbeat component exists
- Task TTL/eviction strategy — trigger: when worker dispatch pipeline is wired
- DAGSpec extension for composite skills — trigger: when composite task execution is implemented

---

## S11 — Audit Open Questions

Check if any open questions from `project-vision-Rev5.md` have been implicitly resolved by recent plans. If yes, move to "Resolved Open Questions" with a note.

Currently resolved: Q5-Q7, Q10-Q12, Q15-Q30, Q26 (confirmed at Plan 4 /close)
Still open: Q1 (adapter contract — resolved by Plan 2), Q2 (skill discovery — resolved by Plan 2), Q3 (memory abstraction — interface defined Plan 3), Q4 (routing — resolved by Plan 3), Q8 (versioning MVP — resolved by Plan 2), Q9 (test strategy — resolved by Plan 1), Q13 (learning — deferred), Q14 (persistence — in-memory Plan 3), Q31 (packaging — deferred), Q32 (DEBT register — resolved by Plan 1)

Verify the vision doc's open questions section is updated to reflect these resolutions.

---

## S12 — Apply Kimi's Scan Report (if available)

**Note**: The user is running a Kimi scan of the repo for issues. When the report is pasted, the Architect will update this section with specific fixes. If no report is available at execution time, skip this step.

---

## S13 — Final Summary

```
=== SCAN COMPLETE (prompt-5) ===

Tools run:
- pytest: {count} tests, {count} passed
- ruff: {count} findings
- mypy: {count} findings (full repo)
- bandit: {count} findings
- pip-audit: {count} CVEs
- vulture: {count} findings ({count} new)
- custom AR checks: all pass / {count} failures

Fixes applied:
- {list of mechanical fixes}

Vision principle audit: 14/14 pass / {count} violations
Success criteria audit: 40/40 pass / {count} failures

DEBT.md review: {count} items reviewed, {count} flagged
Open questions audit: {count} resolved, {count} remain

=== REMINDER ===
Copy the chat log to logs/execution-log-prompt-5.md before closing this session.
```

---

## S14 — Commit, Tag, Push

1. Stage any mechanical fixes:
   ```bash
   git add -A
   git status -s | tail -n 20
   ```

2. Commit (if fixes were applied):
   ```bash
   git commit -m "prompt-5: Scan 5 — mechanical fixes" -m "Full-repo scan of Plans 1-4 batch. Fixes applied: {list}." -m "Baselines verified: {count} tests, 0 ruff errors, 0 mypy errors, {count} bandit Low, 0 CVEs, 0 vulture findings."
   ```

3. Tag:
   ```bash
   git tag prompt-5
   git tag --list prompt-5
   ```

4. Push:
   ```bash
   git push origin main
   git push origin prompt-5
   ```

5. Verify tag on origin:
   ```bash
   git ls-remote --tags origin | grep "prompt-5"
   ```

---

## Closing

Run `/close` workflow from `.devin/workflows/close.md`. Run all 21 steps.

**Expected results**:
- Tests: {count} passed (same as S1.1 or updated after fixes)
- Ruff: 0 errors
- Mypy: 0 errors (full repo — scan prompt)
- Bandit: {count} Low findings (B101 assert_used in tests — expected)
- pip-audit: 0 CVEs
- Vulture: 0 findings
- Detect-secrets: pass

**Reminder**: Step 21 (kill bash) mandatory.

---

## Files WILL Create

- `logs/execution-log-prompt-5.md` (created by `/close` step 14)

## Files WILL Edit

- (Depends on S12 — Kimi's scan report may identify files to fix)
- `PLANS.md` (update baselines if counts changed; add prompt-5 row; shift queue)
- `CHANGELOG.md` (append prompt-5 entry)
- `LANDMINES.md` (if new patterns discovered)
- `DEBT.md` (if items flagged or addressed)

## Files WILL NOT Edit

- `AGENTS.md` (no new rules unless scan reveals a pattern — if so, propose via C9)
- `AI_HANDOFF.md` (no changes)
- `.devin/workflows/*.md` (no changes)
- `documents/*` (archived — do not touch)
- `prompts/*` (no changes to existing plan files)
- `project-vision-Rev5.md` (locked — but open questions section may be crossed off per S11)

---

*Plan 5 — Scan 5. Rev1. Architect draft. Skips Round Table review per AI_HANDOFF.md scan-prompt exemption (mechanical verification, no architectural decisions).*
