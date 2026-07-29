---
id: workflow-template
status: active
owner: architect-agent
updated: 2026-07-28
purpose: Architect-specific template for creating agent workflows with consistent structure
---

# Architect Workflow Template

**Purpose**: Architect-specific template for creating agent workflows.

## Template Overview

This template is used by the Architect agent to create workflows for other agents. All workflows must follow this structure for consistency.

## Workflow Types

Architect creates two types of workflows with different Phase 10 patterns:

### 1. Continuous Operation Workflows (Standard Agent Workflows)
- **Purpose**: Agents that should always be ready for new tasks
- **Phase 10 Pattern**: Include "Return to step 1" for continuous operation
- **Examples**: Architect_General_Workflow, Planner_Plan_Workflow, Executor_Implementation_Cycle
- **Behavior**: Workflow cycles indefinitely, agent always ready for next task
- **Use Case**: Primary agent workflows that handle ongoing agent operations

### 2. Single-Execution Workflows (Utility/Tool Workflows)
- **Purpose**: Utility workflows that execute once and terminate
- **Phase 10 Pattern**: Exclude or modify to termination (no "Return to step 1")
- **Examples**: Architect_Consistency_Check_Workflow, Architect_Consistency_Fix_Workflow
- **Behavior**: Workflow executes once and terminates, no automatic looping
- **Use Case**: Specialized workflows that run on-demand and complete

### Workflow Type Selection Guidelines
- **Use Continuous Operation**: For primary agent workflows that should always be available
- **Use Single-Execution**: For utility workflows, validation workflows, maintenance workflows

## Template Reference

- **Location**: Workflow/Templates/Workflow_Template.md
- **Owner**: Architect Agent
- **Usage**: Architect uses this template to create workflows for all agents
- **Updates**: Only Architect should modify this template

## Template Structure

## Workflow Header
```markdown
# {Agent} {WorkflowType} Workflow

**ID**: WF-{AGENT}-{XXX}  
**Owner**: {Agent} Agent  
**Frequency**: {Frequency}  
**Duration**: {Duration}  
**Priority**: {Priority}
**Execution Modes**: {Workflow-specific execution mode options}

## Purpose
{What this workflow accomplishes and why it exists}

## Roles and Owners
- **{Agent} Agent**: Executes workflow steps, enforces governance rules
- **User**: Provides task requirements, approves decisions
- **Governance System**: Validation and compliance enforcement

## Trigger and End State
- **Trigger**: {What triggers this workflow}
- **End State**: {What constitutes workflow completion}

## Workflow Steps ({total steps} steps)
### Phase 0. Load Governance Rules
- 1. **OPEN** WorkflowOpen skill to dynamically load agent-specific rules based on current agent type
- 2. **STATUS TRACKING**: Update workflow status to "phase_0_complete"
- 3. **PRINT** "Governance rules loaded dynamically based on agent type"

### Phase 1. Select Execution Mode (Workflow-Specific)
- 6. Ask user to select execution mode for this workflow using popup menu:
  - **Workflow-Specific Options**: Each workflow defines its own execution mode options based on its operational needs
  - **Common Patterns**: 
    - Manual/Auto/Complete (traditional phase-based workflows)
    - Manual/Manual Batched/Automatic Batched (file/item processing workflows)
    - Custom modes defined by workflow requirements
- 7. Store selected execution mode for failure handling throughout workflow
- 8. **PRINT** "Execution mode selected - [workflow-specific modes] will govern failure handling"

### Phase 2. {Agent} Interaction
- 9. Ask user: "Hi, {Agent} here - how can I help you today?"
- 10. Wait for user to specify their task or question
- 11. Clarify the task if needed
- 12. Review user request and check local research using index files before web search
- 13. Apply loaded {agent} rules to task requirements
- 14. **EXECUTION MODE HANDLING**: Apply execution mode handling patterns (see Workflow/Workflow_Reference/Execution_Mode_Patterns.md)
- 15. **STATUS TRACKING**: Update workflow status to "phase_2_complete"
- 16. **PRINT** "Initiating {agent} interaction - awaiting user task specification"

### Phase 3. Research Best Practices
- 17. Check code documentation (Docs/Code/) for examples relevant to the specific type of work
- 18. **BEST PRACTICES WEB SEARCH**: Web search must be performed before major decisions (per {Agent}_Rules.md). Research industry standards and established patterns for the approach being considered.
- 19. Gather multiple approaches and patterns from web search and local research
- 20. Ensure proposed solutions comply with governance rules
- 21. **EXECUTION MODE HANDLING**: Apply execution mode handling patterns (see Workflow/Workflow_Reference/Execution_Mode_Patterns.md)
- 22. **STATUS TRACKING**: Update workflow status to "phase_3_complete"
- 23. **PRINT** "Researching best practices - checking code documentation for relevant examples"
- 24. **PRINT**: "Best practices web search initiated - required before major decisions"
- 25. **PRINT**: "Research complete - gathered multiple implementation approaches from industry standards"

### Phase 4. {Agent} Work Phase
- 26. {Agent-specific work steps}
- 27. **VALIDATION**: Validate work completion and quality (see Workflow/Workflow_Reference/Validation_Enforcement_Patterns.md for universal pattern)
- 28. **EXECUTION MODE HANDLING**: Apply execution mode handling patterns (see Workflow/Workflow_Reference/Execution_Mode_Patterns.md)
- 29. **STATUS TRACKING**: Update workflow status to "phase_4_complete"
- 30. **PRINT**: "{Agent} work phase complete - ready for next phase"

### Phase 5. {Agent} Validation Phase
- 31. {Agent-specific validation steps}
- 32. **VALIDATION**: Validate that work completed successfully (see Workflow/Workflow_Reference/Validation_Enforcement_Patterns.md for universal pattern)
- 33. **STATUS TRACKING**: Update workflow status to "phase_5_complete"
- 34. **PRINT**: "{Agent} validation complete - work verified for compliance"

### Phase 6. {Agent} Documentation Phase
- 35. Update relevant governance files and documentation
- 36. **EXECUTION MODE HANDLING**: Apply execution mode handling patterns (see Workflow/Workflow_Reference/Execution_Mode_Patterns.md)
- 37. **STATUS TRACKING**: Update workflow status to "phase_6_complete"
- 38. **PRINT**: "Documentation complete - governance files updated"

### Phase 7. Final Validation
- 39. Verify implementation matches intended scope
- 40. Ensure compliance with all rules and constraints
- 41. **VALIDATION**: Validate that final validation completed successfully (see Workflow/Workflow_Reference/Validation_Enforcement_Patterns.md for universal pattern)
- 42. **EXECUTION MODE HANDLING**: Apply execution mode handling patterns (see Workflow/Workflow_Reference/Execution_Mode_Patterns.md)
- 43. **STATUS TRACKING**: Update workflow status to "phase_7_complete"
- 44. **PRINT**: "Final validation complete - work verified for compliance"

### Phase 8. Session Logging + Validate
- 45. Consolidate all work iterations into session log to Logs/{Agent}/
- 46. Generate session attestation hash for verification from all session logs
- 47. **VALIDATION**: Validate that session logging completed successfully and audit trail is complete
- 48. **STATUS TRACKING**: Update workflow status to "phase_8_complete"
- 49. **PRINT**: "Session logging complete - audit trail validated, {Agent} workflow complete"

### Phase 10. Return to Phase 0 (CONTINUOUS OPERATION WORKFLOWS ONLY)
- 50. **PRINT** "Workflow cycle complete - returning to Phase 0 for next {agent} task"
- 51. **PRINT** "{Agent} agent ready - awaiting next user request"
- 52. Return to step 1

### Phase 10. Workflow Termination (SINGLE-EXECUTION WORKFLOWS ONLY)
- 50. **PRINT** "Workflow execution complete - workflow terminated"
- 51. **PRINT** "{Agent} agent ready - awaiting next user request"
- 52. **TERMINATE**: End workflow execution (do not return to step 1)

---

## Universal Framework References

### Quality Assessment
- **Universal Framework**: Workflow/Workflow_Reference/Quality_Assessment_Framework.md
- **{Agent} Customization**: {Agent}-specific quality criteria
- **Focus**: Quality assessment with {agent}-specific criteria

### Role Responsibilities
- **Universal Framework**: Workflow/Workflow_Reference/Role_Responsibilities_Framework.md
- **{Agent} Customization**: {Agent}-specific role definitions
- **Focus**: {Agent}-specific responsibilities and tasks

### Performance Metrics
- **Universal Framework**: Workflow/Workflow_Reference/Performance_Metrics_Framework.md
- **{Agent} Customization**: {Agent}-specific performance metrics
- **Focus**: Performance metrics and efficiency assessment

### State Management
- **Universal Framework**: Workflow/Workflow_Reference/State_Management_Guidelines.md
- **{Agent} Customization**: {Agent}-specific state tracking
- **Focus**: State management and progress tracking

### Execution Strategy
- **Universal Framework**: Workflow/Workflow_Reference/Execution_Strategy_Guidelines.md
- **{Agent} Customization**: {Agent}-specific execution patterns
- **Focus**: Execution strategies and iteration patterns

### Runtime Prerequisites
- **Universal Framework**: Workflow/Workflow_Reference/Runtime_Prerequisites.md
- **{Agent} Customization**: {Agent}-specific runtime requirements
- **Focus**: Runtime paths and infrastructure requirements

## Template Requirements

### Mandated Sections (Required)
All workflows must include:
- **Workflow Header**: ID, Owner, Frequency, Duration, Priority, Execution Modes, Purpose, Roles, Trigger and End State
- **Universal Framework References** section at the end
- References to all universal frameworks relevant to the workflow
- **Relevance Requirement**: Only include universal framework references that are actually relevant to the agent's specific purpose
- **Execution Modes Definition**: Each workflow must define its specific execution mode options in the header and Phase 1

### Suggested Phases (Recommended but Flexible)
The following phases are suggested patterns that work well for most workflows, but agents should adapt them based on their specific needs:
- **Phase 0**: Read {Agent} Rules (loads governance constraints)
- **Phase 1**: Select Execution Mode (Manual/Auto/Complete)
- **Phase 2**: {Agent} Interaction (user task specification)
- **Phase 3**: Research Best Practices (web search required before major decisions)

### Suggested Elements (Recommended but Flexible)
The following elements are suggested patterns for good workflow design:
- **VALIDATION** entries in phases where quality checks are needed
- **STATUS TRACKING** entries for workflow state management
- **PRINT** commands for status updates and user communication

### Phase 10 (Workflow Type Dependent - Optional)
- **Continuous Operation Workflows**: May include Phase 10 with "Return to step 1" for continuous operation
- **Single-Execution Workflows**: May include Phase 10 with "TERMINATE" (no "Return to step 1")
- **Note**: Phase 10 is optional and should only be included if the workflow requires it

### Naming Convention
Workflow files should follow: `{Agent}_{WorkflowType}_Workflow.md`
- Example: `Architect_General_Workflow.md`, `Planner_Plan_Workflow.md`

## Template Maintenance

- **Owner**: Architect Agent
- **Updates**: Only Architect should modify this template
- **Version Control**: Track template changes with version history
- **Change Process**: Major template changes require Architect review and testing

## Execution Strategy Handling

See Workflow/Workflow_Reference/Execution_Strategy_Guidelines.md for detailed execution strategy specifications and agent-specific patterns.

## State Management

- **WORKFLOW STATE**: workflow_state.json in current working directory
- **EXECUTION STRATEGY**: Stored in workflow state for consistent behavior
- **STATUS TRACKING**: Phase status updates for recovery
- **AUDIT TRAIL**: Complete execution history in Logs/{Agent}/

See Workflow/Workflow_Reference/State_Management_Guidelines.md for detailed state management patterns and recovery procedures.

## Template Usage Guidelines

See Workflow/Workflow_Reference/Template_Usage_Guidelines.md for detailed template usage guidelines and customization patterns.

## Universal Framework References

### Quality Assessment
- **Universal Framework**: Workflow/Workflow_Reference/Quality_Assessment_Framework.md
- **Agent Customization**: Agent-specific quality criteria within universal framework
- **Usage**: Reference universal framework for consistency

### Role Responsibilities
- **Universal Framework**: Workflow/Workflow_Reference/Role_Responsibilities_Framework.md
- **Agent Customization**: Agent-specific responsibilities within universal framework
- **Usage**: Reference universal framework for consistency

### Performance Metrics
- **Universal Framework**: Workflow/Workflow_Reference/Performance_Metrics_Framework.md
- **Agent Customization**: Agent-specific metric customization
- **Usage**: Reference universal framework for consistency

### State Management
- **Universal Framework**: Workflow/Workflow_Reference/State_Management_Guidelines.md
- **Agent Customization**: Agent-specific state tracking
- **Usage**: Reference universal framework for consistency

### Execution Strategy
- **Universal Framework**: Workflow/Workflow_Reference/Execution_Strategy_Guidelines.md
- **Agent Customization**: Agent-specific execution patterns
- **Usage**: Reference universal framework for consistency

### Runtime Prerequisites
- **Universal Framework**: Workflow/Workflow_Reference/Runtime_Prerequisites.md
- **Agent Customization**: Agent-specific runtime requirements
- **Usage**: Reference universal framework for consistency

### Validation Enforcement
- **Universal Framework**: Workflow/Workflow_Reference/Validation_Enforcement_Patterns.md
- **Agent Customization**: Agent-specific validation patterns
- **Usage**: Reference universal framework for consistency

### Convergence Loops
- **Universal Framework**: Workflow/Workflow_Reference/Convergence_Loop_Patterns.md
- **Agent Customization**: Agent-specific convergence patterns
- **Usage**: Reference universal framework for consistency

### Quota Handling
- **Universal Framework**: Workflow/Workflow_Reference/Quota_Handling_Patterns.md
- **Agent Customization**: Agent-specific quota patterns
- **Usage**: Reference universal framework for consistency

### Template Usage
- **Universal Framework**: Workflow/Workflow_Reference/Template_Usage_Guidelines.md
- **Agent Customization**: Agent-specific template customization
- **Usage**: Reference universal framework for consistency

## Universal Framework Coverage

This template includes all 10 universal frameworks for reference, but individual workflows should only include the frameworks that are actually relevant to the agent's specific purpose (see Relevance Requirement above).

Available universal frameworks:
1. Quality Assessment Framework
2. Role Responsibilities Framework
3. Performance Metrics Framework
4. State Management Guidelines
5. Execution Strategy Guidelines
6. Runtime Prerequisites
7. Validation Enforcement Patterns
8. Convergence Loop Patterns
9. Quota Handling Patterns
10. Template Usage Guidelines

**Note**: Not all frameworks are relevant to all agents. Workflows should selectively include only the frameworks that apply to their specific workflow purpose and operational needs.