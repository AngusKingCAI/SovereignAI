# AGENTS.md Length and Size Best Practices Research

**Source:** Multiple web sources  
**Date:** 2026-07-25  
**Purpose:** AGENTS.md character limit and size recommendations

## Key Findings from Research

### Size Recommendations
- **150 lines recommended** - Factory.ai and multiple sources recommend under 150 lines
- **100-200 lines ideal** - Some sources say 100-300 lines at root, but 150 is the sweet spot
- **32 KiB technical maximum** - Codex caps at 32 KiB default
- **500 lines absolute maximum** - Most agents start ignoring after first few thousand tokens

### Problems with Long Files
- Buried instructions lose salience
- Rules can conflict with each other
- Files go stale at different rates
- Most important rules get buried under nice-to-knows
- Agents start ignoring buried instructions

### Progressive Disclosure Principle
- Link to docs rather than pasting them inline
- Use `@docs/architecture.md` syntax for references
- Keep detailed style guides in separate files
- AGENTS.md should be the map, not the territory

### Separation of Concerns
- Each file has one job, stays focused
- Can be updated without touching everything else
- When coding standards change, edit separate docs file
- AGENTS.md doesn't need a PR for style guide updates

### Optimal Structure
- Root AGENTS.md: 100-200 lines covering essentials
- Detailed docs in separate files referenced by AGENTS.md
- Nested AGENTS.md files for subdirectories: 30-80 lines each
- Total documentation can be same size, but properly separated

### Best Practice Summary
- Keep AGENTS.md under 150 lines
- Link to extended documentation
- Focus on hard rules and essential commands
- Move code examples, detailed style guides to separate files
- Progressive disclosure: essentials in AGENTS.md, details in referenced docs
