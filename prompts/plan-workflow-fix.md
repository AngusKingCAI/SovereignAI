# Plan: workflow-fix — Fix Governance Workflow Inconsistencies

Depends on: none
Vision principles: P1, P5, P11
Open questions resolved: none

---

## S0 — Opening

1. Run `/open`
2. Read `AGENTS.md` in full
3. Check `.agent/executor/suggestions/` for new rule proposals (create directory if missing)
4. Check `.agent/shared/DEBT.md` for non-rule deferred items

## S1 — Fix RULE_LIFECYCLE.md DEBT.md References

**WILL edit**: `.agent/shared/RULE_LIFECYCLE.md`

**S1.1**: Read `RULE_LIFECYCLE.md` in full

**S1.2**: Replace all 5 DEBT.md references for rule implementation with "implement directly" per AI_HANDOFF.md step 4:

- Line 5: "Architect implements via .agent/shared/DEBT.md workflow" → "Architect implements directly per AI_HANDOFF.md step 4"
- Line 25: "Architect implements via DEBT.md workflow per AI_HANDOFF.md step 4" → "Architect implements directly per AI_HANDOFF.md step 4"
- Line 41: "Add to .agent/shared/DEBT.md with target plan number per AI_HANDOFF.md step 4" → "Include in next plan's S0 per AI_HANDOFF.md step 4"
- Line 50: "Add to .agent/shared/DEBT.md with target plan" → "Include in next plan's S0"
- Line 59: "implementation via DEBT.md workflow per AI_HANDOFF.md step 4" → "implementation directly per AI_HANDOFF.md step 4"

**S1.3**: Add note in TRIAGE stage: "Accepted rules are included in next plan's S0; rejected rules are archived; deferred rules are added to DEBT.md only if they are non-rule items"

**S1.4**: Run `/verify` on `RULE_LIFECYCLE.md`

**S1.5**: Run `/verify` on `AI_HANDOFF.md` to confirm consistency

## S2 — Create Missing Directories and Infrastructure

**S2.1**: Create `.agent/executor/suggestions/` directory with `.gitkeep`

**S2.2**: Create `.agent/executor/suggestions/archived/` directory with `.gitkeep`

**S2.3**: Create `.agent/executor/suggestions/graduated/` directory with `.gitkeep`

**S2.4**: Create `logs/` directory with `.gitkeep`

**S2.5**: Update `suggest_rule.py` to validate directory exists before writing (already handles this, but add explicit check)

**S2.6**: Run `/verify` on `suggest_rule.py`

## S3 — Fix Empty OR and Landmine Check Runners

**S3.1**: Read `.agent/executor/scripts/or_checks/run_all.py`

**S3.2**: Update to properly discover and execute OR check scripts (pattern after ar_checks/run_all.py)

**S3.3**: Exit 1 if any OR check fails, exit 0 if all pass, exit 0 with message if no checks exist yet

**S3.4**: Read `.agent/executor/scripts/landmine_checks/run_all.py`

**S3.5**: Update to properly discover and execute landmine check scripts (pattern after ar_checks/run_all.py)

**S3.6**: Exit 1 if any landmine check fails, exit 0 if all pass, exit 0 with message if no checks exist yet

**S3.7**: Run `/verify` on both runners

**S3.8**: Test both runners in isolation: `python or_checks/run_all.py` and `python landmine_checks/run_all.py`

## S4 — Verify Workflow Consistency Across All Documents

**S4.1**: Cross-reference check: AI_HANDOFF.md step 4 ↔ RULE_LIFECYCLE.md SUGGEST/TRIAGE/DECIDE/IMPLEMENT

**S4.2**: Cross-reference check: close/SKILL.md steps 6-7 ↔ or_checks/run_all.py and landmine_checks/run_all.py

**S4.3**: Cross-reference check: verify/SKILL.md steps 5-6 ↔ or_checks/run_all.py and landmine_checks/run_all.py

**S4.4**: Cross-reference check: scan/SKILL.md steps 5-6 ↔ or_checks/run_all.py and landmine_checks/run_all.py

**S4.5**: Cross-reference check: open/SKILL.md step 5 ↔ suggest_rule.py and suggestions/ directory

**S4.6**: Cross-reference check: close/SKILL.md step 11 ↔ logs/ directory existence

**S4.7**: Run `check_rule_crossrefs.py` if available

**S4.8**: Document any remaining inconsistencies in execution log

## S5 — Update CHANGELOG and Documentation

**S5.1**: Prepend `CHANGELOG.md` with workflow-fix entry documenting all fixes

**S5.2**: Update `PLANS.md` with plan entry

**S5.3**: Verify no new DEBT items created (all fixes are governance consistency, not deferred features)

## Closing

**S5.4**: Run `/close`

---

**Files modified**: ~6
**Lines changed**: ~50
**Risk**: Low — all documentation and infrastructure consistency fixes, no code changes
