# SovereignAI Workflow Redesign Proposal
## Version: Rev7 — Post-Round Table Rev6
## Date: 2026-07-18
## Depends on: Round Table Rev6 (7 panelists, 50 findings, 3 BLOCK, 4 CONDITIONAL, 0 PASS)
## Open questions resolved: Q-25.1 (AST+glob hybrid), Q-25.2 (deferred to phase 2 with calendar trigger), Q-25.4 (Architect-only by convention), Q-25.5 (archive AGENTS.md.pre-split), Q-25.6 (scope drift = hard STOP + post-hoc + Git commit blocking), Q-25.7 (zero matches = Architect review required), Q-25.9 (re-resolution at phase boundaries), Q-25.10 (no inheritance, critical rule auto-BLOCK), Q-25.11 (immutable contract + critical exception with auto-BLOCK), Q-25.12 (scope drift metric tracked post-migration), Q-25.14 (AST parsing: stdlib ast module), Q-25.15 (phase 2 calendar trigger + check_stale_headers.py), Q-25.16 (heuristic warning precision targets), Q-25.17 (LANDMINES_AUTO.md in-place annotation), Q-25.18 (computed complexity tier: small≤3 subs+≤10 files, medium≤6+≤50, large>6 or >50), Q-25.19 (Git commit-based compliance state replaces CI artifact dependency)
## New open questions: Q-25.20 (GPG vs SSH signing preference for compliance commits), Q-25.21 (emergency override chain: who qualifies as "senior team member"), Q-25.22 (annual taxonomy review cadence alignment with Round Table schedule)

---

## 1. Problem Statement (unchanged from Rev1-Rev6)

Current AGENTS.md is 135 lines, 7,053 bytes. The Executor re-reads it in full at every /open (OR1/S0.2). Per OpenAI's harness engineering research, a bloated always-loaded instruction file crowds out task context, causes agents to pattern-match locally instead of reasoning globally, and cannot be mechanically verified for freshness.

The current file mixes three concerns that should be separated:
1. Workflow contract — universal, applies to every plan
2. Subsystem rules — only relevant when touching specific code
3. Rationale — why a rule exists, needed for Architect decisions, not Executor execution

Additionally, the skills (open/SKILL.md, close/SKILL.md, scan/SKILL.md, verify/SKILL.md) already encode most operational rules as literal numbered steps. AGENTS.md restates them in prose, creating duplication.

---

## 2. Design Goals (unchanged from Rev1-Rev6)

| Goal | How |
|---|---|
| Minimize Executor per-session token cost | AGENTS.md -> ~40 lines; per-plan rules resolved by Architect into plan header |
| Shift reasoning cost to Architect | Architect resolves rule applicability once at plan-authoring time |
| Mechanical enforcement over prose | Rules backed by scripts don't need prose restatement |
| Progressive disclosure | Executor reads only what's relevant to this plan |
| No deletion of governance history | OR11/OR28 still hold; content moves, never deleted |
| Skills remain authoritative | open/close/scan/verify SKILL.md are the literal checklists; AGENTS.md points to them |
| Honest trust boundaries | No claims of non-bypassable in-repo enforcement; real gates are pre-commit + CI + Git commit chain |
| Permanent compliance state | Git commit-based, not CI artifact (artifacts expire: 90 days public, 400 max private) |

---

## 3. Proposed Directory Structure

SovereignAI/
├── AGENTS.md                           # NEW: ~40 lines, workflow contract + universal rules only
├── README.md                           # unchanged
├── .gitignore                          # EDITED: explicit log tracking statement
├── pyproject.toml                      # EDITED: test paths updated to .agent/executor/tests/
├── .pre-commit-config.yaml             # EDITED: script paths + validate_plan_header.py hook
│
├── .agent/                             # NEW: all governance, split by role
│   ├── architect/                      # Architect-only files (Executor never reads by convention)
│   │   ├── AI_HANDOFF.md             # moved from root, process guide
│   │   ├── PRINCIPLES.md             # moved from root, 14 principles
│   │   ├── RULES_INDEX.md            # NEW: trigger->pointer table, formal predicates + critical taxonomy
│   │   ├── RULES_REFERENCE.md        # NEW: full AR/OR bodies, Architect-only reference
│   │   ├── PROMOTIONS.md             # NEW: landmine->AR/OR promotion queue
│   │   ├── CRITICAL_TAXONOMY.md    # NEW: 20 worked examples for critical rule classification
│   │   ├── HOLIDAYS.yaml             # NEW: configured holidays for business-day calculation
│   │   └── documents/                # moved from root
│   │       ├── SovereignAI_Consolidated_Design_v1.0.md
│   │       └── ... (all existing docs)
│   │
│   └── executor/                     # Executor-owned files
│       ├── PLANS.md                  # moved from root
│       ├── LANDMINES.md              # moved from root
│       ├── LANDMINES_AUTO.md         # NEW: auto-promoted landmines (READ at /open, structured metadata)
│       ├── LANDMINES-ARCHIVE.md      # moved from root
│       ├── DEBT.md                   # moved from root
│       ├── DECISIONS.md              # moved from root
│       ├── CHANGELOG.md              # moved from root
│       ├── scripts/                  # moved from root
│       │   ├── resolve_rules.py      # NEW: AST+glob hybrid, mechanical first pass
│       │   ├── validate_plan_header.py  # NEW: 2-layer gate (pre-commit + CI)
│       │   ├── check_stale_headers.py   # NEW: weekly CI job, reports stale header count
│       │   ├── get_current_plan.py
│       │   ├── is_scan_plan.py
│       │   ├── get_scoped_tests.py
│       │   ├── verify_syntax.py
│       │   ├── verify_close.py       # EDITED: + severity classification + Git commit write
│       │   ├── check_rule_crossrefs.py
│       │   ├── .resolve_rules_ignore  # NEW: project-level ignore patterns for generated/vendor files
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
│       ├── open/SKILL.md             # EDITED: named anchors, validation POINTER (not invocation)
│       ├── close/SKILL.md            # EDITED: path references updated, + severity classification + Git commit
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

## Commit rules
See close/SKILL.md §20-21 (OR12: no --no-verify, OR23: stray-file scan).

## Plan-specific rules
Resolved per-plan by Architect into each plan's `Applicable rules:` header.
Apply exactly those rules plus the universal set above.
Full rule index: .agent/architect/RULES_INDEX.md
Full rule bodies: .agent/architect/RULES_REFERENCE.md (Architect-only, not required Executor reading)
```

### 4.2 .agent/architect/RULES_INDEX.md (unchanged from Rev6, see Rev6 §4.2)

Key: Critical rule taxonomy is objective (domain-based), not discretionary.

### 4.3 .agent/architect/CRITICAL_TAXONOMY.md (new, versioned)

```markdown
# CRITICAL_TAXONOMY.md
# Version: 1.0
# Last updated: 2026-07-18
# Review cadence: Annual (aligned with Round Table schedule)

Worked examples for critical rule classification. 20 cases.
Reference when applying taxonomy to specific plans.
Edge cases require 2-of-3 Round Table majority to override.

## Definitely CRITICAL (no override without 2-of-3 majority)

1. Database schema migration (databases/migrations/)
   -> data persistence, irreversible in production
2. Authentication flow change (web/auth/, adapters/auth/)
   -> security boundary
3. External API client with write operations (adapters/external/)
   -> security boundary, irreversible
4. File write with os.replace() pattern (sovereignai/persistence/)
   -> data persistence, atomic write requirement
5. Cache with TTL >0 that affects downstream behavior (sovereignai/cache/)
   -> data persistence (cache state is observable)
6. Privilege escalation path (sovereignai/auth/)
   -> security boundary
7. One-way data transformation with no rollback (sovereignai/transform/)
   -> irreversible action
8. WAL mode toggle for SQLite (databases/)
   -> data persistence, irreversible

## Definitely NOT CRITICAL (override available with 1-of-3 consensus)

9. In-memory computation with no side effects (sovereignai/compute/)
   -> reversible in git, no production persistence
10. Logging at INFO/DEBUG level (sovereignai/telemetry/)
    -> reversible, no production persistence
11. Read-only config file parser (sovereignai/config/)
    -> no mutation, reversible
12. Test fixture with mock data (tests/unit/)
    -> not production, reversible
13. UI rendering code with no data mutation (web/components/)
    -> reversible, no persistence
14. Documentation update (docs/)
    -> not production, reversible

## Edge Cases (require 2-of-3 Round Table majority to override)

15. Redis cache with 5-minute TTL for deduplication (sovereignai/cache/)
    -> Argument for critical: cache state affects behavior
    -> Argument against: ephemeral, rebuilt on restart
    -> DEFAULT: critical (data persistence)
16. Integration test that writes to temp database (tests/integration/)
    -> Argument for critical: touches database
    -> Argument against: test-only, not production
    -> DEFAULT: not critical (test scope)
17. Webhook receiver that logs but does not act (web/hooks/)
    -> Argument for critical: receives external data
    -> Argument against: read-only, no mutation
    -> DEFAULT: not critical (no persistence)
18. Background job scheduler that enqueues tasks (sovereignai/scheduler/)
    -> Argument for critical: affects execution order
    -> Argument against: queue is recoverable
    -> DEFAULT: critical (irreversible side effect)
19. Feature flag toggle (sovereignai/features/)
    -> Argument for critical: affects production behavior
    -> Argument against: reversible by toggle
    -> DEFAULT: not critical (reversible)
20. Health check endpoint that probes database (adapters/health/)
    -> Argument for critical: touches database
    -> Argument against: read-only, no mutation
    -> DEFAULT: not critical (read-only)

## Extension process
New examples proposed via PR with `taxonomy-extension` label.
Reviewed at next Round Table.
Version incremented on accepted changes.
```

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
Production-coupled tests: <list>  # REQUIRED if integration tests touch production paths
Scope justification: <text>      # REQUIRED if >12 rules or atomic plan
```

**Scope justification schema (evidence-based, cross-referenced):**
```
Scope justification:
  Subsystems touched: [list each subsystem]
  Cross-subsystem coupling evidence:
    - File pair 1: <pathA> and <pathB> share <data structure / interface / state>
    - File pair 2: <pathC> and <pathD> share <data structure / interface / state>
    [OR] Circular dependency chain: <pathA> -> <pathB> -> <pathC> -> <pathA>
  Why not split: [specific reason with evidence]
  Complexity tier: <small | medium | large>  # Computed by resolve_rules.py
```

validate_plan_header.py checks:
- Justification contains ≥2 file-path citations OR ≥1 circular dependency chain
- File paths exist in repository (verified by os.path.exists)
- File paths are in the plan's `WILL edit:` scope (cross-referenced)
- Complexity tier matches resolve_rules.py computed tier (small ≤3 subs + ≤10 files; medium ≤6 + ≤50; large >6 or >50)
- Architect override permitted with documented reason
- >12 rules = automatic Round Table agenda item (justification reviewed by Round Table)

**Token-budget cap (3,000 bytes, soft limit):**
- Plan header (all fields combined) should not exceed 3,000 bytes.
- Exceeding 3,000 bytes triggers Round Table pre-approval requirement.
- Async approval path: ≥2 Architects can approve via PR review within 24h.
- If disputed: sync Round Table. Default Round Table cadence: biweekly minimum.
- If approved: plan proceeds with "Round Table approved: <date>" annotation.
- If rejected: Architect must split.
- validate_plan_header.py measures total header size and flags if >3,000 bytes.

### 4.5 .devin/skills/open/SKILL.md (edited, named anchors + validation POINTER)

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

1. Read `AGENTS.md` in full. (~40 lines)

## validate-plan-header

2. The plan header must pass validation before proceeding.
   Validation is enforced at TWO layers:
   - Layer 1: Pre-commit hook (runs locally before commit)
   - Layer 2: CI gate (runs on push, blocks merge if failed)

   The Executor is responsible for ensuring validation passes.
   Run `.agent/executor/scripts/validate_plan_header.py` against this plan file.
   If validation fails: STOP. Surface error: "Plan header validation failed."
   If validation passes: log "Header validated. Proceeding."

   NOTE: This skill file contains a POINTER to validation, not an invocation.
   The Executor must actively run the validation. Skipping is possible but
   will be caught by Layer 2 (CI) before merge.

## check-landmines-auto

3. Read `.agent/executor/LANDMINES_AUTO.md`.
   Filter for relevance: match `subsystems` field against plan header subsystems.
   If matching entries found: log them as "Active landmines:" and proceed.
   If no matches: log "No active landmines for this plan."

## check-compliance-git-ref

4. Query Git for compliance status of previous plan.
   Run: `.agent/executor/scripts/check_compliance_git_ref.py --last-plan`
   This queries `refs/agent/compliance` for the most recent compliance commit.
   If last plan is NON-COMPLIANT (CRITICAL): STOP.
   Surface error: "Previous plan non-compliant (CRITICAL). Architect review required."
   If last plan is NON-COMPLIANT (MINOR): log warning, proceed.
   If no compliance ref found (first plan): log "No compliance history. Proceeding.", continue.

## read-plan-file

5. Read this plan's `Mechanical resolution:` and `Applicable rules:` header fields.
   Apply exactly those rules plus AGENTS.md's universal set.
6. Read `prompts/plan-{N}-Rev{X}.md` in full.
7. Read `CHANGELOG.md`'s most recent `## prompt-{N-1}` entry.

## pre-execution-clarification

8. Identify 1-3 ambiguities in the plan. Check for: (a) undefined terms, (b) conflicting requirements, (c) missing preconditions.
9. Ask user. Wait for answers.
10. Post answers in-session as "Plan {N} clarifications". Do not write to the execution log.
11. If no ambiguities: log "No ambiguities -- proceeding with Phase 1".

## setup

12. Add new landmines to `.agent/shared/LANDMINES.md`.
13. If LANDMINES.md changed: `git add -A && git status -s && git commit -m "docs: add landmines for prompt-{N}"`. Else: log "N/A".
14. `git add prompts/*.md` -- ensure ALL plan files in prompts/ are added to git.
15. Update `.agent/shared/PLANS.md` with new plan entry.
16. Begin Phase 1.

## scope-expansion-protocol

17. If during execution you discover you must edit files NOT in the plan's `WILL edit:` list:
    a. STOP current phase. Do NOT commit changes to unanticipated files.
    b. Run `.agent/executor/scripts/resolve_rules.py --diff` against actual git diff.
    c. Compare output to plan's `Mechanical resolution:` field.
    d. If new rules triggered: log discrepancy to execution log.
       Do NOT resume until Architect updates plan header with new Mechanical resolution: and Applicable rules:.
    e. Resume phase only after header updated.

## incremental-verification

18-22. [unchanged -- same as current open/SKILL.md steps 11-15]
```

### 4.6 .devin/skills/close/SKILL.md (edited)

```markdown
## post-hoc-rule-resolution-check

20. Run `.agent/executor/scripts/resolve_rules.py --diff` against actual git diff.
    Compare to plan header's `Mechanical resolution:` field.
    Classify discrepancies:
    - CRITICAL: edited production files outside resolved scope → write Git compliance commit: NON-COMPLIANT (CRITICAL)
    - MINOR: edited test files, docs, config outside scope → write Git compliance commit: NON-COMPLIANT (MINOR)
    - TRIVIAL: comments, whitespace → write Git compliance commit: COMPLIANT

    Git compliance commit format (signed, pushed to refs/agent/compliance):
    {
      "plan": "plan-{N}",
      "status": "COMPLIANT | NON-COMPLIANT",
      "severity": "CRITICAL | MINOR | TRIVIAL",
      "discrepancies": [...],
      "timestamp": "ISO-8601",
      "verified_by": "verify_close.py",
      "commit_hash": "<sha256 of this commit>"
    }

    The commit is signed (GPG or SSH) and pushed to `refs/agent/compliance`.
    This ref is permanent (Git history never expires) and tamper-evident (signed).
    Query via: `git log refs/agent/compliance --format='%H %s' -1`

21. If CRITICAL non-compliance: log to execution log. Architect reviews at next Round Table.
    If MINOR non-compliance: log to execution log. Next plan can proceed with warning.

## pre-commit

22. Verify .pre-commit-config.yaml hooks run successfully after migration.
```

### 4.7 .agent/executor/scripts/check_compliance_git_ref.py (new)

```python
#!/usr/bin/env python3
# check_compliance_git_ref.py -- Query Git for compliance status of previous plan.
#
# Queries `refs/agent/compliance` for the most recent compliance commit.
# Returns: COMPLIANT, NON-COMPLIANT (CRITICAL), NON-COMPLIANT (MINOR), or NOT_FOUND.
#
# Usage:
#     python check_compliance_git_ref.py --last-plan
#     Exit 0 = COMPLIANT or NOT_FOUND (proceed)
#     Exit 1 = NON-COMPLIANT (CRITICAL) -- STOP
#     Exit 2 = NON-COMPLIANT (MINOR) -- warning, proceed
#
# No external CI dependency. Works offline. Works with any Git host.
# Compliance state is permanent (Git history) and tamper-evident (signed commits).
```

### 4.8 .agent/executor/scripts/validate_plan_header.py (new, honest 2-layer gate)

```python
#!/usr/bin/env python3
# validate_plan_header.py -- Pre-open validation gate (2 layers: pre-commit + CI).
#
# Layer 1: Pre-commit hook (local, client-side)
# Layer 2: CI gate (remote, server-side, blocks merge)
#
# This script is invoked by the Executor as a skill step (not a subprocess).
# The Executor CAN skip it. Skipping is caught by Layer 2 (CI) before merge.
# Honest framing: two independent layers, both must fail for invalid headers to reach main.
#
# Validates:
#   1. Plan file has required fields: Applicable rules, Mechanical resolution
#   2. All rule IDs in Applicable rules exist in RULES_INDEX.md
#   3. Mechanical resolution is valid JSON
#   4. Side effects anticipated field is present (yes/no)
#   5. If side effects anticipated == yes: New entry points and Durable backends non-empty
#   6. If side effects anticipated == no: those fields empty or 'N/A'
#   7. Scope justification present with >=2 file-path citations OR >=1 circular dependency chain (if >12 rules)
#   8. File paths in justification exist in repository
#   9. File paths in justification are in the plan's WILL edit: scope
#   10. Complexity tier matches resolve_rules.py computed tier (small <=3 subs + <=10 files; medium <=6 + <=50; large >6 or >50)
#   11. Architect override permitted with documented reason
#   12. Total header size <= 3,000 bytes (soft limit, flags for Round Table if exceeded)
#
# Usage:
#     python validate_plan_header.py prompts/plan-{N}-Rev{n}.md
#     Exit 0 = valid, proceed with /open
#     Exit 1 = invalid, STOP
```

### 4.9 .agent/executor/scripts/.resolve_rules_ignore (new)

```
# .resolve_rules_ignore -- Patterns for files to skip in resolve_rules.py
# These files are annotated as IGNORED (config), not BLOCKED on parse error.
# One pattern per line. Supports glob syntax: ** recursion, ! negation, {a,b} alternation.
# Max pattern length: 200 chars. Max total patterns: 20.
# New patterns require PR with `ignore-pattern` label, reviewed at next Round Table.

# Generated files
proto/gen/**
*_pb2.py
*_generated.py

# Vendor/third-party
vendor/**
third_party/**

# Foreign language bindings
*.pyi
*.c
*.h

# Build artifacts
build/**
dist/**
```

### 4.10 .agent/executor/LANDMINES_AUTO.md (new format -- structured metadata, in-place annotation)

```markdown
# LANDMINES_AUTO.md

Auto-promoted landmines. Executor reads at /open (relevance-filtered by structured metadata).
Entries are annotated in-place, never removed. OR28 preserved.

## Format
Each entry is a YAML frontmatter block followed by description:

```yaml
---
plan: "plan-25"
phase: "Phase 1"
discovered_at: "2026-07-18T10:00:00Z"
subsystems: ["sovereignai", "web"]
keywords: ["capability", "routing"]
status: PENDING  # PENDING | REVIEWED | ARCHIVED | PROMOTED | REJECTED
status_changed_at: ""
round_table: ""
---
Description of the landmine...
```

## Rules
- Executor logs candidate within 1 hour of discovery.
- Architect reviews at next Round Table or via `/review-promotions`.
- Max age in LANDMINES.md: 3 plans.
- After 3 plans with no Architect action: auto-promote to LANDMINES_AUTO.md with status: PENDING.
- LANDMINES_AUTO.md entries never removed. Status annotation changes only.
- Architect must process at least 5 items per Round Table.
- CI escalation: if >80 PENDING entries, warning. If >100 PENDING for 2 consecutive weeks, CI fails builds.
- 2-week grace period between warning and failure.
- Round Table review note required for any mass status change >5 entries.
```

### 4.11 .agent/architect/AI_HANDOFF.md (moved + edited)

- All path references updated
- Plan Template updated with Mechanical resolution:, Applicable rules:, REQUIRED semantic fields, Scope justification schema (evidence-based, cross-referenced)
- S0.2 updated: "Read AGENTS.md in full" (~40 lines)
- S0.5 updated: Harness check references RULES_INDEX.md formal predicates
- GR19 added: Harness check in every plan
- GR20 added: AGENTS.md split threshold at 200 lines (safety rail, now moot at 40)
- Added: "Plan headers are immutable contracts. Governance changes apply prospectively, not retroactively. Critical rules trigger auto-BLOCK (plan cannot reach /close until acknowledged)."
- Added: "No plan-to-plan inheritance. Each plan resolved independently. Dependency plans are NOT transitive for rule resolution."
- Added: "Plan header soft limit: 3,000 bytes. Exceeding requires Round Table pre-approval (async: >=2 Architects within 24h, or sync Round Table)."
- Added: "Non-compliance severity classification: CRITICAL blocks next plan (Git compliance commit), MINOR logs warning, TRIVIAL no action."
- Added: "Phase 2 trigger: 6 months after migration (calendar-only). check_stale_headers.py runs weekly."
- Added: "Critical rule notification: 5 business days to acknowledge. Business days exclude weekends and configured holidays (see .agent/architect/HOLIDAYS.yaml). Unanswered = auto-BLOCK. 2 unanswered in 30 days = mandatory Round Table."
- Added: "Emergency override: after 5 business days + 48h grace, any two senior team members can jointly override with logged risk acceptance. Both signatures in execution log. Round Table reviews at next session."
- Added: "Complexity tier: computed by resolve_rules.py. small <=3 subsystems + <=10 files; medium <=6 + <=50; large >6 or >50. Architect can override with documented reason."
- Added: "Edge case override: 2-of-3 Round Table majority (not 3-of-3). Dissenting opinion documented in DECISIONS.md. Unanimous disagreement escalates to project lead."

### 4.12 .pre-commit-config.yaml (edited)

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
      - id: check-ignore-patterns
        name: Audit .resolve_rules_ignore patterns
        entry: python .agent/executor/scripts/check_ignore_patterns.py
        language: system
        files: ^\.agent/executor/scripts/\.resolve_rules_ignore$
        pass_filenames: true
        stages: [push]
```

### 4.13 .agent/executor/scripts/check_ignore_patterns.py (new)

```python
#!/usr/bin/env python3
# check_ignore_patterns.py -- Audit .resolve_rules_ignore patterns.
#
# Validates:
#   - Pattern count <= 20
#   - No pattern exceeds 200 chars
#   - All patterns use valid glob syntax
#   - New patterns have corresponding PR with `ignore-pattern` label
#   - Patterns reviewed at last Round Table (checked via git log)
#
# CI fails if audit fails.
# Usage:
#     python check_ignore_patterns.py
#     Exit 0 = audit passed
#     Exit 1 = audit failed
```

### 4.14 .agent/executor/scripts/verify_close.py (edited)

```python
#!/usr/bin/env python3
# verify_close.py -- Verify plan close + write Git compliance commit.
#
# Steps:
#   1. Run resolve_rules.py --diff against actual git diff
#   2. Compare to plan header's Mechanical resolution field
#   3. Classify discrepancies: CRITICAL / MINOR / TRIVIAL
#   4. Create signed Git commit to refs/agent/compliance with compliance JSON
#   5. Push compliance ref
#
# Compliance commit is signed (GPG or SSH) for tamper-evidence.
# Git ref is permanent (Git history never expires).
# Works offline. Works with any Git host.
#
# Usage:
#     python verify_close.py prompts/plan-{N}-Rev{n}.md
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
| AGENTS.md | ~40 | ~1,200 | Yes |
| Plan header fields | variable | <=3,000 | Yes (part of plan file) |
| open/SKILL.md | ~55 | ~2,500 | Yes |
| LANDMINES_AUTO.md (filtered) | ~5-10 | ~200-500 | Yes (structured metadata filter) |
| Total per /open | ~100-125 | ~3,900-6,200 | -- |

Savings: ~54-70 lines, ~2,900-4,900 bytes per /open.
- Trivial plan (3 rules): ~75% reduction
- Normal plan (6 rules): ~55% reduction
- Complex plan (12 rules): ~35% reduction
- Soft limit: 3,000 bytes header = predictable cost with override path

### Cost shift to Architect (per plan)

| Action | Lines | Bytes | When |
|---|---|---|---|
| Read RULES_INDEX.md | ~60 | ~2,500 | Once per plan |
| Read RULES_REFERENCE.md (sections) | ~20 | ~1,000 | Only for matched rules |
| Read CRITICAL_TAXONOMY.md | ~30 | ~1,500 | When edge case arises |
| Run resolve_rules.py | -- | -- | Once per plan |
| Review coverage report + sign off | -- | -- | Once per plan |
| Write header fields | variable | <=3,000 | Once per plan |
| Total per plan | ~110-150 | ~4,000-6,000 | At authoring time |

Honest assessment: Architect cost is non-trivial but justified by Executor savings.
- 50 plans/year x ~5,000 bytes = ~250KB/year Architect overhead
- 50 plans/year x ~4,000 bytes saved per /open x average 3 /open per plan = ~600KB/year Executor savings
- Net savings: ~350KB/year

---

## 6. Migration Path (Revised)

1. Pre-migration audit: `grep -rE '(scripts/|prompts/|CHANGELOG|LANDMINES|PLANS|AGENTS|tests/)' --include='*' --exclude-dir=.git --exclude-dir=__pycache__ --exclude-dir=node_modules .` -- manually review every hit.
2. Create new directory structure: .agent/architect/ and .agent/executor/
3. Move files: git mv, no content changes
4. Create RULES_REFERENCE.md: copy AGENTS_EXTENDED.md verbatim
5. Create RULES_INDEX.md: formal predicates + objective critical taxonomy
6. Create CRITICAL_TAXONOMY.md: 20 worked examples, versioned, annual review
7. Create HOLIDAYS.yaml: configured holidays for business-day calculation
8. Rewrite AGENTS.md: ~40 lines, 9 universal rules (OR12/OR23 moved to close/SKILL.md)
9. Edit skill files: path updates, named anchors, validation POINTER (not invocation)
10. Create resolve_rules.py: AST+glob hybrid, synonym table, --diff mode, error handling, caching, warnings, .resolve_rules_ignore support, computed complexity tier
11. Create validate_plan_header.py: 2-layer gate (pre-commit + CI), evidence-based justification check, WILL edit: scope cross-reference, complexity tier verification
12. Create check_stale_headers.py: weekly CI job
13. Create check_compliance_git_ref.py: Git ref query, no CI dependency
14. Create check_ignore_patterns.py: audit .resolve_rules_ignore patterns
15. Create PROMOTIONS.md: auto-promote to LANDMINES_AUTO.md with structured metadata
16. Create LANDMINES_AUTO.md: empty file, READ at /open, structured metadata format
17. Create .resolve_rules_ignore: project-level ignore patterns (max 20, max 200 chars each)
18. Update verify_close.py: severity classification + Git compliance commit (signed, pushed to refs/agent/compliance)
19. Update pyproject.toml: test paths to .agent/executor/tests/
20. Update .pre-commit-config.yaml: script paths + validate_plan_header.py hook + check_ignore_patterns.py hook
21. Update .gitignore: explicit log tracking statement
22. Update AI_HANDOFF.md: path updates, plan template with new fields, immutability contract, critical rule auto-BLOCK, token budget soft limit, non-compliance severity, phase 2 calendar trigger, complexity tier, emergency override chain, edge case 2-of-3 majority
23. Update plan headers: retroactively add fields to existing draft plans (22-24)
24. Update PLANS.md: new baseline: AGENTS.md 40 lines, test count unchanged
25. Add --dry-run to ar_checks: verify paths before executing
26. Run scan: verify no broken references, cross-reference check passes
27. Run pre-commit locally: verify hooks pass after path updates
28. Run full test suite: verify pytest discovers tests at new path
29. Commit: "prompt-25: Workflow redesign -- token cost redistribution, AGENTS.md minimization"
30. Create archive/LOG_ANNOTATION.md: mapping old references to new paths. Do NOT prepend to historical logs.
31. Smoke test: run /open on draft plan, confirm (a) AGENTS.md <= 40 lines, (b) validate_plan_header.py passes at all layers, (c) cross-reference check passes, (d) at least one rule from each RULES_INDEX.md section fires on synthetic test plan, (e) >3,000 bytes flagged for Round Table, (f) non-compliance severity classification works, (g) check_stale_headers.py reports metric, (h) Git compliance commit is created and queryable, (i) LANDMINES_AUTO.md structured metadata filter works, (j) .resolve_rules_ignore pattern audit passes

---

## 7. Risks and Mitigations (Revised)

| Risk | Mitigation | Credibility |
|---|---|---|
| Architect misses a rule during resolution | resolve_rules.py exhaustive coverage report + Architect sign-off; scan step 2c catches post-hoc misses; validate_plan_header.py gate (2 layers) | Credible -- three independent checks |
| Executor doesn't know a rule exists | Mechanical resolution: field mandatory; validate_plan_header.py gate rejects malformed headers; post-hoc check at close catches misses; Git compliance commit blocking for CRITICAL | Credible -- gate + detective + blocking |
| RULES_INDEX.md trigger drift | Formal predicates (glob/imports/tag) are testable; drift detected by resolver test suite | Credible -- testable predicates |
| Skills reference old paths | Pre-migration broad grep audit; post-migration pre-commit + test suite + smoke test | Credible -- exhaustive audit |
| Governance history lost | git mv only; no deletion; archive/LOG_ANNOTATION.md maps old->new; AGENTS.md.pre-split archived; LANDMINES_AUTO.md in-place annotation | Credible -- git history + annotations + no removal |
| Plan header stale enforcement actions | Inline paths (not stable identifiers) for phase 1. Path drift handled by pre-migration audit. Phase 2 trigger: 6 months (calendar-only). check_stale_headers.py tracks metric. | Credible -- bounded deferral + tracking |
| Scope expansion mid-plan | /reresolve protocol: hard STOP, no commit to unanticipated files. Post-hoc check at close catches misses. Non-compliance severity classification. | Credible -- STOP + detective + proportional blocking |
| Round Table objects to structural change | Quantitative token analysis (35-75% range), reversible migration path (git mv), explicit rollback procedure | Credible -- reversible + quantitative |
| PROMOTIONS.md becomes graveyard | Auto-promote to LANDMINES_AUTO.md (structured metadata, never removed). CI fails builds if >100 PENDING for 2 weeks. Staged warning at 80. | Credible -- bounded growth + automatic consequence |
| semantic() predicate ambiguity | Removed entirely. Replaced with REQUIRED plan header fields + validate_plan_header.py verification + heuristic WARNINGS (narrowed, clustered, per-file-pattern suppression). | Credible -- verification + controlled warnings |
| imports() over-fires on TYPE_CHECKING | Documented limitation. Flagged as WARNING in coverage report. Architect confirms exclusion. Production-file-only filtering. | Credible -- documented + human review |
| AST parsing too slow for large plans | Caching (mtime-based). Performance ceiling (<=30s). --fast mode for >200 files (Architect sign-off + explicit flag in report). Import-graph ceiling: 10s, fallback to path-based. | Credible -- engineering solutions |
| validate_plan_header.py bypassed | Honest 2-layer gate: pre-commit (client-side) + CI (server-side). Both must fail for invalid headers to reach main. Executor CAN skip pre-commit; CI catches it. | Credible -- genuinely independent layers |
| Immutable header + no inheritance | Critical rule exception: auto-BLOCK (plan cannot /close until acknowledged). Objective domain-based taxonomy + worked examples. Human decision, auditable. Emergency override chain after timeout + grace. | Credible -- exception with real blocking + recovery |
| LANDMINES_AUTO.md bloat | Structured metadata (never removed). CI fails builds if >100 PENDING for 2 weeks. Staged warning at 80. 2-week grace. Round Table review note for mass changes. | Credible -- bounded growth + auto-enforcement |
| Phase 2 deferred features never happen | Calendar-only trigger (6 months). check_stale_headers.py runs weekly (CI cron + local fallback). Metric visible in DECISIONS.md. | Credible -- accountable deferral + tracking |
| Named anchor drift | CI check for anchor references. Anchor registry in skill file headers. Auto-discovery of skill files (recursive glob). | Credible -- mechanical validation |
| Scope justification rubber stamp | Evidence-based justification (file-path citations cross-referenced against WILL edit: scope, not keywords). Round Table pre-approval for >3,000 bytes. Async approval path (>=2 Architects, 24h). | Credible -- structural gate |
| Heuristic warning fatigue | Narrowed scope (production files + integration tests with production imports). Clustered warnings. Per-file-pattern suppression (not global), 90-day expiry. Max 20 patterns. Pattern audit in CI. | Credible -- signal-to-noise control |
| Non-compliance self-deadlock | Severity classification (CRITICAL/MINOR/TRIVIAL). CRITICAL blocks via Git compliance commit (permanent, tamper-evident). MINOR logs warning. Continuous calibration (30-day human verification, then conditional audit). | Credible -- proportional + recoverable + no self-bypass |
| Critical rule auto-BLOCK creates deadlock | 5 business days to acknowledge. Business days exclude weekends and configured holidays. Handoff to backup Architect required for absences. Emergency override: 2 senior members jointly override after timeout + 48h grace. Round Table reviews. | Credible -- bounded delay with escalation + recovery |
| Git compliance ref requires signed commits | Documented assumption. If team does not use signed commits, compliance commits are still tamper-evident via hash chain but not cryptographically attributable. Acceptable trade-off documented. | Credible -- documented assumption |
| Git compliance ref requires push access to refs/agent/compliance | Configured via Git hooks or CI. If Executor lacks push access, CI pushes on their behalf. Documented setup procedure. | Credible -- configuration solution |
| Complexity tier computed incorrectly | resolve_rules.py computes tier. validate_plan_header.py verifies match. Architect can override with documented reason. Post-migration calibration adjusts thresholds. | Credible -- verification + override + calibration |
| Emergency override chain abused | Requires 2 senior members, both signatures in execution log, Round Table review at next session. Abuse is auditable and reviewable. | Credible -- multi-party + audit trail |
| Edge case 2-of-3 majority creates inconsistency | Dissenting opinion documented in DECISIONS.md. Unanimous disagreement escalates to project lead. Inconsistency is visible, not hidden. | Credible -- transparency + escalation |
| Annual taxonomy review never happens | Aligned with Round Table schedule. Version field in CRITICAL_TAXONOMY.md. CI check for version age >1 year. | Credible -- calendar trigger + CI enforcement |

---

## 8. Open Questions (Revised -- 22 total)

- Q-25.1: RESOLVED -- AST+glob hybrid. Glob for path-based, AST for import-based, keyword synonym table for tag-based.
- Q-25.2: DEFERRED to phase 2 -- Stable identifiers with runtime resolver. Phase 1 uses inline paths. Trigger: 6 months (calendar-only).
- Q-25.3: Should AGENTS.md include one-line skill file pointers? OPEN -- adds ~3 lines. Trade-off: discoverability vs. brevity.
- Q-25.4: RESOLVED -- Architect-only, enforced by convention (OR-LIT). No filesystem permissions.
- Q-25.5: RESOLVED -- Yes, archive/AGENTS.md.pre-split. Git history sufficient but discoverability improved by frozen copy.
- Q-25.6: RESOLVED -- Scope drift = /reresolve protocol (hard STOP) + post-hoc check at close + Git compliance commit severity classification.
- Q-25.7: RESOLVED -- Zero matches = Architect review required, not "no rules apply." Plan cannot proceed without Architect sign-off on coverage report.
- Q-25.8: DEFERRED to phase 2 -- Rule deprecation. Phase 1: append-only, no deprecation.
- Q-25.9: RESOLVED -- Re-resolution at phase boundaries only. Mid-plan scope expansion uses /reresolve protocol.
- Q-25.10: RESOLVED -- No plan-to-plan inheritance. Each plan resolved independently. Dependency plans are NOT transitive. Critical rules trigger auto-BLOCK (plan cannot /close until acknowledged).
- Q-25.11: RESOLVED -- Plan header is immutable contract. Governance changes apply prospectively, not retroactively. Critical rules are the exception (auto-BLOCK with 5 business day timeout + escalation + emergency override).
- Q-25.12: How often does scope drift occur in practice? OPEN -- metric to track post-migration.
- Q-25.13: DEFERRED to phase 2 -- Runtime resolver implementation. Trigger: 6 months (calendar-only).
- Q-25.14: RESOLVED -- AST parsing uses stdlib `ast` module. No external dependencies.
- Q-25.15: Phase 2 timeline and owner. RESOLVED -- Calendar trigger: 6 months. Owner: Architect. check_stale_headers.py tracks metric.
- Q-25.16: Heuristic warning precision targets. OPEN -- define target false-positive rate (<20%) and review cadence.
- Q-25.17: LANDMINES_AUTO.md optimal cap size. RESOLVED -- In-place annotation with structured metadata. CI enforces via build failure on bloat (80 warn, 100 fail, 2-week grace).
- Q-25.18: Complexity tier calibration. RESOLVED -- Computed by resolve_rules.py: small <=3 subs + <=10 files; medium <=6 + <=50; large >6 or >50. Architect can override with documented reason. Post-migration calibration adjusts thresholds.
- Q-25.19: CI artifact provider portability. RESOLVED -- Replaced with Git commit-based compliance state. No CI dependency. Works with any Git host. Works offline.
- Q-25.20: GPG vs SSH signing preference for compliance commits. OPEN -- team preference. Both supported. Documented in setup guide.
- Q-25.21: Who qualifies as "senior team member" for emergency override? OPEN -- project-specific. Suggested: core maintainers with merge rights. Documented in AI_HANDOFF.md.
- Q-25.22: Annual taxonomy review cadence alignment with Round Table schedule. OPEN -- suggest biweekly Round Table = annual taxonomy review at Q4 Round Table.

---

## 9. Decisions Proposed (Revised -- 18 total)

- DD-25.1: Move AR1-30 and OR1-30 from AGENTS.md to .agent/architect/RULES_REFERENCE.md. Rejected alternative: keep in AGENTS.md (consequence: 135->200+ lines, context crowding, rule dropout). Accepted: separate files, progressive disclosure.
- DD-25.2: Add Mechanical resolution: and Applicable rules: to plan header template. Rejected alternative: Executor reads full RULES_REFERENCE.md when ambiguous (consequence: ambiguity judgment costs tokens every session). Accepted: Architect resolves once, Executor reads resolved list + coverage report.
- DD-25.3a: Adopt mechanical rule resolution over manual. Rejected alternative: Architect resolves from memory (consequence: drift, missed rules). Accepted: mechanical first pass + human review.
- DD-25.3b: resolve_rules.py implementation: AST+glob hybrid with synonym table and --diff mode. Rejected alternative: glob-only (consequence: misses import-based triggers, ~55% catch rate for multi-subsystem plans). Accepted: hybrid catches path + import + keyword.
- DD-25.4: Split open/SKILL.md step 8: Executor prepends to LANDMINES.md only; AR/OR promotion becomes Architect Round Table action via PROMOTIONS.md queue. Rejected alternative: Executor edits AGENTS.md directly (consequence: rule-graph reasoning in execution loop, error-prone). Accepted: shift reasoning-heavy step upstream with auto-promote fallback.
- DD-25.5: Move governance docs to .agent/ subdirectory. Rejected alternative: keep at root (consequence: clutter, no role separation). Accepted: explicit ownership, Executor knows what not to read.
- DD-25.6: Promote OR1, OR2, OR3, OR4 to AGENTS.md universal set. Move OR12, OR23 to close/SKILL.md. Rejected alternative: keep all in AGENTS.md (consequence: 135 lines, bloat) OR keep OR12/OR23 in AGENTS.md (consequence: per-open bloat for plans that never commit). Accepted: 9-rule universal set + pointer to close/SKILL.md.
- DD-25.7: DEFERRED to phase 2 -- Stable enforcement action identifiers with runtime resolver. Rejected alternative for phase 1: inline paths (consequence: path drift when scripts move). Accepted for phase 1: inline paths with pre-migration audit. Phase 2 trigger: 6 months (calendar-only).
- DD-25.8: Add /reresolve protocol for mid-plan scope expansion. Rejected alternative: ignore scope expansion (consequence: rules missed, governance drift). Accepted: hard STOP + post-hoc check + Git compliance commit severity classification.
- DD-25.9: Add formal predicates (glob/imports/tag/always) to RULES_INDEX.md. Rejected alternative: natural language triggers (consequence: ambiguous, untestable, drift-prone). Accepted: testable predicates with defined inputs and coverage expectations.
- DD-25.10: Remove semantic() predicate. Replaced with REQUIRED plan header fields + validate_plan_header.py verification + heuristic WARNINGS (narrowed, clustered, per-file-pattern suppression). Rejected alternative: keep semantic() as formal predicate (consequence: not actually formal, relies on inference, untestable). Accepted: Architect declares semantic properties explicitly, tool verifies presence.
- DD-25.11: Remove 7-entry cap. Replace with 3,000-byte soft cap + evidence-based Scope justification for >12 rules. Rejected alternative: keep cap with escalation (consequence: silent rule dropping, perverse incentives) OR 2,000-byte hard cap (consequence: artificial splitting). Accepted: soft cap with Round Table override, evidence-based justification.
- DD-25.12: Auto-promote to LANDMINES_AUTO.md (structured metadata, in-place annotation, never removed). Rejected alternative: mandatory promotion or rejection DD (consequence: graveyard when Architect unavailable) OR auto-promote to LANDMINES.md (consequence: bloat erases savings) OR auto-archive (consequence: OR28 violation). Accepted: structured metadata with CI-enforced bloat control.
- DD-25.13: Plan header is immutable contract + critical rule exception. Rejected alternative: dynamic header updates (consequence: mid-plan rule changes create stealth variance) OR no exception (consequence: critical rules silently bypassed). Accepted: snapshot contract with auto-BLOCK exception (plan cannot /close until acknowledged) + emergency override chain.
- DD-25.14: No plan-to-plan inheritance + critical rule auto-BLOCK. Rejected alternative: automatic inheritance from dependency plans (consequence: implicit transitive rules, fragile dependency tracking). Accepted: explicit re-resolution per plan, critical rules trigger auto-BLOCK.
- DD-25.15: Phase 2 calendar trigger + check_stale_headers.py. Rejected alternative: indefinite deferral (consequence: deferred features never happen). Accepted: 6-month calendar trigger, weekly metric tracking, defined acceptance criteria.
- DD-25.16: Critical rule taxonomy is objective (domain-based) + worked examples + 2-of-3 majority override. Rejected alternative: Architect discretion for critical designation (consequence: political capture, inconsistent application). Accepted: data persistence, security boundaries, irreversible actions = automatic critical, with 20 worked examples and 2-of-3 override consensus.
- DD-25.17: Replace CI artifact with Git commit-based compliance state (signed commits to refs/agent/compliance). Rejected alternative: keep CI artifact (consequence: artifacts expire after 90 days public / 400 days private max, making long-term governance impossible). Accepted: Git commits are permanent, tamper-evident, queryable offline, no external dependency.

---

End of Rev7 proposal. Ready for Round Table re-check (diff-summary per GR14).
