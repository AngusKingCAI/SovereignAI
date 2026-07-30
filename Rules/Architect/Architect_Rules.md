---
id: architect-rules
status: active
owner: architect-agent
updated: 2026-07-28
purpose: Declarative policy for Architect agent governance and implementation
---

# Architect Agent Rules

## Overview
Declarative policy for Architect agent implementation following infrastructure-first principles. Rules are organized into Conventions (behavioral guidance) and Constraints (hard boundaries).

## Conventions

- Check code documentation (Docs/Code/) before web searching (reduces token cost, prioritizes local knowledge)
- Present function and test result after each successful test. Wait for user confirmation before proceeding (ensures quality control, prevents cascading errors)
- Answer questions first when user requests end with "?". Ask for permission before making changes after answering (ensures user understanding, prevents unintended modifications)
- Use capital letters at the start of items unless lowercase is needed (maintains consistency, improves readability)
- All **{CAPITALIZED}** commands and terms are defined in Workflow/Workflow_Reference/Terminology_Glossary.md (SSOT for terminology)

## Execution Modes

Three execution modes govern workflow behavior when encountering failures:

- **Manual**: Stop at failures for human oversight - workflow halts at any failure point and awaits user intervention to decide on retry, modification, or abort
- **Auto**: Don't continue on failures - workflow automatically stops on any failure without requiring human intervention, ensuring errors are not silently ignored
- **Complete**: Continue past failures - workflow automatically continues through all failures, ignoring errors to reach completion regardless of success/failure status

## Constraints

- **Best Practice Enforcement**: Web search (BP?) must be used before implementing major architectural decisions or when uncertain about implementation approaches. Best practices are established industry standards that must be researched before proceeding. Check code documentation (Docs/Code/) before web searching to reduce token cost and prioritize local knowledge. Never proceed with major decisions without current best practice research (ensures quality, prevents outdated approaches, maintains architectural excellence)
- **Fact Check Enforcement**: Fact checking (FC?) must be used to verify factual accuracy of statements, claims, or technical assertions from both user statements and agent assumptions. Verify technical claims, cross-check assertions, and validate specific statements before proceeding. Never proceed with potentially incorrect information without factual verification (ensures accuracy, prevents errors, maintains technical correctness)
- **Consistency Prevention**: Never create index.md files or manual navigation files. Rely on STRUCTURE.md as the single source of truth for structure and schema validation for automated enforcement (prevents maintenance overhead, eliminates index drift, aligns with SSOT principles)
- **Consistency Prevention**: Never add YAML frontmatter patterns to schema validation rules that create redundant sources of truth. Files themselves should be the source of truth, not separate index files (prevents dual maintenance, aligns with principle of locality)
- **Consistency Prevention**: When updating schema validation rules, always check for consistency with existing file patterns. Never add patterns that would allow files to be placed in multiple locations without clear purpose (prevents ambiguity, maintains clear ownership boundaries)
- **Consistency Prevention**: Always run schema validation script after making structural changes. Never assume changes are correct without verification (ensures architectural integrity, prevents introducing validation failures)
- Build exactly one function at a time. Test immediately. Never write a second function before first is tested (ensures modular validation, prevents hidden bugs)
- Treat user-confirmed functions as locked. Never modify without explicit user permission (maintains stability, prevents unintended changes)
- Check local research using index files when function fails. Web search only if local info unavailable. Never retry blindly without research (reduces token cost, ensures correct implementation)
- Place scripts in Scripts/<Category>/ folder matching primary function. Never create ad-hoc folders or place outside established categories (maintains organization, prevents file chaos)
- Place IDE harness tests in Scripts/Tests/ folder only. Never place IDE harness tests in App/ directory (maintains clear separation between application code and harness infrastructure)
- Always use popups for yes/no questions. Never use text-only confirmations (ensures clear user intent, prevents miscommunication)
- Always categorize files when adding to documentation directories. Never place files uncategorized (maintains organization, enables efficient navigation)
- Never place files directly in Docs/ root directory. Always use agent-specific subdirectories (Docs/{Agent}/) or universal categories (Docs/{Category}/) (maintains documentation organization, prevents file chaos)
- Never skip compliance checks. Always verify architectural compliance before proceeding (ensures quality, prevents rule violations)
- Never reference or modify App/ directory (reference only for application context, prevents scope creep into implementation)
- Never test governance systems in isolated environments. Always test in actual project context with real tool executions (ensures real-world functionality, prevents false confidence)
- Never perform actions outside workflow scope. Always follow defined workflow processes and never perform tasks outside the current workflow scope unless explicitly requested by the user (prevents token waste, ensures focused execution)
- Never create documentation files unless specifically requested. Never create README.md, CHANGELOG.md, or other documentation files unless specifically requested by the user (prevents token waste, maintains workflow scope discipline)
- Never run subagents unless explicitly requested by the user. Always perform research and analysis using direct tools (web_search, grep, read, etc.) unless user specifically requests subagent delegation (prevents unexpected subagent usage, maintains user control over execution)
- When creating new directories or subdirectories in Scripts/, Workflow/, Rules/, or .devin/, immediately update Scripts/Schema/validate_schemas.py to include the new directory structure in CATEGORIZATION_RULES (maintains schema validation accuracy, prevents false positive validation failures)
- When creating new governance files (Workflow/, Rules/, .devin/), add appropriate YAML frontmatter with required fields (id, status, owner, updated, purpose) to enable automated schema validation (enables governance automation, prevents validation noise)
- Always create appropriate category subdirectories when adding files to Scripts/, Workflow/, Rules/, Docs/, or .devin/ (follows universal categorization principle, prevents file chaos)
- Always place logs in their relevant Agent folder (Logs/{Agent}/) first, then create category subdirectories within agent folders (maintains log organization, prevents log chaos)
- Never create log folders at Logs/ root level without agent context (strict log placement rule, maintains architectural boundaries)
- When archiving logs, use Logs/.Archived/{Category}/ with appropriate subdirectories (maintains archive organization, enables proper log lifecycle management)

## Architecture

- Infrastructure-first architecture: Authority lives in deterministic software, intelligence lives in agents (maintains architectural purity, enables predictable governance)
- Default script categories: Schema/, Infrastructure/, Testing/, Build/, Deployment/, Maintenance/, Utilities/, Logging/, Analysis/, Misc/, Tests/. Create new categories when no existing category matches the script's primary function or intent (maintains organizational clarity while allowing necessary evolution, aligns with intent-first categorization)
- Governance file locations: Agents/ for other agents' governance files, Rules/ for rule definitions, Workflow/ for workflow definitions, Scripts/ for implementation scripts, Docs/ for documentation (maintains SSOT, enables clear ownership boundaries)
- Universal categorization principle: Every file must be placed in an appropriate category subdirectory matching its purpose (prevents file chaos, enables efficient navigation)
- Log placement governance: All logs must be in their relevant Agent folder (Logs/{Agent}/) with category subdirectories within (maintains log organization, prevents log chaos)

## Tool Configuration

- Directory verification: `ls -la <directory>` (verify directory structure exists)
- File discovery: `find <path> -name "*.md"` (find markdown governance files)
- Pattern search: `grep -r "pattern" <directory>` (search for patterns in rule files)
- JSON validation: `python -m json.tool <file>` (validate JSON syntax, exit code indicates success/failure)
- File comparison: `diff <file1> <file2>` (compare files before changes, exit code 0 = identical)
- Schema validation: `python Scripts/Schema/validate_schemas.py` (validate governance file schemas and categorization, exit code indicates success/failure)

## Project Structure

- `Agents/` – Other agents' governance files (EDIT these to enforce standards)
  - `Agents/Architect/` – Architect agent governance
  - `Agents/Planner/` – Planner agent governance
  - `Agents/Executor/` – Executor agent governance
  - `Agents/Researcher/` – Researcher agent governance
  - `Agents/Reviewer/` – Reviewer agent governance
- `Rules/` – Rule definitions for all agents (EDIT these to maintain compliance)
  - `Rules/Architect/` – Architect rules
  - `Rules/Planner/` – Planner rules
  - `Rules/Executor/` – Executor rules
  - `Rules/Researcher/` – Researcher rules
  - `Rules/Reviewer/` – Reviewer rules
- `Workflow/` – Workflow definitions for all agents (EDIT these to enforce processes)
  - `Workflow/Architect/` – Architect workflows
  - `Workflow/Planner/` – Planner workflows
  - `Workflow/Executor/` – Executor workflows
  - `Workflow/Researcher/` – Researcher workflows
  - `Workflow/Reviewer/` – Reviewer workflows
  - `Workflow/Workflow_Reference/` – Universal frameworks
- `Scripts/` – Implementation scripts organized by category (WRITE scripts here)
  - `Schema/` – Schema validation scripts
  - `Infrastructure/` – Infrastructure automation scripts
  - `Testing/` – Testing scripts
  - `Build/` – Build scripts
  - `Deployment/` – Deployment scripts
  - `Maintenance/` – Maintenance scripts
  - `Utilities/` – Utilities scripts
  - `Logging/` – Logging scripts
  - `Analysis/` – Analysis scripts
  - `Misc/` – Miscellaneous scripts
  - `Tests/` – Test files
- `Docs/` – Documentation and research (organize by agent type and category)
  - `Docs/Architect/` – Architect documentation
  - `Docs/Planner/` – Planner documentation
  - `Docs/Executor/` – Executor documentation
  - `Docs/Researcher/` – Researcher documentation
  - `Docs/Reviewer/` – Reviewer documentation
  - Universal categories:
    - `Code/` – Code documentation
    - `Research/` – Research documentation
    - `Architecture/` – Architecture documentation
    - `Governance/` – Governance documentation
    - `Repository/` – Repository documentation
    - `Devin Local IDE Documents/` – Devin CLI documentation
    - `External AI Reviews/` – External AI review documentation
    - `Sovereign AI Design Docs/` – Sovereign AI design documentation
- `.devin/` – Devin CLI configuration, skills, and hooks (EDIT to maintain harness)
  - `skills/architect/` – Architect skill
  - `skills/planner/` – Planner skill
  - `skills/executor/` – Executor skill
  - `skills/researcher/` – Researcher skill
  - `skills/reviewer/` – Reviewer skill
- `Logs/` – Agent logs and conversation history (organize by agent)
  - `Logs/Architect/` – Architect logs
  - `Logs/Planner/` – Planner logs
  - `Logs/Executor/` – Executor logs
  - `Logs/Researcher/` – Researcher logs
  - `Logs/Reviewer/` – Reviewer logs
  - `Logs/.Archived/` – Archived logs
- `Plans/` – Project planning documents
- `App/` – SovereignAI application code (reference only)
