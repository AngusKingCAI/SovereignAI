# SovereignAI Project Structure Index

**Purpose**: Current project structure verification and single source of truth for file locations  
**Created**: 2026-07-23  
**Last Updated**: 2026-07-23 20:30 (MYT)  
**Status**: Active

## Section Index

| Section | Line |
|---------|------|
| Project Overview | 64 |
| Directory Structure | 67 |
| IDE Agent Structure | 85 |
| Rules Structure | 91 |
| Workflows Structure | 105 |
| Skills Structure | 115 |
| Application Structure | 126 |
| Logging Structure | 142 |
| Scripts Structure | 149 |
| Governance Framework | 165 |
| Key Integration Points | 187 |
| Version Status | 194 |

## File Location Index

| File Type | Location | Line |
|-----------|----------|------|
| AGENTS.md (root) | AGENTS.md | 30 |
| Global Rules | Rules/Global/RULES.md | 57 |
| Planner Rules | Rules/Planner/Rules.md | 58 |
| Executor Rules | Rules/Executor/Rules.md | 59 |
| Reviewer Rules | Rules/Reviewer/Rules.md | 60 |
| Researcher Rules | Rules/Researcher/Rules.md | 61 |
| Planner Workflow | Workflows/Planner/Plan.md | 71 |
| Executor Workflow | Workflows/Executor/Execute.md | 72 |
| Reviewer Workflow | Workflows/Reviewer/Review.md | 73 |
| Researcher Workflow | Workflows/Researcher/Research.md | 74 |
| Devin Governance Workflow | Workflows/Devin/Devin.md | 75 |
| Shared Principles | Shared/PRINCIPLES.md | 32 |
| Shared Landmines | Shared/LANDMINES.md | 33 |
| Planner AGENTS.md | .Agents/Planner/AGENTS.md | 79 |
| Executor AGENTS.md | .Agents/Executor/AGENTS.md | 80 |
| Reviewer AGENTS.md | .Agents/Reviewer/AGENTS.md | 81 |
| Researcher AGENTS.md | .Agents/Researcher/AGENTS.md | 82 |
| Session Logging Skill | .devin/skills/session-logging/SKILL.md | 113 |
| Quality Check Skill | .devin/skills/quality-check/SKILL.md | 114 |
| Web Verify Skill | .devin/skills/web-verify/SKILL.md | 115 |
| Log Action Skill | .devin/skills/log-action/SKILL.md | 116 |
| Session Summary Skill | .devin/skills/session-summary/SKILL.md | 120 |
| Devin Workflow Skill | .devin/skills/devin-workflow/SKILL.md | 124 |
| Workflow Executor Script | Scripts/Devin/workflow_executor.ps1 | 144 |
| State Manager Script | Scripts/Devin/state_manager.ps1 | 145 |
| Step Validators | Scripts/Devin/step_validators/*.ps1 | 146 |
| Log Format Verification | Scripts/Logging/verify_log_format.ps1 | 147 |
| UTF-8 Encoding Verification | Scripts/Logging/verify_utf8_encoding.ps1 | 148 |
| Schema Compliance Verification | Scripts/Logging/verify_schema_compliance.ps1 | 149 |
| Attestation Hash Verification | Scripts/Logging/verify_attestation_hash.ps1 | 150 |
| Executor Workflow Verification | Scripts/Executor/verify_executor_workflow.py | 151 |
| Planner Workflow Verification | Scripts/Planner/verify_planner_workflow.py | 152 |
| Researcher Workflow Verification | Scripts/Researcher/verify_researcher_workflow.py | 153 |
| Reviewer Workflow Verification | Scripts/Reviewer/verify_reviewer_workflow.py | 154 |
| Shared Agent Logger | Scripts/Shared/agent_logger.py | 155 |
| Shared Conversation Log | Scripts/Shared/populate_conversation_log.py | 156 |
| Shared Logger Test | Scripts/Shared/test_logger_read.py | 157 |

## Project Overview
SovereignAI is a modular AI system with local-first architecture, pluggable components, and clear separation between IDE agents (Planner/Executor/Reviewer/Researcher) and SovereignAI application agents.

## Directory Structure

### Root Level
- `AGENTS.md` - IDE agent instructions for workflow coordination
- `Shared/` - Shared governance documents
  - `PRINCIPLES.md` - Project principles (P1-P15)
  - `LANDMINES.md` - Known blocking issues and constraints
- `App/` - SovereignAI application agents and components
- `.Agents/` - IDE agent governance (Planner, Executor, Reviewer, Researcher)
- `.devin/` - Devin CLI configuration and skills
- `Plans/` - Workflow plans with Executor Manifests
- `Logs/` - Structured logging per agent type
- `Scripts/` - Hard gate scripts and tooling
- `Workflows/` - Workflow definitions
- `Rules/` - Rules (Global and agent-specific)
- `INDEX.md` - This file - current project structure and file locations
- `log.txt` - Previous conversation log (archived for decision extraction)

### IDE Agent Structure (.Agents/)
- `.Agents/Planner/AGENTS.md` - Planner agent governance
- `.Agents/Executor/AGENTS.md` - Executor agent governance  
- `.Agents/Reviewer/AGENTS.md` - Reviewer agent governance
- `.Agents/Researcher/AGENTS.md` - Researcher agent governance

### Rules Structure (Rules/)
- `Rules/Global/RULES.md` - Global rules (GR1-GR33) - apply to all agents
- `Rules/Planner/Rules.md` - Planner-specific rules (PR1-PR9)
- `Rules/Executor/Rules.md` - Executor-specific rules (ER1-ER*)
- `Rules/Reviewer/Rules.md` - Reviewer-specific rules (RR1-RR*)
- `Rules/Researcher/Rules.md` - Researcher-specific rules (RS1-RS*)

**Rule Prefix Mapping**:
- GR (Global): Rules/Global/RULES.md - universal operational rules
- PR (Planner): Rules/Planner/Rules.md - planning behavior rules
- ER (Executor): Rules/Executor/Rules.md - execution behavior rules
- RR (Reviewer): Rules/Reviewer/Rules.md - review behavior rules
- RS (Researcher): Rules/Researcher/Rules.md - research behavior rules

### Workflows Structure (Workflows/)
- `Workflows/Planner/Plan.md` - Planner workflow (plan creation and Round Table review)
- `Workflows/Executor/Execute.md` - Executor workflow (plan execution)
- `Workflows/Reviewer/Review.md` - Reviewer workflow (implementation review)
- `Workflows/Researcher/Research.md` - Researcher workflow (external research)
- `Workflows/Devin/Devin.md` - Devin governance workflow (governance modifications and new functionality)

### Skills Structure (.devin/skills/)
- `.devin/skills/planner/SKILL.md` - Planner workflow skill
- `.devin/skills/executor/SKILL.md` - Executor workflow skill
- `.devin/skills/reviewer/SKILL.md` - Reviewer workflow skill
- `.devin/skills/researcher/SKILL.md` - Researcher workflow skill
- `.devin/skills/session-logging/SKILL.md` - Real-time logging with UTF-8 encoding (GR24/GR25)
- `.devin/skills/quality-check/SKILL.md` - Q/TC/E decision framework (GR29)
- `.devin/skills/web-verify/SKILL.md` - Web search verification (GR8)
- `.devin/skills/gitpush/SKILL.md` - Git push with tagging skill
- `.devin/skills/log-action/SKILL.md` - Log individual agent actions to JSONL format
- `.devin/skills/log-action/scripts/log_action.ps1` - PowerShell script for JSONL logging
- `.devin/skills/log-action/references/LOG_SCHEMA.md` - Log schema documentation
- `.devin/skills/session-summary/SKILL.md` - Generate session completion logging and attestation
- `.devin/skills/session-summary/scripts/session_summary.ps1` - PowerShell script for session summary logging
- `.devin/skills/session-summary/references/SESSION_SCHEMA.md` - Session summary schema documentation
- `.devin/skills/devin-workflow/SKILL.md` - Execute Devin Governance Workflow with hard gate enforcement

### Application Structure (App/)
- `App/sovereignai/` - Core SovereignAI application logic
  - `agent/` - Agent configuration and factory
  - `memory/` - Memory backends (episodic, procedural, trace, working, graph)
  - `messaging/` - Message bus and adapters
  - `managers/` - Component managers
  - `lifecycle/` - Lifecycle management
  - `conformance/` - Conformance checking
  - `indexing/` - Symbol indexing
  - `librarian/` - Librarian component
- `App/adapters/` - External adapters (llama_cpp, ollama)
- `App/adapters/internal/` - Internal memory adapters
- `App/services/` - Service providers (ollama_service)
- `App/skills/` - Application skills (official, user)
- `App/databases/` - Database providers (hf_database)

### Logging Structure (Logs/)
- `Logs/devin/` - Devin CLI session logs
- `Logs/planner/` - Planner agent logs
- `Logs/executor/` - Executor agent logs
- `Logs/reviewer/` - Reviewer agent logs
- `Logs/researcher/` - Researcher agent logs

### Scripts Structure (Scripts/)
- `Scripts/Devin/workflow_executor.ps1` - Master controller for Devin Governance Workflow execution
- `Scripts/Devin/state_manager.ps1` - State file operations for workflow tracking
- `Scripts/Devin/step_validators/` - Individual step validators (validate_step0_scope.ps1 through validate_step11_index.ps1)
- `Scripts/Logging/verify_log_format.ps1` - Verify JSONL log file format and required fields
- `Scripts/Logging/verify_utf8_encoding.ps1` - Verify UTF-8 encoding compliance for log files
- `Scripts/Logging/verify_schema_compliance.ps1` - Verify log schema compliance (timestamp, agent type, action type, result, compliance status, attestation hash format)
- `Scripts/Logging/verify_attestation_hash.ps1` - Verify attestation hash generation for tamper-evidence
- `Scripts/Executor/verify_executor_workflow.py` - Executor workflow verification script
- `Scripts/Planner/verify_planner_workflow.py` - Planner workflow verification script
- `Scripts/Researcher/verify_researcher_workflow.py` - Researcher workflow verification script
- `Scripts/Reviewer/verify_reviewer_workflow.py` - Reviewer workflow verification script
- `Scripts/Shared/agent_logger.py` - Shared agent logging functionality
- `Scripts/Shared/populate_conversation_log.py` - Conversation log population utility
- `Scripts/Shared/test_logger_read.py` - Logger read testing utility

## Governance Framework

### Principles (Shared/PRINCIPLES.md)
- P1-P14: Core principles (sacred core, pluggable, local-first, etc.)
- P15: Quality > Token Cost > Efficiency (with rating system: 1-10 ratings, total score (X+Y+Z)/30)

### Global Rules (Rules/Global/RULES.md)
- GR1-GR3: Structural rules (file format, workflow, folders)
- GR31: Test-first implementation rule
- GR32: Three-failure web search rule
- GR33: New functionality architecture preservation rule
- GR4-GR9: IDE agent coordination rules
- GR10-GR15: Workflow best practices
- GR16-GR21: Rule file quality criteria
- GR22-GR29: Operational rules (uncertainty handling, logging, tool usage, file locations, SSOT, Q/TC/E)

### Hard Gate Enforcement System
- **Scripts/Devin/workflow_executor.ps1** - Master controller for Devin Governance Workflow execution
- **Scripts/Devin/state_manager.ps1** - State file operations for workflow tracking
- **Scripts/Devin/step_validators/** - Individual step validators (validate_step0_scope.ps1 through validate_step11_index.ps1)
- **Exit Code Enforcement**: 0 = PASS, ≠0 = FAIL for hard gate compliance
- **State Tracking**: JSON-based workflow state file with attestation hashes
- **Modification Order**: AGENTS.md → Rules → Workflows → Scripts → Skills → INDEX.md

## Key Integration Points
- IDE agents coordinate workflow via skills
- SovereignAI agents perform actual application work
- File-based state coordination between sessions
- Governance enforced via GR rules and P principles
- Logging follows action-focused approach per GR23 (Quality 9, Cost 9, Efficiency 9 = 27/30)

## Version Status
- Current structure validated: 2026-07-23 20:30 (MYT)
- GR30 compliance fixed: Scripts directory case consistency (Devin, Executor, Logging, Planner, Researcher, Reviewer, Shared)
- Hard gate enforcement system implemented: Scripts/Devin/ with workflow executor, state manager, and step validators
- Devin workflow execution skill created: .devin/skills/devin-workflow/ with hard gate enforcement orchestration
- SSOT compliance: Removed undocumented Scripts/Devin/run_workflow.ps1 and corrected devin-workflow skill documentation
- Skill-based logging system implemented: log-action and session-summary skills (from previous session)
- Verification scripts created: Log format, UTF-8 encoding, schema compliance, attestation hash verification (from previous session)
- Agent workflow verification scripts documented: Executor, Planner, Researcher, Reviewer (from previous session)
- Shared logging utilities documented: agent_logger.py, populate_conversation_log.py, test_logger_read.py (from previous session)
- Planner workflow updated: Version 1.5 → 1.6 with logging skill integration (from previous session)
- Governance optimization completed: AGENTS.md 1.5, Rules 1.21 (GR33 added), Devin workflow 1.2 (Step 0.5 added for architecture preservation)
- Planner governance updated: AGENTS.md, Rules 1.4 (PR10 added), Workflow 1.7 (GR1-GR33, PR1-PR10, procedural skills, Step 1.5 added)
- Planner skill fixed: Session management moved from .Planner/ to Logs/Planner/ per GR3 compliance
- Gate enforcement enhanced: Planner workflow 1.8 with intermediate sequence gates, verification script 1.1 with --step-seq parameter