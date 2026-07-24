# Plan Brief Template

**Purpose**: Brief document for Round Table panelists (internal and external) summarizing the plan for review  
**Location**: Workflow/Planner/Plan_Brief_Template.md  
**Usage**: Save as Logs/Roundtable/Devin/brief-rev{N}.md or Logs/Roundtable/External/brief-rev{N}.md  
**Version**: 1.0

---

## Brief Structure Template

```markdown
# Plan Brief - Plan {N} Revision {rev}

**Date**: {YYYY-MM-DD}  
**Review Type**: {Internal Round Table | External Round Table}  
**Plan File**: Plans/plan-{N}.{rev}.md  
**Previous Iterations**: {List previous iterations if applicable}

---

## Plan Overview

**Goal**: {Copy goal from plan}

**Context Summary**: {Brief summary of why this work matters from user perspective}

**Changes Planned**: {High-level summary of what changes are being planned}

---

## Steps Summary

{Summarize the key steps from the plan (1-2 lines per step)}

---

## Dependencies Summary

{Brief overview of dependencies and execution order}

---

## Review Focus Areas

**Quality Dimensions to Evaluate**:
- Accuracy: Are the steps technically accurate and feasible?
- Completeness: Are all necessary elements included?
- Clarity: Is the plan clear and unambiguous?
- Structure: Is the plan well-organized and executable?
- Context: Is sufficient background provided?

**Scope Compliance**:
- Planning language only (no implementation details)
- Infrastructure focus if applicable
- Manual execution approach

**Risk Assessment**:
- Identify any potential implementation risks
- Check for missing dependencies
- Evaluate feasibility of proposed approach

---

## Quality Rubric Reference

**Scoring**: Use Plans/Quality_Rubric.md for dimension-specific evaluation
**Thresholds**: 
- 5.0-4.5: Excellent - Clean pass
- 4.4-3.5: Good - Clean pass  
- 3.4-2.5: Fair - Proceed with rationale
- 2.4-1.5: Poor - Requires revisions
- 1.4-0.0: Critical - Block review

---

## Panelist Assignment

**Your Persona**: {Structure Expert | Scope Expert | Quality Expert | Risk Expert | Alternative Expert | Infrastructure Expert}

**Your Focus**: {Specific domain expertise based on persona}

**Web Search Requirement**: MUST use web search to verify findings against current best practices and research

---

## Iteration Context

**Previous Findings**: {If not first iteration, summarize key findings from previous round}
**Changes Made**: {If not first iteration, summarize changes applied to address previous findings}
**Convergence Status**: {Current iteration count, trending toward convergence or not}

---

## Output Format

Provide structured review in JSON format:
```json
{
  "verdict": "PASS|FAIL",
  "dimensions": {
    "accuracy": {"score": 1-5, "notes": "...", "web_sources": ["https://..."]},
    "completeness": {"score": 1-5, "notes": "...", "web_sources": []},
    "clarity": {"score": 1-5, "notes": "...", "web_sources": ["https://..."]},
    "structure": {"score": 1-5, "notes": "...", "web_sources": []},
    "context": {"score": 1-5, "notes": "...", "web_sources": []}
  },
  "overall_score": 0.0-5.0,
  "issues": [
    {"severity": "CRITICAL|HIGH|MEDIUM|LOW", "dimension": "...", "description": "...", "web_sources": ["https://..."]}
  ],
  "notes": "Overall assessment with rationale"
}
```

---

## Review Guidelines

1. **Use Web Search**: Verify your findings against current best practices and research
2. **Stay in Persona**: Focus on your assigned domain expertise
3. **Be Specific**: Provide concrete, actionable feedback
4. **Cite Sources**: Include web search URLs for verification
5. **Rate Honestly**: Use quality rubric objectively
6. **Consider Execution**: Plan is for manual implementation, ensure clarity

---

## Review Timeline

**Start Time**: {Timestamp}  
**Expected Completion**: {Timestamp}  
**Panelist Deadline**: {Deadline for submitting review}
```