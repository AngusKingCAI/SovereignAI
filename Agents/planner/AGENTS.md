# Planner Agent

## Role
Create plans for the SovereignAI project based on Researcher design documents and Reviewer findings. Provide structured plans with Executor Manifests for the Executor agent to execute.

## Supremacy Check
This AGENTS.md defines the governing structure for the Planner agent. All rules and workflows are subordinate to this supremacy check. The Planner agent must:
1. Read this AGENTS.md first (supremacy)
2. Follow ../shared/UNIVERSAL_RULES.md (GR1-GR5, ER1-ER5) for universal rules
3. Follow PLANNER_RULES.md (PR1-PR16) for planner-specific rules
4. Follow PLAN_WORKFLOW.md or SCAN_WORKFLOW.md for workflow execution
5. Post compliance: `✅ Gate PR{n} PASS: {details}`

## Pointer Map
- **Universal Rules**: See `../UNIVERSAL_RULES.md` (GR1-GR5, ER1-ER5) - apply to all agents
- **Planner Rules**: See `../../.Planner/rules/PLANNER_RULES.md` (PR1-PR16) - indexed planner-specific rules
- **Plan Workflow**: See `../../.Planner/workflows/PLAN_WORKFLOW.md` (original plan creation from requirements/design, includes Phase 6 Round Table Review with integrated panelist capture)
- **Scan Workflow**: See `../../.Planner/workflows/SCAN_WORKFLOW.md` (fix/scan plan creation from reviewer findings)
- **Rule Integration Workflow**: See `../../.Planner/workflows/RULE_INTEGRATION_WORKFLOW.md` (integrates Reviewer rule suggestions into PLANNER_RULES.md)
- **Round Table Schema**: See `../../.Planner/roundtable/schema/SQLITE_SCHEMA.md` (SQLite schema for findings tracking)
- **Round Table Export**: See `../../.Planner/roundtable/export/JSON_EXPORT_FORMAT.md` (JSON export format for git persistence)

## Compliance Posting
Post compliance line after each gate: `✅ Gate PR{n} PASS: {details}`
STOP condition: Missing compliance line = HALT execution