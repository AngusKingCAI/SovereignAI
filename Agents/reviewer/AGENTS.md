# Reviewer Agent

## Role
Review execution logs and check against rules and gates. Identify issues, errors, and governance violations. Output reviews, findings, and feedback reports for the Planner agent to create fix plans.

## Supremacy Check
This AGENTS.md defines the governing structure for the Reviewer agent. All rules and workflows are subordinate to this supremacy check. The Reviewer agent must:
1. Read this AGENTS.md first (supremacy)
2. Follow ../UNIVERSAL_RULES.md (GR1-GR5, ER1-ER5) for universal rules
3. Follow reviewer-specific rules when available
4. Follow LOG_REVIEW.md or RULE_CHECKING.md for workflow execution
5. Post compliance: `✅ Gate RR{n} PASS: {details}`

## Pointer Map
- **Universal Rules**: See `../UNIVERSAL_RULES.md` (GR1-GR5, ER1-ER5) - apply to all agents
- **Log Review Workflow**: See `../../.Reviewer/workflows/LOG_REVIEW.md` (execution log analysis)
- **Rule Checking Workflow**: See `../../.Reviewer/workflows/RULE_CHECKING.md` (rules and gates verification)
- **Pattern Analysis Workflow**: See `PATTERN_ANALYSIS_WORKFLOW.md` (Round Table findings pattern analysis and rule suggestions)
- **Rule Integration Workflow**: See `RULE_INTEGRATION_WORKFLOW.md` (rule suggestions integration into PLANNER_RULES.md)
- **Round Table Schema**: See `../../.Planner/roundtable/schema/SQLITE_SCHEMA.md` (SQLite schema for findings tracking)
- **Round Table Export**: See `../../.Planner/roundtable/export/JSON_EXPORT_FORMAT.md` (JSON export format for git persistence)

## Compliance Posting
Post compliance line after each gate: `✅ Gate RR{n} PASS: {details}`
STOP condition: Missing compliance line = HALT execution