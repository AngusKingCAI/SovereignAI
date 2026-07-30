---
id: wf-arch-agents-validation
status: active
owner: architect-agent
updated: 2026-07-29
version: "2.1"
purpose: Architect workflow for comprehensive validation of AGENTS.md files
expected_agent_type: architect-agent
persona:
  role: "AGENTS.md Validation Architect"
  expertise: "AGENTS.md structure validation, command verification, boundary checking, reference integrity, token efficiency, progressive disclosure validation"
  process: "Interactive phase-by-phase validation with stop-and-fix approach, web search integration, fact checking, and reference integrity verification"
  output: "Real-time inconsistency identification with specific fix suggestions and immediate user collaboration"
  constraints: "Interactive validation with user approval required for modifications, SSOT compliance enforcement"
---

# Architect AGENTS.md Validation Workflow

**ID**: WF-ARCH-AGENTS-VALIDATION  
**Owner**: Architect Agent  
**Frequency**: Per AGENTS.md validation task  
**Duration**: Variable (document-dependent)  
**Priority**: High
**Workflow Type**: Single-Execution (systematic validation process)
**Execution Modes**: Manual, Automatic
**Phase Structure**: Modular phases following AGENTS.md best practices

## Purpose
Comprehensive validation of AGENTS.md files to ensure they meet industry best practices, maintain proper structure, contain executable commands, define clear boundaries, and follow KISS principles. This workflow validates AGENTS.md as a repository instruction file for AI coding agents, ensuring it provides high-signal, actionable guidance without unnecessary complexity.

## Reference Documents
- **Universal Framework References**: Workflow/Workflow_Reference/ (referenced frameworks based on workflow relevance)
- **Agent Rules**: Rules/Architect/Architect_Rules.md (Architect-specific governance rules)
- **Terminology**: Workflow/Workflow_Reference/Terminology_Glossary.md (SSOT for governance terminology)
- **Execution Mode Patterns**: Workflow/Workflow_Reference/Execution_Mode_Patterns.md (execution mode definitions and handling)
- **Validation Enforcement**: Workflow/Workflow_Reference/Validation_Enforcement_Patterns.md (universal validation patterns)
- **Best Practice Integration**: Web search points (BP?) for current AGENTS.md best practices
- **Fact Check Integration**: Fact checking points (FC?) for factual accuracy verification
- **AGENTS.md Spec**: agents.md (AAIF-stewarded AGENTS.md convention)

## Roles and Owners
- **Architect Agent**: Executes Architect AGENTS.md validation workflow, applies Validation Architect persona
- **Validation Architect Persona**: Session-scoped persona for AGENTS.md validation tasks

## Trigger and End State
- **Trigger**: User requests AGENTS.md validation or Architect initiates AGENTS.md review
- **End State**: AGENTS.md validated with all inconsistencies fixed interactively during validation process

## Workflow Steps

### Load Governance Rules
- **OPEN** WorkflowOpen skill to dynamically load agent-specific rules based on current agent type
- **STATUS TRACKING**: Update workflow status to "governance_rules_loaded"
- **PRINT** "Governance rules loaded dynamically based on agent type"

### Select Execution Mode
- Ask user to select execution mode for this workflow using popup menu:
  - **Manual**: Stop at each inconsistency for user oversight
  - **Automatic**: Process automatically until failure, then ask user
- Store selected execution mode for failure handling throughout workflow
- **STATUS TRACKING**: Update workflow status to "execution_mode_selected"
- **PRINT** "Execution mode selected - [Manual/Automatic] will govern failure handling"

### Phase 0. Persona Validation and Workflow Initialization
**Best Practice**: Persona validation - ensure persona is properly configured for AGENTS.md validation

- 0.1. **STATUS TRACKING**: Update workflow status to "phase_0_in_progress"
- 0.2. **ACTION**: BP? - "persona validation and AGENTS.md workflow initialization best practices"
- 0.3. **ACTION**: FC? - "persona structure accuracy and factual correctness verification"
- 0.4. **VALIDATE PERSONA**: Verify expected_agent_type matches current agent (architect-agent)
- 0.5. **LOAD PERSONA**: Load Validation Architect persona from workflow YAML frontmatter
- 0.6. **VALIDATE PERSONA STRUCTURE**: Ensure persona contains required elements (role, expertise, process, output, constraints)
- 0.7. **VALIDATE PERSONA-SCOPE ALIGNMENT**: Ensure persona expertise aligns with AGENTS.md validation (not workflow validation)
- 0.8. **PRINT**: "AGENTS.md Validation Architect persona loaded - ready for AGENTS.md validation"
- 0.9. **VALIDATION**: Validate that persona loading completed successfully before proceeding to Phase 1
- 0.10. **STATUS TRACKING**: Update workflow status to "phase_0_complete"

### Phase 1. Document Header Analysis
**Best Practice**: Document control standards - verify metadata accuracy and frontmatter handling

- 1.1. **STATUS TRACKING**: Update workflow status to "phase_1_in_progress"
- 1.2. **ACTION**: BP? - "AGENTS.md header analysis and metadata validation best practices"
- 1.3. **ACTION**: FC? - "AGENTS.md header accuracy and factual correctness verification"
- 1.4. **ACTION**: Read AGENTS.md YAML frontmatter (if present)
- 1.5. **CHECK**: Frontmatter is OPTIONAL - handle frontmatter-free case correctly (AGENTS.md is plain Markdown)
- 1.6. **CHECK**: If frontmatter present, validate against MDA AGENTS.md schema (name, description, license, compatibility, metadata, integrity, signatures)
- 1.7. **CHECK**: Atemporal language detection - no temporal references (dates, "currently", "now") in header
- 1.8. **CHECK**: Anti-pattern detection - no role-play preambles, vague instructions, contradictions, TODOs
- 1.9. **CHECK**: Context budget validation - header doesn't exceed token limits
- 1.10. **IF INCONSISTENCY FOUND**: STOP - Report inconsistency with specific location and suggested fix
- 1.11. **AWAIT USER APPROVAL**: Wait for user to approve fix before proceeding
- 1.12. **VALIDATION**: Validate that header analysis completed successfully
- 1.13. **STATUS TRACKING**: Update workflow status to "phase_1_complete"

### Phase 2. Structure and Organization Validation
**Best Practice**: Document structure - ensure AGENTS.md follows recommended sections and organization

- 2.1. **STATUS TRACKING**: Update workflow status to "phase_2_in_progress"
- 2.2. **ACTION**: BP? - "AGENTS.md structure and organization best practices"
- 2.3. **ACTION**: FC? - "AGENTS.md structure accuracy and factual correctness verification"
- 2.4. **ACTION**: Read AGENTS.md structure and organization
- 2.5. **CHECK**: Structure follows popular/recommended sections pattern (Project, Stack, Architecture, Conventions, Testing, Deployment, Gotchas)
- 2.6. **CHECK**: Sections flow logically and are well-organized
- 2.7. **CHECK**: Three-tier boundaries pattern present (Always do / Ask first / Never do)
- 2.8. **CHECK**: Commands are executable with flags, not just tool names
- 2.9. **CHECK**: Section completeness matches project needs
- 2.10. **IF INCONSISTENCY FOUND**: STOP - Report inconsistency with specific location and suggested fix
- 2.11. **AWAIT USER APPROVAL**: Wait for user to approve fix before proceeding
- 2.12. **VALIDATION**: Validate that structure validation completed successfully
- 2.13. **STATUS TRACKING**: Update workflow status to "phase_2_complete"

### Phase 3. Command Reference Validation
**Best Practice**: Reference integrity - ensure all referenced commands, scripts, and tools exist

- 3.1. **STATUS TRACKING**: Update workflow status to "phase_3_in_progress"
- 3.2. **ACTION**: BP? - "command reference validation and integrity checking best practices"
- 3.3. **ACTION**: FC? - "command reference accuracy and factual correctness verification"
- 3.4. **ACTION**: Extract all command references from AGENTS.md
- 3.5. **ACTION**: Validate each referenced command/script exists
- 3.6. **CHECK**: Script references exist in repo (reference integrity)
- 3.7. **CHECK**: Makefile targets and npm scripts exist
- 3.8. **CHECK**: Package manager commands are valid
- 3.9. **CHECK**: Commands have proper flags and options
- 3.10. **IF INCONSISTENCY FOUND**: STOP - Report inconsistency with specific location and suggested fix
- 3.11. **AWAIT USER APPROVAL**: Wait for user to approve fix before proceeding
- 3.12. **VALIDATION**: Validate that command reference validation completed successfully
- 3.13. **STATUS TRACKING**: Update workflow status to "phase_3_complete"

### Phase 4. Path Reference Validation
**Best Practice**: Reference integrity - ensure all referenced paths and files exist

- 4.1. **STATUS TRACKING**: Update workflow status to "phase_4_in_progress"
- 4.2. **ACTION**: BP? - "path reference validation and integrity checking best practices"
- 4.3. **ACTION**: FC? - "path reference accuracy and factual correctness verification"
- 4.4. **ACTION**: Extract all path references from AGENTS.md
- 4.5. **ACTION**: Validate each referenced path exists
- 4.6. **CHECK**: Internal markdown links resolve correctly (broken link detection)
- 4.7. **CHECK**: Path resolution works from multiple bases (own file, module root, repo root)
- 4.8. **CHECK**: Directory references are accurate
- 4.9. **CHECK**: No ambiguous path conflicts
- 4.10. **IF INCONSISTENCY FOUND**: STOP - Report inconsistency with specific location and suggested fix
- 4.11. **AWAIT USER APPROVAL**: Wait for user to approve fix before proceeding
- 4.12. **VALIDATION**: Validate that path reference validation completed successfully
- 4.13. **STATUS TRACKING**: Update workflow status to "phase_4_complete"

### Phase 5. KISS/Minimal Complexity Validation
**Best Practice**: Minimal viable validation - ensure AGENTS.md follows KISS principles

- 5.1. **STATUS TRACKING**: Update workflow status to "phase_5_in_progress"
- 5.2. **ACTION**: BP? - "KISS principle AGENTS.md minimal complexity best practices"
- 5.3. **ACTION**: FC? - "documentation complexity and simplicity accuracy verification"
- 5.4. **CHECK**: File length within recommended range (100-150 lines, ≤800 tokens)
- 5.5. **CHECK**: Signal-to-noise ratio high (only what agent cannot infer from code)
- 5.6. **CHECK**: Six-core-areas framework present (Commands, Testing, Structure, Style, Git, Boundaries)
- 5.7. **CHECK**: Progressive disclosure used (links to detailed docs vs inlining)
- 5.8. **CHECK**: Three-tier boundaries structure present (ALWAYS/ASK FIRST/NEVER)
- 5.9. **CHECK**: No redundancy detected (repeated information wasting context)
- 5.10. **CHECK**: Critical rules placed early (not buried late in document)
- 5.11. **CHECK**: Monolithic design avoided (split into linked files)
- 5.12. **IF INCONSISTENCY FOUND**: STOP - Report inconsistency with specific location and suggested fix
- 5.13. **AWAIT USER APPROVAL**: Wait for user to approve fix before proceeding
- 5.14. **VALIDATION**: Validate that KISS compliance validation completed successfully
- 5.15. **STATUS TRACKING**: Update workflow status to "phase_5_complete"

### Phase 6. Boundary Pattern Validation
**Best Practice**: Boundary validation - ensure three-tier boundary system is properly implemented

- 6.1. **STATUS TRACKING**: Update workflow status to "phase_6_in_progress"
- 6.2. **ACTION**: BP? - "three-tier boundary system AGENTS.md best practices"
- 6.3. **ACTION**: FC? - "boundary pattern accuracy and factual correctness verification"
- 6.4. **ACTION**: Review boundary sections in AGENTS.md
- 6.5. **CHECK**: Always do section contains non-negotiables (5-8 items max)
- 6.6. **CHECK**: Ask first section contains approval-required actions
- 6.7. **CHECK**: Never do section contains hard prohibitions
- 6.8. **CHECK**: Never rules are machine-checkable (specific, observable patterns)
- 6.9. **CHECK**: Boundaries are clearly defined and specific
- 6.10. **CHECK**: No contradictory boundary rules (ALWAYS vs NEVER conflicts)
- 6.11. **IF INCONSISTENCY FOUND**: STOP - Report inconsistency with specific location and suggested fix
- 6.12. **AWAIT USER APPROVAL**: Wait for user to approve fix before proceeding
- 6.13. **VALIDATION**: Validate that boundary pattern validation completed successfully
- 6.14. **STATUS TRACKING**: Update workflow status to "phase_6_complete"

### Phase 7. Code Style and Convention Validation
**Best Practice**: Convention validation - ensure code style guidelines are actionable and specific

- 7.1. **STATUS TRACKING**: Update workflow status to "phase_7_in_progress"
- 7.2. **ACTION**: BP? - "code style guidelines AGENTS.md best practices"
- 7.3. **ACTION**: FC? - "code style accuracy and factual correctness verification"
- 7.4. **ACTION**: Review code style section in AGENTS.md
- 7.5. **CHECK**: Code style uses real examples (good/bad snippets) not prose descriptions
- 7.6. **CHECK**: Style guidelines are specific and actionable
- 7.7. **CHECK**: Formatter, linter, naming conventions are specified
- 7.8. **CHECK**: File organization patterns are defined
- 7.9. **CHECK**: Style guidelines match actual project configuration
- 7.10. **IF INCONSISTENCY FOUND**: STOP - Report inconsistency with specific location and suggested fix
- 7.11. **AWAIT USER APPROVAL**: Wait for user to approve fix before proceeding
- 7.12. **VALIDATION**: Validate that code style validation completed successfully
- 7.13. **STATUS TRACKING**: Update workflow status to "phase_7_complete"

### Phase 8. Nested AGENTS.md Handling Validation
**Best Practice**: Monorepo validation - ensure nested AGENTS.md files follow precedence rules

- 8.1. **STATUS TRACKING**: Update workflow status to "phase_8_in_progress"
- 8.2. **ACTION**: BP? - "nested AGENTS.md monorepo precedence best practices"
- 8.3. **ACTION**: FC? - "nested AGENTS.md handling accuracy and factual correctness verification"
- 8.4. **ACTION**: Check for nested AGENTS.md files in subdirectories
- 8.5. **CHECK**: Nested AGENTS.md files exist only at worldview boundaries
- 8.6. **CHECK**: Precedence rules are clear (nearest file wins)
- 8.7. **CHECK**: Root AGENTS.md contains shared baseline rules
- 8.8. **CHECK**: Nested files contain only area-specific overrides
- 8.9. **CHECK**: No unnecessary nesting (avoid file proliferation)
- 8.10. **IF INCONSISTENCY FOUND**: STOP - Report inconsistency with specific location and suggested fix
- 8.11. **AWAIT USER APPROVAL**: Wait for user to approve fix before proceeding
- 8.12. **VALIDATION**: Validate that nested AGENTS.md handling validation completed successfully
- 8.13. **STATUS TRACKING**: Update workflow status to "phase_8_complete"

### Phase 9. Terminology Consistency Validation
**Best Practice**: Terminology validation - ensure consistent use of governance terminology

- 9.1. **STATUS TRACKING**: Update workflow status to "phase_9_in_progress"
- 9.2. **ACTION**: BP? - "terminology consistency validation and governance best practices"
- 9.3. **ACTION**: FC? - "terminology accuracy and factual correctness verification"
- 9.4. **ACTION**: Review AGENTS.md for terminology usage
- 9.5. **ACTION**: Cross-reference with Workflow/Workflow_Reference/Terminology_Glossary.md
- 9.6. **CHECK**: All capitalized terms are defined in Terminology Glossary
- 9.7. **CHECK**: Terminology usage is consistent across AGENTS.md
- 9.8. **CHECK**: No outdated terminology is present
- 9.9. **CHECK**: No generic software engineering principles that agent already knows
- 9.10. **IF INCONSISTENCY FOUND**: STOP - Report inconsistency with specific location and suggested fix
- 9.11. **AWAIT USER APPROVAL**: Wait for user to approve fix before proceeding
- 9.12. **VALIDATION**: Validate that terminology consistency validation completed successfully
- 9.13. **STATUS TRACKING**: Update workflow status to "phase_9_complete"

### Phase 10. Markdown Structure Validation
**Best Practice**: Documentation structure - ensure proper markdown formatting

- 10.1. **STATUS TRACKING**: Update workflow status to "phase_10_in_progress"
- 10.2. **ACTION**: BP? - "markdown structure validation and formatting best practices"
- 10.3. **ACTION**: FC? - "markdown structure accuracy and formatting correctness verification"
- 10.4. **ACTION**: Validate markdown document structure
- 10.5. **CHECK**: Heading hierarchy is consistent
- 10.6. **CHECK**: Section organization is logical
- 10.7. **CHECK**: Formatting is consistent (bold, italics, lists)
- 10.8. **CHECK**: Code blocks have proper language tags
- 10.9. **CHECK**: Links are properly formatted
- 10.10. **IF INCONSISTENCY FOUND**: STOP - Report inconsistency with specific location and suggested fix
- 10.11. **AWAIT USER APPROVAL**: Wait for user to approve fix before proceeding
- 10.12. **VALIDATION**: Validate that markdown structure validation completed successfully
- 10.13. **STATUS TRACKING**: Update workflow status to "phase_10_complete"

### Phase 11. Final Consistency Validation
**Best Practice**: Document control - final quality assurance check

- 11.1. **STATUS TRACKING**: Update workflow status to "phase_11_in_progress"
- 11.2. **ACTION**: BP? - "final AGENTS.md validation and quality assurance best practices"
- 11.3. **ACTION**: FC? - "final verification accuracy and factual correctness check"
- 11.4. **ACTION**: Perform comprehensive review of all fixes applied during validation
- 11.5. **CHECK**: All inconsistencies found during validation were resolved
- 11.6. **CHECK**: AGENTS.md is ready for deployment/use
- 11.7. **IF REMAINING ISSUES**: STOP - Report remaining issues with suggested fixes
- 11.8. **AWAIT USER APPROVAL**: Wait for user to approve final state
- 11.9. **VALIDATION**: Validate that final consistency validation completed successfully
- 11.10. **STATUS TRACKING**: Update workflow status to "phase_11_complete"
- 11.11. **PRINT**: "Architect AGENTS.md Validation workflow execution complete - AGENTS.md validated"

---

## Universal Framework References

### Validation Enforcement
- **Universal Framework**: Workflow/Workflow_Reference/Validation_Enforcement_Patterns.md
- **Agent Customization**: AGENTS.md validation enforcement patterns
- **Usage**: Reference universal framework for consistency

---

## Execution Guidelines

### Process
1. Execute phases in sequential order
2. Stop at each inconsistency found
3. Report inconsistency with specific location and suggested fix
4. Await user approval before proceeding
5. Apply fix and continue validation
6. Repeat until all phases are complete

### Best Practice Application
- **Structure validation**: Ensure AGENTS.md follows recommended sections and organization
- **Reference integrity**: Validate all commands, scripts, and paths exist

## Changelog

**2026-07-30**: Template compliance fixes
- Added Load Governance Rules section (mandated by template)
- Added Select Execution Mode section (mandated by template)
- Added Reference Documents section with Universal Framework References
- Added Universal Framework References section (mandated by template)
- Updated version to 2.1
- **KISS compliance**: Ensure file is concise (100-150 lines, ≤800 tokens)
- **Boundary validation**: Verify three-tier boundary system (ALWAYS/ASK FIRST/NEVER)
- **Web search integration**: Use "BP?" web searches at designated points to validate against current industry best practices
- **Fact check integration**: Use "FC?" fact checking at designated points to verify factual accuracy

### Quality Standards
- All critical issues must be resolved before deployment
- Important issues should be resolved with documented rationale if deferred
- Minor issues can be deferred to next revision cycle
- AGENTS.md must remain under 150 lines and ≤800 tokens

## Usage Instructions

### For AGENTS.md Validation
1. Specify target AGENTS.md file path
2. Workflow executes through all validation phases
3. Each inconsistency triggers stop-and-fix with user approval
4. Final validation confirms AGENTS.md is ready for use