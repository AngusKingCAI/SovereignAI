# SovereignAI Workflow Redesign Proposal
## Version: Rev1 -- For Round Table Review
## Date: 2026-07-17

---

## 1. Problem Statement

Current AGENTS.md is 135 lines, 7,053 bytes. The Executor re-reads it in full at every `/open` (OR1/S0.2). Per OpenAI's harness engineering research, a bloated always-loaded instruction file crowds out task context, causes agents to pattern-match locally instead of reasoning globally, and cannot be mechanically verified for freshness.

The current file mixes three concerns that should be separated:
1. **Workflow contract** -- universal, applies to every plan (e.g., /open -> execute -> /close)
2. **Subsystem rules** -- only relevant when touching specific code (e.g., TUI panel rules, adapter health checks)
3. **Rationale** -- why a rule exists, rejected alternatives, consequences -- needed for Architect decisions, not Executor execution

Additionally, the skills (open/SKILL.md, close/SKILL.md, scan/SKILL.md, verify/SKILL.md) already encode most operational rules as literal numbered steps. AGENTS.md restates them in prose, creating duplication.

---

## 2. Design Goals

| Goal | How |
|---|---|
| Minimize Executor per-session token cost | AGENTS.md -> ~30 lines; per-plan rules resolved by Architect into plan header |
| Shift reasoning cost to Architect | Architect resolves rule applicability once at plan-authoring time |
| Mechanical enforcement over prose | Rules backed by scripts don't need prose restatement |
| Progressive disclosure | Executor reads only what's relevant to this plan |
| No deletion of governance history | OR11/OR28 still hold; content moves, never deleted |
| Skills remain authoritative | open/close/scan/verify SKILL.md are the literal checklists; AGENTS.md points to them |

---

## 3. Proposed Directory Structure

```
SovereignAI/
├── AGENTS.md                           # NEW: ~30 lines, workflow contract + universal rules only
├── README.md                           # unchanged
├── .gitignore                          # unchanged
├── pyproject.toml                      # unchanged
├── .pre-commit-config.yaml             # unchanged
│
├── .agent/                             # NEW: all governance, split by role
│   ├── architect/                      # Architect-only files (Executor never reads)
│   │   ├── AI_HANDOFF.md             # moved from root, process guide
│   │   ├── PRINCIPLES.md             # moved from root, 14 principles
│   │   ├── RULES_INDEX.md            # NEW: trigger->pointer table for mechanical resolution
│   │   ├── RULES_REFERENCE.md        # NEW: full AR/OR bodies, Architect-only reference
│   │   └── documents/                # moved from root
│   │       ├── SovereignAI_Consolidated_Design_v1.0.md
│   │       └── ... (all existing docs)
│   │
│   └── executor/                     # Executor-owned files
│       ├── PLANS.md                  # moved from root
│       ├── LANDMINES.md              # moved from root
│       ├── DEBT.md                   # moved from root
│       ├── DECISIONS.md              # moved from root
│       ├── CHANGELOG.md              # moved from root
│       ├── scripts/                  # moved from root
│       │   ├── resolve_rules.py      # NEW: mechanical rule resolution for Architect
│       │   ├── get_current_plan.py
│       │   ├── is_scan_plan.py
│       │   ├── get_scoped_tests.py
│       │   ├── verify_syntax.py
│       │   ├── verify_close.py       # NEW: close-step verification script
│       │   ├── check_rule_crossrefs.py
│       │   └── ar_checks/            # unchanged
│       │       ├── no_globals.py
│       │       ├── constructor_arg_cap.py
│       │       ├── no_context_bags.py
│       │       ├── no_hardcoded_component_names.py
│       │       ├── ui_does_not_touch_core.py
│       │       ├── check_tracing.py
│       │       ├── check_placeholders.py
│       │       ├── check_p4_compliance.py
│       │       ├── check_changelog.py
│       │       ├── check_dependencies.py
│       │       ├── check_rule_conciseness.py
│       │       └── check_ar7_allowlist.py
│       │
│       ├── tests/                    # moved from root
│       ├── prompts/                  # moved from root
│       │   ├── plan-{N}-Rev{n}.md    # header gains `Applicable rules:` field
│       │   └── completed/
│       │
│       └── logs/                     # moved from root
│           ├── execution-log-prompt-{N}.md
│           └── screenshots/
│
├── .devin/                             # unchanged role, skill files edited
│   └── skills/
│       ├── open/SKILL.md             # EDITED: Step 1.5 removed, Step 8 split
│       ├── close/SKILL.md            # EDITED: references moved paths
│       ├── scan/SKILL.md             # EDITED: references moved paths
│       └── verify/SKILL.md           # EDITED: references moved paths
│
├── sovereignai/                        # source code, unchanged
├── web/                                # web UI, unchanged
├── tui/                                # TUI, unchanged
├── cli/                                # CLI, unchanged
├── phone/                              # phone UI, unchanged
├── adapters/                           # adapters, unchanged
├── databases/                          # databases, unchanged
├── services/                           # services, unchanged
├── skills/                             # user skills, unchanged
├── txt/                                # requirements, whitelist, baseline
└── archive/                            # LANDMINES-ARCHIVE.md
```

---

## 4. File Contents

### 4.1 AGENTS.md (new, ~30 lines)

```markdown
# AGENTS.md

Authority: .agent/architect/PRINCIPLES.md
Ambiguous -> .agent/shared/LANDMINES.md

## Workflow contract
Every plan: /open -> execute -> /close, per .devin/skills/{open,close,scan,verify}/SKILL.md.
Follow steps literally, in order, no skipping. Exit!=0 = STOP.
Do not explain, justify, or offer workarounds -- STOP is the only valid response.

## Universal rules (apply to every plan)
AR11. No docstrings. Self-documenting names.
AR-DI. DI only: no globals, no context bags, <=15 constructor args.
       Script-enforced every /close via ar_checks/.
OR-GOV. Never delete governance-doc content. Prepend-only for LANDMINES.md/CHANGELOG.md.
OR-LIT. Follow instructions literally. Restrictive terms ('only', 'never', 'must') = exact compliance.

## Plan-specific rules
Resolved per-plan by Architect into each plan's `Applicable rules:` header.
Apply exactly those, plus the universal set above.
Full rule index: .agent/architect/RULES_INDEX.md
Full rule bodies: .agent/architect/RULES_REFERENCE.md (Architect-only, not required Executor reading)
```

**Rationale for what stays:**
- AR11 (no docstrings): Universal -- applies to every file, every plan. Agent cannot discover this from code (D103 is disabled in pyproject.toml, but the agent doesn't know that without being told).
- AR-DI (DI only): Universal -- applies to every class, every plan. The constructor arg cap and no-globals rules are script-enforced, but the agent needs to know the constraint exists to design around it.
- OR-GOV (prepend-only): Universal -- applies to every edit of LANDMINES.md/CHANGELOG.md. The agent cannot discover this from code.
- OR-LIT (follow literally): Universal -- applies to every instruction in every plan. Learned from log 21 failure pattern.

**What moves to RULES_REFERENCE.md:**
- AR1-AR10, AR12-AR30: Subsystem-specific. Only relevant when touching orchestrator, adapters, TUI, web layer, etc.
- OR1-OR30: Most are already the literal content of skill steps. open/SKILL.md step 1 = OR1. close/SKILL.md step 12 = OR5. No need to restate.

### 4.2 .agent/architect/RULES_INDEX.md (new)

```markdown
# RULES_INDEX.md

Trigger-condition -> rule pointer table. One row per rule.
Architect uses this to resolve `Applicable rules:` for each plan.
Mechanical first pass: .agent/executor/scripts/resolve_rules.py

| Rule  | Trigger condition                              | Enforcement action                              | Full text ->                      |
|-------|-----------------------------------------------|------------------------------------------------|----------------------------------|
| AR1   | touches orchestrator/ or workers/             | verify chain: Owner->Orchestrator->Manager->Worker | RULES_REFERENCE.md secAR1          |
| AR2   | touches librarian/ or memory/                 | verify no direct backend queries               | RULES_REFERENCE.md secAR2          |
| AR3   | touches adapters/ or model loading              | verify inference routes through adapters       | RULES_REFERENCE.md secAR3          |
| AR4   | new component or inter-component reference    | verify capability graph discovery, no hardcoded  | RULES_REFERENCE.md secAR4          |
| AR5   | new MCP server or adapter wrapping            | verify adapter wrapper before use              | RULES_REFERENCE.md secAR5          |
| AR6   | new adapter or tool registration                | verify health_check() + graceful error           | RULES_REFERENCE.md secAR6          |
| AR7   | touches tui/panels/ or app/web/*                | run scripts/ar_checks/check_ar7_allowlist.py   | RULES_REFERENCE.md secAR7          |
| AR8   | new trace/logging code                        | verify local SSD only, no external telemetry   | RULES_REFERENCE.md secAR8          |
| AR9   | new skill authoring method                    | verify manifest+code+DAG output                | RULES_REFERENCE.md secAR9          |
| AR10  | new external component integration            | verify local copy before use                   | RULES_REFERENCE.md secAR10         |
| AR12  | touches web/ or FastAPI routes                  | verify separate process, public API surface    | RULES_REFERENCE.md secAR12         |
| AR13  | touches web/ auth or SSE                       | verify HTTP session cookie, no query params    | RULES_REFERENCE.md secAR13         |
| AR14  | touches web/schemas.py or DTOs                | verify DTOs in web/schemas.py                  | RULES_REFERENCE.md secAR14         |
| AR15  | new adapter or health check change              | verify health_check() returns typed dataclass  | RULES_REFERENCE.md secAR15         |
| AR16  | new capability class or conformance test        | verify <100ms, cached, fail-closed/open          | RULES_REFERENCE.md secAR16         |
| AR17  | touches public API surface                      | verify contract tests pass                     | RULES_REFERENCE.md secAR17         |
| AR18  | any commit                                      | property-based tests run (CI gate)             | RULES_REFERENCE.md secAR18         |
| AR19  | new memory backend or backend swap              | verify CapabilityGraph pluggability            | RULES_REFERENCE.md secAR19         |
| AR20  | new crash recovery or shutdown logic            | verify .shutdown_marker check                  | RULES_REFERENCE.md secAR20         |
| AR21  | new durable backend (SQLite/JSON)               | verify atomic writes, WAL, os.replace()        | RULES_REFERENCE.md secAR21         |
| AR22  | new function with side effects                  | verify trace event emission                    | RULES_REFERENCE.md secAR22         |
| AR23  | new entry point or correlation ID change        | verify context var propagation                 | RULES_REFERENCE.md secAR23         |
| AR24  | touches web/ logs panel                         | verify /api/traces SSE consumption only        | RULES_REFERENCE.md secAR24         |
| AR25  | touches databases/ or services/                 | verify root-level packages, no nesting         | RULES_REFERENCE.md secAR25         |
| AR26  | new ServiceProvider/DatabaseProvider            | verify health_check() dataclass, lazy init     | RULES_REFERENCE.md secAR26         |
| AR27  | touches web/ Models or Hardware panels          | verify capability API consumption only         | RULES_REFERENCE.md secAR27         |
| AR28  | new adapter manifest or routing change          | verify routing_priority int, ascending         | RULES_REFERENCE.md secAR28         |
| AR29  | new diagnostic harness or test stage            | verify load->use->unload per stage               | RULES_REFERENCE.md secAR29         |
| AR30  | touches tui/ panels                             | verify real backend state, no placeholders     | RULES_REFERENCE.md secAR30         |
| OR1   | scan plan or mypy invocation                    | file-scoped mypy only, never `mypy .`          | SKILL.md scan step 1             |
| OR2   | scan plan or multiple tools                     | run ONE AT A TIME, never parallel              | SKILL.md scan step 1             |
| OR3   | any edit operation                              | never replace_all, edit each occurrence        | SKILL.md verify step 2           |
| OR4   | editing AGENTS.md, AI_HANDOFF.md, plans, etc.  | use Edit tool only, never sed/redirection      | SKILL.md open step 8             |
| OR5   | editing CHANGELOG.md or LANDMINES.md            | prepend-only, never append or edit existing    | SKILL.md close step 12           |
| OR6   | any plan                                        | pre-declare scope: WILL edit / will NOT edit   | plan header (universal)          |
| OR7   | any datetime code                               | never mix naive/aware, use timezone.utc          | SKILL.md verify step 2           |
| OR8   | any temp file creation                          | dedicated temp dir, delete after consume       | SKILL.md open step 8             |
| OR9   | new implementation                              | corresponding test file with passing tests     | SKILL.md close step 1            |
| OR10  | test deletion requested                         | STOP, scope deviation                          | SKILL.md close step 1            |
| OR11  | failing test                                    | fix root cause, never re-run without fix       | SKILL.md close step 1            |
| OR12  | git commit                                      | never --no-verify, fix hooks                   | SKILL.md close step 19           |
| OR13  | hook exclusion requested                        | STOP, out-of-scope                             | SKILL.md close step 19           |
| OR14  | dependency change                               | runtime deps in txt/requirements.txt only      | SKILL.md close step 5            |
| OR15  | AR check script edit                            | STOP, never edit to make failure pass          | SKILL.md close step 8            |
| OR16  | backend + UI plan                               | backend ships with UI surface                  | plan header (conditional)        |
| OR17  | deliverable incomplete                          | defer per item, log in exec log + DEBT         | SKILL.md close step 14           |
| OR18  | "already done" claim                            | require logged command + exit code             | plan header (conditional)        |
| OR19  | test/mypy/static-analysis failure               | no "pre-existing" exemption, fix or DEBT       | SKILL.md close step 1            |
| OR20  | skipped test                                    | carry # TODO(prompt-N), >=3 consecutive = fix   | SKILL.md close step 1            |
| OR21  | HTML/CSS/JS plan                                | syntax validation before tests                 | SKILL.md open step 12-15         |
| OR22  | new test                                        | real-shape fixtures, no MagicMock for domain   | SKILL.md close step 1            |
| OR23  | any commit                                      | stray-file scan: git status -s after git add   | SKILL.md close step 17           |
| OR24  | user-authorized exception                       | needs target plan documentation                | SKILL.md close step 14           |
| OR25  | any test                                        | 30s timeout via pytest-timeout                 | pyproject.toml (discoverable)    |
| OR26  | skill workflow                                  | follow systematically, no skipping             | SKILL.md open step 1             |
| OR27  | any plan file                                   | never delete prompt files                      | SKILL.md close step 18           |
| OR28  | any governance doc                              | never delete content, prepend-only             | OR-GOV (universal)               |
| OR29  | non-scan plan                                   | pytest scoped to changed files + dependents    | SKILL.md close step 1            |
| OR30  | any instruction                                 | follow literally, restrictive terms = exact    | OR-LIT (universal)               |
```

### 4.3 .agent/architect/RULES_REFERENCE.md (new)

This is the full text of every AR1-30 and OR1-30, moved from the current AGENTS.md. Content is identical to current AGENTS.md's AR and OR sections, just relocated. No rewording, no additions. The only change is location.

Format: one section per rule, stable ID, append-only.

```markdown
# RULES_REFERENCE.md

Full rule bodies. Architect-only reference. Executor never reads this file.

## AR1. Owner <-> Orchestrator only
Chain: Orchestrator -> Manager -> Worker. Bypass allowed for single-Worker, single-capability, no-state tasks. All Owner-facing output routes through Orchestrator.

## AR2. Workers query Librarian directly for memory
No component queries a memory backend directly.

## AR3. All model inference routes through Adapters
No component loads weights or calls inference endpoints directly.

... (all AR1-30 and OR1-30, verbatim from current AGENTS.md)
```

### 4.4 Plan Header Template (edit in AI_HANDOFF.md)

```markdown
Depends on: <prerequisite plan numbers>
Vision principles: <which of 14 this satisfies/affects>
Open questions resolved: <which Q1-Q34, or "none">
Applicable rules: <AR/OR IDs resolved by Architect, each with concrete enforcement action>
  e.g. "AR7: run scripts/ar_checks/check_ar7_allowlist.py before commit"
  e.g. "AR12: verify FastAPI runs as separate process, imports via public API only"
  e.g. "OR16: backend ships with UI surface -- defer if explicitly scoped out"
```

### 4.5 .devin/skills/open/SKILL.md (edited)

```markdown
---
name: open
description: Run at start of every plan. Don't skip steps.
argument-hint: "[plan-number]"
allowed-tools:
  - read
  - grep
  - glob
  - exec
  - edit
  - write
---

Run the /open workflow for the current plan. Follow all steps in order. Don't skip steps.

## Read context

1. Read `AGENTS.md` in full. (~30 lines)
2. Read this plan's `Applicable rules:` header field. Apply exactly those rules plus AGENTS.md's universal set.
3. Read `prompts/plan-{N}-Rev{X}.md` in full.
4. Read `CHANGELOG.md`'s most recent `## prompt-{N-1}` entry.

## Pre-execution clarification

5. Identify 1-3 ambiguities in the plan. Check for: (a) undefined terms, (b) conflicting requirements, (c) missing preconditions.
6. Ask user. Wait for answers.
7. Post answers in-session as "Plan {N} clarifications". Do not write to the execution log.
8. If no ambiguities: log "No ambiguities -- proceeding with Phase 1".

## Setup

9. Add new landmines to `.agent/shared/LANDMINES.md`. (Promoting a landmine to an AR/OR rule is an Architect action at Round Table -- not an Executor mid-plan edit.)
10. If LANDMINES.md changed: `git add -A && git status -s && git commit -m "docs: add landmines for prompt-{N}"`. Else: log "N/A".
10.5. `git add prompts/*.md` -- ensure ALL plan files in prompts/ are added to git.
11. Update `.agent/shared/PLANS.md` with new plan entry.
12. Begin Phase 1.

## Incremental verification (after each phase)

13-17. [unchanged -- same as current open/SKILL.md steps 11-15]
```

**Key changes from current open/SKILL.md:**
- Step 1.5 ("if edge cases not covered... read AGENTS_EXTENDED.md") -- DELETED. No more ambiguity judgment for Executor.
- Step 2 (was step 3) -- NEW: Read plan's `Applicable rules:` header. This is the resolved rule list from Architect.
- Step 8 (was step 8) -- SPLIT: Executor still prepends to LANDMINES.md (cheap, no reasoning). But promoting to AR/OR becomes Architect action.
- All path references updated to `.agent/executor/` and `.agent/architect/`.

### 4.6 .devin/skills/close/SKILL.md (edited)

Path references updated from root-level files to `.agent/executor/` locations. Content otherwise identical. Key changes:
- All `AGENTS.md` references -> `.agent/architect/RULES_REFERENCE.md` (for Architect-only context)
- All `PLANS.md`, `CHANGELOG.md`, `DEBT.md`, `LANDMINES.md` references -> `.agent/executor/`
- All `scripts/` references -> `.agent/executor/scripts/`
- All `prompts/` references -> `.agent/executor/prompts/`

### 4.7 .devin/skills/scan/SKILL.md (edited)

Same path updates. One addition:
- Step 2 (scan LANDMINES.md for un-graduated rules): also report which AR/OR entries `resolve_rules.py` matched zero times across the last 5 plans, as candidates for a demotion DD.

### 4.8 .devin/skills/verify/SKILL.md (edited)

Path updates only. Content otherwise identical.

### 4.9 .agent/executor/scripts/resolve_rules.py (new)

```python
#!/usr/bin/env python3
# resolve_rules.py -- Mechanical first pass for Architect rule resolution.
#
# Takes a draft plan's declared file globs and tech-stack tags,
# matches against RULES_INDEX.md trigger conditions,
# outputs a candidate AR/OR subset for Architect review.
#
# Usage:
#     python resolve_rules.py --plan prompts/plan-25-rev1.md
#     python resolve_rules.py --files "sovereignai/orchestrator/*.py,tui/panels/*.py"
#     python resolve_rules.py --tags "fastapi,ui,tui"
#
# Output: JSON list of {rule_id, trigger, enforcement_action, confidence}
#         confidence = "mechanical" (glob match) or "heuristic" (tag match)
#         Architect reviews and corrects before writing to plan header.
```

**Implementation sketch:**
- Parse plan file for "WILL edit:" and "WILL NOT edit:" declarations
- Parse for tech-stack tags (FastAPI, Textual, MCP, etc.)
- Match against RULES_INDEX.md trigger conditions using glob + keyword matching
- Output candidate list with confidence scores
- Architect reviews, adds/removes heuristically-detected rules, writes final `Applicable rules:` to plan header

### 4.10 .agent/architect/AI_HANDOFF.md (moved + edited)

Moved from root. Edits:
- All path references updated to `.agent/executor/` and `.agent/architect/`
- Plan Template section updated with `Applicable rules:` field
- S0.2 updated: "Read AGENTS.md in full" (now ~30 lines, not 135)
- S0.5 updated: "Harness check" references `.agent/architect/RULES_INDEX.md` for context
- GR rules updated: GR19 added (harness check in every plan), GR20 added (AGENTS.md split threshold at 200 lines -- now moot since target is 30, but kept as safety rail)

---

## 5. Token Cost Analysis

### Current state (per Executor /open)

| File | Lines | Bytes | Read every /open? |
|---|---|---|---|
| AGENTS.md | 135 | 7,053 | Yes |
| open/SKILL.md | 44 | 2,008 | Yes |
| close/SKILL.md | 132 | 6,935 | No (only at /close) |
| scan/SKILL.md | 53 | 2,918 | No (only at scan) |
| verify/SKILL.md | 24 | 874 | Per-edit |
| **Total per /open** | **179** | **9,061** | -- |

### Proposed state (per Executor /open)

| File | Lines | Bytes | Read every /open? |
|---|---|---|---|
| AGENTS.md | ~30 | ~800 | Yes |
| Plan header `Applicable rules:` | ~5 | ~300 | Yes (part of plan file) |
| open/SKILL.md | ~40 | ~1,800 | Yes |
| **Total per /open** | **~70** | **~2,900** | -- |

**Savings: ~109 lines, ~6,100 bytes per /open (~67% reduction).**

### Cost shift to Architect (per plan)

| Action | Lines | Bytes | When |
|---|---|---|---|
| Read RULES_INDEX.md | ~35 | ~1,500 | Once per plan |
| Read RULES_REFERENCE.md (sections) | ~20 | ~1,000 | Only for matched rules |
| Run resolve_rules.py | -- | -- | Once per plan |
| Review + correct output | -- | -- | Once per plan |
| Write `Applicable rules:` to plan header | ~5 | ~300 | Once per plan |
| **Total per plan** | **~60** | **~2,800** | **At authoring time** |

The Architect already reads the full rule graph for Round Table prep, so this is marginal additional cost. The Executor saves ~6,100 bytes every /open, compounded across every plan execution.

---

## 6. Migration Path

1. **Create new directory structure** -- `.agent/architect/` and `.agent/executor/`
2. **Move files** -- no content changes, just `git mv`
3. **Create RULES_REFERENCE.md** -- copy AR/OR sections from current AGENTS.md verbatim
4. **Create RULES_INDEX.md** -- new file, trigger conditions from analysis above
5. **Rewrite AGENTS.md** -- ~30 lines, universal rules only
6. **Edit skill files** -- path updates, step 1.5 deletion, step 8 split
7. **Create resolve_rules.py** -- mechanical rule resolution script
8. **Update AI_HANDOFF.md** -- path updates, plan template with `Applicable rules:`
9. **Update plan headers** -- retroactively add `Applicable rules:` to existing draft plans (22-24)
10. **Update PLANS.md** -- new baseline: AGENTS.md 30 lines, test count unchanged
11. **Run scan** -- verify no broken references, cross-reference check passes
12. **Commit** -- "prompt-25: Workflow redesign -- token cost redistribution, AGENTS.md minimization"

---

## 7. Risks and Mitigations

| Risk | Mitigation |
|---|---|
| Architect misses a rule during resolution | resolve_rules.py mechanical first pass catches 80%+ of matches; Architect reviews full output; scan step 2 catches misses |
| Executor doesn't know a rule exists because it's not in AGENTS.md | `Applicable rules:` header is mandatory; missing = plan header incomplete = STOP at open step 2 |
| RULES_INDEX.md trigger conditions drift | LANDMINES.md entries tagged by trigger content (not OR number); cross-reference check verifies |
| Skills reference old paths after move | Global search/replace in skill files; verify step catches syntax errors |
| Governance history lost | No files deleted -- only moved via `git mv`; OR11/OR28 still hold |
| Round Table objects to structural change | This document IS the Round Table input; critique expected and welcome |

---

## 8. Open Questions for Round Table

- Q-25.1: Should `resolve_rules.py` use glob matching, AST parsing, or both? Glob is faster but less precise; AST catches imports but requires parsing.
- Q-25.2: Should the `Applicable rules:` field include enforcement actions inline ("run script X") or just rule IDs with lookup? Inline is more token-efficient for Executor; IDs with lookup is less brittle if scripts change.
- Q-25.3: Should AGENTS.md include a one-line pointer to each skill file ("open: .devin/skills/open/SKILL.md") or is the workflow contract sufficient? Pointer helps discoverability but adds lines.
- Q-25.4: Should RULES_INDEX.md live under `.agent/architect/` (Architect-only) or `.agent/executor/` (shared, read-only for Executor)? Shared risks Executor reading it (defeating the purpose); Architect-only requires trust in resolution.
- Q-25.5: Should the current AGENTS.md be archived (LANDMINES-ARCHIVE.md style) or is git history sufficient? Git history is sufficient per OR11/OR28 (no deletion, just move).

---

## 9. Decisions Proposed

- **DD-25.1**: Move AR1-30 and OR1-30 from AGENTS.md to `.agent/architect/RULES_REFERENCE.md`. Rejected alternative: keep in AGENTS.md and add new rules (consequence: 135->200+ lines, context crowding, rule dropout). Accepted: separate files, progressive disclosure.
- **DD-25.2**: Add `Applicable rules:` to plan header template. Rejected alternative: Executor reads full RULES_REFERENCE.md when ambiguous (consequence: ambiguity judgment costs tokens every session, per Claude Code findings). Accepted: Architect resolves once, Executor reads resolved list.
- **DD-25.3**: Create `resolve_rules.py` for mechanical rule resolution. Rejected alternative: Architect resolves from memory (consequence: D5-style drift, missed rules). Accepted: mechanical first pass + human review.
- **DD-25.4**: Split open/SKILL.md step 8: Executor prepends to LANDMINES.md only; AR/OR promotion becomes Architect Round Table action. Rejected alternative: Executor edits AGENTS.md directly (consequence: rule-graph reasoning in execution loop, error-prone). Accepted: shift reasoning-heavy step upstream.
- **DD-25.5**: Move governance docs to `.agent/` subdirectory. Rejected alternative: keep at root (consequence: clutter, no role separation). Accepted: explicit ownership, Executor knows what not to read.

---

*End of proposal. Ready for Round Table critique.*
