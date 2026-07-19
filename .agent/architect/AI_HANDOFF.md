# AI Handoff — SovereignAI

Process guide for the Architect. Vision: `PRINCIPLES.md`. Stack: Python v1, Windows.

---

## Repository

- **Repo**: https://github.com/AngusKingCAI/SovereignAI · `main`
- **Plan files**: `prompts/plan-{N}-Rev{n}.md`
- **Skills**: `.devin/skills/`
- **Design documents**: `.agent/architect/documents/`
- **All paths use `/`**

**Clone**: `cd /tmp && rm -rf SovereignAI && git clone https://github.com/AngusKingCAI/SovereignAI.git`

---

## Architect Workflow

1. Read logs end-to-end. Extract test counts, STOPs, deviations.
1.5. If user states execution log has been pushed: clone latest repo, read execution log, diff-check against plan expectations.
2. Verify repo state. Read `.agent/shared/CHANGELOG.md` latest entry in full. Read `.agent/shared/PLANS.md` current baseline. No scope creep.
3. Re-read governance documents in full:
   - `PRINCIPLES.md`
   - `.agent/executor/OR_RULES.md`
   - `.agent/executor/ARCHITECTURE.md`
   - `.agent/shared/LANDMINES.md`
   - `.agent/shared/DEBT.md` (check for triggered items; note resolutions;
     review open items — if trigger fired or plan resolves it, include resolution in upcoming plan)
4. Decision & Debt Action:
   - For each AR/OR rule with status "Proposed": if originating plan completed successfully,
     include status promotion to "Accepted" in plan body. If plan STOPped, leave as "Proposed" with note.
   - For each open debt in DEBT.md: if trigger fired or target plan reached,
     draft resolution steps for upcoming plan OR update status to "Blocked" with justification.
   - If debt is external dependency (e.g., DEBT-1): verify trigger condition, document status.
5. Review execution patterns. Identify rule gaps or recurring failure patterns from execution logs. Create rule specifications with IDs (OR{n}, AR{n}, {C|H|M|L}{n}).
   - New AR → assign ID, draft entry and verification script spec for plan body (Executor adds to ARCHITECTURE.md)
   - New OR → assign ID, draft entry and skill reference for plan body (Executor adds to OR_RULES.md)
   - New landmine → assign ID, draft entry and detection script spec for plan body (Executor adds to LANDMINES.md)
6. Research. Web search for new tech. Document findings in plan header.
7. Draft. N plan files + 1 brief (Rev 1 only) + 1 Round Table prompt per rev.
   - Include debt resolutions in plan body if any debts are being addressed.
   - Include rule status promotions in brief section 4 if any rules change status.
   - Include new AR/OR/landmine entries in plan body with explicit executor instructions.
8. Round Table. Runs until clean pass. Apply findings at discretion.
9. Score panelists. Post inline (GR11).
10. Deliver. User copies to `prompts/plan-{N}.md`.

---

## Round Table

See `PRINCIPLES.md` Workflow principles for clean-pass protocol. Severity levels:

**Severity**:
- **CRITICAL**: Data loss, security, irreversible damage. Blocks.
- **HIGH**: Executor STOP, test failure, broken build. Blocks.
- **MEDIUM**: Degraded functionality, tech debt. Address or document.
- **LOW**: Style, naming. Architect discretion.

**Prompt structure** (per GR10):
- **Full** (first pass): Roles + Material (brief + plans + dimensions + risks + settled findings) + Answer format (Severity/Evidence/Fix).
- **Diff** (re-check): Roles + Material (what changed since last rev only) + Answer format.

No host paths inside prompts (GR4).

---

## Batch Process

4 plans per batch. 1 shared brief (Rev 1 only). 1 Round Table prompt per rev. Scan every 5 plans (5, 10, 15…).

1. Draft 4 individual plan files + 1 brief (Rev 1) + 1 prompt per rev
2. Round Table reviews
3. Architect applies findings → Rev2 if needed
4. User copies finals to Executor

**Dependency**: If Plan {Xn} STOPs, all plans with `Depends on: {Xn}` also STOP. Binary.

---

## Plan Template

Plans ≤120 lines. Executable steps only. See `PRINCIPLES.md` Workflow principles for full guidance.

**Header**:
```
Depends on: <prerequisite plan numbers>
Vision principles: <which of 14 this satisfies/affects>
AR rules: <AR IDs relevant to this plan, or "none">
OR rules: <OR IDs relevant to this plan, or "none">
Open questions resolved: <which Q1-Q34, or "none">
```

**S0 — Opening**:
- S0.1: Run `/open`
- S0.2: Read `AGENTS.md` in full
- S0.3: Read plan header AR rules from `.agent/executor/ARCHITECTURE.md`. Read plan header OR rules from `.agent/executor/OR_RULES.md`.
- S0.4: Check `.agent/shared/DEBT.md` for deferred items.
- S0.5: If new tech stack, add research findings to plan header (per Architect Workflow step 6).

**Plan body (S1-Sn)**: Execute steps. Run `/verify` after each edit. HTML/CSS/JS plans: include "WILL edit" UI element list. Reference operational rules where pertinent (e.g., "Use VOR-2 for test suite execution").

**Closing**: Run `/close`.

**Token budget**: This Handoff + PRINCIPLES.md + plan file = context.

---

## Brief Format

One brief per batch. ≤80 lines. 10 sections in order:

1. **Context** — baseline, repo state.
2. **Plans in this batch** — table: plan #, title, depends on, vision principles, AR rules, OR rules.
3. **Rules proposed** — AR-ID/OR-ID/M-ID + rule/rejected alternative/consequence.
4. **Rules carried forward** — AR/OR/M-IDs only, pointer to `.agent/executor/ARCHITECTURE.md` or `.agent/executor/OR_RULES.md` or `.agent/shared/LANDMINES.md`.
5. **Questions for Round Table** — Q-ID.
6. **Open questions resolved** — list resolved Q-IDs; "none" if none.
7. **Risks flagged** — includes landmine pre-screen.
8. **Coverage target**
9. **Round Table protocol reminder**
10. **Superseded rules** — AR/OR/M-ID + pointer to replacement.

Missing/reordered sections block delivery (GR7).

---

## Document Relationships

| Document | Responsibility | Content Authority | File Writer |
|---|---|---|---|
| `AI_HANDOFF.md` | Process guide | Architect | Architect (user request only) |
| `PRINCIPLES.md` | Living principles | User + Architect | Architect (user request only) |
| `.agent/executor/OR_RULES.md` | Operational rules (UOR/VOR/OOR/COR) | Architect | Executor (per plan instruction) |
| `.agent/executor/ARCHITECTURE.md` | Architecture constraints | Architect | Executor (per plan instruction) |
| `PLANS.md` | Dynamic state, baselines, queue | Executor | Executor |
| `.agent/shared/LANDMINES.md` | Failure patterns | Architect | Executor (per plan instruction) |
| `.agent/shared/CHANGELOG.md` | Per-plan change log | Executor | Executor |
| `AGENTS.md` | Universal Invariants | Executor | Executor |
| `.agent/shared/DEBT.md` | Non-rule deferred items | Architect (identification), Executor (resolution) | Executor |
| `.devin/skills/*/SKILL.md` | Workflow skills | Architect | Architect (user request only) |

**SSOT**: Each fact in one document only.

**Read order**:
- Architect (new chat): AI_HANDOFF → PRINCIPLES → `.agent/executor/OR_RULES.md` → `.agent/executor/ARCHITECTURE.md` → PLANS → `.agent/shared/LANDMINES.md` → `.agent/shared/DEBT.md`
- Executor (S0.2): AGENTS.md → plan header AR/OR list → `.agent/executor/ARCHITECTURE.md` (relevant AR only) → `.agent/executor/OR_RULES.md` (relevant OR only)

**Rule References in Plans**:
- Architect lists specific AR/OR rules in plan header for executor context
- Executor reads only listed rules, not full documents
- Reference format: "Use {RULE-ID}" or "Follow {RULE-ID}"

---

## GR Rules (Architect)

GR1. Plan header lists `Vision principles:`, `AR rules:`, `OR rules:`, and `Open questions resolved:`.
GR2. Panelist responses attributed: `**Panelist**: <name/model>`.
GR3. Architect accepts/rejects every finding with reasoning.
GR4. No host-local paths in plans, briefs, prompts. Bare filenames for uploads; repo-relative paths for repo files.
GR5. New OR/AR rules: rule + rejected alternative + consequence — one line each.
GR6. Rules get stable IDs (AR{n}, OR{n}, M{n}). Status: Proposed / Accepted / Superseded. Never delete. Accepted → `.agent/executor/ARCHITECTURE.md` or `.agent/executor/OR_RULES.md` (SSOT). Rejected → needs new evidence to re-propose.
GR7. Briefs: 10 sections in order, ≤80 lines. Missing/reordered sections block delivery.
GR8. Screen plans against `.agent/shared/LANDMINES.md` before Round Table. BLOCKING landmines fixed before delivery.
GR9. Majority of panelists must return verdict before delivery. Conditional/block needs GR3 reasoning.
GR10. First pass per rev: full prompt. Re-checks: diff summary only. Round Table questions get Q-IDs. Answers become rule IDs or stay open.
GR11. Clean pass: post panelist scorecard inline (1-100, weighted toward accepted findings).
GR12. UI-change plans: check precedent first. ≤6 unresolved questions per plan, 2-4 options each. Overflow → Proposed rule IDs.
GR13. All rule changes go through Round Table. No silent edits to `.agent/executor/OR_RULES.md`, `.agent/executor/ARCHITECTURE.md`, or `.agent/shared/LANDMINES.md`.

---

## UR Rules (User Interaction)

UR1. When user asks for a file download, provide the download link immediately without asking follow-up questions. Do not ask "Do you want me to..." — just deliver the file.
