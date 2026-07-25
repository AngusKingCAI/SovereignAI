# Hook-Based Gate System Documentation

## Overview

The SovereignAI hook-based gate system provides automatic, real-time governance enforcement using Devin CLI's lifecycle hooks. This replaces the manual gate invocation system with automatic enforcement at every tool execution.

## System Architecture

### Hook Configuration
**File**: `.devin/hooks.v1.json`

The hook system uses four lifecycle hooks:

1. **SessionStart Hook**: Initializes governance environment
2. **PreToolUse Hook**: Enforces permissions before tool execution
3. **PostToolUse Hook**: Logs operations and updates state after execution
4. **SessionEnd Hook**: Final validation and cleanup

### Hook Scripts
**Location**: `Scripts/Governance/Hooks/`

- **session_init.py**: Session initialization and state loading
- **tool_permission_check.py**: Pre-tool use permission validation
- **operation_logger.py**: Post-tool use logging and state updates
- **session_finalization.py**: Session end validation and reporting

### Configuration Files
**Location**: `Scripts/Governance/Config/`

- **phase_permissions.json**: Phase-based permission definitions
- **governance_rules.json**: Governance rule definitions and hook configuration

## Phase System

### Phase Definitions
- **Phase 0**: Repository Foundation - infrastructure setup only
- **Phase 1**: Rule System - rule file creation and validation
- **Phase 2**: Workflow Design - workflow creation and structure
- **Phase 3**: Gate Implementation - hook system setup and governance
- **Phase 4**: Testing - validation and testing
- **Phase 5**: Documentation - final documentation

### Phase Progression
Phases must be completed in order. Each phase requires completion of all previous phases.

## Permission System

### Tool-Level Permissions
Each phase defines:
- **Allowed Tools**: Which tools can be used (read, write, edit, exec)
- **Allowed File Operations**: Which file operations are permitted
- **Forbidden Operations**: Operations that are explicitly blocked
- **Required Completions**: Which previous phases must be complete

### Governance Rules
- **File Protection**: Core governance files cannot be modified
- **Operation Restrictions**: Dangerous commands require special approval
- **Phase Requirements**: Completion verification, integrity checking, audit logging
- **Compliance Thresholds**: Minimum completeness, maximum violations

## State Management

### State Files
**Location**: `Logs/Architect/Gates/phase-{N}-state.json`

State files track:
- Phase number and name
- Completion hash (cryptographic verification)
- State hash (integrity verification)
- Timestamp and completion signature
- Previous phase hash (chain verification)
- State files list
- Metadata (specification, implementation, test status)

### Session Context
**Location**: `Logs/Architect/Gates/session-context.json`

Session context includes:
- Session ID (UUID)
- Timestamp
- Current phase
- Project root and state directory paths
- Environment validity
- Operation counters

## Audit Trail

### Audit Log
**Location**: `Logs/Architect/Gates/audit-trail.log`

Logs all:
- Session start/end events
- Tool executions with tool name, file path, phase, session ID
- Permission decisions
- State changes
- Violations and warnings

## Usage

### Agent Workflow Integration

1. **Session Start**: Hook automatically initializes governance environment
2. **Tool Execution**: PreToolUse hook checks permissions automatically
3. **Operation Logging**: PostToolUse hook logs all operations automatically
4. **Session End**: SessionEnd hook performs final validation automatically

### Phase Transition

1. **Complete Current Phase**: Mark phase as complete in state file
2. **Update State**: Hook system automatically updates state metadata
3. **Move to Next Phase**: Agent can proceed to next phase
4. **Permission Update**: New phase permissions automatically apply

### Manual Phase Recording

For manual phase completion (optional):

```bash
# Record phase completion
bash Scripts/Architect/Gates/record-phase-complete.sh <phase_number> <signature>
```

## Configuration

### Modify Phase Permissions

Edit `Scripts/Governance/Config/phase_permissions.json`:

```json
{
  "phase_3": {
    "name": "Gate Implementation",
    "allowed_tools": ["read", "write", "edit", "exec"],
    "allowed_file_operations": [
      "modify:Scripts/Governance/",
      "create:Scripts/Governance/",
      "modify:.devin/",
      "read:*"
    ],
    "forbidden_operations": [
      "modify:App/",
      "delete:Scripts/Governance/",
      "modify:.git/"
    ],
    "required_completions": ["phase_2"],
    "description": "Hook system setup and governance"
  }
}
```

### Modify Governance Rules

Edit `Scripts/Governance/Config/governance_rules.json`:

```json
{
  "governance_rules": {
    "file_protection": {
      "protected_files": [
        ".git/",
        "App/",
        "Rules/Architect/IDE_Architecture_Rules.md"
      ],
      "protection_level": "strict"
    }
  }
}
```

### Configure Hook Behavior

Edit hook configuration in `governance_rules.json`:

```json
{
  "hook_configuration": {
    "session_init": {
      "load_state": true,
      "validate_environment": true,
      "check_incomplete_sessions": true,
      "initialize_audit_log": true,
      "timeout": 30
    }
  }
}
```

## Troubleshooting

### Hooks Not Triggering

1. Check `.devin/hooks.v1.json` exists and is valid JSON
2. Verify hook scripts are executable (`chmod +x Scripts/Governance/Hooks/*.py`)
3. Check hook configuration is correct
4. Test hooks manually with `python Scripts/Governance/Hooks/session_init.py`

### Permission Blocking

1. Check current phase in `Logs/Architect/Gates/session-context.json`
2. Verify phase permissions in `Scripts/Governance/Config/phase_permissions.json`
3. Check previous phase completion status
4. Review audit trail for permission decisions

### State File Issues

1. Validate JSON syntax of state files
2. Check state file permissions
3. Verify state file paths are correct
4. Review hook logs for state file errors

## Migration from Manual Gates

### Compatibility

The hook system maintains compatibility with:
- Existing state file structure
- Manual gate invocation scripts
- Previous phase state files

### Transition

1. **Phase 1**: Both systems run in parallel
2. **Phase 2**: Manual gates become optional
3. **Phase 3**: Manual gates deprecated
4. **Phase 4**: Manual gates archived

### Rollback

If hooks need to be disabled:
1. Remove or rename `.devin/hooks.v1.json`
2. Manual gate scripts remain available
3. State files remain compatible
4. No data loss occurs

## Benefits

### Automatic Enforcement
- No manual script invocation required
- Every operation checked automatically
- Consistent enforcement across all agents

### Real-Time Validation
- Permissions checked before execution
- Violations blocked immediately
- Comprehensive operation logging

### Better Security
- Prevents violations before they happen
- Cryptographic integrity verification
- Comprehensive audit trail

### Improved Maintainability
- Centralized hook configuration
- Clear permission definitions
- Easier to add new governance rules

## Monitoring

### Hook Execution Monitoring

Check audit trail:
```bash
cat Logs/Architect/Gates/audit-trail.log
```

### Session Context Monitoring

Check current session:
```bash
cat Logs/Architect/Gates/session-context.json
```

### State File Monitoring

Check phase states:
```bash
ls -la Logs/Architect/Gates/phase-*-state.json
```

## Future Enhancements

### Planned Features
- Advanced permission matching patterns
- Multi-agent session coordination
- Real-time compliance dashboards
- Automated violation remediation
- Enhanced cryptographic verification

### Extension Points
- Custom permission engines
- Additional hook events
- Plugin system for governance rules
- Integration with external compliance systems

## Support

For issues or questions:
1. Check audit trail for detailed error information
2. Review hook script logs for execution details
3. Validate configuration files for syntax errors
4. Test hooks manually to isolate issues