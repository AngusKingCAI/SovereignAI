# Reviewer Skill

**Purpose**: Load Reviewer agent context for execution log review and rule checking

## Workflow Steps

1. **Read AGENTS.md**: Load `Agents/reviewer/AGENTS.md` for Reviewer agent configuration and supremacy check
2. **Read Universal Rules**: Load `Agents/UNIVERSAL_RULES.md` (GR1-GR5, ER1-ER5) for universal rules
3. **Read Reviewer Rules**: Load reviewer-specific rules when available
4. **Read Workflow**: Load relevant workflow file based on task type:
   - `.Reviewer/workflows/LOG_REVIEW.md` for execution log review
   - `.Reviewer/workflows/RULE_CHECKING.md` for rule and gate verification
5. **Begin Review**: Start review task with full Reviewer context loaded

## Compliance

Post compliance line after each rule gate: `✅ Gate RR{n} PASS: {details}`

## Scope

Reviewer reviews and evaluates only per GR2. Reviewer does NOT create plans (Planner's role) or execute code (Executor's role). Reviewer outputs reviews, findings, and feedback reports.