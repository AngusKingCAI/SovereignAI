# AGENTS.md vs Rules.md Best Practices Research

**Source:** Multiple web sources  
**Date:** 2026-07-25  
**Purpose:** Determine where operational rules should be placed

## Key Findings from Research

### AGENTS.md Purpose
- **Operational contract** for the repository
- **How the repo works** - stable, verifiable, true for every agent
- Contains: build commands, test commands, file structure, boundaries
- **Imperative and specific** instructions
- **Loaded into context** when session begins
- **Travels to any engine** - agent-agnostic standard

### RULES.md Purpose  
- **Sticky rules** - hard requirements that should always apply
- **Short, hard requirements** that get converted to always-apply rules
- **Durable project background** and policy
- **Re-attached near current turn** to maintain hold over conversation
- **Used for cross-repo policy** management

### Decision Rule
- **If an AI agent needs it to write correct code** → AGENTS.md
- **If it's a hard requirement that always applies** → RULES.md
- **If it's how the repo works operationally** → AGENTS.md
- **If it's durable policy/decision reasoning** → RULES.md

### Examples from Research
**AGENTS.md content:**
- "Run `make test` before you claim done"
- "Migrations live in `db/migrate`"  
- "Never edit generated files"
- How to build, how to run tests, which commands are safe

**RULES.md content:**
- Short, hard requirements
- Cross-repo policy
- Always-apply behavioral rules
- Product decision reasoning

### Best Practice Summary
- AGENTS.md: Operational instructions, commands, structure, boundaries
- RULES.md: Hard requirements, sticky rules, durable policy
- AGENTS.md travels to any engine, RULES.md for always-apply behavior
