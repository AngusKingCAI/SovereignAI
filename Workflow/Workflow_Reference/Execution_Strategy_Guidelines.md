# Execution Strategy Guidelines

**Purpose**: Universal execution strategy specifications for all agent workflows.

## Agent-Specific Strategies

### Architect Agent
- **Manual/Auto/Complete Execution Modes**: 
  - **Manual**: Stop at failures for human oversight with checkpoint handling
  - **Auto**: Don't continue on failures (auto-stop on errors)
  - **Complete**: Continue past failures (ignore all errors)
- **Checkpoint Handling**: User confirmation via popup menu before phase transitions in Manual mode
- **Retry Logic**: Configurable retry with exponential backoff (max 3 retries) for Auto/Complete modes

### Planner Agent
- **Gate-Based Validation**: Standard gate validation with Round Table review loops
- **Fast-Track Planning**: Simplified validation for simple planning tasks
- **Iterative Planning**: Extended iteration loops for complex architectural changes
- **Convergence Loops**: Internal and external Round Table review until convergence achieved

### Executor Agent
- **Implementation Phases**: Systematic implementation with testing and deployment validation
- **Hook-Based Governance**: Automatic enforcement via Devin CLI hooks
- **Plan-Based Permissions**: Automatic enforcement of plan restrictions
- **Quality Verification**: Implementation quality checks against plan specifications

### Reviewer Agent
- **Review Phases**: Quality assessment and feedback loops
- **Pattern Recognition**: Identify recurring issues and governance gaps
- **Gate Analysis**: Analyze gate failure patterns and recommend improvements
- **Quality Metrics**: Dimension-based quality assessment

### Researcher Agent
- **Investigation Phases**: Research and analysis with validation
- **Web Search Verification**: Verify findings against current best practices
- **Documentation**: Create design documents with proper citations
- **Analysis**: Comprehensive investigation with quality assessment

## Strategy Configuration Patterns

### Strategy Selection Pattern
1. Agent selects appropriate strategy based on task complexity
2. Strategy stored in workflow state for consistent behavior
3. Strategy governs failure handling and progression throughout workflow
4. Strategy can be changed during workflow if conditions change

### Failure Handling Pattern
- **Manual**: Stop and await user intervention for retry/modify/abort decision
- **Auto**: Stop automatically without requiring human intervention
- **Complete**: Continue automatically, ignoring failures
- **Retry Logic**: Configurable exponential backoff for automatic strategies

### Checkpoint Pattern
- **Manual Mode**: Require user confirmation via popup menu before proceeding
- **Auto/Complete Modes**: Proceed automatically without checkpoints
- **Checkpoint Criteria**: Major phase transitions, critical decisions, failure points

## Universal Strategy Guidelines

### Strategy Consistency
- Maintain consistent strategy behavior throughout workflow execution
- Document strategy changes with rationale
- Update workflow state when strategy changes
- Notify user of strategy transitions

### Strategy Selection Criteria
- **Task Complexity**: Simple tasks may use faster strategies
- **Risk Level**: High-risk tasks may require manual oversight
- **User Preference**: Allow user to select strategy when appropriate
- **System Constraints**: Resource limits may influence strategy choice

### Strategy Monitoring
- Track strategy effectiveness across workflow executions
- Monitor failure rates and recovery patterns
- Adjust strategy based on performance metrics
- Document strategy evolution patterns