# Execution Mode Patterns

**Purpose**: Universal execution mode patterns for all agent workflows.

## Execution Mode Definitions

### Manual Mode
**Behavior**: Stop at failures for human oversight
- **Checkpoint Handling**: Require user confirmation via popup menu before proceeding to next phase
- **Failure Handling**: Stop workflow and await user intervention for retry/modify/abort decision
- **User Control**: Maximum user control over workflow progression
- **Risk Mitigation**: Human oversight at each phase transition

### Auto Mode
**Behavior**: Don't continue on failures (auto-stop on errors)
- **Checkpoint Handling**: Proceed automatically to next phase
- **Failure Handling**: Stop workflow automatically without requiring human intervention
- **Efficiency**: Balanced efficiency with failure detection
- **Risk Mitigation**: Automatic failure detection and stopping

### Complete Mode
**Behavior**: Continue past failures (ignore all errors)
- **Checkpoint Handling**: Proceed automatically to next phase
- **Failure Handling**: Continue workflow automatically, ignoring failures
- **Efficiency**: Maximum efficiency with failure tolerance
- **Risk Mitigation**: Minimal risk mitigation

## Execution Mode Handling Patterns

### Phase Transition Handling
**Manual Mode Pattern**:
1. Complete phase actions
2. **EXECUTION MODE HANDLING**: Require user confirmation via popup menu before proceeding to next phase (CHECKPOINT)
3. **STATUS TRACKING**: Update workflow status to "phase_{N}_complete"
4. **PRINT**: Phase completion message with checkpoint confirmation
5. Wait for user approval before proceeding

**Auto Mode Pattern**:
1. Complete phase actions
2. **EXECUTION MODE HANDLING**: Proceed automatically to next phase
3. **STATUS TRACKING**: Update workflow status to "phase_{N}_complete"
4. **PRINT**: Phase completion message
5. Proceed automatically to next phase

**Complete Mode Pattern**:
1. Complete phase actions (even if failures occur)
2. **EXECUTION MODE HANDLING**: Proceed automatically to next phase
3. **STATUS TRACKING**: Update workflow status to "phase_{N}_complete"
4. **PRINT**: Phase completion message (including any failures)
5. Proceed automatically to next phase

### Failure Handling Patterns
**Manual Mode Failure Pattern**:
1. Detect failure in current phase
2. **EXECUTION MODE HANDLING**: Stop workflow and await user intervention for retry/modify/abort decision (CHECKPOINT)
3. **STATUS TRACKING**: Update workflow status to "phase_{N}_failed"
4. **PRINT**: Failure message with error details
5. Await user decision on recovery action

**Auto Mode Failure Pattern**:
1. Detect failure in current phase
2. **EXECUTION MODE HANDLING**: Stop workflow automatically without requiring human intervention
3. **RETRY LOGIC**: Implement configurable retry with exponential backoff (max 3 retries)
4. **STATUS TRACKING**: Update workflow status to "phase_{N}_failed"
5. **PRINT**: Failure message with retry attempt information
6. Proceed with retry logic automatically

**Complete Mode Failure Pattern**:
1. Detect failure in current phase
2. **EXECUTION MODE HANDLING**: Continue workflow automatically, ignoring the failure
3. **RETRY LOGIC**: Implement configurable retry with exponential backoff (max 3 retries)
4. **STATUS TRACKING**: Update workflow status to "phase_{N}_complete" (despite failure)
5. **PRINT**: Failure message but continue workflow
6. Proceed to next phase automatically

## Retry Logic with Exponential Backoff

### Retry Configuration
- **Max Retries**: 3 retries maximum
- **Backoff Pattern**: Exponential backoff (1s, 2s, 4s, 8s, etc.)
- **Retry Criteria**: Configurable based on error type
- **Retry Logging**: Log each retry attempt with metadata

### Retry Implementation
```python
retry_count = 0
max_retries = 3
backoff_time = 1

while retry_count < max_retries:
    try:
        # Execute phase
        execute_phase()
        break  # Success, exit retry loop
    except Exception as error:
        retry_count += 1
        if retry_count >= max_retries:
            raise  # Max retries reached
        time.sleep(backoff_time)
        backoff_time *= 2  # Exponential backoff
```

## Execution Mode Tracking

### State Management
- **Mode Storage**: Store selected execution mode in workflow state
- **Mode Changes**: Track mode changes with reasoning
- **Mode Effectiveness**: Track mode effectiveness metrics
- **Mode Optimization**: Optimize mode selection based on patterns

### Audit Trail
- **Mode Selection**: Log mode selection with reasoning
- **Mode Changes**: Log mode changes with trigger events
- **Checkpoint Outcomes**: Log checkpoint outcomes in Manual mode
- **Failure Handling**: Log failure handling patterns and outcomes

## Usage Guidelines

### Mode Selection Process
1. **Assess Task**: Evaluate task complexity and risk
2. **Present Options**: Present execution mode options to user
3. **Recommend**: Recommend appropriate mode based on assessment
4. **User Selection**: User selects mode via popup menu
5. **Store Mode**: Store selected mode in workflow state

### Mode Execution
1. **Apply Pattern**: Apply appropriate execution mode pattern
2. **Handle Checkpoints**: Handle checkpoints according to mode
3. **Handle Failures**: Handle failures according to mode
4. **Track Progress**: Track progress according to mode requirements
5. **Log Actions**: Log mode-specific actions for audit trail

### Mode Evaluation
1. **Track Success Rates**: Track success rates by mode
2. **Track User Satisfaction**: Track user satisfaction by mode
3. **Analyze Patterns**: Analyze which modes work best for which task types
4. **Refine Criteria**: Refine mode selection criteria based on patterns
5. **Optimize Patterns**: Optimize execution mode patterns over time