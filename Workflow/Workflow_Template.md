# {Title}

**ID**: {WorkflowID}  
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

### Quality Metrics
- **Universal Framework**: Workflow/Workflow_Reference/Quality_Metrics_Framework.md
- **Agent Customization**: Agent-specific metric customization
- **Usage**: Reference universal framework for consistency