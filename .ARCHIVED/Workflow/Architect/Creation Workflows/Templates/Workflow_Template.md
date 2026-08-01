---
id: workflow-template
status: active
owner: architect-agent
updated: 2026-07-29
version: "2.0"
purpose: Architect-specific template for creating agent workflows with consistent structure
---

# Architect Workflow Template

**Purpose**: Architect-specific template for creating agent workflows.

## Template Overview

This template is used by the Architect agent to create workflows for other agents. All workflows must follow this structure for consistency.

## Workflow Types

Architect creates two types of workflows with different termination patterns:

### 1. Continuous Operation Workflows (Standard Agent Workflows)
- **Purpose**: Agents that should always be ready for new tasks
- **Termination Pattern**: Include "Return to Load Governance Rules section" for continuous operation
- **Examples**: Architect_General_Workflow, Planner_Plan_Workflow, Executor_Implementation_Cycle
- **Behavior**: Workflow cycles indefinitely, agent always ready for next task
- **Use Case**: Primary agent workflows that handle ongoing agent operations

### 2. Single-Execution Workflows (Utility/Tool Workflows)
- **Purpose**: Utility workflows that execute once and terminate
- **Termination Pattern**: Exclude or modify to termination (no "Return to Load Governance Rules section")
- **Examples**: Architect_Consistency_Check_Workflow, Architect_Consistency_Fix_Workflow
- **Behavior**: Workflow executes once and terminates, no automatic looping
- **Use Case**: Specialized workflows that run on-demand and complete

### Workflow Type Selection Guidelines
- **Use Continuous Operation**: For primary agent workflows that should always be available
- **Use Single-Execution**: For utility workflows, validation workflows, maintenance workflows

## Template Reference

- **Location**: Workflow/Architect/Creation Workflows/Templates/Workflow_Template.md
- **Owner**: Architect Agent
- **Usage**: Architect uses this template to create workflows for all agents
- **Updates**: Only Architect should modify this template

## Template Structure

## Workflow Header
```markdown
---
id: wf-{agent}-{workflow-type}
status: active
owner: {agent}-agent
updated: {date}
version: 1.0
purpose: {workflow purpose description}
expected_agent_type: {agent}-agent
persona:
  role: "{specific role for this workflow}"
  expertise: "{relevant expertise areas}"
  process: "{workflow execution approach}"
  output: "{expected output format}"
  constraints: "{operational constraints}"
---

# {Agent} {WorkflowType} Workflow

**ID**: WF-{AGENT}-{XXX}
**Owner**: {Agent} Agent
**Frequency**: {Frequency}
**Duration**: {Duration}
**Priority**: {Priority}
**Workflow Type**: {Continuous Operation or Single-Execution}
**Execution Modes**: {Workflow-specific execution mode options}
**Phase Structure**: {Brief description of workflow phases}

## Purpose
{What this workflow accomplishes and why it exists}

## Reference Documents
- **Universal Framework References**: Workflow/Workflow_Reference/ (referenced frameworks based on workflow relevance)
- **Agent Rules**: .devin/rules/{agent}.md (agent-specific governance rules)
- **Best Practice Integration**: Web search points (BP?) for current industry standards
- **Terminology**: Workflow/Workflow_Reference/Terminology_Glossary.md (SSOT for governance terminology)

## Roles and Owners
- **{Agent} Agent**: Executes workflow steps, enforces governance rules
- **User**: Provides task requirements, approves decisions
- **Governance System**: Validation and compliance enforcement

## Trigger and End State
- **Trigger**: {What triggers this workflow - when should it be executed}
- **End State**: {What constitutes workflow completion - when is the workflow considered finished}

## Workflow Steps

### Load Governance Rules [**MANDATED**]
- **OPEN** WorkflowOpen skill to dynamically load agent-specific rules based on current agent type
- **STATUS TRACKING**: Update workflow status to "governance_rules_loaded"
- **PRINT** "Governance rules loaded dynamically based on agent type"

### Select Execution Mode [**MANDATED**]
- Ask user to select execution mode for this workflow using popup menu:
  - **Workflow-Specific Options**: Each workflow defines its own execution mode options based on its operational needs
  - **Common Patterns**: 
    - Manual/Auto/Complete (traditional phase-based workflows)
    - Manual/Manual Batched/Automatic Batched (file/item processing workflows)
    - Custom modes defined by workflow requirements
- Store selected execution mode for failure handling throughout workflow
- **STATUS TRACKING**: Update workflow status to "execution_mode_selected"
- **PRINT** "Execution mode selected - [workflow-specific modes] will govern failure handling"

### {Agent} Interaction [**SUGGESTED**]
- Ask user: "Hi, {Agent} here - how can I help you today?"
- Wait for user to specify their task or question
- Clarify the task if needed
- Review user request and check local research using index files before web search
- Apply loaded {agent} rules to task requirements
- **EXECUTION MODE HANDLING**: Apply execution mode handling patterns (see Workflow/Workflow_Reference/Execution_Mode_Patterns.md)
- **STATUS TRACKING**: Update workflow status to "agent_interaction_complete"
- **PRINT** "Initiating {agent} interaction - awaiting user task specification"

### Research Best Practices [**SUGGESTED**]
- Check code documentation (Docs/Code/) for examples relevant to the specific type of work
- **BEST PRACTICES WEB SEARCH**: Web search must be performed before major decisions (per {Agent}_Rules.md). Research industry standards and established patterns for the approach being considered.
- Gather multiple approaches and patterns from web search and local research
- Ensure proposed solutions comply with governance rules
- **EXECUTION MODE HANDLING**: Apply execution mode handling patterns (see Workflow/Workflow_Reference/Execution_Mode_Patterns.md)
- **STATUS TRACKING**: Update workflow status to "research_complete"
- **PRINT** "Researching best practices - checking code documentation for relevant examples"
- **PRINT** "Best practices web search initiated - required before major decisions"
- **PRINT** "Research complete - gathered multiple implementation approaches from industry standards"

### {Agent} Work Phase [**SUGGESTED**]
- {Agent-specific work steps}
- **VALIDATION**: Validate work completion and quality (see Workflow/Workflow_Reference/Validation_Enforcement_Patterns.md for universal pattern)
- **EXECUTION MODE HANDLING**: Apply execution mode handling patterns (see Workflow/Workflow_Reference/Execution_Mode_Patterns.md)
- **STATUS TRACKING**: Update workflow status to "agent_work_complete"
- **PRINT** "{Agent} work phase complete - ready for next phase"

### {Agent} Validation Phase [**SUGGESTED**]
- {Agent-specific validation steps}
- **VALIDATION**: Validate that work completed successfully (see Workflow/Workflow_Reference/Validation_Enforcement_Patterns.md for universal pattern)
- **STATUS TRACKING**: Update workflow status to "agent_validation_complete"
- **PRINT** "{Agent} validation complete - work verified for compliance"

### {Agent} Documentation Phase [**SUGGESTED**]
- Update relevant governance files and documentation
- **EXECUTION MODE HANDLING**: Apply execution mode handling patterns (see Workflow/Workflow_Reference/Execution_Mode_Patterns.md)
- **STATUS TRACKING**: Update workflow status to "documentation_complete"
- **PRINT** "Documentation complete - governance files updated"

### Final Validation [**SUGGESTED**]
- Verify implementation matches intended scope
- Ensure compliance with all rules and constraints
- **VALIDATION**: Validate that final validation completed successfully (see Workflow/Workflow_Reference/Validation_Enforcement_Patterns.md for universal pattern)
- **EXECUTION MODE HANDLING**: Apply execution mode handling patterns (see Workflow/Workflow_Reference/Execution_Mode_Patterns.md)
- **STATUS TRACKING**: Update workflow status to "final_validation_complete"
- **PRINT** "Final validation complete - work verified for compliance"

### Session Logging + Validate [**SUGGESTED**]
- Consolidate all work iterations into session log to Logs/{Agent}/
- Generate session attestation hash for verification from all session logs
- **VALIDATION**: Validate that session logging completed successfully and audit trail is complete
- **STATUS TRACKING**: Update workflow status to "session_logging_complete"
- **PRINT** "Session logging complete - audit trail validated, {Agent} workflow complete"

### Workflow Type-Specific Termination [**SUGGESTED**]
**For Continuous Operation Workflows:**
- **PRINT** "Workflow cycle complete - returning to Load Governance Rules section for next {agent} task"
- **PRINT** "{Agent} agent ready - awaiting next user request"
- Return to Load Governance Rules section

**For Single-Execution Workflows:**
- **PRINT** "Workflow execution complete - workflow terminated"
- **PRINT** "{Agent} agent ready - awaiting next user request"
- **TERMINATE**: End workflow execution (do not return to Load Governance Rules section)

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
All workflows must include the following sections marked with [**MANDATED**]:
- **Workflow Header**: ID, Owner, Frequency, Duration, Priority, Execution Modes, Purpose, Roles, Trigger and End State
- **expected_agent_type**: Required field in YAML frontmatter specifying which agent executes this workflow
- **persona**: Required field in YAML frontmatter with proper persona structure (role, expertise, process, output, constraints)
- **Reference Documents section**: Must list all referenced documents, universal frameworks, agent rules, and terminology sources
- **Trigger and End State section**: Must specify workflow entry conditions and completion criteria
- **Load Governance Rules [**MANDATED**]**: Required section for loading agent-specific governance rules
- **Select Execution Mode [**MANDATED**]**: Required section for workflow-specific execution mode selection
- **Universal Framework References** section at the end
- References to all universal frameworks relevant to the workflow
- **Relevance Requirement**: Only include universal framework references that are actually relevant to the agent's specific purpose
- **Execution Modes Definition**: Each workflow must define its specific execution mode options in the header and Select Execution Mode section

### Suggested Sections (Recommended but Flexible)
The following sections are recommended for most workflows but are marked with [**SUGGESTED**]:
- **{Agent} Interaction [**SUGGESTED**]**: User task specification and interaction
- **Research Best Practices [**SUGGESTED**]**: Industry standards and pattern research
- **{Agent} Work Phase [**SUGGESTED**]**: Agent-specific work implementation
- **{Agent} Validation Phase [**SUGGESTED**]**: Agent-specific validation steps
- **{Agent} Documentation Phase [**SUGGESTED**]**: Governance file updates
- **Final Validation [**SUGGESTED**]**: Final verification and compliance check
- **Session Logging + Validate [**SUGGESTED**]**: Audit trail and session verification
- **Workflow Type-Specific Termination [**SUGGESTED**]**: Optional termination based on workflow type

### Template Usage Instructions
**IMPORTANT**: When creating actual workflows from this template:
1. **Remove [**MANDATED**] and [**SUGGESTED**] markers** from section names in the final workflow
2. **Convert template sections to numbered phases** (Phase 0, Phase 1, etc.) with numbered steps (0.1, 0.2, etc.)
3. **Include all [**MANDATED**] sections** in the final workflow
4. **Select appropriate [**SUGGESTED**] sections** based on workflow needs
5. **Customize section content** based on specific agent requirements and user intent
6. **Actual workflows should have proper phase structure** with numbered steps, unlike this template

### Suggested Elements (Recommended but Flexible)
The following elements are suggested patterns for good workflow design:
- **VALIDATION** entries in phases where quality checks are needed
- **STATUS TRACKING** entries for workflow state management
- **PRINT** commands for status updates and user communication

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