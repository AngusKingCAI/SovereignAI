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

### 0. Read {Agent} Rules
- **ACTION**: Read Rules/{Agent}/{Agent}_Rules.md to load current governance constraints
- **ACTION**: Parse YAML frontmatter and rule definitions for implementation guidance
- **ACTION**: Store rule context for reference throughout workflow execution
- **VERBOSE LOG**: "{Agent} rules loaded from Rules/{Agent}/{Agent}_Rules.md"

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

### 9. Return to Step 0
- **ACTION**: After completing workflow, return to Step 0
- **ACTION**: This makes the workflow repeatable for continuous work
- **ACTION**: Ready for next task
- **VERBOSE LOG**: "Workflow cycle complete - returning to Step 0 for next task"
- **VERBOSE LOG**: "{Agent} agent ready - awaiting next user request"

## Hook-Based Gate System Integration

### Automated Progression System
The workflow uses an automated progression system based on step-based gating:
- **State machine architecture**: External state in `Logs/{Agent}/Gating/workflow-state.json`
- **Single responsibility separation**: Manager, Gate, Tracker, Handler components
- **Agent-agnostic design**: Uses `DEVIN_PROJECT_DIR` for portability
- **Fail-open on errors**: Never deadlocks the agent on internal failures
- **Devin-compatible hooks**: Proper JSON output format as per guides
- **Regex-based workflow parsing**: `^###\s+(\d+)\.\s+(.+)$` pattern

### Automated Workflow Progression
- **Step completion detection**: Automatically detects successful step completion via state-mutating tools
- **Automatic advancement**: System auto-advances to next step on success
- **Failure detection**: Detects step failures and triggers user intervention
- **User intervention**: Only pauses on failure with `/retry`, `/modify`, `/abort` options
- **No manual commands**: No need for `/step-complete` or `/step-begin` commands

### Commands (for failure intervention only)
| Command | Effect |
|---------|--------|
| `/retry` | Retry failed step from beginning |
| `/modify` | Allow modifications while step is failed |
| `/abort` | Skip failed step and advance to next |
| `/workflow-status` | Show all steps and completion state |

Research tools (`read`, `grep`, `glob`, `ask_user_question`, `view`) are never gated. State-mutating tools (`edit`, `write`, `exec`) are automatically allowed in normal progression and only blocked on failure.

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
- **PRE-TOOL USE**: workflow_step_gate.py hook
- **POST-TOOL USE**: automated_progress_tracker.py hook
- **USER PROMPT SUBMIT**: user_decision_handler.py hook
- **SESSION END**: session_finalization.py hook

### Workflow State Management
- **WORKFLOW STATE**: Logs/{Agent}/Gating/workflow-state.json
- **WORKFLOW HISTORY**: Logs/{Agent}/Gating/workflow-history.jsonl
- **SESSION CONTEXT**: Logs/{Agent}/Gating/session-context.json
- **AUDIT TRAIL**: Logs/{Agent}/Gating/audit-trail.log

### Hook Script Components
- **workflow_state_manager.py**: State I/O and validation, regex workflow parsing
- **workflow_step_gate.py**: PreToolUse gate, blocks on failure only
- **automated_progress_tracker.py**: PostToolUse tracker, detects completion and failures
- **user_decision_handler.py**: UserPromptSubmit handler, processes retry/modify/abort commands
- **session_init.py**: Session initialization, creates session context
- **session_finalization.py**: Session end validation and cleanup

### {Agent} Rules Compliance
- **CONSTRAINTS**: Rules/{Agent}/{Agent}_Rules.md constraints enforced
- **FILE PLACEMENT**: Scripts/Gating/ category per architect rules
- **TESTING REQUIREMENT**: Never test in isolated environments, always test in actual project context
- **GOVERNANCE COMPLIANCE**: Hook system provides automatic enforcement without manual invocation