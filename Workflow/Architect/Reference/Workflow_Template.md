# Architect Workflow Template

**Purpose**: Architect-specific template for creating agent workflows.

## Template Overview

This template is used by the Architect agent to create workflows for other agents. All workflows must follow this structure for consistency.

## Template Reference

- **Location**: Workflow/Architect/Reference/Workflow_Template.md
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
### Phase 0. Read {Agent} Rules
- 1. Read Rules/{Agent}/{Agent}_Rules.md to load current governance constraints
- 2. Parse YAML frontmatter and rule definitions for implementation guidance
- 3. Store rule context for reference throughout workflow execution
- 4. **STATUS TRACKING**: Update workflow status to "phase_0_complete"
- 5. **PRINT** "{Agent} rules loaded from Rules/{Agent}/{Agent}_Rules.md"

### Phase 1. Select Execution Mode
- 6. Ask user to select execution mode for this workflow using popup menu:
  - **Manual**: Stop at failures for human oversight
  - **Auto**: Don't continue on failures (auto-stop on errors)
  - **Complete**: Continue past failures (ignore all errors)
- 7. Store selected execution mode for failure handling throughout workflow
- 8. **PRINT** "Execution mode selected - [Manual/Auto/Complete] will govern failure handling"

### Phase 2. {Agent} Interaction
- 9. Ask user: "Hi, {Agent} here - how can I help you today?"
- 10. Wait for user to specify their task or question
- 11. Clarify the task if needed
- 12. Review user request and check local research using index files before web search
- 13. Apply loaded {agent} rules to task requirements
- 14. **EXECUTION MODE HANDLING**: Apply execution mode handling patterns (see Workflow/Architect/Reference/Execution_Mode_Patterns.md)
- 15. **STATUS TRACKING**: Update workflow status to "phase_2_complete"
- 16. **PRINT** "Initiating {agent} interaction - awaiting user task specification"

### Phase 3. Research Best Practices
- 17. Check code documentation (Docs/Code/) for examples relevant to the specific type of work
- 18. **BEST PRACTICES WEB SEARCH**: Web search must be performed before major decisions (per {Agent}_Rules.md). Research industry standards and established patterns for the approach being considered.
- 19. Gather multiple approaches and patterns from web search and local research
- 20. Ensure proposed solutions comply with governance rules
- 21. **EXECUTION MODE HANDLING**: Apply execution mode handling patterns (see Workflow/Architect/Reference/Execution_Mode_Patterns.md)
- 22. **STATUS TRACKING**: Update workflow status to "phase_3_complete"
- 23. **PRINT** "Researching best practices - checking code documentation for relevant examples"
- 24. **PRINT**: "Best practices web search initiated - required before major decisions"
- 25. **PRINT**: "Research complete - gathered multiple implementation approaches from industry standards"

### Phase 4. {Agent} Work Phase
- 26. {Agent-specific work steps}
- 27. **VALIDATION**: Validate work completion and quality (see Workflow/Workflow_Reference/Validation_Enforcement_Patterns.md for universal pattern)
- 28. **EXECUTION MODE HANDLING**: Apply execution mode handling patterns (see Workflow/Architect/Reference/Execution_Mode_Patterns.md)
- 29. **STATUS TRACKING**: Update workflow status to "phase_4_complete"
- 30. **PRINT**: "{Agent} work phase complete - ready for next phase"

### Phase 5. {Agent} Validation Phase
- 31. {Agent-specific validation steps}
- 32. **VALIDATION**: Validate that work completed successfully (see Workflow/Workflow_Reference/Validation_Enforcement_Patterns.md for universal pattern)
- 33. **STATUS TRACKING**: Update workflow status to "phase_5_complete"
- 34. **PRINT**: "{Agent} validation complete - work verified for compliance"

### Phase 6. {Agent} Documentation Phase
- 35. Update relevant governance files and documentation
- 36. **EXECUTION MODE HANDLING**: Apply execution mode handling patterns (see Workflow/Architect/Reference/Execution_Mode_Patterns.md)
- 37. **STATUS TRACKING**: Update workflow status to "phase_6_complete"
- 38. **PRINT**: "Documentation complete - governance files updated"

### Phase 7. Final Validation
- 39. Verify implementation matches intended scope
- 40. Ensure compliance with all rules and constraints
- 41. **VALIDATION**: Validate that final validation completed successfully (see Workflow/Workflow_Reference/Validation_Enforcement_Patterns.md for universal pattern)
- 42. **EXECUTION MODE HANDLING**: Apply execution mode handling patterns (see Workflow/Architect/Reference/Execution_Mode_Patterns.md)
- 43. **STATUS TRACKING**: Update workflow status to "phase_7_complete"
- 44. **PRINT**: "Final validation complete - work verified for compliance"

### Phase 8. Session Logging + Validate
- 45. Consolidate all work iterations into session log to Logs/{Agent}/
- 46. Generate session attestation hash for verification from all session logs
- 47. **VALIDATION**: Validate that session logging completed successfully and audit trail is complete
- 48. **STATUS TRACKING**: Update workflow status to "phase_8_complete"
- 49. **PRINT**: "Session logging complete - audit trail validated, {Agent} workflow complete"

### Phase 10. Return to Phase 0
- 50. **PRINT** "Workflow cycle complete - returning to Phase 0 for next {agent} task"
- 51. **PRINT** "{Agent} agent ready - awaiting next user request"
- 52. Return to step 1

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

### Mandatory Phases
All workflows must include:
- **Phase 0**: Read {Agent} Rules (loads governance constraints)
- **Phase 1**: Select Execution Mode (Manual/Auto/Complete)
- **Phase 2**: {Agent} Interaction (user task specification)
- **Phase 3**: Research Best Practices (web search required before major decisions)
- **Phase 10**: Return to Phase 0 (workflow cycle)

### Mandatory Elements
All workflows must include:
- **VALIDATION** entries in each phase
- **STATUS TRACKING** entries in each phase
- **PRINT** commands for status updates
- **Universal Framework References** section at the end
- References to all 6 universal frameworks

### Naming Convention
Workflow files should follow: `{Agent}_{WorkflowType}_Workflow.md`
- Example: `Architect_General_Workflow.md`, `Planner_Plan_Workflow.md`

## Template Maintenance

- **Owner**: Architect Agent
- **Updates**: Only Architect should modify this template
- **Version Control**: Track template changes with version history
- **Change Process**: Major template changes require Architect review and testing

## Workflow Steps ({TotalSteps} steps)

### Phase 0. Read {Agent} Rules
- 1. Read Rules/{Agent}/{Agent}_Rules.md to load current governance constraints
- 2. Parse YAML frontmatter and rule definitions for implementation guidance
- 3. Store rule context for reference throughout workflow execution
- 4. **PRINT** "{Agent} rules loaded from Rules/{Agent}/{Agent}_Rules.md"

### Phase 1. Select Execution Strategy
- 5. Select execution strategy appropriate for agent type:
  - **{Option 1}**: {Description of first execution strategy}
  - **{Option 2}**: {Description of second execution strategy}
  - **{Option 3}**: {Description of third execution strategy}
- 6. Store selected execution strategy for workflow behavior
- 7. **PRINT** "Execution strategy selected - {Strategy} will govern workflow behavior"

### Phase 2. {Phase Name}
- 8. {Specific action description}
- 9. {Additional actions as needed}
- 10. **VALIDATION**: {Validation criteria for this phase}
- 11. **STATUS TRACKING**: Update workflow status to "phase_2_complete"
- 12. **PRINT** "{Description of what was logged for transparency}"

### Phase 3. Research and Best Practices
- 13. Check relevant documentation (Docs/{Category}/) for examples relevant to the specific task type
- 14. **BEST PRACTICES WEB SEARCH**: Web search must be performed before major decisions (per Architect_Rules.md). Research industry standards and established patterns for the approach being considered.
- 15. Gather multiple approaches and patterns from web search and local research
- 16. Ensure proposed solutions comply with governance rules
- 17. **VALIDATION**: {Validation criteria for research phase}
- 18. **STATUS TRACKING**: Update workflow status to "phase_3_complete"
- 19. **PRINT** "Researching best practices - checking documentation for relevant examples"
- 20. **PRINT** "Best practices web search initiated - required before major decisions"
- 21. **PRINT** "Research complete - gathered multiple implementation approaches from industry standards"

### Phase 4. {Phase Name}
- 22. {Specific action description}
- 23. **VALIDATION**: {Validation criteria for this phase}
- 24. **STATUS TRACKING**: Update workflow status to "phase_4_complete"
- 25. **PRINT** "{Description of what was logged for transparency}"

### Phase 5. {Phase Name}
- 26. {Specific action description}
- 27. **VALIDATION**: {Validation criteria for this phase}
- 28. **STATUS TRACKING**: Update workflow status to "phase_5_complete"
- 29. **PRINT** "{Description of what was logged for transparency}"

### Phase 6. {Phase Name}
- 30. {Specific action description}
- 31. When step fails, apply selected execution strategy:
  - **{Strategy 1}**: {Failure handling for strategy 1}
  - **{Strategy 2}**: {Failure handling for strategy 2}
  - **{Strategy 3}**: {Failure handling for strategy 3}
- 32. **RETRY LOGIC**: {Retry behavior for this agent type}
- 33. **STATUS TRACKING**: Update workflow status to "phase_6_in_progress" during execution, "phase_6_complete" when finished
- 34. **PRINT** "{Description of what was logged for transparency}"

### Phase 7. {Phase Name}
- 35. {Specific action description}
- 36. **VALIDATION**: {Validation criteria for this phase}
- 37. **STATUS TRACKING**: Update workflow status to "phase_7_complete"
- 38. **PRINT** "{Description of what was logged for transparency}"

### Phase 8. {Phase Name}
- 39. {Specific action description}
- 40. **VALIDATION**: {Validation criteria for this phase}
- 41. **STATUS TRACKING**: Update workflow status to "phase_8_complete"
- 42. **PRINT** "{Description of what was logged for transparency}"

### Phase 9. {Phase Name}
- 43. {Specific action description}
- 44. **VALIDATION**: {Validation criteria for this phase}
- 45. **STATUS TRACKING**: Update workflow status to "phase_9_complete"
- 46. **PRINT** "{Description of what was logged for transparency}"

### Phase 10. Return to Phase 0
- 47. **PRINT** "Workflow cycle complete - returning to Phase 0 for next task"
- 48. **PRINT** "{Agent} agent ready - awaiting next user request"
- 49. Return to step 1

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