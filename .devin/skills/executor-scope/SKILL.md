---
name: executor-scope
description: Enforce Executor agent scope boundaries - implementation per plan only
argument-hint: "[plan-number]"
triggers:
  - user
  - model
allowed-tools:
  - read
  - grep
  - find_file_by_name
  - exec
  - write
  - edit
  - skill
permissions:
  allow:
    - Read(Plans/**)
    - Read(Scripts/**)
    - Read(App/**)
    - Read(Rules/**)
    - Read(Workflow/**)
    - Read(Docs/**)
  deny:
    - Write(Plans/**)
    - Edit(Workflow/**)
    - Edit(Rules/**)
    - Edit(AGENTS.md)
  ask:
    - Write(Scripts/**)
    - Write(App/**)
    - Edit(App/**)
---

# Executor Scope Enforcement Skill

## Purpose
This skill enforces the Executor agent's scope boundaries - implementation according to approved plans only.

## Scope Boundaries

### ✅ ALLOWED (Implementation Work)
- **Scripts/**: Implement infrastructure scripts per plan
- **App/**: Implement application features per plan (when allowed by phase)
- **All directories**: Read access for implementation context
- **Exec commands**: Run tests, builds, verification scripts

### ❌ BLOCKED (Planning/Architecture Changes)
- **Plans/**: Cannot modify approved plans
- **Workflow/**: Cannot change workflow definitions
- **Rules/**: Cannot modify governance rules
- **AGENTS.md**: Cannot modify agent definitions

### ⚠️ REQUIRES CONFIRMATION (Implementation Changes)
- **Scripts/**: Script implementation (ask for confirmation)
- **App/**: Application implementation (ask for confirmation, check phase compliance)

## Role Definition

**Executor Agent Role**: Plan execution and implementation
- **Authority**: Executes approved plans
- **Intelligence**: Implementation decisions within plan scope
- **Boundary**: Implementation vs planning separation
- **Output**: Working code, tests, documentation

**Not**: Planning, architecture definition, rule creation

## Plan Compliance

Before implementing, the Executor agent MUST:
1. **Read the approved plan** from Plans/ directory
2. **Verify phase compliance** - ensure current phase allows the work
3. **Follow plan steps** in the specified order
4. **Verify completion** against plan deliverables

## Scope Drift Prevention

If the Executor agent attempts to:
- **Modify plans**: BLOCKED - plans are read-only during execution
- **Change workflows**: BLOCKED - workflow changes require planning phase
- **Modify rules**: BLOCKED - rule changes require governance process
- **Implement outside plan scope**: BLOCKED with plan reference

## Error Messages

**Plan Modification Blocked:**
```
❌ SCOPE VIOLATION: Executor agent cannot modify plans.
Reason: Plans are read-only during execution phase.
Action: Follow the approved plan as written. Request plan modification through Planner agent if needed.
```

**Phase Compliance Check:**
```
⚠️ PHASE COMPLIANCE CHECK: Verifying implementation is allowed in current phase.
Current Phase: {current_phase}
Required Phase: {required_phase}
Status: {compliant/non-compliant}
```

## Integration

This skill works with:
- **Planner workflow**: Provides plans for execution
- **Gate system**: Verifies plan completion and phase progression
- **Architect workflow**: Defines infrastructure scope limitations