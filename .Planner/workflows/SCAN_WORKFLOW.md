# Scan Workflow

**Version**: 1.0  
**Last Updated**: 2026-07-22  
**Status**: Active

## Purpose
Create fix/scan plans for the SovereignAI project based on Reviewer findings or periodic maintenance cycles. Scanner plans address issues, errors, or governance violations identified during plan execution or review.

## Workflow Overview
```
Reviewer Findings → Scan Plan Creation → Scan Plan Delivery → Round Table → Executor
```

## Phase 1: Review Input Assessment

**Trigger**: Reviewer provides findings, errors, or governance violations  
**Goal**: Understand the scope and severity of issues requiring fix/scan plan

**Steps**:
1. **Read Reviewer Report**: Read the review findings document provided by Reviewer agent
2. **Assess Severity**: Categorize findings by severity (critical, high, medium, low)
3. **Scope Impact**: Determine which files/components are affected by findings
4. **Check Dependencies**: Identify any dependencies or ripple effects of fixes
5. **Compliance**: Post `✅ Gate SCAN-1 PASS: {findings_count} findings assessed, severity: {summary}`

**Exit Gate**: Reviewer findings fully understood and categorized

---

## Phase 2: Root Cause Analysis

**Trigger**: Review input assessment complete  
**Goal**: Identify root causes of issues to prevent recurrence

**Steps**:
1. **Investigate Root Causes**: For each finding, identify the underlying cause
2. **Pattern Detection**: Look for patterns or systemic issues across findings
3. **Governance Check**: Check if findings indicate governance rule violations
4. **Compliance**: Post `✅ Gate SCAN-2 PASS: {root_cause_count} root causes identified, patterns: {summary}`

**Exit Gate**: Root causes identified for all critical/high findings

---

## Phase 3: Fix Strategy Design

**Trigger**: Root cause analysis complete  
**Goal**: Design effective fix strategies for identified issues

**Steps**:
1. **Strategy Selection**: Choose appropriate fix strategy for each finding
2. **Alternatives Considered**: Document rejected alternative strategies and reasoning
3. **Consequence Analysis**: Assess consequences of fix approach vs alternatives
4. **Risk Assessment**: Identify risks associated with fix implementation
5. **Compliance**: Post `✅ Gate SCAN-3 PASS: {strategy_count} fix strategies designed, risks: {summary}`

**Exit Gate**: Fix strategies designed for all findings with risk assessment

---

## Phase 4: Scan Plan Creation

**Trigger**: Fix strategy design complete  
**Goal**: Create comprehensive scan plan following PR1-PR15 and GR1-GR5

**Steps**:
1. **Plan Header**: Create plan header with Vision principles, PR rules, and resolved questions (PR1)
2. **Path Convention**: Use repo-relative paths only, no host-local paths (PR2)
3. **Manifest Integration**: Include complete Executor Manifest section (PR5)
4. **Plan Structure**: Follow defined structure: header, manifest, phases, deliverables (PR6)
5. **Quality Gates**: Ensure plan passes completeness, clarity, and specificity checks (PR7)
6. **Landmine Screening**: Screen plan against governance landmines (PR8)
7. **Compliance**: Post `✅ Gate SCAN-4 PASS: Scan plan created, gates: {pass_count} PASS`

**Exit Gate**: Scan plan created and passes all quality gates

---

## Phase 5: Reviewer Integration

**Trigger**: Scan plan created  
**Goal**: Ensure scan plan addresses all Reviewer findings comprehensively

**Steps**:
1. **Finding Coverage**: Verify all Reviewer findings are addressed in scan plan
2. **Action Mapping**: Map each finding to specific plan phases/actions
3. **Verification Gates**: Include verification gates for each fix
4. **Compliance**: Post `✅ Gate SCAN-5 PASS: {findings_count} findings addressed, coverage: 100%`

**Exit Gate**: All Reviewer findings comprehensively addressed in scan plan

---

## Phase 6: Scan Plan Delivery

**Trigger**: Reviewer integration complete  
**Goal**: Deliver scan plan to Round Table for coordination

**Steps**:
1. **Plan Validation**: Final validation of scan plan completeness
2. **Handoff Documentation**: Create handoff document for Round Table
3. **Compliance Posting**: Ensure all compliance lines are present and valid
4. **Compliance**: Post `✅ Gate SCAN-6 PASS: Scan plan ready for Round Table, phases: {phase_count}`

**Exit Gate**: Scan plan delivered to Round Table

---

## Periodic Scan Plans (Every 5 Plans)

**Trigger**: Every 5 completed plans in the plan sequence  
**Goal**: Periodic maintenance and governance compliance check

**Steps**:
1. **Scan Trigger**: Automatically trigger scan workflow at plan 5, 10, 15, etc.
2. **Comprehensive Review**: Conduct comprehensive review of recent plan executions
3. **Governance Check**: Verify governance rules are being followed correctly
4. **Quality Assessment**: Assess overall quality of recent plan executions
5. **Issue Identification**: Identify any patterns or systemic issues
6. **Compliance**: Post `✅ Gate SCAN-PERIODIC PASS: Periodic scan at plan {plan_number}, issues: {issue_count}`

**Exit Gate**: Periodic scan plan created and delivered to Round Table

---

## Universal Rules Compliance

**All phases must follow**:
- **GR1-GR5**: Universal governance rules (agent responsibilities, single-responsibility, handoff boundaries)
- **ER1-ER5**: Universal editing rules (file editing best practices, large changes, failure recovery)
- **PR1-PR15**: Planner-specific rules (plan creation, structure, quality gates)
- **PR16**: Universal rules integration
- **G6**: Gate enforcement mechanisms (hard gates blocking, soft gates non-blocking per AGENTS.md)

---

## Stop Conditions

**Halt execution if** (Hard Gates):
- Missing compliance line for any gate
- Scan plan fails to address critical Reviewer findings
- Root cause analysis incomplete for critical findings
- Fix strategy lacks risk assessment
- Plan fails quality gates (PR7)
- Plan contains governance landmines (PR8)

**Soft Gate Warnings** (Non-Blocking):
- Quality score <70 with documented rationale may proceed
- Quality score 70-89 with documented rationale may proceed
- Scan triggers similar soft gates as main workflow per G6

---

## Evolution

**This workflow evolves when**:
- New types of Reviewer findings emerge
- Scan plan patterns change
- Governance rules are updated
- Periodic scan frequency changes
- Workflow integration points change
