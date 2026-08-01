---
id: wf-exec-ref-exec-mode-patterns
status: active
owner: executor-agent
updated: 2026-07-28
purpose: Executor-specific execution mode patterns for plan execution workflows
---

# Executor Execution Mode Patterns

**Purpose**: Executor-specific execution mode patterns for plan execution workflows.

## Executor Execution Mode Definitions

### Manual Mode
**Behavior**: Require user confirmation at each function implementation step for maximum oversight
- **Checkpoint Handling**: Require user confirmation via popup menu before proceeding to each function implementation
- **Failure Handling**: Stop workflow and await user intervention for retry/modify/abort decision
- **User Control**: Maximum user control over function-by-function progression
- **Risk Mitigation**: Human oversight at each function implementation
- **Use Case**: Critical implementations, complex functions, learning phase

### Auto Mode
**Behavior**: Execute functions automatically without user confirmation, stopping on errors
- **Checkpoint Handling**: Proceed automatically through function implementations
- **Failure Handling**: Stop workflow automatically if function implementation or tests fail
- **User Control**: Minimal user control with automated function implementation
- **Risk Mitigation**: Automatic failure detection and stopping at function level
- **Use Case**: Standard implementations, well-understood patterns, established processes

### Complete Mode
**Behavior**: Execute functions automatically without user confirmation, continuing past failures
- **Checkpoint Handling**: Proceed automatically through all function implementations
- **Failure Handling**: Continue workflow automatically, ignoring function implementation failures
- **User Control**: Minimal user control with maximum automated implementation
- **Risk Mitigation**: Minimal risk mitigation, maximum efficiency
- **Use Case**: Experimental implementations, rapid prototyping, non-critical code

## Executor Execution Mode Handling Patterns

### Manual Mode Pattern
1. **{BP}** web search for current best practices before file creation/modification
2. Implement single function from plan
3. **{BP}** web search for current testing best practices before test file creation
4. Create test file and run quality checks
5. **EXECUTION MODE HANDLING**: Require user confirmation via popup menu before proceeding to next function (CHECKPOINT)
6. **STATUS TRACKING**: Update workflow status to "function_{N}_complete"
7. **PRINT**: Function completion message with BP research findings and checkpoint confirmation
8. Wait for user approval before proceeding to next function

### Auto Mode Pattern
1. **{BP}** web search for current best practices before file creation/modification
2. Implement single function from plan
3. **{BP}** web search for current testing best practices before test file creation
4. Create test file and run quality checks
5. **EXECUTION MODE HANDLING**: Proceed automatically to next function if function succeeded, stop if function failed
6. **STATUS TRACKING**: Update workflow status to "function_{N}_complete" (success) or "function_{N}_failed" (failure)
7. **PRINT**: Function completion message (success) or failure message with retry attempt information
8. Proceed automatically to next function on success, apply retry logic on failure

### Complete Mode Pattern
1. **{BP}** web search for current best practices before file creation/modification
2. Implement single function from plan (even if failures occur)
3. **{BP}** web search for current testing best practices before test file creation
4. Create test file and run quality checks
5. **EXECUTION MODE HANDLING**: Proceed automatically to next function regardless of success/failure
6. **STATUS TRACKING**: Update workflow status to "function_{N}_complete" (even if function failed)
7. **PRINT**: Function completion message (including any failures but continue workflow)
8. Proceed to next function automatically

## Executor Failure Handling Patterns

### Manual Mode Failure Pattern
1. Detect failure in current function implementation or testing
2. **EXECUTION MODE HANDLING**: Stop workflow and await user intervention for retry/modify/abort decision (CHECKPOINT)
3. **RETRY LOGIC**: Implement configurable retry with exponential backoff (max 3 retries) upon user approval
4. **STATUS TRACKING**: Update workflow status to "function_{N}_failed"
5. **PRINT**: Failure message with function-level error details and BP research context
6. Await user decision on recovery action

### Auto Mode Failure Pattern
1. Detect failure in current function implementation or testing
2. **EXECUTION MODE HANDLING**: Stop workflow automatically without requiring human intervention
3. **RETRY LOGIC**: Implement configurable retry with exponential backoff (max 3 retries)
4. **STATUS TRACKING**: Update workflow status to "function_{N}_failed"
5. **PRINT**: Failure message with retry attempt information and BP research context
6. Proceed with retry logic automatically

### Complete Mode Failure Pattern
1. Detect failure in current function implementation or testing
2. **EXECUTION MODE HANDLING**: Continue workflow automatically, ignoring the failure
3. **RETRY LOGIC**: Implement configurable retry with exponential backoff (max 3 retries)
4. **STATUS TRACKING**: Update workflow status to "function_{N}_complete" (despite failure)
5. **PRINT**: Failure message but continue workflow
6. Proceed to next function automatically

## Executor BP Research Integration

### BP Research Requirements
- **CRITICAL REQUIREMENT**: Before any file creation or modification, perform **{BP}** web search for current best practices
- **CRITICAL REQUIREMENT**: Before test file creation, perform **{BP}** web search for current testing best practices
- **Documentation**: Document BP research findings and apply relevant best practices to implementation
- **Presentation**: Present BP research findings alongside function results to user
- **Validation**: Verify BP research was conducted and applied for all file operations in final validation

### BP Research Process
1. Analyze the specific function or file being created/modified
2. **{BP}** web search for current best practices relevant to the specific implementation
3. Document findings and determine applicable best practices
4. Apply relevant best practices to the implementation
5. Include BP research findings in function presentation to user
6. Document BP research findings in handoff to Reviewer agent

## Executor Retry Logic with Exponential Backoff

### Retry Configuration
- **Max Retries**: 3 retries maximum
- **Backoff Pattern**: Exponential backoff (1s, 2s, 4s, 8s, etc.)
- **Retry Criteria**: Configurable based on error type
- **Retry Logging**: Log each retry attempt with metadata
- **Function Retry**: For function implementation failures, retry specific function or related components

### Retry Implementation
```python
retry_count = 0
max_retries = 3
backoff_time = 1

while retry_count < max_retries:
    try:
        # Execute function implementation
        implement_function()
        break  # Success, exit retry loop
    except Exception as error:
        retry_count += 1
        if retry_count >= max_retries:
            raise  # Max retries reached
        time.sleep(backoff_time)
        backoff_time *= 2  # Exponential backoff
```

## Executor State Management

### Mode Storage
- **Mode Storage**: Store selected execution mode in workflow state
- **Function Progress**: Track current function number and implementation status
- **BP Research Log**: Store BP research findings for each function
- **Failure Context**: Store failure context for retry logic

### Audit Trail
- **Mode Selection**: Log mode selection with reasoning
- **Function Processing**: Log each function with BP research findings and outcomes
- **Failure Handling**: Log failure handling patterns and recovery actions
- **BP Research Documentation**: Log all BP research conducted during implementation
- **User Checkpoints**: Log user checkpoint decisions in Manual mode

## Executor Execution Mode Selection Guidelines

### Manual Mode Selection
- Critical infrastructure implementations
- Complex algorithm implementations
- Security-critical code modifications
- When learning new patterns or technologies
- User wants maximum oversight of each function

### Auto Mode Selection
- Standard plan implementations
- Well-understood implementation patterns
- When user wants some automation with safety
- Routine function implementations
- Established codebase patterns

### Complete Mode Selection
- Experimental or prototyping implementations
- Non-critical feature implementations
- When user wants maximum automation
- Rapid prototyping or exploration
- Tasks where function failures are acceptable