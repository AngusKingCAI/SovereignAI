# Planner Plan Workflow

**ID**: WF-PLAN-001  
**Owner**: Planner Agent  
**Frequency**: Per planning task  
**Duration**: Variable (task-dependent)  
**Priority**: High

## Purpose
Create detailed, implementation-ready plans for AI-driven software development with comprehensive analysis and validation, including internal and external Round Table review with incremental validation to ensure plan quality and completeness.

## Roles and Owners
- **Planner Agent**: Executes workflow steps, enforces governance rules
- **User**: Provides task requirements, approves decisions
- **Governance System**: Gate-based validation and compliance enforcement

## Trigger and End State
- **Trigger**: User requests planning work or agent initiates task
- **End State**: Plan delivered for manual implementation with delivery authorization

## Scope

### Included
- Plan creation and refinement for development tasks
- Dependency analysis and requirement specification
- Quality assessment and risk identification
- Scope definition and boundary setting
- Implementation strategy development
- Plan validation and gate verification

### Excluded
- Direct code implementation (deferred to Executor agent)
- Application feature development (deferred to Executor agent)
- Production deployment operations (deferred to Executor agent)
- Infrastructure design (deferred to Architect agent)
- User interface development (deferred to Executor agent)
- Database schema modifications (deferred to Executor agent)

---

## Workflow Steps (64 steps)

### Phase 0. Read Planner Rules

Read current governance documents to ensure up-to-date context for infrastructure planning.

- 1. Read Rules/Planner/Planner_Rules.md to understand operational rules, scope boundaries, and best practices
- 2. Parse YAML frontmatter and rule definitions for implementation guidance
- 3. Store rule context for reference throughout workflow execution
- 4. **VALIDATION**: Validate that governance documents were read successfully and context is established
- 5. **STATUS TRACKING**: Update workflow status to "phase_0_complete"
- 6. **PRINT**: "Planner rules loaded from Rules/Planner/Planner_Rules.md"

---

### Phase 1. Select Execution Strategy

Select execution strategy appropriate for Planner agent type.

- 7. Select execution strategy appropriate for Planner agent type:
  - **Gate-Based Validation**: Standard gate validation with Round Table review loops
  - **Fast-Track Planning**: Simplified validation for simple planning tasks
  - **Iterative Planning**: Extended iteration loops for complex architectural changes
- 8. Store selected execution strategy for workflow behavior throughout planning process
- 9. **VALIDATION**: Validate that execution strategy was selected and stored successfully
- 10. **STATUS TRACKING**: Update workflow status to "phase_1_complete"
- 11. **PRINT**: "Execution strategy selected - {Strategy} will govern workflow behavior"

---

### Phase 2. Read Governance

Read current governance documents to ensure up-to-date context for infrastructure planning.

- 12. Read Workflow/Planner/Templates/Plan_Template.md to understand required plan structure and format
- 13. **VALIDATION**: Validate that governance documents were read successfully and context is established
- 14. **STATUS TRACKING**: Update workflow status to "phase_2_complete"
- 15. **PRINT**: "Plan template loaded from Workflow/Planner/Templates/Plan_Template.md"

---

### Phase 3. Plan Creation + Early Gate Validation

Create plan draft following Plan_Template.md format and run early gate validation to catch issues before review cycles.

- 16. Understand the user's request and what changes are needed for SovereignAI implementation
- 17. Assess the current system state and dependencies relevant to the planned changes
- 18. Create plan draft following Workflow/Planner/Templates/Plan_Template.md format exactly:
  - Required sections: Context, Steps, Dependencies
  - Metadata: Revision, Date, Goal
  - Planning language only (no implementation details)
  - Clear dependencies and execution order
- 19. Save plan draft to Plans/plan-{N}.{rev}.md with incrementing revision numbers
- 20. **STATUS TRACKING**: Update workflow status to "phase_3_in_progress" during plan creation
- 21. **PRINT**: "Creating plan draft - following template structure and format"
- 22. Run Planner gate system to validate plan structure and scope before review cycles:
```bash
bash Scripts/Planner/Gates/run-all-planner-gates.sh Plans/plan-{N}.{rev}.md phase3-early-validation
```
- 23. **VALIDATION**: Validate that plan creation completed successfully and early gates passed (see Workflow/Workflow_Reference/Gate_Enforcement_Patterns.md for universal pattern, see Workflow/Planner/Reference/Gate_Enforcement_System.md for Planner-specific gates)
- 24. **STATUS TRACKING**: Update workflow status to "phase_3_complete"
- 25. **PRINT**: "Plan creation complete - early gate validation passed, ready for internal review"

---

### Phase 4. Internal Round Table + Incremental Logging + Validate

Run internal Round Table review with domain-split panelists based on best practices for committee review patterns.

- 26. Create plan brief and review prompt for initial internal review using templates:
  - **Use Template**: Workflow/Planner/Plan_Brief_Template.md
  - **Brief Content**: Summarize context, goals, steps, dependencies, assign panelist personas
  - **Prompt Content**: Include explicit persona adoption instructions from Workflow/Planner/Plan_Prompt_Template.md
  - **Web Search Requirement**: Each panelist must use web search to verify findings against current best practices
  - **Persona Assignment**: Assign specific domain-split personas to each panelist
  - Save to: Logs/Roundtable/Devin/brief-rev1.md
- 27. Launch internal subagent panelists with domain-split personas (4-6 panelists based on plan complexity)
- 28. Collect panelist reviews with structured findings:
  - Each panelist must use web search to verify findings and current best practices
  - Each panelist provides findings with severity (CRITICAL, HIGH, MEDIUM, LOW)
  - Panelists rate plan quality on relevant dimensions (accuracy, completeness, clarity, structure, context)
  - Panelists provide specific improvement suggestions grounded in current research
  - Structured output format: {"verdict": "PASS|FAIL", "issues": [...], "notes": [...], "web_sources": [...]}
- 29. Save each panelist review incrementally as received to Logs/Roundtable/Devin/iteration-{N}-panelist-{M}.md
- 30. Aggregate all panelist findings and generate consolidated feedback:
  - Count findings by severity
  - Identify common themes and patterns
  - Generate improvement recommendations
  - Calculate quality scores across dimensions
- 31. **VALIDATION**: Validate that internal review completed successfully and findings were logged
- 32. **STATUS TRACKING**: Update workflow status to "phase_4_complete"
- 33. **PRINT**: "Internal Round Table complete - findings aggregated, ready for application"

---

### Phase 5. Apply Findings + Validate

Apply Round Table findings to improve plan quality and create new revision.

- 34. Review aggregated findings from internal or external Round Table:
  - CRITICAL findings: Must address before proceeding
  - HIGH findings: Must address before proceeding
  - MEDIUM findings: Address or document rationale
  - LOW findings: Consider for improvement
- 35. Apply findings to plan and create new revision:
  - Increment revision number (plan-{N}.{rev+1}.md)
  - Address CRITICAL and HIGH findings
  - Address or document MEDIUM findings
  - Consider LOW findings for improvement
  - Maintain plan structure and scope compliance
- 36. Run gate validation on revised plan to ensure changes maintain quality:
```bash
bash Scripts/Planner/Gates/run-all-planner-gates.sh Plans/plan-{N}.{rev+1}.md phase5-revision-validation
```
- 37. Log plan iteration with changes made to Logs/Planner/iteration-{N}-rev-{rev+1}.md
- 38. **VALIDATION**: Validate that findings were applied correctly and plan quality improved
- 39. **STATUS TRACKING**: Update workflow status to "phase_5_complete"
- 40. **PRINT**: "Findings applied - plan iteration logged, ready for next review iteration"

---

### Phase 6. External Round Table + Incremental Logging + Validate

Run external Round Table review with Chathub.gg panelists for final validation and broader perspective.

- 41. Create external review brief and prompt for Chathub.gg panelists using templates:
  - **Use Template**: Workflow/Planner/Plan_Brief_Template.md
  - **Brief Content**: Updated brief with internal iteration context, assign external panelist personas
  - **Prompt Content**: Include explicit persona adoption instructions from Workflow/Planner/Plan_Prompt_Template.md
  - **Web Search Requirement**: Each external panelist must use web search to verify findings against current best practices
  - **Persona Assignment**: Assign specific domain-split personas to each external panelist
  - Save to: Logs/Roundtable/External/brief-rev1.md
- 42. Launch external Chathub.gg panelists with domain-split personas (4-6 panelists based on plan complexity)
- 43. Collect external panelist reviews with structured findings:
  - Each panelist must use web search to verify findings and current best practices
  - Each panelist provides findings with severity (CRITICAL, HIGH, MEDIUM, LOW)
  - Panelists rate plan quality on relevant dimensions (accuracy, completeness, clarity, structure, context)
  - Panelists provide specific improvement suggestions grounded in current research
  - Panelists provide overall quality score (0-100)
  - Structured output format: {"verdict": "PASS|FAIL", "issues": [...], "notes": [...], "score": 0-100, "web_sources": [...]}
- 44. Save each external panelist review incrementally as received to Logs/Roundtable/External/round-{N}-panelist-{M}.md
- 45. Aggregate all external panelist findings and generate consolidated feedback:
  - Count findings by severity
  - Calculate average quality score
  - Identify common themes and patterns
  - Generate improvement recommendations
- 46. **VALIDATION**: Validate that external review completed successfully and findings were logged
- 47. **STATUS TRACKING**: Update workflow status to "phase_6_complete"
- 48. **PRINT**: "External Round Table complete - findings aggregated, ready for application"

---

### Phase 7. Final Gate Delivery + Validate

Run final Planner gate system validation before plan delivery for manual implementation.

- 49. Run full Planner gate system on final plan revision:
```bash
bash Scripts/Planner/Gates/run-all-planner-gates.sh Plans/plan-{N}.{final-rev}.md phase7-final-validation
```
- 50. Validate that all gates passed and gate completion hash was generated
- 51. Authorize plan delivery for manual implementation based on gate validation (see Workflow/Planner/Reference/Delivery_Authorization_Specifications.md)
- 52. **VALIDATION**: Validate that final gate validation completed successfully and delivery is authorized (see Workflow/Workflow_Reference/Gate_Enforcement_Patterns.md for universal pattern, see Workflow/Planner/Reference/Gate_Enforcement_System.md for Planner-specific gates)
- 53. **STATUS TRACKING**: Update workflow status to "phase_7_complete"
- 54. **PRINT**: "Final gate validation passed - delivery authorized, plan ready for manual implementation"

---

### Phase 8. Session Logging + Validate

Complete session logging with comprehensive audit trail and validate logging completeness.

- 55. Consolidate all plan iterations into session log to Logs/Planner/session-plan-{N}.md
- 56. Consolidate all Round Table reviews into session summary to Logs/Roundtable/session-roundtable-{N}.md
- 57. Consolidate all gate validation results to Logs/Planner/session-gates-{N}.md
- 58. Generate session attestation hash for verification from all session logs
- 59. **VALIDATION**: Validate that session logging completed successfully and audit trail is complete
- 60. **STATUS TRACKING**: Update workflow status to "phase_8_complete"
- 61. **PRINT**: "Session logging complete - audit trail validated, Planner workflow complete"

---

### Phase 10. Return to Phase 0

- 62. **PRINT** "Workflow cycle complete - returning to Phase 0 for next planning task"
- 63. **PRINT** "Planner agent ready - awaiting next user request"
- 64. Return to step 1

---

## Quality Hierarchy

Follow Quality > Token Cost > Efficiency hierarchy per PRINCIPLES.md when making trade-off decisions.

---

## Continuous Improvement

See Workflow/Planner/Reference/Role_Responsibilities.md for detailed continuous improvement processes and role responsibilities.

---

## Workflow Logging

See Workflow/Planner/Reference/Workflow_Overview.md for detailed logging structure and procedures.

---