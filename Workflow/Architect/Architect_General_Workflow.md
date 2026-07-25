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

### 1. Architect Interaction
- **ACTION**: Ask user: "Hi, Architect here - how can I help you today?"
- **ACTION**: Wait for user to specify their architectural task or question
- **ACTION**: Clarify the task if needed
- **ACTION**: Review user request and check local research using index files before web search
- **ACTION**: Review applicable rules from Rules/Architect/Architect_Rules.md
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
- **ACTION**: When placing files, check INDEX.md for folder structure (token-efficient vs loading full directory)
- **ACTION**: Load Rules/Architect/Architect_Rules.md only when specific constraints are needed
- **ACTION**: When function fails, check local research using index files, then web search only if local info unavailable
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

### 9. Return to Step 1
- **ACTION**: After completing workflow, return to Step 1 (Architect Interaction)
- **ACTION**: This makes the workflow repeatable for continuous architectural work
- **ACTION**: Ready for next architectural task
- **VERBOSE LOG**: "Workflow cycle complete - returning to Step 1 for next architectural task"
- **VERBOSE LOG**: "Architect agent ready - awaiting next user request"

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
- **AUDIT TRAIL**: All operations automatically logged to Logs/Architect/Gating/audit-trail.log
- **SESSION TRACKING**: Session context maintained in Logs/Architect/Gating/session-context.json

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
- **STATE MANAGEMENT**: Logs/Architect/Gating/phase-{N}-state.json
- **SESSION CONTEXT**: Logs/Architect/Gating/session-context.json
- **AUDIT TRAIL**: Logs/Architect/Gating/audit-trail.log

### Architect Rules Compliance
- **CONSTRAINTS**: Rules/Architect/Architect_Rules.md constraints enforced
- **FILE PLACEMENT**: Scripts/Gating/ category per architect rules
- **TESTING REQUIREMENT**: Never test in isolated environments, always test in actual project context
- **GOVERNANCE COMPLIANCE**: Hook system provides automatic enforcement without manual invocation