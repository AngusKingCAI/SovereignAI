# IDE Architecture Rules

**Status**: Architect Agent Standard  
**Authority**: Enforced by Architect agent and gate system  
**Created**: 2026-07-24  
**Constitutional Compliance**: Verified

## Purpose

These rules govern the Architect agent's responsibility for IDE structure and project organization. Since only the Architect agent modifies IDE files and project structure, these rules are specific to the Architect agent's domain.

## Core Directory Structure Standard

The Architect agent MUST maintain this deterministic directory structure:

```
SovereignAI/
├── Agents/              # Agent definitions and documentation
│   └── {AgentName}/    # Each agent has its own folder
│       └── AGENTS.md   # Agent-specific documentation
├── Rules/              # Rule definitions and governance
│   └── {AgentName}/    # Each agent has its own rules folder
│       └── {Agent}_Rules.md
├── Workflow/           # Workflow definitions and procedures
│   └── {AgentName}/    # Each agent has its own workflow folder
│       └── {Agent}_Workflow.md
├── Scripts/            # All executable scripts and source code
│   ├── {AgentName}/    # Agent-specific scripts
│   ├── src/           # Source code
│   ├── config/        # Configuration files
│   └── tests/         # Test suites
├── Logs/              # All log files
│   └── {AgentName}/    # Agent-specific logs
│       ├── Gates/      # Gate system logs
│       ├── Conversations/  # AI conversation logs
│       └── {Component}/    # Component-specific logs
└── Docs/               # Documentation
    ├── specs/         # Specifications
    └── {Component}/   # Component documentation
```

## Mandatory Directory Structure Rules

### 1. Agent Structure (MANDATORY)
- **Each agent MUST have a folder in `Agents/`**
- **Each agent folder MUST contain `AGENTS.md`**
- **Agent documentation MUST define the agent's purpose, philosophy, and constitutional framework**

### 2. Rules Structure (MANDATORY)
- **Each agent MUST have a folder in `Rules/`**
- **Each agent rules folder MUST contain `{Agent}_Rules.md`**
- **Architect agent MUST maintain IDE architecture rules in `Rules/Architect/IDE_Architecture_Rules.md`**
- **Rules MUST define agent-specific constraints and requirements**

### 3. Workflow Structure (MANDATORY)
- **Each agent MUST have a folder in `Workflow/`**
- **Each agent workflow folder MUST contain `{Agent}_Workflow.md`**
- **Workflows MUST define step-by-step procedures for the agent**

### 4. Scripts Structure (MANDATORY)
- **All executable scripts and source code MUST be in `Scripts/`**
- **Agent-specific scripts MUST be in `Scripts/{AgentName}/`**
- **Source code MUST be in `Scripts/src/`**
- **Configuration files MUST be in `Scripts/config/`**
- **Test suites MUST be in `Scripts/tests/`**

### 5. Logs Structure (MANDATORY)
- **All log files MUST be in `Logs/`**
- **Agent-specific logs MUST be in `Logs/{AgentName}/`**
- **Gate system logs MUST be in `Logs/{AgentName}/Gates/`**
- **Conversation logs MUST be in `Logs/{AgentName}/Conversations/`**
- **Component logs MUST be in `Logs/{AgentName}/{Component}/`**

## Naming Conventions

### Directory Naming
- **Directories**: PascalCase (e.g., `Agents`, `Rules`, `Workflow`, `Scripts`, `Logs`, `Docs`)
- **Agent Names**: PascalCase (e.g., `Architect`, `Developer`, `Tester`)
- **Component Names**: PascalCase (e.g., `Logging`, `Kernel`, `Policy`)

### File Naming
- **Agent Files**: `AGENTS.md` (always uppercase)
- **Rule Files**: `{Agent}_Rules.md` (e.g., `Architect_Rules.md`)
- **Workflow Files**: `{Agent}_Workflow.md` (e.g., `Architect_Workflow.md`)
- **Spec Files**: `phase-{N}-{component}.md` (e.g., `phase-0-logging-foundation.md`)
- **Log Files**: `{component}-{YYYY-MM-DD}.jsonl` (e.g., `harness_infrastructure-2024-01-01.jsonl`)
- **State Files**: `phase-{N}-state.json` (e.g., `phase-0-state.json`)
- **Conversation Files**: `{session-id}.json` (e.g., `phase-0-implementation.json`)

## Enforcement Mechanisms

### 1. Gate System Verification
- **Gate system MUST verify directory structure before phase progression**
- **Structure validation MUST be part of phase completion criteria**
- **Non-compliant structures MUST block phase progression**

### 2. Architect Agent Responsibility
- **Architect agent MUST enforce structure during development**
- **Architect agent MUST validate structure before approving specifications**
- **Architect agent MUST document any structural exceptions**

### 3. Automated Validation
- **Automated scripts MUST validate directory structure**
- **Validation MUST run before major operations**
- **Validation failures MUST halt operations**

## Constitutional Compliance

This architecture rule enforces constitutional requirements:

- **Deterministic**: Predictable, standardized structure across all agents
- **Observable**: Clear location for all project artifacts
- **Minimal Coupling**: Separated concerns with clear boundaries
- **Architecture First**: Structure established before implementation
- **Explicit Interfaces**: Clear separation between agents, rules, workflows

## Exceptions Process

### Valid Exceptions
- **Legacy code**: Pre-existing structure requiring migration
- **External dependencies**: Third-party tools with fixed structure
- **Temporary structures**: Short-term development artifacts

### Exception Process
1. **Document exception** in project architecture log
2. **Get Architect approval** for structural deviation
3. **Define migration plan** to standard structure
4. **Set deadline** for compliance

## Migration Guide

### For New Agents
1. **Create agent folder** in `Agents/`
2. **Create AGENTS.md** with agent documentation
3. **Create rules folder** in `Rules/`
4. **Create rule file** with agent-specific rules
5. **Create workflow folder** in `Workflow/`
6. **Create workflow file** with agent procedures
7. **Create scripts folder** in `Scripts/`
8. **Follow Scripts structure** for implementation
9. **Create logs folder** in `Logs/`
10. **Follow Logs structure** for logging

### For Existing Agents
1. **Audit current structure** against standards
2. **Identify deviations** from standard structure
3. **Create migration plan** for each deviation
4. **Execute migration** incrementally
5. **Validate new structure** with gate system
6. **Update documentation** to reflect changes

## Compliance Checklist

- [ ] Agent folder exists in `Agents/`
- [ ] `AGENTS.md` exists in agent folder
- [ ] IDE architecture rules exist in `Rules/Architect/IDE_Architecture_Rules.md`
- [ ] Rules folder exists in `Rules/`
- [ ] Rule file exists in rules folder
- [ ] Workflow folder exists in `Workflow/`
- [ ] Workflow file exists in workflow folder
- [ ] Scripts are in `Scripts/` directory
- [ ] Source code is in `Scripts/src/`
- [ ] Configuration is in `Scripts/config/`
- [ ] Tests are in `Scripts/tests/`
- [ ] Logs are in `Logs/` directory
- [ ] Agent logs are in `Logs/{AgentName}/`
- [ ] Gate logs are in `Logs/{AgentName}/Gates/`
- [ ] Conversation logs are in `Logs/{AgentName}/Conversations/`
- [ ] Naming conventions followed
- [ ] Gate system validation passed

## Amendment Process

Amendments to these architectural rules require:
1. **Formal proposal** via Architecture Decision Record
2. **Impact analysis** on existing structure
3. **Constitutional compliance verification**
4. **Architect approval**
5. **Migration plan** for existing agents
6. **Documentation update**

## Amendment Log

| Date | Amendment | Rationale |
|------|-----------|-----------|
| 2026-07-24 | Initial IDE architecture rules | Establish deterministic project structure for Architect agent based on Phase 0 implementation experience |
| 2026-07-24 | Renamed from PROJECT_ARCHITECTURE_RULES to IDE_Architecture_Rules | Made rules specific to Architect agent since only Architect modifies IDE files |

**Current Constitutional Status**: COMPLIANT

These IDE architecture rules ensure the Architect agent maintains deterministic, observable, and structured project organization for the SovereignAI Harness infrastructure.