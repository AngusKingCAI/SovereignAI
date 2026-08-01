---
id: wf-ref-state-mgmt
status: active
owner: architect-agent
updated: 2026-07-28
purpose: Universal state management guidelines for all agent workflows
---

# State Management Guidelines

**Purpose**: Universal state management guidelines for all agent workflows.

## Universal State Management Structure

### Workflow State File
**Location**: `workflow_state.json` in current working directory
**Purpose**: Track workflow execution state for recovery and monitoring
**Format**: JSON-structured state data

### Universal State Schema
```json
{
  "workflow_id": "string",
  "agent_type": "string",
  "execution_strategy": "string",
  "current_phase": "string",
  "phase_status": "string",
  "start_time": "timestamp",
  "last_update": "timestamp",
  "total_steps": "number",
  "completed_steps": "number",
  "failed_steps": "number",
  "retry_count": "number",
  "session_metadata": {}
}
```

---

## Universal State Management Patterns

### Phase Status Tracking
**Status Values**:
- `phase_0_complete`: Rules loaded and ready
- `phase_{N}_in_progress`: Phase currently executing
- `phase_{N}_complete`: Phase successfully completed
- `phase_{N}_failed`: Phase failed, requires intervention
- `workflow_complete`: Entire workflow completed

**Update Pattern**:
1. Set status to `phase_{N}_in_progress` when starting phase
2. Update to `phase_{N}_complete` when phase succeeds
3. Update to `phase_{N}_failed` when phase fails
4. Maintain audit trail of all status changes

### Execution Strategy Storage
**Storage Pattern**:
- Store selected execution strategy in state file
- Maintain strategy throughout workflow execution
- Enable strategy changes with proper logging
- Track strategy effectiveness for future optimization

**Strategy Values**:
- `manual`: Manual oversight with checkpoints
- `auto`: Automatic progression with failure detection
- `complete`: Full automation with failure tolerance
- Agent-specific strategies as needed

### Error Recovery State
**Recovery State Management**:
- Track failure points and recovery actions
- Store retry count and backoff status
- Maintain recovery action history
- Enable recovery from any state point

**Recovery Metadata**:
```json
{
  "last_failure": {
    "phase": "string",
    "step": "number",
    "error": "string",
    "timestamp": "timestamp"
  },
  "retry_attempts": "number",
  "recovery_actions": ["array of actions"],
  "max_retries": "number"
}
```

---

## Universal Audit Trail Patterns

### State Change Logging
**Logging Requirements**:
- Log every state change with timestamp
- Include change reason and context
- Track user decisions and approvals
- Maintain complete execution history

**Log Entry Format**:
```json
{
  "timestamp": "timestamp",
  "event": "string",
  "previous_state": "object",
  "new_state": "object",
  "reason": "string",
  "context": "object"
}
```

### Session Metadata
**Metadata Requirements**:
- Session ID for tracking
- User identification
- Task description
- Execution context
- Resource usage tracking

**Metadata Schema**:
```json
{
  "session_id": "string",
  "user_id": "string",
  "task_description": "string",
  "execution_context": "object",
  "resource_usage": {
    "memory": "number",
    "cpu": "number",
    "time": "number"
  }
}
```

---

## Universal Recovery Patterns

### State Recovery
**Recovery Process**:
1. Load current state from workflow_state.json
2. Identify last successful state point
3. Determine recovery strategy
4. Execute recovery actions
5. Update state with recovery progress
6. Resume workflow execution

**Recovery Strategies**:
- **Retry with Backoff**: Exponential backoff for transient failures
- **Checkpoint Recovery**: Resume from last successful checkpoint
- **State Rollback**: Rollback to previous stable state
- **Manual Intervention**: Request user intervention for complex failures
- **Alternative Path**: Try alternative execution path

### Checkpoint Management
**Checkpoint Creation**:
- Create checkpoints at critical phase transitions
- Store checkpoint state for recovery
- Include checkpoint metadata for validation
- Enable rollback to any checkpoint

**Checkpoint Schema**:
```json
{
  "checkpoint_id": "string",
  "phase": "string",
  "step": "number",
  "state_snapshot": "object",
  "validation_hash": "string",
  "timestamp": "timestamp"
}
```

---

## Agent-Specific State Management

### Planner Agent State
**Planner-Specific State Elements**:
- Round Table iteration state
- Convergence metrics tracking
- Validation results history
- Plan revision tracking
- Panelist review aggregation state

**Additional State Schema**:
```json
{
  "planner_state": {
    "internal_iteration": "number",
    "external_iteration": "number",
    "convergence_metrics": {
      "findings_count": "number",
      "panelist_agreement": "number",
      "quality_score": "number"
    },
    "plan_revision": "string",
    "validation_results": "array"
  }
}
```

### Architect Agent State
**Architect-Specific State Elements**:
- Execution mode state
- Implementation mode selection
- Validation checkpoint state
- File placement compliance state
- Governance file update tracking

**Additional State Schema**:
```json
{
  "architect_state": {
    "execution_mode": "string",
    "implementation_mode": "string",
    "validation_checkpoints": "array",
    "file_compliance": "object",
    "governance_updates": "array"
  }
}
```

---

## Universal State Update Patterns

### State Update Rules
**Update Requirements**:
- Update state atomically to prevent corruption
- Validate state before persistence
- Include change metadata for audit trail
- Handle concurrent access safely
- Enable rollback on update failure

### State Persistence
**Persistence Requirements**:
- Persist state after each phase completion
- Persist state on error conditions
- Persist state on user decisions
- Persist state on strategy changes
- Maintain state file integrity

### State Validation
**Validation Requirements**:
- Validate state schema on load
- Validate state consistency before use
- Validate state transitions are legal
- Validate metadata completeness
- Validate no state corruption

---

## Universal State Monitoring

### State Health Monitoring
**Health Checks**:
- Monitor state file integrity
- Monitor state consistency
- Monitor state update frequency
- Monitor state size and complexity
- Monitor state access patterns

### State Performance Monitoring
**Performance Metrics**:
- State update latency
- State file size trends
- State access patterns
- Recovery success rates
- State corruption incidents

### State Analytics
**Analytics Requirements**:
- Track state transition patterns
- Analyze failure state patterns
- Analyze recovery success rates
- Analyze execution strategy effectiveness
- Generate state management insights

---

## Usage Guidelines

### State Management Implementation
1. **Initialize State**: Create initial state file at workflow start
2. **Update State**: Update state after each phase completion
3. **Handle Failures**: Update state on failures with recovery metadata
4. **Enable Recovery**: Enable recovery from any state point
5. **Maintain Audit Trail**: Maintain complete state change history

### State Management Best Practices
- **Atomic Updates**: Update state atomically to prevent corruption
- **Validation**: Always validate state before use
- **Backup**: Maintain state backups for recovery
- **Cleanup**: Clean up old state files periodically
- **Security**: Secure state files from unauthorized access

### State Recovery Best Practices
- **Multiple Recovery Points**: Enable recovery from multiple state points
- **Recovery Testing**: Test recovery mechanisms regularly
- **Recovery Documentation**: Document recovery procedures
- **Recovery Monitoring**: Monitor recovery success rates
- **Recovery Optimization**: Optimize recovery based on patterns