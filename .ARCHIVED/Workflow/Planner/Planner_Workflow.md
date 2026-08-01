---
id: wf-plan-unified
status: active
owner: planner-agent
updated: 2026-07-30
version: "1.0"
purpose: Unified Planner workflow for both standard planning and scan-based plan creation with comprehensive analysis and validation
expected_agent_type: planner-agent
persona:
  role: "Planning Specialist"
  expertise: "Plan creation, workflow orchestration, batch processing, review material generation, internal/external round table coordination, plan revision management"
  process: "Dual-mode workflow (plan mode and scan mode) with iterative review process, batch processing capabilities, and comprehensive validation"
  output: "Implementation-ready plans with delivery authorization, review materials, and comprehensive logging"
  constraints: "plan mode uses external round table, scan mode uses internal round table only, follows governance rules, maintains SSOT compliance"
---

# Planner Unified Workflow

**id**: WF-PLAN-UNIFIED  
**owner**: planner agent  
**frequency**: Per planning task  
**duration**: Variable (task-dependent)  
**priority**: High
**workflow type**: Single-Execution (both plan mode and scan mode)
**execution modes**: Manual, Automatic
**phase structure**: 11 modular phases following KISS principles (one task/phase) with SSOT compliance

## purpose
Unified workflow for creating detailed, implementation-ready plans for AI-driven software development with comprehensive analysis and validation. Supports both standard planning (with external round table review, using documentation to implement new functionality) and scan-based plan creation (using scan logs to fix issues) through mode selection in phase 1.

## reference documents
- **validation patterns**: Workflow/Workflow_Reference/Validation_Enforcement_Patterns.md (universal validation patterns for all phases)
- **execution modes**: Workflow/Workflow_Reference/Execution_Mode_Patterns.md (execution mode definitions and handling)
- **quality assessment**: Workflow/Workflow_Reference/Quality_Assessment_Framework.md (quality scoring criteria and thresholds)
- **batch specifications**: Workflow/Planner/Reference/Plan_Batch_Specifications.md (batch processing patterns and plan numbering)
- **quota handling**: Workflow/Workflow_Reference/Quota_Handling_Patterns.md (internal subagent quota tracking)
- **runtime prerequisites**: Workflow/Workflow_Reference/Runtime_Prerequisites.md (validation system status and directory requirements)

## roles and owners
- **planner agent**: Executes workflow steps, enforces governance rules
- **User**: Provides task requirements, approves decisions, provides documentation to implement new functionality (plan mode) or scan logs to fix issues (scan mode)
- **governance system**: Validation-based compliance enforcement

## trigger and end state
- **trigger**: User requests planning work and provides documentation to implement new functionality (plan mode) or provides scan logs to fix issues (scan mode)
- **end state**: Plan(s) saved to Plans/ directory for executor execution with delivery authorization, workflow terminates

## workflow steps (11 phases: Phase 0-11)

### Phase 0. Load Governance Rules
- 0.1. **OPEN** WorkflowOpen skill to dynamically load agent-specific rules based on current agent type
- 0.2. **STATUS TRACKING**: python Scripts/Logging/session_state.py Planner --workflow phase_0_in_progress
- 0.3. **PRINT** "Governance rules loaded dynamically based on agent type"
- 0.4. **VALIDATION**: Validate that governance rules loaded successfully before proceeding to Phase 1
- 0.5. **STATUS TRACKING**: python Scripts/Logging/session_state.py Planner --workflow phase_0_complete

### Phase 1. Select Planning Mode
- 1.1. **STATUS TRACKING**: python Scripts/Logging/session_state.py Planner --workflow phase_1_in_progress
- 1.2. Ask user to select planning mode using popup menu:
  - **plan mode**: Standard planning from user requests with external round table review, single-execution workflow
  - **scan mode**: Plan creation from existing governance scan results (user provides logs in chat), internal round table only, single-execution
- 1.3. Store selected planning mode for workflow structure throughout workflow
- 1.4. **PRINT** "Planning mode selected - [plan mode/scan mode] will govern workflow structure and review process"
- 1.5. **VALIDATION**: Validate that planning mode was selected and stored correctly before proceeding to Phase 2
- 1.6. **STATUS TRACKING**: python Scripts/Logging/session_state.py Planner --workflow phase_1_complete

### Phase 2. Select Execution Mode
- 2.1. **STATUS TRACKING**: python Scripts/Logging/session_state.py Planner --workflow phase_2_in_progress
- 2.2. Ask user to select execution mode for this workflow using popup menu (see Workflow/Workflow_Reference/Execution_Mode_Patterns.md for execution mode definitions)
- 2.3. Store selected execution mode for failure handling throughout workflow
- 2.4. **PRINT** "Execution mode selected - [Manual/Automatic] will govern failure handling"
- 2.5. **VALIDATION**: Validate that execution mode was selected and stored correctly before proceeding to Phase 3
- 2.6. **STATUS TRACKING**: python Scripts/Logging/session_state.py Planner --workflow phase_2_complete

### Phase 3. Planner Interaction
- 3.1. **STATUS TRACKING**: python Scripts/Logging/session_state.py Planner --workflow phase_3_in_progress
- 3.2. Ask user: "Hi, Planner here - how can I help you?"
- 3.3. Wait for user to specify their planning task or question (or provide scan results for scan mode)
- 3.4. Clarify the task if needed
- 3.5. Review user request and check local research using index files before web search
- 3.6. Apply loaded planner rules to task requirements
- 3.7. **EXECUTION MODE HANDLING**: Apply execution mode handling patterns per Workflow/Workflow_Reference/Execution_Mode_Patterns.md
- 3.8. **PRINT**: "Initiating planner interaction - awaiting user task specification"
- 3.9. **VALIDATION**: Validate that user provided valid input/task specification before proceeding to Phase 4
- 3.10. **STATUS TRACKING**: python Scripts/Logging/session_state.py Planner --workflow phase_3_complete
- 3.11. **if plan mode**: Proceed to phase 4A (plan mode Input Processing)
- 3.12. **if scan mode**: Proceed to phase 4B (scan mode Input Processing)

### Phase 4A. plan mode Input Processing (plan mode Only)
- 4.1. **STATUS TRACKING**: python Scripts/Logging/session_state.py Planner --workflow phase_4a_in_progress
- 4.2. Process input source (user provides documentation files in chat to implement new functionality)
- 4.3. Assess current system state and dependencies relevant to planned changes
- 4.4. **EXECUTION MODE HANDLING**: Apply execution mode handling patterns per Workflow/Workflow_Reference/Execution_Mode_Patterns.md
- 4.5. **PRINT**: "Documentation analyzed - proceeding with plan creation"
- 4.6. **VALIDATION**: Validate that input processing completed successfully before proceeding to Phase 5A
- 4.7. **STATUS TRACKING**: python Scripts/Logging/session_state.py Planner --workflow phase_4a_complete
- 4.8. Proceed to phase 5A (Plan Creation - plan mode)

### Phase 4B. scan mode Input Processing (scan mode Only)
- 4.1. **STATUS TRACKING**: python Scripts/Logging/session_state.py Planner --workflow phase_4b_in_progress
- 4.2. Process input source (user provides scan logs in chat to fix issues)
- 4.3. Assess current system state and dependencies relevant to planned changes
- 4.4. **EXECUTION MODE HANDLING**: Apply execution mode handling patterns per Workflow/Workflow_Reference/Execution_Mode_Patterns.md
- 4.5. **PRINT**: "Scan logs analyzed - proceeding with plan creation"
- 4.6. **VALIDATION**: Validate that input processing completed successfully before proceeding to Phase 5B
- 4.7. **STATUS TRACKING**: python Scripts/Logging/session_state.py Planner --workflow phase_4b_complete
- 4.8. Proceed to phase 5B (Plan Creation - scan mode)

### Phase 5A. Plan Creation - plan mode
- 5.1. **STATUS TRACKING**: python Scripts/Logging/session_state.py Planner --workflow phase_5a_in_progress
- 5.2. Determine plan numbers and types for batch per Workflow/Planner/Reference/Plan_Batch_Specifications.md
- 5.3. Create plan files following Plan Template structure (see Workflow/Planner/Templates/Plan_Template.md)
- 5.4. Save plan drafts to Plans/Queued/plan-{N}.{rev}.md with incrementing revision numbers
- 5.5. **if revision > 1**: **DELETE** older plan revision files (Plans/Queued/plan-{N}.Rev{N-1}.md, Plans/Queued/plan-{N}.Rev{N-2}.md, etc.) immediately after new revision creation; if revision == 1: skip deletion (no older files exist)
- 5.6. **VALIDATION**: Validate that plan creation completed successfully and follows template structure
- 5.7. **STATUS TRACKING**: python Scripts/Logging/session_state.py Planner --workflow phase_5a_complete
- 5.8. **PRINT**: "Plan creation complete - ready for review material creation"
- 5.9. Proceed to phase 6A (Review Material Creation - plan mode)

### Phase 5B. Plan Creation - scan mode
- 5.1. **STATUS TRACKING**: python Scripts/Logging/session_state.py Planner --workflow phase_5b_in_progress
- 5.2. Determine plan number and type per Workflow/Planner/Reference/Plan_Batch_Specifications.md
- 5.3. Create plan file following Plan Template structure (see Workflow/Planner/Templates/Plan_Template.md)
- 5.4. Save plan draft to Plans/Queued/plan-{N}.{rev}.md with incrementing revision numbers
- 5.5. **if revision > 1**: **DELETE** older plan revision files (Plans/Queued/plan-{N}.Rev{N-1}.md, Plans/Queued/plan-{N}.Rev{N-2}.md, etc.) immediately after new revision creation; if revision == 1: skip deletion (no older files exist)
- 5.6. **VALIDATION**: Validate that plan creation completed successfully and follows template structure
- 5.7. **STATUS TRACKING**: python Scripts/Logging/session_state.py Planner --workflow phase_5b_complete
- 5.8. **PRINT**: "Plan creation complete - ready for review material creation"
- 5.9. Proceed to phase 6B (Review Material Creation - scan mode)

### Phase 6A. Review Material Creation - plan mode (Internal Round Table)
- 6.1. **STATUS TRACKING**: python Scripts/Logging/session_state.py Planner --workflow phase_6a_in_progress
- 6.2. Create internal review materials following Batch_Brief_Template.md and Batch_Prompt_Template.md (save as Plans/Queued/Plan-Batch-{N}-{N}-Brief.md and Plans/Queued/Plan-Batch-{N}-{N}-Prompt.md)
- 6.3. **if revision > 1**: **DELETE** older batch prompt file (Plans/Queued/Plan-Batch-{N}-{N}-Prompt.md) immediately after new version creation; if revision == 1: skip deletion (no older files exist)
- 6.4. **VALIDATION**: Validate that internal review materials were created successfully and follow internal template structure
- 6.5. **STATUS TRACKING**: python Scripts/Logging/session_state.py Planner --workflow phase_6a_complete
- 6.6. **PRINT**: "Internal review materials complete - ready for Internal round table"
- 6.7. Proceed to phase 7A (Internal round table - plan mode)

### Phase 6B. Review Material Creation - scan mode
- 6.1. **STATUS TRACKING**: python Scripts/Logging/session_state.py Planner --workflow phase_6b_in_progress
- 6.2. Create review materials following Plan_Brief_Template.md and Plan_Prompt_Template.md (save as Plans/Queued/Plan-{N}-Brief.md and Plans/Queued/Plan-{N}-Prompt.md)
- 6.3. **if revision > 1**: **DELETE** older plan prompt file (Plans/Queued/Plan-{N}-Prompt.md) immediately after new version creation; if revision == 1: skip deletion (no older files exist)
- 6.4. **VALIDATION**: Validate that review materials were created successfully and follow template structure
- 6.5. **STATUS TRACKING**: python Scripts/Logging/session_state.py Planner --workflow phase_6b_complete
- 6.6. **PRINT**: "Review materials complete - ready for Internal round table"
- 6.7. Proceed to phase 7B (Internal round table - scan mode)

### Phase 7A. Internal round table Execution - plan mode
- 7.1. **STATUS TRACKING**: python Scripts/Logging/session_state.py Planner --workflow phase_7a_in_progress
- 7.2. Identify batch of plans from Plans/Queued/ directory for parallel processing per Workflow/Planner/Reference/Plan_Batch_Specifications.md
- 7.3. **launch sub agents in parallel**: Launch internal panelist sub agents per Batch_Prompt_Template.md persona definitions using run_subagent tool with profile "subagent_general" (all panelists launched once per batch, not per plan)
- 7.4. Send each plan file along with consolidated batch brief and batch prompt to corresponding sub agents
- 7.5. Each sub agent reviews their assigned plan using their assigned persona and websearch to verify assumptions, research best practices, and validate architectural decisions, returning structured JSON review
- 7.6. Wait for all sub agents to complete their reviews and return results
- 7.7. Log panelist reviews to consolidated file Logs/Planner/round table/Internal/Batch{N}-{N}_Roundtable.md (append per revision, separated by {Agent_Persona}) and verify logging completed successfully for the batch
- 7.8. **CONVERGENCE CHECK**: Check if all panelists chose PASS per Workflow/Workflow_Reference/Quality_Assessment_Framework.md
  - **if all pass**: Proceed to phase 9 (External round table - plan mode)
  - **if any fail**: Proceed to phase 8A (Apply Findings - plan mode)
- 7.9. **QUOTA AWARENESS**: Monitor internal subagent quota usage per Workflow/Workflow_Reference/Quota_Handling_Patterns.md
- 7.10. **VALIDATION**: Validate that internal round table completed successfully and convergence check passed
- 7.11. **PRINT**: "Internal round table complete - convergence status: [PASS/CONTINUE]"
- 7.12. **STATUS TRACKING**: python Scripts/Logging/session_state.py Planner --workflow phase_7a_complete

### Phase 7B. Internal round table Execution - scan mode
- 7.1. **STATUS TRACKING**: python Scripts/Logging/session_state.py Planner --workflow phase_7b_in_progress
- 7.2. **launch sub agents in parallel**: Launch internal panelist sub agents per Plan_Prompt_Template.md persona definitions using run_subagent tool with profile "subagent_general"
- 7.3. Send plan file, brief file, and prompt file to corresponding sub agents
- 7.4. Each sub agent reviews their assigned plan using their assigned persona and websearch to verify assumptions, research best practices, and validate architectural decisions, returning structured JSON review
- 7.5. Wait for all sub agents to complete their reviews and return results
- 7.6. Log panelist reviews to consolidated file Logs/Planner/round table/Internal/Plan{N}_Roundtable.md (append per revision, separated by {Agent_Persona}) and verify logging completed successfully
- 7.7. **CONVERGENCE CHECK**: Check if all panelists chose PASS per Workflow/Workflow_Reference/Quality_Assessment_Framework.md
  - **if all pass**: Proceed to phase 10 (Final Validation)
  - **if any fail**: Proceed to phase 8B (Apply Findings - scan mode)
- 7.8. **QUOTA AWARENESS**: Monitor internal subagent quota usage per Workflow/Workflow_Reference/Quota_Handling_Patterns.md
- 7.9. **VALIDATION**: Validate that internal round table completed successfully and convergence check passed
- 7.10. **PRINT**: "Internal round table complete - convergence status: [PASS/CONTINUE]"
- 7.11. **STATUS TRACKING**: python Scripts/Logging/session_state.py Planner --workflow phase_7b_complete

### Phase 8A. Apply Findings + Loop Back - plan mode
- 8.1. **STATUS TRACKING**: python Scripts/Logging/session_state.py Planner --workflow phase_8a_in_progress
- 8.2. Review aggregated findings from internal or external round table (handles both internal and external failures)
- 8.3. **if findings exist**: Apply findings to plans and create new revisions (rev 2, rev 3, etc.)
- 8.4. **if findings exist**: Save new plan revisions to Plans/Queued/directory (older revisions deleted per phase 5A step 5.5)
- 8.5. **if findings exist**: Validate revised plan structures and quality
- 8.6. **if findings exist**: Create new review materials following Batch_Brief_Template.md and Batch_Prompt_Template.md for the revised batch (save as Plans/Queued/Plan-Batch-{N}-{N}-Brief.md and Plans/Queued/Plan-Batch-{N}-{N}-Prompt.md)
- 8.7. **if findings exist**: **LOOP BACK**: Return to phase 6A (Review Material Creation - plan mode) for next iteration - Note: This loops back through internal round table (Phase 7A) to reach external round table (Phase 9) again, creating continuous loop until both internal and external round tables pass
- 8.8. **VALIDATION**: Validate that findings were applied correctly and plan revisions are valid (if revisions were created)
- 8.9. **PRINT**: "Findings applied - revisions saved, returning to phase 6A for next round table iteration"
- 8.10. **STATUS TRACKING**: python Scripts/Logging/session_state.py Planner --workflow phase_8a_complete

### Phase 8B. Apply Findings + Loop Back - scan mode
- 8.1. **STATUS TRACKING**: python Scripts/Logging/session_state.py Planner --workflow phase_8b_in_progress
- 8.2. Review aggregated findings from internal round table
- 8.3. **if findings exist**: Apply findings to plans and create new revisions (rev 2, rev 3, etc.)
- 8.4. **if findings exist**: Save new plan revisions to Plans/Queued/directory (older revisions deleted per phase 5B step 5.5)
- 8.5. **if findings exist**: Validate revised plan structures and quality
- 8.6. **if findings exist**: Create new review materials following Plan_Brief_Template.md and Plan_Prompt_Template.md for the revised plan (save as Plans/Queued/Plan-{N}-Brief.md and Plans/Queued/Plan-{N}-Prompt.md)
- 8.7. **if findings exist**: **LOOP BACK**: Return to phase 6B (Review Material Creation - scan mode) for next iteration with same panelist sub agents
- 8.8. **VALIDATION**: Validate that findings were applied correctly and plan revisions are valid (if revisions were created)
- 8.9. **PRINT**: "Findings applied - revisions saved, returning to phase 6B for next round table iteration"
- 8.10. **STATUS TRACKING**: python Scripts/Logging/session_state.py Planner --workflow phase_8b_complete

### Phase 9. External round table Execution - plan mode Only
- 9.1. **STATUS TRACKING**: python Scripts/Logging/session_state.py Planner --workflow phase_9_in_progress
- 9.2. **PRINT**: "External round table ready - create External_Batch-{N}-{N}-Brief.md and External_Batch-{N}-{N}-Prompt.md using External_Batch_*_Template.md for multi-perspective evaluation"
- 9.3. Create external review materials following External_Batch_Brief_Template.md and External_Batch_Prompt_Template.md (save as Plans/Queued/External_Batch-{N}-{N}-Brief.md and Plans/Queued/External_Batch-{N}-{N}-Prompt.md)
- 9.4. **VALIDATION**: Validate that external review materials were created successfully and follow external template structure
- 9.5. **STATUS TRACKING**: python Scripts/Logging/session_state.py Planner --workflow phase_9_materials_complete
- 9.6. **PRINT**: "External round table materials complete - awaiting user to post prompt to external agents for multi-perspective evaluation"
- 9.7. **WAIT** for user to post the external review prompt to external agents and provide their comprehensive multi-perspective reviews
- 9.8. **USER POSTS REVIEWS**: User posts external agent comprehensive reviews back in chat as structured JSON reviews with all 6 domain perspectives (Security, Infrastructure, Data Architecture, Application Architecture, Operations/DevOps, Business Alignment)
- 9.9. Log external agent comprehensive reviews to consolidated file Logs/Planner/round table/External/Batch{N}-{N}_Roundtable.md (append per revision, separated by Agent_Name) and verify logging completed successfully
- 9.10. Aggregate external agent findings and generate consolidated feedback across all perspectives
- 9.11. **CONVERGENCE CHECK**: Check if external agent overall verdict is PASS per Workflow/Workflow_Reference/Quality_Assessment_Framework.md
  - **if pass**: Proceed to phase 10 (Final Validation)
  - **if fail**: Proceed to phase 8A (Apply Findings - plan mode) - Note: Phase 8A handles both internal and external failures, looping back through internal round table to reach external again
- 9.12. **VALIDATION**: Validate that external round table completed successfully and convergence check passed
- 9.13. **PRINT**: "External round table complete - convergence status: [PASS/CONTINUE]"
- 9.14. **STATUS TRACKING**: python Scripts/Logging/session_state.py Planner --workflow phase_9_complete

### Phase 10. Final Validation + Delivery Authorization
- 10.1. **STATUS TRACKING**: python Scripts/Logging/session_state.py Planner --workflow phase_10_in_progress
- 10.2. Validate final plan structure and quality per Plan Template.md and validation requirements
- 10.3. Authorize plan delivery for implementation based on validation
- 10.4. **VALIDATION**: Validate that final validation completed successfully and delivery is authorized
- 10.5. **PRINT**: "Final validation complete - delivery authorized for executor execution"
- 10.6. **STATUS TRACKING**: python Scripts/Logging/session_state.py Planner --workflow phase_10_complete

### Phase 11. Workflow Termination
- 11.1. **STATUS TRACKING**: python Scripts/Logging/session_state.py Planner --workflow phase_11_in_progress
- 11.2. **PRINT** "Planner workflow execution complete - workflow terminated"
- 11.3. **PRINT** "Plan(s) available in Plans/Queued/ directory for implementation"
- 11.4. **VALIDATION**: Validate that workflow completed successfully before termination
- 11.5. **TERMINATE**: End workflow execution (do not return to Phase 0)
- 11.6. **STATUS TRACKING**: python Scripts/Logging/session_state.py Planner --workflow phase_11_complete

---

## Universal Framework References

### quality assessment
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
- **Planner Customization**: round table iteration state, convergence metrics tracking
- **Focus**: Convergence loops, validation results, plan revision tracking

### Execution Strategy
- **Universal Framework**: Workflow/Workflow_Reference/Execution_Strategy_Guidelines.md
- **Planner Customization**: Validation-based planning, round table review loops
- **Focus**: Planning strategies and convergence-based iteration

### Validation Enforcement
- **Universal Framework**: Workflow/Workflow_Reference/Validation_Enforcement_Patterns.md
- **Planner Customization**: Plan validation patterns and convergence loop validation
- **Focus**: Plan structure validation and delivery authorization

### Convergence Loop Patterns
- **Universal Framework**: Workflow/Workflow_Reference/Convergence_Loop_Patterns.md
- **Planner Customization**: round table review convergence patterns
- **Focus**: Internal and external round table convergence loops

### quota handling
- **Universal Framework**: Workflow/Workflow_Reference/Quota_Handling_Patterns.md
- **Planner Customization**: Internal subagent quota tracking for round table reviews
- **Focus**: Basic quota awareness and step progress tracking for internal subagents

### Plan Batch Processing
- **Planner Specifications**: Workflow/Planner/Reference/Plan_Batch_Specifications.md
- **Planner Customization**: Batch execution patterns and scan plan categorization
- **Focus**: Plan numbering, scan plan logic, and batch processing workflow

### runtime prerequisites
- **Universal Framework**: Workflow/Workflow_Reference/Runtime_Prerequisites.md
- **Planner Customization**: Validation system status and runtime directory requirements
- **Focus**: Runtime paths and infrastructure requirements for workflow execution

---

**Last Updated**: 2026-07-30
**Version**: 4.8 (Fixed file naming patterns, logging locations, deletion logic, and step references for logical consistency between plan mode and scan mode workflows)
**Maintained By**: Architect Agent

## phase structure Overview

- **Phase 0**: Load Governance Rules
- **phase 1**: Select Planning Mode
- **phase 2**: Select Execution Mode (references Execution_Mode_Patterns.md)
- **phase 3**: Planner Interaction (references Execution_Mode_Patterns.md)
- **phase 4A**: plan mode Input Processing (references Execution_Mode_Patterns.md)
- **phase 4B**: scan mode Input Processing (references Execution_Mode_Patterns.md)
- **phase 5A**: Plan Creation - plan mode (references Plan_Template.md, Plan_Batch_Specifications.md)
- **phase 5B**: Plan Creation - scan mode (references Plan_Template.md, Plan_Batch_Specifications.md)
- **phase 6A**: Review Material Creation - plan mode (references batch templates)
- **phase 6B**: Review Material Creation - scan mode (references single plan templates)
- **phase 7A**: Internal round table Execution - plan mode (references Plan_Prompt_Template.md, Quality_Assessment_Framework.md, Quota_Handling_Patterns.md, Plan_Batch_Specifications.md)
- **phase 7B**: Internal round table Execution - scan mode (references Plan_Prompt_Template.md, Quality_Assessment_Framework.md, Quota_Handling_Patterns.md)
- **phase 8A**: Apply Findings + Loop Back - plan mode (references templates for revisions)
- **phase 8B**: Apply Findings + Loop Back - scan mode (references templates for revisions)
- **phase 9**: External round table Execution - plan mode Only (references Plan_Prompt_Template.md, Quality_Assessment_Framework.md)
- **phase 10**: Final Validation + Delivery Authorization (shared phase, references Plan_Template.md)
- **phase 11**: Workflow Termination