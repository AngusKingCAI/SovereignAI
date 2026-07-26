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
- **Governance System**: Validation-based compliance enforcement

## Trigger and End State
- **Trigger**: User requests planning work or agent initiates task
- **End State**: Plan saved to Plans/ directory for executor execution with delivery authorization (workflow continues to next plan in batch sequence)

## Workflow Steps (64 steps)
### Phase 0. Read Planner Rules + Governance
- 1. Read Rules/Planner/Planner_Rules.md to understand operational rules, scope boundaries, and best practices
- 2. Read Workflow/Planner/Templates/Plan_Template.md to understand required plan structure and format
- 3. Read Workflow/Planner/Reference/Plan_Batch_Specifications.md to understand batch processing and scan plan patterns
- 4. Parse YAML frontmatter and rule definitions for implementation guidance
- 5. Store rule context, template structure, and batch specifications for reference throughout workflow execution
- 6. **STATUS TRACKING**: Update workflow status to "phase_0_complete"
- 7. **PRINT** "Planner rules, template, and batch specifications loaded"

### Phase 1. Select Execution Mode
- 8. Ask user to select execution mode for this workflow using popup menu:
  - **Manual**: Stop at failures for human oversight
  - **Auto**: Don't continue on failures (auto-stop on errors)
  - **Complete**: Continue past failures (ignore all errors)
- 9. Store selected execution mode for failure handling throughout workflow
- 10. **PRINT** "Execution mode selected - [Manual/Auto/Complete] will govern failure handling"

### Phase 2. Planner Interaction
- 11. Ask user: "Hi, Planner here - how can I help you today?"
- 12. Wait for user to specify their planning task or question
- 13. Clarify the task if needed
- 14. Review user request and check local research using index files before web search
- 15. Apply loaded planner rules to task requirements
- 16. **EXECUTION MODE HANDLING**: Apply execution mode handling patterns (see Workflow/Architect/Reference/Execution_Mode_Patterns.md)
- 17. **STATUS TRACKING**: Update workflow status to "phase_2_complete"
- 18. **PRINT** "Initiating planner interaction - awaiting user task specification"

### Phase 3. Plan Creation + Validate
- 19. Determine plan number and type (standard vs scan) per batch specifications
- 20. Understand the user's request and what changes are needed for SovereignAI implementation
- 21. For scan plans: Review previous plans in batch for issues requiring resolution
- 22. Assess the current system state and dependencies relevant to the planned changes
- 23. Create plan draft following Workflow/Planner/Templates/Plan_Template.md format exactly:
  - Required sections: Context, Steps, Dependencies
  - Metadata: Revision, Date, Goal, Plan Number, Plan Type
  - Planning language only (no implementation details)
  - Clear dependencies and execution order
- 24. Save plan draft to Plans/plan-{N}.{rev}.md with incrementing revision numbers
- 25. **STATUS TRACKING**: Update workflow status to "phase_3_in_progress" during plan creation
- 26. **PRINT** "Creating plan draft - following template structure and format"
- 27. **VALIDATION**: Validate that plan creation completed successfully and follows template structure (see Workflow/Workflow_Reference/Validation_Enforcement_Patterns.md for universal pattern, see Workflow/Workflow_Reference/Runtime_Prerequisites.md for validation system status)
- 28. **STATUS TRACKING**: Update workflow status to "phase_3_complete"
- 29. **PRINT**: "Plan creation complete - ready for internal review"

### Phase 4. Internal Round Table + Validate (Convergence Loop)
- 30. Create plan brief and review prompt for initial internal review using templates
- 31. Run internal Round Table review with domain-split panelists (see Workflow/Workflow_Reference/Quota_Handling_Patterns.md for quota exhaustion handling)
- 32. Log panelist reviews incrementally as received in Logs/Roundtable/Devin/
- 33. **CONVERGENCE CHECK**: Check if all panelists chose PASS
  - If ALL PASS → Proceed to Phase 6 (External Round Table)
  - If ANY FAIL → Proceed to Phase 5 (Apply Findings)
- 34. **QUOTA HANDLING**: If quota exhausted during panelist execution, use state persistence + resume pattern
- 35. **STATUS TRACKING**: Update workflow status to "phase_4_complete"
- 36. **PRINT**: "Internal Round Table complete - convergence status: [PASS/CONTINUE]"

### Phase 5. Apply Findings + Validate (Loop Back)
- 37. Review aggregated findings from internal or external Round Table
- 38. Apply findings to plan and create new revision
- 39. Validate revised plan structure and quality
- 40. Log plan iteration with changes made to Logs/Planner/
- 41. **LOOP BACK**: Return to Phase 4 (Internal Round Table) for next iteration
- 42. **LOOP CAP**: Maximum 5 internal iterations (then escalate to user)
- 43. **STATUS TRACKING**: Update workflow status to "phase_5_complete"
- 44. **PRINT**: "Findings applied - plan iteration logged, returning to Phase 4 for next Round Table iteration"

### Phase 6. External Round Table + Validate (Convergence Loop)
- 45. Create external review brief and prompt for Chathub.gg panelists (see Workflow/Workflow_Reference/Quota_Handling_Patterns.md for quota exhaustion handling)
- 46. Run external Round Table review with Chathub.gg panelists
- 47. Log external panelist reviews incrementally as received in Logs/Roundtable/External/
- 48. Aggregate external panelist findings and generate consolidated feedback
- 49. **CONVERGENCE CHECK**: Check if all panelists chose PASS (≥90 score or 70-89 with rationale)
  - If ALL PASS → Proceed to Phase 7 (Final Validation)
  - If ANY FAIL (<70 score) → Proceed to Phase 5 (Apply Findings)
- 50. **LOOP CAP**: Maximum 3 external iterations (then escalate to user)
- 51. **STATUS TRACKING**: Update workflow status to "phase_6_complete"
- 52. **PRINT**: "External Round Table complete - convergence status: [PASS/CONTINUE]"

### Phase 7. Final Validation + Delivery Authorization
- 53. Validate final plan structure and quality
- 54. Save final plan to Plans/ directory for executor execution
- 55. Authorize plan delivery for manual implementation based on validation
- 56. **VALIDATION**: Validate that final validation completed successfully and delivery is authorized (see Workflow/Workflow_Reference/Validation_Enforcement_Patterns.md for universal pattern, see Workflow/Workflow_Reference/Runtime_Prerequisites.md for validation system status)
- 57. **STATUS TRACKING**: Update workflow status to "phase_7_complete"
- 58. **PRINT**: "Final validation passed - plan saved to Plans/ directory, delivery authorized for executor execution"

### Phase 8. Session Logging + Validate
- 59. Consolidate all plan iterations into session log to Logs/Planner/
- 60. Consolidate all Round Table reviews into session summary to Logs/Roundtable/
- 61. Generate session attestation hash for verification from all session logs
- 62. **VALIDATION**: Validate that session logging completed successfully and audit trail is complete
- 63. **STATUS TRACKING**: Update workflow status to "phase_8_complete"
- 64. **PRINT**: "Session logging complete - audit trail validated, Planner workflow complete"

---

## Universal Framework References

### Quality Assessment
- **Universal Framework**: Workflow/Workflow_Reference/Quality_Assessment_Framework.md
- **Planner Customization**: Planner-specific plan quality criteria
- **Focus**: Plan quality assessment with planning-specific criteria

### Role Responsibilities
- **Universal Framework**: Workflow/Workflow_Reference/Role_Responsibilities_Framework.md
- **Planner Customization**: Planner-specific role definitions for plan creation
- **Focus**: Plan creation, dependency analysis, quality assessment

### Performance Metrics
- **Universal Framework**: Workflow/Workflow_Reference/Performance_Metrics_Framework.md
- **Planner Customization**: Planning efficiency, plan quality rate, convergence speed
- **Focus**: Planning efficiency metrics and quality assessment

### State Management
- **Universal Framework**: Workflow/Workflow_Reference/State_Management_Guidelines.md
- **Planner Customization**: Round Table iteration state, convergence metrics tracking
- **Focus**: Convergence loops, validation results, plan revision tracking

### Execution Strategy
- **Universal Framework**: Workflow/Workflow_Reference/Execution_Strategy_Guidelines.md
- **Planner Customization**: Validation-based planning, Round Table review loops
- **Focus**: Planning strategies and convergence-based iteration

### Quota Handling
- **Universal Framework**: Workflow/Workflow_Reference/Quota_Handling_Patterns.md
- **Planner Customization**: External agent preference, quota planning for subagents
- **Focus**: Current practice and future implementation plans
- **Note**: Quota handling patterns are design documents only, not yet implemented

### Plan Batch Processing
- **Planner Specifications**: Workflow/Planner/Reference/Plan_Batch_Specifications.md
- **Planner Customization**: Batch execution patterns and scan plan categorization
- **Focus**: Plan numbering, scan plan logic, and batch processing workflow

### Runtime Prerequisites
- **Universal Framework**: Workflow/Workflow_Reference/Runtime_Prerequisites.md
- **Planner Customization**: Validation system status and runtime directory requirements
- **Focus**: Runtime paths and infrastructure requirements for workflow execution

### Workflow Template
- **Architect Tool**: Workflow/Architect/Reference/Workflow_Template.md
- **Planner Customization**: Planner follows Architect's template for workflow structure
- **Focus**: Template compliance and workflow standardization