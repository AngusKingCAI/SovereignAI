# Governor.py: Complete Modular & Standardized Architecture for Devin CLI (8 Hooks)

## Executive Summary

Governor.py is a fully modular, standardized control layer that wraps Devin CLI, enforcing rule adherence through composable, auto-discoverable components. This document specifies **universal interfaces, standardized response formats, unified state management, and data-driven configuration** to ensure complete modularity and zero ambiguity.

Every component follows identical patterns. Every response follows identical schemas. Every configuration is data-driven. An Architect agent can implement this with mechanical precision.

---

## Part 1: Core Principles (Standardization & Modularity)

### 1.1 Six Pillars of Standardization

**Pillar 1: Universal Component Interface**
- Every hook handler implements same 4 methods
- Every action implements same 3 methods
- Every validator implements same 2 methods
- No exceptions, no special cases

**Pillar 2: Standardized Data Formats**
- Every hook returns identical response structure
- Every audit entry follows identical schema
- Every state file uses identical wrapper
- Every error follows identical format

**Pillar 3: Data-Driven Configuration**
- Phases defined in YAML, not hardcoded
- Tool allowlists defined in YAML
- Permission policies defined in YAML
- Action mappings defined in YAML

**Pillar 4: Automatic Composition**
- Actions chain automatically (output → input)
- Hooks route automatically (hook name → handler)
- Rules load automatically (directory scan)
- No registration code, no configuration files in code

**Pillar 5: Unified State Management**
- All state files have identical wrapper
- All state queries use identical methods
- All state updates use identical methods
- Single source of truth (disk-based)

**Pillar 6: Consistent Error Handling**
- All failures use identical error format
- All errors follow identical recovery strategy
- All components fail gracefully (never halt)
- All errors logged to unified audit trail

---

## Part 2: Universal Component Interfaces

### 2.1 Hook Handler Universal Interface

**Every hook handler, regardless of which hook, implements exactly this interface:**

#### Required Property
```
hook_name: str
  - Returns the name of the hook this handler processes
  - Example: "SessionStart", "PreToolUse", "Stop"
  - Used for auto-discovery and routing
```

#### Required Method 1: validate_input(payload: dict) → bool
**Purpose**: Verify incoming payload has correct structure

**Input**: 
- payload (dict): Raw JSON from Devin

**Output**: 
- bool: True if valid, False if invalid

**Implementation Guidelines**:
- Check payload has required fields for this hook
- Check field types match expected types
- Return False if malformed (don't raise exception)
- Log warning if invalid but continue

**Standard Validation**:
- All payloads have: timestamp, session_id
- Tool payloads have: tool, input
- Response payloads have: success, output

#### Required Method 2: build_request_context(payload: dict, state_machine: StateMachine) → dict
**Purpose**: Extract and prepare request context from payload

**Input**: 
- payload (dict): Validated hook payload
- state_machine (StateMachine): Current session state

**Output**: 
- dict: Request context with extracted data

**Standard Context Structure**:
```
{
  "hook_name": "...",
  "timestamp": "ISO 8601",
  "session_id": "...",
  "current_phase": "...",
  "tool": "..." (if applicable),
  "payload": {...}
}
```

**Implementation Guidelines**:
- Extract fields from payload
- Add current phase from state machine
- Add session metadata
- Never fail; use defaults if fields missing

#### Required Method 3: execute(payload: dict, rules: list, state_machine: StateMachine, engine: RuleEngine) → dict
**Purpose**: Main hook handler logic - evaluate rules and build response

**Input**: 
- payload (dict): Hook payload (already validated)
- rules (list): Rules applicable to this hook
- state_machine (StateMachine): Current session state
- engine (RuleEngine): Rule evaluation engine

**Output**: 
- dict: Hook response (standardized format, see 2.2)

**Implementation Pattern (ALL handlers follow this)**:
1. Call build_request_context(payload, state_machine)
2. Call engine.evaluate_all_rules(rules, payload, context)
3. Update state machine based on evaluation result
4. Build standardized response
5. Log execution to audit trail
6. Return response

**Exception Handling**:
- Catch ALL exceptions
- Log to audit trail (ERROR severity)
- Return safe default: {decision: "allow", reason: "handler error"}
- Never raise to caller

#### Required Method 4: build_response(decision: str, context: dict) → dict
**Purpose**: Build standardized hook response JSON

**Input**: 
- decision (str): "allow" | "deny" | "block" | "modify" | "ask"
- context (dict): Execution context with decisions, modifications, violations

**Output**: 
- dict: Standardized response (see 2.2 specification)

**Implementation Guidelines**:
- Use standardized response template
- Fill in hook_specific_output based on hook type
- Add audit entry
- Add timestamps
- Never modify template structure

**All Hook Handlers Implement These 4 Methods Identically.**

No exceptions. No handler-specific variations.

---

### 2.2 Standardized Hook Response Format

**Every hook, regardless of which hook, returns exactly this JSON structure:**

```json
{
  "decision": "allow|deny|block|modify|ask",
  "timestamp": "ISO 8601",
  "hook_name": "string",
  "session_id": "string",
  
  "metadata": {
    "rules_evaluated": 0,
    "rules_triggered": 0,
    "violations_count": 0,
    "modifications_made": false,
    "phase_transition": null,
    "execution_time_ms": 0
  },
  
  "hook_specific_output": {
    "updated_input": null,
    "additional_context": "string or null",
    "permission_decision": null,
    "reason": "string or null"
  },
  
  "audit_entry": {
    "timestamp": "ISO 8601",
    "session_id": "string",
    "event_type": "hook",
    "hook_name": "string",
    "decision": "string",
    "severity": "info|warning|error|critical",
    "message": "string",
    "context": {},
    "status": "success|error"
  }
}
```

**Field Definitions**:

| Field | Type | Usage | Notes |
|-------|------|-------|-------|
| decision | string | All hooks | Always required; one of 5 values |
| timestamp | ISO 8601 | All hooks | When decision was made |
| hook_name | string | All hooks | Name of hook that fired |
| session_id | string | All hooks | For linking to audit trail |
| metadata.rules_evaluated | int | All hooks | Count of rules checked |
| metadata.rules_triggered | int | All hooks | Count of rules that matched |
| metadata.violations_count | int | All hooks | Count of violations found |
| metadata.modifications_made | bool | All hooks | Whether payload was rewritten |
| metadata.phase_transition | string or null | All hooks | "RESEARCH→EXECUTE" or null |
| metadata.execution_time_ms | int | All hooks | How long handler took |
| hook_specific_output.updated_input | object or null | PreToolUse only | Rewritten tool input |
| hook_specific_output.additional_context | string or null | Most hooks | Message to inject to agent |
| hook_specific_output.permission_decision | string or null | PermissionRequest only | "allow" or "deny" |
| hook_specific_output.reason | string or null | Stop, blocking hooks | Explanation if denying |
| audit_entry | object | All hooks | Full audit log entry |

**Decision Values**:

| Decision | Meaning | Exit Code | When to Use |
|----------|---------|-----------|------------|
| allow | Proceed, no changes | 0 | Tool/action is compliant |
| deny | Reject, re-prompt agent | 0 | Violation detected, agent can retry |
| block | Reject, hard stop | 2 | Critical violation, no retry |
| modify | Proceed with rewritten input | 0 | Ghosting, normalization, or rewriting |
| ask | Ask user for permission | 0 | Rare, only PermissionRequest |

**Hook-Specific Variations** (ONLY these fields vary per hook):

- **SessionStart**: additional_context contains constitution + rules summary
- **UserPromptSubmit**: additional_context contains rewritten prompt
- **PreToolUse**: updated_input contains modified tool input (if modify)
- **PostToolUse**: additional_context contains feedback + phase transition
- **PermissionRequest**: permission_decision contains auto-approval decision
- **Stop**: reason contains completion gate explanation
- **SessionEnd**: (minimal output, mostly logging)
- **PostCompaction**: additional_context contains re-injected state

All other fields are identical across all hooks.

**Exit Code Convention**:
- Exit 0: Always (success or recoverable error)
- Exit 2: Only for block decision (hard stop, Devin must handle)

---

### 2.3 Universal Action Interface

**Every action, regardless of what it checks, implements exactly this interface:**

#### Required Property
```
name: str
  - Returns unique identifier for this action
  - Example: "check_frontmatter", "ghost_template", "block_command"
  - Used for rule YAML reference and auto-discovery
```

#### Required Method 1: get_required_params() → list[str]
**Purpose**: Declare which params this action requires

**Output**: 
- list[str]: Required parameter names

**Implementation Guidelines**:
- Return list of param names that MUST be in rule YAML
- Example: ["target_tools", "required_fields", "scope_dirs"]
- Engine calls this before evaluate() to validate params
- If params missing, rule evaluation fails (logged, not fatal)

#### Required Method 2: validate_params(params: dict) → bool
**Purpose**: Validate param values (types, ranges, etc.)

**Input**: 
- params (dict): Action parameters from rule YAML

**Output**: 
- bool: True if all params valid, False otherwise

**Implementation Guidelines**:
- Check each required param exists
- Check types (list, string, int, bool)
- Check value ranges (e.g., quota > 0)
- Check enum values (e.g., phase in [INIT, RESEARCH, EXECUTE, ...])
- Return False if invalid (don't raise)
- Log warning if invalid

#### Required Method 3: evaluate(payload: dict, params: dict, context: dict) → ActionResult
**Purpose**: Execute the rule check/action

**Input**: 
- payload (dict): Tool call JSON or other data
- params (dict): Parameters from rule YAML (already validated)
- context (dict): Execution context

**Output**: 
- ActionResult (standardized object, see 2.4)

**Implementation Pattern (ALL actions follow this)**:
1. Check if action applies to this tool (most actions skip non-applicable tools)
2. Extract relevant data from payload
3. Perform check or transformation
4. Return ActionResult with decision

**Exception Handling**:
- Catch ALL exceptions
- Log to audit trail (ERROR severity)
- Return {decision: "allow"} (fail open, don't block)
- Never raise to caller

**Standard Implementation Template**:
```
def evaluate(self, payload, params, context):
  # Step 1: Check applicability
  tool = payload.get("tool", "")
  target_tools = params.get("target_tools", [])
  if tool not in target_tools:
    return ActionResult(decision="allow")
  
  # Step 2: Extract data
  content = payload.get("input", {}).get("content", "")
  
  # Step 3: Perform check
  if check_passes(content, params):
    return ActionResult(decision="allow")
  else:
    return ActionResult(
      decision="deny",
      reason="Human-readable explanation",
      rule_id=context.get("rule_id")
    )
```

**All Actions Implement This Pattern Identically.**

---

### 2.4 Standardized ActionResult Format

**Every action returns exactly this format:**

```python
class ActionResult:
  decision: str              # "allow"|"deny"|"modify"|"warn"
  reason: str               # Human-readable explanation
  rule_id: str              # Which rule triggered this result
  modified_payload: dict    # Only if decision="modify"
  modifications: dict       # Details of changes made
  additional_context: str   # Message to inject to agent
  action_metadata: dict     # Execution details
```

**ActionResult Field Definitions**:

| Field | Type | Required | Notes |
|-------|------|----------|-------|
| decision | string | Yes | One of 4 values |
| reason | string | Yes | Why this decision (always provided) |
| rule_id | string | Yes | Which rule this result came from |
| modified_payload | dict | No | Only if decision="modify" |
| modifications | dict | No | What changed (keys, before/after) |
| additional_context | string | No | Message to inject to agent |
| action_metadata | dict | No | execution_time_ms, action_name, etc. |

**Decision Values** (for actions):

| Decision | Meaning | Next Action |
|----------|---------|-------------|
| allow | Check passed, proceed | Continue to next action |
| deny | Check failed, violation | Stop execution, fail fast |
| modify | Transform payload | Continue with modified payload |
| warn | Warning only | Continue (non-blocking) |

**Modified Payload Format** (if decision="modify"):
- Must preserve original structure
- Only modify relevant fields
- Must be valid for tool being called
- Example: {file_path: "...", content: "modified content"}

**Modifications Dict Format** (optional, for audit trail):
```
{
  "template_applied": "python_service.py",
  "line_endings_normalized": true,
  "content_size_before": 1234,
  "content_size_after": 1567,
  "changes": [
    {"type": "frontmatter_added", "size": 333},
    {"type": "line_ending_changed", "from": "CRLF", "to": "LF"}
  ]
}
```

---

### 2.5 Standardized State Machine Interface

**State machine is the single source of truth for session state. All operations use identical interface:**

#### Required Methods (All Components Use These)

**Method 1: load() → bool**
- Load phase.json, tool_counts.json, memory_state.json from disk
- Return True if successful, False if error
- If file missing: initialize to defaults
- If file corrupted: log warning, initialize to defaults
- Never raise exception

**Method 2: save() → bool**
- Save all three state files to disk atomically
- Return True if successful, False if error
- Use temp file + rename pattern for atomicity
- Never raise exception

**Method 3: get_current_phase() → str**
- Return current phase (INIT, RESEARCH, PLAN, EXECUTE, VALIDATE, COMMIT)
- Never returns None; returns INIT if no state loaded

**Method 4: transition_to(phase: str) → bool**
- Transition to new phase
- Validate phase is valid (one of 6 phases)
- Update phase.json with timestamp
- Save to disk
- Return True if successful

**Method 5: get_allowed_tools(phase: str = None) → list[str]**
- Return tools allowed in given phase
- If phase is None, use current_phase
- Return immutable list
- Never empty (at least "read" is always allowed)

**Method 6: add_violation(violation: dict) → None**
- Record violation in current phase
- Violation dict must have: {rule_id, reason, severity, timestamp}
- Update memory_state.json
- Never raise exception

**Method 7: get_state_summary() → dict**
- Return unified view of all state data
- Single query to get everything
- Format: {phase, tool_counts, violations, flags, quotas}
- Used for Status/Logging

**Method 8: is_complete(requirements: dict) → bool**
- Check if session meets completion requirements
- Input requirements: {research_required, validation_required, tests_passing, etc.}
- Return True if all requirements met
- Used by Stop hook

**Method 9: get_tool_count(tool_name: str) → int**
- Get usage count for specific tool
- Example: get_tool_count("web_search") → 5
- Return 0 if tool never used

**Method 10: increment_tool_count(tool_name: str) → None**
- Increment usage count for tool
- Called by PreToolUse for each tool call
- Save to disk immediately

**Method 11: validate_phase_transition(from_phase: str, tool: str) → bool**
- Check if transitioning from one phase to another is valid
- Used by PreToolUse to check phase progression
- Return True if transition allowed, False if violation

**All Components Use These Same 11 Methods.**

No component implements its own state logic. All state operations go through StateMachine.

---

### 2.6 Unified Audit Entry Format

**Every event, regardless of type, logs exactly this format to JSONL:**

```json
{
  "timestamp": "ISO 8601",
  "session_id": "string",
  "event_type": "hook|action|phase_transition|violation|state_change|error",
  "severity": "info|warning|error|critical",
  
  "source": {
    "hook_name": "string or null",
    "action_name": "string or null",
    "rule_id": "string or null"
  },
  
  "context": {
    "phase": "string",
    "tool": "string or null",
    "decision": "allow|deny|modify|warn|block",
    "status": "success|error"
  },
  
  "data": {
    "message": "string",
    "details": {},
    "error": "string or null"
  },
  
  "audit_metadata": {
    "logged_by": "component_name",
    "entry_type": "request|response|state_change",
    "entry_id": "uuid"
  }
}
```

**Entry Type Variations**:

| Event Type | Source | Context | Data |
|-----------|--------|---------|------|
| hook | hook_name | phase, tool, decision | message, hook details |
| action | action_name, rule_id | phase, tool, decision | check result, violations |
| phase_transition | rule_id or hook_name | from_phase, to_phase | trigger, reason |
| violation | rule_id | phase, severity | violation details |
| state_change | component_name | phase | what changed |
| error | component_name | phase | error message, stack trace |

**All Audit Entries Follow This Schema.**

No exceptions. Queryable. Analyzable. Immutable.

---

## Part 3: Data-Driven Configuration

### 3.1 Configuration File Structure

All configuration is externalized to YAML files in `Rules/Config/` directory.

Governor loads configuration at startup, not hardcoded.

#### File 1: `Rules/Config/phases.yaml`

**Purpose**: Define all execution phases, allowed tools, transitions

**Structure**:
```yaml
phases:
  INIT:
    description: "Session initialization"
    allowed_tools: [read]
    transitions:
      web_search: RESEARCH
      file_write: EXECUTE
      file_edit: EXECUTE
    enforcement: "block"  # block|redirect|warn
    
  RESEARCH:
    description: "Information gathering phase"
    allowed_tools: [web_search, read]
    transitions:
      file_write: EXECUTE
      file_edit: EXECUTE
      exec_test: VALIDATE
      exec_git: COMMIT
    enforcement: "block"
    quotas:
      web_search_minimum: 5
      quality_check: true
    
  PLAN:
    description: "Architecture and planning phase (optional)"
    allowed_tools: [read]
    transitions:
      file_write: EXECUTE
      file_edit: EXECUTE
    enforcement: "warn"
    
  EXECUTE:
    description: "Implementation phase"
    allowed_tools: [file_write, file_edit, exec, read]
    transitions:
      exec_test: VALIDATE
      exec_git: COMMIT
    enforcement: "block"
    
  VALIDATE:
    description: "Testing and verification phase"
    allowed_tools: [exec, read, file_edit]
    transitions:
      exec_git: COMMIT
    enforcement: "block"
    quotas:
      test_required: true
      max_retries: 3
    
  COMMIT:
    description: "Version control and finalization"
    allowed_tools: [exec]
    allowed_exec_patterns: ["git"]
    transitions: {}
    enforcement: "block"

phase_defaults:
  enforcement: "block"  # default enforcement strategy
  auto_transition: true  # automatically transition on tool call
```

**Usage**:
- Governor loads at SessionStart
- Engine consults phases.yaml for allowed_tools per phase
- PreToolUse checks tool against allowed_tools[current_phase]
- Phase transitions triggered by exec_* patterns (defined here)

#### File 2: `Rules/Config/permissions.yaml`

**Purpose**: Define permission policies for auto-approval/denial

**Structure**:
```yaml
permissions:
  file_write:
    policy: "auto_allow"
    reason: "Governed by template ghosting"
    
  file_read:
    policy: "auto_allow"
    reason: "Read-only, safe"
    
  file_delete:
    policy: "auto_deny"
    reason: "Destructive operation requires human review"
    
  exec_shell_true:
    policy: "auto_deny"
    reason: "Shell injection risk"
    
  exec_test_pattern:
    policy: "auto_allow"
    patterns: ["pytest", "unittest", "npm test", "cargo test"]
    reason: "Tests are validated separately"
    
  exec_git:
    policy: "auto_allow"
    patterns: ["git commit", "git push", "git tag"]
    requires_commit_message: true
    reason: "Git operations logged in audit trail"
    
  web_search:
    policy: "auto_allow"
    reason: "Read-only, rate-limited"
    
  exec_dangerous:
    policy: "auto_deny"
    patterns: ["rm -rf", "chmod 777", "eval(", "exec("]
    reason: "Dangerous shell commands blocked"

policy_defaults:
  policy: "auto_deny"  # default to denying unknown operations
  reason: "Unknown operation, denied by default"
```

**Usage**:
- PermissionRequest hook loads this file
- Consults policy for requested operation
- Returns auto_allow or auto_deny

#### File 3: `Rules/Config/tools.yaml`

**Purpose**: Define tool metadata and patterns

**Structure**:
```yaml
tools:
  web_search:
    type: "information_gathering"
    pattern_type: "none"
    
  read:
    type: "information_gathering"
    pattern_type: "none"
    
  file_write:
    type: "modification"
    pattern_type: "none"
    requires_frontmatter: true
    
  file_edit:
    type: "modification"
    pattern_type: "none"
    
  exec:
    type: "execution"
    pattern_type: "regex"
    patterns:
      test: "(pytest|unittest|npm test|cargo test|go test|mocha)"
      git: "(git commit|git push|git tag|git branch)"
      shell: "(rm|chmod|mv|cp|mkdir|touch)"
    dangerous: ["rm -rf", "chmod 777", "eval(", "exec(", ":(){:|:&};"]
    
tool_counts:
  web_search:
    phase: RESEARCH
    quota: 5
    required: true
    
  file_write:
    phase: EXECUTE
    quota: null
    required: false
    
  exec_test:
    phase: VALIDATE
    quota: null
    required_if_validation_required: true
```

**Usage**:
- Tool counting in PostToolUse references this
- Phase inference references patterns
- Dangerous command blocking references dangerous list

#### File 4: `Rules/Config/actions.yaml`

**Purpose**: Map actions to hooks and define default parameters

**Structure**:
```yaml
actions:
  check_frontmatter:
    description: "Validate YAML frontmatter exists with required fields"
    triggers: [PreToolUse, PostToolUse]
    default_params:
      target_tools: [file_write, file_edit]
      scope_dirs: [Rules/, Scripts/]
      required_fields: [id, version, owner, updated, purpose, agent, persona]
    
  check_encoding:
    description: "Validate UTF-8 encoding and LF line endings"
    triggers: [PreToolUse]
    default_params:
      target_tools: [file_write, file_edit]
      expected_encoding: "utf-8"
      line_ending: "lf"
    
  ghost_template:
    description: "Apply canonical template to file"
    triggers: [PreToolUse]
    default_params:
      target_tools: [file_write]
      template_map:
        .py: Rules/Templates/python_service.py
        .md: Rules/Templates/markdown_doc.md
        .yaml: Rules/Templates/yaml_rule.yaml
        .json: Rules/Templates/json_config.json
    
  block_command:
    description: "Block dangerous shell commands"
    triggers: [PreToolUse]
    default_params:
      target_tools: [exec]
      forbidden_patterns: []  # Load from tools.yaml
    
  check_placement:
    description: "Validate file created in correct directory"
    triggers: [PreToolUse]
    default_params:
      target_tools: [file_write]
      allowed_dirs: []  # Define per rule
    
  check_agent_scope:
    description: "Validate agent authority"
    triggers: [PreToolUse]
    default_params:
      agent: "all"
      allowed_operations: []  # Define per rule
    
  count_tool_usage:
    description: "Track tool usage for quota enforcement"
    triggers: [PreToolUse, PostToolUse]
    default_params: {}  # Automatic
    
  schema_validate:
    description: "Validate JSON/YAML schema"
    triggers: [PreToolUse]
    default_params:
      target_tools: [file_write]
    
  fact_check:
    description: "Verify citations in research"
    triggers: [PostToolUse]
    default_params:
      require_sources: true
      min_source_count: 3
    
  memory_inject:
    description: "Inject prior solutions to prevent regression"
    triggers: [SessionStart, PostToolUse]
    default_params:
      memory_key: "solutions"
      relevance_threshold: 0.8

action_composition:
  PreToolUse:
    order:
      - check_frontmatter
      - check_encoding
      - ghost_template
      - block_command
      - check_placement
      - check_agent_scope
      - schema_validate
    merge_strategy: "deep_merge"  # Merge modifications from multiple actions
    error_strategy: "fail_fast"   # Stop on first deny
```

**Usage**:
- Engine references this to load actions
- Engine uses order for action sequencing
- Engine applies default_params to rules

#### File 5: `Rules/Config/state_schema.yaml`

**Purpose**: Define schema for state files (validation)

**Structure**:
```yaml
state_files:
  phase.json:
    version: "1.0"
    schema:
      current_phase: "enum:[INIT, RESEARCH, PLAN, EXECUTE, VALIDATE, COMMIT]"
      phase_start_timestamp: "string:iso8601"
      previous_phase: "string"
      phase_transition_count: "integer"
      violation_in_phase: "array[object]"
      completion_allowed: "boolean"
    
  tool_counts.json:
    version: "1.0"
    schema:
      web_search_count: "integer"
      file_write_count: "integer"
      file_edit_count: "integer"
      exec_count: "integer"
      exec_test_count: "integer"
      exec_git_count: "integer"
      research_quota_required: "integer"
      research_quota_met: "boolean"
      validation_required: "boolean"
      validation_test_passed: "boolean"
      validation_retry_count: "integer"
      validation_retry_limit: "integer"
    
  memory_state.json:
    version: "1.0"
    schema:
      session_id: "string"
      prompt_intent: "enum:[QUESTION, CODE_GEN, DEBUG, REFACTOR, DOCS]"
      research_required_flag: "boolean"
      plan_required_flag: "boolean"
      validation_required_flag: "boolean"
      recent_violations: "array[object]"
      phase_requirements: "object"
      special_constraints: "array[string]"

state_file_wrapper:
  required_fields:
    - metadata.version
    - metadata.last_updated
    - metadata.session_id
    - data
    - audit.created
```

**Usage**:
- StateMachine validates state files against schema on load
- Invalid files rejected (corrupted), reset to defaults

---

## Part 4: Automatic Component Discovery

### 4.1 Hook Handler Auto-Discovery

**Location**: `Governor/hook_handlers/`

**Discovery Algorithm**:
1. Scan `Governor/hook_handlers/` directory
2. Find all `.py` files (exclude `_*.py`)
3. For each file:
   - Import as module
   - Find all classes inheriting from HookHandler
   - Instantiate class
   - Query `hook_name` property
   - Register in HOOK_HANDLERS dict with hook_name as key
4. At startup, all 8 handlers auto-loaded

**Registration Result**:
```
HOOK_HANDLERS = {
  "SessionStart": SessionStartHandler(),
  "UserPromptSubmit": UserPromptSubmitHandler(),
  "PreToolUse": PreToolUseHandler(),
  "PostToolUse": PostToolUseHandler(),
  "PermissionRequest": PermissionRequestHandler(),
  "Stop": StopHandler(),
  "SessionEnd": SessionEndHandler(),
  "PostCompaction": PostCompactionHandler()
}
```

**No Registration Code Needed.**

---

### 4.2 Action Auto-Discovery

**Location**: `Governor/actions/`

**Discovery Algorithm**:
1. Scan `Governor/actions/` directory
2. Find all `.py` files (exclude `_*.py`)
3. For each file:
   - Import as module
   - Find all classes inheriting from RuleAction
   - Instantiate class
   - Query `name` property
   - Register in ACTION_REGISTRY dict with name as key
4. At startup, all actions auto-loaded

**Registration Result**:
```
ACTION_REGISTRY = {
  "check_frontmatter": CheckFrontmatterAction(),
  "check_encoding": CheckEncodingAction(),
  "ghost_template": GhostTemplateAction(),
  "block_command": BlockCommandAction(),
  "check_placement": CheckPlacementAction(),
  "check_agent_scope": CheckAgentScopeAction(),
  "count_tool_usage": CountToolUsageAction(),
  "schema_validate": SchemaValidateAction(),
  "fact_check": FactCheckAction(),
  "memory_inject": MemoryInjectAction()
}
```

**No Registration Code Needed.**

**Adding New Action**:
1. Create `Governor/actions/new_action.py`
2. Implement class inheriting from RuleAction
3. Implement 3 methods + name property
4. Done. Auto-discovered on next startup.

---

### 4.3 Rule Auto-Discovery

**Location**: `Rules/` directory (all subdirectories)

**Discovery Algorithm**:
1. Scan `Rules/Shared/`, `Rules/Architect/`, `Rules/Executor/`, etc.
2. Find all `.yaml` files
3. For each file:
   - Parse YAML
   - Validate against rule schema
   - Extract `id` and `triggers` fields
   - Index by id and trigger hooks
4. At SessionStart, load rules applicable to session
5. At each hook, load rules applicable to that hook

**Rule Loading**:
- Rules loaded at SessionStart (full scan)
- Rules filtered by hook name on each hook call
- Rules sorted by tier (blocking → warning → observational)
- Invalid rules logged (not fatal)

**No Rule Registration Code Needed.**

**Adding New Rule**:
1. Create `Rules/Category/ID.yaml`
2. Define metadata (id, version, tier, triggers, actions)
3. Done. Auto-loaded on next hook.

---

## Part 5: Standardized Action Composition

### 5.1 Action Sequencing Rules

**All actions in a rule execute in YAML order (top to bottom).**

```yaml
check:
  params:
    actions:
      - name: check_frontmatter      # Runs first
      - name: check_encoding         # Runs second
      - name: ghost_template         # Runs third
```

**Sequence is immutable. No reordering.**

### 5.2 Action Chaining Rules

**Output of Action 1 becomes input of Action 2.**

**Decision Chaining**:
```
Action 1 decision: "allow"
  ↓
Action 2 receives: original payload
  ↓
Action 2 decision: "deny"
  ↓
STOP (fail fast on first deny)

---

Action 1 decision: "deny"
  ↓
STOP (fail immediately, don't execute Action 2)

---

Action 1 decision: "modify"
  ↓
Action 2 receives: modified payload
  ↓
Action 2 decision: "allow"
  ↓
CONTINUE
```

**Payload Chaining**:
```
Action 1 modifies: {file_path: "auth.py", content: "def auth(): pass"}
  ↓
Action 2 receives: {file_path: "auth.py", content: "def auth(): pass"}
  ↓
Action 2 modifies: {file_path: "auth.py", content: "---\nid: auth\n---\n\ndef auth(): pass"}
  ↓
Final payload: templated + original content
```

**Context Chaining**:
```
Action 1 decision: "deny" (reason: "Missing frontmatter")
  ↓
Context updated: {violations: [{rule: check_frontmatter, reason: "..."}]}
  ↓
STOP (don't run Action 2)

---

Action 1 decision: "warn" (reason: "Missing encoding spec")
  ↓
Context updated: {warnings: [...]}
  ↓
Action 2 receives: same context + warning added
  ↓
CONTINUE
```

### 5.3 Modification Merging Rules

**When multiple actions return "modify", merge modifications:**

```
Action 1 modifies: {content: "modified by 1"}
Action 2 modifies: {content: "modified by 2"}

Conflict? YES (both modify same field)
Result: DENY (error: conflicting modifications)

---

Action 1 modifies: {content: "modified by 1"}
Action 2 modifies: {line_ending: "LF"}

Conflict? NO (different fields)
Result: MERGE (deep merge modifications)
Final payload: {content: "modified by 1", line_ending: "LF"}
```

**Merge Strategy** (defined in `Rules/Config/actions.yaml`):
- `deep_merge`: Merge at object level (default)
- `replace`: Later action replaces earlier (error if conflict)
- `sequential`: Modifications applied sequentially (safe)

### 5.4 Context Injection Ordering

**When multiple actions return additionalContext:**

```
Action 1 context: "Frontmatter added."
Action 2 context: "Line endings normalized."

Result: Concatenate in order
Final context: "Frontmatter added. Line endings normalized."
```

**Ordering**: Strict execution order → strict context order

---

## Part 6: Standardized State Management

### 6.1 Unified State File Wrapper

**All state files have identical wrapper structure:**

```json
{
  "metadata": {
    "version": "1.0",
    "file_type": "phase|tool_counts|memory_state",
    "created": "ISO 8601",
    "last_updated": "ISO 8601",
    "session_id": "string",
    "source": "governor.py"
  },
  
  "data": {
    // File-specific data here
    // phase.json: {current_phase, phase_start_timestamp, ...}
    // tool_counts.json: {web_search_count, file_write_count, ...}
    // memory_state.json: {prompt_intent, flags, violations, ...}
  },
  
  "audit": {
    "created_by_hook": "string",
    "modifications_count": 0,
    "last_modified_by_hook": "string",
    "last_modified_timestamp": "ISO 8601",
    "checksum": "sha256 hash of data"
  }
}
```

**Benefits**:
- Identical structure across all files
- Easy to query state (all files have same wrapper)
- Corruption detection (checksum validation)
- Audit trail per file (who modified it)

### 6.2 Unified State Query Interface

**All state queries go through StateMachine methods:**

```
# Instead of reading files directly:
import json
with open('.devin/state/phase.json') as f:
  phase = json.load(f)['data']['current_phase']

# Use standardized method:
phase = state_machine.get_current_phase()
```

**This ensures**:
- Single source of truth
- Error handling centralized
- Validation consistent
- Atomicity guaranteed

### 6.3 State Mutation Atomicity

**All state mutations are atomic:**

```
state_machine.transition_to("RESEARCH")
  1. Load current state from disk
  2. Validate transition (INIT → RESEARCH allowed)
  3. Update phase.json with new phase
  4. Update timestamp
  5. Write to temp file
  6. Atomic rename (temp → actual)
  7. Save to disk
  8. Return True

If any step fails:
  - Rollback (delete temp file)
  - Log error
  - Return False
  - State unchanged
```

**No partial updates. No corrupted state.**

---

## Part 7: Standardized Audit and Logging

### 7.1 Unified Audit Entry Schema

**Every event, regardless of source, logs exactly this format (already specified in 2.6):**

File: `Logs/Audit/audit_trail.jsonl`

One JSON object per line, immutable append-only.

**Query Examples**:
```
# Find all violations for session
grep '"event_type":"violation"' audit_trail.jsonl | grep 'sess_abc123'

# Find all PreToolUse decisions
grep '"hook_name":"PreToolUse"' audit_trail.jsonl

# Find all "deny" decisions
grep '"decision":"deny"' audit_trail.jsonl

# Find all errors
grep '"severity":"error"' audit_trail.jsonl
```

### 7.2 Violations Log Format

**File**: `Logs/Audit/violations.jsonl`

Same audit entry format, filtered to violations only.

**Queryable**: Find violations by rule_id, severity, session_id, timestamp.

### 7.3 Compliance Report Schema

**File**: `Logs/Sessions/<session_id>/compliance_report.json`

**Fixed JSON structure** (not JSONL):

```json
{
  "session_summary": {
    "session_id": "string",
    "start_time": "ISO 8601",
    "end_time": "ISO 8601",
    "duration_seconds": 0,
    "success": true
  },
  
  "phases": {
    "completed": ["INIT", "RESEARCH", "EXECUTE", "VALIDATE"],
    "final_phase": "VALIDATE",
    "phase_durations": {
      "INIT": 5,
      "RESEARCH": 45,
      "EXECUTE": 120,
      "VALIDATE": 30
    }
  },
  
  "compliance": {
    "rules_evaluated": 0,
    "rules_violations": 0,
    "compliance_rate": 0.98,
    "violations_by_severity": {
      "critical": 0,
      "high": 1,
      "medium": 0,
      "low": 2
    }
  },
  
  "tools": {
    "web_search": {"count": 7, "quota": 5, "quota_met": true},
    "file_write": {"count": 3},
    "file_edit": {"count": 1},
    "exec": {"count": 5, "test_count": 3, "git_count": 1}
  },
  
  "violations": [
    {"timestamp": "...", "rule_id": "SHR-01", "severity": "high", "reason": "..."}
  ],
  
  "escalations": []
}
```

---

## Part 8: Error Handling Standardization

### 8.1 Unified Error Handling Policy

**Every component follows identical error policy:**

```
For every fallible operation:
  try:
    execute operation
  catch exception:
    1. Log to audit trail (ERROR severity)
    2. Log full stack trace to stderr
    3. Return safe default (allow decision, continue)
    4. Never raise exception to caller
    5. Never halt execution
```

**Standard Safe Defaults**:
- Hook error: return {decision: "allow"}
- Action error: return {decision: "allow"}
- State error: initialize to defaults, continue
- Rule load error: skip rule, continue
- Action load error: skip action, continue

### 8.2 Unified Error Format

**Error Audit Entry** (standard format, see 2.6):

```json
{
  "timestamp": "ISO 8601",
  "session_id": "string",
  "event_type": "error",
  "severity": "error",
  "source": {
    "component": "string",
    "method": "string"
  },
  "context": {
    "phase": "string",
    "operation": "string"
  },
  "data": {
    "message": "Error message",
    "error_type": "ExceptionType",
    "stack_trace": "full stack trace"
  }
}
```

**All errors logged this way. Queryable. Recoverable.**

### 8.3 Recovery Procedures

**For Each Failure Mode** (Already specified in Part 9 of previous doc):
- Detection: How to identify the failure
- Action: What Governor does immediately
- Recovery: What governor does to recover
- Logging: What gets logged

All follow standardized error handling policy.

---

## Part 9: Implementation Checklist (Modularity & Standardization)

### Phase 1: Foundation (Standardization)
- [ ] Implement HookHandler abstract base with 4 required methods
- [ ] Implement RuleAction abstract base with 3 required methods
- [ ] Implement ActionResult dataclass with standardized fields
- [ ] Implement StateMachine with 11 standardized methods
- [ ] Test: Each component implements exactly required interface

### Phase 2: Configuration (Data-Driven)
- [ ] Create `Rules/Config/phases.yaml` with all 6 phases
- [ ] Create `Rules/Config/permissions.yaml` with policies
- [ ] Create `Rules/Config/tools.yaml` with tool metadata
- [ ] Create `Rules/Config/actions.yaml` with action composition
- [ ] Create `Rules/Config/state_schema.yaml` for validation
- [ ] Test: Governor loads and parses all config files

### Phase 3: Auto-Discovery (Modularity)
- [ ] Implement hook handler auto-discovery registry
- [ ] Implement action auto-discovery registry
- [ ] Implement rule auto-discovery scan
- [ ] Test: Adding new hook/action/rule auto-discovered

### Phase 4: Standardized Responses (Format)
- [ ] Implement response builder (all hooks use same builder)
- [ ] Test: All hooks return identical JSON structure
- [ ] Verify: All fields populated correctly per hook type

### Phase 5: Unified State (Management)
- [ ] Implement state file wrapper (identical for all files)
- [ ] Implement StateMachine with 11 methods
- [ ] Implement atomic saves (temp file + rename)
- [ ] Test: State persists, survives corruption, recovers

### Phase 6: Unified Audit (Logging)
- [ ] Implement audit entry formatter (all events same format)
- [ ] Implement JSONL writer (append-only)
- [ ] Implement query interface for audit trail
- [ ] Test: All events logged, queryable, immutable

### Phase 7: Error Standardization (Resilience)
- [ ] Implement unified error handler (try/catch pattern)
- [ ] Implement error recovery procedures
- [ ] Test: Errors logged, system continues, state intact

### Phase 8: Integration (Full System)
- [ ] All 8 hooks implemented with standard interface
- [ ] All core actions implemented with standard interface
- [ ] All 5 config files created
- [ ] Auto-discovery working
- [ ] End-to-end test scenarios passing
- [ ] Audit trail complete and queryable

---

## Part 10: Completeness Verification

### Modularity Verification Checklist

**Hook Handlers**:
- [ ] All 8 handlers implement identical 4-method interface
- [ ] Adding new hook requires only new `.py` file
- [ ] No modification to core code

**Actions**:
- [ ] All actions implement identical 3-method interface
- [ ] Adding new action requires only new `.py` file
- [ ] No modification to core code

**Rules**:
- [ ] Adding new rule requires only YAML file
- [ ] No modification to core code
- [ ] Auto-discovered on next hook

**Configuration**:
- [ ] All phases defined in YAML (not hardcoded)
- [ ] All tools defined in YAML (not hardcoded)
- [ ] All permissions defined in YAML (not hardcoded)
- [ ] All actions mapped in YAML (not hardcoded)

**State Management**:
- [ ] All state operations go through StateMachine
- [ ] No direct file access except in StateMachine
- [ ] No circular dependencies

### Standardization Verification Checklist

**Hook Handlers**:
- [ ] All handlers use same 4-method signature
- [ ] All handlers use same response format
- [ ] All handlers follow same error handling
- [ ] All handlers validate input identically

**Actions**:
- [ ] All actions use same 3-method signature
- [ ] All actions return identical ActionResult
- [ ] All actions validate params identically
- [ ] All actions handle errors identically

**Responses**:
- [ ] All hooks return identical JSON structure
- [ ] No hook-specific fields in main body
- [ ] Hook-specific fields only in hook_specific_output
- [ ] All responses include audit_entry

**State Files**:
- [ ] All state files have identical wrapper
- [ ] All state operations via StateMachine methods
- [ ] All state mutations atomic
- [ ] All state backed up with checksum

**Audit Entries**:
- [ ] All events use identical entry format
- [ ] All entries queryable by any field
- [ ] All entries immutable (JSONL append-only)
- [ ] All errors logged with stack trace

---

## Conclusion

Governor.py with **complete modularity and standardization** is now fully specified.

**Key Achievements**:

✅ **Universal Interfaces**: Hook handlers, actions, state management all follow identical patterns

✅ **Standardized Formats**: All hooks return same JSON, all audits use same schema, all errors follow same format

✅ **Data-Driven Config**: All phases, tools, permissions, actions defined in YAML (not hardcoded)

✅ **Automatic Discovery**: New hooks/actions/rules auto-discovered (no registration code)

✅ **Unified State**: All state operations through single interface, atomic, recoverable

✅ **Complete Audit Trail**: All events logged in single queryable format, immutable

**An Architect agent can now implement Governor.py with mechanical precision, following these specifications exactly.**

No guessing. No ambiguity. Complete modularity. Complete standardization.
