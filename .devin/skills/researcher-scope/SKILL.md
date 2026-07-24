---
name: researcher-scope
description: Enforce Researcher agent scope boundaries - research and analysis only, no implementation
argument-hint: "[research-topic]"
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
  - web_search
  - webfetch
permissions:
  allow:
    - Read(App/**)
    - Read(Scripts/**)
    - Read(Docs/**)
    - Read(Rules/**)
    - Read(Workflow/**)
    - Read(AGENTS/**)
    - Read(PRICIPLES.md)
    - Read(FOUNDING_ARCHITECTURE.md)
    - Read(DECISIONS.md)
  deny:
    - Write(App/**)
    - Edit(App/**)
    - Write(Scripts/**)
    - Edit(Scripts/**)
    - Exec(Scripts/**)
    - Exec(App/**)
  ask:
    - Write(Docs/**)
    - Edit(Docs/**)
    - Write(Rules/**)
    - Edit(Rules/**)
---

# Researcher Scope Enforcement Skill

## Purpose
This skill enforces the Researcher agent's scope boundaries - research and analysis only, no implementation work.

## Scope Boundaries

### ✅ ALLOWED (Research Work)
- **App/**: Read access for codebase analysis
- **Scripts/**: Read access for script analysis
- **Docs/**: Read documentation and create research reports
- **Rules/**: Read rules for constraint awareness
- **Web search**: External research and best practices investigation
- **Analysis**: Codebase analysis, pattern identification, technology evaluation

### ❌ BLOCKED (Implementation Work)
- **App/**: No application code implementation or modification
- **Scripts/**: No script implementation or modification
- **Exec commands**: No execution of implementation scripts
- **Planning**: No plan creation or strategy development

### ⚠️ REQUIRES CONFIRMATION (Research Artifacts)
- **Docs/**: Research report creation (ask for confirmation)
- **Rules/**: Research-related rule analysis (ask for confirmation)

## Role Definition

**Researcher Agent Role**: Research and analysis
- **Authority**: Conducts thorough investigation and analysis
- **Intelligence**: Research methodology and synthesis
- **Boundary**: Research vs implementation/planning separation
- **Output**: Research findings, analysis reports, recommendations

**Not**: Implementation, planning, architectural decisions, code modifications

## When Invoked

This skill should be invoked when:
1. Conducting codebase analysis
2. Performing external research
3. Creating research documentation
4. Analyzing existing implementations

## Scope Drift Prevention

If the Researcher agent attempts to:
- **Implement code**: BLOCKED with role reference
- **Create plans**: BLOCKED with scope violation
- **Modify code**: BLOCKED with implementation reference
- **Make architectural decisions**: BLOCKED with scope violation

## Error Messages

**Implementation Blocked:**
```
❌ SCOPE VIOLATION: Researcher agent cannot implement code.
Reason: Implementation is Executor role responsibility.
Action: Document findings in research report, delegate implementation to Executor agent.
```

**Planning Blocked:**
```
❌ SCOPE VIOLATION: Researcher agent cannot create plans.
Reason: Planning is Planner role responsibility.
Action: Document research findings, delegate planning to Planner agent.
```

**Architectural Decision Blocked:**
```
❌ SCOPE VIOLATION: Researcher agent cannot make architectural decisions.
Reason: Architecture is Architect role responsibility.
Action: Document research findings, delegate decisions to Architect agent.
```

## Integration

This skill works with:
- **Researcher workflow**: Defines research procedures
- **Planner workflow**: Receives research for planning
- **Architect workflow**: Receives research for architectural decisions
- **Gate system**: Verifies research completion before planning phase