# Rules Formatting Specification

**Source:** GitHub - btakita/agent-rules  
**Date:** 2026-07-25  
**Purpose:** Format specification for prescribed policy in AI agent instruction files

## Key Findings

### File Locations
Rules live in instruction files for different tools:
- `CLAUDE.md` - Claude Code
- `AGENTS.md` - Codex, Claude Code
- `.cursorrules` - Cursor
- `.cursor/rules/*.mdc` - Cursor (scoped)
- `.windsurfrules` - Windsurf
- `.github/copilot-instructions.md` - GitHub Copilot
- `GEMINI.md` - Gemini CLI
- `CONVENTIONS.md` - Aider

### Recommended Sections
Organize rules into these sections:
- **Conventions** - Coding standards and patterns
- **Constraints** - Hard boundaries (Never/Always/Do not)
- **Architecture** - System design decisions with "why"
- **Tool Configuration** - How to invoke project tooling
- **Project Structure** - Brief layout reference

### Formatting Guidelines
- **Start each rule with imperative verb** (use, prefer, name, write, keep)
- **Constraints start with "Never", "Do not", or "Always"** to signal non-negotiable
- **Include the "why" in parentheses** for architecture decisions
- **Keep commands concrete** - reference runbooks for multi-step procedures
- **Only include paths that affect agent behavior** - not documentation

### Validation Rules
1. **Actionable content** - Every rule must contain imperative verb
2. **Line budget** - Stay under 1000 lines total
3. **No machine-local paths** - Must work across different machines
4. **No large code blocks** - Code over 10 lines belongs in external files
