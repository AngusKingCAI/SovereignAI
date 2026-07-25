# Hook-Based Gate System Architecture

## Overview

Convert the manual gate system to an automatic hook-based system using Devin CLI's lifecycle hooks. This provides real-time governance enforcement instead of periodic manual checks.

## Architecture Design

### Core Components

#### 1. Hook Configuration (.devin/hooks.v1.json)
- **SessionStart Hook**: Initialize session, load phase state, validate environment
- **PreToolUse Hook**: Enforce permissions, check phase scope, block dangerous operations
- **PostToolUse Hook**: Log operations, update state, verify integrity
- **SessionEnd Hook**: Final validation, generate reports, cleanup

#### 2. Hook Scripts (Scripts/Governance/Hooks/)
- **session_init.py**: Session initialization and state loading
- **tool_permission_check.py**: Pre-tool use permission validation
- **operation_logger.py**: Post-tool use logging and state updates
- **session_finalization.py**: Session end validation and reporting

#### 3. State Management (Scripts/Governance/State/)
- **phase_state_manager.py**: Manage phase state files
- **integrity_validator.py**: Cryptographic integrity verification
- **permission_engine.py**: Phase-based permission system

#### 4. Configuration (Scripts/Governance/Config/)
- **phase_permissions.json**: Define allowed operations per phase
- **governance_rules.json**: Governance rule definitions
- **hook_config.json**: Hook system configuration

## Hook Event Mapping

### SessionStart Hook
**Purpose**: Initialize governance environment
**Actions**:
- Load current phase state from `Logs/Architect/Gates/`
- Validate environment configuration
- Initialize session audit log
- Check for incomplete previous sessions
- Set up governance context

**Exit Codes**:
- 0: Session initialized successfully
- 2: Block session (environment issues, incomplete previous session)

### PreToolUse Hook
**Purpose**: Real-time permission enforcement
**Actions**:
- Check if tool is allowed in current phase
- Validate operation against governance rules
- Check for file write permissions (governance file protection)
- Verify phase completion prerequisites
- Apply scope restrictions

**Exit Codes**:
- 0: Tool execution allowed
- 2: Block tool (permission denied, phase incomplete, governance violation)

### PostToolUse Hook
**Purpose**: Operation logging and state updates
**Actions**:
- Log tool execution to audit trail
- Update operation counters
- Verify file integrity after writes
- Check for governance violations
- Update state if phase completion criteria met

**Exit Codes**:
- 0: Logging successful (doesn't block operation)
- Other: Log error (operation still succeeded)

### SessionEnd Hook
**Purpose**: Final validation and cleanup
**Actions**:
- Verify all required operations completed
- Generate session compliance report
- Validate cryptographic integrity
- Check phase completion status
- Clean up temporary files
- Archive session logs

**Exit Codes**:
- 0: Session end successful
- 2: Block session closure (critical violations)

## Phase Permission System

### Phase Definitions
- **Phase 0**: Repository Foundation - infrastructure setup only
- **Phase 1**: Rule System - rule file creation and validation
- **Phase 2**: Workflow Design - workflow creation and structure
- **Phase 3**: Gate Implementation - hook system setup
- **Phase 4**: Testing - validation and testing
- **Phase 5**: Documentation - final documentation

### Permission Matrix
```json
{
  "phase_0": {
    "allowed_tools": ["read", "exec"],
    "allowed_file_operations": ["create:Scripts/", "create:Rules/", "create:Docs/"],
    "forbidden_operations": ["modify:App/", "delete:*"],
    "required_completions": []
  },
  "phase_1": {
    "allowed_tools": ["read", "write", "edit"],
    "allowed_file_operations": ["modify:Rules/", "create:Rules/"],
    "forbidden_operations": ["modify:App/", "delete:Rules/"],
    "required_completions": ["phase_0"]
  }
}
```

## State File Structure

### Maintain Compatibility
Keep existing state file structure for backward compatibility:
```json
{
  "phase": "1",
  "phase_name": "Rule System",
  "completion_hash": "abc123...",
  "state_hash": "def456...",
  "timestamp": "2026-07-24T12:00:00Z",
  "completion_signature": "architect-approved",
  "previous_phase_hash": "ghi789...",
  "state_files": ["file1.md", "file2.py"],
  "metadata": {
    "specification_status": "complete",
    "implementation_status": "complete",
    "test_status": "passing"
  }
}
```

### Hook-Specific Extensions
Add hook-specific metadata:
```json
{
  "hook_metadata": {
    "session_id": "session-uuid",
    "operations_count": 15,
    "violations_count": 0,
    "last_operation": "2026-07-24T12:30:00Z"
  }
}
```

## Implementation Priority

### Phase 1: Core Hook Infrastructure
1. Create `.devin/hooks.v1.json` with basic hook structure
2. Implement `session_init.py` for SessionStart
3. Implement `session_finalization.py` for SessionEnd
4. Test basic hook functionality

### Phase 2: Permission System
1. Implement `tool_permission_check.py` for PreToolUse
2. Create phase permission configuration
3. Implement permission engine
4. Test permission enforcement

### Phase 3: Logging and State
1. Implement `operation_logger.py` for PostToolUse
2. Implement state management system
3. Add integrity verification
4. Test logging and state updates

### Phase 4: Advanced Features
1. Implement governance rule validation
2. Add compliance reporting
3. Implement phase transition logic
4. Add cryptographic verification

### Phase 5: Migration
1. Archive old gate system scripts
2. Update workflow documentation
3. Train agents on new system
4. Remove manual gate invocation

## Migration Strategy

### Compatibility Mode
- Keep old state file structure
- Support manual gate invocation as fallback
- Gradual migration of agents to hook system
- Parallel operation during transition

### Rollback Plan
- Keep old scripts archived
- Disable hooks via configuration if needed
- Restore manual gate system if hooks fail
- Data migration scripts if needed

## Benefits of Hook System

### Immediate Benefits
- **Automatic Enforcement**: No manual script invocation needed
- **Real-time Validation**: Every operation checked immediately
- **Better Security**: Prevents violations before they happen
- **Reduced Error**: Eliminates manual gate invocation mistakes

### Long-term Benefits
- **Scalability**: Easier to add new governance rules
- **Maintainability**: Centralized hook configuration
- **Auditability**: Comprehensive operation logging
- **Flexibility**: Easy to adjust permissions per phase

## Testing Strategy

### Unit Tests
- Test each hook script independently
- Test permission engine logic
- Test state management operations
- Test integrity verification

### Integration Tests
- Test hook system with Devin CLI
- Test phase transitions
- Test permission enforcement
- Test state file compatibility

### Regression Tests
- Ensure old state files still work
- Test manual gate fallback
- Test data migration
- Test rollback procedures

## Monitoring and Debugging

### Hook Execution Logs
- Log all hook invocations
- Log permission decisions
- Log state changes
- Log errors and warnings

### Debug Mode
- Enable verbose logging
- Show permission decisions
- Show state file operations
- Show integrity checks

### Performance Monitoring
- Track hook execution time
- Monitor state file operations
- Check for hook failures
- Monitor system resources

## Configuration Examples

### Basic Hook Configuration
```json
{
  "SessionStart": [
    {
      "hooks": [
        {
          "type": "command",
          "command": "python Scripts/Governance/Hooks/session_init.py",
          "timeout": 30
        }
      ]
    }
  ],
  "PreToolUse": [
    {
      "matcher": "*",
      "hooks": [
        {
          "type": "command",
          "command": "python Scripts/Governance/Hooks/tool_permission_check.py",
          "timeout": 10
        }
      ]
    }
  ]
}
```

### Advanced Configuration with Multiple Hooks
```json
{
  "PreToolUse": [
    {
      "matcher": "^(edit|write)$",
      "hooks": [
        {
          "type": "command",
          "command": "python Scripts/Governance/Hooks/tool_permission_check.py --type=file-write",
          "timeout": 10
        },
        {
          "type": "command",
          "command": "python Scripts/Governance/Hooks/integrity_check.py --pre-write",
          "timeout": 5
        }
      ]
    }
  ]
}
```

## Success Criteria

### Functional Requirements
- ✅ Hooks trigger automatically at lifecycle events
- ✅ Permissions enforced at tool level
- ✅ State files maintained automatically
- ✅ Integrity verification performed
- ✅ Session lifecycle managed properly

### Non-Functional Requirements
- ✅ Hook execution doesn't significantly impact performance
- ✅ System maintains backward compatibility
- ✅ Comprehensive logging for debugging
- ✅ Easy to configure and maintain
- ✅ Robust error handling and recovery

### Migration Requirements
- ✅ Old state files remain compatible
- ✅ Manual gate system available as fallback
- ✅ Agents can use either system during transition
- ✅ No data loss during migration
- ✅ Clear rollback path if needed