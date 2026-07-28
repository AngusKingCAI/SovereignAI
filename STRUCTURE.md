# SovereignAI File Structure

**Root-Level File Placement Reference**

## Core Rule
**STRICT PROHIBITION**: No files may be added to root directory without explicit user approval.

## Agent Types
The SovereignAI system uses 5 core agent types:
- **Architect** - System-level designer and infrastructure architect
- **Planner** - Planning and task coordination agent
- **Executor** - Implementation and execution agent
- **Researcher** - Research and analysis agent
- **Reviewer** - Review and compliance checking agent

---

## File Placement Rules

### Root Directory (Current Approved Files)
✅ `AGENTS.md` - Main agent configuration  
✅ `PRINCIPLES.md` - Constitutional framework  
✅ `INDEX.md` - Repository index  
✅ `STRUCTURE.md` - This file (file placement reference)

### Scripts → Scripts/
- All implementation scripts organized by category
- Schema validation scripts → `Scripts/Schema/`
- Infrastructure automation scripts → `Scripts/Infrastructure/`
- Testing scripts → `Scripts/Testing/`
- Build scripts → `Scripts/Build/`
- Deployment scripts → `Scripts/Deployment/`
- Maintenance scripts → `Scripts/Maintenance/`
- Utilities scripts → `Scripts/Utilities/`
- Logging scripts → `Scripts/Logging/`
- Analysis scripts → `Scripts/Analysis/`
- Misc scripts → `Scripts/Misc/`
- Tests → `Scripts/Tests/`
- **Rule**: Always create appropriate category subdirectory when adding new scripts

### Workflows → Workflow/
- Universal frameworks → `Workflow/Workflow_Reference/`
- Architect workflows → `Workflow/Architect/`
- Planner workflows → `Workflow/Planner/`
- Executor workflows → `Workflow/Executor/`
- Researcher workflows → `Workflow/Researcher/`
- Reviewer workflows → `Workflow/Reviewer/`
- Reference docs → `Workflow/{Agent}/Reference/`
- Templates → `Workflow/{Agent}/Templates/`
- **Rule**: Always create agent-specific subdirectory when adding new workflows

### Rules → Rules/
- Architect rules → `Rules/Architect/`
- Planner rules → `Rules/Planner/`
- Executor rules → `Rules/Executor/`
- Researcher rules → `Rules/Researcher/`
- Reviewer rules → `Rules/Reviewer/`
- Naming: `{Agent}_Rules.md`
- **Rule**: Always create agent-specific subdirectory when adding new rules

### Documentation → Docs/
- **STRICT RULE**: No files may be placed directly in Docs/ root directory
- All documentation files organized by agent type and category
- Architect documentation → `Docs/Architect/`
- Planner documentation → `Docs/Planner/`
- Executor documentation → `Docs/Executor/`
- Researcher documentation → `Docs/Researcher/`
- Reviewer documentation → `Docs/Reviewer/`
- Universal documentation categories:
  - Code documentation → `Docs/Code/`
  - Research docs → `Docs/Research/`
  - Architecture docs → `Docs/Architecture/`
  - Governance docs → `Docs/Governance/`
  - Repository docs → `Docs/Repository/`
  - Devin Local IDE Documents → `Docs/Devin Local IDE Documents/`
  - External AI Reviews → `Docs/External AI Reviews/`
  - Sovereign AI Design Docs → `Docs/Sovereign AI Design Docs/`
- **Rule**: Always create agent-specific subdirectory first, then category subdirectory within when adding agent documentation
- **Rule**: Use universal categories for cross-agent documentation
- **Rule**: Never place files directly in Docs/ root directory

### Logs → Logs/
- **STRICT RULE**: All logs must be placed in their relevant Agent folder
- Architect logs → `Logs/Architect/`
- Planner logs → `Logs/Planner/`
- Executor logs → `Logs/Executor/`
- Researcher logs → `Logs/Researcher/`
- Reviewer logs → `Logs/Reviewer/`
- Archived logs → `Logs/.Archived/`
- Format: `Logs/{Agent}/{Category}/`
- **Categories**: Session/, Consistency_Review/, BP/, and other agent-specific categories
- **Rule**: New log folders must be created inside agent folders, never at Logs/ root level
- **Rule**: When archiving logs, use `Logs/.Archived/{Category}/` with appropriate subdirectories

### Agent Governance → Agents/
- Architect governance → `Agents/Architect/`
- Planner governance → `Agents/Planner/`
- Executor governance → `Agents/Executor/`
- Researcher governance → `Agents/Researcher/`
- Reviewer governance → `Agents/Reviewer/`
- Agent-specific configurations
- **Rule**: Always create agent-specific subdirectory when adding agent governance files

### Devin CLI → .devin/
- Skills → `.devin/skills/{agent}/`
- Architect skill → `.devin/skills/architect/`
- Planner skill → `.devin/skills/planner/`
- Executor skill → `.devin/skills/executor/`
- Researcher skill → `.devin/skills/researcher/`
- Reviewer skill → `.devin/skills/reviewer/`
- Hooks → `.devin/hooks.v1.json`
- Other Devin config
- **Rule**: Always create agent-specific skill subdirectory when adding new skills

### Plans → Plans/
- Project planning documents
- Completed plans → `Plans/Completed/`
- Queued plans → `Plans/Queued/`
- **Rule**: Use Completed/ for finished plans, Queued/ for pending plans

### Claude Code → .claude/
- Claude Code configuration
- Claude Code rules

---

## Categorization Governance Rules

### Universal Categorization Principle
**Every file must be placed in an appropriate category subdirectory matching its purpose.**

### Mandatory Category Creation
When adding files to any directory, create appropriate category subdirectories:
- **Scripts/**: Create category subdirectory (Schema/, Infrastructure/, Testing/, etc.)
- **Workflow/**: Create agent-specific subdirectory (Architect/, Planner/, Executor/, Researcher/, Reviewer/)
- **Rules/**: Create agent-specific subdirectory (Architect/, Planner/, Executor/, Researcher/, Reviewer/)
- **Agents/**: Create agent-specific subdirectory (Architect/, Planner/, Executor/, Researcher/, Reviewer/)
- **Docs/**: Create agent-specific subdirectory first (Architect/, Planner/, Executor/, Researcher/, Reviewer/), then category subdirectory within. Use universal categories (Code/, Research/, etc.) for cross-agent documentation
- **Logs/**: Create agent-specific subdirectory first (Architect/, Planner/, Executor/, Researcher/, Reviewer/), then category subdirectory within
- **.devin/skills/**: Create agent-specific subdirectory (architect/, planner/, executor/, researcher/, reviewer/)

### Prohibited File Placement
- Never place files directly at root level (except approved root files)
- Never place files directly in Docs/ root directory (must use agent or category subdirectories)
- Never place scripts in Scripts/ without category subdirectory
- Never place workflows in Workflow/ without agent subdirectory
- Never place rules in Rules/ without agent subdirectory
- Never place agent governance in Agents/ without agent subdirectory
- Never place logs in Logs/ without agent subdirectory
- Never place skills in .devin/skills/ without agent subdirectory
- Never create ad-hoc categories when existing categories match

### Log Placement Rules
- **Strict**: All logs must be in their relevant Agent folder (Logs/{Agent}/)
- **Subcategories**: Create log categories inside agent folders (Session/, Consistency_Review/, etc.)
- **Archiving**: Use Logs/.Archived/{Category}/ with appropriate subdirectories
- **Never**: Create log folders at Logs/ root level without agent context

---

## Quick Reference
**Before creating any file:**
1. Scripts? → Scripts/{Category}/
2. Workflows? → Workflow/{Agent}/
3. Rules? → Rules/{Agent}/
4. Agent governance? → Agents/{Agent}/
5. Documentation? → Docs/{Category}/
6. Logs? → Logs/{Agent}/{Category}/
7. Plans? → Plans/{Completed|Queued}/
8. Devin config? → .devin/
9. Claude config? → .claude/
10. Approved root file? → Root (with user approval)
11. None of above? → ASK USER FIRST

---

**Created**: 2026-07-28  
**Authority**: Architect Agent  
**Status**: Active