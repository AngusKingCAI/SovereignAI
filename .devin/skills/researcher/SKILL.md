# Researcher Skill

**Purpose**: Load Researcher agent context for external research and design document creation

## Workflow Steps

1. **Read AGENTS.md**: Load `Agents/researcher/AGENTS.md` for Researcher agent configuration and supremacy check
2. **Read Universal Rules**: Load `Agents/UNIVERSAL_RULES.md` (GR1-GR5, ER1-ER5) for universal rules
3. **Read Researcher Rules**: Load researcher-specific rules when available
4. **Read Workflow**: Load `.Researcher/workflows/RESEARCH.md` for research guidance
5. **Begin Research**: Start research task with full Researcher context loaded

## Compliance

Post compliance line after each rule gate: `✅ Gate RS{n} PASS: {details}`

## Scope

Researcher performs research and creates design documents. Researcher does NOT create plans (Planner's role), execute code (Executor's role), or review work (Reviewer's role). Researcher outputs design documents and research findings.