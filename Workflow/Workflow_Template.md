# {Title}

**ID**: {WorkflowID}  
**Owner**: {Agent} Agent  
**Frequency**: {Frequency}  
**Duration**: {Duration}  
**Priority**: {Priority}

## Purpose
{What this workflow accomplishes and why it exists}

## Roles and Owners
- **{Agent} Agent**: Executes workflow steps, enforces governance rules
- **User**: Provides task requirements, approves decisions
- **Governance System**: Automatic enforcement via hooks (non-manual)

## Trigger and End State
- **Trigger**: {What triggers this workflow}
- **End State**: {What constitutes workflow completion}

## Workflow Steps

### 1. {Step Name}
- **ACTION**: {Specific action description}
- **ACTION**: {Additional actions as needed}
- **VERBOSE LOG**: "{Description of what was logged for transparency}"

### 2. {Step Name}
- **ACTION**: {Specific action description}
- **ACTION**: {Additional actions as needed}
- **VERBOSE LOG**: "{Description of what was logged for transparency}"

### 3. {Step Name}
- **ACTION**: {Specific action description}
- **ACTION**: {Additional actions as needed}
- **VERBOSE LOG**: "{Description of what was logged for transparency}"

### 4. {Step Name}
- **ACTION**: {Specific action description}
- **ACTION**: {Additional actions as needed}
- **VERBOSE LOG**: "{Description of what was logged for transparency}"

### 5. {Step Name}
- **ACTION**: {Specific action description}
- **ACTION**: {Additional actions as needed}
- **VERBOSE LOG**: "{Description of what was logged for transparency}"

### 6. {Step Name}
- **ACTION**: {Specific action description}
- **ACTION**: {Additional actions as needed}
- **VERBOSE LOG**: "{Description of what was logged for transparency}"

### 7. {Step Name}
- **ACTION**: {Specific action description}
- **ACTION**: {Additional actions as needed}
- **VERBOSE LOG**: "{Description of what was logged for transparency}"

### 8. {Step Name}
- **ACTION**: {Specific action description}
- **ACTION**: {Additional actions as needed}
- **VERBOSE LOG**: "{Description of what was logged for transparency}"

### 9. Return to Step 1
- **ACTION**: After completing workflow, return to Step 1
- **ACTION**: This makes the workflow repeatable for continuous work
- **ACTION**: Ready for next task
- **VERBOSE LOG**: "Workflow cycle complete - returning to Step 1 for next task"
- **VERBOSE LOG**: "{Agent} agent ready - awaiting next user request"

## Hook-Based Gate System Integration

### Automatic Enforcement
- **HOOK SYSTEM**: Scripts/Gating/Hooks/ provides automatic governance enforcement
- **SESSION START**: SessionStart hook initializes governance environment
- **PRE-TOOL USE**: PreToolUse hook validates permissions before each tool execution
- **POST-TOOL USE**: PostToolUse hook logs all operations to audit trail
- **SESSION END**: SessionEnd hook performs final validation and cleanup

### Phase-Based Permissions
- **PHASE 0**: Repository Foundation - infrastructure setup only (read, exec tools)
- **PHASE 1**: Rule System - rule file creation and validation (read, write, edit tools)
- **PHASE 2**: Workflow Design - workflow creation and structure (read, write, edit tools)
- **PHASE 3**: Gate Implementation - hook system setup and governance (read, write, edit, exec tools)
- **PHASE 4**: Testing - validation and testing (read, write, edit, exec tools)
- **PHASE 5**: Documentation - final documentation (read, write, edit tools)

### Compliance Verification
- **AUTOMATIC CHECKS**: Hook system automatically validates permissions at tool execution time
- **PHASE VALIDATION**: Required phase completions checked before allowing operations
- **FILE PROTECTION**: Core governance files automatically protected from modification
- **AUDIT TRAIL**: All operations automatically logged to Logs/{Agent}/Gating/audit-trail.log
- **SESSION TRACKING**: Session context maintained in Logs/{Agent}/Gating/session-context.json

### Verbose Action Logging
- **EVERY ACTION**: Each workflow step includes explicit ACTION markers
- **VERBOSE LOG**: Each step includes VERBOSE LOG statements for chat output
- **TRANSPARENCY**: All actions explicitly stated in workflow execution
- **OBSERVABILITY**: Complete audit trail of workflow step execution
- **ACCOUNTABILITY**: Every action logged and visible in agent communication

## Integration Points

### Hook Configuration
- **FILE**: .devin/hooks.v1.json
- **SESSION START**: session_init.py hook
- **PRE-TOOL USE**: tool_permission_check.py hook
- **POST-TOOL USE**: operation_logger.py hook
- **SESSION END**: session_finalization.py hook

### Phase Permissions
- **CONFIGURATION**: Scripts/Gating/Config/phase_permissions.json
- **STATE MANAGEMENT**: Logs/{Agent}/Gating/phase-{N}-state.json
- **SESSION CONTEXT**: Logs/{Agent}/Gating/session-context.json
- **AUDIT TRAIL**: Logs/{Agent}/Gating/audit-trail.log

### {Agent} Rules Compliance
- **CONSTRAINTS**: Rules/{Agent}/{Agent}_Rules.md constraints enforced
- **FILE PLACEMENT**: Scripts/Gating/ category per architect rules
- **TESTING REQUIREMENT**: Never test in isolated environments, always test in actual project context
- **GOVERNANCE COMPLIANCE**: Hook system provides automatic enforcement without manual invocation