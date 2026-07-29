---
id: wf-plan-tmpl-brief
status: active
owner: planner-agent
updated: 2026-07-28
purpose: Brief document for Round Table panelists summarizing the plan for review
---

# Plan Brief Template

**Purpose**: Brief document for Round Table panelists (internal and external) summarizing the plan for review  
**Location**: Workflow/Planner/Templates/Plan_Brief_Template.md  
**Usage**: Save as Plans/Queued/plan-{N}.{rev}_Brief.md (stored with the plan file)  
**Version**: 1.0

---

## Brief Structure Template

```markdown
# Plan Brief - Plan {N} Revision {rev}

**Date**: {YYYY-MM-DD}  
**Review Type**: {Internal Round Table | External Round Table}  
**Plan File**: Plans/Queued/plan-{N}.{rev}.md  
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
- Accuracy: Are the technical claims accurate and feasible?
- Completeness: Are all necessary elements included for your domain?
- Clarity: Is the plan clear and unambiguous for your domain?
- Structure: Is the plan well-organized and executable?
- Context: Is sufficient background provided for your domain?

**Domain-Specific Focus**:
- **Security Expert**: Security vulnerabilities, compliance gaps, threat coverage, encryption strategies
- **Infrastructure Expert**: Scalability, reliability, operational readiness, cost efficiency
- **Data Architecture Expert**: Data integrity, storage patterns, data flows, governance compliance
- **Application Architecture Expert**: Component boundaries, dependency health, pattern appropriateness, integration design
- **Operations/DevOps Expert**: Deployment safety, monitoring coverage, operational readiness, supportability
- **Business Alignment Expert**: Business value alignment, cost-effectiveness, time-to-market considerations, user impact

---

## Quality Rubric Reference

**Scoring**: Use Workflow/Workflow_Reference/Quality_Assessment_Framework.md for dimension-specific evaluation (1-5 scale)
**Thresholds**: 
- 5 (Excellent): Clean pass
- 4 (Good): Clean pass  
- 3 (Fair): Proceed with rationale
- 2 (Poor): Requires revisions
- 1 (Critical): Block review

---

## Panelist Assignment

**Your Persona**: {Security Expert | Infrastructure Expert | Data Architecture Expert | Application Architecture Expert | Operations/DevOps Expert | Business Alignment Expert}

**Your Focus**: {Specific domain expertise based on persona}

**CRITICAL**: At the start of your review response, you MUST explicitly state:
- For Internal Round Table: "I am reviewing as {Persona}"
- For External Round Table: "I am reviewing as {Model Name} ({Persona})"

This ensures proper logging to the consolidated file:
- Internal: Logs/Planner/Round Table/Internal/Plan{N}_Roundtable.md (append per revision, separated by {Agent_Persona})
- External: Logs/Planner/Round Table/External/Plan{N}_Roundtable.md (append per revision, separated by Agent_Name_{Agent_Persona})

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
  "overall_score": 1-5,
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