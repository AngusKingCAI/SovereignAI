# Architect Hook Creator Workflow

**File**: Architect_Hook_Creator_Workflow.md  
**Workflow Name**: Architect Hook Creator Workflow  
**Description**: Complete 12-step implementation cycle for creating and testing new hooks with documentation analysis, web research, and automatic hook-based governance enforcement  
**Status**: Architect Agent Standard  
**Template Compliance**: Verified  
**Hook-Based Governance**: Enabled (automatic enforcement)

Systematic 12-step implementation cycle for creating, implementing, and testing new hooks for SovereignAI governance system with documentation analysis, web research, and automatic governance enforcement.

## Purpose

Provide systematic hook development with gated implementation cycles to ensure hooks follow best practices, maintain compliance with IDE architecture standards, and integrate properly with the Devin CLI hook system.

## Scope

### Included
- Hook documentation analysis and requirements gathering
- Hook implementation research and design
- Hook script development and testing
- Hook configuration and integration
- Project-wide hook validation
- Hook documentation and usage examples

### Excluded
- Application code implementation (deferred to appropriate agents)
- Infrastructure changes outside hooks
- Direct file editing in App/ directory
- Application-level testing and debugging (deferred to appropriate agents)

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
- Load hook documentation paths and requirements
- Hook system automatically enforces permissions during research

**CRITICAL CONFIGURATION REQUIREMENTS**:
- Devin CLI reads hooks from user-level config: `%APPDATA%\devin\config.json` (Windows)
- OR project-level: `.devin/hooks.v1.json` (recommended)
- User-level config format: hooks nested under `"hooks"` key
- Project-level format: hooks object is the entire file (no wrapper key)
- Use absolute paths in hook commands
- Test with simple echo commands first before complex Python scripts
- Verify hooks load with `/hooks` command in Devin CLI

**CRITICAL TECHNICAL REQUIREMENTS**:
- **Devin CLI passes event data in JSON stdin, NOT environment variables**
- **Hook event name is in `hook_event_name` field in JSON stdin data**
- **Do NOT rely on `DEVIN_HOOK_EVENT` environment variable** (not set by Devin CLI)
- **Environment variables are unreliable** - hooks need fallback mechanisms
- **Session file detection**: Read agent config and find most recent file in agent's logs directory
- **Agent detection**: Read from `.devin/agent_config.json` to determine current agent
- **Platform-specific events**: MessageDisplay is Claude Code specific, NOT supported by Devin CLI
- **Devin CLI supported events**: SessionStart, UserPromptSubmit, PreToolUse, PostToolUse, PermissionRequest, Stop, SessionEnd

**Hook Documentation Paths**:
- `Docs/Claude Hooks/agent-sdk-hooks.md`
- `Docs/Claude Hooks/claude-code-hooks-guide.md`
- `Docs/Claude Hooks/claude-code-hooks-reference.md`
- `Docs/Claude Hooks/hook-events-lifecycle-comparison.md`
- `Docs/Claude Hooks/production-hooks-tutorial.md`
- `Docs/Devin Local IDE Documents/Hooks-Guide.md`
- `Docs/Hook-Based-Gate-System.md`
- `Docs/Hooks-Gate-System-Architecture.md`

**Automatic Enforcement**: PreToolUse hook validates all tool permissions

### 2. Architect Interaction
- Ask user: "Hi, Architect here - what hook-related task can I help you with today?"
- Wait for user to specify their hook development task or question
- Clarify the hook requirements if needed
- Hook system logs all interactions automatically

**Automatic Enforcement**: PostToolUse hook logs all operations

### 3. Research
- Read relevant hook documentation from identified paths
- Analyze implementation patterns from documentation
- Extract JSON schema requirements for hooks.v1.json
- Understand hook event input/output formats
- Review matcher patterns and tool-specific configurations
- Use web search to find similar hook implementations online
- Reference Devin CLI documentation and examples
- Look for Claude Code hook examples and patterns
- Research best practices for hook development
- Gather multiple implementation approaches
- Ensure proposed implementation follows documented patterns
- Hook system automatically validates all research operations

**IMPLEMENTATION PATTERNS FOR SESSION FILE DETECTION**:
```python
def get_current_session_file():
    """Get current session file from config or environment."""
    # First try environment variable (may not be set)
    session_file = os.environ.get('DEVIN_SESSION_FILE')
    if session_file:
        return session_file
    
    # Fallback: read from agent config to find latest session
    try:
        project_root = Path("C:/SovereignAI")
        config_file = project_root / ".devin" / "agent_config.json"
        
        if config_file.exists():
            with open(config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            current_agent = config.get('current_agent', 'Architect')
            logs_dir = project_root / "Logs" / current_agent
            
            if logs_dir.exists():
                # Find the most recent session file
                session_files = list(logs_dir.glob("*.md"))
                if session_files:
                    # Sort by modification time and get the most recent
                    latest_file = max(session_files, key=lambda f: f.stat().st_mtime)
                    return str(latest_file)
    except Exception:
        pass
    
    return None
```

**IMPLEMENTATION PATTERNS FOR AGENT DETECTION**:
```python
def get_current_agent():
    """Determine current agent from config, environment, or skill."""
    # First check environment variable (highest priority during session)
    agent = os.environ.get('DEVIN_CURRENT_AGENT')
    if agent:
        return agent
    
    # Then check configuration file (for session startup)
    config = self.read_agent_config()
    if config and config.get('current_agent'):
        return config['current_agent']
    
    # Then check current skill
    skill = os.environ.get('DEVIN_CURRENT_SKILL')
    if skill:
        return skill.capitalize()
    
    # Default to Architect
    return "Architect"
```

**DEBUGGING HOOK CONFIGURATION**:
- Use `/hooks` command in Devin CLI to verify loaded hooks
- **RESTART Devin CLI after any hook configuration changes**
- Remove environment variable dependencies from hooks.v1.json (they're unreliable)
- Use debug logging to verify event data sources (JSON stdin vs env vars)
- Test hooks manually with JSON input: `echo '{"hook_event_name":"Test"}' | python hook_script.py`
- Check agent config file for current agent state
- Verify session file paths and permissions

**Automatic Enforcement**: PreToolUse hook validates all research tool permissions

### 4. Options (Generate 2-5 Implementation Options)
- Generate 2-5 hook implementation options based on research
- **RESEARCH RUBRIC** (GitHub analysis of 2,500+ repositories):
  - **Minimality**: Only operational knowledge, not discoverable content
  - **Tooling Specification**: Explicit tool names and commands
  - **Novelty vs Redundancy**: Unique operational context not found elsewhere
  - **Authorship**: Human-written or heavily human-edited content
- **EACH OPTION MUST INCLUDE**:
  - Summary of what the hook does
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
- User selects the preferred hook implementation option
- Architect agent validates constitutional compliance of selection
- Hook system automatically validates all decision-related operations

**Automatic Enforcement**: PreToolUse hook validates all decision operations

### 6. Specify
- Create detailed specification for selected hook approach
- Define hook event type, handler structure, and interface
- Specify JSON schema and configuration requirements
- Define testing and documentation requirements
- Ensure specification follows proper hook naming conventions
- Verify proposed file locations comply with directory structure rules
- **IMPLEMENTATION MODE SELECTION**: Ask user to choose implementation mode:
  - **Mode 1: Automated**: Agent implements hook automatically
  - **Mode 2: Manual**: User and agent use steps 4-5 pattern for iterative implementation. Architect provides opinion on each iteration.

**Automatic Enforcement**: Hook system validates all specification file operations

### 7. Implement
- Implement hook according to specification
- **CRITICAL**: Implement proper stdin JSON reading for event data
- **CRITICAL**: Use fallback mechanisms for session file and agent detection
- **CRITICAL**: Do not rely on environment variables for event names
- Add hook to `.devin/hooks.v1.json` with proper configuration
- Follow IDE architecture rules for file placement
- Hook system automatically enforces all implementation permissions

**Automatic Enforcement**: PreToolUse hook validates all implementation operations

### 8. Test
- Test hook with sample input data (simulate JSON stdin)
- Verify hook produces correct JSON output
- Validate hook exit codes and error handling
- Ensure hook integrates properly with hook system
- Test hook behavior with and without environment variables set
- Run comprehensive test of all hooks in `.devin/hooks.v1.json`
- Test each hook with appropriate sample input
- Verify hook integration across different events
- Check for conflicts between hooks
- Validate hook performance and timeouts
- Ensure all hooks work together as a system
- Hook system automatically logs all testing activities

**Automatic Enforcement**: PostToolUse hook logs all test operations

### 9. Verify
- Verify hook implementation matches specification
- Run verification tests with real Devin CLI hook system
- Ensure constitutional compliance with governance rules
- Verify hook loads correctly with `/hooks` command
- Check hook event data handling and JSON parsing
- Validate fallback mechanisms work correctly
- Hook system automatically validates all verification operations

**Automatic Enforcement**: PreToolUse hook validates all verification operations

### 10. Document
- Update hook documentation with implementation details
- Create usage examples and configuration guides
- Document critical technical requirements and patterns
- Update Architect Hook Creator Workflow with lessons learned
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
- Architect can handle multiple hook-related tasks in sequence
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
- **Workflows**: `Workflow/Architect/Architect_Hook_Creator_Workflow.md`
- **Skills**: `.devin/skills/architect/SKILL.md`
- **Logs**: `Logs/Architect/`

**Hook System Integration Points:**
- **Hook Configuration**: `.devin/hooks.v1.json`
- **Hook Scripts**: `Scripts/Governance/Hooks/`
- **Governance Config**: `Scripts/Governance/Config/`
- **Session Logs**: `Logs/{AgentType}/`
- **Documentation**: `Docs/Claude Hooks/`, `Docs/Devin Local IDE Documents/`, `Docs/Hook-Based-Gate-System.md`, `Docs/Hooks-Gate-System-Architecture.md`

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
Hook system automatically maintains session logs in `Logs/{AgentType}/` for each hook creation session with:
- Session ID and timestamp
- Agent type identification
- All operations with tool names, file paths, and results
- Session start and end times
- Session status and summary
- Automatic operation counting
- Agent-specific session files with .md format

## Usage Examples

### Example Architect Hook Creator Workflow with Hook-Based Governance

```markdown
## Architect Hook Creator Workflow: Chat Capture Hook Implementation

### 0. Environment Initialization (Automatic)
- Hook system automatically initializes governance environment
- SessionStart hook creates session log: `Logs/Architect/Sessions/{session_id}.json`
- Phase permissions automatically loaded from configuration
- No manual intervention required

**Automatic Hook**: SessionStart hook executed successfully

### 1. Understand
- Review applicable rules from governance configuration
- Load hook documentation paths and requirements
- Understand critical technical requirements for Devin CLI hooks
- PreToolUse hook automatically validates all research permissions

**Automatic Enforcement**: PreToolUse hook validated all tool permissions

### 2. Architect Interaction
- User requests implementation of chat capture hook for logging user messages
- Clarify requirements: capture UserPromptSubmit events, log to session files
- Hook system logs all interactions automatically

**Automatic Enforcement**: PostToolUse hook logged all operations

### 3. Research
- Read relevant hook documentation from identified paths
- Analyze implementation patterns from documentation
- Extract JSON schema requirements for hooks.v1.json
- Understand hook event input/output formats
- Use web search to find similar hook implementations online
- Research best practices for hook development
- PreToolUse hook validates all research operations

**Automatic Enforcement**: PreToolUse hook validated all research operations

### 4. Options (Generate 2-5 Implementation Options)
- Generate 2-5 hook implementation options based on research
- Present options with Quality, Token Cost, and Efficiency scores
- Provide architect's analysis and recommendation
- Use ask_user_question for selection

**Automatic Enforcement**: Hook system logged all option generation activities

### 5. Decide
- User selects the preferred hook implementation option
- Architect agent validates constitutional compliance of selection
- Hook system automatically validates all decision-related operations

**Automatic Enforcement**: PreToolUse hook validated all decision operations

### 6. Specify
- Create detailed specification for chat capture hook
- Define hook event type (UserPromptSubmit), handler structure, and interface
- Specify JSON schema and configuration requirements
- Define testing and documentation requirements
- Choose implementation mode (Automated vs Manual)

**Automatic Enforcement**: Hook system validated all specification file operations

### 7. Implement
- Implement chat capture hook according to specification
- Implement proper stdin JSON reading for event data
- Use fallback mechanisms for session file and agent detection
- Add hook to `.devin/hooks.v1.json` with proper configuration
- PreToolUse hook validates all implementation operations

**Automatic Enforcement**: PreToolUse hook validated all implementation operations

### 8. Test
- Test hook with sample input data (simulate JSON stdin)
- Verify hook produces correct JSON output
- Validate hook exit codes and error handling
- Test hook behavior with and without environment variables set
- PostToolUse hook logs all testing activities

**Automatic Enforcement**: PostToolUse hook logged all test operations

### 9. Verify
- Verify hook implementation matches specification
- Run verification tests with real Devin CLI hook system
- Ensure constitutional compliance with governance rules
- Verify hook loads correctly with `/hooks` command
- PreToolUse hook validates all verification operations

**Automatic Enforcement**: PreToolUse hook validated all verification operations

### 10. Document
- Update hook documentation with implementation details
- Create usage examples and configuration guides
- Document critical technical requirements and patterns
- PostToolUse hook logs all documentation activities

**Automatic Enforcement**: PostToolUse hook logged all documentation operations

### 11. Session Finalization (Automatic)
- SessionEnd hook automatically validates session completion
- SessionEnd hook generates session completion report
- SessionEnd hook archives session logs automatically
- No manual intervention required

**Automatic Hook**: SessionEnd hook executed successfully

### 12. Cycle Back to Step 1
- Workflow completed successfully
- Ready for next hook-related task
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
- Session logs stored in `Logs/{AgentType}/{timestamp}.md`
- Automatic session lifecycle management
- Comprehensive operation tracking via hooks
- Agent-specific directory organization
