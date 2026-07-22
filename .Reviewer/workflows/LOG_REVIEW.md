# Log Review Workflow

**Version**: 1.0  
**Last Updated**: 2026-07-22  
**Status**: Active

## Purpose
Review execution logs to identify issues, errors, and patterns. Create findings for the Planner agent to create fix plans.

## Workflow Overview
```
Execution Log → Log Analysis → Findings Generation → Report Creation
```

## Phase 1: Log Loading

**Trigger**: Execution log provided by Executor agent  
**Goal**: Load and understand the execution log

**Steps**:
1. **Read Execution Log**: Read the execution log from Logs/ directory
2. **Read Attestation**: Read the execution attestation document if available
3. **Read CHANGELOG**: Read the CHANGELOG for recent changes
4. **Understand Context**: Understand the plan that was executed
5. **Compliance**: Post `✅ Gate LOG-1 PASS: Execution log loaded, context understood`

**Exit Gate**: Execution log fully loaded and understood

---

## Phase 2: Log Analysis

**Trigger**: Log loading complete  
**Goal**: Analyze execution log for issues, errors, and patterns

**Steps**:
1. **Error Detection**: Identify errors, failures, and exceptions in the log
2. **Pattern Detection**: Look for patterns or recurring issues
3. **Governance Check**: Check for governance rule violations
4. **Quality Assessment**: Assess overall execution quality
5. **Compliance**: Post `✅ Gate LOG-2 PASS: Log analysis complete, {error_count} errors found`

**Exit Gate**: Log analysis complete with findings identified

---

## Phase 3: Findings Generation

**Trigger**: Log analysis complete  
**Goal**: Generate structured findings from analysis

**Steps**:
1. **Categorize Findings**: Categorize findings by severity (critical, high, medium, low)
2. **Document Evidence**: Document evidence for each finding
3. **Identify Root Causes**: Identify potential root causes for each finding
4. **Suggest Fixes**: Suggest potential fixes for each finding
5. **Compliance**: Post `✅ Gate LOG-3 PASS: {findings_count} findings generated`

**Exit Gate**: Findings documented and categorized

---

## Phase 4: Report Creation

**Trigger**: Findings generation complete  
**Goal**: Create comprehensive review report for Planner agent

**Steps**:
1. **Create Report**: Create structured review report
2. **Include Evidence**: Include evidence and severity for each finding
3. **Add Recommendations**: Add recommendations for fix plans
4. **Validate Report**: Validate report completeness and accuracy
5. **Compliance**: Post `✅ Gate LOG-4 PASS: Review report created`

**Exit Gate**: Review report ready for Planner agent

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
- Execution log cannot be loaded
- Findings cannot be categorized
- Report cannot be created

---

## Evolution

**This workflow evolves when**:
- Log format changes
- Review criteria change
- Finding categorization changes
- Governance rules are updated