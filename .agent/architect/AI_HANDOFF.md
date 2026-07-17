# AI Handoff — SovereignAI

## Project

Local-first modular AI assistant for one user. Strong modular core. Wire as you go. UIs are separate processes consuming capability API. Every adapter/skill/memory backend/model interchangeable.

**Vision**: `.agent/architect/PRINCIPLES.md`. 14 principles + workflow principles.
**Stack**: Python v1, Windows only. Rust-migratable later.

---

## Repository

- **Repo**: https://github.com/AngusKingCAI/SovereignAI · **Branch**: `main`
- **Executor tree**: `C:/SovereignAI/`
- **Architect review clone**: `/tmp/SovereignAI/` (read-only)
- **Plan files**: `C:/SovereignAI/prompts/plan-{N}-Rev{n}.md`
- **Skills**: `.agent/skills/`
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
3. **Re-read** `.agent/executor/LANDMINES.md` + `.agent/architect/PRINCIPLES.md`.
4. **Review C9 proposals + scan for patterns.** Propose new rules or reject. Include in next plan's S0.
5. **Best practices research (web search).** For technical implementation plans (especially new tech stacks or frameworks), search for official docs, best practices, and common pitfalls. Document findings in plan header. Example: Textual ContentSwitcher import path, CSS patterns, async worker patterns. Use Context7 MCP for library-specific API questions (import paths, method signatures, version-specific behavior). Use web search for broader patterns (multi-panel layouts, testing strategies). Context7 prevents hallucinated APIs (P20.4 ContentSwitcher ImportError); web search catches framework-level best practices.
6. **Make plan files + context brief + Round Table prompt.** N plan files + 1 brief (per Brief Format) + 1 prompt (per Round Table Prompt, full or diff-summary per GR14).
7. **Pause for Round Table.** Runs until clean pass. Apply findings at discretion.
8. **Score panelists (GR16).** Posted inline in chat.
9. **Deliver.** Tell User to copy to `C:/SovereignAI/prompts/plan-{N}.md`.

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
- S0.4: If plan involves new tech stack/framework, add best practices research (web search) findings to plan header per Architect Workflow step 5. Add S0.4 to Plan Template if this is the first plan requiring step 5.

**Plan body (S1-Sn)**: Execute steps. Run `/verify` after each edit. For HTML/CSS/JS plans: include a "WILL edit" UI element list.

**Closing**: Run `/close`.

---

## Document Relationships

| Document | Responsibility | Who writes |
|---|---|---|
| `.agent/architect/AI_HANDOFF.md` | Process guide | Architect |
| `.agent/architect/PRINCIPLES.md` | Living principles (14 core + workflow) | User + Architect |
| `.agent/executor/PLANS.md` | Dynamic state, baselines, queue | Executor |
| `.agent/executor/LANDMINES.md` | Failure patterns | Executor |
| `.agent/executor/CHANGELOG.md` | Per-plan change log | Executor |
| `AGENTS.md` | Rules (AR + OR) | Executor |
| `.agent/executor/DECISIONS.md` | Architectural decisions | Executor |
| `.agent/executor/DEBT.md` | Deferred items | Executor |
| `.devin/skills/*/SKILL.md` | Workflow skills | Architect |

**SSOT**: Each fact in one document only.

**Read order**:
- Architect (new chat): .agent/architect/AI_HANDOFF → .agent/architect/PRINCIPLES.md → .agent/executor/PLANS.md → .agent/executor/LANDMINES.md → .agent/executor/DECISIONS.md → .agent/executor/DEBT.md
- Executor (S0.2): AGENTS.md (consult .agent/executor/LANDMINES.md if ambiguous)

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
GR16. On clean pass, Architect posts a panelist scorecard inline: 1-100 quality score weighted toward accepted findings (GR4) over volume and recommendation (keep as-is | narrow scope | consolidate | cut).
GR17. Before drafting a plan with UI changes, Architect checks existing specs/prior plans/context docs for precedent and states what was checked and why it didn't resolve the question. Only unresolved UI-shape questions go to the User — ≤6 per plan, 2-4 options each. Overflow beyond 6 is logged as Proposed DD-IDs for Round Table ratification instead of being dropped. "You decide" → Architect decides and logs it as a Proposed DD-ID the same way.

GR18. Rules in AGENTS.md must use minimal tokens whilst maintaining functionality. Constraint + consequence only; context belongs in LANDMINES.md (linked). Not a hard char limit — function over brevity. Token cost: AGENTS.md read in full per OR14/OR45; verbose rules cost ~200 tokens per re-read. SWE-1.6 research (Cognition 2026-07) shows concise function-first rules are followed more verbatim.