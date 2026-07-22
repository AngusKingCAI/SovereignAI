# Executor Skill

**Purpose**: Load Executor agent context for plan execution

## Workflow Steps

1. **Read AGENTS.md**: Load `Agents/executor/AGENTS.md` for Executor agent configuration and supremacy check
2. **Read Universal Rules**: Load `Agents/UNIVERSAL_RULES.md` (GR1-GR5, ER1-ER5) for universal rules
3. **Read Executor Rules**: Load executor-specific rules when available
4. **Read Workflow**: Load `.Executor/workflows/CODE_EXECUTION.md` for execution guidance
5. **Begin Execution**: Start execution task with full Executor context loaded

## Compliance

Post compliance line after each rule gate: `✅ Gate ER{n} PASS: {details}`

## Scope

Executor executes plans created by Planner per GR3. Executor does NOT create plans (Planner's role) or review work (Reviewer's role) per GR2.