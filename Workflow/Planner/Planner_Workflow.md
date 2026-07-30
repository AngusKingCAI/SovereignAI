---
id: wf-plan-unified
status: active
owner: planner-agent
updated: 2026-07-30
purpose: Unified Planner workflow for both standard planning and scan-based plan creation with comprehensive analysis and validation
---

# Planner Unified Workflow

**ID**: WF-PLAN-UNIFIED  
**Owner**: Planner Agent  
**Frequency**: Per planning task  
**Duration**: Variable (task-dependent)  
**Priority**: High
**Workflow Type**: Single-Execution (both Plan Mode and Scan Mode)
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
- **End State**: Plan(s) saved to Plans/ directory for executor execution with delivery authorization, workflow terminates

## Workflow Steps (11 phases: Phase 0-11)

### Phase 0. Load Governance Rules
- 0.1. **OPEN** WorkflowOpen skill to dynamically load agent-specific rules based on current agent type
- 0.2. **STATUS TRACKING**: Update workflow status to "phase_0_in_progress"
- 0.3. **PRINT** "Governance rules loaded dynamically based on agent type"
- 0.4. **VALIDATION**: Validate that governance rules loaded successfully before proceeding to Phase 1
- 0.5. **STATUS TRACKING**: Update workflow status to "phase_0_complete"

### Phase 1. Select Planning Mode
- 1.1. **STATUS TRACKING**: Update workflow status to "phase_1_in_progress"
- 1.2. Ask user to select planning mode using popup menu:
  - **Plan Mode**: Standard planning from user requests with external Round Table review, single-execution workflow
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
- 4.6. **VALIDATION**: Validate that input processing completed successfully before proceeding to Phase 5A
- 4.7. **STATUS TRACKING**: Update workflow status to "phase_4a_complete"
- 4.8. Proceed to Phase 5A (Plan Creation - Plan Mode)

### Phase 4B. Scan Mode Input Processing (Scan Mode Only)
- 4.1. **STATUS TRACKING**: Update workflow status to "phase_4b_in_progress"
- 4.2. Process input source (user provides scan logs in chat to fix issues)
- 4.3. Assess current system state and dependencies relevant to planned changes
- 4.4. **EXECUTION MODE HANDLING**: Apply execution mode handling patterns per Workflow/Workflow_Reference/Execution_Mode_Patterns.md
- 4.5. **PRINT**: "Scan logs analyzed - proceeding with plan creation"
- 4.6. **VALIDATION**: Validate that input processing completed successfully before proceeding to Phase 5B
- 4.7. **STATUS TRACKING**: Update workflow status to "phase_4b_complete"
- 4.8. Proceed to Phase 5B (Plan Creation - Scan Mode)

### Phase 5A. Plan Creation - Plan Mode
- 5.1. **STATUS TRACKING**: Update workflow status to "phase_5a_in_progress"
- 5.2. Determine plan numbers and types for batch per Workflow/Planner/Reference/Plan_Batch_Specifications.md
- 5.3. Create plan files following Plan Template structure (see Workflow/Planner/Templates/Plan_Template.md)
- 5.4. Save plan drafts to Plans/Queued/plan-{N}.{rev}.md with incrementing revision numbers
- 5.5. **IF Revision > 1**: **DELETE** older plan revision files (Plans/Queued/plan-{N}.Rev{N-1}.md, Plans/Queued/plan-{N}.Rev{N-2}.md, etc.) immediately after new revision creation; IF Revision == 1: skip deletion (no older files exist)
- 5.6. **VALIDATION**: Validate that plan creation completed successfully and follows template structure
- 5.7. **STATUS TRACKING**: Update workflow status to "phase_5a_complete"
- 5.8. **PRINT**: "Plan creation complete - ready for review material creation"
- 5.9. Proceed to Phase 6A (Review Material Creation - Plan Mode)

### Phase 5B. Plan Creation - Scan Mode
- 5.1. **STATUS TRACKING**: Update workflow status to "phase_5b_in_progress"
- 5.2. Determine plan number and type per Workflow/Planner/Reference/Plan_Batch_Specifications.md
- 5.3. Create plan file following Plan Template structure (see Workflow/Planner/Templates/Plan_Template.md)
- 5.4. Save plan draft to Plans/Queued/plan-{N}.{rev}.md with incrementing revision numbers
- 5.5. **IF Revision > 1**: **DELETE** older plan revision files (Plans/Queued/plan-{N}.Rev{N-1}.md, Plans/Queued/plan-{N}.Rev{N-2}.md, etc.) immediately after new revision creation; IF Revision == 1: skip deletion (no older files exist)
- 5.6. **VALIDATION**: Validate that plan creation completed successfully and follows template structure
- 5.7. **STATUS TRACKING**: Update workflow status to "phase_5b_complete"
- 5.8. **PRINT**: "Plan creation complete - ready for review material creation"
- 5.9. Proceed to Phase 6B (Review Material Creation - Scan Mode)

### Phase 6A. Review Material Creation - Plan Mode
- 6.1. **STATUS TRACKING**: Update workflow status to "phase_6a_in_progress"
- 6.2. Create review materials following Batch_Brief_Template.md and Batch_Prompt_Template.md (save as Plans/Queued/Plan-Batch-{N}-{N}-Brief.md and Plans/Queued/Plan-Batch-{N}-{N}-Prompt.md)
- 6.3. **IF Revision > 1**: **DELETE** older batch prompt file (Plans/Queued/Plan-Batch-{N}-{N}-Prompt.md) immediately after new version creation; IF Revision == 1: skip deletion (no older files exist)
- 6.4. **VALIDATION**: Validate that review materials were created successfully and follow template structure
- 6.5. **STATUS TRACKING**: Update workflow status to "phase_6a_complete"
- 6.6. **PRINT**: "Review materials complete - ready for Internal Round Table"
- 6.7. Proceed to Phase 7A (Internal Round Table - Plan Mode)

### Phase 6B. Review Material Creation - Scan Mode
- 6.1. **STATUS TRACKING**: Update workflow status to "phase_6b_in_progress"
- 6.2. Create review materials following Plan_Brief_Template.md and Plan_Prompt_Template.md (save as Plans/Queued/Plan-{N}-Brief.md and Plans/Queued/Plan-{N}-Prompt.md)
- 6.3. **IF Revision > 1**: **DELETE** older plan prompt file (Plans/Queued/Plan-{N}-Prompt.md) immediately after new version creation; IF Revision == 1: skip deletion (no older files exist)
- 6.4. **VALIDATION**: Validate that review materials were created successfully and follow template structure
- 6.5. **STATUS TRACKING**: Update workflow status to "phase_6b_complete"
- 6.6. **PRINT**: "Review materials complete - ready for Internal Round Table"
- 6.7. Proceed to Phase 7B (Internal Round Table - Scan Mode)

### Phase 7A. Internal Round Table Execution - Plan Mode
- 7.1. **STATUS TRACKING**: Update workflow status to "phase_7a_in_progress"
- 7.2. Identify batch of plans from Plans/Queued/ directory for parallel processing per Workflow/Planner/Reference/Plan_Batch_Specifications.md
- 7.3. **LAUNCH SUB AGENTS IN PARALLEL**: Launch internal panelist sub agents per Plan_Prompt_Template.md persona definitions using run_subagent tool with profile "subagent_general" (all panelists launched once per batch, not per plan)
- 7.4. Send each plan file along with consolidated batch brief and batch prompt to corresponding sub agents
- 7.5. Each sub agent reviews their assigned plan using their assigned persona and websearch to verify assumptions, research best practices, and validate architectural decisions, returning structured JSON review
- 7.6. Wait for all sub agents to complete their reviews and return results
- 7.7. Log panelist reviews to consolidated file Logs/Planner/Round Table/Internal/Batch{N}-{N}_Roundtable.md (append per revision, separated by {Agent_Persona}) and verify logging completed successfully for the batch
- 7.8. **CONVERGENCE CHECK**: Check if all panelists chose PASS per Workflow/Workflow_Reference/Quality_Assessment_Framework.md
  - **IF ALL PASS**: Proceed to Phase 9 (External Round Table - Plan Mode)
  - **IF ANY FAIL**: Proceed to Phase 8A (Apply Findings - Plan Mode)
- 7.9. **QUOTA AWARENESS**: Monitor internal subagent quota usage per Workflow/Workflow_Reference/Quota_Handling_Patterns.md
- 7.10. **VALIDATION**: Validate that internal Round Table completed successfully and convergence check passed
- 7.11. **PRINT**: "Internal Round Table complete - convergence status: [PASS/CONTINUE]"
- 7.12. **STATUS TRACKING**: Update workflow status to "phase_7a_complete"

### Phase 7B. Internal Round Table Execution - Scan Mode
- 7.1. **STATUS TRACKING**: Update workflow status to "phase_7b_in_progress"
- 7.2. **LAUNCH SUB AGENTS IN PARALLEL**: Launch internal panelist sub agents per Plan_Prompt_Template.md persona definitions using run_subagent tool with profile "subagent_general"
- 7.3. Send plan file, brief file, and prompt file to corresponding sub agents
- 7.4. Each sub agent reviews their assigned plan using their assigned persona and websearch to verify assumptions, research best practices, and validate architectural decisions, returning structured JSON review
- 7.5. Wait for all sub agents to complete their reviews and return results
- 7.6. Log panelist reviews to consolidated file Logs/Planner/Round Table/Internal/Plan{N}_Roundtable.md (append per revision, separated by {Agent_Persona}) and verify logging completed successfully
- 7.7. **CONVERGENCE CHECK**: Check if all panelists chose PASS per Workflow/Workflow_Reference/Quality_Assessment_Framework.md
  - **IF ALL PASS**: Proceed to Phase 10 (Final Validation)
  - **IF ANY FAIL**: Proceed to Phase 8B (Apply Findings - Scan Mode)
- 7.8. **QUOTA AWARENESS**: Monitor internal subagent quota usage per Workflow/Workflow_Reference/Quota_Handling_Patterns.md
- 7.9. **VALIDATION**: Validate that internal Round Table completed successfully and convergence check passed
- 7.10. **PRINT**: "Internal Round Table complete - convergence status: [PASS/CONTINUE]"
- 7.11. **STATUS TRACKING**: Update workflow status to "phase_7b_complete"

### Phase 8A. Apply Findings + Loop Back - Plan Mode
- 8.1. **STATUS TRACKING**: Update workflow status to "phase_8a_in_progress"
- 8.2. Review aggregated findings from internal or external Round Table
- 8.3. **IF FINDINGS EXIST**: Apply findings to plans and create new revisions (rev 2, rev 3, etc.)
- 8.4. **IF FINDINGS EXIST**: Save new plan revisions to Plans/Queued/directory (older revisions deleted per Phase 5A step 5.5)
- 8.5. **IF FINDINGS EXIST**: Validate revised plan structures and quality
- 8.6. **IF FINDINGS EXIST**: Create new review materials following Batch_Brief_Template.md and Batch_Prompt_Template.md for the revised batch (save as Plans/Queued/Plan-Batch-{N}-{N}-Brief.md and Plans/Queued/Plan-Batch-{N}-{N}-Prompt.md)
- 8.7. **IF FINDINGS EXIST**: **LOOP BACK**: Return to Phase 6A (Review Material Creation - Plan Mode) for next iteration with same panelist sub agents
- 8.8. **VALIDATION**: Validate that findings were applied correctly and plan revisions are valid (if revisions were created)
- 8.9. **PRINT**: "Findings applied - revisions saved, returning to Phase 6A for next Round Table iteration"
- 8.10. **STATUS TRACKING**: Update workflow status to "phase_8a_complete"

### Phase 8B. Apply Findings + Loop Back - Scan Mode
- 8.1. **STATUS TRACKING**: Update workflow status to "phase_8b_in_progress"
- 8.2. Review aggregated findings from internal Round Table
- 8.3. **IF FINDINGS EXIST**: Apply findings to plans and create new revisions (rev 2, rev 3, etc.)
- 8.4. **IF FINDINGS EXIST**: Save new plan revisions to Plans/Queued/directory (older revisions deleted per Phase 5B step 5.5)
- 8.5. **IF FINDINGS EXIST**: Validate revised plan structures and quality
- 8.6. **IF FINDINGS EXIST**: Create new review materials following Plan_Brief_Template.md and Plan_Prompt_Template.md for the revised plan (save as Plans/Queued/Plan-{N}-Brief.md and Plans/Queued/Plan-{N}-Prompt.md)
- 8.7. **IF FINDINGS EXIST**: **LOOP BACK**: Return to Phase 6B (Review Material Creation - Scan Mode) for next iteration with same panelist sub agents
- 8.8. **VALIDATION**: Validate that findings were applied correctly and plan revisions are valid (if revisions were created)
- 8.9. **PRINT**: "Findings applied - revisions saved, returning to Phase 6B for next Round Table iteration"
- 8.10. **STATUS TRACKING**: Update workflow status to "phase_8b_complete"

### Phase 9. External Round Table Execution - Plan Mode Only
- 9.1. **STATUS TRACKING**: Update workflow status to "phase_9_in_progress"
- 9.2. **PRINT**: "External Round Table prompt ready for manual Chathub.gg review - awaiting user to post prompt and provide external panelist replies"
- 9.3. **WAIT** for user to manually post the external review prompt to Chathub.gg panelists and provide the replies
- 9.4. **USER POSTS REVIEWS**: User posts external panelist reviews back in chat as structured JSON reviews from each external agent with their assigned persona
- 9.5. Log external panelist reviews to consolidated file Logs/Planner/Round Table/External/Batch{N}-{N}_Roundtable.md (append per revision, separated by Agent_Name_{Agent_Persona}) and verify logging completed successfully
- 9.6. Aggregate external panelist findings and generate consolidated feedback
- 9.7. **CONVERGENCE CHECK**: Check if all panelists chose PASS per Workflow/Workflow_Reference/Quality_Assessment_Framework.md
  - **IF ALL PASS**: Proceed to Phase 10 (Final Validation)
  - **IF ANY FAIL**: Proceed to Phase 8A (Apply Findings - Plan Mode)
- 9.8. **VALIDATION**: Validate that external Round Table completed successfully and convergence check passed
- 9.9. **PRINT**: "External Round Table complete - convergence status: [PASS/CONTINUE]"
- 9.10. **STATUS TRACKING**: Update workflow status to "phase_9_complete"

### Phase 10. Final Validation + Delivery Authorization
- 10.1. **STATUS TRACKING**: Update workflow status to "phase_10_in_progress"
- 10.2. Validate final plan structure and quality per Plan Template.md and validation requirements
- 10.3. Authorize plan delivery for implementation based on validation
- 10.4. **VALIDATION**: Validate that final validation completed successfully and delivery is authorized
- 10.5. **PRINT**: "Final validation complete - delivery authorized for executor execution"
- 10.6. **STATUS TRACKING**: Update workflow status to "phase_10_complete"

### Phase 11. Workflow Termination
- 11.1. **STATUS TRACKING**: Update workflow status to "phase_11_in_progress"
- 11.2. **PRINT** "Planner workflow execution complete - workflow terminated"
- 11.3. **PRINT** "Plan(s) available in Plans/Queued/ directory for implementation"
- 11.4. **VALIDATION**: Validate that workflow completed successfully before termination
- 11.5. **TERMINATE**: End workflow execution (do not return to Phase 0)
- 11.6. **STATUS TRACKING**: Update workflow status to "phase_11_complete"

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

**Last Updated**: 2026-07-30
**Version**: 4.8 (Fixed file naming patterns, logging locations, deletion logic, and step references for logical consistency between Plan Mode and Scan Mode workflows)
**Maintained By**: Architect Agent

## Phase Structure Overview

- **Phase 0**: Load Governance Rules
- **Phase 1**: Select Planning Mode
- **Phase 2**: Select Execution Mode (references Execution_Mode_Patterns.md)
- **Phase 3**: Planner Interaction (references Execution_Mode_Patterns.md)
- **Phase 4A**: Plan Mode Input Processing (references Execution_Mode_Patterns.md)
- **Phase 4B**: Scan Mode Input Processing (references Execution_Mode_Patterns.md)
- **Phase 5A**: Plan Creation - Plan Mode (references Plan_Template.md, Plan_Batch_Specifications.md)
- **Phase 5B**: Plan Creation - Scan Mode (references Plan_Template.md, Plan_Batch_Specifications.md)
- **Phase 6A**: Review Material Creation - Plan Mode (references batch templates)
- **Phase 6B**: Review Material Creation - Scan Mode (references single plan templates)
- **Phase 7A**: Internal Round Table Execution - Plan Mode (references Plan_Prompt_Template.md, Quality_Assessment_Framework.md, Quota_Handling_Patterns.md, Plan_Batch_Specifications.md)
- **Phase 7B**: Internal Round Table Execution - Scan Mode (references Plan_Prompt_Template.md, Quality_Assessment_Framework.md, Quota_Handling_Patterns.md)
- **Phase 8A**: Apply Findings + Loop Back - Plan Mode (references templates for revisions)
- **Phase 8B**: Apply Findings + Loop Back - Scan Mode (references templates for revisions)
- **Phase 9**: External Round Table Execution - Plan Mode Only (references Plan_Prompt_Template.md, Quality_Assessment_Framework.md)
- **Phase 10**: Final Validation + Delivery Authorization (shared phase, references Plan_Template.md)
- **Phase 11**: Workflow Termination