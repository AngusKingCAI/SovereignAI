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
**Phase Structure**: 11 modular phases following KISS principles (one task/phase) with SSOT compliance

## Purpose
Unified workflow for creating detailed, implementation-ready plans for AI-driven software development with comprehensive analysis and validation. Supports both standard planning (with external Round Table review, using documentation to implement new functionality) and scan-based plan creation (using scan logs to fix issues) through mode selection in Phase 1.

## Reference Documents
- **Validation Patterns**: Workflow/Workflow_Reference/Validation_Enforcement_Patterns.md (universal validation patterns for all phases)
- **Execution Modes**: Workflow/Workflow_Reference/Execution_Mode_Patterns.md (execution mode definitions and handling)
- **Quality Assessment**: Workflow/Workflow_Reference/Quality_Assessment_Framework.md (quality scoring criteria and thresholds)
- **Batch Specifications**: Workflow/Planner/Reference/Plan_Batch_Specifications.md (batch processing patterns and plan numbering)
- **Quota Handling**: Workflow/Workflow_Reference/Quota_Handling_Patterns.md (internal subagent quota tracking)
- **Runtime Prerequisites**: Workflow/Workflow_Reference/Runtime_Prerequisites.md (validation system status and directory requirements)

## Roles and Owners
- **Planner Agent**: Executes workflow steps, enforces governance rules
- **User**: Provides task requirements, approves decisions, provides documentation to implement new functionality (Plan Mode) or scan logs to fix issues (Scan Mode)
- **Governance System**: Validation-based compliance enforcement

## Trigger and End State
- **Trigger**: User requests planning work and provides documentation to implement new functionality (Plan Mode) or provides scan logs to fix issues (Scan Mode)
- **End State**: 
  - **Plan Mode**: Plan saved to Plans/ directory for executor execution with delivery authorization, returns to Phase 0 for next plan (always batch operation)
  - **Scan Mode**: Plan saved to Plans/ directory for implementation, workflow terminates

## Workflow Steps (11 phases)

### Phase 0. Load Governance Rules
- 0.1. **OPEN** WorkflowOpen skill to dynamically load agent-specific rules based on current agent type
- 0.2. **STATUS TRACKING**: Update workflow status to "phase_0_in_progress"
- 0.3. **PRINT** "Governance rules loaded dynamically based on agent type"
- 0.4. **VALIDATION**: Validate that governance rules loaded successfully before proceeding to Phase 1
- 0.5. **STATUS TRACKING**: Update workflow status to "phase_0_complete"

### Phase 1. Select Planning Mode
- 1.1. **STATUS TRACKING**: Update workflow status to "phase_1_in_progress"
- 1.2. Ask user to select planning mode using popup menu:
  - **Plan Mode**: Standard planning from user requests with external Round Table review, continuous batch operation (always returns to Phase 0 after each plan)
  - **Scan Mode**: Plan creation from existing governance scan results (user provides logs in chat), internal Round Table only, single-execution
- 1.3. Store selected planning mode for workflow structure throughout workflow
- 1.4. **PRINT** "Planning mode selected - [Plan Mode/Scan Mode] will govern workflow structure and review process"
- 1.5. **VALIDATION**: Validate that planning mode was selected and stored correctly before proceeding to Phase 2
- 1.6. **STATUS TRACKING**: Update workflow status to "phase_1_complete"

### Phase 2. Select Execution Mode
- 2.1. **STATUS TRACKING**: Update workflow status to "phase_2_in_progress"
- 2.2. Ask user to select execution mode for this workflow using popup menu (see Workflow/Workflow_Reference/Execution_Mode_Patterns.md for execution mode definitions)
- 2.3. Store selected execution mode for failure handling throughout workflow
- 2.4. **PRINT** "Execution mode selected - [Manual/Automatic] will govern failure handling"
- 2.5. **VALIDATION**: Validate that execution mode was selected and stored correctly before proceeding to Phase 3
- 2.6. **STATUS TRACKING**: Update workflow status to "phase_2_complete"

### Phase 3. Planner Interaction
- 3.1. **STATUS TRACKING**: Update workflow status to "phase_3_in_progress"
- 3.2. Ask user: "Hi, Planner here - how can I help you today?"
- 3.3. Wait for user to specify their planning task or question (or provide scan results for Scan Mode)
- 3.4. Clarify the task if needed
- 3.5. Review user request and check local research using index files before web search
- 3.6. Apply loaded planner rules to task requirements
- 3.7. **EXECUTION MODE HANDLING**: Apply execution mode handling patterns per Workflow/Workflow_Reference/Execution_Mode_Patterns.md
- 3.8. **PRINT**: "Initiating planner interaction - awaiting user task specification"
- 3.9. **VALIDATION**: Validate that user provided valid input/task specification before proceeding to Phase 4
- 3.10. **STATUS TRACKING**: Update workflow status to "phase_3_complete"
- 3.11. **IF Plan Mode**: Proceed to Phase 4A (Plan Mode Input Processing)
- 3.12. **IF Scan Mode**: Proceed to Phase 4B (Scan Mode Input Processing)

### Phase 4A. Plan Mode Input Processing (Plan Mode Only)
- 4.1. **STATUS TRACKING**: Update workflow status to "phase_4a_in_progress"
- 4.2. Process input source (user provides documentation files in chat to implement new functionality)
- 4.3. Assess current system state and dependencies relevant to planned changes
- 4.4. **EXECUTION MODE HANDLING**: Apply execution mode handling patterns per Workflow/Workflow_Reference/Execution_Mode_Patterns.md
- 4.5. **PRINT**: "Documentation analyzed - proceeding with plan creation"
- 4.6. **VALIDATION**: Validate that input processing completed successfully before proceeding to Phase 5
- 4.7. **STATUS TRACKING**: Update workflow status to "phase_4a_complete"
- 4.8. Proceed to Phase 5 (Plan Creation)

### Phase 4B. Scan Mode Input Processing (Scan Mode Only)
- 4.1. **STATUS TRACKING**: Update workflow status to "phase_4b_in_progress"
- 4.2. Process input source (user provides scan logs in chat to fix issues)
- 4.3. Assess current system state and dependencies relevant to planned changes
- 4.4. **EXECUTION MODE HANDLING**: Apply execution mode handling patterns per Workflow/Workflow_Reference/Execution_Mode_Patterns.md
- 4.5. **PRINT**: "Scan logs analyzed - proceeding with plan creation"
- 4.6. **VALIDATION**: Validate that input processing completed successfully before proceeding to Phase 5
- 4.7. **STATUS TRACKING**: Update workflow status to "phase_4b_complete"
- 4.8. Proceed to Phase 5 (Plan Creation)

### Phase 5. Plan Creation
- 5.1. **STATUS TRACKING**: Update workflow status to "phase_5_in_progress"
- 5.2. Determine plan number and type (standard vs scan) per Workflow/Planner/Reference/Plan_Batch_Specifications.md
- 5.3. Create plan file following Plan Template structure (see Workflow/Planner/Templates/Plan_Template.md)
- 5.4. Save plan draft to Plans/Queued/plan-{N}.{rev}.md with incrementing revision numbers
- 5.5. **IF Revision > 1**: Remove previous plan revision file
- 5.6. **VALIDATION**: Validate that plan creation completed successfully and follows template structure
- 5.7. **STATUS TRACKING**: Update workflow status to "phase_5_complete"
- 5.8. **PRINT**: "Plan creation complete - ready for review material creation"

### Phase 6. Review Material Creation
- 6.1. **STATUS TRACKING**: Update workflow status to "phase_6_in_progress"
- 6.2. **IF processing batch of plans**: Create review materials following Batch_Brief_Template.md and Batch_Prompt_Template.md (save as Plans/Queued/Batch_Brief.md and Plans/Queued/Batch_Prompt.md)
- 6.3. **IF processing single plan**: Create review materials following Plan_Brief_Template.md and Plan_Prompt_Template.md (save as Plans/Queued/plan-{N}.{rev}_Brief.md and Plans/Queued/plan-{N}.{rev}_Prompt.md)
- 6.4. **VALIDATION**: Validate that review materials were created successfully and follow template structure
- 6.5. **STATUS TRACKING**: Update workflow status to "phase_6_complete"
- 6.6. **PRINT**: "Review materials complete - ready for Internal Round Table"

### Phase 7. Internal Round Table Execution
- 7.1. **STATUS TRACKING**: Update workflow status to "phase_7_in_progress"
- 7.2. **IF processing batch of plans**: Identify batch of plans from Plans/Queued/ directory for parallel processing per Workflow/Planner/Reference/Plan_Batch_Specifications.md
- 7.3. **IF processing batch of plans**: **LAUNCH SUB AGENTS IN PARALLEL**: Launch internal panelist sub agents per Plan_Prompt_Template.md persona definitions using run_subagent tool with profile "subagent_general" (all panelists launched once per batch, not per plan)
- 7.4. **IF processing batch of plans**: Send each plan file along with consolidated batch brief and batch prompt to corresponding sub agents
- 7.5. **IF processing single plan**: **LAUNCH SUB AGENTS IN PARALLEL**: Launch internal panelist sub agents per Plan_Prompt_Template.md persona definitions using run_subagent tool with profile "subagent_general"
- 7.6. **IF processing single plan**: Send plan file, brief file, and prompt file to corresponding sub agents
- 7.7. Each sub agent reviews their assigned plan using their assigned persona and websearch to verify assumptions, research best practices, and validate architectural decisions, returning structured JSON review
- 7.8. Wait for all sub agents to complete their reviews and return results
- 7.9. **IF processing batch of plans**: Log panelist reviews to consolidated file Logs/Planner/Round Table/Internal/Batch{N}_Roundtable.md (append per revision, separated by {Agent_Persona}) and verify logging completed successfully for the batch
- 7.10. **IF processing single plan**: Log panelist reviews to consolidated file Logs/Planner/Round Table/Internal/Plan{N}_Roundtable.md (append per revision, separated by {Agent_Persona}) and verify logging completed successfully
- 7.11. **CONVERGENCE CHECK**: Check if all panelists chose PASS per Workflow/Workflow_Reference/Quality_Assessment_Framework.md
  - **IF ALL PASS AND Plan Mode**: Proceed to Phase 9 (External Round Table)
  - **IF ALL PASS AND Scan Mode**: Proceed to Phase 10 (Final Validation)
  - **IF ANY FAIL**: Proceed to Phase 8 (Apply Findings)
- 7.12. **QUOTA AWARENESS**: Monitor internal subagent quota usage per Workflow/Workflow_Reference/Quota_Handling_Patterns.md
- 7.13. **VALIDATION**: Validate that internal Round Table completed successfully and convergence check passed
- 7.14. **PRINT**: "Internal Round Table complete - convergence status: [PASS/CONTINUE]"
- 7.15. **STATUS TRACKING**: Update workflow status to "phase_7_complete"

### Phase 8. Apply Findings + Loop Back
- 8.1. **STATUS TRACKING**: Update workflow status to "phase_8_in_progress"
- 8.2. Review aggregated findings from internal or external Round Table
- 8.3. **IF FINDINGS EXIST**: Apply findings to plans and create new revisions (rev 2, rev 3, etc.)
- 8.4. **IF FINDINGS EXIST**: Validate revised plan structures and quality
- 8.5. **IF FINDINGS EXIST**: Save new plan revisions to Plans/Queued/ directory (remove previous revisions per workflow step 5.5)
- 8.6. **IF FINDINGS EXIST AND processing batch of plans**: Create new review materials following Batch_Brief_Template.md and Batch_Prompt_Template.md for the revised batch
- 8.7. **IF FINDINGS EXIST AND processing single plan**: Create new review materials following Plan_Brief_Template.md and Plan_Prompt_Template.md for the revised plan
- 8.8. **IF FINDINGS EXIST**: **LOOP BACK**: Return to Phase 6 (Review Material Creation) for next iteration with same panelist sub agents
- 8.9. **VALIDATION**: Validate that findings were applied correctly and plan revisions are valid (if revisions were created)
- 8.10. **PRINT**: "Findings applied - revisions saved, returning to Phase 6 for next Round Table iteration"
- 8.11. **STATUS TRACKING**: Update workflow status to "phase_8_complete"

### Phase 9. External Round Table Execution (Plan Mode Only)
- 9.1. **STATUS TRACKING**: Update workflow status to "phase_9_in_progress"
- 9.2. **IF processing batch of plans**: **USER PROVIDES FILES**: User provides plan files along with existing consolidated batch brief and batch prompt from Phase 6 to external Chathub.gg panelists per Plan_Prompt_Template.md persona definitions
- 9.3. **IF processing single plan**: Create external review brief and prompt following Plan_Brief_Template.md and Plan_Prompt_Template.md (includes model name + persona presentation instructions for proper logging)
- 9.4. **IF processing single plan**: **USER PROVIDES FILES**: User provides plan file, brief file, and prompt file to external Chathub.gg panelists per Plan_Prompt_Template.md persona definitions
- 9.5. **USER POSTS REVIEWS**: User posts external panelist reviews back in chat as structured JSON reviews from each external agent with their assigned persona
- 9.6. **IF processing batch of plans**: Log external panelist reviews to consolidated file Logs/Planner/Round Table/External/Batch{N}_Roundtable.md (append per revision, separated by Agent_Name_{Agent_Persona}) and verify logging completed successfully
- 9.7. **IF processing single plan**: Log external panelist reviews to consolidated file Logs/Planner/Round Table/External/Plan{N}_Roundtable.md (append per revision, separated by Agent_Name_{Agent_Persona}) and verify logging completed successfully
- 9.8. Aggregate external panelist findings and generate consolidated feedback
- 9.9. **CONVERGENCE CHECK**: Check if all panelists chose PASS per Workflow/Workflow_Reference/Quality_Assessment_Framework.md
  - **IF ALL PASS**: Proceed to Phase 10 (Final Validation)
  - **IF ANY FAIL**: Proceed to Phase 8 (Apply Findings)
- 9.10. **VALIDATION**: Validate that external Round Table completed successfully and convergence check passed
- 9.11. **PRINT**: "External Round Table complete - convergence status: [PASS/CONTINUE]"
- 9.12. **STATUS TRACKING**: Update workflow status to "phase_9_complete"

### Phase 10. Final Validation + Delivery Authorization
- 10.1. **STATUS TRACKING**: Update workflow status to "phase_10_in_progress"
- 10.2. Validate final plan structure and quality per Plan Template.md and validation requirements
- 10.3. **IF Plan Mode**: Authorize plan delivery for manual implementation based on validation
- 10.4. **VALIDATION**: Validate that final validation completed successfully and delivery is authorized
- 10.5. **PRINT**: "Final validation complete - delivery authorized for executor execution"
- 10.6. **STATUS TRACKING**: Update workflow status to "phase_10_complete"

### Phase 11. Workflow Termination or Return (Mode-Dependent)
- 11.1. **STATUS TRACKING**: Update workflow status to "phase_11_in_progress"
- 11.2. **IF Scan Mode**: **PRINT** "Planner Scan Mode workflow execution complete - workflow terminated"
- 11.3. **IF Scan Mode**: **PRINT** "Plan {N}-Rev1 available in Plans/Queued/ directory for implementation"
- 11.4. **IF Scan Mode**: **VALIDATION**: Validate that workflow completed successfully before termination
- 11.5. **IF Scan Mode**: **TERMINATE**: End workflow execution (do not return to Phase 0)
- 11.6. **IF Plan Mode**: **PRINT** "Plan workflow complete - returning to Phase 0 for next planning task (batch operation)"
- 11.7. **IF Plan Mode**: **PRINT** "Planner agent ready - awaiting next planning request"
- 11.8. **IF Plan Mode**: **VALIDATION**: Validate that workflow completed successfully before returning to Phase 0
- 11.9. **IF Plan Mode**: Return to Phase 0 (Load Governance Rules)
- 11.10. **STATUS TRACKING**: Update workflow status to "phase_11_complete"

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
**Version**: 4.0 (SSOT-compliant with template and reference document simplification)
**Maintained By**: Architect Agent

## Phase Structure Overview

- **Phase 0**: Load Governance Rules
- **Phase 1**: Select Planning Mode
- **Phase 2**: Select Execution Mode (references Execution_Mode_Patterns.md)
- **Phase 3**: Planner Interaction (references Execution_Mode_Patterns.md)
- **Phase 4A**: Plan Mode Input Processing (references Execution_Mode_Patterns.md)
- **Phase 4B**: Scan Mode Input Processing (references Execution_Mode_Patterns.md)
- **Phase 5**: Plan Creation (references Plan_Template.md, Plan_Batch_Specifications.md)
- **Phase 6**: Review Material Creation (references batch/individual templates)
- **Phase 7**: Internal Round Table Execution (references Plan_Prompt_Template.md, Quality_Assessment_Framework.md, Quota_Handling_Patterns.md, Plan_Batch_Specifications.md)
- **Phase 8**: Apply Findings + Loop Back (references templates for revisions)
- **Phase 9**: External Round Table Execution (references Plan_Prompt_Template.md, Quality_Assessment_Framework.md)
- **Phase 10**: Final Validation + Delivery Authorization (references Plan_Template.md)
- **Phase 11**: Workflow Termination or Return (Mode-Dependent)