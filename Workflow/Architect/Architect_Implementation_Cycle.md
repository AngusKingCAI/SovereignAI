# Architect Implementation Cycle

**File**: Architect_Implementation_Cycle.md  
**Workflow Name**: Architect Implementation Cycle  
**Description**: Complete 12-step implementation cycle with hook-based governance enforcement for systematic architectural work  
**Status**: Architect Agent Standard  
**Template Compliance**: Verified  
**Hook-Based Governance**: Enabled (automatic enforcement)

Step-by-step process for architectural decisions with best practice validation and automatic hook-based governance.

## Purpose

Provide systematic architectural decision-making with gated implementation cycles to ensure infrastructure design follows best practices and maintains compliance with IDE architecture standards.

## Scope

### Included
- Infrastructure design and architecture planning
- Directory structure and file organization standards
- Workflow definition and procedure documentation
- Gate system design and verification
- Constitutional compliance verification
- IDE architecture rules definition and enforcement

### Excluded
- SovereignAI application code implementation (deferred to Phase 12)
- Direct application feature development (deferred to Phase 12)
- Application-level testing and debugging (deferred to Phase 12)
- Direct file editing in App/ directory (reference only)
- Production deployment operations (deferred to Phase 12)
- User interface development (deferred to Phase 12)
- Database schema modifications (deferred to Phase 12)

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

### 1. Understand
- Review applicable rules from governance configuration
- Identify current phase and dependencies
- Understand task context within framework of governance rules
- Hook system automatically enforces permissions during research

**Automatic Enforcement**: PreToolUse hook validates all tool permissions

### 2. Architect Interaction
- Ask user: "Hi, Architect here - how can I help you today?"
- Wait for user to specify their architectural task or question
- Clarify the task if needed
- Hook system logs all interactions automatically

**Automatic Enforcement**: PostToolUse hook logs all operations

### 3. Research
- Use web search to find industry best practices
- Reference Devin CLI documentation for IDE-related features: `Docs/Devin Local IDE Documents/`
- Cross-reference with Devin Local documentation for implementation feasibility
- Gather multiple approaches and patterns
- Ensure proposed solutions comply with governance rules
- Hook system automatically validates all research operations

**Automatic Enforcement**: PreToolUse hook validates all research tool permissions

### 4. Options (Generate 2-5 Implementation Options)
- Generate 2-5 implementation options based on research
- **RESEARCH RUBRIC** (GitHub analysis of 2,500+ repositories):
  - **Minimality**: Only operational knowledge, not discoverable content
  - **Tooling Specification**: Explicit tool names and commands
  - **Novelty vs Redundancy**: Unique operational context not found elsewhere
  - **Authorship**: Human-written or heavily human-edited content
- **EACH OPTION MUST INCLUDE**:
  - Summary of what the option does
  - Quality score (out of 10) with reasoning based on rubric
  - Token Cost score (out of 10) with reasoning based on rubric
  - Efficiency score (out of 10) with reasoning based on rubric
- **ARCHITECT OPINION**: After presenting options, provide architect's analysis and recommendation BEFORE calling ask_user_question
- **PRESENTATION PATTERN**: 
  1. Present options with full metrics in text format
  2. Provide architect's analysis and opinion
  3. Use ask_user_question for selection

**Automatic Enforcement**: Hook system logs all option generation activities

### 5. Decide
- User selects the preferred option
- Architect agent validates constitutional compliance of selection
- Hook system automatically validates all decision-related operations

**Automatic Enforcement**: PreToolUse hook validates all decision operations

### 6. Specify
- Create detailed specification for selected approach
- Define interfaces, data structures, error handling
- Specify testing and documentation requirements
- Ensure specification follows IDE architecture file naming conventions
- Verify proposed file locations comply with directory structure rules
- **IMPLEMENTATION MODE SELECTION**: Ask user to choose implementation mode:
  - **Mode 1: Automated**: Agent implements everything automatically
  - **Mode 2: Manual**: User and agent use steps 4-5 pattern for iterative implementation. Architect provides opinion on each iteration.

**Automatic Enforcement**: Hook system validates all specification file operations

### 7. Implement
- Implement according to specification
- Follow IDE architecture rules for file placement
- Cross-reference Devin CLI documentation for IDE-related implementations
- Hook system automatically enforces all implementation permissions

**Automatic Enforcement**: PreToolUse hook validates all implementation operations

### 8. Test
- Run unit tests
- Run integration tests
- Verify all tests pass
- Hook system automatically logs all testing activities

**Automatic Enforcement**: PostToolUse hook logs all test operations

### 9. Verify
- Verify implementation matches specification
- Run verification tests
- Ensure constitutional compliance
- Hook system automatically validates all verification operations

**Automatic Enforcement**: PreToolUse hook validates all verification operations

### 10. Document
- Update agent documentation
- Create usage examples
- Hook system automatically logs all documentation activities

**Automatic Enforcement**: PostToolUse hook logs all documentation operations

### 11. Session Finalization (Automatic)
- SessionEnd hook automatically validates session completion
- Generates session completion report
- Archives session logs automatically
- No manual intervention required

**Automatic Hook**: SessionEnd hook runs automatically at session end

### 12. Cycle Back to Step 1
**MANDATORY**: After completing workflow, cycle back to Step 1 (Understand)
- This makes the workflow repeatable
- Architect can handle multiple tasks in sequence
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
- **Rules**: `Rules/Architect/Architect_Rules.md`
- **Workflows**: `Workflow/Architect/Architect_Implementation_Cycle.md`
- **Skills**: `.devin/skills/architect/SKILL.md` (skill to be created)
- **Logs**: `Logs/Architect/`

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
Hook system automatically maintains session logs in `Logs/{AgentType}/Sessions/` for each implementation cycle session with:
- Session ID and timestamp
- Agent type identification
- All operations with tool names, file paths, and results
- Session start and end times
- Session status and summary
- Automatic operation counting

## Usage Examples

### Example Architect Implementation Cycle with Hook-Based Governance

```markdown
## Architect Implementation Cycle: Hook System Implementation

### 0. Environment Initialization (Automatic)
- Hook system automatically initializes governance environment
- SessionStart hook creates session log: `Logs/Architect/Sessions/{session_id}.json`
- Phase permissions automatically loaded from `Scripts/Governance/Config/phase_permissions.json`
- No manual intervention required

**Automatic Hook**: SessionStart hook executed successfully

### 1. Understand
- Review applicable rules from governance configuration
- Identify current phase and dependencies
- Understand task context within framework of governance rules
- PreToolUse hook automatically validates all research permissions

**Automatic Enforcement**: PreToolUse hook validated all tool permissions

### 2. Architect Interaction
- User requests implementation of Hook-Based Governance System
- Clarify requirements: automatic enforcement via hooks
- Hook system logs all interactions automatically

**Automatic Enforcement**: PostToolUse hook logged all operations

### 3. Research
- Use web search to find industry best practices for hook systems
- Reference Devin CLI documentation for IDE-related features
- Ensure proposed solutions comply with governance rules
- Hook system automatically validates all research operations

**Automatic Enforcement**: PreToolUse hook validated all research operations

[... continue with steps 4-10 ...]

### 11. Session Finalization (Automatic)
- SessionEnd hook automatically validates session completion
- SessionEnd hook generates session completion report
- SessionEnd hook archives session logs automatically
- No manual intervention required

**Automatic Hook**: SessionEnd hook executed successfully

### 12. Cycle Back to Step 1
- Workflow completed successfully
- Ready for next architectural task
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
- Session logs stored in `Logs/Architect/Sessions/{session_id}.json`
- Automatic session lifecycle management
- Comprehensive operation tracking via hooks