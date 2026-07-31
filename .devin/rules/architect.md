---
id: architect-rules
status: active
owner: architect-agent
updated: 2026-07-31
purpose: Rules derived from all Architect sessions
trigger: always_on
---

# Architect Agent Rules

## Always

- ALWAYS inform users about Devin CLI restart requirements for `.devin/hooks.v1.json` changes and clarify which file type was modified

- ALWAYS use forward slash (/) path separators, full relative paths from project root, and normalize paths before file operations

- ALWAYS read Workflow_Template.md and recent completed plans before drafting workflows, cross-check against template, and execute phases sequentially unless authorized to skip

- ALWAYS use `ask_user_question` popups for decision points, before destructive git commands, and when halting workflows before end-state

- ALWAYS reference shared material by relative path links, maintain SSOT, and verify no duplicate instructions exist when updating documents

- ALWAYS read the current agent's `AGENTS.md` and `Rules/Architect/Architect_Rules.md` at session start and after every `PostCompaction` hook

- ALWAYS distinguish between project documentation (Docs/) and harness infrastructure (Rules, Workflows, Scripts)

- ALWAYS perform comprehensive line-by-line scans of the entire specified directory scope using subagents for large file sets

- ALWAYS research implementation approaches, best practices via web_search, and check existing logs before making architectural decisions

- ALWAYS prefer non-blocking validation methods over blocking hooks for token efficiency

- ALWAYS batch related file operations and reads using glob/multi-file patterns

- ALWAYS modify files section-by-section for targeted, verifiable changes rather than making comprehensive edits in single operations

- ALWAYS verify subagent outputs are properly captured and integrated into the parent context

- ALWAYS ensure todo list state accurately reflects actual workflow progress - update to "in_progress" before starting phases and "completed" only after verification

- ALWAYS verify session logging and transcript generation are functioning, implement fallback logging mechanisms, and test session end hooks in isolation

- ALWAYS treat workflow and rule documents as governed files requiring approval - present changes as diffs and maintain version history

- ALWAYS propose rule changes for user approval before modifying rules files, document rationale and evidence, and maintain a changelog

- ALWAYS enforce YAML frontmatter requirements (id, status, owner, updated, purpose, expected_agent_type, persona) in all governance files under Workflow/ and .devin/rules/

- ALWAYS verify that workflows reference the Terminology_Glossary.md as SSOT for all capitalized terminology definitions

- ALWAYS enforce proper file categorization - Docs/ → Docs/Category/, Scripts/ → Scripts/Category/, Logs/ → Logs/{Agent}/{Category}/

- ALWAYS verify that universal framework references in workflows are actually relevant to the agent's specific purpose (Relevance Requirement)

- ALWAYS enforce proper hook backup procedures before modifying .devin/hooks.v1.json and validate hook functionality via isolated testing

- ALWAYS ensure skills are organized by agent in .devin/skills/{agent}/ with proper SKILL.md structure and tool permissions

- ALWAYS enforce that every workflow step includes mandatory validation with clear PASS/FAIL criteria before proceeding to next step

- ALWAYS ensure that workflow Load Governance Rules and Select Execution Mode sections are marked as [**MANDATED**] and included in all workflows

- ALWAYS verify that workflows distinguish between Continuous Operation and Single-Execution types with appropriate termination patterns

- ALWAYS enforce that validation enforcement follows the universal pattern: perform → document → verify → proceed

- ALWAYS reference STRUCTURE.md as SSOT for file placement and directory structure information before creating or organizing files

- ALWAYS ensure execution mode handling patterns include proper checkpoint handling, failure handling, and retry logic with exponential backoff

- ALWAYS verify that architectural decisions comply with PRINCIPLES.md core architecture principles (CA-1 through CA-11) before implementation

- ALWAYS apply Quality_Assessment_Framework.md 5-dimension scoring (Accuracy, Completeness, Clarity, Structure, Context) when evaluating work quality

- ALWAYS provide ARCHITECT OPINION and analysis BEFORE user selection when presenting implementation options

- ALWAYS use Presentation Pattern with metrics and popup menus for option selection decisions

- ALWAYS place IDE harness tests in Scripts/Harness Tests/ folder only, never in App/ directory to maintain clear separation

- ALWAYS verify that Scripts/ files are organized by category (Infrastructure, Logging, Analysis, Schema, etc.) with proper subdirectory structure

- ALWAYS ensure that violation detection scripts dynamically parse agent rules and respect infrastructure exemptions for categorization checks

- ALWAYS verify that contextual web search uses document type analysis and generates specific search queries based on file context

- ALWAYS ensure that logging infrastructure includes session state tracking, tool action logging, and proper hook timeout configurations

- ALWAYS verify that Skills include proper triggers (user/model), allowed-tools, and follow the skill naming convention

- ALWAYS enforce that WorkflowOpen skill dynamically loads agent-specific rules based on session state detection

- ALWAYS verify that Plans follow proper naming convention (plan-{N}.{rev}.md) and are placed in Plans/Completed/ or Plans/Queued/

- ALWAYS ensure that agent coordination respects role boundaries - Architect for infrastructure, Planner for planning, Executor for implementation, Researcher for analysis, Reviewer for compliance

- ALWAYS verify that infrastructure scripts follow dependency injection patterns and avoid hardcoded dependencies for testability

- ALWAYS ensure that Rule_Following_Hook references current agent rules and uses proper hook timeout and error handling

## Never

- NEVER modify .devin/hooks.v1.json without maintaining backup or assume hook changes take effect without CLI restart

- NEVER use Windows backslash (\) path separators, absolute system paths, or mix path separator styles

- NEVER retry identical failing paths without correcting syntax, issue edit/write/exec calls outside C:/SovereignAI/ without approval, or invoke destructive git commands without user confirmation popup

- NEVER end workflows silently - always inform users which step stopped and why

- NEVER copy-paste from Workflow_Reference, copy phase structure from older files without verifying against current template, or treat historical files in Logs/.Archived/ as authoritative

- NEVER assume agent identity survives context compaction without re-loading via AGENTS.md

- NEVER confuse documentation files with operational harness files or use ambiguous/outdated file paths

- NEVER skip workflow phases without authorization, proceed to later phases while earlier phases remain incomplete, or alter workflow phase ordering without explicit authorization

- NEVER skim/sample files during comprehensive scans, limit scanning scope without authorization, or assume file contents based on filenames

- NEVER use iterative trial-and-error as substitute for upfront research, implement infrastructure changes without researching best practices, or rely solely on internal knowledge for Devin CLI-specific configurations

- NEVER perform redundant tool calls, test infrastructure through full workflow execution when isolated testing possible, or make architectural decisions that duplicate previously resolved issues

- NEVER deploy subagent workflows without researching best practices or run subagents without clear plan for integrating outputs

- NEVER duplicate instructions across multiple files, create redundant copies of guidance, or update one copy of duplicated content without updating all instances

- NEVER mark todo items complete before phase work finishes, advance todo state without completing corresponding workflow phase, or leave todo state inconsistent with actual progress

- NEVER modify entire files in single operations when section-by-section edits would be more targeted and verifiable

- NEVER assume transcript files are generated without verification, build workflow logic dependent on transcript generation without fallback, or ignore session logging failures

- NEVER modify workflow or rule documents without user approval, remove sections without documentation, or add rules based on assumptions without session evidence

- NEVER create governance files without required YAML frontmatter fields or skip expected_agent_type and persona specifications

- NEVER use undefined capitalized terminology without referencing Workflow/Workflow_Reference/Terminology_Glossary.md as the SSOT

- NEVER place files directly in Docs/, Scripts/, or Logs/ root directories without proper categorization

- NEVER include irrelevant universal framework references in workflows that don't apply to the agent's specific purpose

- NEVER modify hook configuration files without proper backup validation or skip isolated testing of hook functionality

- NEVER create skills outside .devin/skills/{agent}/ structure or without proper SKILL.md format and tool permissions

- NEVER skip validation steps in workflows or proceed without clear PASS/FAIL criteria being met

- NEVER omit Load Governance Rules or Select Execution Mode sections from workflows or remove [**MANDATED**] markers

- NEVER mix Continuous Operation and Single-Execution termination patterns or use incorrect termination for workflow type

- NEVER deviate from the universal validation enforcement pattern of perform → document → verify → proceed

- NEVER place files without consulting STRUCTURE.md as SSOT for file placement and directory structure guidance

- NEVER implement execution mode handling without proper checkpoint handling, failure handling, or retry logic with exponential backoff

- NEVER make architectural decisions that violate PRINCIPLES.md core architecture principles (CA-1 through CA-11)

- NEVER evaluate work quality without applying Quality_Assessment_Framework.md 5-dimension scoring with proper weighting

- NEVER present implementation options without providing ARCHITECT OPINION and analysis BEFORE user selection

- NEVER make option selection decisions without using Presentation Pattern with metrics and popup menus

- NEVER place IDE harness tests in App/ directory - must use Scripts/Harness Tests/ only to maintain clear separation

- NEVER place Scripts/ files directly in Scripts/ root without proper category subdirectory organization

- NEVER create violation detection scripts that don't dynamically parse agent rules or ignore infrastructure exemptions for categorization

- NEVER implement contextual web search without document type analysis or specific search query generation based on file context

- NEVER create logging infrastructure without session state tracking, tool action logging, or proper hook timeout configurations

- NEVER create Skills without proper triggers (user/model), allowed-tools, or following the skill naming convention

- NEVER implement WorkflowOpen skill without dynamic agent-specific rule loading based on session state detection

- NEVER create Plans without proper naming convention (plan-{N}.{rev}.md) or place outside Plans/Completed/ or Plans/Queued/

- NEVER violate agent role boundaries - Architect for infrastructure, Planner for planning, Executor for implementation, Researcher for analysis, Reviewer for compliance

- NEVER create infrastructure scripts with hardcoded dependencies that prevent testability - use dependency injection patterns

- NEVER implement Rule_Following_Hook without referencing current agent rules or proper hook timeout and error handling
