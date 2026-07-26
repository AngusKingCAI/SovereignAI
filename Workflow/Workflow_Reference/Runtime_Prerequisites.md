# Runtime Prerequisites

**Purpose**: Documentation of runtime directories and files required for workflow execution.

## Overview

The workflows reference several runtime paths that are either created during execution or represent infrastructure that needs to be provisioned. This document categorizes these paths and their current status.

## Runtime Directories (Created During Execution)

### Planner Runtime Directories
- **Plans/**: Storage location for finalized plans created by Planner workflow
  - **Status**: Created during Planner workflow execution
  - **Usage**: Plans are saved here after Phase 7 validation
  - **Naming Convention**: plan-{N}.{rev}.md

- **Logs/Planner/**: Storage location for Planner-specific logs
  - **Status**: Created during Planner workflow execution
  - **Usage**: Plan iterations, validation results, session logs
  - **Subdirectories**: 
    - `validation-completions/`: Successful validation results
    - `validation-failures/`: Failed validation results

- **Logs/Roundtable/Devin/**: Storage location for internal Round Table reviews
  - **Status**: Created during Planner workflow execution
  - **Usage**: Internal panelist reviews and briefs
  - **Naming Convention**: brief-rev{N}.md, iteration-{N}-panelist-{M}.md

- **Logs/Roundtable/External/**: Storage location for external Round Table reviews
  - **Status**: Created during Planner workflow execution
  - **Usage**: External panelist reviews and briefs
  - **Naming Convention**: brief-rev{N}.md, round-{N}-panelist-{M}.md

### Executor Runtime Directories
- **Logs/{AgentType}/Sessions/**: Storage location for Executor session logs
  - **Status**: Created during Executor workflow execution
  - **Usage**: Session-level logging and audit trails
  - **Example**: Logs/Executor/Sessions/session-{timestamp}.md

## Infrastructure Directories (Require Provisioning)

### Scripts Directory Structure
- **Scripts/**: Top-level directory for automation scripts
  - **Status**: ❌ Does not exist - requires creation
  - **Purpose**: Infrastructure automation and validation scripts

### Planner Validation Scripts
- **Scripts/Planner/Gates/run-all-planner-gates.sh**: Automated validation script
  - **Status**: ❌ Does not exist - requires creation
  - **Purpose**: Execute all 6 validation checks for plans
  - **Validation Checks**:
    1. Plan Structure Validation
    2. Scope Compliance Validation
    3. Dependency Analysis Validation
    4. Quality Assessment
    5. Landmine Screening Verification
    6. Infrastructure Scope Validation

### Governance Infrastructure
- **Scripts/Governance/Hooks/**: Hook system scripts
  - **Status**: ❌ Does not exist - requires creation
  - **Purpose**: Governance hook automation

- **Scripts/Governance/Config/phase_permissions.json**: Phase permission configuration
  - **Status**: ❌ Does not exist - requires creation
  - **Purpose**: Define execution permissions per workflow phase

- **Scripts/Governance/simple_logger.py**: Logging utility
  - **Status**: ❌ Does not exist - requires creation
  - **Purpose**: Standardized logging across workflows

### Devin CLI Configuration
- **.devin/hooks.v1.json**: Devin CLI hook configuration
  - **Status**: ❌ Does not exist - requires creation
  - **Purpose**: Configure automated hooks for workflow enforcement
  - **Note**: Changes to this file require Devin CLI restart to take effect

- **.devin/skills/executor/SKILL.md**: Executor agent skill definition
  - **Status**: ❌ Does not exist - requires creation
  - **Purpose**: Define Executor agent capabilities and commands

## Implementation Priority

### Immediate Required (Blocking Workflow Execution)
1. **Scripts/Planner/Gates/run-all-planner-gates.sh**: Required for validation steps in Planner workflow
2. **.devin/hooks.v1.json**: Required for hook-based governance system

### Short-term Required (Full Workflow Functionality)
3. **Scripts/Governance/Hooks/**: Governance automation
4. **Scripts/Governance/Config/phase_permissions.json**: Phase permissions
5. **Scripts/Governance/simple_logger.py**: Standardized logging
6. **.devin/skills/executor/SKILL.md**: Executor agent definition

### Automatic Creation (No Manual Intervention Required)
7. **Plans/**: Created automatically by Planner workflow
8. **Logs/Planner/**: Created automatically by Planner workflow
9. **Logs/Roundtable/Devin/**: Created automatically by Planner workflow
10. **Logs/Roundtable/External/**: Created automatically by Planner workflow
11. **Logs/{AgentType}/Sessions/**: Created automatically by Executor workflow

## Current Workflow Status

### Planner Workflow
- **Validation Steps**: Currently use manual validation (placeholder for script)
- **Runtime Directories**: Will be created automatically during execution
- **Impact**: Can execute with manual validation, missing automation

### Architect Workflow
- **Runtime Dependencies**: Minimal runtime directory requirements
- **Impact**: Can execute with current setup

### Executor Workflow
- **Hook System**: References non-existent .devin configuration
- **Runtime Directories**: Will be created automatically during execution
- **Impact**: Cannot execute as designed without hook infrastructure

## Recommendations

### Phase 1: Enable Planner Validation
1. Create `Scripts/Planner/Gates/run-all-planner-gates.sh` with 6 validation checks
2. Test validation script with sample plans
3. Update Planner workflow to use automated validation when script is available

### Phase 2: Implement Hook System
1. Create `.devin/hooks.v1.json` with basic hook configuration
2. Create hook scripts in `Scripts/Governance/Hooks/`
3. Configure phase permissions in `Scripts/Governance/Config/phase_permissions.json`
4. Implement standardized logging in `Scripts/Governance/simple_logger.py`

### Phase 3: Define Executor Agent
1. Create `.devin/skills/executor/SKILL.md` with Executor capabilities
2. Define Executor-specific commands and patterns
3. Test Executor workflow with hook system

### Phase 4: Automation Enhancement
1. Add more automation scripts to `Scripts/` as needed
2. Enhance governance automation over time
3. Standardize logging across all workflows

## Migration Notes

- **Manual Validation**: Until Scripts/Planner/Gates/ is created, Planner workflow uses manual validation
- **Hook Fallback**: Until .devin/hooks.v1.json is created, workflows rely on agent-level enforcement
- **Directory Creation**: Runtime directories are created on-demand during workflow execution
- **Path Consistency**: Ensure all workflows use consistent path conventions (lowercase vs uppercase)