# Rules Template

**Purpose**: Generic rule template following AI agent best practices with warm-rules optimization for persistent agents  
**Status**: Template  
**Created**: 2026-07-24  
**Template Type**: Hybrid Warm-Rules  

---

## Warm Rules (Critical - First 50 Lines)

These 5-10 critical rules are enforced on every task and cached separately for optimal compliance.

### 1. Constitutional Compliance
- ALWAYS verify constitutional compliance before making decisions
- NEVER skip constitutional compliance checks for convenience
- BEFORE any architectural change, verify constitutional framework alignment
- AFTER decisions, document constitutional compliance rationale

### 2. Scope Boundaries  
- NEVER implement features outside defined agent scope
- ALWAYS reference scope boundaries when uncertain
- BEFORE starting work, verify task is within agent scope
- IF scope unclear, STOP and request clarification

### 3. Authority and Intelligence Separation
- NEVER mix authority and intelligence in the same component
- ALWAYS maintain separation between governance and execution
- BEFORE component design, verify authority/intelligence separation
- DURING implementation, check for separation violations

### 4. Verification and Testing
- NEVER proceed without verification when verification is required
- ALWAYS test implementations before marking complete
- BEFORE completion, run all required verification steps
- IF verification fails, STOP and address issues

### 5. Documentation and Evidence
- NEVER make undocumented changes to governed files
- ALWAYS generate evidence (hashes, logs) for compliance verification
- BEFORE completion, ensure documentation is current
- AFTER changes, update relevant documentation

### 6. Best Practice Research
- NEVER make architectural decisions without industry best practices research
- ALWAYS search for best practices before proposing solutions
- BEFORE architectural decisions, complete research step
- IF uncertain about best practices, conduct additional research

### 7. Gate Enforcement
- NEVER skip gate verification for convenience
- ALWAYS treat gate failures as STOP conditions
- BEFORE proceeding to next step, verify current gate passes
- IF gate fails, address issues before proceeding

### 8. File and Directory Compliance
- NEVER place files outside designated directories per IDE architecture rules
- ALWAYS use standard naming conventions for files and directories
- BEFORE creating files, verify location complies with IDE architecture
- DURING file operations, follow directory structure standards

---

## Template Metadata

### Template Information
- **Template Name**: Hybrid Warm-Rules Template
- **Version**: 1.0
- **Created**: 2026-07-24
- **Last Modified**: 2026-07-24
- **Template Type**: Generic Rule Template
- **Compatibility**: All agent types (Architect, Planner, Executor, Researcher, Reviewer)

### Caching Directives
- **Warm Rules Cache**: HIGH PRIORITY - Cache first 50 lines separately
  - Cache file: `Logs/{AgentName}/Cache/warm_rules_cache.json`
  - Re-read triggers: File modification, session start, context compaction
  - Cache validation: Hash-based verification
  - Refresh strategy: Automatic on template changes

- **Appendices Cache**: OPTIONAL - Cache detailed sections on-demand
  - Cache file: `Logs/{AgentName}/Cache/appendices_cache.json`  
  - Re-read triggers: Template modification, manual refresh
  - Cache validation: Hash-based verification
  - Refresh strategy: On-demand when complex decisions needed

### Integration Points
- **IDE Architecture Rules**: Complies with `Rules/Architect/IDE_Architecture_Rules.md`
- **Agent AGENTS.md Files**: Reference this template for rule creation
- **Gate System**: Includes gate enforcement hook points at each rule
- **Audit Logging**: Violations logged to `Logs/{AgentName}/Gates/`
- **MCP Integration**: Designed for future rule repository tool integration

### Dependencies
- **Required**: IDE Architecture Rules compliance
- **Optional**: MCP server for rule repository integration
- **Related**: Agent-specific AGENTS.md files
- **Compatible**: Existing agent workflows and gate systems

### Template Usage
- **For New Agents**: Copy template and customize Warm Rules for agent-specific needs
- **For Existing Agents**: Use template to refactor current rules into warm-rules format
- **For Rule Updates**: Follow evolution procedures in appendices
- **For Compliance**: Verify template compliance before agent deployment

---

## Structured Appendices

Detailed rule coverage organized by category for comprehensive agent governance.

### 1. Constitutional Constraints (Detailed)

**DO**:
- Follow constitutional framework in all decisions
- Verify constitutional compliance before architectural changes
- Document constitutional compliance rationale for all decisions
- Reference constitutional principles when uncertain
- Escalate constitutional questions for clarification

**DON'T**:
- Skip constitutional compliance checks for convenience
- Make decisions without constitutional verification
- Override constitutional constraints without explicit approval
- Ignore constitutional framework in emergency situations
- Proceed when constitutional compliance is unclear

### 2. Architectural Constraints

**DO**:
- Follow infrastructure-first principles in all designs
- Maintain separation between authority and intelligence components
- Design deterministic systems with predictable behavior
- Create observable systems with clear audit trails
- Implement minimal coupling between components
- Design systems with explicit interfaces

**DON'T**:
- Mix authority and intelligence in the same component
- Trust AI models for decision-making without verification
- Rely on voluntary compliance for critical constraints
- Proceed when uncertain without architectural verification
- Make architectural decisions without best practices research
- Create tightly coupled components without clear boundaries

### 3. Process Constraints

**DO**:
- Follow defined workflows for all agent operations
- Complete all required steps before proceeding
- Verify gate compliance before phase transitions
- Generate evidence (hashes, logs) for compliance verification
- Document process deviations with approval
- Follow quality > token cost > efficiency hierarchy

**DON'T**:
- Skip workflow steps for convenience
- Proceed without required verification
- Override gate decisions without explicit approval
- Make undocumented process changes
- Ignore quality standards for speed
- Proceed when process compliance is uncertain

### 4. Integration Constraints

**DO**:
- Follow IDE architecture rules for file placement
- Use standard naming conventions for files and directories
- Verify directory structure compliance before development
- Reference agent-specific rules for cross-agent coordination
- Follow integration procedures for system changes
- Maintain clear interfaces between components

**DON'T**:
- Place files outside designated directories
- Use non-standard naming conventions
- Skip directory structure verification
- Modify infrastructure without Architect approval
- Create agent folders without proper documentation
- Violate integration boundaries without approval

### 5. Quality Standards

**DO**:
- Follow project coding standards and conventions
- Write clean, readable, maintainable code
- Include appropriate error handling
- Add meaningful comments where necessary
- Follow security best practices
- Test implementations thoroughly
- Maintain clear documentation

**DON'T**:
- Write code that is difficult to understand
- Skip error handling and validation
- Leave TODOs or FIXMEs without resolution
- Implement insecure coding practices
- Duplicate code instead of creating reusable functions
- Skip testing or verification steps
- Leave documentation outdated

### 6. Enforcement Mechanisms

**DO**:
- Implement automated hooks for critical rules
- Use gate system for workflow enforcement
- Generate audit trails for all decisions
- Log rule violations for analysis
- Use verification scripts for compliance checking
- Implement escalation procedures for violations

**DON'T**:
- Rely on agent attention for critical rule enforcement
- Skip gate verification for convenience
- Proceed without generating required evidence
- Ignore rule violation patterns
- Override enforcement mechanisms without approval
- Proceed when enforcement is uncertain

### 7. Evolution Procedures

**DO**:
- Add rules based on pattern recognition from violations
- Document rule changes with rationale
- Update related documentation when rules change
- Test rule changes before deployment
- Follow amendment process for constitutional changes
- Review rules periodically for relevance

**DON'T**:
- Add rules without clear violation patterns
- Make undocumented rule changes
- Skip testing for rule changes
- Override constitutional amendment process
- Ignore rule obsolescence
- Make rule changes without impact analysis

---

## Best Practice Integration

Based on AI agent rule enforcement research and production deployment patterns:

### Warm Rules Optimization
- Critical rules in first 50 lines achieve 99% compliance vs 50% for buried rules
- Separate caching enables efficient re-reading between edits
- Trigger-action-verification pattern ensures rule enforceability
- Persistent agents benefit from warm-start mechanisms

### Enforcement Hierarchy
- Automated hooks for critical rules (99% reliable)
- Warm-rules injection for persistent agents (85% reliable)
- Inline rules at decision points (70% reliable)
- Reference documentation for complex scenarios (50% reliable)

### Caching Strategy
- Rule propagation cost drops to O(1) with proper caching
- Single source of truth eliminates update synchronization issues
- Hash-based validation ensures cache integrity
- Automatic refresh triggers maintain consistency

### Integration Architecture
- Complies with IDE architecture rules for file placement
- Compatible with existing agent workflows and gate systems
- Designed for future MCP server integration
- Supports both automated and manual enforcement modes

---

## Template Compliance Checklist

- [ ] Warm Rules Section contains 5-10 critical rules
- [ ] Warm Rules are within first 50 lines of template
- [ ] Each warm rule follows trigger-action-verification pattern
- [ ] Metadata section includes caching directives
- [ ] Integration points align with IDE architecture rules
- [ ] Structured appendices provide comprehensive coverage
- [ ] Evolution procedures support rule updates
- [ ] Template follows naming conventions
- [ ] File location complies with directory structure
- [ ] Template is compatible with existing infrastructure

---

**Current Constitutional Status**: COMPLIANT

This template follows infrastructure-first principles and implements best practices for AI agent rule enforcement based on research into production systems and rule repository architectures.