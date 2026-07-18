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
2. Verify repo state. Spot-check `.agent/shared/CHANGELOG.md` latest entry (first 10 lines). PLANS.md updated. No scope creep.
3. Re-read `.agent/shared/LANDMINES.md` + `PRINCIPLES.md` + `.agent/shared/RULE_LIFECYCLE.md`.
4. Review execution patterns. Identify rule gaps or recurring failure patterns from execution logs. Create rule specifications with IDs (OR{n}, AR{n}, {C|H|M|L}{n}) directly.
   - New AR → assign ID, implement directly: add to ARCHITECTURE.md with verification script
   - New OR → assign ID, implement directly: edit relevant skill with OR reference
   - New landmine → assign ID, implement directly: add to LANDMINES.md with detection script
   Implementation per RULE_LIFECYCLE.md IMPLEMENT stage.
5. Check `.agent/shared/DEBT.md` for non-rule deferred items (features, tech debt, security fixes).
6. Research. Web search for new tech. Document findings in plan header.
7. Draft. N plan files + 1 brief (Rev 1 only) + 1 Round Table prompt per rev.
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
Open questions resolved: <which Q1-Q34, or "none">
```

**S0 — Opening**:
- S0.0: If resuming from prior execution, clone latest repo and verify execution log state.
- S0.1: Run `/open` (if skill tool fails, execute via shell fallback per AGENTS.md Rule 11)
- S0.2: Read `AGENTS.md` in full
- S0.3: Check `.agent/shared/DEBT.md` for other deferred items (non-rule items).
- S0.4: If new tech stack, add research findings to plan header (per Architect Workflow step 7).

**Plan body (S1-Sn)**: Execute steps. Run `/verify` after each edit (if skill tool fails, execute via shell fallback per AGENTS.md Rule 11). HTML/CSS/JS plans: include "WILL edit" UI element list. Reference operational rules where pertinent (e.g., "Use VOR-2 for test suite execution").

**Closing**: Run `/close` (if skill tool fails, execute via shell fallback per AGENTS.md Rule 11).

**Token budget**: This Handoff + PRINCIPLES.md + plan file = context.

---

## Brief Format

One brief per batch. ≤80 lines. 10 sections in order:

1. **Context** — baseline, repo state.
2. **Plans in this batch** — table: plan #, title, depends on, vision principles.
3. **Decisions proposed** — DD-ID + rule/rejected alternative/consequence.
4. **Decisions carried forward** — DD-IDs only, pointer to `.agent/shared/DECISIONS.md`.
5. **Questions for Round Table** — Q-ID.
6. **Open questions resolved** — list resolved Q-IDs; "none" if none.
7. **Risks flagged** — includes landmine pre-screen.
8. **Coverage target**
9. **Round Table protocol reminder**
10. **Superseded decisions** — DD-ID + pointer to replacement.

Missing/reordered sections block delivery (GR7).

---

## Document Relationships

| Document | Responsibility | Who writes |
|---|---|---|
| `AI_HANDOFF.md` | Process guide | Architect |
| `PRINCIPLES.md` | Living principles | User + Architect |
| `.agent/shared/RULE_LIFECYCLE.md` | Rule lifecycle process | Architect |
| `.agent/shared/OR_RULES.md` | Operational rules (UOR/VOR/OOR/COR) | Architect |
| `PLANS.md` | Dynamic state, baselines, queue | Executor |
| `.agent/shared/LANDMINES.md` | Failure patterns | Executor |
| `.agent/shared/CHANGELOG.md` | Per-plan change log | Executor |
| `AGENTS.md` | Universal Invariants | Executor |
| `.agent/shared/DECISIONS.md` | Architectural decisions | Executor |
| `.agent/shared/DEBT.md` | Non-rule deferred items (features, tech debt, security) | Executor |
| `.devin/skills/*/SKILL.md` | Workflow skills | Architect |

**SSOT**: Each fact in one document only.

**Read order**:
- Architect (new chat): AI_HANDOFF → PRINCIPLES → `.agent/shared/RULE_LIFECYCLE.md` → `.agent/shared/OR_RULES.md` → `.agent/shared/ARCHITECTURE.md` → PLANS → `.agent/shared/LANDMINES.md` → `.agent/shared/DECISIONS.md` → `.agent/shared/DEBT.md`
- Executor (S0.2): AGENTS.md (consult `.agent/shared/LANDMINES.md` if ambiguous)

**Rule References in Plans**:
- Architect may reference specific operational rules in plan steps (e.g., "Use VOR-2 for test suite execution")
- Reference format: "Use {RULE-ID}" or "Follow {RULE-ID}"
- Executor reads relevant rule sections from OR_RULES.md when executing

*Pending: Document structure will be revised as part of workflow optimisation.*

---

## GR Rules (Architect)

GR1. Plan header lists `Vision principles:` and `Open questions resolved:`.
GR2. Panelist responses attributed: `**Panelist**: <name/model>`.
GR3. Architect accepts/rejects every finding with reasoning.
GR4. No host-local paths in plans, briefs, prompts. Bare filenames for uploads; repo-relative paths for repo files.
GR5. New OR/AR rules: rule + rejected alternative + consequence — one line each.
GR6. Decisions get stable IDs (DD1...). Status: Proposed / Accepted / Superseded. Never delete. Accepted → `.agent/shared/DECISIONS.md` (SSOT). Rejected → needs new evidence to re-propose.
GR7. Briefs: 10 sections in order, ≤80 lines. Missing/reordered sections block delivery.
GR8. Screen plans against `.agent/shared/LANDMINES.md` before Round Table. BLOCKING landmines fixed before delivery.
GR9. Majority of panelists must return verdict before delivery. Conditional/block needs GR3 reasoning.
GR10. First pass per rev: full prompt. Re-checks: diff summary only. Round Table questions get Q-IDs. Answers become DD-IDs or stay open.
GR11. Clean pass: post panelist scorecard inline (1-100, weighted toward accepted findings).
GR12. UI-change plans: check precedent first. ≤6 unresolved questions per plan, 2-4 options each. Overflow → Proposed DD-IDs.

---

## UR Rules (User Interaction)

UR1. When user asks for a file download, provide the download link immediately without asking follow-up questions. Do not ask "Do you want me to..." — just deliver the file.
