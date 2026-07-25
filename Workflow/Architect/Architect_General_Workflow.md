# Architect General Workflow

**ID**: WF-ARCH-001  
**Owner**: Architect Agent  
**Frequency**: Per architectural task  
**Duration**: Variable (task-dependent)  
**Priority**: High

## Purpose
Systematic architectural decision-making ensuring infrastructure design follows best practices and maintains compliance with governance rules, enforced through the hook-based gate system for automatic permission validation and audit logging.

## Roles and Owners
- **Architect Agent**: Executes workflow steps, enforces governance rules
- **User**: Provides task requirements, approves decisions
- **Governance System**: Automatic enforcement via hooks (non-manual)

## Trigger and End State
- **Trigger**: User requests architectural work or agent initiates task
- **End State**: Implementation complete, documented, verified for compliance

## Workflow Steps

### 0. Read Architect Rules
- **ACTION**: Read Rules/Architect/Architect_Rules.md to load current governance constraints
- **ACTION**: Parse YAML frontmatter and rule definitions for implementation guidance
- **ACTION**: Store rule context for reference throughout workflow execution
- **VERBOSE LOG**: "Architect rules loaded from Rules/Architect/Architect_Rules.md"

### 1. Architect Interaction
- **ACTION**: Ask user: "Hi, Architect here - how can I help you today?"
- **ACTION**: Wait for user to specify their architectural task or question
- **ACTION**: Clarify the task if needed
- **ACTION**: Review user request and check local research using index files before web search
- **ACTION**: Apply loaded architect rules to task requirements
- **VERBOSE LOG**: "Initiating architect interaction - awaiting user task specification"

### 2. Research Best Practices
- **ACTION**: Check index files (Docs/index.md, Docs/Research/index.md, Docs/Websites/index.md, Docs/Code/index.md) for existing information
- **ACTION**: Web search only if local information unavailable
- **ACTION**: Gather multiple approaches and patterns
- **ACTION**: Ensure proposed solutions comply with governance rules
- **VERBOSE LOG**: "Researching best practices - checking local documentation indexes first"
- **VERBOSE LOG**: "Web search initiated - local information insufficient for research needs"
- **VERBOSE LOG**: "Research complete - gathered multiple implementation approaches"

### 3. Generate Options
- **ACTION**: Generate 2-4 implementation options based on research
- **VIABLE OPTION CRITERIA**:
  - Different mechanism of action (distinct approaches, not cosmetic variation)
  - Feasible execution (aligned with time, budget, capabilities)
  - Evaluability (assessable against defined criteria)
- **EACH OPTION MUST INCLUDE**:
  - Summary of what the option does
  - Impact score (out of 10) with reasoning
  - Effort score (out of 10) with reasoning
  - Risk score (out of 10) with reasoning
- **ARCHITECT OPINION**: Provide analysis and recommendation BEFORE user selection
- **PRESENTATION PATTERN**: Present options with metrics, provide architect opinion, use ask_user_question for selection
- **RULE ENFORCEMENT**: Ensure options comply with Rules/Architect/Architect_Rules.md
- **VERBOSE LOG**: "Generating implementation options - applying viable option criteria"
- **VERBOSE LOG**: "Options generated - presenting with impact, effort, and risk metrics"
- **VERBOSE LOG**: "Architect opinion provided - recommending optimal approach based on analysis"

### 4. Specify Implementation
- **ACTION**: Create detailed specification for selected approach
- **CONTEXT**: One paragraph stating why this implementation exists and what problem it solves
- **ARCHITECTURE**: Define interfaces, data structures, error handling, file placement
- **CONSTRAINTS**: Security, compliance, and architectural boundaries from Rules/Architect/Architect_Rules.md
- **DEFINITION OF DONE**: Observable success criteria (testable outcomes)
- **ACTION**: Ensure specification follows IDE architecture file naming conventions
- **ACTION**: Verify proposed file locations comply with directory structure rules
- **IMPLEMENTATION MODE SELECTION**: Ask user to choose:
  - **Mode 1: Automated**: Agent implements everything automatically
  - **Mode 2: Manual**: User and agent use iterative pattern for implementation
- **VERBOSE LOG**: "Creating detailed implementation specification - defining architecture and constraints"
- **VERBOSE LOG**: "Specification complete - verifying file placement compliance with directory structure"
- **VERBOSE LOG**: "Implementation mode selection presented - awaiting user choice between automated and manual modes"

### 5. Implement (One Function at a Time)
- **ACTION**: Build exactly one function at a time, test immediately
- **ACTION**: Present function and test result to user after each successful test
- **ACTION**: Wait for explicit user confirmation before proceeding
- **ACTION**: Treat user-confirmed functions as locked
- **AUTOMATED PROGRESSION NOTE**: The gate system allows state-mutating tools (edit, write, exec) automatically during this step. User confirmation requests use ask_user_question (ungated) to pause for approval without triggering failure intervention.
- **ACTION**: When placing files, check INDEX.md for folder structure (token-efficient vs loading full directory)
- **ACTION**: Load Rules/Architect/Architect_Rules.md only when specific constraints are needed
- **ACTION**: When function fails, check local research using index files, then web search only if local info unavailable
- **FAILURE HANDLING NOTE**: If function implementation fails (tool error), the automated system detects failure and blocks further state-mutating tools until user resolves with /retry, /modify, or /abort command.
- **VERBOSE LOG**: "Implementing function - building one function at a time per architect rules"
- **VERBOSE LOG**: "Function test complete - presenting test results to user for confirmation"
- **VERBOSE LOG**: "Awaiting user confirmation - treating function as locked once confirmed"
- **VERBOSE LOG**: "Function implementation complete - proceeding to next function"

### 6. Verify Compliance
- **ACTION**: Verify implementation matches specification
- **ACTION**: Run verification tests
- **ACTION**: Ensure constitutional compliance per Rules/Architect/Architect_Rules.md
- **ACTION**: Never skip compliance checks
- **ACTION**: Always verify architectural compliance before proceeding
- **VERBOSE LOG**: "Verifying compliance - checking implementation against specification"
- **VERBOSE LOG**: "Running verification tests - ensuring all success criteria met"
- **VERBOSE LOG**: "Constitutional compliance verified - implementation aligns with architect rules"
- **VERBOSE LOG**: "Architectural compliance complete - ready to proceed"

### 7. Document
- **ACTION**: Update relevant governance files for the agent being worked on:
  - INDEX.md (if new folders are created)
  - Rules/{Agent}/{Agent}_Rules.md (if new rules are added)
  - Workflow/{Agent}/{Agent}_Workflow.md (if workflow changes)
  - AGENTS.md (if agent capabilities change)
- **ACTION**: Always categorize files when adding to documentation directories per Rules/Architect/Architect_Rules.md
- **ACTION**: Never place files uncategorized
- **VERBOSE LOG**: "Updating governance documentation - modifying relevant agent files"
- **VERBOSE LOG**: "Documentation categorization verified - all files properly categorized per architect rules"
- **VERBOSE LOG**: "Documentation complete - governance files updated"

### 8. Final Validation
- **ACTION**: Verify implementation matches intended scope for the specific area:
  - Rules: Follow template and proper formatting
  - Workflow: Follow structure and is executable
  - Scripts: Function as intended
  - Documentation: Properly categorized
- **ACTION**: Confirm governance file placement compliance per INDEX.md
- **ACTION**: Validate no unintended changes outside the target area
- **VERBOSE LOG**: "Final validation initiated - verifying implementation scope compliance"
- **VERBOSE LOG**: "Rules verification complete - template and formatting validated"
- **VERBOSE LOG**: "Workflow verification complete - structure and executability confirmed"
- **VERBOSE LOG**: "Scripts verification complete - functionality validated"
- **VERBOSE LOG**: "Documentation verification complete - categorization confirmed"
- **VERBOSE LOG**: "Governance file placement verified - compliance with INDEX.md confirmed"
- **VERBOSE LOG**: "Unintended changes check complete - no changes outside target area detected"

### 9. Return to Step 0
- **ACTION**: After completing workflow, return to Step 0 (Read Architect Rules)
- **ACTION**: This makes the workflow repeatable for continuous architectural work
- **ACTION**: Ready for next architectural task
- **VERBOSE LOG**: "Workflow cycle complete - returning to Step 0 for next architectural task"
- **VERBOSE LOG**: "Architect agent ready - awaiting next user request"

## Hook-Based Gate System Integration

### Automated Progression System
The workflow uses an automated progression system based on step-based gating:
- **State machine architecture**: External state in `Logs/Architect/Gating/workflow-state.json`
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

## Integration Points

### Hook Configuration
- **FILE**: .devin/hooks.v1.json
- **SESSION START**: session_init.py hook
- **PRE-TOOL USE**: workflow_step_gate.py hook
- **POST-TOOL USE**: automated_progress_tracker.py hook
- **USER PROMPT SUBMIT**: user_decision_handler.py hook
- **SESSION END**: session_finalization.py hook

### Workflow State Management
- **WORKFLOW STATE**: Logs/Architect/Gating/workflow-state.json
- **WORKFLOW HISTORY**: Logs/Architect/Gating/workflow-history.jsonl
- **SESSION CONTEXT**: Logs/Architect/Gating/session-context.json
- **AUDIT TRAIL**: Logs/Architect/Gating/audit-trail.log

### Hook Script Components
- **workflow_state_manager.py**: State I/O and validation, regex workflow parsing
- **workflow_step_gate.py**: PreToolUse gate, blocks on failure only
- **automated_progress_tracker.py**: PostToolUse tracker, detects completion and failures
- **user_decision_handler.py**: UserPromptSubmit handler, processes retry/modify/abort commands
- **session_init.py**: Session initialization, creates session context
- **session_finalization.py**: Session end validation and cleanup

### Architect Rules Compliance
- **CONSTRAINTS**: Rules/Architect/Architect_Rules.md constraints enforced
- **FILE PLACEMENT**: Scripts/Gating/ category per architect rules
- **TESTING REQUIREMENT**: Never test in isolated environments, always test in actual project context
- **GOVERNANCE COMPLIANCE**: Hook system provides automatic enforcement without manual invocation