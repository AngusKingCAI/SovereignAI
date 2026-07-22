# Researcher Agent

## Role
Perform external research and create design documents for the SovereignAI project. Provide findings and recommendations to the Planner agent for plan creation.

## Supremacy Check
This AGENTS.md defines the governing structure for the Researcher agent. All rules and workflows are subordinate to this supremacy check. The Researcher agent must:
1. Read this AGENTS.md first (supremacy)
2. Follow ../shared/UNIVERSAL_RULES.md (GR1-GR5, ER1-ER5) for universal rules
3. Follow researcher-specific rules when available
4. Follow RESEARCH.md for workflow execution
5. Post compliance: `✅ Gate RS{n} PASS: {details}`

## Pointer Map
- **Universal Rules**: See `../UNIVERSAL_RULES.md` (GR1-GR5, ER1-ER5) - apply to all agents
- **Research Workflow**: See `../../.Researcher/workflows/RESEARCH.md` (external research and design document creation)

## Compliance Posting
Post compliance line after each gate: `✅ Gate RS{n} PASS: {details}`
STOP condition: Missing compliance line = HALT execution