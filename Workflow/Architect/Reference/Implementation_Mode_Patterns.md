# Architect Implementation Modes

**Purpose**: Architect-specific implementation mode selection and execution patterns.

## Universal Pattern Reference

See Workflow/Workflow_Reference/Execution_Strategy_Guidelines.md for universal execution strategy patterns including:
- Universal execution strategy guidelines
- Universal implementation mode handling patterns
- Universal execution strategy framework

## Architect Implementation Mode Specifications

### Implementation Mode Options

### Mode 1: Automated
**Description**: Agent implements everything automatically
- Agent executes all implementation steps without user intervention
- Continuous progression through implementation phases
- Automatic testing and validation
- Minimal user interaction required

**When to Use**:
- Well-defined, low-risk implementations
- Standard architectural patterns
- Tasks with clear success criteria
- When user trusts agent's judgment

**Benefits**:
- Faster implementation
- Consistent execution
- Reduced user overhead
- Efficient for standard tasks

**Risks**:
- Less user control over implementation
- Potential for unexpected decisions
- May not handle edge cases optimally
- Less visibility into implementation process

### Mode 2: Manual
**Description**: User and agent use iterative pattern for implementation
- Agent and user collaborate on implementation
- User provides guidance and approval at key points
- Iterative approach with frequent user feedback
- User maintains control over implementation direction

**When to Use**:
- Complex or high-risk implementations
- Novel architectural approaches
- Tasks requiring domain expertise
- When user wants close control

**Benefits**:
- Greater user control
- Better handling of edge cases
- Domain expertise integration
- Increased visibility

**Risks**:
- Slower implementation
- Higher user time commitment
- Potential for user fatigue
- May introduce inconsistencies

## Mode Selection Criteria

### Complexity Assessment
- **Low Complexity**: Consider Automated mode
- **Medium Complexity**: Assess based on risk and user preference
- **High Complexity**: Manual mode recommended

### Risk Assessment
- **Low Risk**: Can use Automated mode
- **Medium Risk**: Assess based on complexity and user confidence
- **High Risk**: Manual mode recommended

### User Confidence
- **High Confidence**: Agent has relevant expertise and track record
- **Medium Confidence**: Assess based on task complexity
- **Low Confidence**: Manual mode recommended

### Time Constraints
- **Tight Timeline**: Automated mode for faster execution
- **Moderate Timeline**: Balance based on complexity and risk
- **Flexible Timeline**: Manual mode for quality focus

## Implementation Execution Patterns

### Automated Mode Execution
1. **Specification Phase**: Agent creates detailed specification
2. **Implementation Phase**: Agent implements automatically
3. **Testing Phase**: Agent tests automatically
4. **Validation Phase**: Agent validates automatically
5. **Documentation Phase**: Agent documents automatically
6. **Completion Phase**: Agent notifies user of completion

### Manual Mode Execution
1. **Specification Phase**: Agent creates specification, user reviews
2. **Implementation Phase**: Agent implements function-by-function, user approves each
3. **Testing Phase**: Agent tests, user reviews results
4. **Validation Phase**: Agent validates, user confirms compliance
5. **Documentation Phase**: Agent documents, user reviews and approves
6. **Completion Phase**: Agent notifies user, user validates and accepts

## Mode Switching

### Mid-Workflow Mode Changes
- **Automated to Manual**: User can switch to Manual mode if issues arise
- **Manual to Automated**: Generally not recommended mid-workflow
- **Mode Change Documentation**: Document mode changes with reasoning
- **State Preservation**: Preserve implementation state during mode changes

### Mode Change Triggers
- **Complexity Increase**: Switch to Manual if complexity increases unexpectedly
- **Risk Discovery**: Switch to Manual if unexpected risks discovered
- **User Preference**: User can request mode change at any time
- **Failure Recovery**: May switch modes for recovery from failures

## Usage Guidelines

### Mode Selection Process
1. **Assess Task**: Evaluate task complexity, risk, and user confidence
2. **Present Options**: Present both mode options with trade-offs
3. **Recommend**: Recommend mode based on assessment
4. **User Selection**: User selects mode via popup menu
5. **Execute**: Execute implementation according to selected mode

### Mode Execution
1. **Follow Pattern**: Execute according to selected mode pattern
2. **Maintain Communication**: Maintain appropriate communication level
3. **Seek Approval**: Seek user approval at appropriate checkpoints
4. **Adapt**: Adapt execution based on feedback
5. **Complete**: Complete implementation according to mode

### Mode Evaluation
1. **Track Performance**: Track mode-specific performance metrics
2. **User Feedback**: Collect user feedback on mode effectiveness
3. **Pattern Analysis**: Analyze which modes work best for which tasks
4. **Refine Criteria**: Refine mode selection criteria based on patterns
5. **Optimize**: Optimize mode execution patterns over time