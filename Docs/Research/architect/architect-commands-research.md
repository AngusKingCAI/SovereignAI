# Architect Agent Commands Section Best Practices Research

**Source:** Multiple web sources  
**Date:** 2026-07-25  
**Purpose:** Commands section best practices for AGENTS.md

## Key Best Practices from Research

### Command-First Instructions
- **Exact invocations, not descriptions** - Don't say "run tests", say `pytest -v --tb=short`
- **Specific flags and options** - Include all arguments, not just tool names
- **Answer the question:** "What command proves this was done correctly?"
- **Every instruction should be verifiable** via exit codes

### Format Requirements
- **Format:** "Purpose: `command` (explanation)"
- **Runnable command sequences** - Commands in exact order with exact flags
- **Task-organized sections** - Coding, review, release sections
- **Explicit "done" criteria** - Define completion via specific exit codes

### Anti-Patterns to Avoid
- ❌ Prose paragraphs and descriptions
- ❌ Ambiguous directives like "be careful"
- ❌ Generic tool names without flags
- ❌ Contradictory priorities without explicit ordering
- ❌ "I think I'm done" without verification

### GitHub Blog Template Example
```markdown
## Commands you can use
Build docs: `npm run docs:build` (checks for broken links)
Lint markdown: `npx markdownlint docs/` (validates your work)
```

### Best Practice Example from Addy Osmani
```markdown
## Commands

- Build: `npm run build`
- Lint: `npm run lint -- --fix`
- Test all: `npm test`
- Test single file: `npm test -- --testPathPattern=<filename>`
- Dev server: `npm run dev` (runs on port 3000)
- Type check: `npx tsc --noEmit`
```

### Architect Agent Specific Requirements
Based on research, Architect agent commands should:
1. Be specific to governance infrastructure tasks
2. Include verification commands for compliance
3. Support file operations for AGENTS.md, Rules/, Workflow/ editing
4. Include safety checks before modifications
5. Provide clear "done" criteria for each operation
