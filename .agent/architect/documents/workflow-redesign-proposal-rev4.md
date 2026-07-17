# SovereignAI Workflow Redesign Proposal
## Version: Rev4 — Post-Round Table Rev3
## Date: 2026-07-18
## Depends on: Round Table Rev3 (7 panelists, 60 findings, 1 BLOCK, 6 CONDITIONAL, 0 pass)
## Open questions resolved: Q-25.1 (AST+glob hybrid), Q-25.2 (deferred to phase 2 with trigger), Q-25.4 (Architect-only by convention), Q-25.5 (archive AGENTS.md.pre-split), Q-25.6 (scope drift = hard STOP + post-hoc + blocking dependency), Q-25.7 (zero matches = Architect review required), Q-25.9 (re-resolution at phase boundaries), Q-25.10 (no inheritance, critical rule exception), Q-25.11 (immutable contract + critical exception), Q-25.12 (scope drift metric tracked post-migration), Q-25.14 (AST parsing: stdlib ast module)
## New open questions: Q-25.13 (runtime resolver — deferred to phase 2 with trigger), Q-25.15 (phase 2 timeline and owner)

---

## 1. Problem Statement (unchanged from Rev1-Rev3)

Current AGENTS.md is 135 lines, 7,053 bytes. The Executor re-reads it in full at every /open (OR1/S0.2). Per OpenAI's harness engineering research, a bloated always-loaded instruction file crowds out task context, causes agents to pattern-match locally instead of reasoning globally, and cannot be mechanically verified for freshness.

The current file mixes three concerns that should be separated:
1. Workflow contract — universal, applies to every plan
2. Subsystem rules — only relevant when touching specific code
3. Rationale — why a rule exists, needed for Architect decisions, not Executor execution

Additionally, the skills (open/SKILL.md, close/SKILL.md, scan/SKILL.md, verify/SKILL.md) already encode most operational rules as literal numbered steps. AGENTS.md restates them in prose, creating duplication.

---

## 2. Design Goals (unchanged from Rev1-Rev3)

| Goal | How |
|---|---|
| Minimize Executor per-session token cost | AGENTS.md -> ~45 lines; per-plan rules resolved by Architect into plan header |
| Shift reasoning cost to Architect | Architect resolves rule applicability once at plan-authoring time |
| Mechanical enforcement over prose | Rules backed by scripts don't need prose restatement |
| Progressive disclosure | Executor reads only what's relevant to this plan |
| No deletion of governance history | OR11/OR28 still hold; content moves, never deleted |
| Skills remain authoritative | open/close/scan/verify SKILL.md are the literal checklists; AGENTS.md points to them |

---

## 3. Proposed Directory Structure

SovereignAI/
├── AGENTS.md                           # NEW: ~45 lines, workflow contract + universal rules only
├── README.md                           # unchanged
├── .gitignore                          # EDITED: explicit log tracking statement
├── pyproject.toml                      # EDITED: test paths updated to .agent/executor/tests/
├── .pre-commit-config.yaml             # EDITED: script paths + validate_plan_header.py hook
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
│       ├── LANDMINES_AUTO.md         # NEW: auto-promoted landmines (NOT read at /open)
│       ├── LANDMINES-ARCHIVE.md      # moved from root
│       ├── DEBT.md                   # moved from root
│       ├── DECISIONS.md              # moved from root
│       ├── CHANGELOG.md              # moved from root
│       ├── scripts/                  # moved from root
│       │   ├── resolve_rules.py      # NEW: AST+glob hybrid, mechanical first pass
│       │   ├── validate_plan_header.py  # NEW: independent gate (3 layers)
│       │   ├── get_current_plan.py
│       │   ├── is_scan_plan.py
│       │   ├── get_scoped_tests.py
│       │   ├── verify_syntax.py
│       │   ├── verify_close.py       # EDITED: + non-compliance blocking
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
│       │   ├── plan-{N}-Rev{n}.md    # header gains fields (see 4.4)
│       │   └── completed/
│       │
│       └── logs/                     # moved from root, tracked (append-only per OR28)
│           ├── execution-log-prompt-{N}.md
│           └── screenshots/
│
├── .devin/                             # unchanged role, skill files edited
│   └── skills/
│       ├── open/SKILL.md             # EDITED: named anchors, no half-steps, + /reresolve protocol
│       ├── close/SKILL.md            # EDITED: path references updated, + post-hoc check + blocking
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
└── archive/                            # LANDMINES-ARCHIVE.md + AGENTS.md.pre-split + LOG_ANNOTATION.md

---

## 4. File Contents

### 4.1 AGENTS.md (new, ~45 lines)

```markdown
# AGENTS.md

Authority: .agent/architect/PRINCIPLES.md
Ambiguous -> .agent/shared/LANDMINES.md

## Workflow contract
Every plan: /open -> execute -> /close, per .devin/skills/{open,close,scan,verify}/SKILL.md.
Follow steps literally, in order, no skipping. Exit!=0 = STOP.
Do not explain, justify, or offer workarounds -- STOP is the only valid response.

## Universal rules (apply to every plan, no exceptions)
AR4.   No hardcoded component names. All discovery through CapabilityGraph.
AR11.  No docstrings. Self-documenting names.
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
Apply exactly those rules plus the universal set above.
Full rule index: .agent/architect/RULES_INDEX.md
Full rule bodies: .agent/architect/RULES_REFERENCE.md (Architect-only, not required Executor reading)
```

### 4.2 .agent/architect/RULES_INDEX.md (new, formal predicates + critical flag)

```markdown
# RULES_INDEX.md

Trigger-condition -> rule pointer table. One row per rule.
Architect uses this to resolve `Applicable rules:` for each plan.
Mechanical first pass: .agent/executor/scripts/resolve_rules.py

## Predicate definitions

- `glob(path)`: plan's `WILL edit:` globs include files matching `path`
- `imports(module)`: AST analysis of `WILL edit:` files detects `import module` or `from module import`
  - Direct static imports only: top-level, conditional (if/try), TYPE_CHECKING blocks
  - Dynamic imports (importlib, __import__, getattr) are NOT caught -- require explicit tag
  - imports() may over-fire on TYPE_CHECKING imports -- flagged as WARNING, Architect confirms exclusion
- `tag(keyword)`: plan's declared tags include `keyword` or synonym
- `always`: rule applies to every plan (already in AGENTS.md universal set, not in index)

## Critical rules
Rules marked `critical: true` trigger notification for ALL in-flight plans.
Definition: rules addressing security vulnerabilities, data loss, or irreversible damage.
Current critical rules: [none yet -- added via DD process]

## Conditional rules

| Rule  | Critical | Predicate                                    | Enforcement action                              | Full text ->                      |
|-------|----------|---------------------------------------------|------------------------------------------------|----------------------------------|
| AR1   |          | glob("sovereignai/orchestrator/**") OR glob("sovereignai/workers/**") | verify chain: Owner->Orchestrator->Manager->Worker | RULES_REFERENCE.md secAR1          |
| AR2   |          | glob("sovereignai/librarian/**") OR glob("sovereignai/memory/**") OR imports("librarian") | verify no direct backend queries               | RULES_REFERENCE.md secAR2          |
| AR3   |          | glob("adapters/**") OR imports("adapters") OR tag("model", "inference", "llm") | verify inference routes through adapters       | RULES_REFERENCE.md secAR3          |
| AR5   |          | glob("adapters/**") AND tag("mcp", "server", "wrapper") | verify adapter wrapper before use              | RULES_REFERENCE.md secAR5          |
| AR6   |          | glob("adapters/**") AND (new file OR tag("health", "check")) | verify health_check() + graceful error           | RULES_REFERENCE.md secAR6          |
| AR7   |          | glob("tui/panels/**") OR glob("app/web/**") OR imports("tui.panels") | run scripts/ar_checks/check_ar7_allowlist.py   | RULES_REFERENCE.md secAR7          |
| AR8   |          | glob("sovereignai/**") AND tag("trace", "log", "emit") | verify local SSD only, no external telemetry   | RULES_REFERENCE.md secAR8          |
| AR9   |          | glob("skills/**") AND tag("author", "manifest", "dag") | verify manifest+code+DAG output                | RULES_REFERENCE.md secAR9          |
| AR10  |          | glob("sovereignai/**") AND tag("external", "copy", "local") | verify local copy before use                   | RULES_REFERENCE.md secAR10         |
| AR12  |          | glob("web/**") OR imports("fastapi") OR imports("web") | verify separate process, public API surface    | RULES_REFERENCE.md secAR12         |
| AR13  |          | glob("web/**") AND (tag("auth", "sse", "cookie") OR imports("auth")) | verify HTTP session cookie, no query params    | RULES_REFERENCE.md secAR13         |
| AR14  |          | glob("web/schemas.py") OR glob("web/**/schemas.py") | verify DTOs in web/schemas.py                  | RULES_REFERENCE.md secAR14         |
| AR15  |          | glob("adapters/**") AND (new file OR tag("health", "check")) | verify health_check() returns typed dataclass  | RULES_REFERENCE.md secAR15         |
| AR16  |          | glob("sovereignai/**") AND (new class OR tag("capability", "conformance")) | verify <100ms, cached, fail-closed/open          | RULES_REFERENCE.md secAR16         |
| AR17  |          | glob("sovereignai/**") AND (changes public method signature OR tag("api", "contract")) | verify contract tests pass                     | RULES_REFERENCE.md secAR17         |
| AR18  |          | always (property-based tests run every commit) | property-based tests run (CI gate)             | RULES_REFERENCE.md secAR18         |
| AR19  |          | glob("sovereignai/**") AND (tag("memory", "backend", "swap") OR imports("memory_backend")) | verify CapabilityGraph pluggability            | RULES_REFERENCE.md secAR19         |
| AR20  |          | glob("sovereignai/**") AND (tag("crash", "recovery", "shutdown", "marker") OR tag("shutdown logic")) | verify .shutdown_marker check                  | RULES_REFERENCE.md secAR20         |
| AR21  | true     | glob("databases/**") OR glob("sovereignai/**") AND (tag("sqlite", "json", "atomic", "wal") OR tag("durable backend")) | verify atomic writes, WAL, os.replace()        | RULES_REFERENCE.md secAR21         |
| AR22  |          | glob("sovereignai/**") AND (tag("side effects") OR tag("trace", "emit", "log", "write", "network")) | verify trace event emission                    | RULES_REFERENCE.md secAR22         |
| AR23  |          | glob("sovereignai/**") AND (new entry point OR tag("correlation ID", "request ID", "trace ID", "continuity")) | verify context var propagation                 | RULES_REFERENCE.md secAR23         |
| AR24  |          | glob("web/**") AND tag("logs", "panel", "sse", "trace") | verify /api/traces SSE consumption only        | RULES_REFERENCE.md secAR24         |
| AR25  |          | glob("databases/**") OR glob("services/**") | verify root-level packages, no nesting         | RULES_REFERENCE.md secAR25         |
| AR26  |          | glob("services/**") OR glob("databases/**") AND (new class OR tag("provider", "service")) | verify health_check() dataclass, lazy init     | RULES_REFERENCE.md secAR26         |
| AR27  |          | glob("web/**") AND (tag("models", "hardware", "panel") OR imports("models_panel") OR imports("hardware_panel")) | verify capability API consumption only         | RULES_REFERENCE.md secAR27         |
| AR28  |          | glob("adapters/**") AND (new file OR tag("manifest", "routing", "priority")) | verify routing_priority int, ascending         | RULES_REFERENCE.md secAR28         |
| AR29  |          | glob("sovereignai/**") AND tag("diagnostic", "harness", "test", "stage") | verify load->use->unload per stage               | RULES_REFERENCE.md secAR29         |
| AR30  |          | glob("tui/panels/**") OR imports("tui.panels") | verify real backend state, no placeholders     | RULES_REFERENCE.md secAR30         |
| OR5   |          | glob("CHANGELOG.md") OR glob("LANDMINES.md") | prepend-only, never append or edit existing    | SKILL.md close step 12 (OR-GOV)    |
| OR6   |          | always (plan header field)                  | pre-declare scope: WILL edit / will NOT edit   | plan header (universal)            |
| OR7   |          | glob("sovereignai/**") AND (imports("datetime") OR tag("datetime", "timezone")) | never mix naive/aware, use timezone.utc          | SKILL.md verify step 2             |
| OR8   |          | glob("sovereignai/**") AND tag("temp", "tmp", "temporary") | dedicated temp dir, delete after consume       | SKILL.md open step 8             |
| OR9   |          | glob("sovereignai/**") AND new file         | corresponding test file with passing tests     | SKILL.md close step 1            |
| OR10  |          | glob("tests/**") AND tag("delete", "remove") | STOP, scope deviation                          | SKILL.md close step 1            |
| OR11  |          | glob("tests/**") AND tag("failing", "fail")   | fix root cause, never re-run without fix       | SKILL.md close step 1            |
| OR13  |          | tag("hook", "exclude", "bypass")              | STOP, out-of-scope                             | SKILL.md close step 19           |
| OR14  |          | glob("txt/requirements.txt") OR tag("dependency", "requirements") | runtime deps in txt/requirements.txt only      | SKILL.md close step 5            |
| OR15  |          | glob("scripts/ar_checks/**") OR tag("ar_check", "script") | STOP, never edit to make failure pass          | SKILL.md close step 8            |
| OR16  |          | glob("sovereignai/**") AND (glob("web/**") OR glob("tui/**")) AND tag("backend", "ui") | backend ships with UI surface                  | plan header (conditional)        |
| OR17  |          | tag("incomplete", "defer", "debt")            | defer per item, log in exec log + DEBT         | SKILL.md close step 14           |
| OR18  |          | tag("already done", "done", "complete")       | require logged command + exit code             | plan header (conditional)        |
| OR19  |          | glob("tests/**") OR tag("test", "mypy", "static", "analysis") | no "pre-existing" exemption, fix or DEBT       | SKILL.md close step 1            |
| OR20  |          | glob("tests/**") AND tag("skip", "skipped", "todo") | carry # TODO(prompt-N), >=3 consecutive = fix   | SKILL.md close step 1            |
| OR21  |          | glob("web/**") OR glob("tui/**") AND tag("html", "css", "js", "frontend") | syntax validation before tests                 | SKILL.md open step 12-15         |
| OR22  |          | glob("tests/**") AND new file                 | real-shape fixtures, no MagicMock for domain   | SKILL.md close step 1            |
| OR24  |          | tag("exception", "user authorized", "scope deviation") | needs target plan documentation                | SKILL.md close step 14           |
| OR25  |          | always (pyproject.toml)                       | 30s timeout via pytest-timeout                 | pyproject.toml (discoverable)    |
| OR26  |          | always (skill workflow)                       | follow systematically, no skipping             | SKILL.md open step 1             |
| OR27  |          | glob("prompts/**") OR tag("prompt", "plan file") | never delete prompt files                      | SKILL.md close step 18           |
| OR28  |          | always (OR-GOV)                               | never delete content, prepend-only             | OR-GOV (universal)               |
| OR29  |          | glob("tests/**") AND NOT tag("scan")          | pytest scoped to changed files + dependents    | SKILL.md close step 1            |
| OR30  |          | always (OR-LIT)                               | follow literally, restrictive terms = exact    | OR-LIT (universal)               |
```

Key changes from Rev3:
- Added `critical` column to RULES_INDEX.md. AR21 marked as critical (durable backend = data loss risk).
- TYPE_CHECKING imports flagged as WARNING in coverage report.
- Dynamic imports flagged as WARNING in coverage report.

### 4.3 .agent/architect/RULES_REFERENCE.md (new)

Identical to current AGENTS_EXTENDED.md content, relocated. No rewording. Append-only.

### 4.4 Plan Header Template (edit in AI_HANDOFF.md)

```markdown
Depends on: <prerequisite plan numbers>
Vision principles: <which of 14 this satisfies/affects>
Open questions resolved: <which Q1-Q34, or "none">
Mechanical resolution: <output from resolve_rules.py, embedded verbatim, signed by Architect>
Applicable rules: <AR/OR IDs + inline script paths, resolved by Architect>
  e.g. "AR7: run .agent/executor/scripts/ar_checks/check_ar7_allowlist.py"
  e.g. "AR12: verify separate process, public API surface"
  e.g. "OR16: backend ships with UI surface -- defer if explicitly scoped out"
Side effects anticipated: <yes/no>  # REQUIRED field
New entry points: <list>           # REQUIRED if yes to side effects
Durable backends: <list>          # REQUIRED if yes to side effects
Scope justification: <text>      # REQUIRED if >12 rules or atomic plan
```

Key changes from Rev3:
- Added `Scope justification:` field. Required if >12 rules OR if plan is atomic (inherently indivisible).
- validate_plan_header.py enforces: >12 rules without justification = rejection.

### 4.5 .devin/skills/open/SKILL.md (edited, named anchors)

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

## read-agents

1. Read `AGENTS.md` in full. (~45 lines)

## validate-plan-header

2. Run `.agent/executor/scripts/validate_plan_header.py` against this plan file.
   This script runs at THREE layers: (1) pre-commit hook, (2) CI gate, (3) harness validation.
   If ANY layer fails, /open cannot proceed.
   If validation fails (missing fields, malformed Mechanical resolution, empty Applicable rules,
   >12 rules without Scope justification, invalid semantic field values):
   STOP. Surface error: "Plan header validation failed -- Architect review required."
   Do not proceed until validation passes.

## read-plan-file

3. Read this plan's `Mechanical resolution:` and `Applicable rules:` header fields.
   Apply exactly those rules plus AGENTS.md's universal set.
4. Read `prompts/plan-{N}-Rev{X}.md` in full.
5. Read `CHANGELOG.md`'s most recent `## prompt-{N-1}` entry.

## pre-execution-clarification

6. Identify 1-3 ambiguities in the plan. Check for: (a) undefined terms, (b) conflicting requirements, (c) missing preconditions.
7. Ask user. Wait for answers.
8. Post answers in-session as "Plan {N} clarifications". Do not write to the execution log.
9. If no ambiguities: log "No ambiguities -- proceeding with Phase 1".

## setup

10. Add new landmines to `.agent/shared/LANDMINES.md`.
11. If LANDMINES.md changed: `git add -A && git status -s && git commit -m "docs: add landmines for prompt-{N}"`. Else: log "N/A".
12. `git add prompts/*.md` -- ensure ALL plan files in prompts/ are added to git.
13. Update `.agent/executor/PLANS.md` with new plan entry.
14. Begin Phase 1.

## scope-expansion-protocol

15. If during execution you discover you must edit files NOT in the plan's `WILL edit:` list:
    a. STOP current phase. Do NOT commit changes to unanticipated files.
    b. Run `.agent/executor/scripts/resolve_rules.py --diff` against actual git diff.
    c. Compare output to plan's `Mechanical resolution:` field.
    d. If new rules triggered: log discrepancy to execution log.
       Do NOT resume until Architect updates plan header with new Mechanical resolution: and Applicable rules:.
    e. Resume phase only after header updated.

## incremental-verification

16-20. [unchanged -- same as current open/SKILL.md steps 11-15]
```

### 4.6 .devin/skills/close/SKILL.md (edited)

Path references updated. Two additions:

```markdown
## post-hoc-rule-resolution-check

20. Run `.agent/executor/scripts/resolve_rules.py --diff` against actual git diff.
    Compare to plan header's `Mechanical resolution:` field.
    If discrepancy found (files touched outside resolved scope without logged /reresolve entry):
    - Plan marked as NON-COMPLIANT.
    - Log non-compliance to execution log.
    - BLOCK next plan from starting until Architect reviews and resolves.
    - Architect reviews at next Round Table.

## pre-commit

21. Verify .pre-commit-config.yaml hooks run successfully after migration.
```

### 4.7 .devin/skills/scan/SKILL.md (edited)

Path references updated. Steps 2a/2b/2c:

```markdown
## scan-landmines-and-rule-index

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
# triggers, keyword synonym table for tag-based triggers.
#
# Usage:
#     python resolve_rules.py --plan prompts/plan-25-rev1.md
#     python resolve_rules.py --files "sovereignai/orchestrator/*.py,tui/panels/*.py"
#     python resolve_rules.py --tags "fastapi,ui,tui"
#     python resolve_rules.py --diff  # reads actual git diff, not declared scope (close-time only)
#
# Error handling:
#     - SyntaxError: log warning, skip file, include as "parse_error" in coverage report
#     - Unsupported file type (not .py): skip, include as "skipped_non_python"
#     - Generated code: skip files matching .gitignore or with "# GENERATED" header
#     - Dynamic import: NOT caught -- flagged as "dynamic_import_detected" WARNING
#     - TYPE_CHECKING import: flagged as "type_only_import" WARNING, Architect confirms exclusion
#
# Performance:
#     - AST parse results cached per file (mtime-based)
#     - Must complete in <=30s for 95% of plans
#     - For plans >200 files: use --fast mode (glob-only, no AST)
#       --fast mode requires Architect sign-off: "I accept that import-based triggers may be missed."
#
# Output: JSON with exhaustive coverage report:
#   {
#     "mechanical": [{"rule_id": "AR7", "predicate": "glob(tui/panels/**)", "status": "fired"}],
#     "not_fired": [{"rule_id": "AR1", "predicate": "glob(sovereignai/orchestrator/**)", "status": "not_fired", "reason": "no matching files"}],
#     "predicate_error": [{"rule_id": "AR3", "file": "broken.py", "status": "predicate_error", "reason": "SyntaxError at line 42"}],
#     "input_missing": [{"rule_id": "AR22", "status": "input_missing", "reason": "Side effects anticipated field absent"}],
#     "warnings": [{"rule_id": "AR2", "file": "models.py", "status": "type_only_import", "suggestion": "Confirm TYPE_CHECKING import is not runtime-relevant"}],
#     "coverage_report": "Evaluated 34 triggers. 12 fired. 19 not_fired. 1 predicate_error. 2 input_missing. 1 warning."
#   }
#
# Architect must sign off on coverage report, not just output list.
```

### 4.10 .agent/executor/scripts/validate_plan_header.py (new, 3-layer gate)

```python
#!/usr/bin/env python3
# validate_plan_header.py -- Independent pre-open validation gate (3 layers).
#
# Layer 1: Pre-commit hook (local)
# Layer 2: CI gate (remote)
# Layer 3: Harness validation (framework-level)
#
# If ANY layer fails, /open cannot proceed.
#
# Validates:
#   1. Plan file has required fields: Applicable rules, Mechanical resolution
#   2. All rule IDs in Applicable rules exist in RULES_INDEX.md
#   3. Mechanical resolution is valid JSON
#   4. Side effects anticipated field is present (yes/no)
#   5. If side effects anticipated == yes: New entry points and Durable backends fields present and non-empty
#   6. If side effects anticipated == no: New entry points and Durable backends fields empty or 'N/A'
#   7. Applicable rules count <= 12 OR Scope justification field is present and non-empty
#   8. Semantic field values are valid Python identifiers (if present)
#
# Does NOT validate (deferred to phase 2):
#   - All fired rules are represented (requires runtime resolver)
#   - Stable identifier resolution (deferred)
#   - Semantic correctness of enforcement actions
#
# Usage:
#     python validate_plan_header.py prompts/plan-{N}-Rev{n}.md
#     Exit 0 = valid, proceed with /open
#     Exit 1 = invalid, STOP
```

### 4.11 .agent/architect/PROMOTIONS.md (new)

```markdown
# PROMOTIONS.md

Landmine -> AR/OR promotion queue. Executor-discovered candidates.

## Format
| Plan | Phase | Landmine | Rationale | Status | Round Table |
|------|-------|----------|-----------|--------|-------------|

## Rules
- Executor logs candidate within 1 hour of discovery.
- Architect reviews at next Round Table or via `/review-promotions`.
- Max age in LANDMINES.md: 3 plans.
- After 3 plans with no Architect action: **auto-promote to LANDMINES_AUTO.md** (permanent record, OR28).
  - LANDMINES_AUTO.md is NOT read at /open. It is reviewed by Architect at Round Table.
  - Promoted items move to LANDMINES.md. Rejected items move to LANDMINES-ARCHIVE.md.
  - This prevents LANDMINES.md bloat while preserving the record.
- Rejected candidates: move to LANDMINES-ARCHIVE.md with rejection reason.
```

### 4.12 .agent/architect/AI_HANDOFF.md (moved + edited)

- All path references updated
- Plan Template updated with Mechanical resolution:, Applicable rules:, REQUIRED semantic fields, Scope justification
- S0.2 updated: "Read AGENTS.md in full" (~45 lines)
- S0.5 updated: Harness check references RULES_INDEX.md formal predicates
- GR19 added: Harness check in every plan
- GR20 added: AGENTS.md split threshold at 200 lines (safety rail, now moot at 45)
- Added: "Plan headers are immutable contracts. Governance changes apply prospectively, not retroactively. Critical rules (marked in RULES_INDEX.md) trigger notification for in-flight plans, not automatic modification."
- Added: "No plan-to-plan inheritance. Each plan resolved independently. Dependency plans are NOT transitive for rule resolution."
- Added: "Atomic plans (inherently indivisible operations) may exceed 12 rules. Justification required in Scope justification: field."
- Added: "Non-compliant plans (post-hoc check failure) block next plan from starting until Architect resolves."

### 4.13 .pre-commit-config.yaml (edited)

```yaml
repos:
  - repo: local
    hooks:
      - id: validate-plan-header
        name: Validate plan header
        entry: python .agent/executor/scripts/validate_plan_header.py
        language: system
        files: ^prompts/plan-.*\.md$
        pass_filenames: true
        stages: [commit]
```

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
| Total per /open | 179 | 9,061 | -- |

### Proposed state (per Executor /open)

| File | Lines | Bytes | Read every /open? |
|---|---|---|---|
| AGENTS.md | ~45 | ~1,500 | Yes |
| Plan header fields | variable | variable | Yes (part of plan file) |
| open/SKILL.md | ~50 | ~2,300 | Yes |
| Total per /open | ~95-120 | ~3,800-5,500 | -- |

Savings: ~59-75 lines, ~3,500-5,200 bytes per /open.
- Trivial plan (3 rules): ~75% reduction
- Normal plan (6 rules): ~60% reduction
- Complex plan (12 rules): ~40% reduction
- No cap -- all rules included, cost proportional to plan complexity

### Cost shift to Architect (per plan)

| Action | Lines | Bytes | When |
|---|---|---|---|
| Read RULES_INDEX.md | ~60 | ~2,500 | Once per plan |
| Read RULES_REFERENCE.md (sections) | ~20 | ~1,000 | Only for matched rules |
| Run resolve_rules.py | -- | -- | Once per plan |
| Review coverage report + sign off | -- | -- | Once per plan |
| Write header fields | variable | variable | Once per plan |
| Total per plan | ~80-120 | ~3,500-5,500 | At authoring time |

Honest assessment: Architect cost is non-trivial but justified by Executor savings.
- 50 plans/year x ~4,500 bytes = ~225KB/year Architect overhead
- 50 plans/year x ~4,500 bytes saved per /open x average 3 /open per plan = ~675KB/year Executor savings
- Net savings: ~450KB/year

---

## 6. Migration Path (Revised)

1. Pre-migration audit: `grep -rE '(scripts/|prompts/|CHANGELOG|LANDMINES|PLANS|AGENTS|tests/)' --include='*' --exclude-dir=.git --exclude-dir=__pycache__ --exclude-dir=node_modules .` -- manually review every hit.
2. Create new directory structure: .agent/architect/ and .agent/executor/
3. Move files: git mv, no content changes
4. Create RULES_REFERENCE.md: copy AGENTS_EXTENDED.md verbatim
5. Create RULES_INDEX.md: formal predicates from analysis above + critical flag
6. Rewrite AGENTS.md: ~45 lines, 11 universal rules
7. Edit skill files: path updates, named anchors, /reresolve protocol, post-hoc check + blocking
8. Create resolve_rules.py: AST+glob hybrid, synonym table, --diff mode, error handling, caching, warnings
9. Create validate_plan_header.py: 3-layer gate (pre-commit + CI + harness)
10. Create PROMOTIONS.md: auto-promote to LANDMINES_AUTO.md
11. Create LANDMINES_AUTO.md: empty file, NOT read at /open
12. Update pyproject.toml: test paths to .agent/executor/tests/
13. Update .pre-commit-config.yaml: script paths + validate_plan_header.py hook
14. Update .gitignore: explicit log tracking statement
15. Update AI_HANDOFF.md: path updates, plan template with new fields, immutability contract, critical rule exception, atomic plan exception, non-compliance blocking
16. Update plan headers: retroactively add fields to existing draft plans (22-24)
17. Update PLANS.md: new baseline: AGENTS.md 45 lines, test count unchanged
18. Add --dry-run to ar_checks: verify paths before executing
19. Run scan: verify no broken references, cross-reference check passes
20. Run pre-commit locally: verify hooks pass after path updates
21. Run full test suite: verify pytest discovers tests at new path
22. Commit: "prompt-25: Workflow redesign -- token cost redistribution, AGENTS.md minimization"
23. Create archive/LOG_ANNOTATION.md: mapping old references to new paths. Do NOT prepend to historical logs.
24. Smoke test: run /open on draft plan, confirm (a) AGENTS.md <= 45 lines, (b) validate_plan_header.py passes at all 3 layers, (c) cross-reference check passes, (d) at least one rule from each RULES_INDEX.md section fires on synthetic test plan, (e) >12 rules without justification rejected, (f) non-compliance blocks next plan

---

## 7. Risks and Mitigations (Revised)

| Risk | Mitigation | Credibility |
|---|---|---|
| Architect misses a rule during resolution | resolve_rules.py exhaustive coverage report + Architect sign-off; scan step 2c catches post-hoc misses; validate_plan_header.py gate (3 layers) | Credible -- four independent checks |
| Executor doesn't know a rule exists | Mechanical resolution: field mandatory; validate_plan_header.py gate rejects malformed headers; post-hoc check at close catches misses; non-compliance blocks next plan | Credible -- gate + detective + blocking |
| RULES_INDEX.md trigger drift | Formal predicates (glob/imports/tag) are testable; drift detected by resolver test suite | Credible -- testable predicates |
| Skills reference old paths | Pre-migration broad grep audit; post-migration pre-commit + test suite + smoke test | Credible -- exhaustive audit |
| Governance history lost | git mv only; no deletion; archive/LOG_ANNOTATION.md maps old->new; AGENTS.md.pre-split archived | Credible -- git history + annotations |
| Plan header stale enforcement actions | Inline paths (not stable identifiers) for phase 1. Path drift handled by pre-migration audit. Phase 2 trigger: 6 months or 15 stale headers. | Credible -- bounded deferral |
| Scope expansion mid-plan | /reresolve protocol: hard STOP, no commit to unanticipated files. Post-hoc check at close catches misses. Non-compliance blocks next plan. | Credible -- STOP + detective + blocking |
| Round Table objects to structural change | Quantitative token analysis (40-75% range), reversible migration path (git mv), explicit rollback procedure | Credible -- reversible + quantitative |
| PROMOTIONS.md becomes graveyard | Auto-promote to LANDMINES_AUTO.md (not LANDMINES.md). No blocking. Reviewed at Round Table. | Credible -- no always-read bloat |
| semantic() predicate ambiguity | Removed entirely. Replaced with REQUIRED plan header fields + validate_plan_header.py verification + heuristic WARNINGS. | Credible -- verification + warnings |
| imports() over-fires on TYPE_CHECKING | Documented limitation. Flagged as WARNING in coverage report. Architect confirms exclusion. | Credible -- documented + human review |
| AST parsing too slow for large plans | Caching (mtime-based). Performance ceiling (<=30s). --fast mode for >200 files (Architect sign-off). | Credible -- engineering solutions |
| validate_plan_header.py bypassed | 3-layer enforcement: pre-commit hook + CI gate + harness validation. Executor cannot bypass all three. | Credible -- defense in depth |
| Immutable header + no inheritance | Critical rule exception: notification (not auto-modification) for in-flight plans. Human decision, auditable. | Credible -- exception with human gate |
| LANDMINES.md bloat from auto-promote | Auto-promote to LANDMINES_AUTO.md (not LANDMINES.md). LANDMINES_AUTO.md not read at /open. | Credible -- separation of concerns |
| Phase 2 deferred features never happen | Trigger: 6 months or 15 stale headers. Owner: Architect. Acceptance criteria defined. | Credible -- accountable deferral |
| Named anchor drift | CI check for anchor references. Anchor registry in skill file headers. | Credible -- mechanical validation |

---

## 8. Open Questions (Revised -- 15 total)

- Q-25.1: RESOLVED -- AST+glob hybrid. Glob for path-based, AST for import-based, keyword synonym table for tag-based.
- Q-25.2: DEFERRED to phase 2 -- Stable identifiers with runtime resolver. Phase 1 uses inline paths.
- Q-25.3: Should AGENTS.md include one-line skill file pointers? OPEN -- adds ~5 lines. Trade-off: discoverability vs. brevity.
- Q-25.4: RESOLVED -- Architect-only, enforced by convention (OR-LIT). No filesystem permissions.
- Q-25.5: RESOLVED -- Yes, archive/AGENTS.md.pre-split. Git history sufficient but discoverability improved by frozen copy.
- Q-25.6: RESOLVED -- Scope drift = /reresolve protocol (hard STOP) + post-hoc check at close + non-compliance blocks next plan.
- Q-25.7: RESOLVED -- Zero matches = Architect review required, not "no rules apply." Plan cannot proceed without Architect sign-off on coverage report.
- Q-25.8: DEFERRED to phase 2 -- Rule deprecation. Phase 1: append-only, no deprecation.
- Q-25.9: RESOLVED -- Re-resolution at phase boundaries only. Mid-plan scope expansion uses /reresolve protocol.
- Q-25.10: RESOLVED -- No plan-to-plan inheritance. Each plan resolved independently. Dependency plans are NOT transitive. Critical rules trigger notification for in-flight plans.
- Q-25.11: RESOLVED -- Plan header is immutable contract. Governance changes apply prospectively, not retroactively. Critical rules are the exception (notification, not auto-modification).
- Q-25.12: How often does scope drift occur in practice? OPEN -- metric to track post-migration.
- Q-25.13: DEFERRED to phase 2 -- Runtime resolver implementation. Trigger: 6 months or 15 stale headers.
- Q-25.14: RESOLVED -- AST parsing uses stdlib `ast` module. No external dependencies.
- Q-25.15: Phase 2 timeline and owner. RESOLVED -- Trigger: 6 months or 15 stale headers. Owner: Architect. Acceptance: runtime resolver + rule deprecation + semantic validation + versioned headers.

---

## 9. Decisions Proposed (Revised -- 15 total)

- DD-25.1: Move AR1-30 and OR1-30 from AGENTS.md to .agent/architect/RULES_REFERENCE.md. Rejected alternative: keep in AGENTS.md (consequence: 135->200+ lines, context crowding, rule dropout). Accepted: separate files, progressive disclosure.
- DD-25.2: Add Mechanical resolution: and Applicable rules: to plan header template. Rejected alternative: Executor reads full RULES_REFERENCE.md when ambiguous (consequence: ambiguity judgment costs tokens every session). Accepted: Architect resolves once, Executor reads resolved list + coverage report.
- DD-25.3a: Adopt mechanical rule resolution over manual. Rejected alternative: Architect resolves from memory (consequence: drift, missed rules). Accepted: mechanical first pass + human review.
- DD-25.3b: resolve_rules.py implementation: AST+glob hybrid with synonym table and --diff mode. Rejected alternative: glob-only (consequence: misses import-based triggers, ~55% catch rate for multi-subsystem plans). Accepted: hybrid catches path + import + keyword.
- DD-25.4: Split open/SKILL.md step 8: Executor prepends to LANDMINES.md only; AR/OR promotion becomes Architect Round Table action via PROMOTIONS.md queue. Rejected alternative: Executor edits AGENTS.md directly (consequence: rule-graph reasoning in execution loop, error-prone). Accepted: shift reasoning-heavy step upstream with auto-promote fallback.
- DD-25.5: Move governance docs to .agent/ subdirectory. Rejected alternative: keep at root (consequence: clutter, no role separation). Accepted: explicit ownership, Executor knows what not to read.
- DD-25.6: Promote OR1, OR2, OR3, OR4, OR12, OR23 to AGENTS.md universal set. Rejected alternative: keep in RULES_INDEX.md only (consequence: Executor violates during intermediate operations, no safeguard). Accepted: 11-rule universal set, still 67% reduction from 135 lines.
- DD-25.7: DEFERRED to phase 2 -- Stable enforcement action identifiers with runtime resolver. Rejected alternative for phase 1: inline script paths (consequence: path drift when scripts move). Accepted for phase 1: inline paths with pre-migration audit. Phase 2 trigger: 6 months or 15 stale headers.
- DD-25.8: Add /reresolve protocol for mid-plan scope expansion. Rejected alternative: ignore scope expansion (consequence: rules missed, governance drift). Accepted: hard STOP + post-hoc check + non-compliance blocks next plan.
- DD-25.9: Add formal predicates (glob/imports/tag/always) to RULES_INDEX.md. Rejected alternative: natural language triggers (consequence: ambiguous, untestable, drift-prone). Accepted: testable predicates with defined inputs and coverage expectations.
- DD-25.10: Remove semantic() predicate. Replaced with REQUIRED plan header fields + validate_plan_header.py verification + heuristic WARNINGS. Rejected alternative: keep semantic() as formal predicate (consequence: not actually formal, relies on inference, untestable). Accepted: Architect declares semantic properties explicitly, tool verifies presence.
- DD-25.11: Remove 7-entry cap on Applicable rules:. Replace with >12 rules enforcement + Scope justification field. Rejected alternative: keep cap with escalation (consequence: silent rule dropping, perverse incentives). Accepted: no cap, mechanical enforcement at 12 rules, atomic plan exception.
- DD-25.12: Auto-promote to LANDMINES_AUTO.md (not LANDMINES.md) after 3 plans. Rejected alternative: mandatory promotion or rejection DD (consequence: graveyard when Architect unavailable) OR auto-promote to LANDMINES.md (consequence: bloat erases savings). Accepted: separate file, not read at /open, reviewed at Round Table.
- DD-25.13: Plan header is immutable contract + critical rule exception. Rejected alternative: dynamic header updates (consequence: mid-plan rule changes create stealth variance) OR no exception (consequence: critical rules silently bypassed). Accepted: snapshot contract with notification exception for critical rules.
- DD-25.14: No plan-to-plan inheritance + critical rule notification. Rejected alternative: automatic inheritance from dependency plans (consequence: implicit transitive rules, fragile dependency tracking). Accepted: explicit re-resolution per plan, critical rules trigger notification.
- DD-25.15: Phase 2 trigger and owner. Rejected alternative: indefinite deferral (consequence: deferred features never happen). Accepted: 6-month or 15-stale-header trigger, Architect owner, defined acceptance criteria.

---

End of Rev4 proposal. Ready for Round Table re-check (diff-summary per GR14).
