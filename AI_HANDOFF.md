# AI Handoff — SovereignAI

## Project Overview

SovereignAI is a local-first, modular AI assistant framework for a single user. Runs locally by default, escalates to cloud when needed, designed to absorb new models/adapters/skills/memory backends without rewrites.

**Philosophy**: Strong modular core. Wire as you go. UIs are separate processes consuming the core's capability API. Every adapter, skill, memory backend, and model is interchangeable. We prompt the model's reasoning — we don't code it.

**Canonical vision**: `project-vision-Rev5.md` (locked). 14 principles, 40 success criteria, 10 open questions for Plan 1. All architecture must comply.

**Stack**: Python v1, Rust-migratable later. Contracts are language-agnostic. v1 targets Windows only.

---

## How to use this document

This is the **static process guide** for the Architect role — how to make plans, how Round Table review works, how plans are structured. Dynamic state (baselines, queue) → `PLANS.md`. Failure patterns → `LANDMINES.md`.

**New Architect chat** (receiving handoff + execution log):
1. Clone: `git clone https://github.com/AngusKingCAI/SovereignAI.git` → `/home/z/my-project/sovereignai-review/`
2. Read this handoff end-to-end
3. Read in order: `project-vision-Rev5.md` → `PLANS.md` → `LANDMINES.md` (L1–L23 inherited from sovereign-ai; new start at L24) → `DECISIONS.md` → `DEBT.md`
4. Start Architect Workflow below

**Starting fresh** (no execution log): repo should have `prompt-0` (governance docs only, no code). Begin drafting Plans 1–4.

---

## Roles

| Actor | Job | Tools |
|---|---|---|
| **User** | Pastes Executor log to Architect. Bridges Round Table (sends plan files + brief, pastes findings back). Copies Architect deliverables to Executor's working tree. After `/close`, copies chat log to `logs/execution-log-prompt-{N}.md` and asks Executor to commit/push it. | IM chat; file copy |
| **Architect** | 7-step post-execution workflow. Creates plans, context briefs, revised plans. **Never edits repo directly** — produces files in `/home/z/my-project/download/`. Read-only git (`git fetch origin`, `git show`, `git log`). No push, no commit, no tool runs. | Read-only review clone |
| **Executor** | Executes plans. Runs `/open`, `/verify`, `/close`, `/scan`. Runs tests, ruff, mypy, bandit, pip-audit, vulture, custom AR checks. Commits, tags, pushes. Updates CHANGELOG, PLANS, LANDMINES, DEBT. Proposes rules via C9. | Git Bash; `C:/SovereignAI/` |

**Key separation**: Architect never commits/pushes. Executor never creates plans/briefs. User is the bridge.

---

## Repository Bootstrap

- **Repo**: https://github.com/AngusKingCAI/SovereignAI · **Branch**: `main`
- **Tags**: `prompt-{N}` per completed plan. `prompt-0` = bootstrap (governance docs only, no code). Tag-push gate mandatory.
- **Executor tree**: `C:/SovereignAI/` · **Architect review clone**: `/home/z/my-project/sovereignai-review/` (read-only)
- **Plan files**: `C:/SovereignAI/prompts/plan-{N}-Rev{n}.md` (flat directory, no decade subfolders)
- **All paths use `/`** — Windows accepts both; User's keyboard lacks `\`

---

## Architect Workflow

7 steps in order after the User pastes an execution log. Do not skip. Do not improvise.

**Step 1 — Read execution logs end-to-end.** Extract: actual test counts for ALL suites, ruff/mypy/bandit/pip-audit/vulture counts, STOP conditions triggered, C9 rule proposals, deviations from plan. If a new test suite was introduced, include it — the count list is not fixed.

**Step 2 — Verify repo state.** `git fetch origin` → tag exists on origin → CHANGELOG entry matches → commit stat matches plan scope (no scope creep) → `PLANS.md` updated (completed row, baselines, queue shift). Flag mismatches to User.

**Step 3 — Re-read `LANDMINES.md` and `project-vision-Rev5.md`.** Refresh on failure patterns and principles before drafting. Do NOT re-read this handoff (you're already in it). Do NOT re-read `AGENTS.md` (Executor reads that; Architect references it only if a rule is ambiguous).

**Step 4 — Review C9 proposals and scan for patterns.** Architect is the rule authority — Executor proposes, Architect disposes.
- Read Executor's C9 proposals (if any)
- Independently scan the log for patterns the Executor may have missed: scope creep, repeated failures, workarounds, multi-attempt steps
- Cross-reference `LANDMINES.md` — already captured? No new rule needed. Not captured? Consider proposing one
- Cross-reference `AGENTS.md` — rule already exists but wasn't followed? Enforcement problem, not a new rule. No rule? Propose one
- New rule → include in next plan's S0 instructions (Executor adds to `AGENTS.md` at `/open` step 4, with source: "Source: L{n}" or "Source: Round Table Rev{n}"). Write in compact style: one to three sentences, verb-first, actionable content only — no narrative backstory, no repeated framing.
- Reject C9 proposals if redundant/unnecessary — document rejection in context brief

**Step 5 — Make plan files + context brief.** N individual files at `/home/z/my-project/download/plan-{N}-Rev1.md` + one shared brief at `/home/z/my-project/download/plan-{X1}-{X4}-batch-Rev1-context-brief.md`. Rev{n} notation: one file per plan per revision. Context brief created for Rev1 only — Rev2+ brief not required. All Revs kept forever. Plan files contain ONLY what the Executor needs (S0, body, STOP conditions, file lists, closing, header lines). Briefs follow the 3-part scaffold below.

**Step 6 — Pause for Round Table review.** User sends plan files + brief (Rev1) or revised files only (Rev2+) to Round Table, then pastes findings back. Round Table reviews only — does not create or edit files. Wait for User's paste. Apply findings at Architect's discretion.

**Step 7 — Deliver.** Tell User: "Copy `plan-{N}-Rev{n}.md` to `C:/SovereignAI/prompts/plan-{N}.md` and point the Executor at it."

---

## Brief Scaffold

All briefs follow this 3-part scaffold. Briefs reference it ("per the scaffold in AI_HANDOFF.md") and do not re-describe it.

**Part 1 — Roles/Rules (~5 lines)**
- Reviewer's role: "Your job is to find issues, not rewrite the plan"
- Adversarial framing: "Assume this plan will fail — identify how"
- Proof requirement: "Each issue must include a concrete failure scenario"
- Sign-off (GR3): "End with `**Panelist**: <name/model>`. Anonymous responses flagged but adjudicated; named preferred."

**Part 2 — Context (~30–40 lines)**
- Plan scope summary (files, components)
- Key dependencies (existing modules this builds on)
- **Author's reasoning (clearly labeled)**: "My reasoning: [X]. Attack this reasoning — don't ratify the conclusion."
- Named open questions — specific and substantive; vague or confirmatory questions banned
- Architect's confidence level on key decisions (e.g., "65% confident on the filesystem layout")
- For architecture-affecting plans: which `project-vision-Rev5.md` principles this plan satisfies or violates (cross-reference `Vision principles:` header line)

**Part 3 — Answer Format (~5 lines)**
- Specify response structure (flexible, not rigid boxes)
- ALWAYS include an "other concerns" open field
- Permit "No issues found" — do not force the reviewer to invent problems

**Anti-sycophancy measures**
- Open with pre-mortem frame: "Assume this plan failed in 6 months. List the most plausible reasons."
- Permit "No issues found" explicitly
- Require proof: each issue must cite a concrete failure scenario and evidence from the codebase
- Ban style/formatting/speculative-future/feature-request comments

**Anchoring mitigation**
- State Architect's reasoning in a clearly labeled block
- Instruct reviewer: "Criticize my reasoning, not my conclusion"
- Disclose confidence explicitly ("I'm 65% confident on step 3")

---

## Round Table Review Process

**What goes to Round Table**: All plans except scan prompts. Scan prompts (5, 10, 15…) are mechanical — no architectural decisions, no design review needed. Go straight to Executor.

**Composition**: Referred to collectively as "the Round Table." No fixed composition — User chooses who to send each brief to. No quorum — adjudicate whatever responses come back. Panelist sign-off mandatory by default (GR3); User can override to accept anonymous responses.

**Process**:
1. Architect drafts plans + brief
2. User bridges to Round Table (files + brief + short read-me-first prompt)
3. Round Table reviews, returns findings (with sign-off)
4. Architect judges, adopts highest-scoring recommendations — even if it contradicts Architect's original position
5. For roadmap-level decisions (philosophy changes, feature arc launches, architecture decisions): User reviews Architect's judgment before final decision
6. User can override CRITICAL with explicit sign-off + documented accepted risk

**Severity rubric**:
- **CRITICAL**: Data loss, security vulnerability, or irreversible damage. Blocks clean pass — no exceptions (formally; User override with documented accepted risk in practice)
- **HIGH**: Would cause Executor STOP, test failure, broken build, or Windows incompatibility. Blocks clean pass; must be resolved or explicitly overruled with User sign-off
- **MEDIUM**: Degraded functionality, poor UX, or tech debt. Should be addressed; if accepted, document reasoning in adjudication log
- **LOW**: Style, naming, speculative features, unvalidated perf optimisations. Accept/reject at Architect discretion with one-paragraph reasoning

If panelist and Architect disagree on severity, treat as the higher severity until resolved.

**Clean pass**: (a) No unaddressed substantiated CRITICAL or HIGH; (b) remaining MEDIUM/LOW documented as accepted/rejected with reasoning in adjudication log.

**Adjudication (GR4)**: Architect must explicitly accept or reject every finding with reasoning. No silent dismissals. Recorded in: brief's adjudication log (Rev1) or a separate adjudication section in the revised plan file (Rev2+).

---

## Batch Plan Process

**Structure**: Batches of 4 plans, drafted as individual files from the start. 1 shared batch context brief. Scan every 5 plans (5, 10, 15…). Plan 1 is a regular plan — no special "Architecture Decision Plan" treatment.

**Cadence**: Plans 1–4 → Scan 5 → Plans 6–9 → Scan 10 → Plans 11–14 → Scan 15 → …

**Why separate files**: The combined-file + split approach from sovereign-ai introduced mechanical transformation bugs (stale references, missing sections). Separate files eliminate this — what the Round Table reviews IS what the Executor executes.

**Step 1 — Draft individual plan files.** N files, one per plan:
```
/home/z/my-project/download/plan-{X1}-Rev1.md
/home/z/my-project/download/plan-{X2}-Rev1.md
/home/z/my-project/download/plan-{X3}-Rev1.md
/home/z/my-project/download/plan-{X4}-Rev1.md
```
Each file is self-contained: S0 Opening, body, STOP conditions, Files WILL create/edit/NOT edit, Closing, header lines (`Depends on:`, `Vision principles:`, `Open questions resolved:`).

**Step 2 — Draft batch context brief.** One shared file:
```
/home/z/my-project/download/plan-{X1}-{X4}-batch-Rev1-context-brief.md
```
Follows the 3-part scaffold, plus: cross-plan dependency map, sequencing risks, Architect's confidence by plan, named open questions, vision principle compliance by plan.

**Step 3 — Round Table review.** User sends N individual files + 1 brief. Architect collects all responses, judges, applies substantiated findings to individual files.

**Step 4 — Fix and re-review.** Revise individual files as needed (`plan-{X1}-Rev2.md`, etc.). Rev2+ needs no new brief unless revisions are substantial (new architecture, changed dependencies). Repeat until clean pass.

**Execution failure within a batch**: If Executor hits STOP on Plan {Xn}, all plans with `Depends on: {Xn}` (directly or transitively) must also STOP. Dependency is determined by `Depends on:` header — not User judgment. Plans with no dependency on {Xn} may proceed if their prerequisite tags are confirmed on origin. Partial outputs do not lift the dependency STOP — it's binary. After a STOP, Architect revises the failed plan and any dependents; revisions must go through Round Table before re-execution.

---

## Scan Prompt

Scan prompts occur every 5 plans (5, 10, 15…) — verify baselines, fix accumulated issues, reconcile state before the next batch.

**Purpose**: After 4 plans, the repo accumulates small inconsistencies (stale imports, minor type errors, outdated docstrings, uncaptured LANDMINES, suppressed ruff warnings). Scan cleans them before the next batch.

**Drafting order constraint**: Next batch must NOT be drafted or Round Table-reviewed until the scan prompt completes and its changes (including any C9 rules) are committed to origin. Ensures the batch is drafted against the post-scan state.

**Batch failure interaction**: Scan must not execute until all plans in the current batch have completed. Running scan on a partial batch produces false positives.

**Structure**: Standard S0 opening + `/close` closing. Gets its own `prompt-{N}` tag. Scan workflow is in `.devin/workflows/scan.md` — the scan prompt just tells the Executor to run `/scan`. Skips Round Table.

---

## Architect Operating Discipline

GR rules (General Rules) mirror the AR/OR scheme for the Executor.

**GR1 — Vision principle compliance.** Every plan MUST include `Vision principles:` in its header listing which of the 14 principles the plan satisfies or affects. If a plan violates a principle: `Vision principles: violates 3 (no provider lock-in) — justification: <reason>`. Round Table uses this line to verify architectural fidelity.

**GR2 — Open questions resolved.** Every plan header MUST include `Open questions resolved:` listing which Q1–Q34 the plan resolves. If none: `Open questions resolved: none`.

**GR3 — Brief sign-off requirement.** Every brief MUST include the panelist sign-off requirement in Part 1: "End with `**Panelist**: <name/model>`. Anonymous flagged but adjudicated; named preferred." User can override.

**GR4 — Explicit adjudication.** Architect MUST explicitly accept or reject every Round Table finding with reasoning. No silent dismissals. Format:
```
Finding: <description> — Severity: <CRITICAL/HIGH/MEDIUM/LOW> — Panelist: <name>
Adjudication: <ACCEPTED/REJECTED/PARTIALLY ACCEPTED>
Reasoning: <one paragraph>
Action: <what changed, or "no change — reasoning above">
```

---

## Plan Template

Architect copies this into every plan file. Plan file = Executor's instruction manual. Contains ONLY what the Executor needs.

**Header lines**:
```
Depends on: <prerequisite plan numbers, or empty>
Vision principles: <which of the 14 principles this plan satisfies/affects>
Open questions resolved: <which open questions this plan resolves, or "none">
```

**S0 — Opening**:
- **S0.1**: Run `/open` — verifies previous prompt's tag on origin, confirms working copy is clean and on `main`. If missing or fails, STOP and report.
- **S0.2**: Read `AGENTS.md` in full. Every file edit MUST comply. If a rule is ambiguous, read `LANDMINES.md` for diagnostic context. L1–L23 are inherited from sovereign-ai and are equally binding.
- **S0.2.5**: If resuming after a governance patch that added new rules to `AGENTS.md`, re-read `AGENTS.md` NOW before S1. Rules added by the patch were not present at S0.2.
- **S0.3**: Add any new rules the Architect specified for this plan and commit before any coding step.

**Plan body (S1–Sn)**: Execute all steps in the plan file. After each file edit, run `/verify`. If a step has a STOP condition, pause and report to User before proceeding.

**Closing**: Run `/close` — handles test suite, ruff, mypy, bandit, pip-audit, vulture, custom AR checks, commit, tag, CHANGELOG, PLANS.md, LANDMINES.md (if new pattern), DEBT.md (if deferred), rule proposal (C9), docs commit, push, post-push verification, chat-log reminder, Git Bash cleanup. If missing or fails, STOP and report. Workflow files (`.devin/workflows/*.md`) are the source of truth — Architect reads them from the repo at Workflow Step 2.

---

## Document Relationships

Twelve documents govern this project. Each has a single responsibility — no content duplication (SSOT).

| Document | Responsibility | Who writes | When |
|---|---|---|---|
| `AI_HANDOFF.md` | Static process guide — workflow, plan template, document relationships | Architect | Workflow changes only |
| `project-vision-Rev5.md` | Canonical vision — principles, capability surface, non-goals, success criteria, open questions | User (with Architect) | Principles change; open questions crossed off (not deleted) as resolved |
| `PLANS.md` | Dynamic state — baselines, completed prompts, next-5-queue | Executor (`/close`) | Every plan |
| `LANDMINES.md` | Known failure patterns — trigger and impact only. Append-only. L1–L23 from sovereign-ai; new start at L24 | Executor (`/close`) | New pattern captured |
| `CHANGELOG.md` | Chronological change log — one entry per plan, append-only | Executor (`/close`) | Every plan |
| `AGENTS.md` | Executor's always-on rules — AR + OR. Rules reference source landmine | Executor (`/open` S0.3) | New rules added |
| `DECISIONS.md` | Architectural decisions record — context, options, decision, rationale, trade-offs. Append-only | Executor (`/close`) | New architectural decision |
| `DEBT.md` | Deferred items — what, why, trigger condition, target plan | Executor (`/close`) | Item deferred or addressed |
| `.devin/workflows/open.md` | `/open` workflow | Architect | Workflow changes |
| `.devin/workflows/verify.md` | `/verify` workflow | Architect | Workflow changes |
| `.devin/workflows/close.md` | `/close` workflow | Architect | Workflow changes |
| `.devin/workflows/scan.md` | `/scan` workflow | Architect | Workflow changes |

**SSOT mapping** — each fact lives in exactly one document:
- Environment details → `AGENTS.md`
- Current baselines → `PLANS.md`
- Process/workflow/plan template → `AI_HANDOFF.md`
- Known failure patterns → `LANDMINES.md`
- Per-plan change record → `CHANGELOG.md`
- Architectural decisions → `DECISIONS.md`
- Deferred items → `DEBT.md`
- Vision/principles/open questions → `project-vision-Rev5.md`
- Workflow steps → `.devin/workflows/*.md`

**Read order**:
- **Architect (new chat)**: `AI_HANDOFF.md` → `project-vision-Rev5.md` → `PLANS.md` → `LANDMINES.md` → `DECISIONS.md` → `DEBT.md` → start workflow
- **Executor (S0.2)**: `AGENTS.md` (consult `LANDMINES.md` if a rule is ambiguous)

---

## Bootstrap Sequence

1. **`prompt-0`**: Initial commit — all 12 governance docs, no code. Tag: `prompt-0`.
2. **Plans 1–4**: Architect drafts 4 plan files + 1 batch brief. Round Table reviews. Architect revises to clean pass. User copies finals to `C:/SovereignAI/prompts/`. Executor tags `prompt-1` through `prompt-4`. Plan 1 scaffolds the core — it's a regular plan, not a special Architecture Decision Plan.
3. **Scan 5**: Architect drafts scan prompt. Skip Round Table. Executor runs `/scan`, tags `prompt-5`.
4. **Plans 6–9**: Same as Plans 1–4, drafted against post-scan repo state.
5. **Scan 10**: Second scan.
6. **Plans 11+**: Continue per batch process.

---

## Closing

This handoff is the operating manual for the Architect role — intentionally lean, one responsibility per section, SSOT enforced throughout. Read once per chat session, reference other governance docs as needed. If the process isn't working, amend this handoff — it's a living document.
