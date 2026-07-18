Depends on: workflow-fix-2
Vision principles: P1, P5, P11
Open questions resolved: none

---

## S0 — Opening

- S0.1: Run `/open`
- S0.2: Read `AGENTS.md` in full
- S0.3: Check `.agent/executor/suggestions/` for new rule proposals
- S0.4: Check `.agent/shared/DEBT.md` for non-rule deferred items

---

## S1 — Fix AR21 Reference in ARCHITECTURE.md

- S1.1: Read `ARCHITECTURE.md` constraint verification table
- S1.2: Remove `check_ar21.py` reference from AR21 row; change to `—` (retired rule needs no check script)
- S1.3: Verify no other retired rules have check script references
- S1.4: Run `/verify` on `ARCHITECTURE.md`

---

## S2 — Fix AR Check Script Paths

- S2.1: Read `check_dependencies.py` — fix `tomli` import (use `tomllib` for Python 3.11+ or add fallback)
- S2.2: Read `check_p4_compliance.py` — fix path to DEBT.md (`.agent/shared/DEBT.md` not `.agent/executor/DEBT.md`)
- S2.3: Read `check_rule_conciseness.py` — fix path to AGENTS.md (`.agent/shared/AGENTS.md` not `.agent/executor/AGENTS.md`)
- S2.4: Run each fixed script in isolation to confirm exit 0
- S2.5: Run `ar_checks/run_all.py` — must pass with 0 failures
- S2.6: Run `/verify` on each modified script

---

## S3 — Re-enable and Fix verify_close.py Checks

- S3.1: Read `verify_close.py` current state
- S3.2: Re-enable execution log size check with correct logic: check only logs created in current session, not all historical logs
- S3.3: Re-enable plan file check with correct logic: check only plans that were executed in current session (match against CHANGELOG entry or PLANS.md active plan)
- S3.4: Add Windows PowerShell syntax note to skill files: use `;` not `&&` for command chaining
- S3.5: Run `verify_close.py` — must pass with all checks green
- S3.6: Run `/verify` on `verify_close.py`

---

## S4 — Verify Full Workflow Consistency

- S4.1: Run `check_rule_crossrefs.py` — must pass with 0 undefined citations
- S4.2: Run `ar_checks/run_all.py` — must pass with 0 failures
- S4.3: Run `or_checks/run_all.py` — must pass
- S4.4: Run `landmine_checks/run_all.py` — must pass
- S4.5: Run `verify_close.py` — must pass with all checks green
- S4.6: Verify no disabled checks remain (grep for "disabled" in verify_close.py)

---

## S5 — Update CHANGELOG and Documentation

- S5.1: Prepend CHANGELOG.md with workflow-fix-3 entry
- S5.2: Update PLANS.md with plan entry
- S5.3: Verify no new DEBT items created

---

## Closing

- S5.4: Run `/close`
