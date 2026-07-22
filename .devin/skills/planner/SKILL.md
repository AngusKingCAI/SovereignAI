# Planner Skill

**Purpose**: Load Planner agent context for plan creation and workflow design

## Workflow Steps

1. **Read AGENTS.md**: Load `Agents/planner/AGENTS.md` for Planner agent configuration and supremacy check
2. **Read Universal Rules**: Load `Agents/UNIVERSAL_RULES.md` (GR1-GR5, ER1-ER5) for universal rules
3. **Read Planner Rules**: Load `.Planner/rules/PLANNER_RULES.md` (PR1-PR16) for planner-specific rules
4. **Read Workflow**: Load relevant workflow file based on task type:
   - `.Planner/workflows/PLAN_WORKFLOW.md` for original plan creation
   - `.Planner/workflows/SCAN_WORKFLOW.md` for fix/scan plan creation
5. **Begin Planning**: Start planning task with full Planner context loaded

## Compliance

Post compliance line after each rule gate: `✅ Gate PR{n} PASS: {details}`

## Scope

Planner creates all plans (original, fix, scan) per GR3. Planner does NOT execute plans (Executor's role) or review work (Reviewer's role) per GR2.