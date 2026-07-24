---
name: architect-scope
description: Enforce Architect agent scope boundaries - infrastructure only, no application code
argument-hint: "[task]"
triggers:
  - model
allowed-tools:
  - read
  - grep
  - find_file_by_name
  - exec
  - write
  - edit
  - ask_user_question
  - todo_write
  - skill
permissions:
  allow:
    - Read(Agents/**)
    - Read(Rules/**)
    - Read(Workflow/**)
    - Read(Scripts/**)
    - Read(Docs/**)
    - Read(Logs/**)
    - Read(Plans/**)
    - Read(PRICIPLES.md)
    - Read(FOUNDING_ARCHITECTURE.md)
    - Read(DECISIONS.md)
    - Read(README.md)
  deny:
    - Write(App/**)
    - Edit(App/**)
    - Exec(App/**)
  ask:
    - Write(Scripts/**)
    - Edit(Scripts/**)
    - Write(Docs/**)
    - Edit(Docs/**)
---

# Architect Scope Enforcement Skill

## Purpose
This skill enforces the Architect agent's scope boundaries as defined in `Agents/Architect/AGENTS.md`. It prevents scope drift by restricting access to application code (App/ directory) while allowing infrastructure work.

## Scope Boundaries

### ✅ ALLOWED (Infrastructure Work)
- **Agents/**: Agent definitions and governance
- **Rules/**: Rule definitions and architecture rules  
- **Workflow/**: Workflow definitions and procedures
- **Scripts/**: Infrastructure scripts and tools
- **Docs/**: Documentation and specifications
- **Logs/**: Log files and audit trails
- **Plans/**: Execution plans and state management
- **Root constitutional docs**: PRINCIPLES.md, FOUNDING_ARCHITECTURE.md, DECISIONS.md

### ❌ BLOCKED (Application Work)
- **App/**: SovereignAI application code (completely blocked)
- No writing, editing, or executing commands in App/ directory

### ⚠️ REQUIRES CONFIRMATION (Infrastructure Modifications)
- **Scripts/**: Infrastructure script changes (ask for confirmation)
- **Docs/**: Documentation changes (ask for confirmation)

## Constitutional Compliance

This skill enforces the FOUNDING_ARCHITECTURE.md First Rule:
> "Never build SovereignAI first. Build the infrastructure that will later build SovereignAI."

## When Invoked

This skill should be automatically invoked when:
1. The Architect agent is working on infrastructure tasks
2. Any file operations are attempted
3. Scope boundaries need to be enforced

## Scope Drift Detection

If the Architect agent attempts to:
- **Edit files in App/**: BLOCKED with error message
- **Implement application features**: BLOCKED with constitutional reference
- **Modify App/ directory structure**: BLOCKED with scope violation notice

## Error Messages

**App/ Access Blocked:**
```
❌ SCOPE VIOLATION: Architect agent cannot modify App/ directory.
Reason: Application code implementation is deferred to Phase 12 per FOUNDING_ARCHITECTURE.md.
Action: Redirect to infrastructure work or defer to appropriate phase.
Reference: Agents/Architect/AGENTS.md - Scope Boundaries section
```

**Infrastructure Modification Confirmation:**
```
⚠️ CONFIRMATION REQUIRED: Modifying infrastructure file.
File: {file_path}
Action: {write/edit}
This change affects infrastructure architecture. Confirm this aligns with infrastructure scope.
```

## Usage

The skill is automatically active during Architect agent sessions. No manual invocation needed - it enforces scope boundaries transparently.

## Integration

This skill works with:
- **AGENTS.md**: Defines the scope boundaries this skill enforces
- **Gate system**: Verifies compliance at phase boundaries
- **Conversation logging**: Documents any scope violations that occur