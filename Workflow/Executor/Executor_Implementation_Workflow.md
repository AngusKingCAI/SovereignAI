---
id: wf-exec-impl-cycle
status: active
owner: executor-agent
updated: 2026-07-28
purpose: Systematic plan execution ensuring implementation follows best practices and maintains compliance with governance rules
---

# Executor Implementation Workflow

**ID**: WF-EXEC-001  
**Owner**: Executor Agent  
**Frequency**: Per plan execution  
**Duration**: Variable (plan-dependent)  
**Priority**: High
**Workflow Type**: Single-Execution
**Execution Modes**: Manual, Auto, Complete

## Purpose
Systematic plan execution ensuring implementation follows best practices and maintains compliance with governance rules, with structured handoff to Reviewer agent for verification.

## Roles and Owners
- **Executor Agent**: Executes workflow steps, enforces governance rules
- **User**: Provides plan and task requirements
- **Governance System**: Automatic enforcement via validation system

## Trigger and End State
- **Trigger**: Plan provided by Planner agent
- **End State**: Plan execution complete, structured handoff to Reviewer agent prepared

## Workflow Steps (77 steps)

### Phase 0. Read Executor Rules
- 1. Read Rules/Executor/Executor_Rules.md to load current governance constraints
- 2. Read PRINCIPLES.md to understand constitutional framework and architectural principles
- 3. Read Workflow/Workflow_Reference/Terminology_Glossary.md to understand terminology definitions
- 4. Parse YAML frontmatter and rule definitions for implementation guidance
- 5. Store rule context for reference throughout workflow execution
- 6. **STATUS TRACKING**: Update workflow status to "phase_0_complete"
- 7. **PRINT** "Executor rules, constitutional principles, and terminology definitions loaded"

### Phase 1. Select Execution Mode
- 1. Ask user to select execution mode for this workflow using popup menu (see Workflow/Workflow_Reference/Execution_Mode_Patterns.md for execution mode definitions)
- 2. Store selected execution mode for failure handling throughout workflow
- 3. **PRINT** "Execution mode selected - [Manual/Auto/Complete] will govern failure handling"

### Phase 2. Executor Interaction
- 1. Ask user: "Hi, Executor here - how can I help you today?"
- 2. Wait for user to specify their task (provide plan)
- 3. Clarify the task if needed
- 4. Apply loaded executor rules to task requirements
- 5. **EXECUTION MODE HANDLING**: Apply execution mode handling patterns (see Workflow/Workflow_Reference/Execution_Mode_Patterns.md)
- 6. **STATUS TRACKING**: Update workflow status to "phase_2_complete"
- 7. **PRINT** "Initiating executor interaction - awaiting user task specification"

### Phase 3. Plan Execution Research
- 1. Review the plan provided by Planner agent
- 2. Check code documentation (Docs/Code/) for implementation examples relevant to plan steps
- 3. Research execution patterns for the specific plan (if needed for complex steps)
- 4. Ensure plan execution approach complies with governance rules
- 5. **EXECUTION MODE HANDLING**: Apply execution mode handling patterns (see Workflow/Workflow_Reference/Execution_Mode_Patterns.md)
- 6. **STATUS TRACKING**: Update workflow status to "phase_3_complete"
- 7. **PRINT** "Reviewing plan from Planner - checking for implementation requirements"
- 8. **PRINT** "Researching execution patterns for plan steps - checking code documentation for relevant examples"
- 9. **PRINT** "Plan execution research complete - ready to begin implementation"

### Phase 4. Executor Work Phase (Loop per plan step)
- 1. Execute single step from plan (not big picture planning)
- 2. **CRITICAL REQUIREMENT**: Before any file creation or modification, perform **{BP}** web search for current best practices relevant to the specific function or file being created/modified
- 3. **CRITICAL REQUIREMENT**: Document BP research findings and apply relevant best practices to the implementation
- 4. Build one function at a time, test immediately
- 5. **CRITICAL REQUIREMENT**: Before test file creation, perform **{BP}** web search for current testing best practices relevant to the specific function being tested
- 6. Create test file in Scripts/Tests/{Relevant SovereignAI app section}/{Test File Name}
- 7. Run quality checks in optimal order:
  - 1. ruff format (formatting)
  - 2. ruff check (linting + security via S rules)
  - 3. mypy (type checking)
  - 4. bandit (security scanning - optional)
  - 5. pytest (run tests)
- 8. Present function, test results, quality check output, and BP research findings after each successful execution
- 9. Wait for user confirmation before proceeding to next step
- 10. When function fails, apply selected execution mode (see Workflow/Workflow_Reference/Execution_Mode_Patterns.md)
- 11. **STATUS TRACKING**: Update workflow status to "phase_4_in_progress" during implementation, "phase_4_complete" when finished
- 12. **PRINT**: "Performing **{BP}** web search for current best practices before file creation/modification"
- 13. **PRINT**: "Implementing function - building one function at a time per executor rules with BP compliance"
- 14. **PRINT**: "Performing **{BP}** web search for current testing best practices before test file creation"
- 15. **PRINT**: "Function test complete - presenting test results and BP research findings to user for confirmation"
- 16. **PRINT**: "Awaiting user confirmation - treating function as locked once confirmed"
- 17. **PRINT**: "Function implementation complete - proceeding to next function"
- 18. **PRINT**: "Executor work phase complete - step executed with optimal quality check pipeline and BP compliance"

### Phase 5. Executor Validation Phase (Loop per plan step)
- 1. Verify implementation matches intended scope for the specific work
- 2. Ensure compliance with executor governance rules and BP research findings
- 3. Verify integration with broader system (if applicable)
- 4. Confirm plan step completion against acceptance criteria
- 5. **VALIDATION**: Validate that work completed successfully (see Workflow/Workflow_Reference/Validation_Enforcement_Patterns.md for universal pattern)
- 6. **STATUS TRACKING**: Update workflow status to "phase_5_complete" (when all plan steps done)
- 7. **PRINT**: "Executor validation complete - work verified for compliance, scope, and BP best practice adherence"

### Phase 6. Executor Documentation Phase (Loop per plan step)
- 1. Update relevant governance files and documentation for the completed plan step
- 2. Update progress tracking for plan completion status
- 3. Document BP research findings applied to implementation
- 4. **EXECUTION MODE HANDLING**: Apply execution mode handling patterns (see Workflow/Workflow_Reference/Execution_Mode_Patterns.md)
- 5. **LOOP DECISION**: If more plan steps remain → Return to step 25 with next step
- 6. **STATUS TRACKING**: Update workflow status to "phase_6_complete" (when all plan steps done)
- 7. **PRINT**: "Documentation complete - governance files updated for current plan step with BP research documentation"

### Phase 7. Final Validation
- 1. Verify all plan steps completed successfully
- 2. Verify overall implementation matches intended scope
- 3. Ensure compliance with all rules and constraints across entire plan
- 4. Verify BP research was conducted and applied for all file creation/modification operations
- 5. Verify integration of all plan steps with broader system
- 6. **VALIDATION**: Validate that final validation completed successfully (see Workflow/Workflow_Reference/Validation_Enforcement_Patterns.md for universal pattern)
- 7. **EXECUTION MODE HANDLING**: Apply execution mode handling patterns (see Workflow/Workflow_Reference/Execution_Mode_Patterns.md)
- 8. **STATUS TRACKING**: Update workflow status to "phase_7_complete"
- 9. **PRINT**: "Final validation complete - entire plan verified for compliance and BP best practice adherence"

### Phase 8. Agent Handoff
- 1. Create structured handoff file in Logs/Executor/Handoff/{Plan Name}/handoff.md following Workflow/Executor/Templates/Handoff_Template.md
- 2. Handoff file includes required fields as per template:
  - Trigger: Plan execution complete
  - Source: Executor agent
  - Target: Reviewer agent
  - Context payload: Plan summary, execution results, key decisions, files changed, BP research findings
  - Acceptance criteria: Review for compliance, scope, quality, and BP adherence
  - Session log reference: Specific path to Logs/Executor/Session/{Session ID}/ for this execution
- 3. **VALIDATION**: Validate that handoff file was created successfully (see Workflow/Workflow_Reference/Validation_Enforcement_Patterns.md for universal pattern)
- 4. **HANDOFF VALIDATION**: Verify handoff file integrity per Workflow/Executor/Templates/Handoff_Template.md:
  - Check file exists at correct path: Logs/Executor/Handoff/{Plan Name}/handoff.md
  - Verify file is readable and not corrupted
  - Validate all required fields are present (Trigger, Source, Target, Context payload, Acceptance criteria, Session log reference)
  - Verify context payload contains all required components (Plan summary, execution results, key decisions, files changed, BP research findings)
  - Validate session log reference path exists and is accessible
- 5. **VALIDATION**: Validate that handoff validation completed successfully
- 6. **EXECUTION MODE HANDLING**: Apply execution mode handling patterns (see Workflow/Workflow_Reference/Execution_Mode_Patterns.md)
- 7. **STATUS TRACKING**: Update workflow status to "phase_8_complete"
- 8. **PRINT**: "Executor workflow complete - structured handoff to Reviewer agent prepared in Logs/Executor/Handoff/{Plan Name}/ with reference to session log Logs/Executor/Session/{Session ID}/"
- 9. **PRINT**: "Handoff validation complete - file integrity verified, all required fields present including BP research findings, session log reference accessible"
- 10. **TERMINATE**: End workflow execution (do not return to step 1)

---

## Universal Framework References

### Quality Assessment
- **Universal Framework**: Workflow/Workflow_Reference/Quality_Assessment_Framework.md
- **Executor Customization**: Executor-specific quality criteria for plan execution
- **Focus**: Quality assessment with executor-specific criteria

### Role Responsibilities
- **Universal Framework**: Workflow/Workflow_Reference/Role_Responsibilities_Framework.md
- **Executor Customization**: Executor-specific role definitions for plan execution
- **Focus**: Plan execution, quality checks, compliance enforcement

### Performance Metrics
- **Universal Framework**: Workflow/Workflow_Reference/Performance_Metrics_Framework.md
- **Executor Customization**: Executor-specific performance metrics
- **Focus**: Execution efficiency, compliance rate, quality check results

### State Management
- **Universal Framework**: Workflow/Workflow_Reference/State_Management_Guidelines.md
- **Executor Customization**: Executor-specific state tracking
- **Focus**: Plan execution progress tracking and execution mode state

### Execution Strategy
- **Universal Framework**: Workflow/Workflow_Reference/Execution_Strategy_Guidelines.md
- **Executor Customization**: Executor-specific execution patterns
- **Focus**: Plan execution strategies and quality check integration

### Implementation Mode Patterns
- **Universal Framework**: Workflow/Workflow_Reference/Implementation_Mode_Patterns.md
- **Executor Customization**: Workflow/Executor/Reference/Implementation_Mode_Patterns.md
- **Focus**: Implementation mode selection (Automated vs Manual) for plan execution

### Runtime Prerequisites
- **Universal Framework**: Workflow/Workflow_Reference/Runtime_Prerequisites.md
- **Executor Customization**: Executor-specific runtime requirements
- **Focus**: Runtime paths and infrastructure requirements for workflow execution

### Validation Enforcement
- **Universal Framework**: Workflow/Workflow_Reference/Validation_Enforcement_Patterns.md
- **Executor Customization**: Executor-specific validation patterns
- **Focus**: Quality check validation and compliance verification

### Template Usage
- **Universal Framework**: Workflow/Workflow_Reference/Template_Usage_Guidelines.md
- **Executor Customization**: Workflow/Executor/Templates/Handoff_Template.md
- **Focus**: Structured handoff file creation for Reviewer agent transfer

## File Placement Compliance
- Create Workflow/Executor/ directory if it doesn't exist
- Place workflow file in Workflow/Executor/Executor_Implementation_Workflow.md
- Create Templates/ subdirectory for Executor-specific templates (including Handoff_Template.md)
- Create Reference/ subdirectory for Executor-specific reference files
- Follow naming convention: {Agent}_{WorkflowType}_Workflow.md
- Check INDEX.md for folder structure compliance