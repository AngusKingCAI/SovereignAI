---
id: wf-ref-validation-enforcement
status: active
owner: architect-agent
updated: 2026-07-28
purpose: Universal validation enforcement patterns for all agent workflows
---

# Validation Enforcement Patterns

**Purpose**: Universal validation enforcement patterns for all agent workflows.

## Validation Enforcement Overview

**EVERY STEP HAS A VALIDATION REQUIREMENT**: Each workflow step includes a mandatory validation that must pass before proceeding to the next step.

## Validation Rules

- Validation verification must be explicit and actionable
- Validation must have clear PASS/FAIL criteria
- Validation failures must stop progression until resolved
- Validation results must be documented in conversation log
- Validation should validate completion, quality, and compliance of the step

## Validation Pattern

1. Perform the step's actions
2. Document the results in conversation log
3. Run the step's validation verification
4. Validation must pass to proceed to next step
5. If validation fails, stop and address the issue

## Compliance Requirement

- Skipping any validation is a SCOPE VIOLATION per AGENTS.md
- The validation system provides enforcement for all workflow steps
- Each step is validated individually for comprehensive compliance
- Template compliance requires validation enforcement rules to be defined

## Agent-Specific Customization

Each agent should define:
- **Validation Specifications**: Agent-specific validation definitions and criteria
- **Validation System Execution**: Agent-specific validation scripts and commands
- **Validation System Reference**: Agent-specific references to rules, quality frameworks, and delivery processes

## Usage Guidelines

### Universal Pattern Application
1. **Apply Universal Pattern**: Use the universal validation enforcement pattern for all agent workflows
2. **Define Agent-Specific Validation**: Create agent-specific validation definitions in agent Reference/ folders
3. **Implement Validation Verification**: Create agent-specific validation scripts
4. **Integrate with Workflow**: Integrate validation enforcement into workflow phases
5. **Document Validation References**: Document validation system references for each agent

### Validation Enforcement Consistency
- **Universal Rules**: All agents follow the same validation rules
- **Agent-Specific Validation**: Each agent defines its own validation specifications
- **Consistent Pattern**: Same validation pattern across all agents (perform → document → verify → proceed)
- **Universal Compliance**: Same compliance requirement (validation cannot be skipped)