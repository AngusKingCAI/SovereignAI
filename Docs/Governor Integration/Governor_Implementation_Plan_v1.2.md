# Governor.py v1.5 Implementation Plan v1.2

**Project:** Governor.py - Devin CLI Governance Framework  
**Specification Version:** v1.5  
**Plan Version:** 1.2 (Revised based on second external AI review)  
**Target Framework:** Architect > Planner > Executor > Reviewer (App-specific) + Harness Review Capability  
**Implementation Date:** 2026-08-05  
**Estimated Duration:** 4-6 weeks (2-3 person team)  
**Team Size Assumption:** 2-3 developers

---

## Executive Summary

This implementation plan outlines the development of Governor.py v1.5, a deterministic control layer for Devin CLI that enforces rule adherence through hook-based architecture. The system will support both App-level governance (Planner → Executor → Reviewer) and Harness-level governance (Reviewing Governor itself).

**Key Objectives:**
- Implement Governor.py v1.5 with full Devin CLI protocol compliance
- Integrate with existing Architect > Planner > Executor > Reviewer framework
- Enable dual-mode Reviewer (App review + Harness review)
- Ensure App vs Harness rule scoping
- Implement enhanced security for self-modification

**Success Criteria:**
- All 8 Devin CLI hooks implemented and tested
- Two-tier decision model working (internal → protocol mapping)
- Framework integration tested with all agent roles
- Harness review mode functional with enhanced security
- Cross-platform compatibility verified (Windows Tier-1)

---

## v1.2 Revision Summary

**Must-Fix Items Applied (from second external AI review):**
- ✅ Fixed to_devin_decision() to raise explicit ValueError per spec
- ✅ Fixed build_hook_response() signature with explicit keyword-only parameters per spec
- ✅ Fixed circuit breaker implementation with per-action keying per v1.5 spec §12.7
- ✅ Fixed pyproject.toml to match v1.5 spec Appendix O (pyyaml in dependencies, granular extras)
- ✅ Added timeout fields to .devin/hooks.v1.json per v1.5 spec §10.1
- ✅ Added Bash|Write|Edit matchers for PreToolUse/PostToolUse per v1.5 spec §4.3
- ✅ Fixed audit logging to use current_hash instead of event_hash per v1.5 spec §5.1
- ✅ Enhanced mode detection with command prefix as primary trigger
- ✅ Added Task 2.15: Sample Components Integration Test

**v1.1 Fixes (from first external AI review):**
- ✅ Fixed build_hook_response() to place governor_internal at top level (not nested in hookSpecificOutput)
- ✅ Added Task 2.2 dependency to all hook handler tasks
- ✅ Moved foundational modules (Tasks 2.1-2.4) to Phase 1
- ✅ Moved fsync + checksums to Task 1.6 (state_machine.py)
- ✅ Restructured phases to place hook handlers in Phase 2

**High-Priority Additions:**
- ✅ Added Phase 2.5: Sample Rules & Templates
- ✅ Added Phase 7: Integration & CI
- ✅ Added missing spec components (templates, actions, .devin/hooks.v1.json, etc.)
- ✅ Aligned memoization implementation with v1.5 spec
- ✅ Aligned circuit breaker implementation with v1.5 spec
- ✅ Added internal decision recording to audit logging
- ✅ Improved harness review mode detection

**Medium-Priority Improvements:**
- ✅ Clarified Phase 5 security features as implementing existing v1.5 spec
- ✅ Fixed coverage metrics to be meaningful
- ✅ Added team-size assumptions
- ✅ Added rollout phase mapping table
- ✅ Added Phase 6: Validation with spec-defined stages

---

## Implementation Phases (Restructured)

### Phase 1: Foundation (Week 1-2)
**Goal:** Establish core Governor infrastructure with protocol compliance

**Deliverables:**
- Working Governor.py entry point
- Protocol mapping layer (protocol.py) - FIXED governor_internal placement
- Basic hook handler infrastructure
- State machine with file locking + crash-safety (fsync + checksums)
- Audit logging system
- Foundational modules: tool_normalizer, engine, base classes

### Phase 2: Core Hooks & Rules (Week 2-3)
**Goal:** Implement hook handlers and rule system

**Deliverables:**
- All 8 hook handlers (SessionStart, UserPromptSubmit, PreToolUse, PostToolUse, PermissionRequest, Stop, SessionEnd, PostCompaction)
- Rule loading engine with mtime caching
- Action execution framework
- Base action and handler classes
- YAML rule validation
- Sample rules and templates

### Phase 2.5: Sample Rules & Templates (Week 3)
**Goal:** Create sample implementation components

**Deliverables:**
- Template system with manifest.yaml
- Sample template files
- Sample actions (block_command, ghost_template, present_bypass_menu)
- Sample rule YAMLs
- team_bypasses.json initial file
- Sample components integration test

### Phase 3: Framework Integration (Week 3-4)
**Goal:** Integrate with Architect > Planner > Executor > Reviewer framework

**Deliverables:**
- Agent-specific rule filtering
- App vs Harness path scoping
- Context-aware Reviewer mode
- Framework-specific rule templates
- Integration testing with all agents

### Phase 4: Advanced Features (Week 4-5)
**Goal:** Implement production-grade features and debugging

**Deliverables:**
- Per-layer debug logging
- Execution tracing with trace_id
- State inspection CLI tools
- Circuit breakers (full spec implementation)
- Action memoization (spec-compliant)
- Structured logging (optional)

### Phase 5: Security & Hardening (Week 5-6)
**Goal:** Implement security measures (existing v1.5 spec features)

**Deliverables:**
- Harness file protection (per v1.5 spec §6.4)
- Team-level bypass enforcement (existing v1.5 spec)
- Security threat model implementation (per v1.5 spec §6.4)
- Penetration testing (smoke-test level)
- Security validation

### Phase 6: Validation (Week 6)
**Goal:** Execute spec-defined validation stages

**Deliverables:**
- Stage 9: Cross-platform validation
- Stage 11: Debugging infrastructure validation
- Stage 12: Protocol alignment validation
- Final acceptance testing

### Phase 7: Integration & CI (Week 6)
**Goal:** Production deployment setup

**Deliverables:**
- .devin/hooks.v1.json configuration (with timeouts and matchers per spec)
- pyproject.toml with dependency groups (per spec Appendix O)
- CI/CD pipeline setup
- Cross-platform validation automation
- Documentation completion

---

## Detailed Task List (Restructured)

### Phase 1: Foundation Tasks

#### Task 1.1: Project Setup and Structure
**Priority:** CRITICAL  
**Estimated Time:** 4 hours  
**Dependencies:** None

**Subtasks:**
- [ ] Create Governor/ directory structure per v1.5 spec
- [ ] Set up Python virtual environment
- [ ] Create pyproject.toml with dependency groups
- [ ] Configure optional dependencies ([all] extra)
- [ ] Set up .gitignore for state/ and logs/
- [ ] Create initial __init__.py files

**Verification:**
```bash
# Directory structure matches spec
ls -la Governor/
# pyproject.toml created and valid
pip install -e ".[all]"  # succeeds
```

---

#### Task 1.2: Protocol Mapping Layer (protocol.py) - FIXED
**Priority:** CRITICAL  
**Estimated Time:** 6 hours  
**Dependencies:** Task 1.1

**Subtasks:**
- [ ] Create Governor/protocol.py module
- [ ] Implement to_devin_decision() function
- [ ] Implement build_hook_response() function with FIXED governor_internal placement
- [ ] Add decision mapping tests
- [ ] Add governor_internal field preservation
- [ ] Document protocol isolation benefits

**Implementation Requirements (FIXED):**
```python
# Governor/protocol.py
def to_devin_decision(internal: str) -> str:
    """Map internal decisions to Devin protocol."""
    mapping = {
        "allow": "approve",
        "modify": "approve", 
        "warn": "approve",
        "deny": "block"
    }
    if internal not in mapping:
        raise ValueError(f"Unknown internal decision: {internal!r}")
    return mapping[internal]

def build_hook_response(
    internal_decision: str,
    reason: str,
    hook_event_name: str,
    *,
    additional_context: str = "",
    updated_input: dict | None = None,
    bypass_menu: dict | None = None,
    permission_decision: str | None = None,
) -> dict:
    """Build Devin-compatible hook response with explicit keyword-only parameters."""
    response = {
        "decision": to_devin_decision(internal_decision),
        "governor_internal": {
            "decision": internal_decision
        },
        "reason": reason,
        "hookSpecificOutput": {
            "hookEventName": hook_event_name,
        }
    }
    
    # Conditional field addition per spec
    if additional_context:
        response["hookSpecificOutput"]["additionalContext"] = additional_context
    if updated_input is not None and internal_decision == "modify":
        response["hookSpecificOutput"]["updatedInput"] = updated_input
    if bypass_menu is not None:
        response["hookSpecificOutput"]["bypass_menu"] = bypass_menu
    if permission_decision is not None:
        response["hookSpecificOutput"]["permissionDecision"] = permission_decision
    
    return response
```

**Verification:**
- Unit tests for all decision mappings
- Verify output matches Devin CLI protocol format
- Test with mock hook payloads
- Verify governor_internal at top level of JSON

---

#### Task 1.3: Cross-Platform File Locking (locking.py)
**Priority:** CRITICAL  
**Estimated Time:** 8 hours  
**Dependencies:** Task 1.1

**Subtasks:**
- [ ] Create Governor/locking.py module
- [ ] Implement portalocker backend (preferred)
- [ ] Implement msvcrt backend (Windows fallback)
- [ ] Implement fcntl backend (Unix fallback)
- [ ] Add backend selection logic
- [ ] Implement exponential backoff with jitter
- [ ] Add deadlock detection (wait-for graph)
- [ ] Test on Windows (primary platform)
- [ ] Test on Unix/Linux if available

**Verification:**
- Lock acquisition/release on all platforms
- Concurrent access testing
- Deadlock detection testing
- Performance benchmarking

---

#### Task 1.4: Path Normalization (paths.py)
**Priority:** HIGH  
**Estimated Time:** 4 hours  
**Dependencies:** Task 1.1

**Subtasks:**
- [ ] Create Governor/paths.py module
- [ ] Implement safe_join() for path traversal protection
- [ ] Implement matches_glob() for pattern matching
- [ ] Add Windows backslash handling
- [ ] Implement POSIX path conversion for audit logs
- [ ] Add case-insensitive matching for Windows

**Verification:**
- Path traversal attack testing
- Cross-platform path handling
- Glob pattern matching accuracy

---

#### Task 1.5: Entry Point and Dispatcher (governor.py)
**Priority:** CRITICAL  
**Estimated Time:** 6 hours  
**Dependencies:** Tasks 1.1, 1.2, 1.3

**Subtasks:**
- [ ] Create Governor/governor.py entry point
- [ ] Implement hook argument parsing (sys.argv[1])
- [ ] Implement stdin JSON payload reading
- [ ] Implement _dispatch_error() with protocol compliance
- [ ] Add hook handler registry routing
- [ ] Implement exception handling with fail-open
- [ ] Add state machine lifecycle management
- [ ] Implement audit logging for all events

**Implementation Requirements:**
```python
def _dispatch_error(hook_name, error, payload):
    """Fail-open error handler with Devin protocol compliance."""
    from .protocol import build_hook_response
    log_event(hook_name, payload, {"decision": "allow", "reason": f"governor_error: {error}"}, level="error")
    return build_hook_response(
        internal_decision="allow",
        reason=f"governor_error: {error}",
        hook_event_name=hook_name
    )
```

**Verification:**
- Hook dispatching for all 8 hooks
- Error handling with fail-open
- Protocol-compliant error responses
- Audit logging verification

---

#### Task 1.6: State Machine (state_machine.py) - ENHANCED
**Priority:** CRITICAL  
**Estimated Time:** 12 hours  
**Dependencies:** Tasks 1.1, 1.3

**Subtasks:**
- [ ] Create Governor/state_machine.py module
- [ ] Implement 6-phase state machine (INIT → RESEARCH → PLAN → EXECUTE → VALIDATE → COMMIT)
- [ ] Implement consolidated state.json (v1.3 single file)
- [ ] Add phase allowlist enforcement
- [ ] Implement counter tracking (PostToolUse only)
- [ ] Add flag tracking system
- [ ] Implement bypass registry (team + runtime)
- [ ] Add violation logging
- [ ] **IMPLEMENT fsync for crash-safety (MOVED from Phase 4)**
- [ ] **Implement state checksum sidecar (MOVED from Phase 4)**
- [ ] Test atomic write operations

**Implementation Requirements (ENHANCED):**
```python
# Atomic write with fsync (FOUNDATIONAL)
def save_state(self):
    temp_path = f"{self.state_path}.tmp"
    with open(temp_path, 'w') as f:
        json.dump(self.state, f)
        f.flush()
        os.fsync(f.fileno())
    os.replace(temp_path, self.state_path)
    
    # Checksum sidecar (FOUNDATIONAL)
    self.update_checksum()
```

**Verification:**
- Phase transitions work correctly
- State persistence across hook invocations
- Crash recovery testing
- Checksum validation
- Cross-platform file locking integration

---

#### Task 1.7: Audit Logging (audit/audit_log.py) - ENHANCED
**Priority:** HIGH  
**Estimated Time:** 6 hours  
**Dependencies:** Task 1.1

**Subtasks:**
- [ ] Create Governor/audit/audit_log.py module
- [ ] Implement hash-chained JSONL audit trail
- [ ] Add SHA-256 cryptographic linking
- [ ] Implement append-only file operations
- [ ] **Add trace_id correlation**
- [ ] **RECORD INTERNAL DECISION (allow/deny/modify/warn) not Devin protocol decision**
- [ ] Implement audit event validation

**Implementation Requirements (ENHANCED):**
```python
def log_event(hook_name, payload, response, level="info"):
    """Log event with hash chaining and internal decision."""
    prev_hash = get_last_hash()
    event = {
        "timestamp": datetime.utcnow().isoformat(),
        "hook_name": hook_name,
        "trace_id": current_trace_id,
        "prev_hash": prev_hash,
        "current_hash": compute_hash(event_data),  # FIXED: current_hash per spec §5.1
        "decision": response.get("governor_internal", {}).get("decision"),  # INTERNAL decision
        "level": level,
        "data": response
    }
    append_to_audit_log(event)
```

**Verification:**
- Hash chain integrity
- Tamper detection
- Trace_id correlation
- Internal decision recording

---

#### Task 1.8: Tool Name Normalization (tool_normalizer.py) - MOVED
**Priority:** HIGH  
**Estimated Time:** 3 hours  
**Dependencies:** Task 1.1

**Subtasks:**
- [ ] Create Governor/tool_normalizer.py module
- [ ] Implement Devin → canonical name mapping
- [ ] Add configurable alias system
- [ ] Create phase_patterns.yaml for test/git detection
- [ ] Test with common Devin tool names

**Implementation Requirements:**
```python
CANONICAL_TOOL_MAP = {
    "Read": "read",
    "Write": "file_write",
    "Edit": "file_edit",
    "Bash": "exec",
    "WebSearch": "web_search",
}
```

**Verification:**
- Tool name mapping accuracy
- Alias system functionality
- Phase pattern matching

---

#### Task 1.9: Rule Engine (engine.py) - MOVED
**Priority:** CRITICAL  
**Estimated Time:** 12 hours  
**Dependencies:** Tasks 1.1, 1.6, 1.8

**Subtasks:**
- [ ] Create Governor/engine.py module
- [ ] Implement rule directory scanning
- [ ] Add mtime-based caching
- [ ] Implement rule YAML parsing
- [ ] Add trigger matching logic
- [ ] Implement priority sorting (blocking → warning → observational)
- [ ] Add action instantiation via importlib
- [ ] Implement sequential action execution
- [ ] Add error handling with fail-graceful
- [ ] Implement rule aggregation logic

**Verification:**
- Rule loading accuracy
- Cache invalidation on file changes
- Priority sorting correctness
- Error handling verification

---

#### Task 1.10: Action Base Classes (actions/_base.py) - MOVED
**Priority:** CRITICAL  
**Estimated Time:** 4 hours  
**Dependencies:** Task 1.1

**Subtasks:**
- [ ] Create Governor/actions/_base.py module
- [ ] Implement RuleAction abstract base class
- [ ] Define ActionResult dataclass
- [ ] Add ActionContext dataclass
- [ ] Implement required parameter validation
- [ ] Add decision validation logic

**Implementation Requirements:**
```python
@dataclass
class ActionResult:
    decision: str  # "allow" | "deny" | "modify" | "warn"
    reason: str
    modified_payload: dict | None = None
    additional_context: str = ""
    bypass_key: str = ""

class RuleAction(ABC):
    @property
    @abstractmethod
    def name(self) -> str:
        pass
        
    @abstractmethod
    def get_required_params(self) -> list[str]:
        pass
        
    @abstractmethod
    def evaluate(self, payload, params, context) -> ActionResult:
        pass
```

**Verification:**
- Base class instantiation tests
- ActionResult validation
- Parameter validation logic

---

#### Task 1.11: Hook Handler Base Class (hook_handlers/_base.py) - MOVED
**Priority:** CRITICAL  
**Estimated Time:** 4 hours  
**Dependencies:** Tasks 1.1, 1.2, 1.10

**Subtasks:**
- [ ] Create Governor/hook_handlers/_base.py module
- [ ] Implement HookHandler abstract base class
- [ ] Define execute() method signature
- [ ] Add can_block() method
- [ ] Implement response building protocol
- [ ] Add state machine integration

**Verification:**
- Base class compliance
- Protocol response building
- State machine integration

---

### Phase 2: Core Hooks & Rules Tasks

#### Task 2.1: YAML Rule Validation (validators/yaml_validator.py)
**Priority:** HIGH  
**Estimated Time:** 6 hours  
**Dependencies:** Task 1.1

**Subtasks:**
- [ ] Create Governor/validators/yaml_validator.py
- [ ] Implement strictyaml integration (optional)
- [ ] Add stdlib YAML fallback
- [ ] Create rule schema validation
- [ ] Implement dangerous feature disabling
- [ ] Add type safety validation

**Verification:**
- YAML parsing accuracy
- Schema validation
- Dangerous feature blocking
- Fallback functionality

---

#### Task 2.2: JSON Schema Validation (validators/json_schema.py)
**Priority:** MEDIUM  
**Estimated Time:** 4 hours  
**Dependencies:** Task 1.1

**Subtasks:**
- [ ] Create Governor/validators/json_schema.py
- [ ] Implement JSON schema validation
- [ ] Add rule schema definition
- [ ] Implement validation error reporting

**Verification:**
- Schema validation accuracy
- Error reporting clarity

---

#### Task 2.3: SessionStart Handler
**Priority:** HIGH  
**Estimated Time:** 4 hours  
**Dependencies:** Tasks 1.5, 1.11, 1.9, 1.10

**Subtasks:**
- [ ] Create Governor/hook_handlers/session_start.py
- [ ] Implement phase initialization (INIT)
- [ ] Add constitution context injection
- [ ] Load past errors from flags
- [ ] Pre-populate bypasses from env var
- [ ] Reset counters to 0
- [ ] Implement protocol-compliant response

**Verification:**
- Session start correctness
- State initialization accuracy
- Context injection functional

---

#### Task 2.4: UserPromptSubmit Handler
**Priority:** HIGH  
**Estimated Time:** 6 hours  
**Dependencies:** Tasks 1.5, 1.11, 1.9, 1.10

**Subtasks:**
- [ ] Create Governor/hook_handlers/user_prompt_submit.py
- [ ] Implement intent detection (? vs task keywords)
- [ ] Add research worksheet enrichment
- [ ] Implement bypass command parsing
- [ ] Add mode detection (App vs Harness review)
- [ ] Implement flag setting (research_required)
- [ ] Create protocol-compliant response

**Verification:**
- Intent detection accuracy
- Bypass command parsing
- Mode detection reliability

---

#### Task 2.5: PreToolUse Handler (Primary Gate)
**Priority:** CRITICAL  
**Estimated Time:** 8 hours  
**Dependencies:** Tasks 1.5, 1.11, 1.9, 1.10, 1.8

**Subtasks:**
- [ ] Create Governor/hook_handlers/pre_tool_use.py
- [ ] Implement phase allowlist checking
- [ ] Add validation rule application
- [ ] Implement phase inference from tool usage
- [ ] Add bypass registry checking
- [ ] Implement tool input rewriting (updatedInput)
- [ ] Add block with bypass key generation
- [ ] Implement menu payload attachment (optional)
- [ ] Create protocol-compliant response

**Verification:**
- Phase enforcement accuracy
- Rule application correctness
- Bypass functionality
- Protocol compliance

---

#### Task 2.6: PostToolUse Handler
**Priority:** HIGH  
**Estimated Time:** 6 hours  
**Dependencies:** Tasks 1.5, 1.11, 1.9, 1.10

**Subtasks:**
- [ ] Create Governor/hook_handlers/post_tool_use.py
- [ ] Implement execution logging
- [ ] Add output validation
- [ ] Implement phase transition determination
- [ ] Add counter increment (successful execution only)
- [ ] Trigger auto-fix actions
- [ ] Create protocol-compliant response

**Verification:**
- Logging completeness
- Phase transition accuracy
- Counter correctness

---

#### Task 2.7: PermissionRequest Handler
**Priority:** MEDIUM  
**Estimated Time:** 4 hours  
**Dependencies:** Tasks 1.5, 1.11

**Subtasks:**
- [ ] Create Governor/hook_handlers/permission_request.py
- [ ] Implement auto-approve/deny logic
- [ ] Add escalation based on policy rules
- [ ] Implement permissionDecision field
- [ ] Create protocol-compliant response

**Verification:**
- Permission logic correctness
- Protocol compliance
- Policy rule application

---

#### Task 2.8: Stop Handler (Final Gate)
**Priority:** HIGH  
**Estimated Time:** 6 hours  
**Dependencies:** Tasks 1.5, 1.11, 1.9, 1.10

**Subtasks:**
- [ ] Create Governor/hook_handlers/stop.py
- [ ] Implement phase completion checking
- [ ] Add un-bypassed violation checking
- [ ] Implement minimum tool usage checking
- [ ] Add bypass validation
- [ ] Implement block with menu option
- [ ] Create protocol-compliant response

**Verification:**
- Completion checking accuracy
- Violation detection
- Bypass validation

---

#### Task 2.9: SessionEnd Handler
**Priority:** HIGH  
**Estimated Time:** 4 hours  
**Dependencies:** Tasks 1.5, 1.11, 1.7

**Subtasks:**
- [ ] Create Governor/hook_handlers/session_end.py
- [ ] Implement final logging
- [ ] Add compliance report generation
- [ ] Flush violations to audit trail
- [ ] Flush final counter values
- [ ] Archive state for post-mortem
- [ ] Create protocol-compliant response

**Verification:**
- Logging completeness
- Compliance report accuracy
- State archival

---

#### Task 2.10: PostCompaction Handler
**Priority:** MEDIUM  
**Estimated Time:** 4 hours  
**Dependencies:** Tasks 1.5, 1.11, 1.6

**Subtasks:**
- [ ] Create Governor/hook_handlers/post_compaction.py
- [ ] Implement phase state re-injection
- [ ] Add counter state re-injection
- [ ] Implement flag state re-injection
- [ ] Add bypass registry re-injection
- [ ] Implement state integrity verification
- [ ] Force phase reminder into context
- [ ] Create protocol-compliant response

**Verification:**
- State re-injection accuracy
- Integrity verification
- Context injection

---

### Phase 2.5: Sample Rules & Templates (NEW)

#### Task 2.11: Template System Implementation
**Priority:** HIGH  
**Estimated Time:** 6 hours  
**Dependencies:** Task 1.1

**Subtasks:**
- [ ] Create Governor/templates/ directory
- [ ] Implement templates/manifest.yaml
- [ ] Create sample template files (python_service.py.tpl, python_module.py.tpl)
- [ ] Implement template loading logic
- [ ] Add template manifest validation
- [ ] Create template usage documentation

**Verification:**
- Template loading functionality
- Manifest validation
- Template rendering accuracy

---

#### Task 2.12: Sample Actions Implementation
**Priority:** HIGH  
**Estimated Time:** 8 hours  
**Dependencies:** Task 1.10

**Subtasks:**
- [ ] Implement actions/block_command.py
- [ ] Implement actions/ghost_template.py
- [ ] Implement actions/present_bypass_menu.py
- [ ] Add action validation tests
- [ ] Create action usage documentation

**Verification:**
- Action functionality
- Integration with rule engine
- Documentation completeness

---

#### Task 2.13: Sample Rule YAMLs
**Priority:** HIGH  
**Estimated Time:** 4 hours  
**Dependencies:** Tasks 2.1, 2.12

**Subtasks:**
- [ ] Create sample rule: block_destructive_commands.yaml
- [ ] Create sample rule: enforce_architecture_patterns.yaml
- [ ] Create sample rule: require_review_checklist.yaml
- [ ] Validate rules against schema
- [ ] Create rule writing documentation

**Verification:**
- Rule validation passes
- Rules functional with engine
- Documentation completeness

---

#### Task 2.14: team_bypasses.json Initial File
**Priority:** MEDIUM  
**Estimated Time:** 2 hours  
**Dependencies:** Task 1.1

**Subtasks:**
- [ ] Create Governor/team_bypasses.json
- [ ] Add team bypass file documentation
- [ ] Define team bypass workflow
- [ ] Create bypass policy documentation

**Verification:**
- File structure correct
- Documentation complete

---

#### Task 2.15: Sample Components Integration Test (NEW)
**Priority:** MEDIUM  
**Estimated Time:** 4 hours  
**Dependencies:** Tasks 2.11, 2.12, 2.13

**Subtasks:**
- [ ] Create integration test for ghost_template action
- [ ] Create integration test for block_command action
- [ ] Create integration test for present_bypass_menu action
- [ ] Verify sample rules use descriptive snake_case IDs per §6.3
- [ ] Verify sample rules include aliases field where appropriate
- [ ] Verify sample rules use valid agent values (all, architect, planner, executor, reviewer)
- [ ] Test sample rules trigger correctly in PreToolUse
- [ ] End-to-end test of sample rules + actions + templates working together

**Verification:**
- All sample components functional
- Sample rules compliant with spec §6.3
- Integration test passes
- Documentation updated

---

### Phase 3: Framework Integration Tasks

#### Task 3.1: Agent-Specific Rule Filtering
**Priority:** HIGH  
**Estimated Time:** 6 hours  
**Dependencies:** Tasks 1.9, 2.1

**Subtasks:**
- [ ] Extend rule schema with agent field
- [ ] Implement agent detection from hook payload
- [ ] Add agent filtering logic in engine
- [ ] Create agent-specific rule templates
- [ ] Test with Architect, Planner, Executor, Reviewer

**Verification:**
- Agent detection accuracy
- Rule filtering correctness
- Multi-agent scenarios

---

#### Task 3.2: App vs Harness Path Scoping
**Priority:** HIGH  
**Estimated Time:** 8 hours  
**Dependencies:** Tasks 1.4, 2.1

**Subtasks:**
- [ ] Extend rule schema with scope field
- [ ] Implement path-based scope detection
- [ ] Create App path configuration
- [ ] Create Harness path configuration
- [ ] Add scope validation logic
- [ ] Implement cross-scope protection

**Verification:**
- Path scoping accuracy
- Cross-scope protection
- Configuration flexibility

---

#### Task 3.3: Context-Aware Reviewer Mode - ENHANCED
**Priority:** HIGH  
**Estimated Time:** 8 hours  
**Dependencies:** Tasks 2.4, 3.1, 3.2

**Subtasks:**
- [ ] Implement broader keyword set for mode detection
- [ ] Add command prefix support (mode:harness)
- [ ] Create mode-specific rule sets
- [ ] Implement mode switching logic
- [ ] Add mode persistence in state machine
- [ ] Create mode transition audit logging
- [ ] Document exact trigger phrases

**Implementation Requirements (ENHANCED):**
```python
# Enhanced mode detection with command prefix as primary
HARNESS_KEYWORDS = [
    "review harness", "audit governor", "check harness rules",
    "inspect harness", "harness review", "governor audit"
]

def detect_review_mode(user_prompt):
    """Detect harness review mode with command prefix as primary trigger."""
    prompt_lower = user_prompt.strip().lower()
    
    # Primary: explicit command prefix
    if prompt_lower.startswith("mode:harness"):
        return "harness"
    if prompt_lower.startswith("mode:app"):
        return "app"
    
    # Fallback: keyword detection (with deprecation warning)
    for keyword in HARNESS_KEYWORDS:
        if keyword in prompt_lower:
            logger.warning("mode_detected_via_keyword", 
                keyword=keyword, 
                message="Consider using mode:harness or mode:app for explicit mode control")
            return "harness"
    
    return "app"
```

**Verification:**
- Mode detection accuracy
- Mode switching reliability
- Audit trail completeness

---

#### Task 3.4: Framework-Specific Rule Templates
**Priority:** MEDIUM  
**Estimated Time:** 6 hours  
**Dependencies:** Tasks 3.1, 3.2, 3.3

**Subtasks:**
- [ ] Create Architect-specific rule templates
- [ ] Create Planner-specific rule templates
- [ ] Create Executor-specific rule templates
- [ ] Create Reviewer-specific rule templates (App mode)
- [ ] Create Reviewer-specific rule templates (Harness mode)
- [ ] Document template usage patterns

**Verification:**
- Template completeness
- Template accuracy
- Documentation clarity

---

#### Task 3.5: Framework Integration Testing
**Priority:** HIGH  
**Estimated Time:** 10 hours  
**Dependencies:** Tasks 3.1, 3.2, 3.3, 3.4

**Subtasks:**
- [ ] Create integration test suite
- [ ] Test Architect agent workflow
- [ ] Test Planner agent workflow
- [ ] Test Executor agent workflow
- [ ] Test Reviewer agent workflow (App mode)
- [ ] Test Reviewer agent workflow (Harness mode)
- [ ] Test agent switching scenarios
- [ ] Test mode switching scenarios

**Verification:**
- All agent workflows functional
- Mode switching reliable
- No cross-agent interference
- Performance acceptable

---

### Phase 4: Advanced Features Tasks

#### Task 4.1: Per-Layer Debug Logging
**Priority:** MEDIUM  
**Estimated Time:** 6 hours  
**Dependencies:** Task 1.5

**Subtasks:**
- [ ] Implement GOVERNOR_DEBUG_ENGINE env var
- [ ] Implement GOVERNOR_DEBUG_STATE_MACHINE env var
- [ ] Implement GOVERNOR_DEBUG_HOOK_HANDLERS env var
- [ ] Implement GOVERNOR_DEBUG_ACTIONS env var
- [ ] Implement GOVERNOR_DEBUG_AUDIT env var
- [ ] Add debug log formatting
- [ ] Create debug logging documentation

**Implementation Requirements:**
```python
DEBUG_LEVELS = {
    "GOVERNOR_DEBUG_ENGINE": "engine",
    "GOVERNOR_DEBUG_STATE_MACHINE": "state_machine",
    "GOVERNOR_DEBUG_HOOK_HANDLERS": "hook_handlers",
    "GOVERNOR_DEBUG_ACTIONS": "actions",
    "GOVERNOR_DEBUG_AUDIT": "audit"
}
```

**Verification:**
- Environment variable parsing
- Debug output completeness
- Performance impact acceptable

---

#### Task 4.2: Execution Tracing with trace_id
**Priority:** HIGH  
**Estimated Time:** 6 hours  
**Dependencies:** Task 1.7

**Subtasks:**
- [ ] Implement UUID4 trace_id generation
- [ ] Add trace_id propagation through all components
- [ ] Implement trace_id in audit logging
- [ ] Add trace_id in debug logs
- [ ] Create trace_id correlation tools
- [ ] Implement trace_id in state inspection CLI

**Implementation Requirements:**
```python
import uuid
trace_id = str(uuid.uuid4())
# Propagate through all log entries and audit events
```

**Verification:**
- Trace_id uniqueness
- Trace_id propagation completeness
- Correlation tool accuracy

---

#### Task 4.3: State Inspection CLI
**Priority:** MEDIUM  
**Estimated Time:** 8 hours  
**Dependencies:** Tasks 1.6, 4.2

**Subtasks:**
- [ ] Create Governor/debug/__init__.py
- [ ] Implement inspect-state command
- [ ] Implement trace-rule command
- [ ] Implement trace-bypass command
- [ ] Implement replay-hook command
- [ ] Add CLI argument parsing
- [ ] Create output formatting

**Implementation Requirements:**
```bash
python -m Governor.debug inspect-state
python -m Governor.debug trace-rule block_destructive_commands
python -m Governor.debug trace-bypass block_destructive_commands
python -m Governor.debug replay-hook PreToolUse
```

**Verification:**
- CLI functionality
- Output accuracy
- Error handling

---

#### Task 4.4: Circuit Breaker Pattern - FULL SPEC IMPLEMENTATION
**Priority:** MEDIUM  
**Estimated Time:** 8 hours  
**Dependencies:** Task 1.9

**Subtasks:**
- [ ] Implement circuit breaker state machine per v1.5 spec §12.7
- [ ] Add per-action state tracking
- [ ] Implement failure windowing (deque with maxlen)
- [ ] Add half-open state
- [ ] Implement thread safety (Lock)
- [ ] Add allow() method
- [ ] Add record_success() method
- [ ] Add record_failure() method
- [ ] Implement status() for CLI inspection
- [ ] Create circuit breaker tests

**Implementation Requirements (FULL SPEC):**
```python
from collections import deque
from threading import Lock
import os
import time

HALF_OPEN_TIMEOUT_S = 30

class CircuitBreakerManager:
    """Per-action circuit breaker tracking per v1.5 spec §12.7."""
    
    def __init__(self):
        self.breakers = {}  # (action_name, rule_id) -> CircuitBreaker
        self.lock = Lock()
        self.threshold = int(os.getenv("GOVERNOR_CIRCUIT_BREAKER_THRESHOLD", "3"))
        self.open_timeout_s = int(os.getenv("GOVERNOR_CIRCUIT_BREAKER_OPEN_S", "300"))
        
    def allow(self, action_name: str, rule_id: str) -> tuple[bool, str]:
        """Check if action is allowed, return (allowed, reason)."""
        key = (action_name, rule_id)
        with self.lock:
            if key not in self.breakers:
                self.breakers[key] = CircuitBreaker(self.threshold, self.open_timeout_s)
            return self.breakers[key].allow()
            
    def record_success(self, action_name: str, rule_id: str):
        key = (action_name, rule_id)
        with self.lock:
            if key in self.breakers:
                self.breakers[key].record_success()
                
    def record_failure(self, action_name: str, rule_id: str):
        key = (action_name, rule_id)
        with self.lock:
            if key not in self.breakers:
                self.breakers[key] = CircuitBreaker(self.threshold, self.open_timeout_s)
            self.breakers[key].record_failure()
            
    def status(self) -> dict:
        """Return status of all circuit breakers for CLI inspection."""
        with self.lock:
            return {
                key: breaker.status()
                for key, breaker in self.breakers.items()
            }

class CircuitBreaker:
    def __init__(self, failure_threshold: int, open_timeout_s: int):
        self.failure_threshold = failure_threshold
        self.open_timeout_s = open_timeout_s
        self.failures = deque(maxlen=10)  # Spec: maxlen=10
        self.state = "closed"
        self.last_failure_time = None
        self.half_open_since = None
        self.lock = Lock()
        
    def allow(self) -> tuple[bool, str]:
        """Check if action is allowed, return (allowed, reason)."""
        with self.lock:
            if self.state == "open":
                if time.time() - self.last_failure_time > self.open_timeout_s:
                    self.state = "half_open"
                    self.half_open_since = time.time()
                    return True, "circuit_breaker_half_open"
                return False, "circuit_breaker_open"
            elif self.state == "half_open":
                if time.time() - self.half_open_since > HALF_OPEN_TIMEOUT_S:
                    self.state = "open"
                    self.last_failure_time = time.time()
                    return False, "circuit_breaker_half_open_timeout"
                return True, "circuit_breaker_half_open_test"
            return True, "circuit_breaker_closed"
            
    def record_success(self):
        with self.lock:
            if self.state == "half_open":
                self.state = "closed"
                self.failures.clear()
                self.half_open_since = None
                
    def record_failure(self):
        with self.lock:
            # Filter failures outside window
            now = time.time()
            window = 60  # Spec: 60 second window
            self.failures = deque([f for f in self.failures if now - f < window], maxlen=10)
            self.failures.append(now)
            
            if self.state == "half_open":
                # Reopen on half-open failure
                self.state = "open"
                self.last_failure_time = now
                self.half_open_since = None
            elif len(self.failures) >= self.failure_threshold:
                self.state = "open"
                self.last_failure_time = now
                
    def status(self) -> dict:
        with self.lock:
            return {
                "state": self.state,
                "failures": len(self.failures),
                "last_failure_time": self.last_failure_time,
                "half_open_since": self.half_open_since
            }
```

**Verification:**
- Circuit breaker logic correctness
- Threshold detection accuracy
- Recovery timing accuracy
- Thread safety verification

---

#### Task 4.5: Action Result Memoization - SPEC COMPLIANT
**Priority:** LOW  
**Estimated Time:** 4 hours  
**Dependencies:** Task 1.10

**Subtasks:**
- [ ] Implement @memoize_result decorator per v1.5 spec §12.8
- [ ] Add TTL configuration (60 seconds default)
- [ ] Implement cache key generation with (self.name, context.tool_name, payload_hash)
- [ ] Add cache invalidation logic
- [ ] Create memoization statistics

**Implementation Requirements (SPEC COMPLIANT):**
```python
def memoize_result(ttl_seconds=60):
    def decorator(func):
        cache = {}
        def wrapper(self, payload, params, context):
            # Use spec's key generation
            import hashlib
            payload_hash = hashlib.sha256(str(payload).encode()).hexdigest()
            key = (self.name, context.tool_name, payload_hash)
            
            if key in cache and time.time() - cache[key]['time'] < ttl_seconds:
                return cache[key]['result']
            result = func(self, payload, params, context)
            cache[key] = {'result': result, 'time': time.time()}
            return result
        return wrapper
    return decorator
```

**Verification:**
- Memoization correctness
- TTL accuracy
- Cache invalidation

---

#### Task 4.6: Structured Logging (Optional)
**Priority:** LOW  
**Estimated Time:** 4 hours  
**Dependencies:** Task 4.1

**Subtasks:**
- [ ] Implement structlog integration (optional)
- [ ] Add JSON-formatted log output
- [ ] Implement trace_id field
- [ ] Add rule_id field
- [ ] Add hook_name field
- [ ] Add duration_ms field
- [ ] Create stdlib fallback

**Implementation Requirements:**
```python
try:
    import structlog
    USE_STRUCTLOG = True
except ImportError:
    USE_STRUCTLOG = False
    # Use stdlib logging
```

**Verification:**
- Structured logging accuracy
- Fallback functionality
- Performance impact

---

### Phase 5: Security & Hardening Tasks (v1.5 Spec Features)

#### Task 5.1: Harness File Protection (v1.5 spec §6.4)
**Priority:** HIGH  
**Estimated Time:** 8 hours  
**Dependencies:** Tasks 1.4, 3.2

**Subtasks:**
- [ ] Implement Governor path protection per v1.5 spec §6.4
- [ ] Add .devin path protection per spec
- [ ] Implement Rules path protection per spec
- [ ] Add path traversal protection (safe_join)
- [ ] Implement symlink validation per spec
- [ ] Add file permission checks per spec
- [ ] Create protection violation logging

**Verification:**
- Path protection effectiveness
- Symlink validation
- Permission checking
- Security threat model compliance

---

#### Task 5.2: Team-Level Bypass Enforcement (v1.5 spec)
**Priority:** HIGH  
**Estimated Time:** 6 hours  
**Dependencies:** Tasks 1.6, 5.1

**Subtasks:**
- [ ] Implement team_bypass validation per v1.5 spec
- [ ] Add bypass scope enforcement per spec
- [ ] Implement bypass source tracking per spec
- [ ] Create team bypass approval workflow
- [ ] Add bypass expiration logic per spec
- [ ] Implement bypass audit trail per spec

**Verification:**
- Team bypass enforcement
- Source validation
- Audit trail completeness

---

#### Task 5.3: Security Threat Model Implementation (v1.5 spec §6.4)
**Priority:** HIGH  
**Estimated Time:** 8 hours  
**Dependencies:** Tasks 5.1, 5.2

**Subtasks:**
- [ ] Implement path traversal protection per v1.5 spec
- [ ] Add symlink validation per v1.5 spec
- [ ] Implement file permission checks per v1.5 spec
- [ ] Add resource limits for actions per v1.5 spec
- [ ] Create security audit logging per v1.5 spec
- [ ] Implement security violation response per v1.5 spec

**Verification:**
- Security measure effectiveness
- Attack prevention
- Response appropriateness

---

#### Task 5.4: Penetration Testing (Smoke-Test Level)
**Priority:** HIGH  
**Estimated Time:** 12 hours  
**Dependencies:** All previous tasks

**Subtasks:**
- [ ] Design penetration test scenarios
- [ ] Test path traversal attacks
- [ ] Test bypass system abuse
- [ ] Test audit log tampering
- [ ] Test privilege escalation
- [ ] Test race conditions
- [ ] Test resource exhaustion
- [ ] Document vulnerabilities found
- [ ] Implement fixes for discovered issues

**Note:** This is smoke-test-level security validation, not full red-team engagement. Full penetration testing would require 1-2 weeks with specialized security team.

**Verification:**
- All attacks prevented or detected
- No security bypasses found
- Audit trail integrity maintained

---

### Phase 6: Validation Tasks (NEW)

#### Task 6.1: Stage 9 - Cross-Platform Validation
**Priority:** HIGH  
**Estimated Time:** 8 hours  
**Dependencies:** All previous phases

**Subtasks:**
- [ ] Test on Windows (primary platform)
- [ ] Test on Linux (if available)
- [ ] Test on macOS (if available)
- [ ] Verify file locking on all platforms
- [ ] Verify path handling on all platforms
- [ ] Create cross-platform compatibility report

**Verification:**
- All platforms functional
- Cross-platform consistency verified
- Platform-specific issues documented

---

#### Task 6.2: Stage 11 - Debugging Infrastructure Validation
**Priority:** MEDIUM  
**Estimated Time:** 6 hours  
**Dependencies:** Phase 4 tasks

**Subtasks:**
- [ ] Verify per-layer debug logging functionality
- [ ] Test trace_id correlation across components
- [ ] Verify state inspection CLI tools
- [ ] Test debug log output completeness
- [ ] Create debugging functionality report

**Verification:**
- Debug features functional
- Trace correlation working
- CLI tools operational

---

#### Task 6.3: Stage 12 - Protocol Alignment Validation
**Priority:** CRITICAL  
**Estimated Time:** 6 hours  
**Dependencies:** Phase 1 tasks

**Subtasks:**
- [ ] Verify two-tier decision model implementation
- [ ] Test Devin CLI protocol compliance
- [ ] Verify governor_internal placement at top level
- [ ] Test decision mapping accuracy
- [ ] Create protocol alignment report

**Verification:**
- Protocol compliance verified
- Decision mapping correct
- Audit field placement correct

---

### Phase 7: Integration & CI Tasks (NEW)

#### Task 7.1: .devin/hooks.v1.json Configuration
**Priority:** CRITICAL  
**Estimated Time:** 4 hours  
**Dependencies:** Phase 2 tasks

**Subtasks:**
- [ ] Create .devin/hooks.v1.json file
- [ ] Configure all 8 hook commands
- [ ] Test hook invocation
- [ ] Create hook configuration documentation

**Implementation Requirements (FIXED with timeouts and matchers per spec):**
```json
{
  "SessionStart": [
    {
      "matcher": "",
      "hooks": [
        {
          "type": "command",
          "command": "python3 Governor/governor.py SessionStart",
          "timeout": 10
        }
      ]
    }
  ],
  "UserPromptSubmit": [
    {
      "matcher": "",
      "hooks": [
        {
          "type": "command",
          "command": "python3 Governor/governor.py UserPromptSubmit",
          "timeout": 5
        }
      ]
    }
  ],
  "PreToolUse": [
    {
      "matcher": "Bash|Write|Edit",
      "hooks": [
        {
          "type": "command",
          "command": "python3 Governor/governor.py PreToolUse",
          "timeout": 10
        }
      ]
    }
  ],
  "PostToolUse": [
    {
      "matcher": "Bash|Write|Edit",
      "hooks": [
        {
          "type": "command",
          "command": "python3 Governor/governor.py PostToolUse",
          "timeout": 10
        }
      ]
    }
  ],
  "PermissionRequest": [
    {
      "matcher": "",
      "hooks": [
        {
          "type": "command",
          "command": "python3 Governor/governor.py PermissionRequest",
          "timeout": 5
        }
      ]
    }
  ],
  "Stop": [
    {
      "matcher": "",
      "hooks": [
        {
          "type": "command",
          "command": "python3 Governor/governor.py Stop",
          "timeout": 5
        }
      ]
    }
  ],
  "SessionEnd": [
    {
      "matcher": "",
      "hooks": [
        {
          "type": "command",
          "command": "python3 Governor/governor.py SessionEnd",
          "timeout": 5
        }
      ]
    }
  ],
  "PostCompaction": [
    {
      "matcher": "",
      "hooks": [
        {
          "type": "command",
          "command": "python3 Governor/governor.py PostCompaction",
          "timeout": 5
        }
      ]
    }
  ]
}
```

**Verification:**
- Hook configuration valid
- Devin CLI can invoke Governor
- All hooks functional

---

#### Task 7.2: pyproject.toml Full Content
**Priority:** MEDIUM  
**Estimated Time:** 4 hours  
**Dependencies:** Task 1.1

**Subtasks:**
- [ ] Complete pyproject.toml with dependency groups per v1.5 spec Appendix O
- [ ] Define [all] extra with all optional dependencies
- [ ] Define [basic] extra with stdlib only
- [ ] Add development dependencies
- [ ] Add testing dependencies
- [ ] Create dependency documentation

**Implementation Requirements (FIXED per spec Appendix O):**
```toml
[project]
name = "governor"
version = "1.5.0"
requires-python = ">=3.10"
dependencies = [
    "pyyaml>=6.0"  # Required for basic mode
]

[project.optional-dependencies]
locking = ["portalocker>=2.0.0"]
yaml = ["strictyaml>=1.0.0"]
validation = ["pydantic>=2.0.0"]
logging = ["structlog>=23.0.0"]
debugging = ["portalocker>=2.0.0", "structlog>=23.0.0"]
all = [
    "portalocker>=2.0.0",
    "strictyaml>=1.0.0",
    "pydantic>=2.0.0",
    "structlog>=23.0.0"
]

[build-system]
requires = ["setuptools>=61.0"]
build-backend = "setuptools.build_meta"
```

**Verification:**
- Dependency groups functional
- Installation works correctly
- Documentation complete

---

#### Task 7.3: CI/CD Pipeline Setup
**Priority:** MEDIUM  
**Estimated Time:** 8 hours  
**Dependencies:** All previous phases

**Subtasks:**
- [ ] Create CI pipeline configuration
- [ ] Add cross-platform testing automation
- [ ] Implement automated security scanning
- [ ] Add automated testing in CI
- [ ] Create deployment automation
- [ ] Setup CI notification systems

**Verification:**
- CI pipeline functional
- Cross-platform tests automated
- Security scanning integrated
- Deployment automation working

---

## Testing Strategy

### Unit Testing
**Coverage Goal:** 80%+  
**Framework:** pytest

**Test Categories:**
- Protocol mapping tests
- File locking tests
- Path normalization tests
- State machine tests
- Rule engine tests
- Action tests
- Hook handler tests

### Integration Testing
**Flow Coverage Goal:** All critical paths  
**Framework:** pytest + Devin CLI mock

**Test Scenarios:**
- Full hook lifecycle
- Agent-specific workflows
- Mode switching scenarios
- Error handling paths
- Bypass functionality

### End-to-End Testing
**Coverage Goal:** Critical user journeys  
**Framework:** Manual testing with real Devin CLI

**Test Scenarios:**
- Architect agent workflow
- Planner agent workflow
- Executor agent workflow
- Reviewer agent workflow (App mode)
- Reviewer agent workflow (Harness mode)
- Cross-platform testing (Windows primary)

### Security Testing
**Scenario Coverage Goal:** 100% of threat model addressed  
**Framework:** Custom security tests

**Test Scenarios:**
- Path traversal attacks
- Bypass system abuse
- Audit log tampering
- Privilege escalation
- Race conditions
- Resource exhaustion

---

## Risk Mitigation

### Technical Risks

| Risk | Probability | Impact | Mitigation |
|------|-------------|---------|------------|
| Devin CLI protocol changes | Medium | High | Protocol isolation layer |
| File locking issues on Windows | Low | High | Multi-backend fallback |
| Performance degradation | Medium | Medium | Performance budget + monitoring |
| State corruption | Low | High | Atomic writes + checksums |
| Agent detection failures | Medium | Medium | Conservative fallbacks |

### Integration Risks

| Risk | Probability | Impact | Mitigation |
|------|-------------|---------|------------|
| Framework incompatibility | Low | High | Early integration testing |
| Mode switching failures | Medium | Medium | Extensive testing + fallbacks |
| Rule conflicts | Medium | Medium | Rule priority system |
| Bypass abuse | Medium | High | Team-level enforcement |

### Security Risks

| Risk | Probability | Impact | Mitigation |
|------|-------------|---------|------------|
| Harness tampering | Low | Critical | Enhanced protection + auditing |
| Privilege escalation | Low | Critical | Security threat model |
| Audit log tampering | Low | High | Hash chaining + verification |
| Bypass system abuse | Medium | High | Team-level enforcement |

---

## Success Metrics

### Functional Metrics
- [ ] All 8 hooks implemented and functional
- [ ] Two-tier decision model working correctly
- [ ] Framework integration with all agents
- [ ] Dual-mode Reviewer functional
- [ ] Cross-platform compatibility verified

### Quality Metrics
- [ ] Unit test coverage ≥ 80%
- [ ] Integration test flow coverage: all critical paths
- [ ] Security test scenarios: 100% of threat model addressed
- [ ] Zero critical bugs in production
- [ ] Performance within budget (hook timeout)

### Security Metrics
- [ ] All threat model scenarios addressed
- [ ] Penetration testing passed (smoke-test level)
- [ ] Audit trail integrity verified
- [ ] No privilege escalation paths
- [ ] Harness protection effective

---

## Rollout Plan (Restructured)

### Phase Mapping

| Rollout Phase | Implementation Phases | Duration | Participants |
|---------------|---------------------|----------|-------------|
| Alpha | Phases 1-2 (Foundation + Core Hooks) | 2 weeks | Development team |
| Beta | Phase 3 (Framework Integration) | 1 week | Development + QA team |
| Gamma | Phase 5 (Security & Hardening) | 1 week | Development + Security team |
| Delta | Phase 4 (Advanced) + Phase 6 (Validation) + Phase 7 (Integration) | 1-2 weeks | Full team |

### Phase 1: Alpha (Internal Testing)
**Duration:** 2 weeks  
**Scope:** Foundation + Core Hooks  
**Participants:** Development team  
**Success Criteria:** Basic hook functionality working

### Phase 2: Beta (Framework Integration)
**Duration:** 1 week  
**Scope:** Framework integration  
**Participants:** Development + QA team  
**Success Criteria:** All agent workflows functional

### Phase 3: Gamma (Security Hardening)
**Duration:** 1 week  
**Scope:** Security features and smoke-test pen testing  
**Participants:** Development + Security team  
**Success Criteria:** Security testing passed

### Phase 4: Delta (Production Readiness)
**Duration:** 1-2 weeks  
**Scope:** Advanced features + validation + CI setup  
**Participants:** Full team  
**Success Criteria:** Production-ready deployment

---

## Dependencies

### External Dependencies
- Python 3.10+
- Devin CLI (latest stable)
- Git (for team_bypasses.json versioning)

### Optional Dependencies
- portalocker (for enhanced file locking)
- strictyaml (for YAML security)
- Pydantic (for type validation)
- structlog (for structured logging)

### Internal Dependencies
- Existing Architect > Planner > Executor > Reviewer framework
- Devin CLI hooks configuration (.devin/hooks.v1.json)
- Team development workflow

---

## Documentation Requirements

### Technical Documentation
- [ ] API documentation for all modules
- [ ] Architecture diagrams
- [ ] Protocol specification documentation
- [ ] Security model documentation
- [ ] Performance characteristics

### User Documentation
- [ ] Installation guide
- [ ] Configuration guide
- [ ] Rule writing guide
- [ ] Troubleshooting guide
- [ ] Framework integration guide

### Operational Documentation
- [ ] Deployment guide
- [ ] Monitoring guide
- [ ] Incident response procedures
- [ ] Backup and recovery procedures
- [ ] Performance tuning guide

---

## Review Points for External AI

### Architecture Review
1. **Two-tier decision model**: Is the FIXED protocol isolation approach sound?
2. **Framework integration**: Does the restructured phase ordering make sense?
3. **Dual-mode Reviewer**: Is the enhanced mode detection robust?
4. **App vs Harness scoping**: Is the path-based scoping maintainable?

### Security Review
1. **Harness protection**: Are the v1.5 spec security measures sufficient?
2. **Bypass system**: Is the team-level enforcement appropriate?
3. **Audit logging**: Is the enhanced internal decision recording comprehensive?
4. **Threat model**: Are all v1.5 spec security considerations addressed?

### Implementation Review
1. **Task breakdown**: Are the restructured tasks appropriately sized and ordered?
2. **Dependencies**: Are the FIXED dependencies accurate and complete?
3. **Testing strategy**: Is the enhanced testing approach comprehensive?
4. **Risk mitigation**: Are the identified risks properly mitigated?

### Timeline Review
1. **Duration estimates**: Are the time estimates realistic for 2-3 person team?
2. **Phase sequencing**: Is the restructured phase order logical?
3. **Milestones**: Are the success criteria appropriate?
4. **Rollout plan**: Is the mapped rollout strategy sound?

---

## Appendix A: v1.1 Revision Log

### Critical Fixes
- ✅ Fixed build_hook_response() governor_internal placement (moved to top level)
- ✅ Added Task 1.9 (engine) dependency to all hook handler tasks
- ✅ Moved Tasks 1.8-1.11 (foundational modules) to Phase 1
- ✅ Moved fsync + checksums to Task 1.6 (state_machine.py)
- ✅ Restructured phases: hook handlers now in Phase 2 (not Phase 6)

### High-Priority Additions
- ✅ Added Phase 2.5: Sample Rules & Templates
- ✅ Added Phase 7: Integration & CI
- ✅ Added missing spec components (templates, actions, .devin/hooks.v1.json, team_bypasses.json, pyproject.toml)
- ✅ Aligned memoization with v1.5 spec (payload-hashed keys)
- ✅ Aligned circuit breaker with v1.5 spec (full implementation)
- ✅ Added internal decision recording to audit logging
- ✅ Enhanced harness review mode detection (broader keywords + command prefix)

### Medium-Priority Improvements
- ✅ Clarified Phase 5 as implementing existing v1.5 spec features
- ✅ Fixed coverage metrics (flow coverage vs test coverage)
- ✅ Added team-size assumption (2-3 developers)
- ✅ Added rollout phase mapping table
- ✅ Added Phase 6: Validation with spec-defined stages

---

## Appendix B: Devin CLI Hook Protocol Reference

### Standard Hook Response Format
```json
{
  "decision": "approve" | "block",
  "governor_internal": {
    "decision": "allow" | "deny" | "modify" | "warn"
  },
  "reason": "Human-readable explanation",
  "hookSpecificOutput": {
    "hookEventName": "SessionStart" | "UserPromptSubmit" | "PreToolUse" | "PostToolUse" | "PermissionRequest" | "Stop" | "SessionEnd" | "PostCompaction",
    "additionalContext": "Optional context injection",
    "updatedInput": {"tool": "arguments"},
    "permissionDecision": "approve" | "deny" | "ask"
  }
}
```

### Internal Decision Mapping
```python
Internal → Devin Protocol
"allow" → "approve"
"modify" → "approve"  
"warn" → "approve"
"deny" → "block"
```

---

## Appendix C: Framework Integration Examples

### Architect Agent Rules
```yaml
id: architect_enforce_design_patterns
agent: architect
scope: app
tier: blocking
triggers:
  - PreToolUse
check:
  params:
    file_pattern: "**/*.py"
    actions:
      - name: ghost_template
        template: python_service.py.tpl
```

### Reviewer Harness Mode Rules
```yaml
id: reviewer_harness_audit
agent: reviewer
scope: harness
tier: blocking
triggers:
  - PreToolUse
check:
  params:
    activation_mode: harness_review
    actions:
      - name: require_team_approval
        audit_level: critical
```

---

## Appendix D: Security Considerations

### Protection Zones
1. **App Zone**: Standard development rules apply
2. **Harness Zone**: Enhanced protection with team approval
3. **Cross-Zone**: Special handling for zone transitions

### Approval Chains
1. **App Changes**: Standard bypass system
2. **Harness Changes**: Team-level approval required
3. **Emergency Changes**: Multi-approval + enhanced audit

### Audit Requirements
1. **App Changes**: Standard audit logging
2. **Harness Changes**: Enhanced audit with before/after states
3. **Emergency Changes**: Real-time monitoring + alerting

---

**Document Status:** v1.1 - Ready for Execution  
**Last Updated:** 2026-08-05  
**Next Review:** After Phase 1 completion