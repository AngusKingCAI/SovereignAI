# Rule Lifecycle — SovereignAI

Process guide for rule suggestion, review, implementation, and graduation.

Authority: `.agent/architect/PRINCIPLES.md`. Executor may suggest rules via `suggest_rule.py`; Architect implements via `.agent/shared/DEBT.md` workflow.

---

## Lifecycle Stages

### 1. SUGGEST — Executor Proposes Rule

**Trigger**: Executor encounters recurring error pattern not covered by existing rules.

**Action**: Executor runs `suggest_rule.py` with:
- Rule type (OR/AR/Landmine)
- Trigger condition
- Frequency data
- Proposed rule text
- Detection method
- Affected files

**Output**: Structured suggestion file written to `.agent/executor/suggestions/suggestion_{type}_{timestamp}.md`

**Authority**: Executor may suggest; Architect implements via DEBT.md workflow per AI_HANDOFF.md step 4.

**No Executor Implementation**: Executor does NOT write check scripts or edit governance docs. Suggestion only.

---

### 2. TRIAGE — Architect Reviews Suggestions

**Trigger**: Round Table review or dedicated rule review session.

**Action**: Architect reviews `.agent/executor/suggestions/` directory.

**Decision**: Accept / Reject / Defer

**If Accept**:
- Assign rule ID (OR{n}, AR{n}, {C|H|M|L}{n})
- Add to `.agent/shared/DEBT.md` with target plan number per AI_HANDOFF.md step 4
- Include in next plan's S0

**If Reject**:
- Document reason in suggestion file
- Archive suggestion to `.agent/executor/suggestions/archived/`
- Note pattern in LANDMINES.md as "rejected pattern"

**If Defer**:
- Add to `.agent/shared/DEBT.md` with target plan
- Keep suggestion in pending state

---

### 3. DECIDE — Rule Approved for Implementation

**Trigger**: Round Table acceptance + target plan reached.

**Action**: Rule assigned ID, implementation via DEBT.md workflow per AI_HANDOFF.md step 4.

**Output**:
- AR rules: Added to `.agent/shared/ARCHITECTURE.md` with verification script requirement
- OR rules: Added to relevant `.devin/skills/*/SKILL.md` with verification script requirement
- Landmines: Added to `.agent/shared/LANDMINES.md` with detection script requirement

---

### 4. IMPLEMENT — Executor Writes Check Script

**Trigger**: Plan S0 includes accepted rule.

**Action**: Executor writes verification script:
- AR rules: `.agent/executor/scripts/ar_checks/check_ar{n}.py`
- OR rules: `.agent/executor/scripts/or_checks/check_or{n}.py`
- Landmines: `.agent/executor/scripts/landmine_checks/detect_{severity}{n}.py`

**Integration**:
- Script follows existing check pattern (exit 0 = pass, exit 1 = fail with stderr)
- Script discovered and executed by corresponding `run_all.py`
- Skill file updated with OR reference (if OR rule)
- ARCHITECTURE.md constraint verification table updated (if AR rule)
- LANDMINES.md detection column updated (if landmine)

**Verification**: Run `/verify` on check script, run in isolation, confirm exit codes.

---

### 5. VERIFY — Testing and False Positive Monitoring

**Trigger**: Check script integrated into workflow.

**Action**: Monitor for false positives during next 5 plan executions.

**Criteria**:
- Script must exit 0 (pass) for all clean builds
- No false positive failures in 5 consecutive plan closes
- False positive → script needs refinement before graduation

**If False Positive Detected**:
- Executor stops plan
- Architect reviews detection logic
- Script refined, re-verified, monitoring reset

---

### 6. GRADUATE — Rule Marked as Stable

**Trigger**: 5 clean passes with no false positives.

**Action**: Mark rule as stable in governance docs:
- Remove "PROVISIONAL" or "NEW" status indicator
- Add graduation date to rule metadata
- Archive suggestion file to `.agent/executor/suggestions/graduated/`

**Outcome**: Rule becomes part of stable governance baseline.

---

## Rule Type Specifics

### AR Rules (Architectural Rules)

**Location**: `.agent/shared/ARCHITECTURE.md`
**Verification**: `.agent/executor/scripts/ar_checks/check_ar{n}.py`
**Integration**: Add row to Constraint Verification table
**Execution**: Invoked by `ar_checks/run_all.py` at `/close` and `/scan`

### OR Rules (Operational Rules)

**Location**: `.devin/skills/*/SKILL.md`
**Verification**: `.agent/executor/scripts/or_checks/check_or{n}.py`
**Integration**: Add OR reference to relevant skill workflow steps
**Execution**: Invoked by `or_checks/run_all.py` at `/verify`, `/close`, and `/scan`

### Landmines

**Location**: `.agent/shared/LANDMINES.md`
**Verification**: `.agent/executor/scripts/landmine_checks/detect_{severity}{n}.py`
**Integration**: Add row to appropriate severity table with detection script reference
**Execution**: Invoked by `landmine_checks/run_all.py` at `/close` and `/scan`

---

## Directory Structure

```
.agent/executor/
├── suggestions/
│   ├── suggestion_or_20260718_090000.md (pending)
│   ├── suggestion_ar_20260718_091500.md (pending)
│   ├── archived/ (rejected suggestions)
│   └── graduated/ (graduated rule suggestions)
├── scripts/
│   ├── ar_checks/
│   │   ├── run_all.py
│   │   └── check_ar{n}.py
│   ├── or_checks/
│   │   ├── run_all.py
│   │   └── check_or{n}.py
│   └── landmine_checks/
│       ├── run_all.py
│       └── detect_{severity}{n}.py
└── suggest_rule.py

.agent/shared/
└── RULE_LIFECYCLE.md (this file)
```

---

## Key Principles

1. **Executor Suggests, Architect Decides**: Executor never implements rules without Architect approval.
2. **Structured Suggestion Format**: All suggestions follow the same format for consistent review.
3. **Graduation Requires Monitoring**: Rules must prove stability before graduation.
4. **No Silent Rule Changes**: All rule changes go through SUGGEST → TRIAGE → DECIDE → IMPLEMENT → VERIFY → GRADUATE.
5. **Archival Maintains History**: Rejected and graduated suggestions are archived, not deleted.