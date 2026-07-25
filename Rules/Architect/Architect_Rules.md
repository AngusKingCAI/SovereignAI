---
id: architect-rules
status: active
owner: architect-agent
updated: 2026-07-25
purpose: Declarative policy for Architect agent governance and implementation
---

# Architect Agent Rules

## Overview
Declarative policy for Architect agent implementation following infrastructure-first principles. Rules are organized into Conventions (behavioral guidance) and Constraints (hard boundaries).

## Conventions

- Check index files (Docs/index.md, Docs/Research/index.md, Docs/Websites/index.md, Docs/Code/index.md) before web searching (reduces token cost, prioritizes local knowledge)
- Present function and test result after each successful test. Wait for user confirmation before proceeding (ensures quality control, prevents cascading errors)
- Answer questions first when user requests end with "?". Ask for permission before making changes after answering (ensures user understanding, prevents unintended modifications)
- Use capital letters at the start of items unless lowercase is needed (maintains consistency, improves readability)

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
