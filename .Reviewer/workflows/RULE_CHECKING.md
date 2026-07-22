# Rule Checking Workflow

**Version**: 1.0  
**Last Updated**: 2026-07-22  
**Status**: Active

## Purpose
Check code and configuration against governance rules and quality gates. Verify compliance with established rules and standards.

## Workflow Overview
```
Code/Config → Rule Check → Gate Verification → Compliance Report
```

## Phase 1: Scope Definition

**Trigger**: Rule checking task initiated  
**Goal**: Define the scope of the rule checking

**Steps**:
1. **Identify Target**: Identify the code or configuration to be checked
2. **Define Scope**: Define in-scope and out-of-scope paths
3. **Select Rules**: Select applicable rules and gates for the scope
4. **Set Thresholds**: Set compliance thresholds and criteria
5. **Compliance**: Post `✅ Gate RULE-1 PASS: Scope defined, {rule_count} rules selected`

**Exit Gate**: Scope clearly defined with applicable rules selected

---

## Phase 2: Rule Execution

**Trigger**: Scope defined  
**Goal**: Execute selected rules against the target

**Steps**:
1. **Execute Rules**: Run selected rules against target code/config
2. **Collect Results**: Collect rule execution results
3. **Categorize Violations**: Categorize violations by severity
4. **Identify Patterns**: Identify patterns in violations
5. **Compliance**: Post `✅ Gate RULE-2 PASS: Rules executed, {violation_count} violations found`

**Exit Gate**: Rule execution complete with results collected

---

## Phase 3: Gate Verification

**Trigger**: Rule execution complete  
**Goal**: Verify compliance with quality gates

**Steps**:
1. **Check Gates**: Verify compliance with each quality gate
2. **Assess Severity**: Assess severity of gate failures
3. **Identify Blockers**: Identify blocking issues that must be resolved
4. **Verify Thresholds**: Verify compliance with defined thresholds
5. **Compliance**: Post `✅ Gate RULE-3 PASS: Gates verified, {blocker_count} blockers identified`

**Exit Gate**: Gate verification complete with compliance status

---

## Phase 4: Compliance Report

**Trigger**: Gate verification complete  
**Goal**: Create comprehensive compliance report

**Steps**:
1. **Generate Report**: Create structured compliance report
2. **Include Details**: Include rule results, gate status, and recommendations
3. **Prioritize Issues**: Prioritize issues by severity and impact
4. **Add Recommendations**: Add recommendations for remediation
5. **Compliance**: Post `✅ Gate RULE-4 PASS: Compliance report created`

**Exit Gate**: Compliance report ready for review

---

## Universal Rules Compliance

**All phases must follow**:
- **GR1-GR5**: Universal governance rules (agent responsibilities, single-responsibility, handoff boundaries)
- **ER1-ER5**: Universal editing rules (file editing best practices, large changes, failure recovery)
- **GR2**: Reviewer scope is review only, does NOT create plans

---

## Stop Conditions

**Halt execution if**:
- Missing compliance line for any gate
- Rule execution fails
- Gate verification cannot be completed
- Compliance report cannot be created

---

## Evolution

**This workflow evolves when**:
- Rule definitions change
- Gate criteria change
- Compliance thresholds change
- Governance rules are updated