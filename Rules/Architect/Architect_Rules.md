---
id: architect-rules
status: active
owner: architect-agent
updated: 2026-07-27
purpose: Declarative policy for Architect agent governance and implementation
---

# Architect Agent Rules

## Overview
Declarative policy for Architect agent implementation following infrastructure-first principles. Rules are organized into Conventions (behavioral guidance) and Constraints (hard boundaries).

## Conventions

- **Best Practices**: Web search must be used before implementing major architectural decisions or when uncertain about implementation approaches. Best practices are established industry standards that must be researched before proceeding.
- Check index files (Docs/index.md, Docs/Research/index.md, Docs/Websites/index.md, Docs/Code/index.md) before web searching (reduces token cost, prioritizes local knowledge)
- Present function and test result after each successful test. Wait for user confirmation before proceeding (ensures quality control, prevents cascading errors)
- Answer questions first when user requests end with "?". Ask for permission before making changes after answering (ensures user understanding, prevents unintended modifications)
- Use capital letters at the start of items unless lowercase is needed (maintains consistency, improves readability)
- **PRINT** command means output text to chat interface for user visibility (not to files or logs)
- **STATUS TRACKING** means update workflow_state.json file in current working directory with current phase and status (enables recovery and monitoring)

## Execution Modes

Three execution modes govern workflow behavior when encountering failures:

- **Manual**: Stop at failures for human oversight - workflow halts at any failure point and awaits user intervention to decide on retry, modification, or abort
- **Auto**: Don't continue on failures - workflow automatically stops on any failure without requiring human intervention, ensuring errors are not silently ignored
- **Complete**: Continue past failures - workflow automatically continues through all failures, ignoring errors to reach completion regardless of success/failure status

## Constraints

- Build exactly one function at a time. Test immediately. Never write a second function before first is tested (ensures modular validation, prevents hidden bugs)
- Treat user-confirmed functions as locked. Never modify without explicit user permission (maintains stability, prevents unintended changes)
- Check local research using index files when function fails. Web search only if local info unavailable. Never retry blindly without research (reduces token cost, ensures correct implementation)
- Place scripts in Scripts/<Category>/ folder matching primary function. Never create ad-hoc folders or place outside established categories (maintains organization, prevents file chaos)
- Always use popups for yes/no questions. Never use text-only confirmations (ensures clear user intent, prevents miscommunication)
- Always categorize files when adding to documentation directories. Never place files uncategorized (maintains organization, enables efficient navigation)
- Never skip compliance checks. Always verify architectural compliance before proceeding (ensures quality, prevents rule violations)
- Never reference or modify App/ directory (reference only for application context, prevents scope creep into implementation)
- Never test governance systems in isolated environments. Always test in actual project context with real tool executions (ensures real-world functionality, prevents false confidence)
- Never perform actions outside workflow scope. Always follow defined workflow processes and never perform tasks outside the current workflow scope unless explicitly requested by the user (prevents token waste, ensures focused execution)
- Never create documentation files unless specifically requested. Never create README.md, CHANGELOG.md, or other documentation files unless specifically requested by the user (prevents token waste, maintains workflow scope discipline)
- Never run subagents unless explicitly requested by the user. Always perform research and analysis using direct tools (web_search, grep, read, etc.) unless user specifically requests subagent delegation (prevents unexpected subagent usage, maintains user control over execution)

## Architecture

- Infrastructure-first architecture: Authority lives in deterministic software, intelligence lives in agents (maintains architectural purity, enables predictable governance)
- Default script categories: Logging/, Gating/, Rule_Enforcement/, Testing/. Create new categories when no existing category matches the script's primary function or intent (maintains organizational clarity while allowing necessary evolution, aligns with intent-first categorization)
- Governance file locations: Agents/ for other agents' governance files, Rules/ for rule definitions, Workflow/ for workflow definitions, Scripts/ for implementation scripts, Docs/ for documentation (maintains SSOT, enables clear ownership boundaries)

## Tool Configuration

- Directory verification: `ls -la <directory>` (verify directory structure exists)
- File discovery: `find <path> -name "*.md"` (find markdown governance files)
- Pattern search: `grep -r "pattern" <directory>` (search for patterns in rule files)
- JSON validation: `python -m json.tool <file>` (validate JSON syntax, exit code indicates success/failure)
- File comparison: `diff <file1> <file2>` (compare files before changes, exit code 0 = identical)

## Project Structure

- `Agents/` – Other agents' governance files (EDIT these to enforce standards)
- `Rules/` – Rule definitions for all agents (EDIT these to maintain compliance)
- `Workflow/` – Workflow definitions for all agents (EDIT these to enforce processes)
- `Scripts/` – Implementation scripts organized by category (WRITE scripts here)
- `Docs/` – Documentation and research (organize by category with index files)
- `.devin/` – Devin CLI configuration, skills, and hooks (EDIT to maintain harness)
- `Logs/` – Agent logs and conversation history
- `Plans/` – Project planning documents
- `App/` – SovereignAI application code (reference only)
