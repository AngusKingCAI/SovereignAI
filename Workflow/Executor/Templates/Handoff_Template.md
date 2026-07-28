---
id: wf-exec-tmpl-handoff
status: active
owner: executor-agent
updated: 2026-07-28
purpose: Template for structured handoff files from Executor agent to Reviewer agent
---

# Executor Handoff Template

**Purpose**: Template for structured handoff files from Executor agent to Reviewer agent
**Location**: Workflow/Executor/Templates/Handoff_Template.md
**Usage**: Save as Logs/Executor/Handoff/{Plan Name}/handoff.md
**Version**: 1.0

---

## Handoff File Structure Template

```markdown
# Executor Handoff - {Plan Name}

**Date**: {YYYY-MM-DD}
**Handoff ID**: {Unique identifier for this handoff}
**Source Agent**: Executor
**Target Agent**: Reviewer
**Session ID**: {Session identifier for this execution}

---

## Handoff Trigger

**Trigger**: Plan execution complete
**Plan File**: Plans/{Plan Name}.md
**Execution Mode**: {Manual/Auto/Complete}
**Execution Status**: {Success/Partial/Failed}

---

## Context Payload

### Plan Summary
{Brief summary of the plan that was executed, including goal and scope}

### Execution Results
{Summary of execution results, including what was implemented and what was skipped}

### Key Decisions
{List of key decisions made during execution, with rationale}

### Files Changed
{List of files that were modified, created, or deleted during execution}

### Dependencies
{List of dependencies that were affected or added during execution}

---

## Quality Metrics

**Implementation Quality**: {Assessment of implementation quality}
**Compliance Status**: {Compliance with rules and constraints}
**Test Results**: {Summary of test execution results}
**Validation Status**: {Summary of validation checks performed}

---

## Acceptance Criteria

**Review Focus**:
- Compliance with governance rules and constraints
- Scope alignment with original plan
- Quality of implementation
- Integration with broader system
- Documentation completeness

**Required Review Actions**:
- Review all files changed during execution
- Verify compliance with Architect rules
- Check scope alignment with plan
- Assess implementation quality
- Validate integration points

---

## Session Log Reference

**Session Log Path**: Logs/Executor/Session/{Session ID}/
**Execution Log**: Logs/Executor/Session/{Session ID}/execution.log
**Error Log**: Logs/Executor/Session/{Session ID}/errors.log (if errors occurred)
**Validation Log**: Logs/Executor/Session/{Session ID}/validation.log

---

## Known Issues

{List any known issues or limitations from execution}

---

## Recommendations

{List any recommendations for Reviewer agent}

---

## Handoff Validation

**File Creation**: {Date/time handoff file was created}
**Integrity Check**: {Status of file integrity validation}
**Required Fields**: {Status of required fields validation}
**Session Log Access**: {Status of session log reference validation}

---

## Handoff Acknowledgment

**Status**: {Pending/Acknowledged/Rejected}
**Acknowledged By**: {Reviewer agent signature if applicable}
**Acknowledgment Date**: {Date/time if acknowledged}
**Notes**: {Any notes from Reviewer agent}
```

---

## Required Fields Checklist

**Mandatory Fields**:
- ✅ Trigger
- ✅ Source Agent
- ✅ Target Agent
- ✅ Context Payload (Plan Summary, Execution Results, Key Decisions, Files Changed)
- ✅ Acceptance Criteria
- ✅ Session Log Reference

**Optional Fields**:
- Quality Metrics
- Known Issues
- Recommendations
- Handoff Acknowledgment

---

## Validation Requirements

**File Validation**:
- File must exist at correct path: Logs/Executor/Handoff/{Plan Name}/handoff.md
- File must be readable and not corrupted
- All mandatory fields must be present
- Context payload must contain all required components
- Session log reference path must exist and be accessible

**Content Validation**:
- Plan summary must match executed plan
- Execution results must be accurate and complete
- Files changed list must be accurate
- Session log reference must point to valid session directory

---

## Handoff Protocol

**This handoff file serves as the official transfer of execution responsibility from Executor to Reviewer agent.**

**Upon receiving this handoff, the Reviewer agent should:**
1. Validate handoff file integrity and completeness
2. Review session logs for detailed execution information
3. Examine all files changed during execution
4. Verify compliance with governance rules
5. Assess implementation quality and scope alignment
6. Provide feedback or approval for the executed work

**This handoff file should be retained as part of the execution audit trail.**