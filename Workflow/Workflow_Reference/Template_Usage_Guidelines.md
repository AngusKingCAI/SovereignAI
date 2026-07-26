# Template Usage Guidelines

**Purpose**: Universal template usage guidelines for all agent workflows.

## Universal Core Elements (All Agents)

### Phase 0. Read {Agent} Rules
- **Always Required**: First phase for all agents
- **Purpose**: Load current governance constraints
- **Steps**: Read rules, parse definitions, store context
- **Output**: PRINT confirmation of rules loaded

### Phase 3. Research and Best Practices
- **Always Required**: Research phase for all agents
- **Purpose**: Web search before major decisions
- **Steps**: Check documentation, web search, gather patterns
- **Output**: PRINT research progress and completion

### Phase 10. Return to Phase 0
- **Always Required**: Return phase for all agents
- **Purpose**: Enable continuous workflow execution
- **Steps**: PRINT completion, agent ready, return to step 1
- **Output**: Workflow cycle ready for next task

### Universal Elements
- **VALIDATION**: Include validation criteria for each phase
- **STATUS TRACKING**: Update workflow state at each phase completion
- **PRINT COMMANDS**: Use PRINT for user visibility throughout workflow

## Agent-Specific Customization

### Phase 1. Select Execution Strategy
- **Customize Options**: Define strategy options for agent type
- **Examples**: Manual/Auto/Complete, Validation-Based/Fast-Track/Iterative
- **Storage**: Store strategy in workflow state
- **Reference**: See Execution_Strategy_Guidelines.md

### Phases 2-9. Agent-Specific Phases
- **Customize Names**: Use descriptive phase names for agent workflows
- **Customize Actions**: Define agent-specific actions and processes
- **Customize Validation**: Define appropriate validation criteria
- **Customize Failure Handling**: Define agent-specific failure recovery

### Validation Pattern
- **VALIDATION**: Include validation criteria in each phase
- **Criteria**: Define PASS/FAIL conditions
- **Output**: Update workflow state on validation completion
- **Failure Handling**: Apply selected execution strategy on validation failure

### Status Tracking Pattern
- **STATUS TRACKING**: Update workflow state at phase completion
- **Format**: Use "phase_{N}_complete" or "phase_{N}_in_progress"
- **Recovery**: Enable workflow recovery from state tracking
- **Audit Trail**: Maintain complete execution history

### PRINT Command Pattern
- **PRINT**: Use for user visibility throughout workflow
- **Format**: Descriptive messages about workflow progress
- **Timing**: PRINT at key workflow transition points
- **Transparency**: Provide visibility into agent decision-making

## Template Structure

### Phase Numbering
- **Maintain 0-10**: Consistent phase numbering across all agents
- **Core Phases**: Keep Phase 0 (rules), Phase 3 (research), Phase 10 (return)
- **Customizable**: Adapt Phases 1-2, 4-9 for agent-specific needs
- **Numbering**: Use sequential step numbering within phases

### Phase Customization
- **Customize Middle Phases**: Adapt Phases 1-2, 4-9 for agent workflows
- **Agent-Specific**: Add phases as needed for agent capabilities
- **Iteration Logic**: Add convergence loops if needed (e.g., Planner)
- **Special Phases**: Add agent-specific phases (hook integration, etc.)

### Validation Patterns
- **Appropriate Patterns**: Use validation patterns suitable for agent type
- **Checkpoints**: Add user confirmation checkpoints for manual strategies
- **Automated Validation**: Use automated validation for auto/complete strategies
- **Validation Systems**: Implement validation systems for agents requiring comprehensive validation

### Iteration Logic
- **Document Loops**: If using loops, document convergence criteria
- **Loop Structure**: Define loop exit conditions and iteration caps
- **Convergence Criteria**: Specify quality thresholds for loop completion
- **Escalation**: Define escalation procedures when loops fail

## Template Compliance Checklist

### Universal Elements
- [ ] Phase 0: Read {Agent} Rules present
- [ ] Phase 3: Research and Best Practices present
- [ ] Phase 10: Return to Phase 0 present
- [ ] VALIDATION in each phase
- [ ] STATUS TRACKING in each phase
- [ ] PRINT commands for visibility

### Structure Compliance
- [ ] Phase numbering 0-10 maintained
- [ ] Sequential step numbering within phases
- [ ] Core phases (0, 3, 10) preserved
- [ ] Agent-specific phases added as needed

### Reference Compliance
- [ ] Execution strategy references Execution_Strategy_Guidelines.md
- [ ] Validation patterns appropriate for agent type
- [ ] External documents organized in agent-specific Reference/ subfolders (e.g., Workflow/Architect/Reference/, Workflow/Planner/Reference/)
- [ ] Cross-references use relative paths

### Agent-Specific Customization
- [ ] Phase 1: Execution strategy customized for agent
- [ ] Phases 2-9: Customized for agent workflow
- [ ] Validation criteria appropriate for agent
- [ ] Failure handling customized for agent

## Template Evolution

### Continuous Improvement
- Monitor template usage patterns across agents
- Identify common customization patterns
- Update template based on agent feedback
- Evolve universal elements based on best practices

### Version Management
- Maintain template version history
- Document template changes with rationale
- Coordinate template updates with agent workflows
- Ensure backward compatibility when possible