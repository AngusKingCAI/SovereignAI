# Planner Gate System Specification

**Purpose**: Automated gate system to ensure Planner agent follows rules exactly before plan delivery to Executor.

**Status**: Proposed  
**Created**: 2026-07-24  
**Phase**: Phase 1 - Soft Kernel Governance

---

## Problem Statement

The existing Planner workflow has extensive manual compliance checks but lacks automated enforcement. Plans can be delivered to Executor without verification that:
- Plan format meets structural requirements
- Scope boundaries are respected (no implementation details)
- Executor Manifest is complete and valid
- Dependencies are properly analyzed
- Landmine screening was actually performed
- Architect validation criteria are met

## Solution Overview

Build a "soft kernel" gate system using Devin CLI capabilities to automatically validate Planner outputs before they can be delivered to Executor. This achieves kernel-level rule enforcement without requiring system-level access.

## Gate System Architecture

### Primary Gates

**Gate 1: Plan Structure Validation**
- Validates plan format against specification
- Checks required sections (Context, Steps, Dependencies, Executor Manifest)
- Verifies step ordering and dependency format
- **BLOCK**: Invalid plan structure
- **PASS**: Plan structure validated

**Gate 2: Scope Compliance Validation**
- Scans plan for implementation details (code, script references, function calls)
- Verifies planning language only (no technical implementation terms)
- Checks for forbidden patterns (e.g., "implement", "write code", "function definition")
- **BLOCK**: Implementation details detected
- **PASS**: Scope compliant (planning only)

**Gate 3: Executor Manifest Validation**
- Validates Executor Manifest completeness
- Checks required fields: identity, capabilities, I/O schemas, token budget
- Verifies format consistency with specification
- **BLOCK**: Invalid or incomplete Executor Manifest
- **PASS**: Executor Manifest validated

**Gate 4: Dependency Analysis Validation**
- Verifies dependency graph integrity
- Checks for circular dependencies
- Validates step ordering against dependencies
- **BLOCK**: Invalid dependency structure
- **PASS**: Dependency analysis validated

**Gate 5: Landmine Screening Verification**
- Verifies LANDMINES.md screening was performed
- Checks for documented screening results
- Validates no blocking landmines present
- **BLOCK**: Landmine screening not performed or blocking landmines present
- **PASS**: Landmine screening verified

**Gate 6: Architect Validation Gate**
- Architect validates plan against FOUNDING_ARCHITECTURE.md
- Checks constitutional compliance
- Verifies phase appropriateness
- **BLOCK**: Architect validation failed
- **PASS**: Architect approved

## Implementation Design

### Script Structure

```
Scripts/Planner/Gates/
├── verify-plan-structure.sh
├── verify-scope-compliance.sh
├── verify-executor-manifest.sh
├── verify-dependency-analysis.sh
├── verify-landmine-screening.sh
├── architect-validation-gate.sh
├── run-all-planner-gates.sh
└── gate-core/
    ├── plan-parser.py
    ├── scope-checker.py
    ├── manifest-validator.py
    └── dependency-analyzer.py
```

### Gate Integration Points

**Before Step 7 (Plan Delivery):**
- Run all 6 gates sequentially
- Each gate must pass before proceeding
- Failure blocks plan delivery and requires revision

**After Planner completes workflow:**
- Generate gate completion hash
- Record gate results in Planner state file
- Log gate verification in conversation audit trail

### Gate Error Messages

**Gate 1 Failure:**
```
❌ PLAN STRUCTURE GATE FAILED
Plan: {plan_file}
Errors: {specific structure errors}
Action: Fix plan structure before proceeding
Reference: Workflow/Planner/Plan.md - Plan Format section
```

**Gate 2 Failure:**
```
❌ SCOPE COMPLIANCE GATE FAILED
Plan: {plan_file}
Violations: {implementation details detected}
Action: Remove implementation details, planning only
Reference: .devin/skills/planner-scope/SKILL.md - Scope Boundaries
```

**Gate 3 Failure:**
```
❌ EXECUTOR MANIFEST GATE FAILED
Plan: {plan_file}
Errors: {manifest validation errors}
Action: Complete Executor Manifest per specification
Reference: Workflow/Planner/Plan.md - Executor Manifest section
```

## Integration with Existing System

### Planner Workflow Integration
- Add gate verification after Step 6 (Process Findings)
- Before Step 7 (Plan Delivery Condition)
- Update workflow documentation with gate requirements

### Architect Handoff Validation
- Architect must run Gate 6 before approving plan
- Cross-agent validation ensures architectural compliance
- Architect decision recorded in state file

### Skills Enhancement
- Enhance planner-scope skill with gate integration
- Auto-run gates when Planner attempts to write plan files
- Gate results shown in permission prompts

## Validation Requirements

### Definition of Done
- [ ] All 6 gate scripts implemented and tested
- [ ] Gate verification integrated into Planner workflow
- [ ] Architect validation gate operational
- [ ] Gate completion hash generation working
- [ ] Gate results logged in conversation audit trail
- [ ] Manual gate testing with sample plans (valid and invalid)
- [ ] Cross-agent validation working (Architect-Planner)
- [ ] Documentation updated (workflow, skills, AGENTS.md)

### Testing Requirements
- Test valid plan: All gates pass
- Test invalid structure: Gate 1 fails
- Test scope violation: Gate 2 fails
- Test incomplete manifest: Gate 3 fails
- Test bad dependencies: Gate 4 fails
- Test missing landmine screening: Gate 5 fails
- Test architectural violation: Gate 6 fails

## Compliance Integration

### Constitutional Compliance
- All gates respect FOUNDING_ARCHITECTURE.md First Rule
- Scope enforcement maintains infrastructure-only focus
- Architect validation ensures constitutional hierarchy

### Phase Progression
- Gate system supports Phase 0→Phase 1 progression
- Phase 1 defined as "Soft Kernel Governance"
- Foundation for future Executor and Reviewer gates

## Rollout Plan

1. **Implementation Phase**: Build gate scripts and validation logic
2. **Integration Phase**: Integrate with Planner workflow and skills
3. **Testing Phase**: Test with sample plans and edge cases
4. **Documentation Phase**: Update all relevant documentation
5. **Production Phase**: Enable gates for actual Planner workflows

## Success Metrics

- Zero plans delivered with structural violations
- Zero plans delivered with scope violations
- 100% Executor Manifest completeness
- 100% landmine screening verification
- Architect validation on all plan deliveries
- Reduced manual verification workload