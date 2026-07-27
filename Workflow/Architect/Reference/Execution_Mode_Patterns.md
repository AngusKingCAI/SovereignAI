# Architect Execution Mode Patterns

**Purpose**: Architect-specific execution mode patterns for infrastructure and governance workflows.

## Architect Execution Mode Definitions

### Full Comprehensive Mode
**Behavior**: Execute all 12 consistency variables for complete architecture validation
- **Scope**: All consistency checks (file references, terminology, workflow structure, governance rules, documentation, agent capabilities, framework coverage, execution strategy, state management, runtime prerequisites, scoring scale, behavior rules)
- **Checkpoint Handling**: Proceed automatically through all consistency checks
- **Failure Handling**: Continue workflow automatically, logging failures but completing full scan
- **User Control**: Minimal user control with maximum coverage
- **Use Case**: Monthly comprehensive scans, before/after major architectural changes

### Basic Essential Mode
**Behavior**: Execute essential consistency variables for quick validation
- **Scope**: File references + terminology + workflow structure (3 core variables)
- **Checkpoint Handling**: Proceed automatically through essential checks
- **Failure Handling**: Stop workflow automatically if essential check fails
- **User Control**: Balanced user control with essential coverage
- **Use Case**: Weekly basic scans, quick validation before changes

### Targeted Mode
**Behavior**: Execute user-selected consistency variables for focused validation
- **Scope**: User selects specific consistency variables from available 12
- **Checkpoint Handling**: Proceed automatically through selected checks
- **Failure Handling**: Stop workflow automatically if selected check fails
- **User Control**: Maximum user control with focused coverage
- **Use Case**: Investigating specific architectural concerns, targeted validation

### Quick Check Mode
**Behavior**: Execute file reference consistency only for rapid validation
- **Scope**: File references only (1 variable)
- **Checkpoint Handling**: Proceed automatically through file reference check
- **Failure Handling**: Stop workflow automatically if file reference check fails
- **User Control**: Minimal user control with rapid validation
- **Use Case**: Pre-change validation, quick reference checks

## Architect Execution Mode Handling Patterns

### Full Comprehensive Mode Pattern
1. Execute all 12 consistency variables sequentially
2. **SCAN** each governance file line by line for comprehensive examination
3. **EXECUTION MODE HANDLING**: Proceed automatically through all checks regardless of individual failures
4. **STATUS TRACKING**: Update workflow status for each consistency variable
5. **PRINT**: Progress updates for each consistency variable
6. Continue to next consistency variable automatically
7. Generate comprehensive report with all findings

### Basic Essential Mode Pattern
1. Execute 3 essential consistency variables (file references, terminology, workflow structure)
2. **SCAN** each governance file line by line for essential examination
3. **EXECUTION MODE HANDLING**: Proceed automatically through essential checks, stop on failure
4. **STATUS TRACKING**: Update workflow status for each essential variable
5. **PRINT**: Progress updates for each essential variable
6. Proceed to next essential variable on success, stop on failure
7. Generate basic report with essential findings

### Targeted Mode Pattern
1. User selects specific consistency variables from available 12
2. **SCAN** each governance file line by line for selected examination
3. **EXECUTION MODE HANDLING**: Proceed automatically through selected checks, stop on failure
4. **STATUS TRACKING**: Update workflow status for each selected variable
5. **PRINT**: Progress updates for each selected variable
6. Proceed to next selected variable on success, stop on failure
7. Generate targeted report with selected findings

### Quick Check Mode Pattern
1. Execute file reference consistency check only
2. **SCAN** each governance file line by line for file reference examination
3. **EXECUTION MODE HANDLING**: Proceed automatically through file reference check, stop on failure
4. **STATUS TRACKING**: Update workflow status for file reference check
5. **PRINT**: Progress updates for file reference check
6. Generate quick report with file reference findings

## Architect Failure Handling Patterns

### Full Comprehensive Mode Failure Pattern
1. Detect failure in current consistency variable check
2. **EXECUTION MODE HANDLING**: Continue workflow automatically, logging the failure
3. **RETRY LOGIC**: Implement configurable retry with exponential backoff (max 3 retries)
4. **STATUS TRACKING**: Update workflow status to "variable_{N}_failed" but continue workflow
5. **PRINT**: Failure message but continue to next consistency variable
6. Proceed to next consistency variable automatically

### Basic Essential Mode Failure Pattern
1. Detect failure in current essential variable check
2. **EXECUTION MODE HANDLING**: Stop workflow automatically without requiring human intervention
3. **RETRY LOGIC**: Implement configurable retry with exponential backoff (max 3 retries)
4. **STATUS TRACKING**: Update workflow status to "variable_{N}_failed"
5. **PRINT**: Failure message with retry attempt information
6. Proceed with retry logic automatically, stop if max retries reached

### Targeted Mode Failure Pattern
1. Detect failure in current selected variable check
2. **EXECUTION MODE HANDLING**: Stop workflow automatically without requiring human intervention
3. **RETRY LOGIC**: Implement configurable retry with exponential backoff (max 3 retries)
4. **STATUS TRACKING**: Update workflow status to "variable_{N}_failed"
5. **PRINT**: Failure message with retry attempt information
6. Proceed with retry logic automatically, stop if max retries reached

### Quick Check Mode Failure Pattern
1. Detect failure in file reference check
2. **EXECUTION MODE HANDLING**: Stop workflow automatically without requiring human intervention
3. **RETRY LOGIC**: Implement configurable retry with exponential backoff (max 3 retries)
4. **STATUS TRACKING**: Update workflow status to "file_reference_failed"
5. **PRINT**: Failure message with retry attempt information
6. Proceed with retry logic automatically, stop if max retries reached

## Architect Execution Mode Selection Guidelines

### Full Comprehensive Mode Selection
- Monthly comprehensive architecture validation
- Before major architectural changes
- After major architectural refactoring
- Complete governance health assessment
- When comprehensive baseline is needed

### Basic Essential Mode Selection
- Weekly basic architecture validation
- Quick validation before minor changes
- Essential consistency health check
- When core architecture validation is sufficient
- Time-constrained validation needs

### Targeted Mode Selection
- Investigating specific architectural concerns
- Validating specific consistency variables
- Focused architecture validation
- When specific areas need attention
- User has specific validation requirements

### Quick Check Mode Selection
- Pre-change validation for file references
- Quick reference validation
- Rapid architecture validation
- When only file reference integrity is needed
- Time-critical validation needs

## Architect Retry Logic with Exponential Backoff

### Retry Configuration
- **Max Retries**: 3 retries maximum
- **Backoff Pattern**: Exponential backoff (1s, 2s, 4s, 8s, etc.)
- **Retry Criteria**: Configurable based on error type
- **Retry Logging**: Log each retry attempt with metadata
- **Variable Retry**: For targeted checks, retry individual consistency variables

### Retry Implementation
```python
retry_count = 0
max_retries = 3
backoff_time = 1

while retry_count < max_retries:
    try:
        # Execute consistency variable check
        execute_consistency_check()
        break  # Success, exit retry loop
    except Exception as error:
        retry_count += 1
        if retry_count >= max_retries:
            raise  # Max retries reached
        time.sleep(backoff_time)
        backoff_time *= 2  # Exponential backoff
```

## Architect State Management

### Mode Storage
- **Mode Storage**: Store selected execution mode in workflow state
- **Variable Selection**: Store selected consistency variables for Targeted mode
- **Current Variable**: Track current consistency variable being checked
- **Failure Context**: Store failure context for retry logic

### Audit Trail
- **Mode Selection**: Log mode selection with reasoning
- **Variable Processing**: Log each consistency variable with outcomes
- **Failure Handling**: Log failure handling patterns and recovery actions
- **Report Generation**: Log report generation with consistency metrics