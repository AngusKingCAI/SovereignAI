# Executor Prompt: Update AI_HANDOFF.md for Batch Governance & Round Table Scoring

## Plan Header

**Plan**: batch31-34-governance-plan.md (or next available batch governance plan number)
**Vision principles**: Document workflow gaps, establish batch governance pattern, create persistent Round Table score history
**AR rules**: AR6 (stable IDs), AR12 (review path), AR13 (Executor Manifest)
**OR rules**: UOR-1 (deliverables ship in full), UOR-4 (Executor Manifest compliance), UOR-5 (governance file protection)
**Open questions resolved**: 
- Q: Does AGENTS.md need updating? A: No — batch governance plan is a plan file, not governance doc
- Q: Does CHANGELOG need updating? A: No — only latest entry read per Log Reading Step 2
- Q: Where do batch score docs live? A: logs/roundtable/ directory (new)

## Executor Manifest

Phases: S0, S1, S2, S3, S4
Deliverables:
  - S1: .agent/architect/AI_HANDOFF.md (updated with batch governance & RT scoring)
  - S2: logs/roundtable/ directory (created)
  - S3: Verify no broken references across repo
  - S4: Close + commit

Gates per phase:
  - S0: Repo cloned, verify key files present
  - S1: AI_HANDOFF.md changes applied, diff reviewed
  - S2: logs/roundtable/ exists, no naming conflicts
  - S3: grep search confirms no orphaned references
  - S4: verify_execution.py --final returns PASS

Coverage target: N/A (documentation update)
Forbidden actions:
  - Do NOT modify AGENTS.md
  - Do NOT modify OR_RULES.md
  - Do NOT modify ARCHITECTURE.md
  - Do NOT modify any .agent/executor/ scripts without explicit instruction
  - Do NOT modify any plan files in plans/ or plans/completed/

---

## Phase S0 — Opening

1. Clone repo: `cd /tmp && rm -rf SovereignAI && git clone --depth 1 https://github.com/AngusKingCAI/SovereignAI.git`
2. Verify: `.agent/architect/AI_HANDOFF.md`, `AGENTS.md`, `.agent/executor/ATTESTATION_TEMPLATE.md` exist
3. Run `verify_execution.py --init --plan batch-governance`
4. Post: `✅ S0 Complete: repo ready`

---

## Phase S1 — Update AI_HANDOFF.md

### S1.1 — Section 2: Document Authority Table

**Location**: After `roundtable-scores-plan-{N}.md` row, before `.devin/skills/*/SKILL.md` row

**Add two new rows**:

```markdown
| `roundtable-scores-batch{N}-{M}.md` | Round Table batch panelist performance tracking | Architect (compilation) | Executor (per plan instruction) |
| `batch{N}-{M}-governance-plan.md` | Pre-execution governance setup for a plan batch | Architect | Executor (per plan instruction) |
```

**Post**: `✅ S1.1: Document Authority table updated`

### S1.2 — Section 6 Step 6: Expand Round Table Score Document

**Location**: Replace the entire Step 6 section (currently single-plan only)

**New Step 6 content**:

```markdown
### Step 6 — Create Round Table Score Document (Final Round Only)

After all Round Table rounds complete for a plan or plan batch (clean pass achieved), add write-task to next plan's Executor Manifest to create a persistent score document for long-term tracking of panelist performance.

**Do NOT create this document after each round. Only after the final round.**

**Single-plan review**: Score document named `roundtable-scores-plan-{N}.md`.
**Batch review** (multiple plans reviewed together): Score document named `roundtable-scores-batch{N}-{M}.md` containing per-plan and per-reviewer breakdowns across all rounds.

1. Compile scores from all rounds
2. Post: `✅ Compiled All Scores: {N} rounds, {N} panelists, scores: {details}`
3. **Add to Executor Manifest**: Score document creation added as write-task in the next plan's Executor Manifest (or in the batch's governance plan).
4. Post: `✅ Added to Executor Manifest: {score-doc-filename}`

**Score Document Format (single plan)** (`roundtable-scores-plan-{N}.md`):

```markdown
# Round Table Scores — Plan {N}

**Date**: {YYYY-MM-DD}
**Plan**: plan-{N}.{i}.md
**Total Rounds**: {N}

## Panelist Scores (All Rounds)

| Panelist | Round 1 | Round 2 | ... | Round N | Average | Total Findings | Accepted | Rejected |
|----------|---------|---------|-----|---------|---------|----------------|----------|----------|
| {name} | {score} | {score} | ... | {score} | {avg} | {N} | {N} | {N} |

## Summary

- Total findings across all rounds: {N}
- Critical/High findings: {N}
- Medium/Low findings: {N}
- Clean pass achieved: {Yes / No}

## Notes

{any relevant notes about panelist performance or patterns}
```

**Score Document Format (batch)** (`roundtable-scores-batch{N}-{M}.md`):

```markdown
# Round Table Scores — Batch {N}-{M}

**Date**: {YYYY-MM-DD}
**Plans**: plan-{N} through plan-{M}
**Total Rounds**: {N}
**Total Reviews**: {N}

## Per-Review Verdicts

| Review | Verdict | CRITICAL | HIGH | MEDIUM | LOW | Notes |
|--------|---------|----------|------|--------|-----|-------|

## Per-Plan Verdicts

| Plan | Best Verdict | Worst Verdict | Findings |
|------|-------------|---------------|----------|

## Cross-Reviewer Comparison

{analysis of where reviewers agreed/disagreed, uncorroborated findings, partial-excerpt reviews}

## Summary

- Total findings across all rounds: {N}
- Clean pass achieved: {Yes / No}
- Architect patterns identified: {list}

## Notes

{panelist performance notes, process observations}
```

**Purpose**: These documents enable long-term tracking of which panelists consistently provide the highest-quality findings. Use historical scores to optimize panel composition over time.
```

**Post**: `✅ S1.2: Step 6 expanded with batch score format`

### S1.3 — NEW Step 8: Governance Amendment

**Location**: After Step 7 (Deliver), before end of Section 6

**Insert new section**:

```markdown
### Step 8 — Governance Amendment (Post-Clean-Pass, When Needed)

When a Clean Pass identifies new ARCHITECT_PATTERNS entries (Step 5) but no Executor has yet executed the reviewed batch, the Architect creates a governance plan that runs before the batch.

**Trigger**: Clean Pass achieved AND ARCHITECT_PATTERNS.md has new entries to write AND no prior Executor execution exists for the batch.

1. Architect creates `plans/batch{N}-{M}-governance-plan.md` following standard plan format (header, Executor Manifest, phases)
2. Governance plan includes write-tasks for:
   - ARCHITECT_PATTERNS.md entries (Step 5 output)
   - Round Table score document (Step 6 output)
   - Any handoff process updates (if needed)
3. Post: `✅ Created Governance Plan: batch{N}-{M}-governance-plan.md`
4. Executor runs governance plan before executing the batch (Phase 0 — runs first, no code changes)

**Naming**: `batch{N}-{M}-governance-plan.md` — identifies the batch scope. Not a numbered plan (does not consume plan numbers). Runs before the first plan in the batch.

**Scope**: Governance plans may only modify `.agent/architect/ARCHITECT_PATTERNS.md`, `logs/roundtable/roundtable-scores-batch{N}-{M}.md`, and `AI_HANDOFF.md` (process updates only). They must not modify code, tests, AR/OR rules, or architecture docs.
```

**Post**: `✅ S1.3: Step 8 (Governance Amendment) added`

### S1.4 — Version Bump

Update header:
```markdown
**Version:** v1.6
**Last Updated:** {today's date}
```

**Post**: `✅ S1.4: Version bumped to v1.6`

---

## Phase S2 — Create logs/roundtable/ Directory

1. Create directory: `logs/roundtable/`
2. Add `.gitkeep` or README explaining purpose
3. Verify no naming conflicts with existing logs structure
4. Post: `✅ S2: logs/roundtable/ created`

---

## Phase S3 — Verify No Broken References

Run grep/search across repo for:
- Any hardcoded references to `roundtable-scores-plan-` that should also handle `batch`
- Any log organization scripts that need to know about `logs/roundtable/`
- Any plan movement scripts that need to handle `batch*-governance-plan.md`

Files to check (do NOT modify, just report):
- `.agent/executor/scripts/organize_logs.py`
- `.agent/executor/scripts/move_completed_plans.py`
- `.agent/executor/ATTESTATION_TEMPLATE.md`
- `.agent/shared/PLANS.md`

**Post**: `✅ S3: Impact scan complete — {findings}`

---

## Phase S4 — Close

1. Stage changes: `git add .agent/architect/AI_HANDOFF.md logs/roundtable/`
2. Commit: `git commit -m "docs: add batch governance plan and batch RT score document support (v1.6)"`
3. Run `verify_execution.py --final --plan batch-governance`
4. Post: `✅ S4: Changes committed, attestation verified`

---

## Impact Summary

| File | Action | Risk |
|---|---|---|
| `.agent/architect/AI_HANDOFF.md` | Modified — 3 changes | Low (Architect-only doc) |
| `logs/roundtable/` | Created — new directory | Zero |
| `AGENTS.md` | NOT modified | N/A |
| `OR_RULES.md` | NOT modified | N/A |
| `ARCHITECTURE.md` | NOT modified | N/A |
| `.agent/executor/scripts/*` | NOT modified (scan only) | N/A |
