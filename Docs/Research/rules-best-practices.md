# Rules.md Best Practices Research

**Source:** Multiple web sources  
**Date:** 2026-07-25  
**Purpose:** Rules.md best practices for agent governance

## Key Findings from Research

### Rule Format Standards
- **Declarative policy** - not procedures or informational content
- **Start with imperative verbs** - use, prefer, name, write, keep
- **Actionable content** - every rule must direct agent behavior
- **Falsifiable rules** - must be possible to determine if rule is followed
- **Specific and observable** - avoid vague "best practices" language

### Rule Organization
- **Conventions** - specific rules the AI must follow
- **Constraints** - hard boundaries the agent must not cross
- **Architecture** - decisions that explain system shape
- **Tool Configuration** - concrete commands and tool setup
- **Three-tier boundaries:** Always, Ask first, Never

### Size and Scope
- **Short is better** - 150-200 instructions max before compliance drops
- **Line budget** - stay under 1000 lines total
- **Externalize procedures** - move multi-step procedures to runbooks
- **No large code blocks** - code over 10 lines belongs in external files

### Validation Rules
- **No machine-local paths** - must work across different machines
- **No large code blocks** - procedures belong in runbooks
- **Falsifiable** - must be possible to verify rule compliance
- **Actionable** - every rule must contain imperative verb

### Best Practice Examples
**Good conventions:**
- Use snake_case for all Python modules and functions
- File names: kebab-case (e.g., user-profile.ts)
- API routes return { data, error } envelopes
- All DB queries go through src/db/ helpers

**Bad conventions:**
- Follow best practices (too vague)
- Write clean code (not specific)
- Keep things simple (not observable)

### Rule Types and Purpose
- **Conventions** - specific coding standards
- **Constraints** - hard prohibitions and requirements
- **Architecture** - system design decisions
- **Tool Configuration** - commands and tool setup
