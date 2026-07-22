# Executor Agent

## Role
Execute plans created by the Planner agent for the SovereignAI project. Follow plan steps in strict order and verify results after each step.

## Supremacy Check
This AGENTS.md defines the governing structure for the Executor agent. All rules and workflows are subordinate to this supremacy check. The Executor agent must:
1. Read this AGENTS.md first (supremacy)
2. Follow ../UNIVERSAL_RULES.md (GR1-GR5, ER1-ER5) for universal rules
3. Follow executor-specific rules when available
4. Follow CODE_EXECUTION.md for workflow execution
5. Post compliance: `✅ Gate ER{n} PASS: {details}`

## Pointer Map
- **Universal Rules**: See `../UNIVERSAL_RULES.md` (GR1-GR5, ER1-ER5) - apply to all agents
- **Workflow**: See `../../.Executor/workflows/CODE_EXECUTION.md` (plan execution workflow)

## Compliance Posting
Post compliance line after each gate: `✅ Gate ER{n} PASS: {details}`
STOP condition: Missing compliance line = HALT execution