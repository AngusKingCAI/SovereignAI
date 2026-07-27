# Planner Plan Workflow

**ID**: WF-PLAN-001  
**Owner**: Planner Agent  
**Frequency**: Per planning task  
**Duration**: Variable (task-dependent)  
**Priority**: High
**Workflow Type**: Continuous Operation (Batch Mode) - Single Plan Mode also supported

## Purpose
Create detailed, implementation-ready plans for AI-driven software development with comprehensive analysis and validation, including internal and external Round Table review with incremental validation to ensure plan quality and completeness.

## Roles and Owners
- **Planner Agent**: Executes workflow steps, enforces governance rules
- **User**: Provides task requirements, approves decisions
- **Governance System**: Validation-based compliance enforcement

## Trigger and End State
- **Trigger**: User requests planning work or agent initiates task
- **End State**: Plan saved to Plans/ directory for executor execution with delivery authorization (Batch Mode: continues to next plan in sequence; Single Plan Mode: terminates after single plan)

## Workflow Steps (74 steps)
### Phase 0. Read Planner Rules + Governance
- 1. Read Rules/Planner/Planner_Rules.md to understand operational rules, scope boundaries, and best practices
- 2. Read Workflow/Workflow_Reference/Terminology_Glossary.md to understand terminology definitions
- 3. Read Workflow/Planner/Templates/Plan_Template.md to understand required plan structure and format
- 4. Read Workflow/Planner/Reference/Plan_Batch_Specifications.md to understand batch processing and scan plan patterns
- 5. Parse YAML frontmatter and rule definitions for implementation guidance
- 6. Store rule context, template structure, and batch specifications for reference throughout workflow execution
- 7. **STATUS TRACKING**: Update workflow status to "phase_0_complete"
- 8. **PRINT** "Planner rules, template, and batch specifications loaded"

### Phase 1. Select Execution Mode
- 8. Ask user to select execution mode for this workflow using popup menu (see Workflow/Workflow_Reference/Execution_Mode_Patterns.md for execution mode definitions)
- 9. Ask user to select workflow mode: Batch Mode (process plans sequentially, return to Phase 0 after each plan) or Single Plan Mode (process single plan and terminate)
- 10. Store selected execution mode and workflow mode for failure handling throughout workflow
- 11. **PRINT** "Execution mode selected - [Manual/Auto/Complete] will govern failure handling"
- 12. **PRINT** "Workflow mode selected - [Batch Mode/Single Plan Mode] will govern plan processing pattern"

### Phase 2. Planner Interaction
- 13. Ask user: "Hi, Planner here - how can I help you today?"
- 14. Wait for user to specify their planning task or question
- 15. Clarify the task if needed
- 16. Review user request and check local research using index files before web search
- 17. Apply loaded planner rules to task requirements
- 18. **EXECUTION MODE HANDLING**: Apply execution mode handling patterns (see Workflow/Workflow_Reference/Execution_Mode_Patterns.md)
- 19. **STATUS TRACKING**: Update workflow status to "phase_2_complete"
- 20. **PRINT** "Initiating planner interaction - awaiting user task specification"

### Phase 3. Plan Creation + Validate
- 21. Determine plan number and type (standard vs scan) per batch specifications
- 22. Understand the user's request and what changes are needed for SovereignAI implementation
- 23. For scan plans: Review previous plans in batch for issues requiring resolution
- 24. Assess the current system state and dependencies relevant to the planned changes
- 25. Create plan draft following Workflow/Planner/Templates/Plan_Template.md format exactly:
  - Required sections: Context, Steps, Dependencies
  - Metadata: Revision, Date, Goal, Plan Number, Plan Type
  - Planning language only (no implementation details)
  - Clear dependencies and execution order
- 26. Save plan draft to Plans/plan-{N}.{rev}.md with incrementing revision numbers
- 27. **STATUS TRACKING**: Update workflow status to "phase_3_in_progress" during plan creation
- 28. **PRINT** "Creating plan draft - following template structure and format"
- 29. **VALIDATION**: Validate that plan creation completed successfully and follows template structure (see Workflow/Workflow_Reference/Validation_Enforcement_Patterns.md for universal pattern, see Workflow/Workflow_Reference/Runtime_Prerequisites.md for validation system status)
- 30. **STATUS TRACKING**: Update workflow status to "phase_3_complete"
- 31. **PRINT**: "Plan creation complete - ready for internal review"

### Phase 4. Internal Round Table + Validate (Convergence Loop)
- 32. Create plan brief and review prompt for initial internal review using templates (includes persona presentation instructions for proper logging)
- 33. Run internal Round Table review with domain-split panelists (see Workflow/Workflow_Reference/Quota_Handling_Patterns.md for internal subagent quota tracking)
- 34. Log panelist reviews incrementally as received in Logs/Planner/Roundtable/Internal/plan{N}/{Agent_Persona}.md
- 35. **CONVERGENCE CHECK**: Check if all panelists chose PASS (≥4.5 score or 3.5-4.4 with rationale per Quality_Assessment_Framework.md)
  - If ALL PASS → Proceed to Phase 6 (External Round Table)
  - If ANY FAIL (<3.5 score) → Proceed to Phase 5 (Apply Findings)
- 36. **QUOTA AWARENESS**: Monitor internal subagent quota usage and track step progress for recovery if needed (see Workflow/Workflow_Reference/Quota_Handling_Patterns.md)
- 37. **STATUS TRACKING**: Update workflow status to "phase_4_complete"
- 38. **PRINT**: "Internal Round Table complete - convergence status: [PASS/CONTINUE]"

### Phase 5. Apply Findings + Validate (Loop Back)
- 39. Review aggregated findings from internal or external Round Table
- 40. Apply findings to plan and create new revision
- 41. Validate revised plan structure and quality
- 42. Save new plan revision to Plans/ directory (plan revision logging handled by plan creation step)
- 43. **LOOP BACK**: Return to Phase 4 (Internal Round Table) for next iteration
- 44. **LOOP CAP**: Maximum 5 internal iterations (then escalate to user)
- 45. **STATUS TRACKING**: Update workflow status to "phase_5_complete"
- 46. **PRINT**: "Findings applied - plan revision saved, returning to Phase 4 for next Round Table iteration"

### Phase 6. External Round Table + Validate (Convergence Loop)
- 48. Create external review brief and prompt for Chathub.gg panelists (includes model name + persona presentation instructions for proper logging) (external agents not subject to quota limitations)
- 49. Run external Round Table review with Chathub.gg panelists
- 50. Log external panelist reviews incrementally as received in Logs/Planner/Roundtable/External/plan{N}/{Agent_Name}_{Agent_Persona}.md
- 51. Aggregate external panelist findings and generate consolidated feedback
- 52. **CONVERGENCE CHECK**: Check if all panelists chose PASS (≥4.5 score or 3.5-4.4 with rationale per Quality_Assessment_Framework.md)
  - If ALL PASS → Proceed to Phase 7 (Final Validation)
  - If ANY FAIL (<3.5 score) → Proceed to Phase 5 (Apply Findings)
- 53. **LOOP CAP**: Maximum 3 external iterations (then escalate to user)
- 54. **STATUS TRACKING**: Update workflow status to "phase_6_complete"
- 55. **PRINT**: "External Round Table complete - convergence status: [PASS/CONTINUE]"

### Phase 7. Final Validation + Delivery Authorization
- 56. Validate final plan structure and quality
- 57. Save final plan to Plans/ directory for executor execution
- 58. Authorize plan delivery for manual implementation based on validation
- 59. **VALIDATION**: Validate that final validation completed successfully and delivery is authorized (see Workflow/Workflow_Reference/Validation_Enforcement_Patterns.md for universal pattern, see Workflow/Workflow_Reference/Runtime_Prerequisites.md for validation system status)
- 60. **STATUS TRACKING**: Update workflow status to "phase_7_complete"
- 61. **PRINT**: "Final validation passed - plan saved to Plans/ directory, delivery authorized for executor execution"

### Phase 8. Round Table Logging + Validate
- 62. Consolidate all Round Table reviews into plan-specific folders (manual logging - hooks do not log roundtable reviews)
- 63. Verify all internal reviews are in Logs/Planner/Roundtable/Internal/plan{N}/{Agent_Persona}.md
- 64. Verify all external reviews are in Logs/Planner/Roundtable/External/plan{N}/{Agent_Name}_{Agent_Persona}.md
- 65. **VALIDATION**: Validate that Round Table logging completed successfully and audit trail is complete
- 66. **STATUS TRACKING**: Update workflow status to "phase_8_complete"
- 67. **PRINT**: "Round Table logging complete - audit trail validated, Planner workflow complete"

### Phase 9. Return to Phase 0 (CONTINUOUS OPERATION)
- 68. **WORKFLOW MODE CHECK**: Check if workflow mode is Batch Mode or Single Plan Mode
  - If Batch Mode → Return to Phase 0 for next plan in sequence
  - If Single Plan Mode → Proceed to Phase 10 (Terminate)
- 69. **PRINT** "Plan workflow complete - returning to Phase 0 for next planning task (Batch Mode) or terminating (Single Plan Mode)"
- 70. **PRINT** "Planner agent ready - awaiting next planning request (Batch Mode) or terminating session (Single Plan Mode)"
- 71. Return to step 1

### Phase 10. Terminate (Single Plan Mode)
- 72. **PRINT** "Single Plan Mode - Planner workflow terminating after single plan completion"
- 73. **PRINT** "Plan saved to Plans/ directory with delivery authorization"
- 74. TERMINATE workflow (Single Plan Mode only - Batch Mode loops back to Phase 0)

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

### Validation Enforcement
- **Universal Framework**: Workflow/Workflow_Reference/Validation_Enforcement_Patterns.md
- **Planner Customization**: Plan validation patterns and convergence loop validation
- **Focus**: Plan structure validation and delivery authorization

### Convergence Loop Patterns
- **Universal Framework**: Workflow/Workflow_Reference/Convergence_Loop_Patterns.md
- **Planner Customization**: Round Table review convergence patterns
- **Focus**: Internal and external Round Table convergence loops

### Quota Handling
- **Universal Framework**: Workflow/Workflow_Reference/Quota_Handling_Patterns.md
- **Planner Customization**: Internal subagent quota tracking for Round Table reviews
- **Focus**: Basic quota awareness and step progress tracking for internal subagents

### Plan Batch Processing
- **Planner Specifications**: Workflow/Planner/Reference/Plan_Batch_Specifications.md
- **Planner Customization**: Batch execution patterns and scan plan categorization
- **Focus**: Plan numbering, scan plan logic, and batch processing workflow

### Runtime Prerequisites
- **Universal Framework**: Workflow/Workflow_Reference/Runtime_Prerequisites.md
- **Planner Customization**: Validation system status and runtime directory requirements
- **Focus**: Runtime paths and infrastructure requirements for workflow execution