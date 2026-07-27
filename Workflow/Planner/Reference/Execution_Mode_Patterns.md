# Planner Execution Mode When-to-Use Scenarios

**Purpose**: Planner-specific when-to-use scenarios for execution mode selection.

## Universal Pattern Reference

See Workflow/Workflow_Reference/Execution_Mode_Patterns.md for universal execution mode patterns including:
- Universal execution mode definitions (Manual, Auto, Complete)
- Universal execution mode handling patterns
- Universal failure handling patterns
- Universal retry logic with exponential backoff
- Universal execution mode tracking
- Universal usage guidelines

## Planner Execution Mode When-to-Use Scenarios

### Manual Mode When to Use
- High-risk planning decisions
- Novel or experimental planning approaches
- When user wants close control over planning process
- Complex governance requirements for planning
- Plans affecting system architecture
- Security-critical planning scenarios

### Auto Mode When to Use
- Standard planning tasks
- Well-understood planning patterns
- When user wants some automation with safety
- Medium-risk planning decisions
- Routine plan updates
- Documented planning improvements

### Complete Mode When to Use
- Low-risk, routine planning tasks
- Experimental or exploratory planning work
- When user wants maximum automation
- Planning tasks where failures are acceptable
- Non-critical documentation updates
- Testing and validation workflows

## Planner Execution Strategies

### Validation-Based Validation
**Description**: Standard validation with Round Table review loops
- Comprehensive validation through internal and external Round Table review
- Dual-validation governance with early and final validation phases
- Convergence-based iteration until quality thresholds are met
- Incremental logging for audit trail and Reviewer analysis

**When to Use**:
- Standard planning tasks requiring comprehensive validation
- Complex architectural changes requiring thorough review
- Plans with multiple dependencies and relationships
- When plan quality is critical

### Fast-Track Planning
**Description**: Simplified validation for simple planning tasks
- Streamlined validation process for straightforward planning tasks
- Reduced Round Table review requirements
- Focused validation on critical planning elements
- Faster plan delivery for simple, well-defined tasks

**When to Use**:
- Simple planning tasks with clear requirements
- Well-understood planning patterns
- Low-risk planning scenarios
- When planning speed is prioritized

### Iterative Planning
**Description**: Extended iteration loops for complex architectural changes
- Extended convergence loops for complex planning scenarios
- Multiple Round Table review cycles for quality assurance
- Incremental plan refinement through iteration
- Comprehensive validation of complex planning relationships

**When to Use**:
- Complex architectural changes requiring extensive review
- High-risk planning scenarios requiring thorough validation
- Plans with numerous dependencies and relationships
- When planning accuracy is critical

### Convergence Loops
**Description**: Internal and external Round Table review until convergence achieved
- Internal Round Table convergence loop (max 5 iterations)
- External Round Table convergence loop (max 3 iterations)
- Quality threshold-based convergence criteria
- Automatic escalation when loop caps are reached

**When to Use**:
- All standard planning workflows
- Plans requiring comprehensive quality validation
- Multi-phase planning processes
- When planning quality assurance is required