# AI Handoff — SovereignAI

## Project

Local-first modular AI assistant for one user. Strong modular core. Wire as you go. UIs are separate processes consuming capability API. Every adapter/skill/memory backend/model interchangeable.

**Vision**: `project-vision-Rev5.md` (locked). 14 principles.
**Stack**: Python v1, Windows only. Rust-migratable later.

---

## Roles

| Actor | Job | Tools |
|---|---|---|
| **User** | Bridges Architect ↔ Executor ↔ Round Table. Copies files between. Pastes logs. | IM chat |
| **Architect** | 7-step workflow. Creates plans/briefs. Never edits repo directly. Read-only git. | Review clone |
| **Executor** | Executes plans. Runs `/open`, `/verify`, `/close`, `/scan`. Commits/tags/pushes. | Git Bash, `C:/SovereignAI/` |

---

## Architect Workflow

1. **Read execution logs end-to-end.** Extract test counts, scan results, STOPs, deviations.
2. **Verify repo state.** Tag on origin, CHANGELOG matches, PLANS.md updated, no scope creep.
3. **Re-read** `LANDMINES.md` + `project-vision-Rev5.md`.
4. **Review C9 proposals + scan for patterns.** Propose new rules or reject. Include in next plan's S0.
5. **Make plan files + context brief.** N files at `/home/z/my-project/download/plan-{N}-Rev1.md` + 1 brief.
6. **Pause for Round Table.** Runs until clean pass. Apply findings at discretion.
7. **Deliver.** Tell User to copy to `C:/SovereignAI/prompts/plan-{N}.md`.

---

## Round Table

Runs until clean pass (no unaddressed CRITICAL/HIGH). Each rev brings new evidence — no re-litigating settled findings. User may force-stop. Structured output: Severity + Evidence table. Items without evidence auto-dropped.

**Severity**:
- **CRITICAL**: Data loss, security, irreversible damage. Blocks.
- **HIGH**: Executor STOP, test failure, broken build. Blocks.
- **MEDIUM**: Degraded functionality, tech debt. Address or document.
- **LOW**: Style, naming. Architect discretion.

**Adjudication (GR4)**: Architect explicitly accepts/rejects every finding with reasoning.

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

**Plan body (S1-Sn)**: Execute steps. Run `/verify` after each edit. For HTML/CSS/JS plans: include a "WILL edit" UI element list (element IDs to verify at `/close` step 15).

**Closing**: Run `/close`.

---

## Document Relationships

| Document | Responsibility | Who writes |
|---|---|---|
| `AI_HANDOFF.md` | Process guide | Architect |
| `project-vision-Rev5.md` | Vision, principles, open questions | User + Architect |
| `PLANS.md` | Dynamic state, baselines, queue | Executor |
| `LANDMINES.md` | Failure patterns | Executor |
| `CHANGELOG.md` | Per-plan change log | Executor |
| `AGENTS.md` | Rules (AR + OR) | Executor |
| `DECISIONS.md` | Architectural decisions | Executor |
| `DEBT.md` | Deferred items | Executor |
| `.devin/workflows/*.md` | Workflow steps | Architect |

**SSOT**: Each fact in one document only.

**Read order**:
- Architect (new chat): AI_HANDOFF → vision → PLANS → LANDMINES → DECISIONS → DEBT
- Executor (S0.2): AGENTS.md (consult LANDMINES if ambiguous)

---

## GR Rules (Architect)

GR1. Every plan header lists `Vision principles:` satisfied/affected.
GR2. Every plan header lists `Open questions resolved:`.
GR3. Every brief requires panelist sign-off: `**Panelist**: <name/model>`.
GR4. Architect explicitly accepts/rejects every Round Table finding with reasoning.
GR5. Claude version for OR73 spec-match review: Sonnet 4.6 or later. Update this line when bumping.
