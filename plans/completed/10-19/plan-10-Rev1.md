# Plan 10 — Scan 10 (Second Whole-Repo Scan)

**Special plan**: Scan prompt — mechanical verification of the full Plans 6–9 batch + close-workflow discipline fixes. No new features. No new architecture. Fixes only. If any scan reveals a structural problem requiring design decisions, STOP and report — do not guess. Skips Round Table review (per AI_HANDOFF.md scan-prompt exemption).

Depends on: prompt-9
Vision principles: none (mechanical scan — no architectural impact)
Open questions resolved: none

---

## S0 — Opening

**S0.1** — Run `/open` workflow from `.devin/workflows/open.md`. Verify `prompt-9` tag exists on origin. Confirm clean working copy on `main`. Activate venv (OR45).

**S0.2** — Read `AGENTS.md` in full. Note OR2 (file-scoped mypy except at scan prompts — full repo mypy here), OR3 (run scan tools ONE AT A TIME), OR22 always-on subset. **Re-read `.devin/workflows/close.md` in full before running `/close` at the end of this scan — do not use a cached/remembered version (per OR71 below).**

**S0.3** — Add new rules. These address the close-workflow discipline failures diagnosed across prompts 6–9 (see `close-workflow-diagnosis.md` for full evidence).

- **OR71 — Run workflow commands verbatim.** When executing any step in `.devin/workflows/*.md`, copy the command exactly as written (after substituting `{N}` placeholders for the current plan number). Do not paraphrase, simplify, or substitute a single-file command for a loop. If a command errors, report the error and STOP — do not fall back to a "simpler" version that achieves less (e.g., do not replace `for file in prompts/plan-{N}-Rev*.md; do mv ...; done` with `mv prompts/plan-{N}-Rev5.md ...`). Re-read the workflow file fresh at the start of every `/close` and `/scan` run; do not rely on a cached/remembered version. Source: L32.

- **OR72 — Never edit AR check scripts or tests to make a failure pass.** If a script in `scripts/ar_checks/` or a test in `tests/` fails, the failure indicates a real violation in the source code or a real bug in the test. Fix the source code, or fix the test's *logic* (not its assertion). Editing a test to weaken its assertion — excluding imports from a denylist, commenting out a check, raising a threshold — is a STOP condition. The only exception is if the weakening is explicitly documented in the plan's S0.3 with Architect sign-off (as was done for `WEB_MAIN_ALLOWED_IMPORTS` in Plan 6, which is a scoped allowlist for the web composition root, not a silent weakening). Source: L33.

- **OR73 — `/close` is mandatory and atomic.** Completing a plan's body (S1–Sn) does not close the plan. The plan is not closed until `/close` runs all 22 steps (or STOPs on a real failure). The Executor must not commit and tag manually as a substitute for `/close`. If `/close` fails partway, the Executor must report the failure to the User rather than falling back to manual commit+tag. Source: L27 (reinforced — prompt-7 showed the Executor forgot).

- **OR74 — Workflow files are Architect-authored.** `.devin/workflows/*.md` is authored by the Architect per the Document Relationships table in `AI_HANDOFF.md`. The Executor may apply a minimal patch to unblock the current close if a workflow bug is discovered mid-`/close`, but must (a) flag the patch in the execution log (Step 13 C9 mechanism) and (b) note it for the Architect to formally adopt in the next plan's S0.3. The Executor must not make undocumented workflow changes. The 4 workflow fix commits made during prompts 6–8 (`0619315`, `e0339c4`, `2150e4e`, `e70e285`) are ratified retroactively by this rule — their fixes are correct and are now formally adopted.

Commit: `docs: add OR71-OR74, L32-L33 for prompt-10`

---

## S1 — Fix Open Defect: Archive Plan 9 Rev1–4

**This is the open defect from prompt-9's failed close.** Per OR71, run the Step 17 for-loop verbatim now (it was skipped for Rev1–4 at prompt-9 close).

```bash
# Move all revisions of plan-9 (Rev1, Rev2, Rev3, Rev4 — Rev5 was already moved) to completed/
for file in prompts/plan-9-Rev*.md; do
  if [ -f "$file" ]; then
    mv "$file" prompts/completed/
  fi
done
```

**Verify** (per the new Step 17 verification sub-step added in S2 below):
```bash
remaining=$(ls prompts/plan-9-Rev*.md 2>/dev/null | wc -l)
if [ "$remaining" -gt 0 ]; then
  echo "STOP: $remaining plan-9-Rev*.md files still in prompts/"
  ls prompts/plan-9-Rev*.md
  STOP
fi
```

Expected: 0 remaining. If any remain, STOP.

**Commit** (separate from the scan commit — this is a `fix:` not a `docs:`):
```bash
git add prompts/completed/
git commit -m "fix: archive plan-9 Rev1-4 (missed by prompt-9 close workflow step 17)"
```

---

## S2 — Workflow Fixes (Architect-authored, applied by Executor per OR74)

These edits to `.devin/workflows/close.md` formalize the fixes from the diagnosis. Apply each via the Edit tool (not `sed` — per OR7/L28).

### S2.1 — Add verification sub-step to Step 17

**File**: `.devin/workflows/close.md`
**Location**: After the existing Step 17 for-loop, before Step 18.

**Add**:
```markdown
# Verify all Revs were moved (per OR71 — catches paraphrasing bugs)
remaining=$(ls prompts/plan-{N}-Rev*.md 2>/dev/null | wc -l)
if [ "$remaining" -gt 0 ]; then
  echo "STOP: $remaining plan-{N}-Rev*.md files still in prompts/ — for-loop did not move all Revs"
  ls prompts/plan-{N}-Rev*.md
  STOP
fi
# Also verify the base plan and brief were moved (if they existed)
```

### S2.2 — Add "re-read the workflow" reminder to Step 1 preamble

**File**: `.devin/workflows/close.md`
**Location**: Line 3 (the "Run straight through" preamble).

**Change**:
```
**Prerequisite**: `.venv/` must exist (verified at `/open` step 3). If missing, STOP and run `/open` first. All commands use absolute venv paths per OR46 — do not rely on `source .venv/Scripts/activate` (L30).
```
**To**:
```
**Prerequisite**: `.venv/` must exist (verified at `/open` step 3). If missing, STOP and run `/open` first. All commands use absolute venv paths per OR46 — do not rely on `source .venv/Scripts/activate` (L30).

**Re-read this file in full before starting** (per OR71). Do not use a cached/remembered version of these commands — workflow files change between plans. Copy each command verbatim (after substituting `{N}`), do not paraphrase.
```

### S2.3 — Add Step 17 script option (B3 from diagnosis)

**File**: `.devin/workflows/close.md`
**Location**: Step 17 — add a note pointing to a future script.

**Add** at the end of Step 17:
```markdown
**Note**: The for-loop above is the canonical archiving logic. A script version lives at `scripts/ar_checks/archive_plan.sh` (created in a future plan) — when it exists, prefer `bash scripts/ar_checks/archive_plan.sh {N}` over the inline loop. The script includes the verification check automatically.
```

(Do NOT create the script in this scan — it's a deferred improvement. Just add the note.)

---

## S3 — Audit AR7 Test Weakening (Prompt 6)

**Context**: Prompt-6 added `WEB_MAIN_ALLOWED_IMPORTS` to `tests/test_ar7_no_core_imports_in_ui.py`, allowing `web/main.py` (the web process composition root) to import `sovereignai.shared.container`, `event_bus`, `capability_api`, `capability_graph`, `auth`, `trace_emitter`, and `types`. This was documented in comments as a scoped allowlist for the composition root, not a silent weakening.

**This is NOT a "restore the original assertion" fix.** The allowlist is architecturally justified — `web/main.py` is the web process's equivalent of `sovereignai/main.py` (the core composition root), and a composition root must import the components it wires. The vision's P8 (UIs are separate processes consuming the capability API) is about UI *presentation* files not importing core, not about the web server's bootstrap file.

**Audit tasks**:

### S3.1 — Verify the allowlist is scoped to web/main.py ONLY

**File**: `tests/test_ar7_no_core_imports_in_ui.py`

Read the test logic that applies `WEB_MAIN_ALLOWED_IMPORTS`. Verify:
- The allowlist applies ONLY to `web/main.py` (not to other files in `web/`, `cli/`, `tui/`, `phone/`)
- Other `web/*.py` files (e.g., `web/schemas.py`, `web/static/app.js`) are still subject to the full `UI_PACKAGE_DENYLIST`
- The allowlist does not apply to `sovereignai/shared/capability_api.py` itself (which has its own `CORE_INTERNALS_CONCRETE_DENYLIST`)

If the scoping is correct, no change. If the allowlist leaks to other files, fix the test logic (not the assertion) and STOP.

### S3.2 — Verify web/main.py's imports all appear in the allowlist

**File**: `web/main.py`

Read the import statements (lines 28–38). Verify every `sovereignai.*` import is in `WEB_MAIN_ALLOWED_IMPORTS`. If any import is NOT in the allowlist, either (a) add it to the allowlist with a documented justification, or (b) refactor `web/main.py` to not import it. Do NOT silently add to the allowlist — each addition needs a comment explaining why `web/main.py` needs it.

### S3.3 — Document the audit result in CHANGELOG

If the audit passes (scoping correct, all imports justified), add a note to the prompt-10 CHANGELOG entry: "AR7 audit (S3): `WEB_MAIN_ALLOWED_IMPORTS` scoping verified — allowlist applies only to `web/main.py`; all imports justified as composition-root wiring."

If the audit fails, STOP and report — this is an architectural issue requiring a regular plan, not a scan fix.

---

## S4 — Run All Scan Tools (Full Repo, One at a Time per OR3)

Per `/scan` workflow step 1. Run each tool separately — parallel execution corrupts output streams (OR3). Re-read `.devin/workflows/close.md` steps 1–8 fresh before starting (per OR71).

### S4.1 — Full test suite

```bash
.venv/Scripts/python.exe -m pytest tests/ -vvv
```

Expected: 169 tests passed (per PLANS.md baseline). If count differs, update PLANS.md baseline with actual number + reason.

If any test fails, STOP. Do not fix — report to the Architect.

### S4.2 — Ruff (full repo)

```bash
.venv/Scripts/ruff.exe check . 2>&1 | tail -n 3
```

Expected: 0 errors. If errors, STOP.

### S4.3 — Mypy (full repo — scan prompt per OR2)

```bash
.venv/Scripts/mypy.exe . --ignore-missing-imports 2>&1 | tail -n 5
```

Expected: 0 errors. If errors, document each and fix mechanically (type annotations, `type: ignore` with comment). If any error requires a design decision, STOP and report.

### S4.4 — Bandit

```bash
.venv/Scripts/bandit.exe -r . -ll --exclude .venv,venv,env,.git,node_modules,__pycache__,build,dist,.tox,.eggs,.pytest_cache 2>&1 | tail -n 5
```

Expected: 0 findings above Low. Low findings (B101: assert_used in tests) are expected — count them per OR4. Update PLANS.md baseline with actual count. If new Medium/High findings, STOP.

### S4.5 — pip-audit

```bash
.venv/Scripts/pip-audit.exe --strict --requirement txt/requirements.txt 2>&1 | tail -n 5
```

Expected: 0 CVEs. If CVEs, STOP.

### S4.6 — Vulture

```bash
.venv/Scripts/vulture.exe . --min-confidence 80 --exclude .venv,venv,env,.git,node_modules,__pycache__,build,dist,.tox,.eggs,.pytest_cache,.mypy_cache,.ruff_cache,htmlcov 2>&1 | tail -n 5
```

Compare against `txt/vulture-whitelist.txt`. If new findings, STOP.

### S4.7 — detect-secrets

```bash
.venv/Scripts/detect-secrets.exe scan --baseline txt/.secrets.baseline
```

If exit code != 0, STOP.

### S4.8 — Custom AR checks (per /close step 8)

Run each check separately:
```bash
.venv/Scripts/python.exe scripts/ar_checks/no_globals.py sovereignai/
.venv/Scripts/python.exe scripts/ar_checks/constructor_arg_cap.py sovereignai/ --max-args 15
.venv/Scripts/python.exe scripts/ar_checks/no_context_bags.py sovereignai/
.venv/Scripts/python.exe scripts/ar_checks/docstring_discipline.py sovereignai/
.venv/Scripts/python.exe scripts/ar_checks/no_hardcoded_component_names.py web/ cli/ tui/ phone/
.venv/Scripts/python.exe scripts/ar_checks/ui_does_not_touch_core.py
```

If any check fails, STOP. **Per OR72**: do NOT edit the check script to make it pass. Fix the source code, or STOP and report.

---

## S5 — Governance Scans

### S5.1 — Scan LANDMINES.md

Add L32 and L33 (per the diagnosis):

```markdown
## L32 — Executor paraphrases workflow commands instead of running them verbatim
**Trigger**: Prompts 7, 8, 9 Step 17 — Executor ran `mv plan-{N}-Rev5.md` (single file) instead of the `for file in prompts/plan-{N}-Rev*.md` loop defined in close.md. Result: older plan revisions left in `prompts/`; User had to ask 3 times; repo state inconsistent.
**Impact**: 3 User interventions across prompts 7–9; plan-9 Rev1–4 unarchived for 1+ prompt cycles; undermined trust in /close workflow reliability.
**Graduated to**: OR71.

## L33 — Executor weakens AR check scripts or tests to make a failure pass
**Trigger**: Prompt 6 close — `test_ar7_no_core_imports_in_ui.py` failed because `web/main.py` imported `sovereignai.shared.*`. Executor edited the test to add `WEB_MAIN_ALLOWED_IMPORTS` allowlist. (This case was subsequently documented as a legitimate scoped allowlist — see Plan 10 S3 audit. But the *pattern* of editing a test to make it pass, rather than fixing the source, is the landmine.)
**Impact**: Risk of silently disabling architectural enforcement. AR7 (UI/core separation) could be effectively disabled without Architect sign-off.
**Graduated to**: OR72.
```

### S5.2 — Scan CHANGELOG.md

Verify every plan in the completed batch (prompts 6, 7, 8, 9) has an entry. If any is missing, add it.

### S5.3 — Scan PLANS.md

- Verify Test Baseline is current (169 tests).
- Verify Static Analysis Baseline reflects actual tool output from S4.
- Verify next-5-queue reflects actual state. After this scan completes, the queue should be:
  | Slot | Plan | Description | Depends on | Status |
  |---|---|---|---|---|
  | 1 | Plan 11 | Memory — Librarian + episodic/procedural/trace/working backends | Scan 10 | ⏳ Pending |
  | 2 | Plan 12 | Versioning — semver, negotiator, compatibility matrix | Plan 11 | ⏳ Pending |
  | 3 | Plan 13 | Test framework — conformance, contract, property-based tests | Plan 12 | ⏳ Pending |
  | 4 | Plan 14 | Education department — Teacher worker, self-correction skill | Plan 13 | ⏳ Pending |
  | 5 | Scan 15 | Third whole-repo scan | Plan 14 | ⏳ Pending |
- Refresh the Open Questions snapshot count against `project-vision-Rev5.md`.

### S5.4 — Scan all docstrings for stale references

Grep for references to removed/renamed modules. Fix mechanically. Specifically check for references to `dependency-injector` (removed in prompt-5), old module paths, etc.

### S5.5 — Run full test suite (final confirmation)

```bash
.venv/Scripts/python.exe -m pytest tests/ -vvv
```

### S5.6 — Verify coverage hasn't dropped >5% from baseline

```bash
.venv/Scripts/python.exe -m pytest tests/ --cov=. --cov-report=term 2>&1 | tail -n 10
```

Baseline: 96% (Plan 5). If coverage <91%, STOP.

### S5.7 — Audit against vision principles (14) and success criteria (40)

For each of the 14 principles and 40 success criteria in `project-vision-Rev5.md`, verify the codebase complies. If any principle is violated or criterion fails, STOP — architectural violations require a regular plan with Round Table review, not a scan fix.

### S5.8 — Review DEBT.md

For each deferred item, check if its trigger condition has been met. If yes, flag for the next plan. Specifically check:
- "Full Q8 versioning" — trigger met? (Plan 12 will resolve this)
- "Memory abstraction implementation" — trigger met? (Plan 11 will resolve this)
- "Self-correction / learning loops" — trigger met? (Plan 14 will resolve this)
- "Durable persistence backends and crash recovery" — trigger met? (Plan 11 will resolve this)

### S5.9 — Audit open questions

Check `project-vision-Rev5.md` open questions (Q1, Q2, Q8, Q13, Q31) — have any been implicitly resolved by prompts 6–9? If yes, move to "Resolved Open Questions" with a note. (Likely none — Plans 11–14 will resolve Q3, Q8, Q13, Q14.)

---

## S6 — C9 Rule Proposals

Per the diagnosis, the following rules are proposed (already added in S0.3 — this section documents them for the governance record):
- **OR71** — Run workflow commands verbatim (Source: L32)
- **OR72** — Never edit AR check scripts to make a failure pass (Source: L33)
- **OR73** — `/close` is mandatory and atomic (Source: L27 reinforced)
- **OR74** — Workflow files are Architect-authored (Source: AI_HANDOFF.md Document Relationships)

No additional C9 proposals from this scan.

---

## STOP Conditions

- If any scan tool (S4.1–S4.8) reports new findings, STOP.
- If the Step 17 verification (S1) shows remaining `plan-9-Rev*.md` files in `prompts/`, STOP.
- If the AR7 audit (S3) finds the allowlist scoping is wrong, STOP.
- If coverage <91% (5% drop from 96% baseline), STOP.
- If any vision principle or success criterion is violated, STOP.
- If any test fails after the S2 workflow fixes, STOP.

---

## Files WILL Create

(none — scan prompts do not create new source files)

## Files WILL Edit

- `.devin/workflows/close.md` (S2.1, S2.2, S2.3 — verification sub-step, re-read reminder, script note)
- `AGENTS.md` (S0.3 — add OR71–OR74)
- `LANDMINES.md` (S5.1 — add L32, L33)
- `PLANS.md` (S5.3 — update baselines, queue)
- `CHANGELOG.md` (S5.2 — add prompt-10 entry)
- `DEBT.md` (S5.8 — if any trigger conditions met)

## Files WILL NOT Edit

- Any source file in `sovereignai/` (scan prompts are mechanical — no architecture changes)
- Any test file (per OR72 — do not edit tests to make them pass; if a test fails, STOP)
- Any AR check script in `scripts/ar_checks/` (per OR72)
- `txt/requirements.txt` (no dependency changes)
- `project-vision-Rev5.md` (vision changes require Round Table, not scan)

---

## Closing

Run `/close`. Tag: `prompt-10`. Update CHANGELOG, PLANS.md.

**Critical**: Per OR71, re-read `.devin/workflows/close.md` in full before starting `/close`. Run Step 17's for-loop verbatim — do not paraphrase. The verification sub-step (added in S2.1) will catch any archiving failure.

After `/close` completes, the next batch (Plans 11–14, Rev3) is ready for execution. The Rev3 plans are in `prompts/plan-{11,12,13,14}-Rev3.md` (already in the repo from commit `3c70b34`). Copy each to `prompts/plan-{N}.md` (drop the Rev suffix) when the Executor starts each plan, per the handoff's Step 7 delivery instruction.

---

## Adjudication Summary (Scan 10 scope)

This scan addresses:
1. **Open defect**: Plan 9 Rev1–4 unarchived (S1)
2. **Close-workflow discipline**: OR71–OR74 + L32–L33 + close.md verification sub-step (S0.3, S2, S5.1)
3. **AR7 audit**: Verify the prompt-6 `WEB_MAIN_ALLOWED_IMPORTS` allowlist is scoped correctly (S3)
4. **Standard scan duties**: full-repo tools, governance scans, vision/criteria audit, DEBT review (S4, S5)

Not addressed (out of scope for scan):
- Cross-process GPU lock (deferred to DEBT.md — Plan 14)
- Procedural memory consumer wiring (deferred to DEBT.md — future RoutingEngine plan)
- Separate `sovereignai-education` package (deferred to DEBT.md)
- Full PII filter (deferred to DEBT.md)
- Full model versioning/rollback (deferred to DEBT.md)
- Dedicated task-state ledger (deferred to DEBT.md)
- Batched/background trace inserts (deferred to DEBT.md)
- `scripts/ar_checks/archive_plan.sh` script (noted in S2.3, deferred to future plan)
