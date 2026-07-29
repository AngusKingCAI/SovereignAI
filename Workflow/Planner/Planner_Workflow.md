---
id: wf-plan-unified
status: active
owner: planner-agent
updated: 2026-07-29
purpose: Unified Planner workflow for both standard planning and scan-based plan creation with comprehensive analysis and validation
---

# Planner Unified Workflow

**ID**: WF-PLAN-UNIFIED  
**Owner**: Planner Agent  
**Frequency**: Per planning task  
**Duration**: Variable (task-dependent)  
**Priority**: High
**Workflow Type**: Continuous Operation (Plan Mode always batch) - Single-Execution (Scan Mode)
**Execution Modes**: Manual, Automatic

## Purpose
Unified workflow for creating detailed, implementation-ready plans for AI-driven software development with comprehensive analysis and validation. Supports both standard planning (with external Round Table review, using documentation to implement new functionality) and scan-based plan creation (using scan logs to fix issues) through mode selection in Phase 1.

## Roles and Owners
- **Planner Agent**: Executes workflow steps, enforces governance rules
- **User**: Provides task requirements, approves decisions, provides documentation to implement new functionality (Plan Mode) or scan logs to fix issues (Scan Mode)
- **Governance System**: Validation-based compliance enforcement

## Trigger and End State
- **Trigger**: User requests planning work and provides documentation to implement new functionality (Plan Mode) or provides scan logs to fix issues (Scan Mode)
- **End State**: 
  - **Plan Mode**: Plan saved to Plans/ directory for executor execution with delivery authorization, returns to Phase 0 for next plan (always batch operation)
  - **Scan Mode**: Plan saved to Plans/ directory for implementation, workflow terminates

## Workflow Steps (102 steps)

### Phase 0. Load Governance Rules
- 0.1. **OPEN** WorkflowOpen skill to dynamically load agent-specific rules based on current agent type
- 0.2. **STATUS TRACKING**: Update workflow status to "phase_0_complete"
- 0.3. **PRINT** "Governance rules loaded dynamically based on agent type"
- 0.4. **VALIDATION**: Validate that governance rules loaded successfully before proceeding to Phase 1 (see Workflow/Workflow_Reference/Validation_Enforcement_Patterns.md for universal pattern)

### Phase 1. Select Planning Mode
- 1.1. Ask user to select planning mode using popup menu:
  - **Plan Mode**: Standard planning from user requests with external Round Table review, continuous batch operation (always returns to Phase 0 after each plan)
  - **Scan Mode**: Plan creation from existing governance scan results (user provides logs in chat), internal Round Table only, single-execution
- 1.2. Store selected planning mode for workflow structure throughout workflow
- 1.3. **PRINT** "Planning mode selected - [Plan Mode/Scan Mode] will govern workflow structure and review process"
- 1.4. **VALIDATION**: Validate that planning mode was selected and stored correctly before proceeding to Phase 2 (see Workflow/Workflow_Reference/Validation_Enforcement_Patterns.md for universal pattern)

### Phase 2. Select Execution Mode
- 2.1. Ask user to select execution mode for this workflow using popup menu (see Workflow/Workflow_Reference/Execution_Mode_Patterns.md for execution mode definitions):
  - **Manual**: Complete user oversight - user maintains full control and intervention throughout the entire workflow process
  - **Automatic**: Process automatically without user confirmation, but stop at failures and ask user what to do
- 2.2. Store selected execution mode for failure handling throughout workflow
- 2.3. **PRINT** "Execution mode selected - [Manual/Automatic] will govern failure handling"
- 2.4. **VALIDATION**: Validate that execution mode was selected and stored correctly before proceeding to Phase 3 (see Workflow/Workflow_Reference/Validation_Enforcement_Patterns.md for universal pattern)

### Phase 3. Planner Interaction
- 3.1. Ask user: "Hi, Planner here - how can I help you today?"
- 3.2. Wait for user to specify their planning task or question (or provide scan results for Scan Mode)
- 3.3. Clarify the task if needed
- 3.4. Review user request and check local research using index files before web search
- 3.5. Apply loaded planner rules to task requirements
- 3.6. **EXECUTION MODE HANDLING**: Apply execution mode handling patterns (see Workflow/Workflow_Reference/Execution_Mode_Patterns.md)
- 3.7. **STATUS TRACKING**: Update workflow status to "phase_3_complete"
- 3.8. **PRINT**: "Initiating planner interaction - awaiting user task specification"
- 3.9. **VALIDATION**: Validate that user provided valid input/task specification before proceeding to Phase 4 (see Workflow/Workflow_Reference/Validation_Enforcement_Patterns.md for universal pattern)
- 3.10. **IF Plan Mode**: Proceed to Phase 4A (Plan Mode Input Processing)
- 3.11. **IF Scan Mode**: Proceed to Phase 4B (Scan Mode Input Processing)

### Phase 4A. Plan Mode Input Processing (Plan Mode Only)
- 4.1. Process input source (user provides documentation files in chat to implement new functionality)
- 4.2. Assess current system state and dependencies relevant to planned changes
- 4.3. **EXECUTION MODE HANDLING**: Apply execution mode handling patterns (see Workflow/Workflow_Reference/Execution_Mode_Patterns.md)
- 4.4. **STATUS TRACKING**: Update workflow status to "phase_4a_complete"
- 4.5. **PRINT**: "Documentation analyzed - proceeding with plan creation"
- 4.6. **VALIDATION**: Validate that input processing completed successfully before proceeding to Phase 5 (see Workflow/Workflow_Reference/Validation_Enforcement_Patterns.md for universal pattern)
- 4.7. Proceed to Phase 5 (Plan Creation)

### Phase 4B. Scan Mode Input Processing (Scan Mode Only)
- 4.1. Process input source (user provides scan logs in chat to fix issues)
- 4.2. Assess current system state and dependencies relevant to planned changes
- 4.3. **EXECUTION MODE HANDLING**: Apply execution mode handling patterns (see Workflow/Workflow_Reference/Execution_Mode_Patterns.md)
- 4.4. **STATUS TRACKING**: Update workflow status to "phase_4b_complete"
- 4.5. **PRINT**: "Scan logs analyzed - proceeding with plan creation"
- 4.6. **VALIDATION**: Validate that input processing completed successfully before proceeding to Phase 5 (see Workflow/Workflow_Reference/Validation_Enforcement_Patterns.md for universal pattern)
- 4.7. Proceed to Phase 5 (Plan Creation)

### Phase 5. Plan Creation
- 5.1. Determine plan number and type (standard vs scan) per batch specifications
- 5.2. Create plan file following Plan Template structure (header lines, execution steps):
  - Header lines: Depends on, Vision principles, Open questions resolved
  - Plan body: Execution steps for implementation (note: Executor should perform websearch before implementation for best practices verification)
- 5.3. Save plan draft to Plans/Queued/plan-{N}.{rev}.md with incrementing revision numbers
- 5.4. **IF Revision > 1**: Remove previous plan revision file
- 5.5. Create plan brief for Round Table review and save as Plans/Queued/plan-{N}.{rev}_Brief.md:
  - Cross-plan dependency map
  - Sequencing risks  
  - Author's confidence by plan
  - Named open questions
  - Vision principle compliance
- 5.6. Create review prompt for Round Table review and save as Plans/Queued/plan-{N}.{rev}_Prompt.md
- 5.7. **STATUS TRACKING**: Update workflow status to "phase_5_in_progress" during plan creation
- 5.8. **PRINT** "Creating plan file following template structure"
- 5.9. **VALIDATION**: Validate that plan creation completed successfully and follows template structure (see Workflow/Workflow_Reference/Validation_Enforcement_Patterns.md for universal pattern, see Workflow/Workflow_Reference/Runtime_Prerequisites.md for validation system status)
- 5.10. **STATUS TRACKING**: Update workflow status to "phase_5_complete"
- 5.11. **PRINT**: "Plan creation complete - ready for internal review"

### Phase 6. Internal Round Table + Validate (Convergence Loop)
- 6.1. Identify batch of up to 4 plans from Plans/Queued/ directory for parallel processing
- 6.2. Create plan briefs and review prompts for all plans in batch using templates (includes persona presentation instructions for proper logging)
- 6.3. **LAUNCH SUB AGENTS IN PARALLEL**: Launch separate sub agents simultaneously for each internal panelist persona (Security Expert, Infrastructure Expert, Data Architecture Expert, Application Architecture Expert, Operations/DevOps Expert, Business Alignment Expert) for EACH plan in batch using run_subagent tool with profile "subagent_general" (all agents for all plans launched in parallel, not sequentially)
- 6.4. Send each plan file (Plans/Queued/plan-{N}.{rev}.md), brief file (Plans/Queued/plan-{N}.{rev}_Brief.md), and prompt file (Plans/Queued/plan-{N}.{rev}_Prompt.md) to corresponding sub agents with their assigned persona
- 6.5. Each sub agent reviews their assigned plan using their assigned persona and websearch to verify assumptions, research best practices, and validate architectural decisions, returning structured JSON review
- 6.6. Wait for all sub agents across all plans in batch to complete their reviews and return results
- 6.7. Log panelist reviews for all plans in batch to consolidated files Logs/Planner/Round Table/Internal/Plan{N}_Roundtable.md (append per revision, separated by {Agent_Persona}) and verify logging completed successfully for all plans
- 6.8. **CONVERGENCE CHECK**: Check if all panelists for all plans in batch chose PASS (≥4.5 score or 3.5-4.4 with rationale per Quality_Assessment_Framework.md)
  - **IF ALL PASS AND Plan Mode**: Proceed to Phase 8 (External Round Table) for all plans in batch
  - **IF ALL PASS AND Scan Mode**: Proceed to Phase 9 (Final Validation) for all plans in batch
  - **IF ANY FAIL**: Proceed to Phase 7 (Apply Findings) for failed plans
- 6.9. **QUOTA AWARENESS**: Monitor internal subagent quota usage and track step progress for recovery if needed (see Workflow/Workflow_Reference/Quota_Handling_Patterns.md)
- 6.10. **VALIDATION**: Validate that internal Round Table completed successfully and convergence check passed for all plans in batch (see Workflow/Workflow_Reference/Validation_Enforcement_Patterns.md for universal pattern)
- 6.11. **STATUS TRACKING**: Update workflow status to "phase_6_complete"
- 6.12. **PRINT**: "Internal Round Table complete for batch - convergence status: [PASS/CONTINUE] for each plan"

### Phase 7. Apply Findings + Validate (Loop Back)
- 7.1. Review aggregated findings from internal or external Round Table
- 7.2. **IF FINDINGS EXIST**: Apply findings to plan and create new revision (rev 2, rev 3, etc.)
- 7.3. **IF FINDINGS EXIST**: Validate revised plan structure and quality
- 7.4. **IF FINDINGS EXIST**: Save new plan revision to Plans/Queued/ directory (remove previous revision per workflow step 5.4)
- 7.5. **IF FINDINGS EXIST**: Create new brief and prompt for the revised plan (Plans/Queued/plan-{N}.{rev}_Brief.md and Plans/Queued/plan-{N}.{rev}_Prompt.md)
- 7.6. **IF FINDINGS EXIST**: **LOOP BACK**: Return to Phase 6 (Internal Round Table) for next iteration with same panelist sub agents
- 7.7. **LOOP CAP**: Maximum 5 internal iterations (then escalate to user)
- 7.8. **VALIDATION**: Validate that findings were applied correctly and plan revision is valid (if revision was created) (see Workflow/Workflow_Reference/Validation_Enforcement_Patterns.md for universal pattern)
- 7.9. **STATUS TRACKING**: Update workflow status to "phase_7_complete"
- 7.10. **PRINT**: "Findings applied - plan revision saved, returning to Phase 6 for next Round Table iteration"

### Phase 8. External Round Table + Validate (Plan Mode Only)
- 8.1. Create external review brief and prompt for Chathub.gg panelists (includes model name + persona presentation instructions for proper logging) (external agents not subject to quota limitations)
- 8.2. **USER PROVIDES FILES**: User provides plan file (Plans/Queued/plan-{N}.{rev}.md), brief file (Plans/Queued/plan-{N}.{rev}_Brief.md), and prompt file (Plans/Queued/plan-{N}.{rev}_Prompt.md) to external Chathub.gg panelists (6 different models with assigned personas: Security Expert, Infrastructure Expert, Data Architecture Expert, Application Architecture Expert, Operations/DevOps Expert, Business Alignment Expert)
- 8.3. **USER POSTS REVIEWS**: User posts external panelist reviews back in chat as structured JSON reviews from each external agent with their assigned persona
- 8.4. Log external panelist reviews incrementally as received in Logs/Planner/Round Table/External/Plan{N}_Roundtable.md (append per revision, separated by Agent_Name_{Agent_Persona}) and verify logging completed successfully
- 8.5. Aggregate external panelist findings and generate consolidated feedback
- 8.6. **CONVERGENCE CHECK**: Check if all panelists chose PASS (≥4.5 score or 3.5-4.4 with rationale per Quality_Assessment_Framework.md)
  - **IF ALL PASS**: Proceed to Phase 9 (Final Validation)
  - **IF ANY FAIL**: Proceed to Phase 7 (Apply Findings)
- 8.7. **LOOP CAP**: Maximum 3 external iterations (then escalate to user)
- 8.8. **VALIDATION**: Validate that external Round Table completed successfully and convergence check passed (see Workflow/Workflow_Reference/Validation_Enforcement_Patterns.md for universal pattern)
- 8.9. **STATUS TRACKING**: Update workflow status to "phase_8_complete"
- 8.10. **PRINT**: "External Round Table complete - convergence status: [PASS/CONTINUE]"

### Phase 9. Final Validation + Delivery Authorization
- 9.1. Validate final plan structure and quality
- 9.2. **IF Scan Mode**: Ensure all scan findings are systematically processed and reflected in plan steps
- 9.3. **IF Scan Mode**: Check that recommendations are actionable and implementation-ready
- 9.4. **IF Scan Mode**: Verify plan structure compliance with authoritative Plan Template format (Context, Steps, Dependencies)
- 9.5. Save final plan to Plans/Queued/ directory for executor execution
- 9.6. **IF Plan Mode**: Authorize plan delivery for manual implementation based on validation
- 9.7. **VALIDATION**: Validate that final validation completed successfully and delivery is authorized (see Workflow/Workflow_Reference/Validation_Enforcement_Patterns.md for universal pattern, see Workflow/Workflow_Reference/Runtime_Prerequisites.md for validation system status)
- 9.8. **STATUS TRACKING**: Update workflow status to "phase_9_complete"
- 9.9. **IF Plan Mode**: **PRINT** "Final validation passed - plan saved to Plans/Queued/ directory, delivery authorized for executor execution"
- 9.10. **IF Scan Mode**: **PRINT** "Final validation complete - plan {N} ready for user review"

### Phase 10. Workflow Termination or Return (Mode-Dependent)
- 10.1. **IF Scan Mode**: **PRINT** "Planner Scan Mode workflow execution complete - workflow terminated"
- 10.2. **IF Scan Mode**: **PRINT** "Plan {N}-Rev1 available in Plans/Queued/ directory for implementation"
- 10.3. **IF Scan Mode**: **VALIDATION**: Validate that workflow completed successfully before termination (see Workflow/Workflow_Reference/Validation_Enforcement_Patterns.md for universal pattern)
- 10.4. **IF Scan Mode**: **TERMINATE**: End workflow execution (do not return to step 1)
- 10.5. **IF Plan Mode**: **PRINT** "Plan workflow complete - returning to Phase 0 for next planning task (batch operation)"
- 10.6. **IF Plan Mode**: **PRINT** "Planner agent ready - awaiting next planning request"
- 10.7. **IF Plan Mode**: **VALIDATION**: Validate that workflow completed successfully before returning to Phase 0 (see Workflow/Workflow_Reference/Validation_Enforcement_Patterns.md for universal pattern)
- 10.8. **IF Plan Mode**: Return to step 1

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

---

**Last Updated**: 2026-07-29
**Version**: 1.0 (Unified Planner workflow combining Plan and Scan modes)
**Maintained By**: Architect Agent