# SovereignAI Workflow Redesign Proposal
## Version: Rev2 -- Post-Round Table
## Date: 2026-07-18
## Depends on: Round Table Rev1 (7 panelists, ~110 findings, 0 pass, 7 block)
## Open questions resolved: Q-25.1 (AST+glob hybrid), Q-25.2 (stable identifiers with runtime resolver), Q-25.4 (Architect-only, enforced by convention not permissions), Q-25.6 (scope drift = /reresolve), Q-25.7 (zero matches = Architect review required, not "no rules apply"), Q-25.9 (re-resolution at phase boundaries only)

---

## 1. Problem Statement (unchanged from Rev1)

Current AGENTS.md is 135 lines, 7,053 bytes. The Executor re-reads it in full at every `/open` (OR1/S0.2). Per OpenAI's harness engineering research, a bloated always-loaded instruction file crowds out task context, causes agents to pattern-match locally instead of reasoning globally, and cannot be mechanically verified for freshness.

The current file mixes three concerns that should be separated:
1. **Workflow contract** -- universal, applies to every plan
2. **Subsystem rules** -- only relevant when touching specific code
3. **Rationale** -- why a rule exists, needed for Architect decisions, not Executor execution

Additionally, the skills (open/SKILL.md, close/SKILL.md, scan/SKILL.md, verify/SKILL.md) already encode most operational rules as literal numbered steps. AGENTS.md restates them in prose, creating duplication.

---

## 2. Design Goals (unchanged from Rev1)

| Goal | How |
|---|---|
| Minimize Executor per-session token cost | AGENTS.md -> ~40 lines; per-plan rules resolved by Architect into plan header |
| Shift reasoning cost to Architect | Architect resolves rule applicability once at plan-authoring time |
| Mechanical enforcement over prose | Rules backed by scripts don't need prose restatement |
| Progressive disclosure | Executor reads only what is relevant to this plan |
| No deletion of governance history | OR11/OR28 still hold; content moves, never deleted |
| Skills remain authoritative | open/close/scan/verify SKILL.md are the literal checklists; AGENTS.md points to them |

---

## 3. Proposed Directory Structure

```
SovereignAI/
├── AGENTS.md                           # NEW: ~40 lines, workflow contract + universal rules only
├── README.md                           # unchanged
├── .gitignore                          # EDITED: explicit log tracking statement
├── pyproject.toml                      # EDITED: test paths updated to .agent/executor/tests/
├── .pre-commit-config.yaml             # EDITED: script paths updated to .agent/executor/scripts/
│
├── .agent/                             # NEW: all governance, split by role
│   ├── architect/                      # Architect-only files (Executor never reads by convention)
│   │   ├── AI_HANDOFF.md             # moved from root, process guide
│   │   ├── PRINCIPLES.md             # moved from root, 14 principles
│   │   ├── RULES_INDEX.md            # NEW: trigger->pointer table, formal predicates
│   │   ├── RULES_REFERENCE.md        # NEW: full AR/OR bodies, Architect-only reference
│   │   ├── PROMOTIONS.md             # NEW: landmine->AR/OR promotion queue
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
│       │   ├── resolve_rules.py      # NEW: AST+glob hybrid, mechanical first pass
│       │   ├── get_current_plan.py
│       │   ├── is_scan_plan.py
│       │   ├── get_scoped_tests.py
│       │   ├── verify_syntax.py
│       │   ├── verify_close.py       # EDITED: path references updated
│       │   ├── check_rule_crossrefs.py
│       │   └── ar_checks/            # EDITED: path references updated, --dry-run added
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
│       │   ├── plan-{N}-Rev{n}.md    # header gains `Applicable rules:` + `Mechanical resolution:` fields
│       │   └── completed/
│       │
│       └── logs/                     # moved from root, tracked (append-only per OR28)
│           ├── execution-log-prompt-{N}.md
│           └── screenshots/
│
├── .devin/                             # unchanged role, skill files edited
│   └── skills/
│       ├── open/SKILL.md             # EDITED: Step 1.5 deleted, Step 2.5 added, Step 8 split, half-step notation
│       ├── close/SKILL.md            # EDITED: path references updated, step 17 cross-reference preserved
│       ├── scan/SKILL.md             # EDITED: steps 2a/2b/2c added, path references updated
│       ├── verify/SKILL.md           # EDITED: path references updated
│       └── review/SKILL.md           # unchanged
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
└── archive/                            # LANDMINES-ARCHIVE.md + AGENTS.md.pre-split (frozen copy)
```

---

## 4. File Contents

### 4.1 AGENTS.md (new, ~40 lines)

```markdown
# AGENTS.md

Authority: .agent/architect/PRINCIPLES.md
Ambiguous -> .agent/shared/LANDMINES.md

## Workflow contract
Every plan: /open -> execute -> /close, per .devin/skills/{open,close,scan,verify}/SKILL.md.
Follow steps literally, in order, no skipping. Exit!=0 = STOP.
Do not explain, justify, or offer workarounds -- STOP is the only valid response.

## Universal rules (apply to every plan, no exceptions)
AR11. No docstrings. Self-documenting names.
AR-DI. DI only: no globals, no context bags, <=15 constructor args.
       Script-enforced every /close via ar_checks/.
OR-GOV. Never delete governance-doc content. Prepend-only for LANDMINES.md/CHANGELOG.md.
OR-LIT. Follow instructions literally. Restrictive terms ('only', 'never', 'must') = exact compliance.
       Preferred terms ('preferably X unless cost >Y') = default to X with documented override condition.
       Advisory terms ('consider X') = evaluate X, document decision either way.
OR1.   File-scoped mypy only. Never `mypy .` except at scan prompts.
OR2.   Run scan tools ONE AT A TIME. Parallel execution corrupts output.
OR3.   Never use `replace_all`. Edit each occurrence individually.
OR4.   Structured-markdown edits (AGENTS.md, AI_HANDOFF.md, plans, CHANGELOG, workflow files)
       use Edit tool only. Never `sed` or redirection.
OR12.  Never `git commit --no-verify`. Fix hook issues.
OR23.  Stray-file scan: `git status -s` after `git add` before every commit.

## Plan-specific rules
Resolved per-plan by Architect into each plan's `Applicable rules:` header.
Apply exactly those, plus the universal set above.
Full rule index: .agent/architect/RULES_INDEX.md
Full rule bodies: .agent/architect/RULES_REFERENCE.md (Architect-only, not required Executor reading)
```

**Rationale for universal set (10 rules):**
- AR11, AR-DI, OR-GOV, OR-LIT: Same as Rev1 -- truly universal, not discoverable from code.
- OR1, OR2: Fire during mid-implementation verification (not just scan plans). Executor runs mypy or multiple tools outside scan context.
- OR3, OR4: Fire on every edit operation, regardless of subsystem. Cannot be subsystem-scoped.
- OR12: Fire on every git commit, including intermediate commits during long plans.
- OR23: Fire on every git add, including intermediate staging.

**What moves to RULES_REFERENCE.md:**
- AR1-AR10, AR12-AR30: Subsystem-specific. Only relevant when touching that subsystem.
- OR5-OR11, OR13-OR22, OR24-OR30: Most are already literal skill steps. OR5 (prepend-only) is covered by OR-GOV. OR6 (pre-declare scope) is plan-header universal. OR7 (datetime) is code-pattern specific. OR8 (temp files) is skill-step literal. OR9 (new implementation needs tests) is close/SKILL.md step 1. OR10 (test deletion = STOP) is close/SKILL.md step 1. OR11 (failing test = fix root cause) is close/SKILL.md step 1. OR13 (hook exclusion = STOP) is close/SKILL.md step 19. OR14 (dependency change) is close/SKILL.md step 5. OR15 (AR check script edit = STOP) is close/SKILL.md step 8. OR16 (backend+UI) is plan-header conditional. OR17 (defer per item) is close/SKILL.md step 14. OR18 ("already done" claim) is plan-header conditional. OR19 (no pre-existing exemption) is close/SKILL.md step 1. OR20 (skipped test) is close/SKILL.md step 1. OR21 (HTML/CSS/JS) is open/SKILL.md steps 12-15. OR22 (real-shape fixtures) is close/SKILL.md step 1. OR24 (user-authorized exception) is close/SKILL.md step 14. OR25 (30s timeout) is pyproject.toml. OR26 (skill workflow) is open/SKILL.md step 1. OR27 (never delete prompt files) is close/SKILL.md step 18. OR28 (never delete governance content) is OR-GOV. OR29 (pytest scoped) is close/SKILL.md step 1. OR30 (follow literally) is OR-LIT.

### 4.2 .agent/architect/RULES_INDEX.md (new, formal predicates)

```markdown
# RULES_INDEX.md

Trigger-condition -> rule pointer table. One row per rule.
Architect uses this to resolve `Applicable rules:` for each plan.
Mechanical first pass: .agent/executor/scripts/resolve_rules.py

## Predicate definitions

- `glob(path)`: plan's `WILL edit:` globs include files matching `path`
- `imports(module)`: AST analysis of `WILL edit:` files detects `import module` or `from module import`
- `tag(keyword)`: plan's declared tags include `keyword` or synonym
- `semantic(field)`: plan header includes explicit `Side effects anticipated: yes` or similar field
- `always`: rule applies to every plan (already in AGENTS.md universal set, not in index)

## Conditional rules

| Rule  | Predicate                                    | Enforcement action                              | Full text ->                      |
|-------|---------------------------------------------|------------------------------------------------|----------------------------------|
| AR1   | glob("sovereignai/orchestrator/**") OR glob("sovereignai/workers/**") | verify chain: Owner->Orchestrator->Manager->Worker | RULES_REFERENCE.md secAR1          |
| AR2   | glob("sovereignai/librarian/**") OR glob("sovereignai/memory/**") OR imports("librarian") | verify no direct backend queries               | RULES_REFERENCE.md secAR2          |
| AR3   | glob("adapters/**") OR imports("adapters") OR tag("model", "inference", "llm") | verify inference routes through adapters       | RULES_REFERENCE.md secAR3          |
| AR4   | glob("sovereignai/**") AND (new file OR new import not in capability graph) | verify capability graph discovery, no hardcoded  | RULES_REFERENCE.md secAR4          |
| AR5   | glob("adapters/**") AND tag("mcp", "server", "wrapper") | verify adapter wrapper before use              | RULES_REFERENCE.md secAR5          |
| AR6   | glob("adapters/**") AND (new file OR tag("health", "check")) | verify health_check() + graceful error           | RULES_REFERENCE.md secAR6          |
| AR7   | glob("tui/panels/**") OR glob("app/web/**") OR imports("tui.panels") | run scripts/ar_checks/check_ar7_allowlist.py   | RULES_REFERENCE.md secAR7          |
| AR8   | glob("sovereignai/**") AND tag("trace", "log", "emit") | verify local SSD only, no external telemetry   | RULES_REFERENCE.md secAR8          |
| AR9   | glob("skills/**") AND tag("author", "manifest", "dag") | verify manifest+code+DAG output                | RULES_REFERENCE.md secAR9          |
| AR10  | glob("sovereignai/**") AND tag("external", "copy", "local") | verify local copy before use                   | RULES_REFERENCE.md secAR10         |
| AR12  | glob("web/**") OR imports("fastapi") OR imports("web") | verify separate process, public API surface    | RULES_REFERENCE.md secAR12         |
| AR13  | glob("web/**") AND (tag("auth", "sse", "cookie") OR imports("auth")) | verify HTTP session cookie, no query params    | RULES_REFERENCE.md secAR13         |
| AR14  | glob("web/schemas.py") OR glob("web/**/schemas.py") | verify DTOs in web/schemas.py                  | RULES_REFERENCE.md secAR14         |
| AR15  | glob("adapters/**") AND (new file OR tag("health", "check")) | verify health_check() returns typed dataclass  | RULES_REFERENCE.md secAR15         |
| AR16  | glob("sovereignai/**") AND (new class OR tag("capability", "conformance")) | verify <100ms, cached, fail-closed/open          | RULES_REFERENCE.md secAR16         |
| AR17  | glob("sovereignai/**") AND (changes public method signature OR tag("api", "contract")) | verify contract tests pass                     | RULES_REFERENCE.md secAR17         |
| AR18  | always (property-based tests run every commit) | property-based tests run (CI gate)             | RULES_REFERENCE.md secAR18         |
| AR19  | glob("sovereignai/**") AND (tag("memory", "backend", "swap") OR imports("memory_backend")) | verify CapabilityGraph pluggability            | RULES_REFERENCE.md secAR19         |
| AR20  | glob("sovereignai/**") AND (tag("crash", "recovery", "shutdown", "marker") OR semantic("shutdown logic")) | verify .shutdown_marker check                  | RULES_REFERENCE.md secAR20         |
| AR21  | glob("databases/**") OR glob("sovereignai/**") AND (tag("sqlite", "json", "atomic", "wal") OR semantic("durable backend")) | verify atomic writes, WAL, os.replace()        | RULES_REFERENCE.md secAR21         |
| AR22  | glob("sovereignai/**") AND (semantic("side effects") OR tag("trace", "emit", "log", "write", "network")) | verify trace event emission                    | RULES_REFERENCE.md secAR22         |
| AR23  | glob("sovereignai/**") AND (new entry point OR semantic("correlation ID", "request ID", "trace ID", "continuity")) | verify context var propagation                 | RULES_REFERENCE.md secAR23         |
| AR24  | glob("web/**") AND tag("logs", "panel", "sse", "trace") | verify /api/traces SSE consumption only        | RULES_REFERENCE.md secAR24         |
| AR25  | glob("databases/**") OR glob("services/**") | verify root-level packages, no nesting         | RULES_REFERENCE.md secAR25         |
| AR26  | glob("services/**") OR glob("databases/**") AND (new class OR tag("provider", "service")) | verify health_check() dataclass, lazy init     | RULES_REFERENCE.md secAR26         |
| AR27  | glob("web/**") AND (tag("models", "hardware", "panel") OR imports("models_panel") OR imports("hardware_panel")) | verify capability API consumption only         | RULES_REFERENCE.md secAR27         |
| AR28  | glob("adapters/**") AND (new file OR tag("manifest", "routing", "priority")) | verify routing_priority int, ascending         | RULES_REFERENCE.md secAR28         |
| AR29  | glob("sovereignai/**") AND tag("diagnostic", "harness", "test", "stage") | verify load->use->unload per stage               | RULES_REFERENCE.md secAR29         |
| AR30  | glob("tui/panels/**") OR imports("tui.panels") | verify real backend state, no placeholders     | RULES_REFERENCE.md secAR30         |
| OR5   | glob("CHANGELOG.md") OR glob("LANDMINES.md") | prepend-only, never append or edit existing    | SKILL.md close step 12 (OR-GOV)    |
| OR6   | always (plan header field)                  | pre-declare scope: WILL edit / will NOT edit   | plan header (universal)            |
| OR7   | glob("sovereignai/**") AND (imports("datetime") OR tag("datetime", "timezone")) | never mix naive/aware, use timezone.utc          | SKILL.md verify step 2             |
| OR8   | glob("sovereignai/**") AND tag("temp", "tmp", "temporary") | dedicated temp dir, delete after consume       | SKILL.md open step 8             |
| OR9   | glob("sovereignai/**") AND new file         | corresponding test file with passing tests     | SKILL.md close step 1            |
| OR10  | glob("tests/**") AND tag("delete", "remove") | STOP, scope deviation                          | SKILL.md close step 1            |
| OR11  | glob("tests/**") AND tag("failing", "fail")   | fix root cause, never re-run without fix       | SKILL.md close step 1            |
| OR13  | tag("hook", "exclude", "bypass")              | STOP, out-of-scope                             | SKILL.md close step 19           |
| OR14  | glob("txt/requirements.txt") OR tag("dependency", "requirements") | runtime deps in txt/requirements.txt only      | SKILL.md close step 5            |
| OR15  | glob("scripts/ar_checks/**") OR tag("ar_check", "script") | STOP, never edit to make failure pass          | SKILL.md close step 8            |
| OR16  | glob("sovereignai/**") AND (glob("web/**") OR glob("tui/**")) AND tag("backend", "ui") | backend ships with UI surface                  | plan header (conditional)        |
| OR17  | tag("incomplete", "defer", "debt")            | defer per item, log in exec log + DEBT         | SKILL.md close step 14           |
| OR18  | tag("already done", "done", "complete")       | require logged command + exit code             | plan header (conditional)        |
| OR19  | glob("tests/**") OR tag("test", "mypy", "static", "analysis") | no "pre-existing" exemption, fix or DEBT       | SKILL.md close step 1            |
| OR20  | glob("tests/**") AND tag("skip", "skipped", "todo") | carry # TODO(prompt-N), >=3 consecutive = fix   | SKILL.md close step 1            |
| OR21  | glob("web/**") OR glob("tui/**") AND tag("html", "css", "js", "frontend") | syntax validation before tests                 | SKILL.md open step 12-15         |
| OR22  | glob("tests/**") AND new file                 | real-shape fixtures, no MagicMock for domain   | SKILL.md close step 1            |
| OR24  | tag("exception", "user authorized", "scope deviation") | needs target plan documentation                | SKILL.md close step 14           |
| OR25  | always (pyproject.toml)                       | 30s timeout via pytest-timeout                 | pyproject.toml (discoverable)    |
| OR26  | always (skill workflow)                       | follow systematically, no skipping             | SKILL.md open step 1             |
| OR27  | glob("prompts/**") OR tag("prompt", "plan file") | never delete prompt files                      | SKILL.md close step 18           |
| OR28  | always (OR-GOV)                               | never delete content, prepend-only             | OR-GOV (universal)               |
| OR29  | glob("tests/**") AND NOT tag("scan")          | pytest scoped to changed files + dependents    | SKILL.md close step 1            |
| OR30  | always (OR-LIT)                               | follow literally, restrictive terms = exact    | OR-LIT (universal)               |
```

**Key changes from Rev1:**
- Formal predicates (glob, imports, tag, semantic, always) instead of natural language
- `imports()` predicate for cross-directory dependencies (addresses F16, F17)
- `semantic()` predicate for side effects, correlation IDs, durable backends (addresses F7)
- `always` predicate for rules already in AGENTS.md universal set (not in index)
- Synonym tables for keyword matching ("trace ID", "request ID", "continuity token" all map to AR23)
- Every predicate is testable -- if you can not write a test that fires the trigger, the trigger is too vague

### 4.3 .agent/architect/RULES_REFERENCE.md (new)

Identical to current AGENTS_EXTENDED.md content, relocated. No rewording. Append-only.

### 4.4 Plan Header Template (edit in AI_HANDOFF.md)

```markdown
Depends on: <prerequisite plan numbers>
Vision principles: <which of 14 this satisfies/affects>
Open questions resolved: <which Q1-Q34, or "none">
Mechanical resolution: <output from resolve_rules.py, embedded verbatim, signed by Architect>
Applicable rules: <AR/OR IDs + stable action identifiers, resolved by Architect>
  e.g. "AR7: ALLOWLIST_CHECK"  # runtime resolver maps to actual script path
  e.g. "AR12: FASTAPI_PROCESS_VERIFY"
  e.g. "OR16: BACKEND_UI_SURFACE -- defer if explicitly scoped out"
Side effects anticipated: <yes/no>  # triggers AR22 semantic predicate
New entry points: <list>           # triggers AR23 semantic predicate
Durable backends: <list>          # triggers AR21 semantic predicate
```

**Key changes from Rev1:**
- `Mechanical resolution:` field -- resolve_rules.py output embedded verbatim. Architect signs off on coverage report, not just output list. (addresses F9, F12)
- `Applicable rules:` uses stable identifiers, not inline script paths. Runtime resolver maps identifiers to actual commands. (addresses F10, F34)
- `Side effects anticipated`, `New entry points`, `Durable backends` -- explicit semantic fields trigger semantic predicates. (addresses F7)
- Max 7 entries in `Applicable rules:` field. Overflow requires escalation to Architect. (addresses F13)

### 4.5 .devin/skills/open/SKILL.md (edited, half-step notation)

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

1. Read `AGENTS.md` in full. (~40 lines)
2. Read this plan's `Mechanical resolution:` and `Applicable rules:` header fields.
   Apply exactly those rules plus AGENTS.md's universal set.
   If either field is empty, malformed, or resolve_rules.py output is absent:
   STOP. Surface error: "Plan header incomplete -- Architect review required."
3. Read `prompts/plan-{N}-Rev{X}.md` in full.
4. Read `CHANGELOG.md`'s most recent `## prompt-{N-1}` entry.

## Pre-execution clarification

5. Identify 1-3 ambiguities in the plan. Check for: (a) undefined terms, (b) conflicting requirements, (c) missing preconditions.
6. Ask user. Wait for answers.
7. Post answers in-session as "Plan {N} clarifications". Do not write to the execution log.
8. If no ambiguities: log "No ambiguities -- proceeding with Phase 1".

## Setup

9. Add new landmines to `.agent/shared/LANDMINES.md`.
10. If LANDMINES.md changed: `git add -A && git status -s && git commit -m "docs: add landmines for prompt-{N}"`. Else: log "N/A".
10.5. `git add prompts/*.md` -- ensure ALL plan files in prompts/ are added to git.
11. Update `.agent/executor/PLANS.md` with new plan entry.
12. Begin Phase 1.

## Scope expansion protocol (mid-plan)

12.5. If during execution you discover you must edit files NOT in the plan's `WILL edit:` list:
      a. Halt current phase.
      b. Run `.agent/executor/scripts/resolve_rules.py --diff` against actual git diff.
      c. Compare output to plan's `Mechanical resolution:` field.
      d. If new rules triggered: log discrepancy to execution log.
         Continue with best-effort interpretation of implied rules.
         Architect resolves at next Round Table or via `/review-promotions`.
      e. Resume phase.

## Incremental verification (after each phase)

13-17. [unchanged -- same as current open/SKILL.md steps 11-15]
```

**Key changes from Rev1:**
- Step 1.5 deleted (no more ambiguity judgment for Executor)
- Step 2.5 added (was step 2 in Rev1) -- read header fields, with structural STOP condition
- Step 8 split into 9 (landmines) and promotion pipeline (Architect-only)
- Step 12.5 added -- /reresolve protocol for scope expansion (addresses F1, F17)
- Half-step notation preserves all cross-references (addresses F18)

### 4.6 .devin/skills/close/SKILL.md (edited)

Path references updated. One addition:
- Step 19 (pre-commit): verify `.pre-commit-config.yaml` hooks run successfully after migration.
- Step 17 cross-reference preserved: "see open/SKILL.md step 10.5 for stray-file handling" (step 10.5 unchanged)

### 4.7 .devin/skills/scan/SKILL.md (edited)

Path references updated. Steps 2a/2b/2c:

```markdown
## Scan LANDMINES.md and rule index

2a. Scan LANDMINES.md for un-graduated rules (existing step 2).
    Report: landmines discovered >=3 plans ago with no promotion DD.

2b. Report which AR/OR entries resolve_rules.py matched zero times across last 5 plans.
    These are demotion candidates -- propose as DDs.

2c. Re-run resolve_rules.py against last completed plan's actual git diff.
    Compare to plan header's `Mechanical resolution:` field.
    Report discrepancies as rule-resolution misses -- add to LANDMINES.md.
```

### 4.8 .devin/skills/verify/SKILL.md (edited)

Path references updated. Content otherwise identical.

### 4.9 .agent/executor/scripts/resolve_rules.py (new, AST+glob hybrid)

```python
#!/usr/bin/env python3
# resolve_rules.py -- Mechanical first pass for Architect rule resolution.
#
# Hybrid: glob matching for path-based triggers, AST parsing for import-based
# triggers, keyword synonym table for tag-based triggers, explicit fields for
# semantic triggers.
#
# Usage:
#     python resolve_rules.py --plan prompts/plan-25-rev1.md
#     python resolve_rules.py --files "sovereignai/orchestrator/*.py,tui/panels/*.py"
#     python resolve_rules.py --tags "fastapi,ui,tui"
#     python resolve_rules.py --diff  # reads actual git diff, not declared scope
#
# Output: JSON with two sections:
#   {
#     "mechanical": [{"rule_id": "AR7", "predicate": "glob(tui/panels/**)",
#                     "confidence": "mechanical", "enforcement_action": "ALLOWLIST_CHECK"}],
#     "semantic": [{"rule_id": "AR22", "predicate": "semantic(side_effects)",
#                   "confidence": "requires_architect_signoff",
#                   "enforcement_action": "TRACE_EVENT_VERIFY"}],
#     "coverage_report": "Evaluated 34 triggers. 12 fired (mechanical). 3 semantic flagged for review."
#   }
#
# Architect must sign off on coverage report, not just output list.
```

**Key changes from Rev1:**
- AST parsing for `imports()` predicate
- Keyword synonym table ("trace ID" -> AR23, "request ID" -> AR23, etc.)
- `--diff` mode reads actual git diff, not declared scope (addresses F17)
- Coverage report showing evaluated vs. fired triggers (addresses F9, F22)
- No confidence labels on mechanical matches -- all require Architect review (addresses F19)
- Semantic matches flagged as "requires_architect_signoff" -- cannot be auto-accepted

### 4.10 .agent/architect/PROMOTIONS.md (new)

```markdown
# PROMOTIONS.md

Landmine -> AR/OR promotion queue. Executor-discovered candidates.

## Format
| Plan | Phase | Landmine | Rationale | Status | Round Table |
|------|-------|----------|-----------|--------|-------------|

## Rules
- Executor logs candidate within 1 hour of discovery.
- Architect reviews at next Round Table or via `/review-promotions`.
- Max age in LANDMINES.md: 3 plans. After 3 plans, mandatory promotion or explicit rejection DD.
- Rejected candidates: move to LANDMINES-ARCHIVE.md with rejection reason.
```

### 4.11 .agent/architect/AI_HANDOFF.md (moved + edited)

- All path references updated
- Plan Template updated with `Mechanical resolution:`, `Applicable rules:`, semantic fields
- S0.2 updated: "Read AGENTS.md in full" (~40 lines)
- S0.5 updated: Harness check references RULES_INDEX.md formal predicates
- GR19 added: Harness check in every plan
- GR20 added: AGENTS.md split threshold at 200 lines (safety rail, now moot at 40)
- Composition model added: canonical ordering, conflict handling, max 7 header entries, escalation route

---

## 5. Token Cost Analysis (Revised)

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
| AGENTS.md | ~40 | ~1,200 | Yes |
| Plan header fields | ~10 | ~600 | Yes (part of plan file) |
| open/SKILL.md | ~45 | ~2,100 | Yes |
| **Total per /open** | **~95** | **~3,900** | -- |

**Savings: ~84 lines, ~5,200 bytes per /open (~57% reduction for trivial plans, ~40% for complex plans).**

### Cost shift to Architect (per plan)

| Action | Lines | Bytes | When |
|---|---|---|---|
| Read RULES_INDEX.md | ~60 | ~2,500 | Once per plan |
| Read RULES_REFERENCE.md (sections) | ~20 | ~1,000 | Only for matched rules |
| Run resolve_rules.py | -- | -- | Once per plan |
| Review coverage report + sign off | -- | -- | Once per plan |
| Write header fields | ~10 | ~600 | Once per plan |
| **Total per plan** | **~90** | **~4,100** | **At authoring time** |

The Architect already reads the full rule graph for Round Table prep, so this is marginal additional cost. The Executor saves ~5,200 bytes every /open, compounded across every plan execution.

**Honest range**: 40-57% reduction depending on plan complexity. Trivial plans (1 subsystem) save ~57%. Complex plans (4+ subsystems) save ~40% due to larger header fields.

---

## 6. Migration Path (Revised)

1. **Pre-migration audit** -- grep over `**/*.py`, `pyproject.toml`, `.pre-commit-config.yaml`, `.github/workflows/*` for literal strings of moved paths. Checklist every hit resolved. (addresses F2, F3, F6)
2. **Create new directory structure** -- `.agent/architect/` and `.agent/executor/`
3. **Move files** -- `git mv`, no content changes
4. **Create RULES_REFERENCE.md** -- copy AGENTS_EXTENDED.md verbatim
5. **Create RULES_INDEX.md** -- formal predicates from analysis above
6. **Rewrite AGENTS.md** -- ~40 lines, 10 universal rules
7. **Edit skill files** -- path updates, half-step notation, step 12.5 added
8. **Create resolve_rules.py** -- AST+glob hybrid, synonym table, --diff mode
9. **Create PROMOTIONS.md** -- promotion queue
10. **Update pyproject.toml** -- test paths to `.agent/executor/tests/`
11. **Update .pre-commit-config.yaml** -- script paths to `.agent/executor/scripts/`
12. **Update .gitignore** -- explicit log tracking statement
13. **Update AI_HANDOFF.md** -- path updates, plan template with new fields, composition model
14. **Update plan headers** -- retroactively add fields to existing draft plans (22-24)
15. **Update PLANS.md** -- new baseline: AGENTS.md 40 lines, test count unchanged
16. **Add --dry-run to ar_checks** -- verify paths before executing
17. **Run scan** -- verify no broken references, cross-reference check passes
18. **Run pre-commit locally** -- verify hooks pass after path updates
19. **Run full test suite** -- verify pytest discovers tests at new path
20. **Commit** -- "prompt-25: Workflow redesign -- token cost redistribution, AGENTS.md minimization"
21. **Annotate historical logs** -- prepend migration note to all pre-prompt-25 logs
22. **Smoke test** -- run /open on draft plan, confirm step 1 reads new AGENTS.md, step 2.5 reads header, no broken numbering

---

## 7. Risks and Mitigations (Revised)

| Risk | Mitigation | Credibility |
|---|---|---|
| Architect misses a rule during resolution | resolve_rules.py coverage report + Architect sign-off; scan step 2c catches post-hoc misses | Credible -- independent check |
| Executor doesn't know a rule exists | `Mechanical resolution:` field mandatory; CI/pre-commit rejects empty/malformed headers; structural STOP in open step 2.5 | Credible -- structural enforcement |
| RULES_INDEX.md trigger drift | Formal predicates (glob/imports/tag/semantic) are testable; drift detected by resolver test suite | Credible -- testable predicates |
| Skills reference old paths | Pre-migration grep audit; post-migration pre-commit + test suite + smoke test | Credible -- exhaustive audit |
| Governance history lost | `git mv` only; no deletion; historical logs annotated; AGENTS.md.pre-split archived | Credible -- git history + annotations |
| Plan header stale enforcement actions | Stable identifiers with runtime resolver; controlled regeneration on script changes | Credible -- indirection layer |
| Scope expansion mid-plan | /reresolve protocol (open step 12.5); resolve_rules.py --diff mode; discrepancy logged | Credible -- explicit protocol |
| Round Table objects to structural change | Quantitative token analysis (40-57% range), reversible migration path (git mv), explicit rollback procedure: revert git mv, restore old AGENTS.md, update skill paths back | Credible -- reversible + quantitative |

---

## 8. Open Questions (Revised -- 11 total)

- Q-25.1: **RESOLVED** -- AST+glob hybrid. Glob for path-based, AST for import-based, keyword synonym table for tag-based, explicit fields for semantic.
- Q-25.2: **RESOLVED** -- Stable identifiers with runtime resolver. Not inline script paths.
- Q-25.3: Should AGENTS.md include one-line skill file pointers? **OPEN** -- adds ~5 lines. Trade-off: discoverability vs. brevity.
- Q-25.4: **RESOLVED** -- Architect-only, enforced by convention (OR-LIT). No filesystem permissions.
- Q-25.5: Should current AGENTS.md be archived? **RESOLVED** -- Yes, `archive/AGENTS.md.pre-split`. Git history sufficient but discoverability improved by frozen copy.
- Q-25.6: **RESOLVED** -- Scope drift = /reresolve protocol. Halt -> run resolve_rules.py --diff -> log discrepancy -> continue with best effort -> Architect resolves at Round Table.
- Q-25.7: **RESOLVED** -- Zero matches = Architect review required, not "no rules apply." Plan cannot proceed without Architect sign-off on coverage report.
- Q-25.8: How are rules deprecated? **OPEN** -- Mark DEPRECATED in RULES_INDEX.md, move to archive/, scan step 2b reports zero-match candidates.
- Q-25.9: **RESOLVED** -- Re-resolution at phase boundaries only. Mid-plan scope expansion uses /reresolve protocol, not full re-resolution.
- Q-25.10: Plan-to-plan inheritance? **OPEN** -- Does plan 27 inherit rules from plan 26 if 27 depends on 26? Default: no inheritance; each plan re-resolved independently.
- Q-25.11: Stale header vs. fresh index? **OPEN** -- How does Executor handle plan header referencing rule demoted in RULES_INDEX.md since authoring? Runtime resolver checks rule status; deprecated rules logged as warnings, not failures.

---

## 9. Decisions Proposed (Revised)

- **DD-25.1**: Move AR1-30 and OR1-30 from AGENTS.md to `.agent/architect/RULES_REFERENCE.md`. Rejected alternative: keep in AGENTS.md (consequence: 135->200+ lines, context crowding, rule dropout). Accepted: separate files, progressive disclosure.
- **DD-25.2**: Add `Mechanical resolution:` and `Applicable rules:` to plan header template. Rejected alternative: Executor reads full RULES_REFERENCE.md when ambiguous (consequence: ambiguity judgment costs tokens every session). Accepted: Architect resolves once, Executor reads resolved list + coverage report.
- **DD-25.3a**: Adopt mechanical rule resolution over manual. Rejected alternative: Architect resolves from memory (consequence: D5-style drift, missed rules). Accepted: mechanical first pass + human review.
- **DD-25.3b**: resolve_rules.py implementation: AST+glob hybrid with synonym table and --diff mode. Rejected alternative: glob-only (consequence: misses semantic triggers, ~55% catch rate for multi-subsystem plans). Accepted: hybrid catches path + import + keyword + explicit fields.
- **DD-25.4**: Split open/SKILL.md step 8: Executor prepends to LANDMINES.md only; AR/OR promotion becomes Architect Round Table action via PROMOTIONS.md queue. Rejected alternative: Executor edits AGENTS.md directly (consequence: rule-graph reasoning in execution loop, error-prone). Accepted: shift reasoning-heavy step upstream with defined latency and mid-plan behavior.
- **DD-25.5**: Move governance docs to `.agent/` subdirectory. Rejected alternative: keep at root (consequence: clutter, no role separation). Accepted: explicit ownership, Executor knows what not to read.
- **DD-25.6**: Promote OR1, OR2, OR3, OR4, OR12, OR23 to AGENTS.md universal set. Rejected alternative: keep in RULES_INDEX.md only (consequence: Executor violates during intermediate operations, no safeguard). Accepted: 10-rule universal set, still 70% reduction from 135 lines.
- **DD-25.7**: Use stable enforcement action identifiers with runtime resolver. Rejected alternative: inline script paths in plan headers (consequence: stale paths when scripts move/renamed, every plan header becomes technical debt). Accepted: indirection layer, single point of update.
- **DD-25.8**: Add /reresolve protocol for mid-plan scope expansion. Rejected alternative: ignore scope expansion (consequence: rules missed, governance drift). Accepted: explicit halt-diff-compare-continue protocol.
- **DD-25.9**: Add formal predicates (glob/imports/tag/semantic/always) to RULES_INDEX.md. Rejected alternative: natural language triggers (consequence: ambiguous, untestable, drift-prone). Accepted: testable predicates with defined inputs and coverage expectations.

---

*End of Rev2 proposal. Ready for Round Table re-check (diff-summary per GR14).*
