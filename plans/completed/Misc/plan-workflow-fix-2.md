Depends on: workflow-fix
Vision principles: P1, P5, P11
Open questions resolved: none

---

## S0 — Opening

- S0.1: Run `/open`
- S0.2: Read `AGENTS.md` in full
- S0.3: Check `.agent/executor/suggestions/` for new rule proposals
- S0.4: Check `.agent/shared/DEBT.md` for non-rule deferred items

---

## S1 — Add Clone-on-Log-Pushed to AI_HANDOFF.md

- S1.1: Read `AI_HANDOFF.md` Architect Workflow section
- S1.2: Add new step between current steps 1 and 2 (or as step 1.5):
  - "If user states execution log has been pushed: clone latest repo, read execution log, diff-check against plan expectations"
- S1.3: Update Plan Template S0 to include: "S0.0: If resuming from prior execution, clone latest repo and verify execution log state"
- S1.4: Run `/verify` on `AI_HANDOFF.md`

---

## S2 — Define OR Rules in Skill Files

- S2.1: Read all `.devin/skills/*/SKILL.md` files
- S2.2: Identify all OR references in each skill (e.g., "OR63" in close/SKILL.md, "OR17" in verify/SKILL.md)
- S2.3: Add formal OR rule definitions at the top of each skill file using `OR{n}.` format:
  - Example: `OR63. diskcache CVE monitoring — check DEBT.md for CVE status before close`
  - Example: `OR17. Deliverables ship in full or defer — no partial implementations`
- S2.4: Run `/verify` on each modified skill file
- S2.5: Run `check_rule_crossrefs.py` to verify all OR rules are now defined

---

## S3 — Create Missing AR Check Scripts (AR16-AR31)

- S3.1: Read `ARCHITECTURE.md` to identify which AR16-AR31 rules exist in the codebase references
- S3.2: For each AR rule that has a defined constraint but no check script:
  - Create `ar_checks/check_ar{n}.py` following the pattern of existing check scripts
  - Add entry to ARCHITECTURE.md constraint verification table
- S3.3: For AR rules that are referenced but have no defined constraint:
  - Either define the constraint in ARCHITECTURE.md
  - Or remove the reference from source code
- S3.4: Run `/verify` on each new check script
- S3.5: Run `ar_checks/run_all.py` to verify all scripts pass

---

## S4 — Clarify Execution Log Handling in close/SKILL.md

- S4.1: Read `close/SKILL.md` step 11
- S4.2: Clarify instruction: "Create BLANK execution log file at `logs/execution-log-{plan-name}.md` with ONLY the header template. Do NOT populate with chat transcript — user will populate after execution."
- S4.3: Add template header to step 11:
  ```
  # Execution Log: {plan-name}

  **Date**: YYYY-MM-DD
  **Plan**: {plan-file}
  **Executor**: Devin

  ---

  *Populate this file with the chat transcript from the {plan-name} plan execution.*
  ```
- S4.4: Run `/verify` on `close/SKILL.md`

---

## S5 — Verify Full Workflow Consistency

- S5.1: Run `check_rule_crossrefs.py` — must pass with 0 undefined citations
- S5.2: Run `ar_checks/run_all.py` — must pass
- S5.3: Run `or_checks/run_all.py` — must pass (or report "no checks yet" with exit 0)
- S5.4: Run `landmine_checks/run_all.py` — must pass (or report "no checks yet" with exit 0)
- S5.5: Cross-reference all governance documents for consistency
- S5.6: Document any remaining gaps in execution log

---

## Closing

- S5.7: Run `/close`
