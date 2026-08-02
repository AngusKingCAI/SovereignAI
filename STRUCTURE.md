# SovereignAI File Structure

**Root-Level File Placement Reference**

**SSOT Note**: This file is the single source of truth for file placement and directory structure. For behavioral governance rules and agent constraints, see .devin/rules/architect.md.

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
✅ `STRUCTURE.md` - This file (file placement reference)

### Scripts → Scripts/
- All implementation scripts organized by category
- Schema validation scripts → `Scripts/Schema/`
- Infrastructure automation scripts → `Scripts/Infrastructure/`
- Harness testing scripts → `Scripts/Harness Tests/`
- App testing scripts → `Scripts/App Tests/`
- Build scripts → `Scripts/Build/`
- Deployment scripts → `Scripts/Deployment/`
- Maintenance scripts → `Scripts/Maintenance/`
- Utilities scripts → `Scripts/Utilities/`
- Logging scripts → `Scripts/Logging/`
- Analysis scripts → `Scripts/Analysis/`
- Misc scripts → `Scripts/Misc/`
- **Rule**: Always create appropriate category subdirectory when adding new scripts

### Workflows → Workflow/
- Universal frameworks → `Workflow/Workflow_Reference/`
- Architect workflows → `Workflow/Architect/` (includes Creation Workflows/, Validation Workflows/, .Reference/)
- Planner workflows → `Workflow/Planner/` (includes Templates/, Reference/)
- Executor workflows → `Workflow/Executor/` (includes Templates/, Reference/)
- Researcher workflows → `Workflow/Researcher/`
- Reviewer workflows → `Workflow/Reviewer/`
- **Rule**: Always create agent-specific subdirectory when adding new workflows
- **Rule**: Template organization varies by agent (e.g., Planner/Executor use Templates/, Architect uses Creation Workflows/Templates/)

### Rules → .devin/rules/
- Architect rules → `.devin/rules/architect.md`
- Planner rules → `.devin/rules/planner.md`
- Executor rules → `.devin/rules/executor.md`
- Researcher rules → `.devin/rules/researcher.md`
- Reviewer rules → `.devin/rules/reviewer.md`
- Naming: `{agent}.md` (lowercase)
- **Note**: Rules are autoloaded by Devin CLI from .devin/rules/

### Documentation → Docs/
- **STRICT RULE**: No files may be placed directly in Docs/ root directory
- Available documentation categories:
  - Code documentation → `Docs/Code/`
  - Devin Local IDE Documents → `Docs/Devin Local IDE Documents/`
  - External AI Reviews → `Docs/External AI Reviews/`
  - Sovereign AI Design Docs → `Docs/Sovereign AI Design Docs/`
- **Rule**: Create new subdirectories only when needed for specific documentation types
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
- Agent-specific governance files placed in appropriate agent subdirectories
- **Rule**: Create agent subdirectories only when needed for agent-specific governance
- **Rule**: Most agent governance is handled through .devin/rules/{agent}.md

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

## Quick Reference
**Before creating any file:**
1. Scripts? → Scripts/{Category}/
2. Workflows? → Workflow/{Agent}/
3. Rules? → .devin/rules/{agent}.md
4. Agent governance? → Agents/{Agent}/ (if needed beyond .devin/rules/)
5. Documentation? → Docs/{Category}/ (create category if needed)
6. Logs? → Logs/{Agent}/{Category}/
7. Plans? → Plans/{Completed|Queued}/
8. Devin config? → .devin/
9. Claude config? → .claude/
10. Approved root file? → Root (with user approval)
11. None of above? → ASK USER FIRST

---

**SSOT Reference**: This file is the single source of truth for file placement. For governance rules and behavioral constraints, see .devin/rules/architect.md