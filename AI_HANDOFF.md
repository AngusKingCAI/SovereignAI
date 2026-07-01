# AI Handoff — SovereignAI

## Project

Local-first modular AI assistant for one user. Strong modular core. Wire as you go. UIs are separate processes consuming capability API. Every adapter/skill/memory backend/model interchangeable.

**Vision**: `principles.md`. 14 principles + workflow principles.
**Stack**: Python v1, Windows only. Rust-migratable later.

---

## Repository

- **Repo**: https://github.com/AngusKingCAI/SovereignAI · **Branch**: `main`
- **Executor tree**: `C:/SovereignAI/`
- **Architect review clone**: `/tmp/SovereignAI/` (read-only)
- **Plan files**: `C:/SovereignAI/prompts/plan-{N}-Rev{n}.md`
- **All paths use `/`**

**Clone instructions**: When the User says "log uploaded" or "check the repo", clone the latest state:
```
cd /tmp && rm -rf SovereignAI && git clone --depth 1 https://github.com/AngusKingCAI/SovereignAI.git
```
This ensures the Architect always reviews current state, not a stale clone.

---

## Architect Workflow

1. **Read execution logs end-to-end.** Extract test counts, scan results, STOPs, deviations.
2. **Verify repo state.** Tag on origin, CHANGELOG matches, PLANS.md updated, no scope creep.
3. **Re-read** `LANDMINES.md` + `principles.md`.
4. **Review C9 proposals + scan for patterns.** Propose new rules or reject. Include in next plan's S0.
5. **Make plan files + context brief + Round Table prompt.** N plan files + 1 brief (per Brief Format) + 1 prompt (per Round Table Prompt, full or diff-summary per GR14).
6. **Pause for Round Table.** Runs until clean pass. Apply findings at discretion.
7. **Score panelists (GR16).** Posted inline in chat.
8. **Deliver.** Tell User to copy to `C:/SovereignAI/prompts/plan-{N}.md`.

---

## Round Table

Runs until clean pass (no unaddressed CRITICAL/HIGH). Each rev brings new evidence — no re-litigating settled findings. User may force-stop. Structured output: Severity + Evidence table. Items without evidence auto-dropped.

**Severity**:
- **CRITICAL**: Data loss, security, irreversible damage. Blocks.
- **HIGH**: Executor STOP, test failure, broken build. Blocks.
- **MEDIUM**: Degraded functionality, tech debt. Address or document.
- **LOW**: Style, naming. Architect discretion.

---

## Batch Process

4 plans per batch. 1 shared brief. Scan every 5 plans (5, 10, 15…).

1. Draft N individual plan files + 1 brief
2. Round Table reviews
3. Architect applies findings → Rev2 if needed
4. User copies finals to Executor

**Dependency**: If Plan {Xn} STOPs, all plans with `Depends on: {Xn}` also STOP. Binary.

---

## Plan Template

Plans ≤120 lines. Executable steps only.

**Header**:
```
Depends on: <prerequisite plan numbers>
Vision principles: <which of 14 this satisfies/affects>
Open questions resolved: <which Q1-Q34, or "none">
```

**S0 — Opening**:
- S0.1: Run `/open`
- S0.2: Read `AGENTS.md` in full
- S0.2.5: Re-read `AGENTS.md` if governance patch added rules
- S0.3: Add new rules, commit before coding

**Plan body (S1-Sn)**: Execute steps. Run `/verify` after each edit. For HTML/CSS/JS plans: include a "WILL edit" UI element list.

**Closing**: Run `/close`.

---

## Document Relationships

| Document | Responsibility | Who writes |
|---|---|---|
| `AI_HANDOFF.md` | Process guide | Architect |
| `principles.md` | Living principles (14 core + workflow) | User + Architect |
| `PLANS.md` | Dynamic state, baselines, queue | Executor |
| `LANDMINES.md` | Failure patterns | Executor |
| `CHANGELOG.md` | Per-plan change log | Executor |
| `AGENTS.md` | Rules (AR + OR) | Executor |
| `DECISIONS.md` | Architectural decisions | Executor |
| `DEBT.md` | Deferred items | Executor |
| `.devin/workflows/*.md` | Workflow steps | Architect |

**SSOT**: Each fact in one document only.

**Read order**:
- Architect (new chat): AI_HANDOFF → principles → PLANS → LANDMINES → DECISIONS → DEBT
- Executor (S0.2): AGENTS.md (consult LANDMINES if ambiguous)

---

## One brief per batch. ≤80 lines. Sections in order:

1. **Context** — baseline, repo state, workflow file sizes.
2. **Plans in this batch** — table: plan #, title, depends on, vision principles.
3. **Decisions proposed** — DD-ID + rule/rejected alternative/consequence (GR6, GR8).
4. **Decisions carried forward** — DD-IDs only, pointer to DECISIONS.md (GR9).
5. **Questions for Round Table** — Q-ID, distinct from resolved list (GR15).
6. **Open questions resolved** — per GR2; "none" if none.
7. **Risks flagged** — includes landmine pre-screen (GR12).
8. **Coverage target**
9. **Round Table protocol reminder**
10. **Superseded decisions** — DD-ID + pointer to replacement (GR7).

---

## Round Table Prompt

One prompt per delivery. Structure per GR14:

**Full prompt** (first pass):
1. **Roles** — find issues, not fixes; assume failure, require a concrete
   scenario; sign `**Panelist**: <name/model>` (GR3).
2. **Material** — full brief, all plan files, review dimensions, risks to
   verify/refute, settled findings (do-not-relitigate, GR10).
3. **Answer format** — Severity/Evidence/Fix per finding, other concerns,
   explicit "Clean pass" if none, sign-off.

**Diff-summary prompt** (re-check):
1. **Roles** — same as full.
2. **Material** — what changed since last rev only (DD-IDs, Q-IDs, findings
   addressed). No resend of unchanged brief/plans.
3. **Answer format** — same as full, scoped to the diff.

No host paths inside the prompt (GR5).

---

## GR Rules (Architect)

GR1. Every plan header lists `Vision principles:` satisfied/affected.
GR2. Every plan header lists `Open questions resolved:`.
GR3. Every panelist response must be attributed: `**Panelist**: <name/model>`.
GR4. Architect explicitly accepts/rejects every Round Table finding with reasoning.
GR5. No host-local paths in plans, briefs, or roundtable prompts. Bare filenames for uploads; repo-relative paths for repo files.
GR6. New OR/AR rules state: the rule, rejected alternative(s), and consequence — one line each.
GR7. Decisions carry status: Proposed / Accepted / Superseded (linked). Never delete — move superseded items to their own subsection.
GR8. Decisions get stable IDs (DD1, DD2...) for precise reference.
GR9. On Accepted, decision moves to DECISIONS.md under its DD-ID (SSOT). Brief keeps a pointer, not a duplicate.
GR10. Rejected DD-IDs can't be re-proposed without new evidence.
GR11. Briefs follow the Brief Format section list, ≤80 lines. Missing/reordered sections block delivery.
GR12. Architect screens plans against LANDMINES.md before Round Table. BLOCKING landmines are fixed before delivery, not deferred to findings.
GR13. Majority of assigned panelists must return a verdict (name/model + pass/conditional/block) before delivery. Conditional/block verdicts need Architect's GR4 reasoning before delivery.
GR14. First pass per rev: full prompt (brief + plans + dimensions). Re-checks of unchanged findings: diff summary only.
GR15. Open questions for Round Table (distinct from GR2's "resolved" list) get a
Q-ID. Answers become DD-IDs or stay logged open next rev
GR16. On clean pass, Architect posts a panelist scorecard inline: 1-100 quality score weighted toward accepted findings (GR4) over volume, total time (GR17), quality-per-time ratio, and recommendation (keep as-is | narrow scope | consolidate | cut).
GR17. Round Table reviews state start/end time and duration in seconds. Self-reported timing isn't a direct quality signal — Architect flags durations implausible for the review's depth as a mark against GR16 reliability.

