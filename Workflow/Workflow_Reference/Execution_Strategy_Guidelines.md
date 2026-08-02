---
id: wf-ref-exec-strategy
status: active
owner: architect-agent
updated: 2026-07-28
purpose: Universal execution strategy specifications for all agent workflows
---

# Execution Strategy Guidelines

**Purpose**: Universal execution strategy specifications for all agent workflows.

## Universal Strategy Configuration Patterns

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