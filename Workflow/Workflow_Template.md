# {Title}

**File**: {FileName}.md  
**Workflow Name**: {WorkflowName}  
**Description**: {Description}  
**Status**: {Agent} Agent Standard  
**Template Compliance**: Verified  
**Hook-Based Governance**: Enabled (automatic enforcement)

{Brief one-line description}

## Purpose

{What this workflow accomplishes and why it exists}

## Scope

### Included
{What is included in this workflow}

### Excluded
{What is explicitly not covered by this workflow}

## Hook-Based Governance

**AUTOMATIC GOVERNANCE ENFORCEMENT**: This workflow uses Devin CLI hooks for automatic governance enforcement without manual gate invocation.

**HOOK SYSTEM**:
1. **SessionStart Hook**: Initializes governance environment and session logging
2. **PreToolUse Hook**: Enforces permissions before tool execution
3. **PostToolUse Hook**: Logs operations and updates state after execution
4. **SessionEnd Hook**: Final validation and session cleanup

**HOOK BENEFITS**:
- **Automatic Enforcement**: No manual script invocation required
- **Real-Time Validation**: Permissions checked before every tool execution
- **Comprehensive Logging**: All operations automatically logged to session files
- **Phase-Based Permissions**: Automatic enforcement of phase restrictions
- **Session Management**: Automatic session lifecycle management

**INTEGRATION PATTERN**:
- Hook system is automatically active via `.devin/hooks.v1.json`
- Governance happens automatically without agent intervention
- Session logs stored in `Logs/{AgentType}/Sessions/`
- Phase permissions enforced via `Scripts/Governance/Config/phase_permissions.json`
- Non-compliance automatically blocks operations

## Hook-Based Enforcement

**AUTOMATIC ENFORCEMENT**: Hook system provides automatic governance enforcement without manual gate invocation.

**ENFORCEMENT RULES**:
- Hook verification is automatic and happens at tool execution time
- Hooks must have clear PASS/FAIL criteria via exit codes
- Hook failures automatically block operations (exit code 2)
- Hook results are automatically logged to session files
- Hooks validate permissions, compliance, and security automatically
- Hooks provide comprehensive governance coverage

**ENFORCEMENT PATTERN**:
1. Perform the step's actions
2. PreToolUse hook automatically validates permissions before each tool
3. PostToolUse hook automatically logs each operation
4. Operations are automatically blocked if governance rules are violated
5. SessionEnd hook automatically validates session completion
6. All governance happens automatically without manual intervention

**COMPLIANCE REQUIREMENT**: 
- Hook system is automatically active via `.devin/hooks.v1.json`
- Governance enforcement happens at tool execution time
- No manual gate invocation or rule cache management required
- Hook-based enforcement provides comprehensive compliance coverage
- Hook configuration in `Scripts/Governance/Config/` governs all behavior

## Workflow Steps

### 0. Environment Initialization (Automatic)
- Hook system automatically initializes governance environment
- SessionStart hook creates session log and validates environment
- Phase permissions automatically loaded from configuration
- No manual intervention required

**Automatic Hook**: SessionStart hook runs automatically at session start

### 1. {Step Name}
- {action bullets}
- Hook system automatically enforces permissions during this step

**Automatic Enforcement**: PreToolUse hook validates all tool permissions

### 2. {Step Name}
- {action bullets}
- Hook system logs all interactions automatically

**Automatic Enforcement**: PostToolUse hook logs all operations

### 3. {Step Name}
- {action bullets}
- Hook system automatically validates all operations

**Automatic Enforcement**: PreToolUse hook validates all operations

### 4. {Step Name}
- {action bullets}
- Hook system automatically logs all activities

**Automatic Enforcement**: PostToolUse hook logs all operations

### 5. {Step Name}
- {action bullets}
- Hook system automatically validates all operations

**Automatic Enforcement**: PreToolUse hook validates all operations

### 6. {Step Name}
- {action bullets}
- Hook system automatically logs all activities

**Automatic Enforcement**: PostToolUse hook logs all operations

### 7. {Step Name}
- {action bullets}
- Hook system automatically validates all operations

**Automatic Enforcement**: PreToolUse hook validates all operations

### 8. {Step Name}
- {action bullets}
- Hook system automatically logs all activities

**Automatic Enforcement**: PostToolUse hook logs all operations

### 9. {Step Name}
- {action bullets}
- Hook system automatically validates all operations

**Automatic Enforcement**: PreToolUse hook validates all operations

### 10. {Step Name}
- {action bullets}
- Hook system automatically logs all activities

**Automatic Enforcement**: PostToolUse hook logs all operations

### 11. Session Finalization (Automatic)
- SessionEnd hook automatically validates session completion
- Generates session completion report
- Archives session logs automatically
- No manual intervention required

**Automatic Hook**: SessionEnd hook runs automatically at session end

### 12. Cycle Back to Step 1
**MANDATORY**: After completing workflow, cycle back to Step 1
- This makes the workflow repeatable
- Agent can handle multiple tasks in sequence
- Each cycle maintains automatic hook-based governance

**Automatic Enforcement**: Hook system automatically handles all governance

## Workflow Logging
**AUTOMATIC**: Hook system automatically logs all session activities
- Session logs automatically created by SessionStart hook
- All operations automatically logged by PostToolUse hook
- Session completion automatically logged by SessionEnd hook
- Session logs stored in `Logs/{AgentType}/Sessions/{session_id}.json`
- No manual logging intervention required

**Session Logging:**
- Session logs automatically generated by hook system
- Session logs stored in `Logs/{AgentType}/Sessions/`
- Each session includes: session_id, agent_type, operations, timestamps, status
- All operations automatically logged with tool name, file path, and result
- Session end automatically logged with summary and completion status

## Workflow Closure
Workflow closure is handled automatically by the SessionEnd hook.

**Automatic Closure:**
- SessionEnd hook automatically validates session completion
- SessionEnd hook automatically generates session completion report
- SessionEnd hook automatically archives session logs
- No manual closure intervention required

**Closure Requirements:**
- All workflow steps benefit from automatic hook enforcement
- SessionEnd hook automatically performs final validation
- Session logs automatically archived by hook system
- Session completion status automatically logged

**Closure is Triggered:**
- Automatically when session ends
- Automatically when agent completes all requested tasks
- Automatically when session is interrupted or closed

## Integration Points

**Standard Integration Points:**
- **Rules**: `Rules/{AgentName}/{Agent}_Rules.md`
- **Workflows**: `Workflow/{AgentName}/{Agent}_Workflow.md`
- **Skills**: `.devin/skills/{agent}/SKILL.md`
- **Logs**: `Logs/{Agent}/`

**Hook System Integration Points:**
- **Hook Configuration**: `.devin/hooks.v1.json`
- **Hook Scripts**: `Scripts/Governance/Hooks/`
- **Governance Config**: `Scripts/Governance/Config/`
- **Session Logs**: `Logs/{AgentType}/Sessions/`
- **Simple Logger**: `Scripts/Governance/simple_logger.py`

## Quality Metrics

### Quality (10 points)
- Determinism (3): Predictable, reproducible behavior
- Observability (3): Audit trails, logging, state visibility
- Testability (2): Isolated testing, clear interfaces
- Architectural soundness (2): Single responsibility, minimal coupling

### Token Cost (10 points)
- Context efficiency (3): Targeted information retrieval
- Model selection (3): Appropriate model choices
- Caching strategy (2): Repeated query optimization
- Reasoning overhead (2): Efficient prompt design

### Efficiency (10 points)
- Parallelization (4): Independent task identification
- Latency optimization (3): Critical path analysis
- Resource utilization (3): Computational overhead, data structure efficiency

## Session Logging
Hook system automatically maintains session logs in `Logs/{AgentType}/Sessions/` for each session with:
- Session ID and timestamp
- Agent type identification
- All operations with tool names, file paths, and results
- Session start and end times
- Session status and summary
- Automatic operation counting

## Usage Examples

### Example {Agent} Implementation Cycle with Hook-Based Governance

```markdown
## {Agent} Implementation Cycle: {Task Name}

### 0. Environment Initialization (Automatic)
- Hook system automatically initializes governance environment
- SessionStart hook creates session log: `Logs/{AgentType}/Sessions/{session_id}.json`
- Phase permissions automatically loaded from `Scripts/Governance/Config/phase_permissions.json`
- No manual intervention required

**Automatic Hook**: SessionStart hook executed successfully

### 1. {Step 1 Name}
- {Step 1 Description}
- Hook system automatically enforces permissions during this step

**Automatic Enforcement**: PreToolUse hook validated all tool permissions

### 2. {Step 2 Name}
- {Step 2 Description}
- Hook system logs all interactions automatically

**Automatic Enforcement**: PostToolUse hook logged all operations

[... continue with steps 3-10 ...]

### 11. Session Finalization (Automatic)
- SessionEnd hook automatically validates session completion
- SessionEnd hook generates session completion report
- SessionEnd hook archives session logs automatically
- No manual intervention required

**Automatic Hook**: SessionEnd hook executed successfully

### 12. Cycle Back to Step 1
- Workflow completed successfully
- Ready for next task
- Hook system automatically continues governance enforcement

**Automatic Enforcement**: Hook system maintains continuous governance
```

### Example Session Log Structure

**Session Log with Hook-Based Governance:**
- Session ID and timestamp automatically logged
- Agent type automatically detected
- All operations automatically logged with full details
- Session end automatically logged with summary
- No manual logging intervention required

**Session Log Location:**
- Session logs stored in `Logs/{AgentType}/Sessions/{session_id}.json`
- Automatic session lifecycle management
- Comprehensive operation tracking via hooks