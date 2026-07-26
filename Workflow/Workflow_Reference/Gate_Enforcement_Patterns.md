# Gate Enforcement Patterns

**Purpose**: Universal gate enforcement patterns for all agent workflows.

## Gate Enforcement Overview

**EVERY STEP HAS A GATE REQUIREMENT**: Each workflow step includes a mandatory gate that must pass before proceeding to the next step.

## Gating Rules

- Gate verification must be explicit and actionable
- Gates must have clear PASS/FAIL criteria
- Gate failures must stop progression until resolved
- Gate results must be documented in conversation log
- Gates should validate completion, quality, and compliance of the step

## Gate Pattern

1. Perform the step's actions
2. Document the results in conversation log
3. Run the step's gate verification
4. Gate must pass to proceed to next step
5. If gate fails, stop and address the issue

## Compliance Requirement

- Skipping any gate is a SCOPE VIOLATION per AGENTS.md
- The gate system provides enforcement for all workflow steps
- Each step is gated individually for comprehensive compliance
- Template compliance requires gate enforcement rules to be defined

## Agent-Specific Customization

Each agent should define:
- **Gate Specifications**: Agent-specific gate definitions and validation criteria
- **Gate System Execution**: Agent-specific gate validation scripts and commands
- **Gate System Reference**: Agent-specific references to rules, quality frameworks, and delivery processes

## Usage Guidelines

### Universal Pattern Application
1. **Apply Universal Pattern**: Use the universal gate enforcement pattern for all agent workflows
2. **Define Agent-Specific Gates**: Create agent-specific gate definitions in agent Reference/ folders
3. **Implement Gate Validation**: Create agent-specific gate validation scripts
4. **Integrate with Workflow**: Integrate gate enforcement into workflow phases
5. **Document Gate References**: Document gate system references for each agent

### Gate Enforcement Consistency
- **Universal Rules**: All agents follow the same gating rules
- **Agent-Specific Gates**: Each agent defines its own gate specifications
- **Consistent Pattern**: Same gate pattern across all agents (perform → document → verify → proceed)
- **Universal Compliance**: Same compliance requirement (gates cannot be skipped)