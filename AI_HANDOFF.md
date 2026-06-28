# AI Handoff — SovereignAI

## Project Overview

SovereignAI is a local-first, modular AI assistant framework built for a single user. It runs locally by default, escalates to cloud when the task demands it, and is designed to absorb whatever models, adapters, skills, and memory paradigms arrive over the next decade without forcing rewrites.

**Core philosophy**: Strong, robust, modular, simple core. Wire as you go. UIs are separate processes consuming the core's capability API. Fundamentally modular and flexible — every adapter, skill, memory backend, and model is interchangeable. The orchestrator hosts the LLM's reasoning — we don't code the reasoning, we prompt the model.

**Canonical vision**: `project-vision-Rev5.md` (locked). This is the single document all architecture must comply with. 14 principles, 40 success criteria, 10 open questions for Plan 1 to resolve.

**Stack**: Python for v1, Rust-migratable later. Contracts are language-agnostic. v1 targets Windows only; cross-platform deferred.

---

## How to use this document

This handoff is the **static process guide** for the Architect role. It tells the Architect how to make plans, how the Round Table review operates, and how plans are structured. It does NOT carry dynamic state (baselines, completed prompts, next-queue) — that lives in `PLANS.md`. It does NOT carry failure patterns — that lives in `LANDMINES.md`.

**If you are a new Architect chat** receiving this handoff + an Executor execution log:

1. Clone the repo: `git clone https://github.com/AngusKingCAI/SovereignAI.git` (to `/home/z/my-project/sovereignai-review/` or your preferred path)
2. Read this handoff end-to-end
3. Read the following in order:
   - `project-vision-Rev5.md` — canonical design
   - `PLANS.md` — current state (baselines, completed prompts, next-5-queue)
   - `LANDMINES.md` — failure patterns (note: L1–L23 inherited from sovereign-ai, the predecessor project; new landmines start at L24)
   - `DECISIONS.md` — architectural decisions record
   - `DEBT.md` — deferred items register
4. Start the Architect workflow (see "Architect Workflow" section below)

**If you are starting the project fresh** (no execution log yet, just setting up):
- The repo should already have `prompt-0` (bootstrap commit with governance docs only, no code)
- Begin drafting Plans 1–4 (first batch) per the batch plan process

---

## Roles

Three actors collaborate on this project. Each has a distinct job — do not cross the lines.

| Actor | Job | Tools |
|---|---|---|
| **User** | Pastes Executor's execution log to the Architect after each plan. Bridges the Round Table: sends plan files + brief to the panel, pastes findings back. Copies the Architect's deliverables to the Executor's working tree. After `/close` completes, copies the chat log to `logs/execution-log-prompt-{N}.md` and asks the Executor to commit and push it. | IM chat with Architect; file copy on Executor's machine. |
| **Architect** | 7-step post-execution workflow. Creates plans, context briefs, and revised plans. **Never edits the repo directly** — produces files in `/home/z/my-project/download/` for the user to copy. | `git fetch origin`, `git show`, `git log` (read-only on the review clone). No push, no commit, no tool runs. |
| **Executor** | Executes plans. Runs `/open`, `/verify`, `/close`, `/scan` workflows. Runs tests, ruff, mypy, bandit, pip-audit, vulture, custom AR checks. Commits, tags, pushes. Updates CHANGELOG, PLANS, LANDMINES, DEBT, proposes rules via C9. | Git Bash on Windows; the repo's working tree at `C:/SovereignAI/`. |

**Key separation rule**: The Architect does NOT commit to or push to the repo. The Executor does NOT create plans or briefs. The User is the bridge — copies files between the Architect's download folder and the Executor's working tree, and bridges the Round Table.

---

## Repository bootstrap

- **Repo**: https://github.com/AngusKingCAI/SovereignAI
- **Default branch**: `main`
- **Tags**: `prompt-{N}` for each completed plan (e.g., `prompt-1`). Tag-push gate is mandatory. `prompt-0` is the bootstrap commit (governance docs only, no code).
- **Executor's working tree**: `C:/SovereignAI/` (Windows)
- **Architect review clone**: `/home/z/my-project/sovereignai-review/` (Linux sandbox, read-only)
- **Plan files**: `C:/SovereignAI/prompts/plan-{N}-Rev{n}.md` (flat directory, no decade subfolders)
- **All paths use `/`** (forward slash) — the User's keyboard doesn't have `\`, and Windows accepts both.

---

## Architect Workflow

When the User pastes an Executor execution log, the Architect follows these 7 steps in order. Do not skip steps. Do not improvise.

### Step 1 — Read the execution log end-to-end

Read every line of the logs,Extract: actual test counts for ALL test suites, ruff/mypy/bandit/pip-audit/vulture counts, any STOP conditions triggered, any C9 rule proposals the Executor submitted, any deviations from the plan. If a new test suite was introduced, include it — the test count list is not fixed.

### Step 2 — Verify the repo state

`git fetch origin` → check the prompt's tag exists on origin → check the CHANGELOG entry matches → check the commit stat matches the plan's scope (no scope creep) → check `PLANS.md` was updated (completed prompts row, baselines, queue shift). If anything doesn't match, flag to the User.

### Step 3 — Re-read LANDMINES.md and project-vision-Rev5.md

Refresh on failure patterns and principles before drafting. The Architect does NOT re-read this handoff (circular — you're already reading it). The Architect does NOT re-read AGENTS.md (the Executor reads that; the Architect references it only if a rule is ambiguous).

### Step 4 — Review C9 rule proposals and scan for patterns

The Architect is the rule authority. The Executor proposes; the Architect disposes.

- Read the Executor's C9 proposals (if any) from the execution log
- **Independently scan the log for recurring patterns the Executor might have missed**: scope creep, repeated test failures, workarounds, deviations from the plan, anything that took multiple attempts
- Cross-reference with `LANDMINES.md` — is this pattern already captured? If yes, no new rule needed. If no, consider proposing a rule
- Cross-reference with existing `AGENTS.md` rules — is there already a rule that should have prevented this? If yes, the rule exists but wasn't followed (enforcement problem, not a new rule). If no, propose a new rule
- If the Architect decides a new rule is warranted, include it in the next plan's S0 instructions — tell the Executor to add it to `AGENTS.md` at `/open` step 4, with source reference (e.g., "Source: L24" for a landmine-graduated rule, or "Source: Round Table Rev {n}" for a round-table-derived rule)
- The Architect can reject the Executor's C9 proposal if redundant or unnecessary — document the rejection in the plan's context brief

### Step 5 — Make the plan files + context brief

For a batch of N plans: N individual files at `/home/z/my-project/download/plan-{N}-Rev1.md` (the plans the Executor executes) and one shared brief at `/home/z/my-project/download/plan-{X1}-{X4}-batch-Rev1-context-brief.md` (the review guide for the Round Table).

**Each iteration uses Rev{n} notation**: Rev1, Rev2, Rev3, etc. — one file per plan per revision (e.g., `plan-1-Rev1.md`, `plan-1-Rev2.md`). Context brief is only created for Rev1. Rev2+ revisions do not need a new brief — the Round Table reviews the revised files directly.

**All Revs are kept forever** — no deletion. The `prompts/` directory accumulates the full history.

**Plan files contain ONLY what the Executor needs** — S0 opening, body, STOP conditions, files WILL create/edit/NOT edit, closing, header lines. The Architect's reasoning, Round Table findings, and process documentation live elsewhere (brief, execution log).

**Briefs follow the 3-part scaffold** (defined below in "Brief Scaffold" section).

### Step 6 — Pause for Round Table review

The User bridges: they send the plan files + context brief (Rev1 only) or just the revised plan files (Rev2+) to the Round Table, then paste the Round Table's findings back to the Architect. The Round Table reviews only — does not create or edit plan files, only identifies issues and improvements. Wait for the User's paste. Apply findings at the Architect's discretion.

### Step 7 — Deliver the final plan

Tell the User: "Copy `plan-{N}-Rev{n}.md` to `C:/SovereignAI/prompts/plan-{N}.md` and point the Executor at it."

---

## Brief Scaffold

All briefs follow this 3-part scaffold. The scaffold is defined once here; briefs reference it ("per the scaffold in AI_HANDOFF.md") and do not re-describe it.

### Part 1: Roles/Rules (~5 lines)

- State the reviewer's role: "Your job is to find issues, not rewrite the plan"
- State adversarial framing: "Assume this plan will fail — identify how"
- State proof requirement: "Each issue must include a concrete failure scenario"
- State sign-off requirement (GR3): "End your response with `**Panelist**: <your name/model>`. Anonymous responses will be flagged but still adjudicated; named responses are preferred for accountability."

### Part 2: Context (~30-40 lines)

- Plan scope summary (what files, what components)
- Key dependencies (what existing modules this builds on)
- **Author's reasoning (clearly labeled, to mitigate anchoring bias)**: "My reasoning for this design: [X]. Attack this reasoning — don't ratify the conclusion."
- Named open questions for the reviewer to engage with — as many as pertinent, but each must be specific and substantive. Vague or confirmatory questions are banned
- Architect's confidence level on key decisions (e.g., "65% confident on the filesystem layout")
- **For architecture-affecting plans**: explicit reference to which `project-vision-Rev5.md` principles this plan satisfies or violates (cross-reference the plan's `Vision principles:` header line)

### Part 3: Answer Format (~5 lines)

- Specify the response structure (flexible, not rigid boxes)
- ALWAYS include an "other concerns" open field so unexpected issues can surface
- Permit "No issues found" — do not force the reviewer to invent problems

### Anti-sycophancy measures

- Open with pre-mortem frame: "Assume this plan failed in 6 months. List the most plausible reasons."
- Explicitly permit "No issues found" — don't pad with false concerns
- Require proof before reporting: each issue must cite a concrete failure scenario and evidence from the codebase
- Ban style/formatting/speculative-future/feature-request comments — substance only

### Anchoring mitigation

- State the Architect's reasoning in a clearly labeled block
- Instruct reviewer: "Criticize my reasoning, not my conclusion"
- Disclose the Architect's confidence explicitly ("I'm 65% confident on step 3")
- This gives the reviewer a target without forcing agreement

---

## Round Table Review Process

### What goes to the Round Table

**All plans go to the Round Table, EXCEPT scan prompts.**

- **Regular plans** (Plans 1-4, 6-9, 11-14, etc.): Round Table reviews
- **Scan prompts** (Plan 5, 10, 15, etc.): Skip Round Table — they're mechanical (verify baselines, fix accumulated issues, reconcile state), no architectural decisions, no code changes that need design review. Go straight to the Executor.

### Round Table composition

- Referred to collectively as **"the Round Table"** — not by individual model names
- **No fixed composition** — could be 1, could be 100. The User chooses who to send each brief to
- **No quorum** — adjudicate whatever responses come back
- **Panelist sign-off is mandatory by default** (GR3): every response ends with `**Panelist**: <name/model>`. The User can override (accept anonymous responses) at their discretion. When overriding, the Architect still adjudicates the response — it's just flagged as "anonymous, user-accepted"

### Process

1. Architect drafts plan(s) + context brief
2. User bridges to the Round Table (sends plan files + brief + short read-me-first prompt)
3. Round Table reviews, returns findings (with sign-off)
4. Architect judges responses, adopts highest-scoring recommendations
5. **Architect's commitment**: commits to adopting the highest-scoring recommendation — even if it contradicts the Architect's original position. This is what makes the pattern work
6. **For roadmap-level decisions** (philosophy changes, feature arc launches, architecture decisions): User reviews the Architect's judgment before final decision
7. **User can override CRITICAL with explicit sign-off + documented accepted risk** (the carve-out used for the in-process Security Guard in Rev 5 vision). CRITICAL issues formally "block clean pass — no exceptions, no overrides," but in practice the User is the final authority and can accept the risk with documentation

### Severity rubric

- **CRITICAL**: Issues that would cause data loss, security vulnerability, or irreversible system damage. Any panelist may flag an issue as CRITICAL with a concrete failure scenario. CRITICAL issues block clean pass and must be resolved before Executor execution — no exceptions, no overrides (formally; User override with documented accepted risk in practice)
- **HIGH**: Issues that would cause an Executor STOP condition, test failure, broken build, or Windows incompatibility. HIGH issues block clean pass and must be resolved or explicitly overruled with User sign-off
- **MEDIUM**: Issues that would cause degraded functionality, poor user experience, or technical debt that should be addressed before execution but won't necessarily cause failure. MEDIUM issues should be addressed; if accepted, document reasoning in adjudication log
- **LOW**: Style, formatting, naming preferences, speculative future features, or performance optimizations without measured impact. LOW items may be accepted or rejected at Architect discretion, with one-paragraph reasoning documented in the brief's adjudication log

If a panelist and the Architect disagree on severity, the issue is treated as the higher severity until resolved.

### Clean pass definition

A clean pass requires:
- (a) No panelist reports a substantiated CRITICAL or HIGH issue that hasn't been addressed
- (b) Any remaining MEDIUM/LOW items are documented as accepted/rejected with reasoning in the brief's adjudication log

### Adjudication (GR4)

The Architect must **explicitly accept or reject every Round Table finding with reasoning**. No silent dismissals. The adjudication is recorded in:
- The brief's adjudication log (for Rev1 briefs)
- A separate adjudication section in the revised plan file (for Rev2+ where no new brief is created)

---

## Batch Plan Process

### Structure

- **Batches of 4 plans**, drafted as individual files from the start (no combined batch file, no split step)
- **1 shared batch context brief** covering all 4 plans
- **Scan every 5 plans** (Plan 5, 10, 15, ...) — verifies baselines, fixes accumulated issues, reconciles state
- **Plan 1 is a regular plan** — no special "Architecture Decision Plan" treatment. Architecture emerges plan by plan, just like the vision emerged round by round (per the vision's "wire as you go" principle)

### Cadence

- Plans 1-4 → Scan 5 → Plans 6-9 → Scan 10 → Plans 11-14 → Scan 15 → ...

### Why separate files?

The combined-file + split approach (used in sovereign-ai's early days) introduced a mechanical transformation (split) that could introduce bugs — stale references to other plan numbers, leftover batch header text, missing S0/Closing sections. Drafting separately eliminates this overhead: what the Round Table reviews IS what the Executor executes.

### Step 1 — Draft individual plan files

Create N individual files (one per plan in the batch):

```
/home/z/my-project/download/plan-{X1}-Rev1.md
/home/z/my-project/download/plan-{X2}-Rev1.md
/home/z/my-project/download/plan-{X3}-Rev1.md
/home/z/my-project/download/plan-{X4}-Rev1.md
```

Each file is self-contained: S0 Opening, body, STOP condition, Files WILL create/edit/NOT edit, Closing, header lines (`Depends on:`, `Vision principles:`, `Open questions resolved:`). Reads as a standalone Executor prompt.

### Step 2 — Draft the batch context brief

Create ONE shared brief covering all plans in the batch:

```
/home/z/my-project/download/plan-{X1}-{X4}-batch-Rev1-context-brief.md
```

The brief follows the 3-part scaffold (see "Brief Scaffold" section), with these additions:
- **Cross-plan dependency map**: which plans depend on the output of a prior plan
- **Sequencing risks**: what happens if plans execute out of order
- **Author's confidence by plan**: e.g., "Plans 6–7: 80% confident. Plans 8–9: 65% confident — attack these hardest"
- **Named open questions**: as many as pertinent, but each must be specific and substantive
- **Vision principle compliance**: explicit note on which `project-vision-Rev5.md` principles each plan satisfies

### Step 3 — Round Table review

Batch plans are reviewed by the Round Table (no exceptions, per "What goes to the Round Table" above).

The User sends the N individual files + 1 batch context brief to the Round Table. The Architect collects all responses and judges them. Apply all substantiated findings to the individual files.

### Step 4 — Fix and re-review

Revise individual files as needed (one file per plan per revision):

```
/home/z/my-project/download/plan-{X1}-Rev2.md
/home/z/my-project/download/plan-{X2}-Rev2.md
...
```

Rev2+ files do not need a new context brief — the Round Table reviews the revised files directly. However, if revisions are substantial (new architecture, changed dependencies), update the batch brief to reflect the new state.

Repeat (Rev3, Rev4…) until the Round Table's response is a clean pass.

### Execution failure within a batch

If the Executor hits a STOP condition on Plan {Xn}, subsequent plans that depend on {Xn} — directly or transitively — must also STOP. Dependency is determined by each plan's `Depends on:` line, not by User judgment. Plans with no dependency on {Xn} may proceed, but only if their prerequisite tags are confirmed present on origin.

**Partial outputs:** If Plan {Xn} completed some but not all of its intended outputs, dependent plans must still STOP. The binary rule is: if Plan Y lists Plan X in `Depends on:`, and Plan X STOPped, Plan Y STOPs. No partial-dependency exceptions.

**Revised plan review:** After a STOP, the Architect revises the failed plan and any dependent plans. Revisions must undergo Round Table review before re-execution.

---

## Scan Prompt

Scan prompts occur every 5 plans (5, 10, 15, ...) to verify baselines, fix accumulated issues, and reconcile state before the next batch begins.

### Purpose

After 4 plans execute, the repo accumulates small inconsistencies: stale imports, minor type errors that scraped past mypy, outdated docstrings, LANDMINES.md patterns not yet codified as rules, minor ruff warnings suppressed rather than fixed. The scan prompt cleans all of this up before the next batch begins.

The scan prompt is queued after Plan X4 in `PLANS.md` and executes before the next batch's Plan X1 begins.

**Drafting order constraint:** The next batch (e.g., 6–9) must not be drafted or Round Table-reviewed until the scan prompt has completed and its changes (including any new AR/OR rules proposed via C9) are committed to origin. This ensures the next batch is drafted against the post-scan repo state.

**Batch failure interaction:** If a batch fails partially (e.g., Plan 3 STOPs, halting 4), the scan must not execute until the failure is resolved and all plans 1–4 have completed. The scan verifies the full batch's output; running it on a partial batch would produce false positives.

### Scan prompt structure

Scan prompts use the standard S0 opening and `/close` closing. They get their own `prompt-{N}` tag. The scan workflow is defined in `.devin/workflows/scan.md` — the scan prompt file just tells the Executor to run `/scan`.

**Scan prompts skip the Round Table** — they're mechanical, no architectural decisions.

---

## Architect Operating Discipline

The Architect maintains discipline via GR rules (GR = General Rules, mirroring the AR/OR scheme for the Executor).

### GR1 — Vision principle compliance

Every plan the Architect drafts MUST include a `Vision principles:` line in its header listing which of the 14 principles in `project-vision-Rev5.md` the plan satisfies or affects. Example: `Vision principles: 1 (sacred core), 7 (modular core), 8 (UIs separate processes)`. If a plan violates a principle, the header must say so explicitly: `Vision principles: violates 3 (no provider lock-in) — justification: <reason>`. The Round Table uses this line to verify architectural decisions remain faithful to the vision.

### GR2 — Open questions resolved

Every plan header MUST include an `Open questions resolved:` line listing which open questions (Q1–Q34 in `project-vision-Rev5.md`) the plan resolves. Example: `Open questions resolved: Q1 (adapter contract), Q33 (capability API protocol)`. If none, write `Open questions resolved: none`. This lets the Architect track which open questions are still outstanding and which are resolved.

### GR3 — Brief sign-off requirement

Every brief the Architect drafts MUST include the panelist sign-off requirement in Part 1 (Roles/Rules). The brief states: "End your response with `**Panelist**: <your name/model>`. Anonymous responses will be flagged but still adjudicated; named responses are preferred for accountability." The User can override (accept anonymous responses) at their discretion.

### GR4 — Explicit adjudication

The Architect MUST explicitly accept or reject every Round Table finding with reasoning. No silent dismissals. The adjudication is recorded in:
- The brief's adjudication log (for Rev1 briefs)
- A separate adjudication section in the revised plan file (for Rev2+ where no new brief is created)

Format for each finding:
```
Finding: <description> — Severity: <CRITICAL/HIGH/MEDIUM/LOW> — Panelist: <name>
Adjudication: <ACCEPTED/REJECTED/PARTIALLY ACCEPTED>
Reasoning: <one paragraph>
Action: <what was changed in the plan, or "no change — reasoning above">
```

---

## Plan Template

The Architect copies this structure into every plan file. The plan file is the Executor's instruction manual — it contains ONLY what the Executor needs.

### Header lines

```
Depends on: <prerequisite plan numbers, or empty if independent>
Vision principles: <which of the 14 principles this plan satisfies/affects>
Open questions resolved: <which open questions this plan resolves, or "none">
```

### Opening (S0)

**S0.1 — Run `/open`** — verifies previous prompt's tag on origin and confirms working copy is clean and on `main`. If the workflow is missing or fails, STOP and report.

**S0.2 — Read AGENTS.md in full.** AGENTS.md is always-on — every file edit in this plan MUST comply with its rules. If an AGENTS.md rule's application is ambiguous, read `LANDMINES.md` for the trigger and diagnostic context behind the rule. Note: Landmines L1–L23 are inherited from sovereign-ai; they are just as binding as new landmines.

**S0.2.5 — Re-read AGENTS.md after governance patches.** If this plan is resuming after a governance patch that added new rules to AGENTS.md, re-read AGENTS.md NOW before S1. The rules added by the patch were not in AGENTS.md when you originally read it at S0.2. Do not skip this re-read.

**S0.3 — Add any new rules the Architect specified for this plan and commit** before any coding step. Then proceed to the plan body (S1 onward).

### Plan body (S1-Sn)

Execute all steps specified in the plan file. After each file edit, run `/verify`. If any step has a STOP condition, pause and report to the User before proceeding.

### Closing

**Run `/close`** — handles test suite, ruff, mypy, bandit, pip-audit, vulture, custom AR checks, commit, tag, CHANGELOG, PLANS.md, LANDMINES.md (if new pattern), DEBT.md (if deferred), rule proposal (C9), docs commit, push, post-push verification, chat-log reminder, Git Bash cleanup. If the workflow is missing or fails, STOP and report.

The workflow files (`.devin/workflows/*.md`) are the source of truth for the workflow steps. The Architect reads them from the repo to verify the Executor's execution at Architect Workflow Step 2.

---

## Document Relationships

Twelve documents govern this project. Each has a single responsibility — do not duplicate content across them (SSOT).

| Document | Responsibility | Who writes it | When it changes |
|---|---|---|---|
| `AI_HANDOFF.md` (this file) | Static process guide — how to make plans, workflow, plan template, document relationships | Architect | Only when the workflow itself changes |
| `project-vision-Rev5.md` | Canonical vision — principles, capability surface, non-goals, success criteria, open questions. The document all architecture must comply with | User (with Architect assistance) | Only when principles change. Open questions get crossed off (not deleted) as plans resolve them |
| `PLANS.md` | Dynamic project state — baselines, completed prompts, next-5-queue | Executor (at `/close`) | Every plan |
| `LANDMINES.md` | Known failure patterns — trigger and impact only. Append-only. L1–L23 inherited from sovereign-ai; new landmines start at L24 | Executor (at `/close`) | When a new pattern is captured (append-only) |
| `CHANGELOG.md` | Chronological change log — one entry per plan, append-only | Executor (at `/close`) | Every plan |
| `AGENTS.md` | Executor's always-on rules — environment, edit discipline, git discipline, scope discipline. AR (Architecture Rules) + OR (Operational Rules). Rules reference their source landmine (e.g., "Source: L{n}") | Executor (at `/open` S0.3, when the Architect specifies new rules) | When new rules are added |
| `DECISIONS.md` | Architectural decisions record — context, options considered, decision, rationale, trade-offs. Append-only | Executor (at `/close`, when a decision is codified) | When a new architectural decision is made |
| `DEBT.md` | Deferred items register — what's been pushed to later, why, trigger condition, target plan | Executor (at `/close`, when an item is deferred or addressed) | When item deferred or addressed |
| `.devin/workflows/open.md` | `/open` workflow — steps the Executor runs at the start of every plan | Architect | When workflow changes |
| `.devin/workflows/verify.md` | `/verify` workflow — steps the Executor runs after each file edit | Architect | When workflow changes |
| `.devin/workflows/close.md` | `/close` workflow — steps the Executor runs at the end of every plan | Architect | When workflow changes |
| `.devin/workflows/scan.md` | `/scan` workflow — steps the Executor runs at scan prompts (5, 10, 15, ...) | Architect | When workflow changes |

### Single source of truth (SSOT)

Each fact lives in exactly one document. Other documents reference it, don't copy it.

- Environment details → `AGENTS.md` only (this handoff carries just the bootstrap minimum)
- Current baselines → `PLANS.md` only (this handoff doesn't carry baselines)
- Process/workflow/plan template → `AI_HANDOFF.md` only (`PLANS.md` doesn't carry process docs)
- Known failure patterns → `LANDMINES.md` only (this handoff doesn't carry landmines)
- Per-plan change record → `CHANGELOG.md` only (`PLANS.md` carries the summary row, not the full change log)
- Architectural decisions → `DECISIONS.md` only
- Deferred items → `DEBT.md` only
- Vision / principles / open questions → `project-vision-Rev5.md` only
- Workflow steps → `.devin/workflows/*.md` only (this handoff references them, doesn't duplicate)

### Read order

- **Architect (new chat)**: `AI_HANDOFF.md` → `project-vision-Rev5.md` → `PLANS.md` → `LANDMINES.md` → `DECISIONS.md` → `DEBT.md` → start workflow
- **Executor (S0.2)**: `AGENTS.md` (always-on rules; consult `LANDMINES.md` if a rule is ambiguous)

---

## Bootstrap Sequence

This project starts from an empty repo. The bootstrap sequence is:

1. **`prompt-0`** (bootstrap commit): initial commit containing all 12 governance docs (`AI_HANDOFF.md`, `AGENTS.md`, `LANDMINES.md`, `PLANS.md`, `CHANGELOG.md`, `DECISIONS.md`, `DEBT.md`, `project-vision-Rev5.md`, `.devin/workflows/open.md`, `.devin/workflows/verify.md`, `.devin/workflows/close.md`, `.devin/workflows/scan.md`). No code. Tag: `prompt-0`.

2. **Plans 1–4** (first batch): the Architect drafts 4 individual plan files + 1 batch context brief. Round Table reviews. Architect revises to clean pass. User copies final files to `C:/SovereignAI/prompts/`. Executor executes each plan, tagging `prompt-1` through `prompt-4`. Plan 1 scaffolds the core because that's what the project needs first — it's a regular plan, not a special Architecture Decision Plan.

3. **Scan 5** (first scan prompt): the Architect drafts the scan prompt. Skip Round Table (scan prompts are mechanical). User copies to Executor. Executor runs `/scan`, tags `prompt-5`.

4. **Plans 6–9** (second batch): same process as Plans 1–4, drafted against the post-scan repo state.

5. **Scan 10**: second scan.

6. **Plans 11+**: continue per batch process.

---

## Closing

This handoff is the operating manual for the Architect role. It is intentionally lean — every section has a single responsibility, and SSOT is enforced throughout. The Architect reads this handoff once per chat session, then references the other governance docs as needed.

The project starts with `prompt-0` (governance docs only) and proceeds through Plans 1–4, Scan 5, Plans 6–9, Scan 10, etc. The vision is locked at Rev 5 — no more Round Table review of the vision. The next Round Table review is for Plan 1 (the first batch's first plan).

If the process isn't working, amend this handoff. It's a living document — change it when something doesn't work, not before.
