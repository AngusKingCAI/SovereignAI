# Guide: Self-Implementing Governance From Scratch

**Audience:** Devin (executing this guide directly)
**Context:** Nothing exists yet. All prior scripts and caching infrastructure have been removed. Build `AGENTS.md`, `Rules.md`, `Workflow.md`, and the `Scripts/` folder structure from nothing.
**Governing principle:** KISS. No caching layer. No speculative infrastructure. Build only what has a demonstrated purpose.

Work through these phases in order. Do not skip a verification step to reach the next phase faster.

---

## Phase 0 — Confirm the starting state

1. Confirm no `AGENTS.md`, `Rules.md`, `Workflow.md`, or `Scripts/` folder already exist in this location. If any do, stop and ask before overwriting.
2. Confirm which agent role this is for (Architect, Executor, Planner, Researcher, Reviewer). This determines scope, not content — the structure below applies to all roles.
3. State in one sentence what this agent is responsible for. If you can't state it in one sentence, ask before proceeding.

---

## Phase 1 — Build the `Scripts/` folder structure

Create these category folders. Nothing else. Each is flat and single-purpose:

```
Scripts/
├── Logging/            # session and operation logging scripts
├── Workflow_Gating/     # gate checks, phase-permission enforcement
├── Rule_Enforcement/     # hook scripts that validate rule compliance at runtime
├── Testing/              # function-level test runners and verification scripts
├── WebSearch_Fallback/   # helper scripts used after a test failure to research correct implementation
└── Session_Management/  # session start/end, cleanup, archival
```

Rules for this phase:
- Do not create a category that has no script in it yet unless you are confident it will be needed this session — an empty folder with no near-term purpose is speculative infrastructure.
- Do not nest categories inside each other.
- Do not add a caching folder or caching script. Caching has been deliberately removed from this project. If re-read cost becomes a real, measured problem later, that is a separate, explicit decision — not something to reintroduce by default.
- If a script could belong to more than one category, place it by its *primary* responsibility only.

**Verification before Phase 2:** List the folders you created. Confirm each one maps to something you expect to build this session, not a "might need it later" guess.

---

## Phase 2 — Build `Rules.md` from scratch

Write `Rules.md` yourself. Do not copy a template verbatim — write only rules this specific agent actually needs. Include these five, worded for your own role, plus any project-specific rule you can justify:

1. **Modular, incremental implementation** — build exactly one function at a time. Test it immediately. Never write a second function before the first is tested.
2. **User confirmation before proceeding** — after a function passes its test, present the function and its test result to the user and get explicit confirmation before writing the next function.
3. **Locked functions** — once the user confirms a function, treat it as frozen in all future iterations. Do not modify it later unless the user explicitly asks you to.
4. **Web search on first test failure** — if a function fails its test on the first attempt, perform a web search to check the correct implementation or common pitfalls before writing a second attempt. Never retry blindly.
5. **Script placement** — every script you write goes in the `Scripts/<Category>/` folder matching its primary function, per Phase 1. Never create an ad-hoc folder.

Keep `Rules.md` short. If a rule doesn't reflect something you'd actually violate without being told, cut it.

**Verification before Phase 3:** Re-read your `Rules.md`. If any line states something you'd already do correctly without being told (generic filler like "write clean code"), remove it.

---

## Phase 3 — Build `Workflow.md` from scratch

Write the concrete step-by-step cycle this agent follows when implementing functions. Use this as the core loop — write it out fully, don't leave placeholders:

1. Identify the next function needed.
2. Write that one function only.
3. Run its test in isolation.
4. **If the test fails:** perform a web search for the correct implementation or known pitfalls, then rewrite the function once based on what you found. Return to step 3.
5. **If the test passes:** present the function and the passing test result to the user.
6. Wait for explicit user confirmation.
7. **On confirmation:** mark the function as locked (a one-line note in a plain log is enough — no cache file, no hash validation, just a record of what's confirmed and when).
8. Move to the next function. Do not return to a locked function unless the user explicitly requests a change.
9. Repeat from step 1 until the task is complete.

Do not add hook infrastructure, session caching, or automated enforcement machinery beyond what's needed to run this loop. If you find yourself building a system to enforce the workflow rather than just following it, stop — that's over-engineering for a KISS project.

**Verification before Phase 4:** Walk through the steps once, out loud, for the first function you plan to build. If any step requires infrastructure you haven't built yet and can't justify building now, simplify the step instead.

---

## Phase 4 — Build the first hook: the documentation-read gate

Before building any other hook (permission checks, logging, session lifecycle), build this one first. Every later hook depends on Devin CLI's actual hook API — exit codes, event names, `.devin/hooks.v1.json` format — and that information only comes from the project docs. Building other hooks before this one means relying on memory instead of the manual for the very system meant to enforce reading the manual.

- **Type:** PreToolUse hook
- **Category:** `Scripts/Workflow_Gating/` — it blocks progression through a step rather than validating a violation after the fact
- **Logic:** Before any tool call that writes or edits an implementation file, check a plain session log for an entry recording that relevant documentation was read this session. If missing, block the call (exit code 2) with a message naming which doc to read first.
- **State tracking:** One flat, append-only log — no cache file, no hash validation. `Scripts/Logging/docs_read_log.md`, lines like: `2026-07-25 | hook-implementation | read: Devin CLI manual, hooks section`.
- **Scope of the check:** The hook only verifies *that* something was logged this session — it cannot verify the *right* section was read. That precision comes from Rules.md, not the hook. Keep the hook's job narrow.

Add the matching rule to `Rules.md` from Phase 2: *"Before implementing anything that touches Devin CLI-specific behavior (hooks, permissions, session lifecycle), search the project docs folder for the relevant section and log it, before writing code."*

**Verification before Phase 5:** Confirm this hook blocks a test write when no log entry exists, and allows it once one is added. Test this one hook, get it confirmed, before building the next.

---

## Phase 5 — Build `AGENTS.md`

Keep this short — under 30 lines. It is the entry point, not a restatement of Rules.md or Workflow.md — but a small set of rules that apply to *every* task belong here directly rather than only by reference, because they need to be sent with every conversation regardless of task type.

```markdown
# Project Rules

## Core Rules (always apply)
- KISS: prefer the simplest working solution. Do not add infrastructure (caching, hooks, abstractions) without a demonstrated need.
- Build one function at a time. Test it. Confirm it with the user. Lock it. Then move on.
- If a function fails its first test, web search before retrying. Never retry blindly.
- Place every script in the `Scripts/<Category>/` folder matching its function. Never create an ad-hoc folder.
- If requirements are unclear, ask — don't silently assume.
- Don't touch unrelated code. Smallest reversible diff only.

## Rule & Workflow Sources
- Rules: `./Rules.md` — full detail, read before any implementation work
- Workflow: `./Workflow.md` — read before starting a new function

## Workflow Selection
- Default workflow: `./Workflow.md`
- If additional specialized workflows exist for this agent (e.g. a hook-creation workflow, a consistency-check workflow), list them here with their trigger condition, one line each — do not duplicate their content, only state when to switch to them.

## Tech Stack
<one line per language/framework, with version pins>

## Setup Commands
<exact install/build/test/run commands>

## Boundaries
- Never commit secrets or .env files
```

Do not copy any bullet from `Rules.md` or `Workflow.md` into `AGENTS.md` beyond the Core Rules above. Everything else is a pointer, not a restatement.

**Verification before Phase 6:** Count the lines. If over 30, cut content, don't add scrollable sections.

---

## Phase 6 — If specialized workflows are added later

If this agent grows beyond one general workflow — for example, a narrow workflow for a specific recurring task type — follow this pattern instead of copy-pasting the general `Workflow.md` as a starting point:

1. Keep `Workflow.md` as the default, general-purpose cycle. Do not rename or replace it just because a specialized workflow is added.
2. Any new specialized workflow file gets its own trigger condition, stated plainly (e.g. "used when the task is X, not for general work").
3. If the general workflow and any specialized workflow share governance boilerplate (session logging format, hook enforcement description, closure steps), write that shared content **once**, in a separate reference file, and have each workflow point to it. Never repeat the same block of boilerplate text across multiple workflow files verbatim — that duplication is exactly the kind of bloat this project has already had to clean up once.
4. Add the new workflow's trigger condition to the "Workflow Selection" section of `AGENTS.md` (one line), not a restatement of its steps.

**Verification:** Before finalizing a new specialized workflow, check whether any section is byte-for-byte identical to a section in another workflow file. If so, extract it to a shared file first.

---

## Phase 7 — Self-report

Report back in this exact format before doing any further work:

```
Scripts/ categories created: <list>
Rules.md created: <yes/no>, line count: <n>
Workflow.md created: <yes/no>, line count: <n>
Documentation-read gate hook: <working/not working>
AGENTS.md created: <yes/no>, line count: <n>
First function planned: <name>
Unresolved questions requiring human input: <list or "none">
```

If "Unresolved questions" is non-empty, stop and wait for a response before writing any function.

---

## Why this order matters

Building the folder structure first prevents scripts from landing in ad-hoc locations while rules are still being written. Writing Rules.md and Workflow.md from scratch — rather than copying a template — keeps the files matched to what this agent actually does, avoiding the generic, duplicated content that made the prior version bloated. The modular build-test-confirm-lock loop, backed by a mandatory web search on the first failure, is the mechanism that keeps quality high without needing a caching or enforcement layer to hold it together.

The documentation-read gate is built before any other hook because every other hook depends on facts about Devin CLI's hook system that should come from the manual, not from memory — this hook makes reading the manual a precondition for building the hooks that read the manual's own subject matter.

Splitting rules between AGENTS.md and Rules.md is deliberate: AGENTS.md carries only what must be sent with every single task, kept small enough that it doesn't get skimmed past; Rules.md carries the full detail. If this agent later grows multiple specialized workflows, the same discipline applies one level up — a short routing line in AGENTS.md, full detail and shared boilerplate kept in the workflow files themselves, never duplicated across them.
