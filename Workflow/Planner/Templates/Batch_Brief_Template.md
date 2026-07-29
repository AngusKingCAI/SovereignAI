---
id: wf-plan-tmpl-batch-brief
status: active
owner: planner-agent
updated: 2026-07-29
purpose: Consolidated brief document for Round Table panelists summarizing multiple plans for batch review
---

# Batch Brief Template

**Purpose**: Consolidated brief document for Round Table panelists (internal and external) summarizing multiple plans for batch review  
**Location**: Workflow/Planner/Templates/Batch_Brief_Template.md  
**Usage**: Save as Plans/Queued/Batch_Brief.md (single file for entire batch)  
**Version**: 1.0

---

## Batch Brief Structure Template

```markdown
# Batch Brief - Batch {N}

**Date**: {YYYY-MM-DD}  
**Review Type**: {Internal Round Table | External Round Table}  
**Plans in Batch**: {List plan numbers and revisions (e.g., Plan 1.Rev1, Plan 2.Rev1, Plan 3.Rev1)}  
**Previous Iterations**: {List previous batch iterations if applicable}  
**Batch Revision**: {Current revision number for the batch}

---

## Plan Overviews

### Plan {N1}.Rev{rev1}
**Plan File**: Plans/Queued/plan-{N1}.{rev1}.md  
**Goal**: {Copy goal from plan}  
**Context Summary**: {Brief summary of why this work matters from user perspective}  
**Changes Planned**: {High-level summary of what changes are being planned}

### Plan {N2}.Rev{rev2}
**Plan File**: Plans/Queued/plan-{N2}.{rev2}.md  
**Goal**: {Copy goal from plan}  
**Context Summary**: {Brief summary of why this work matters from user perspective}  
**Changes Planned**: {High-level summary of what changes are being planned}

{Repeat for each plan in batch}

---

## Cross-Plan Dependencies

**Dependency Analysis**: {Analysis of dependencies between plans in batch}  
**Sequencing Risks**: {Analysis of risks related to execution order}  
**Integration Points**: {Key integration points between plans}  
**Shared Resources**: {Resources that are shared across multiple plans}

---

## Author's Confidence by Plan

**Plan {N1}.Rev{rev1}**: {High/Medium/Low} - {Brief rationale}  
**Plan {N2}.Rev{rev2}**: {High/Medium/Low} - {Brief rationale}  
{Repeat for each plan in batch}

---

## Named Open Questions by Plan

**Plan {N1}.Rev{rev1}**: {List open questions or uncertainties}  
**Plan {N2}.Rev{rev2}**: {List open questions or uncertainties}  
{Repeat for each plan in batch}

---

## Vision Principle Compliance by Plan

**Plan {N1}.Rev{rev1}**: {Analysis of compliance with CA-1 through CA-11 principles}  
**Plan {N2}.Rev{rev2}**: {Analysis of compliance with CA-1 through CA-11 principles}  
{Repeat for each plan in batch}

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

**Plan Assignment**: {Each panelist is assigned to review specific plans in the batch}

**CRITICAL**: At the start of your review response, you MUST explicitly state:
- For Internal Round Table: "I am reviewing as {Persona}"
- For External Round Table: "I am reviewing as {Model Name} ({Persona})"

This ensures proper logging to the consolidated file:
- Internal: Logs/Planner/Round Table/Internal/Batch{N}_Roundtable.md (append per revision, separated by {Agent_Persona})
- External: Logs/Planner/Round Table/External/Batch{N}_Roundtable.md (append per revision, separated by Agent_Name_{Agent_Persona})

**Web Search Requirement**: MUST use web search to verify findings against current best practices and research

---

## Iteration Context

**Previous Findings**: {If not first iteration, summarize key findings from previous round}  
**Changes Made**: {If not first iteration, summarize changes applied to address previous findings}  
**Convergence Status**: {Current iteration count, trending toward convergence or not}

---

## Output Format

Provide structured review in JSON format for your assigned plan(s):
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
7. **Batch Context**: Consider cross-plan dependencies and integration points
8. **Assigned Plans Only**: Review only the plans assigned to your persona

---

## Review Timeline

**Start Time**: {Timestamp}  
**Expected Completion**: {Timestamp}  
**Panelist Deadline**: {Deadline for submitting review}
```

---

**Last Updated**: 2026-07-29  
**Version**: 1.0  
**Maintained By**: Planner Agent