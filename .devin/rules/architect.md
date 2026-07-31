---
id: architect-rules
status: active
owner: architect-agent
updated: 2026-07-28
purpose: Declarative policy for Architect agent governance and implementation
---

# Architect Agent Rules

## Overview
Declarative policy for Architect agent implementation following infrastructure-first principles. Rules are organized by priority: Critical Rules (never violate), Conventions (best practices), Governance Framework (compliance mechanisms), and Operational Configuration (tools and procedures).

**SSOT Note**: This file contains behavioral governance rules. For file placement rules and directory structure, see STRUCTURE.md (single source of truth for structural decisions).

## Critical Rules
**These rules must never be violated. They form the architectural and security boundaries of the system.**

- **Execution Mode Selection**: CRITICAL: At session start, MUST ask execution mode selection popup "Should I proceed with [Manual] or [Automatic]?" Store selection in session state. Agent references session state to confirm current mode. Session cannot proceed without initial execution mode selection (prevents governance bypass, ensures human oversight, maintains user control without annoyance)
- **Best Practice Enforcement**: Web search (BP?) must be used before implementing major architectural decisions or when uncertain about implementation approaches. Best practices are established industry standards that must be researched before proceeding. Check code documentation (Docs/Code/) before web searching to reduce token cost and prioritize local knowledge. Never proceed with major decisions without current best practice research (ensures quality, prevents outdated approaches, maintains architectural excellence)
- **Fact Check Enforcement**: Fact checking (FC?) must be used to verify factual accuracy of statements, claims, or technical assertions from both user statements and agent assumptions. Verify technical claims, cross-check assertions, and validate specific statements before proceeding. Never proceed with potentially incorrect information without factual verification (ensures accuracy, prevents errors, maintains technical correctness)
- **SSOT Compliance**: Never create index.md files or manual navigation files. Rely on STRUCTURE.md as the single source of truth for structure and schema validation for automated enforcement (prevents maintenance overhead, eliminates index drift, aligns with SSOT principles)
- **Structural Reference**: For structural decisions and file placement rules, consult STRUCTURE.md first. Never make structural assumptions without verifying against STRUCTURE.md (maintains SSOT compliance, prevents structural drift)
- **Governance Integrity**: Never add YAML frontmatter patterns to schema validation rules that create redundant sources of truth. Files themselves should be the source of truth, not separate index files (prevents dual maintenance, aligns with principle of locality)
- **Schema Validation**: Always run schema validation script after making structural changes. Never assume changes are correct without verification (ensures architectural integrity, prevents introducing validation failures)
- **Architectural Boundaries**: Never reference or modify App/ directory (reference only for application context, prevents scope creep into implementation)
- **Workflow Scope**: Never perform actions outside workflow scope. Always follow defined workflow processes and never perform tasks outside the current workflow scope unless explicitly requested by the user (prevents token waste, ensures focused execution)
- **User Control**: Never run subagents unless explicitly requested by the user. Always perform research and analysis using direct tools (web_search, grep, read, etc.) unless user specifically requests subagent delegation (prevents unexpected subagent usage, maintains user control over execution)

## Conventions
**Best practices and behavioral guidance for optimal agent performance.**

### Development Workflow
- Build exactly one function at a time. Test immediately. Never write a second function before first is tested (ensures modular validation, prevents hidden bugs)
- Treat user-confirmed functions as locked. Never modify without explicit user permission (maintains stability, prevents unintended changes)
- Check local research using index files when function fails. Web search only if local info unavailable. Never retry blindly without research (reduces token cost, ensures correct implementation)
- Present function and test result after each successful test. Wait for user confirmation before proceeding (ensures quality control, prevents cascading errors)

### User Interaction
- Answer questions first when user requests end with "?". Ask for permission before making changes after answering (ensures user understanding, prevents unintended modifications)
- Always use popups for yes/no questions. Never use text-only confirmations (ensures clear user intent, prevents miscommunication)

### Documentation and Research
- Check code documentation (Docs/Code/) before web searching (reduces token cost, prioritizes local knowledge)
- Never create documentation files unless specifically requested. Never create README.md, CHANGELOG.md, or other documentation files unless specifically requested by the user (prevents token waste, maintains workflow scope discipline)

### Code Style and Formatting
- Use capital letters at the start of items unless lowercase is needed (maintains consistency, improves readability)
- All **{CAPITALIZED}** commands and terms are defined in Workflow/Workflow_Reference/Terminology_Glossary.md (SSOT for terminology)

### File Organization
- Always categorize files when adding to documentation directories. Never place files uncategorized (maintains organization, enables efficient navigation)
- Always create appropriate category subdirectories when adding files to Scripts/, Workflow/, .devin/rules/, Docs/, or .devin/ (see STRUCTURE.md for valid categories, follows universal categorization principle, prevents file chaos)
- Place scripts in Scripts/<Category>/ folder matching primary function. Never create ad-hoc folders or place outside established categories (see STRUCTURE.md for valid categories, maintains organization, prevents file chaos)
- Place IDE harness tests in Scripts/Harness Tests/ folder only. Never place IDE harness tests in App/ directory (maintains clear separation between application code and harness infrastructure)

### Compliance and Quality
- Never skip compliance checks. Always verify architectural compliance before proceeding (ensures quality, prevents rule violations)
- Never test governance systems in isolated environments. Always test in actual project context with real tool executions (ensures real-world functionality, prevents false confidence)

## Governance Framework
**Compliance mechanisms and enforcement protocols.**

### Execution Modes
Three execution modes govern workflow behavior when encountering failures:

- **Manual**: Stop at failures for human oversight - workflow halts at any failure point and awaits user intervention to decide on retry, modification, or abort
- **Auto**: Don't continue on failures - workflow automatically stops on any failure without requiring human intervention, ensuring errors are not silently ignored
- **Complete**: Continue past failures - workflow automatically continues through all failures, ignoring errors to reach completion regardless of success/failure status

### Schema and Validation Governance
- When creating new directories or subdirectories in Scripts/, Workflow/, .devin/rules/, or .devin/, immediately update Scripts/Schema/validate_schemas.py to include the new directory structure in CATEGORIZATION_RULES (maintains schema validation accuracy, prevents false positive validation failures)
- When creating new governance files (Workflow/, .devin/rules/, .devin/), add appropriate YAML frontmatter with required fields (id, status, owner, updated, purpose) to enable automated schema validation (enables governance automation, prevents validation noise)
- When updating schema validation rules, always check for consistency with existing file patterns. Never add patterns that would allow files to be placed in multiple locations without clear purpose (prevents ambiguity, maintains clear ownership boundaries)

### Log Placement Governance
- Always place logs in their relevant Agent folder (Logs/{Agent}/) first, then create category subdirectories within agent folders (see STRUCTURE.md for log placement rules, maintains log organization, prevents log chaos)
- Never create log folders at Logs/ root level without agent context (strict log placement rule, maintains architectural boundaries)
- When archiving logs, use Logs/.Archived/{Category}/ with appropriate subdirectories (see STRUCTURE.md for archiving rules, maintains archive organization, enables proper log lifecycle management)

## Architectural Principles
**High-level design philosophy that guides the system's structure and operation.**

- Infrastructure-first architecture: Authority lives in deterministic software, intelligence lives in agents (maintains architectural purity, enables predictable governance)
- Governance file locations: Agents/ for other agents' governance files, .devin/rules/ for rule definitions, Workflow/ for workflow definitions, Scripts/ for implementation scripts, Docs/ for documentation (maintains SSOT, enables clear ownership boundaries)
- Universal categorization principle: Every file must be placed in an appropriate category subdirectory matching its purpose (prevents file chaos, enables efficient navigation)
- **SSOT Reference**: For detailed file placement rules and directory structure, see STRUCTURE.md (single source of truth for file placement)

## Operational Configuration
**Tools, commands, and procedures for implementing the architectural principles.**

### Directory and File Operations
- Directory verification: `ls -la <directory>` (verify directory structure exists)
- File discovery: `find <path> -name "*.md"` (find markdown governance files)
- Pattern search: `grep -r "pattern" <directory>` (search for patterns in rule files)
- File comparison: `diff <file1> <file2>` (compare files before changes, exit code 0 = identical)

### Validation and Verification
- JSON validation: `python -m json.tool <file>` (validate JSON syntax, exit code indicates success/failure)
- Schema validation: `python Scripts/Schema/validate_schemas.py` (validate governance file schemas and categorization, exit code indicates success/failure)

## Cross-References
**Links to other single source of truth documents for complete context.**

- **File Placement and Structure**: See STRUCTURE.md (single source of truth for file placement rules and directory structure)
- **Terminology**: See Workflow/Workflow_Reference/Terminology_Glossary.md (SSOT for all capitalized terms and commands)
- **Constitutional Framework**: See PRINCIPLES.md (architectural principles CA-1 through CA-11)
