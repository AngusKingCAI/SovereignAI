# Convergence Loop Patterns

**Purpose**: Universal convergence loop patterns for iterative improvement processes across all agent workflows.

## Universal Convergence Loop Pattern

### Loop Structure
- **Loop Definition**: Iterative process between phases until convergence criteria are met
- **Back-Edge Pattern**: Return to previous phase after current phase completion
- **Loop Exit Condition**: Quality thresholds or stability criteria achieved
- **Loop Cap**: Maximum iterations to prevent infinite loops

### Convergence Logic
1. **Execute Current Phase**: Complete current phase actions
2. **Evaluate Results**: Assess phase outcomes against convergence criteria
3. **Check Convergence**: Determine if convergence criteria are met
4. **Exit if Converged**: Proceed to next phase if convergence achieved
5. **Loop if Not Converged**: Return to previous phase and iterate

### Universal Convergence Criteria
- **Quality Score Threshold**: Quality metrics meet defined thresholds
- **Stability Metrics**: Results stabilize across iterations
- **Issue Resolution**: Critical and high-priority issues resolved
- **Panel/Expert Agreement**: Expert consensus achieved (when applicable)

### Universal Loop Caps
- **Maximum Iterations**: Define maximum iterations per loop type
- **Escalation Procedures**: Define escalation when loop cap reached
- **User Intervention**: Define when to request user decision
- **Alternative Strategies**: Define alternative approaches when loops fail

## Agent-Specific Customization

Each agent should define:
- **Loop Definitions**: Agent-specific phase loop structures
- **Convergence Criteria**: Agent-specific quality thresholds and stability metrics
- **Loop Caps**: Agent-specific iteration limits
- **Escalation Procedures**: Agent-specific escalation when loops fail

## Usage Guidelines

### Universal Pattern Application
1. **Apply Universal Pattern**: Use the universal convergence loop pattern for iterative improvement
2. **Define Agent-Specific Loops**: Create agent-specific loop definitions in agent Reference/ folders
3. **Set Convergence Criteria**: Define agent-specific quality thresholds and stability metrics
4. **Implement Loop Logic**: Integrate convergence logic into workflow phases
5. **Document Escalation**: Document escalation procedures for loop failures

### Convergence Loop Consistency
- **Universal Pattern**: All agents follow the same convergence loop pattern
- **Agent-Specific Criteria**: Each agent defines its own convergence criteria
- **Consistent Logic**: Same convergence logic across all agents (execute → evaluate → check → exit/loop)
- **Universal Escalation**: Same escalation pattern when loops fail