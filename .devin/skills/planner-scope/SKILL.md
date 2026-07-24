---
name: planner-scope
description: Enforce Planner agent scope boundaries - planning only, no implementation
argument-hint: "[plan]"
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
  - ask_user_question
  - skill
  - todo_write
permissions:
  allow:
    - Read(Plans/**)
    - Read(Workflow/**)
    - Read(Rules/**)
    - Read(Docs/**)
    - Read(PRICIPLES.md)
    - Read(FOUNDING_ARCHITECTURE.md)
    - Read(DECISIONS.md)
  deny:
    - Write(Scripts/**)
    - Write(App/**)
    - Edit(Scripts/**)
    - Edit(App/**)
    - Exec(Scripts/**)
    - Exec(App/**)
  ask:
    - Write(Plans/**)
    - Write(Workflow/**)
    - Write(Docs/**)
---

# Planner Scope Enforcement Skill

## Purpose
This skill enforces the Planner agent's scope boundaries - planning and specification only, no implementation work.

## Scope Boundaries

### ✅ ALLOWED (Planning Work)
- **Plans/**: Create and modify execution plans
- **Workflow/**: Read workflow definitions for planning context
- **Rules/**: Read rules for constraint awareness
- **Docs/**: Read documentation and create specifications
- **Constitutional docs**: Reference for planning compliance

### ❌ BLOCKED (Implementation Work)
- **Scripts/**: No script implementation or modification
- **App/**: No application code work
- **Exec commands**: No execution of implementation scripts

### ⚠️ REQUIRES CONFIRMATION (Planning Artifacts)
- **Plans/**: Plan creation/modification (ask for confirmation)
- **Docs/**: Specification creation (ask for confirmation)

## Role Definition

**Planner Agent Role**: Plan creation and specification
- **Authority**: Defines what should be done
- **Intelligence**: Planning logic and dependency analysis
- **Boundary**: Planning vs implementation separation
- **Output**: Plans, specifications, requirements

**Not**: Implementation, coding, testing, deployment

## When Invoked

This skill should be invoked when:
1. Creating or modifying execution plans
2. Writing specifications
3. Any planning-related documentation work

## Scope Drift Prevention

If the Planner agent attempts to:
- **Implement code**: BLOCKED with role reference
- **Run implementation scripts**: BLOCKED with scope violation
- **Modify Scripts/** without plan authority: BLOCKED

## Error Messages

**Implementation Blocked:**
```
❌ SCOPE VIOLATION: Planner agent cannot implement code.
Reason: Implementation is Executor role responsibility.
Action: Create plan for implementation, delegate to Executor agent.
```

## Integration

This skill works with:
- **Planner workflow**: Defines planning procedures
- **Executor workflow**: Receives plans for implementation
- **Gate system**: Verifies plan completion before implementation