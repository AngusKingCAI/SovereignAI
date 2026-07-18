Depends on: workflow-fix-4
Vision principles: P1, P5, P11
Open questions resolved: none

---

## S0 — Opening

- S0.1: Run `/open`
- S0.2: Read `AGENTS.md` in full
- S0.3: Check `.agent/executor/suggestions/` for new rule proposals
- S0.4: Check `.agent/shared/DEBT.md` for non-rule deferred items

---

## S1 — Define STOP Command in AGENTS.md

- S1.1: Read `AGENTS.md` in full
- S1.2: Add formal STOP definition after invariant 1:
  "STOP means: halt current step execution, report failure reason, do not proceed to next step. Executor may fix the failure and retry the same step, but must not skip to subsequent steps without passing the current step. Only verify_close.py HARD GATE is fatal: do not commit or tag if it fails."
- S1.3: Run `/verify` on `AGENTS.md`

---

## S2 — Fix get_current_plan.py Path Bug

- S2.1: Read `.agent/executor/scripts/get_current_plan.py`
- S2.2: Fix line 22: `repo_root = Path(__file__).parent.parent.parent.parent` (go up 4 levels from scripts/ to repo root)
- S2.3: Verify prompts_dir resolves to `repo_root/prompts` (not `.agent/executor/prompts`)
- S2.4: Run `get_current_plan.py` — must return correct plan name or empty string (not error)
- S2.5: Run `/verify` on `get_current_plan.py`

---

## S3 — Fix verify_close.py Plan File Check (Rev Suffix Handling)

- S3.1: Read `.agent/executor/scripts/verify_close.py`
- S3.2: Fix plan file check to handle Rev suffixes:
  - Look for `plan-{current_plan}.md` OR `plan-{current_plan}-Rev*.md`
  - Check if ANY variant is in completed/ (not just exact match)
- S3.3: Fix execution log size check to only check CURRENT execution log:
  - Get current plan from get_current_plan.py
  - Check only `logs/execution-log-{current_plan}.md`
  - Re-enable the check (currently disabled)
  - Handle Rev suffixes: check `logs/execution-log-{current_plan}-Rev*.md` if base name not found
- S3.4: Run `verify_close.py` — must pass with all checks green
- S3.5: Run `/verify` on `verify_close.py`

---

## S4 — Fix verify_close.py Execution Log Size Check

- S4.1: Read `.agent/executor/scripts/verify_close.py` execution log size check section
- S4.2: Re-enable the check (remove "Execution log size check disabled" comment)
- S4.3: Fix logic to only check the execution log for the CURRENT plan (not all historical logs)
- S4.4: Handle case where execution log doesn't exist yet (return PASS with note)
- S4.5: Run `verify_close.py` — must pass with all checks green
- S4.6: Run `/verify` on `verify_close.py`

---

## S5 — Verify Plans 22-24 Stay in prompts/ (Drafts)

- S5.1: Verify `plan-22-*.md` files are in `prompts/` (not `completed/`)
- S5.2: Verify `plan-23-*.md` files are in `prompts/` (not `completed/`)
- S5.3: Verify `plan-24-*.md` files are in `prompts/` (not `completed/`)
- S5.4: Verify no execution logs exist for plans 22-24
- S5.5: Verify plans 22-24 are NOT in CHANGELOG as completed
- S5.6: If any plan 22-24 is in `completed/`, move back to `prompts/`

---

## S6 — Verify Workflow-Fix Plans in completed/

- S6.1: Verify `plan-workflow-fix.md` is in `completed/` with execution log
- S6.2: Verify `plan-workflow-fix-2.md` or `plan-workflow-fix-2-Rev*.md` is in `completed/` with execution log
- S6.3: Verify `plan-workflow-fix-3.md` or `plan-workflow-fix-3-Rev*.md` is in `completed/` with execution log
- S6.4: Verify execution logs exist for all workflow-fix plans
- S6.5: Run `verify_close.py` — must pass for all workflow-fix plans

---

## S7 — Update CHANGELOG and Documentation

- S7.1: Prepend `CHANGELOG.md` with workflow-fix-5 entry documenting STOP definition, get_current_plan.py fix, verify_close.py fixes
- S7.2: Update `PLANS.md` with plan entry
- S7.3: Verify no new DEBT items created

---

## Closing

- S7.4: Run `/close`
