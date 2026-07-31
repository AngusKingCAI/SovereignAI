---
name: architect-agent
description: System-level designer who creates deterministic harness infrastructure and governance frameworks to keep multi-agent systems aligned with their rules and workflows
---

# AGENTS.md Template

**Purpose**: Template structure for creating AGENTS.md files optimized for Devin CLI with strategic standard sections for the Architect agent.

## Section Structure

### Section 1: Project Context
**Purpose**: High-level overview of the Architect agent role
**Why**: Agent needs immediate context about its specific role and responsibilities

### Section 2: Response Format
**Purpose**: Agent identification and session state function
**Why**: Critical for WorkflowOpen skill to load correct agent rules
**Format**: Always start responses with '[🏗️ ARCHITECT AGENT]' on first line

### Section 3: Universal References
**Purpose**: Single source of truth documents that apply across all agents
**Why**: Establishes critical governance framework before agent makes decisions
**Documents**: .devin/rules/{agent}.md, Workflow/Workflow_Reference/Terminology_Glossary.md, PRINCIPLES.md, STRUCTURE.md

### Section 4: Tech Stack
**Purpose**: Languages, frameworks, key libraries with versions
**Why**: Agent needs to know available tools and version constraints

### Section 5: Architecture/Skills Reference
**Purpose**: Key directories and Devin CLI skill references
**Why**: Skills load only when relevant, optimizing context and cost

### Section 6: Commands
**Purpose**: Specific shell commands for common operations
**Why**: Command-first approach vs. vague instructions

### Section 7: Testing Instructions
**Purpose**: How to run tests, coverage expectations, test conventions
**Why**: Agent needs to know how to validate work before completion

### Section 8: Delegation Rules
**Purpose**: When and how to use subagents (Devin CLI specific)
**Why**: Prevents uncontrolled subagent spawning

### Section 9: Memory/Guidance
**Purpose**: What to store/not store in context
**Why**: Prevents secrets leakage and context bloat

### Section 10: Constraints
**Purpose**: Hard boundaries and prohibited actions
**Why**: Clear "never do this" rules with alternatives

### Section 11: Security Considerations
**Purpose**: Secrets handling, dependencies to avoid, auth patterns
**Why**: Prevents security violations in automated code generation