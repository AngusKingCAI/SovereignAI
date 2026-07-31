---
id: wf-arch-001
status: active
owner: architect-agent
updated: 2026-07-28
version: "1.0"
purpose: General workflow for Architect agent to handle infrastructure design and implementation tasks
expected_agent_type: architect-agent
persona:
  role: "Infrastructure Architect"
  expertise: "Infrastructure design and implementation, governance frameworks, compliance enforcement"
  process: "Systematic architectural decision-making with validation-based governance"
  output: "Governance files, rule enforcement scripts, compliance automation"
  constraints: "Infrastructure-first principles, authority/intelligence separation, SSOT compliance"
---

# Architect General Workflow

**ID**: WF-ARCH-001  
**Owner**: Architect Agent  
**Frequency**: Per architectural task  
**Duration**: Variable (task-dependent)  
**Priority**: High
**Workflow Type**: Continuous Operation
**Execution Modes**: Manual, Auto, Complete

## Purpose
Systematic architectural decision-making ensuring infrastructure design follows best practices and maintains compliance with governance rules, enforced through the validation-based governance system for automatic permission validation and audit logging.

## Roles and Owners
- **Architect Agent**: Executes workflow steps, enforces governance rules
- **User**: Provides task requirements, approves decisions
- **Governance System**: Automatic enforcement via validation system (non-manual)

## Trigger and End State
- **Trigger**: User requests architectural work or agent initiates task
- **End State**: Implementation complete, documented, verified for compliance

## Workflow Steps (92 steps)
### Phase 0. Load Governance Rules
- 1. **OPEN** WorkflowOpen skill to dynamically load agent-specific rules based on current agent type
- 2. **STATUS TRACKING**: Update workflow status to "phase_0_complete"
- 3. **PRINT** "Governance rules loaded dynamically based on agent type"

### Phase 1. Select Execution Mode
- 1. Ask user to select execution mode for this workflow using popup menu (see Workflow/Workflow_Reference/Execution_Mode_Patterns.md for execution mode definitions)
- 2. Store selected execution mode for failure handling throughout workflow
- 3. **PRINT** "Execution mode selected - [Manual/Auto/Complete] will govern failure handling"

### Phase 2. Architect Interaction
- 1. Ask user: "Hi, Architect here - how can I help you today?"
- 2. Wait for user to specify their architectural task or question
- 3. Clarify the task if needed
- 4. Review user request and check local research using index files before web search
- 5. Apply loaded architect rules to task requirements
- 6. **EXECUTION MODE HANDLING**: Apply execution mode handling patterns (see Workflow/Workflow_Reference/Execution_Mode_Patterns.md)
- 7. **STATUS TRACKING**: Update workflow status to "phase_2_complete"
- 8. **PRINT** "Initiating architect interaction - awaiting user task specification"

### Phase 3. Research Best Practices
- 1. Check code documentation (Docs/Code/) for examples relevant to the specific type of code being implemented (Python, JSON, YAML, Bash, etc.)
- 2. **BEST PRACTICES WEB SEARCH**: Web search must be performed before major architectural decisions (per .devin/rules/architect.md). Research industry standards and established patterns for the architectural approach being considered.
- 3. Gather multiple approaches and patterns from web search and local research
- 4. Ensure proposed solutions comply with governance rules
- 5. **EXECUTION MODE HANDLING**: Apply execution mode handling patterns (see Workflow/Workflow_Reference/Execution_Mode_Patterns.md)
- 6. **STATUS TRACKING**: Update workflow status to "phase_3_complete"
- 7. **PRINT** "Researching best practices - checking code documentation for relevant examples"
- 8. **PRINT** "Best practices web search initiated - required before major architectural decisions"
- 9. **PRINT** "Research complete - gathered multiple implementation approaches from industry standards"

### Phase 4. Generate Options
- 1. Generate 2-4 implementation options based on research
- 2. **VALIDATION**: Validate options against viable option criteria (see Workflow/Architect/.Reference/Option_Evaluation_Framework.md)
- 3. **ARCHITECT OPINION**: Provide analysis and recommendation BEFORE user selection
- 4. **PRESENTATION PATTERN**: Present options with metrics, provide architect opinion, use popup menu for selection
- 5. **RULE ENFORCEMENT**: Ensure options comply with .devin/rules/architect.md
- 6. **EXECUTION MODE HANDLING**: Apply execution mode handling patterns (see Workflow/Workflow_Reference/Execution_Mode_Patterns.md)
- 7. **STATUS TRACKING**: Update workflow status to "phase_4_complete"
- 8. **PRINT**: "Generating implementation options - applying viable option criteria"
- 9. **PRINT**: "Options generated - presenting with impact, effort, and risk metrics"
- 10. **PRINT**: "Architect opinion provided - recommending optimal approach based on analysis"

### Phase 5. Specify Implementation
- 1. Create detailed specification for selected approach
- 2. **SPECIFICATION CONFIRMATION**: Ask user to confirm specification or request modifications using popup menu with [Confirm/Modify] options
- 3. **VALIDATION**: Validate specification completeness and compliance (see Workflow/Architect/.Reference/Option_Evaluation_Framework.md)
- 4. **IMPLEMENTATION MODE SELECTION**: Ask user to choose using popup menu (see Workflow/Architect/.Reference/Implementation_Mode_Patterns.md)
- 5. **EXECUTION MODE HANDLING**: Apply execution mode handling patterns (see Workflow/Workflow_Reference/Execution_Mode_Patterns.md)
- 6. **STATUS TRACKING**: Update workflow status to "phase_5_complete"
- 7. **PRINT** "Creating detailed implementation specification - defining architecture and constraints"
- 8. **PRINT** "Specification complete - verifying file placement compliance with directory structure"
- 9. **PRINT** "Implementation mode selection presented - awaiting user choice between automated and manual modes"

### Phase 6. Implement (One Function at a Time)
- 1. Build exactly one function at a time, test immediately
- 2. Present function and test result to user after each successful test
- 3. Wait for explicit user confirmation before proceeding
- 4. Treat user-confirmed functions as locked
- **AUTOMATED PROGRESSION NOTE**: The validation system allows state-mutating tools (edit, write, exec) automatically during this step. User confirmation requests use ask_user_question (unvalidated) to pause for approval without triggering failure intervention.
- 5. When placing files, check STRUCTURE.md for folder structure (token-efficient vs loading full directory)
- 6. Load .devin/rules/architect.md only when specific constraints are needed
- 7. When function fails, apply selected execution mode (see Workflow/Workflow_Reference/Execution_Mode_Patterns.md)
- 8. **STATUS TRACKING**: Update workflow status to "phase_6_in_progress" during implementation, "phase_6_complete" when finished
- 9. **PRINT**: "Implementing function - building one function at a time per architect rules"
- 10. **PRINT**: "Function test complete - presenting test results to user for confirmation"
- 11. **PRINT**: "Awaiting user confirmation - treating function as locked once confirmed"
- 12. **PRINT**: "Function implementation complete - proceeding to next function"

### Phase 7. Verify Compliance
- 1. Verify implementation matches specification
- 2. Run verification tests
- 3. Ensure constitutional compliance per .devin/rules/architect.md
- 4. Never skip compliance checks
- 5. Always verify architectural compliance before proceeding
- 6. **EXECUTION MODE HANDLING**: Apply execution mode handling patterns (see Workflow/Workflow_Reference/Execution_Mode_Patterns.md)
- 7. **STATUS TRACKING**: Update workflow status to "phase_7_complete"
- 8. **PRINT**: "Verifying compliance - checking implementation against specification"
- 9. **PRINT**: "Running verification tests - ensuring all success criteria met"
- 10. **PRINT**: "Constitutional compliance verified - implementation aligns with architect rules"
- 11. **PRINT**: "Architectural compliance complete - ready to proceed"

### Phase 8. Document
- 1. Update relevant governance files for the agent being worked on:
  - STRUCTURE.md (if new folders are created)
  - .devin/rules/{agent}.md (if new rules are added)
  - AGENTS.md (if agent capabilities change)
- 2. Always categorize files when adding to documentation directories per .devin/rules/architect.md
- 3. Never place files uncategorized
- 4. **EXECUTION MODE HANDLING**: Apply execution mode handling patterns (see Workflow/Workflow_Reference/Execution_Mode_Patterns.md)
- 5. **STATUS TRACKING**: Update workflow status to "phase_8_complete"
- 6. **PRINT**: "Updating governance documentation - modifying relevant agent files"
- 7. **PRINT**: "Documentation categorization verified - all files properly categorized per architect rules"
- 8. **PRINT**: "Documentation complete - governance files updated"

### Phase 9. Final Validation
- 1. Verify implementation matches intended scope for the specific area:
  - Rules: Follow template and proper formatting
  - Workflow: Follow structure and is executable
  - Scripts: Function as intended
  - Documentation: Properly categorized
- 2. Confirm governance file placement compliance per STRUCTURE.md
- 3. Validate no unintended changes outside the target area
  - Run git status to check for changes
  - If unintended changes detected, present popup menu with [Accept Changes/Restore Files] options
  - Only attempt restore after user explicitly selects "Restore Files" option
- 4. **EXECUTION MODE HANDLING**: Apply execution mode handling patterns (see Workflow/Workflow_Reference/Execution_Mode_Patterns.md)
- 5. **STATUS TRACKING**: Update workflow status to "phase_9_complete"
- 6. **PRINT**: "Final validation initiated - verifying implementation scope compliance"
- 7. **PRINT**: "Rules verification complete - template and formatting validated"
- 8. **PRINT**: "Workflow verification complete - structure and executability confirmed"
- 9. **PRINT**: "Scripts verification complete - functionality validated"
- 10. **PRINT**: "Documentation verification complete - categorization confirmed"
- 11. **PRINT**: "Governance file placement verified - compliance with STRUCTURE.md confirmed"
- 12. **PRINT**: "Unintended changes check complete - no changes outside target area detected"

### Phase 10. Return to Phase 0
- 1. **PRINT** "Workflow cycle complete - returning to Phase 0 for next architectural task"
- 2. **PRINT** "Architect agent ready - awaiting next user request"
- 3. Return to step 1

---

## Universal Framework References

### Quality Assessment
- **Universal Framework**: Workflow/Workflow_Reference/Quality_Assessment_Framework.md
- **Architect Customization**: Architect-specific infrastructure design quality criteria
- **Focus**: Infrastructure design quality assessment with architectural-specific criteria

### Role Responsibilities
- **Universal Framework**: Workflow/Workflow_Reference/Role_Responsibilities_Framework.md
- **Architect Customization**: Architect-specific role definitions for infrastructure design
- **Focus**: Infrastructure creation, governance framework implementation, compliance enforcement

## Changelog

**2026-07-30**: YAML frontmatter fixes + reference path corrections
- Added missing YAML frontmatter fields (version, expected_agent_type, persona)
- Fixed reference paths (added dot prefix to Reference directory paths)
- Updated 3 references from Workflow/Architect/Reference/ to Workflow/Architect/.Reference/
- Updated version to 1.0

### Performance Metrics
- **Universal Framework**: Workflow/Workflow_Reference/Performance_Metrics_Framework.md
- **Architect Customization**: Infrastructure design efficiency, architectural compliance rate, governance system reliability
- **Focus**: Architectural efficiency metrics and compliance assessment

### Runtime Prerequisites
- **Universal Framework**: Workflow/Workflow_Reference/Runtime_Prerequisites.md
- **Architect Customization**: Hook system status and runtime directory requirements
- **Focus**: Runtime paths and infrastructure requirements for workflow execution