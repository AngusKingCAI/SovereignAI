# SovereignAI Repository Structure

**Purpose**: Defines the official repository structure, file placement rules, and governance for file organization  
**Status**: Active  
**Version**: 1.0  
**Created**: 2026-07-28  
**Authority**: Architect Agent

---

## Core Principles

1. **Root Directory Minimalism**: Root directory should remain minimal. Only files explicitly approved by user should be placed at root level.
2. **Categorized Organization**: All files must be placed in appropriately categorized directories.
3. **Standard Naming**: Follow established naming conventions for directories and files.
4. **Governance Compliance**: File placement must comply with IDE architecture rules.

---

## Directory Structure

```
SovereignAI/
├── Agents/                    # Other agents' governance files
├── App/                       # Application code (excluded from harness architecture scans)
├── Docs/                      # Documentation
├── Logs/                      # Runtime logs and audit trails
├── Rules/                     # Rule definitions for all agents
├── Scripts/                   # Implementation scripts organized by category
├── Workflow/                  # Workflow definitions for all agents
├── .devin/                    # Devin CLI configuration, skills, and hooks
├── .claude/                   # Claude Code configuration and rules
├── AGENTS.md                  # Main agent configuration (root-level, approved)
├── PRINCIPLES.md              # Constitutional framework (root-level, approved)
└── INDEX.md                   # Repository index (root-level, approved)
```

---

## Root Directory Rules

### Approved Root-Level Files
The following files are explicitly approved for root directory placement:
- `AGENTS.md` - Main agent configuration
- `PRINCIPLES.md` - Constitutional framework  
- `INDEX.md` - Repository index

### Root Directory File Addition Policy
- **STRICT PROHIBITION**: No files may be added to root directory without explicit user approval
- **Approval Process**: Before adding any file to root, Architect agent must:
  1. Check if file belongs in existing categorized directory
  2. If root placement is necessary, present popup menu with [Approve/Reject] options
  3. Document approval rationale in Architect workflow log
- **Exception Process**: Only files that cannot be categorized elsewhere may be considered for root placement

---

## Directory-Specific Rules

### Scripts/ Directory
**Purpose**: Implementation scripts organized by category  
**Naming Convention**: Descriptive subdirectories for script categories  
**Examples**:
- `Scripts/SchemaValidation/` - Schema validation scripts
- `Scripts/Infrastructure/` - Infrastructure automation scripts
- `Scripts/Testing/` - Testing and validation scripts

**File Placement Rules**:
- All implementation scripts must be placed in Scripts/
- Create descriptive subdirectories for script categories
- Use descriptive filenames with clear purpose
- No scripts at root level under Scripts/

### Workflow/ Directory
**Purpose**: Workflow definitions for all agents  
**Structure**:
```
Workflow/
├── Workflow_Reference/        # Universal framework references
├── Architect/                 # Architect-specific workflows
│   ├── Reference/            # Architect reference documents
│   └── Templates/            # Architect templates
├── Planner/                   # Planner-specific workflows
│   ├── Reference/            # Planner reference documents
│   └── Templates/            # Planner templates
├── Executor/                  # Executor-specific workflows
│   ├── Reference/            # Executor reference documents
│   └── Templates/            # Executor templates
└── [Other Agents]/            # Other agent workflows following same pattern
```

**File Placement Rules**:
- Universal frameworks in Workflow/Workflow_Reference/
- Agent-specific workflows in Workflow/{Agent}/
- Reference documents in Reference/ subdirectories
- Templates in Templates/ subdirectories
- No workflow files directly in Workflow/

### Rules/ Directory
**Purpose**: Rule definitions for all agents  
**Structure**:
```
Rules/
├── Architect/                 # Architect-specific rules
├── Planner/                   # Planner-specific rules
├── Executor/                  # Executor-specific rules
└── [Other Agents]/            # Other agent rules
```

**File Placement Rules**:
- Agent-specific rules in Rules/{Agent}/
- Naming convention: {Agent}_Rules.md
- No rule files directly in Rules/

### Agents/ Directory
**Purpose**: Other agents' governance files  
**File Placement Rules**:
- Individual agent governance files in appropriate subdirectories
- Follow agent-specific organizational patterns
- Edit these to enforce standards across agents

### Docs/ Directory
**Purpose**: Documentation  
**File Placement Rules**:
- All documentation in Docs/ or appropriate subdirectories
- Categorize documentation by type (Code, Research, Architecture, etc.)
- No documentation files at root level

### Logs/ Directory
**Purpose**: Runtime logs and audit trails  
**Structure**:
```
Logs/
├── Architect/                 # Architect-specific logs
├── Planner/                   # Planner-specific logs
├── Executor/                  # Executor-specific logs
└── [Other Agents]/            # Other agent logs
```

**File Placement Rules**:
- Agent-specific logs in Logs/{Agent}/
- Follow agent-specific log organization patterns
- Timestamp formatting: YYYY-MM-DD_HH-MM-SS
- No log files directly in Logs/

### .devin/ Directory
**Purpose**: Devin CLI configuration, skills, and hooks  
**Structure**:
```
.devin/
├── skills/                    # Agent skill definitions
├── hooks.v1.json             # Hook configuration
└── [Other Devin config]
```

**File Placement Rules**:
- Skill definitions in .devin/skills/
- Hook configuration in .devin/hooks.v1.json
- No Devin config files at root level
- **IMPORTANT**: Changes to .devin/hooks.v1.json require Devin CLI restart

### .claude/ Directory
**Purpose**: Claude Code configuration and rules  
**File Placement Rules**:
- Claude-specific configuration in .claude/
- No Claude config files at root level
- Maintain for compatibility with Claude Code

---

## File Placement Decision Tree

When creating a new file, follow this decision tree:

1. **Is it a script?** → Place in Scripts/{Category}/
2. **Is it a workflow?** → Place in Workflow/{Agent}/
3. **Is it a rule?** → Place in Rules/{Agent}/
4. **Is it documentation?** → Place in Docs/{Category}/
5. **Is it a log?** → Place in Logs/{Agent}/
6. **Is it agent governance?** → Place in Agents/{Agent}/
7. **Is it Devin/CLI config?** → Place in .devin/
8. **Is it Claude Code config?** → Place in .claude/
9. **Is it one of the approved root files?** → Place at root
10. **None of the above?** → ASK USER APPROVAL before root placement

---

## Naming Conventions

### Directory Names
- Use descriptive, meaningful names
- Use PascalCase for agent-specific directories (Architect, Planner, Executor)
- Use lowercase for utility directories (docs, logs, scripts)
- Use hyphens for multi-word directories (SchemaValidation, Workflow_Reference)

### File Names
- Workflows: {Agent}_{WorkflowType}_Workflow.md
- Rules: {Agent}_Rules.md
- Scripts: Descriptive names with clear purpose
- Schemas: {purpose}-schema.json
- Templates: {Purpose}_Template.md

---

## Governance Enforcement

### Architect Agent Responsibilities
- Enforce file placement rules during workflow execution
- Validate directory structure compliance before file creation
- Present approval popup for root-level file additions
- Document file placement decisions in workflow logs
- Maintain this Repository_Structure.md document

### Violation Handling
- Root directory violations without approval: STOP and request user approval
- Misplaced files: MOVE to correct location
- Naming convention violations: RENAME to follow conventions
- Structure violations: REORGANIZE to comply with this document

### Validation Process
Before creating any file, Architect agent must:
1. Check if file belongs in existing categorized directory
2. Verify naming conventions compliance
3. If root placement is considered, present user approval popup
4. Document file placement decision with rationale
5. Update INDEX.md if new directories are created

---

## Change Process

### Adding New Directories
1. Research existing structure patterns
2. Determine appropriate parent directory
3. Present directory addition to user with rationale
4. Update this Repository_Structure.md document
5. Update INDEX.md with new directory structure

### Modifying Structure
1. Assess impact on existing files
2. Plan migration strategy
3. Present modification proposal to user
4. Execute migration with user approval
5. Update this Repository_Structure.md document
6. Update INDEX.md with new structure

---

## Compliance Checklist

When creating or moving files:
- [ ] File placed in appropriate categorized directory
- [ ] Naming conventions followed
- [ ] Root placement only with explicit user approval
- [ ] INDEX.md updated if new directories created
- [ ] This Repository_Structure.md updated if structure changes
- [ ] File placement documented in workflow log

---

**Current Status**: Active  
**Last Updated**: 2026-07-28  
**Maintained By**: Architect Agent  
**Review Frequency**: Monthly or when structure changes are proposed