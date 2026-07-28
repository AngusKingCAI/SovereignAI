---
id: wf-rev-ref-review-mode-patterns
status: active
owner: reviewer-agent
updated: 2026-07-28
purpose: Reviewer-specific execution mode patterns for comprehensive code review workflows
---

# Review Mode Patterns

**Purpose**: Reviewer-specific execution mode patterns for comprehensive code review workflows.

## Review Mode Definitions

### Manual Review Mode
**Behavior**: Require user confirmation at every single review step for maximum oversight
- **Checkpoint Handling**: Require user confirmation via popup menu before proceeding to each next review step (every step, not just failures)
- **Failure Handling**: Stop review and await user intervention for retry/modify/abort decision
- **User Control**: Maximum user control over review progression with step-by-step approval
- **Risk Mitigation**: Human oversight at each review transition and every workflow step

### Auto Review Mode
**Behavior**: Don't continue on review failures (auto-stop on errors, proceed automatically through successes)
- **Checkpoint Handling**: Proceed automatically to next review step
- **Failure Handling**: Stop review automatically without requiring human intervention
- **Efficiency**: Balanced efficiency with failure detection
- **Risk Mitigation**: Automatic failure detection and stopping

### Complete Review Mode
**Behavior**: Continue past review failures (ignore all errors for maximum coverage)
- **Checkpoint Handling**: Proceed automatically to next review step
- **Failure Handling**: Continue review automatically, ignoring failures
- **Efficiency**: Maximum efficiency with failure tolerance
- **Risk Mitigation**: Minimal risk mitigation

## Review Mode Handling Patterns

### Step Transition Handling
**Manual Review Mode Pattern**:
1. Complete current review step action
2. **EXECUTION MODE HANDLING**: Require user confirmation via popup menu before proceeding to next review step (CHECKPOINT at every step)
3. **STATUS TRACKING**: Update workflow status to "step_{N}_complete"
4. **PRINT**: Review step completion message with checkpoint confirmation
5. Wait for user approval before proceeding to next review step

**Auto Review Mode Pattern**:
1. Complete current review step action
2. **EXECUTION MODE HANDLING**: Proceed automatically to next review step if step succeeded, stop if step failed
3. **STATUS TRACKING**: Update workflow status to "step_{N}_complete" (success) or "step_{N}_failed" (failure)
4. **PRINT**: Review step completion message (success) or failure message with retry attempt information
5. Proceed automatically to next review step on success, apply retry logic on failure

**Complete Review Mode Pattern**:
1. Complete current review step action (even if failures occur)
2. **EXECUTION MODE HANDLING**: Proceed automatically to next review step regardless of success/failure
3. **STATUS TRACKING**: Update workflow status to "step_{N}_complete" (even if step failed)
4. **PRINT**: Review step completion message (including any failures but continue review)
5. Proceed to next review step automatically

### Failure Handling Patterns
**Manual Review Mode Failure Pattern**:
1. Detect failure in current review step
2. **EXECUTION MODE HANDLING**: Stop review and await user intervention for retry/modify/abort decision (CHECKPOINT)
3. **STATUS TRACKING**: Update workflow status to "step_{N}_failed"
4. **PRINT**: Failure message with error details
5. Await user decision on recovery action

**Auto Review Mode Failure Pattern**:
1. Detect failure in current review step
2. **EXECUTION MODE HANDLING**: Stop review automatically without requiring human intervention
3. **RETRY LOGIC**: Implement configurable retry with exponential backoff (max 3 retries)
4. **STATUS TRACKING**: Update workflow status to "step_{N}_failed"
5. **PRINT**: Failure message with retry attempt information
6. Proceed with retry logic automatically

**Complete Review Mode Failure Pattern**:
1. Detect failure in current review step
2. **EXECUTION MODE HANDLING**: Continue review automatically, ignoring the failure
3. **RETRY LOGIC**: Implement configurable retry with exponential backoff (max 3 retries)
4. **STATUS TRACKING**: Update workflow status to "step_{N}_complete" (despite failure)
5. **PRINT**: Failure message but continue review
6. Proceed to next review step automatically

## Review-Specific Patterns

### File-by-File Review Pattern
**Manual Mode**: Require user confirmation before proceeding to examine each file
**Auto Mode**: Automatically proceed through files sequentially, stop on critical failures
**Complete Mode**: Automatically proceed through all files regardless of findings

### Subagent Coordination Pattern
**Manual Mode**: Require user confirmation before launching each subagent
**Auto Mode**: Automatically launch subagents according to coordination strategy
**Complete Mode**: Automatically launch all subagents regardless of individual failures

### Findings Consolidation Pattern
**Manual Mode**: Require user confirmation before proceeding to consolidate each category of findings
**Auto Mode**: Automatically consolidate findings as subagent results arrive
**Complete Mode**: Automatically consolidate all findings regardless of subagent failures

## Usage Guidelines

### Mode Selection Process
1. **Assess Review Scope**: Evaluate review complexity and file count
2. **Present Options**: Present review mode options to user
3. **Recommend**: Recommend appropriate mode based on assessment
4. **User Selection**: User selects mode via popup menu
5. **Store Mode**: Store selected review mode in workflow state

### Mode Execution
1. **Apply Pattern**: Apply appropriate review mode pattern
2. **Handle Checkpoints**: Handle checkpoints according to mode
3. **Handle Failures**: Handle failures according to mode
4. **Track Progress**: Track progress according to mode requirements
5. **Log Actions**: Log mode-specific actions for audit trail