---
id: wf-rev-ref-review-mode-patterns
status: active
owner: reviewer-agent
updated: 2026-07-28
purpose: Reviewer-specific execution mode patterns for comprehensive file scanning workflows
---

# Reviewer Execution Mode Patterns

**Purpose**: Reviewer-specific execution mode patterns for comprehensive file scanning workflows.

## Execution Mode Definitions

### Manual Mode
**Behavior**: Process files one by one in alphabetical order, requiring user confirmation at each file for maximum oversight
- **Checkpoint Handling**: Require user confirmation via popup menu before proceeding to each next file
- **Failure Handling**: Stop workflow and await user intervention for retry/modify/abort decision
- **User Control**: Maximum user control over file-by-file progression
- **Risk Mitigation**: Human oversight at each file transition
- **Use Case**: First comprehensive scan, high-risk files, learning phase

### Manual Batched Mode
**Behavior**: Process files in batches of 5-10 files in alphabetical order, requiring user confirmation between batches
- **Checkpoint Handling**: Require user confirmation via popup menu before proceeding to each next batch
- **Failure Handling**: Stop workflow and await user intervention if batch fails
- **User Control**: Balanced user control with batch-level approval
- **Risk Mitigation**: Human oversight at each batch transition with automated intra-batch processing
- **Use Case**: Balanced efficiency with oversight, medium-risk scans

### Automatic Mode
**Behavior**: Process files one by one in alphabetical order automatically without user confirmation for maximum efficiency
- **Checkpoint Handling**: Proceed automatically to next file without user intervention
- **Failure Handling**: Stop workflow automatically if a file fails (auto-stop on errors)
- **User Control**: Minimal user control with maximum automated processing efficiency
- **Risk Mitigation**: Automatic failure detection and stopping at file level
- **Use Case**: Large codebases, established processes, maximum efficiency

### Automatic Batched Mode
**Behavior**: Process files in batches of 5-10 files in alphabetical order automatically without user confirmation
- **Checkpoint Handling**: Proceed automatically through all batches without user intervention
- **Failure Handling**: Stop workflow automatically if a batch fails (auto-stop on errors)
- **User Control**: Minimal user control with maximum automated processing efficiency
- **Risk Mitigation**: Automatic failure detection and stopping at batch level
- **Use Case**: Large codebases, established processes, maximum efficiency

## Execution Mode Handling Patterns

### Manual Mode Pattern
1. **SCAN** single file line by line
2. **{BP}** web search for current best practices (MANDATORY)
3. Document findings to incremental report
4. **EXECUTION MODE HANDLING**: Require user confirmation via popup menu before proceeding to next file (CHECKPOINT)
5. **STATUS TRACKING**: Update workflow status to "file_{N}_complete"
6. **PRINT**: File completion message with checkpoint confirmation
7. Wait for user approval before proceeding to next file

### Manual Batched Mode Pattern
1. **SCAN** batch of 5-10 files line by line
2. **{BP}** web search for all files in batch (MANDATORY)
3. Document findings to incremental report for all files
4. **EXECUTION MODE HANDLING**: Require user confirmation via popup menu before proceeding to next batch (CHECKPOINT)
5. **STATUS TRACKING**: Update workflow status to "batch_{N}_complete"
6. **PRINT**: Batch completion message with checkpoint confirmation
7. Wait for user approval before proceeding to next batch

### Automatic Mode Pattern
1. **SCAN** single file line by line
2. **{BP}** web search for current best practices (MANDATORY)
3. Document findings to incremental report
4. **EXECUTION MODE HANDLING**: Proceed automatically to next file if file succeeded, stop if file failed
5. **STATUS TRACKING**: Update workflow status to "file_{N}_complete" (success) or "file_{N}_failed" (failure)
6. **PRINT**: File completion message (success) or failure message with retry attempt information
7. Proceed automatically to next file on success, apply retry logic on failure

### Automatic Batched Mode Pattern
1. **SCAN** batch of 5-10 files line by line
2. **{BP}** web search for all files in batch (MANDATORY)
3. Document findings to incremental report for all files
4. **EXECUTION MODE HANDLING**: Proceed automatically to next batch if batch succeeded, stop if batch failed
5. **STATUS TRACKING**: Update workflow status to "batch_{N}_complete" (success) or "batch_{N}_failed" (failure)
6. **PRINT**: Batch completion message (success) or failure message with retry attempt information
7. Proceed automatically to next batch on success, apply retry logic on failure

## Failure Handling Patterns

### Manual Mode Failure Pattern
1. Detect failure in current file scan
2. **EXECUTION MODE HANDLING**: Stop workflow and await user intervention for retry/modify/abort decision (CHECKPOINT)
3. **RETRY LOGIC**: Implement configurable retry with exponential backoff (max 3 retries) upon user approval
4. **STATUS TRACKING**: Update workflow status to "file_{N}_failed"
5. **PRINT**: Failure message with file-level error details
6. Await user decision on recovery action

### Manual Batched Mode Failure Pattern
1. Detect failure in current batch
2. **EXECUTION MODE HANDLING**: Stop workflow and await user intervention for retry/modify/abort decision (CHECKPOINT)
3. **RETRY LOGIC**: Implement configurable retry with exponential backoff (max 3 retries) upon user approval
4. **STATUS TRACKING**: Update workflow status to "batch_{N}_failed"
5. **PRINT**: Failure message with batch-level error details
6. Await user decision on recovery action

### Automatic Mode Failure Pattern
1. Detect failure in current file scan
2. **EXECUTION MODE HANDLING**: Stop workflow automatically without requiring human intervention
3. **RETRY LOGIC**: Implement configurable retry with exponential backoff (max 3 retries)
4. **STATUS TRACKING**: Update workflow status to "file_{N}_failed"
5. **PRINT**: Failure message with retry attempt information
6. Proceed with retry logic automatically

### Automatic Batched Mode Failure Pattern
1. Detect failure in current batch
2. **EXECUTION MODE HANDLING**: Stop workflow automatically without requiring human intervention
3. **RETRY LOGIC**: Implement configurable retry with exponential backoff (max 3 retries)
4. **STATUS TRACKING**: Update workflow status to "batch_{N}_failed"
5. **PRINT**: Failure message with retry attempt information
6. Proceed with retry logic automatically

## Batch Configuration

### Batch Size Configuration
- **Default Batch Size**: 5-10 files per batch
- **Batch Size Criteria**: Based on file complexity and token usage
- **Dynamic Adjustment**: Adjust batch size based on available context budget
- **Batch Logging**: Log each batch with file list and processing metadata

### Batch Processing Order
- **Alphabetical Order**: Files processed in alphabetical order by full path
- **Batch Integrity**: All files in batch must complete before proceeding
- **Context Management**: PostCompaction hook reloads governance files when context is compressed
- **Incremental Documentation**: Findings documented immediately after each batch

## Execution Mode Selection Guidelines

### Manual Mode Selection
- First comprehensive scan of codebase
- High-risk or security-critical files
- Learning phase for new team members
- When detailed review of each file is required
- Unknown codebase or unfamiliar patterns

### Manual Batched Mode Selection
- Established scanning process
- Medium-risk codebase
- Balance between efficiency and oversight
- Regular compliance scans
- When batch-level review is sufficient

### Automatic Mode Selection
- Well-established scanning process
- Low-risk routine scans
- Time-constrained individual file processing
- When maximum efficiency for single files is required

### Automatic Batched Mode Selection
- Large codebases (>150 files)
- Well-established scanning process
- Low-risk routine scans
- Time-constrained comprehensive scans
- When maximum efficiency is required

## Retry Logic with Exponential Backoff

### Retry Configuration
- **Max Retries**: 3 retries maximum
- **Backoff Pattern**: Exponential backoff (1s, 2s, 4s, 8s, etc.)
- **Retry Criteria**: Configurable based on error type
- **Retry Logging**: Log each retry attempt with metadata
- **Batch Retry**: For batched modes, retry entire batch or individual items based on failure scope

### Retry Implementation
```python
retry_count = 0
max_retries = 3
backoff_time = 1

while retry_count < max_retries:
    try:
        # Execute file or batch scan
        execute_scan()
        break  # Success, exit retry loop
    except Exception as error:
        retry_count += 1
        if retry_count >= max_retries:
            raise  # Max retries reached
        time.sleep(backoff_time)
        backoff_time *= 2  # Exponential backoff
```

## State Management

### Mode Storage
- **Mode Storage**: Store selected execution mode in workflow state
- **Batch Size**: Store configured batch size for consistency
- **Current Batch**: Track current batch number and file indices
- **Failure Context**: Store failure context for retry logic

### Audit Trail
- **Mode Selection**: Log mode selection with reasoning
- **Batch Processing**: Log each batch with file list and outcomes
- **Failure Handling**: Log failure handling patterns and recovery actions
- **User Checkpoints**: Log user checkpoint decisions in Manual modes