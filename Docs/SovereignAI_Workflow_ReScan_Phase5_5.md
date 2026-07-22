# SovereignAI Planner Workflow — Re-Scan After Phase 5.5

**Repository**: `https://github.com/AngusKingCAI/SovereignAI` (fresh clone)
**Head Commit**: `47c0cc8 Fix consistency issues after Phase 5.5 implementation`
**Re-Scan Date**: 2026-07-22
**Commits Since Last Review**: 2 (`29b08f5` Phase 5.5 implementation, `47c0cc8` consistency fixes)

---

## Executive Summary

The team shipped Phase 5.5 (Competency-based subagent validation) with 5 specialized subagent profiles, added PR22 and W10 rules, and did a "consistency fix" commit. **However, all 4 critical bugs from my last review remain unfixed**, and the Phase 5.5 implementation has 3 new holes. The "consistency fix" commit fixed count claims (PR1-PR22, W1-W10) but the line numbers in the rule indexes are still wrong — 21 of 22 PR rule line numbers point to blank lines.

**Bottom line**: The workflow is accumulating features faster than it's fixing bugs. The 4 critical blockers from my last review (any one of which is production-breaking) have now been open for 4+ commits. Phase 5.5 added 93 lines of Python that just print instructions — it doesn't actually run subagents.

---

## Critical Bugs — Status (ALL 4 UNFIXED)

### 🔴 Critical Bug #1 — Old config.json hooks block ALL writes — STILL UNFIXED

**Status**: ❌ **UNFIXED** (4th commit with this bug)

```json
// .devin/config.json still contains:
"hooks": {
    "before_file_write": "python .agent/executor/hooks/check_manifest.py --file {file_path} --plan {plan_id}",
    "after_skill_invoke": "python .agent/executor/hooks/append_trace.py --skill {skill_name} --plan {plan_id}",
    "session_end": "python .agent/executor/hooks/verify_attestation.py --plan {plan_id}"
}
```

The `.agent/` directory still doesn't exist. Per Devin spec, both hook sources run. Missing scripts exit 2 (BLOCK). **Every file write still triggers a crash that blocks the write.**

**Fix**: 5-minute job. Remove the `"hooks"` block from `.devin/config.json`.

---

### 🔴 Critical Bug #2 — PreToolUse hook exits 0 instead of 2 — STILL UNFIXED

**Status**: ❌ **UNFIXED** (4th commit with this bug)

```
$ echo '{"tool_name":"write","tool_input":{"file_path":"plans/plan-35.1-Rev1.md"...}}' | python .Planner/scripts/hooks/pretooluse_plan_write.py
PreToolUse Hook: Plan file validation failed
   - HG-7: Missing compliance lines
   - HG-9: Missing manifest component: gates
   - HG-14: Missing required section: # Plan: .+
   ...
Blocking write operation to prevent invalid plan modification
Exit code: 0   ← WRONG, should be 2
```

The hook prints "Blocking write operation" but exits 0 (allow). The "unbypassable enforcement" claim is still false.

**Fix**: Trace the control flow in `pretooluse_plan_write.py`. The `sys.exit(2)` on the failure path isn't being reached — likely the exception handler at line 62-67 is catching the wrong thing, or `main()` returns before reaching the exit.

---

### 🔴 Critical Bug #3 — database_manager.py IndentationError — STILL UNFIXED

**Status**: ❌ **UNFIXED** (5th commit with this bug)

```
$ python3 -c "import ast; ast.parse(open('.Planner/roundtable/database/database_manager.py').read())"
FAIL: unexpected indent (<unknown>, line 252)
```

Lines 252-274 and 302-313 still orphaned at 12-space indent. JSON exporter still crashes. Phase 7 handoff still broken.

**Fix**: 5-minute job. De-indent those two blocks from 12-space to 8-space.

---

### 🔴 Critical Bug #4 — gitpush `--confirm` bypasses Gate A10 — STILL UNFIXED

**Status**: ❌ **UNFIXED** (4th commit with this bug)

```python
# .devin/skills/gitpush/push.py lines 104-106, 164-166
elif arg == "--confirm":
    auto_confirm = True
# ...
if auto_confirm:
    confirmation = "yes"
    print("[INFO] Auto-confirmed via --confirm flag")
```

Any agent can run `/gitpush --confirm` and push without user confirmation. Gate A10 is bypassable.

**Fix**: 5-minute job. Remove the `--confirm` flag entirely.

---

## New Holes Introduced in Phase 5.5

### 🟡 New Hole #18 — Phase 5.5 is vapor (script doesn't run subagents)

**Location**: `.Planner/scripts/run_competency_subagents.py`

**Problem**: The script is 93 lines of Python that only prints configuration info and example invocations. It doesn't actually run any subagents. Line 76 admits: "This script provides configuration for manual subagent invocation." The Planner is expected to manually invoke `run_subagent()` tool calls based on the printed examples.

**Verification**:
```
$ python3 .Planner/scripts/run_competency_subagents.py plans/plan-35.1-Rev1.md
[INFO] This script provides configuration for manual subagent invocation
[INFO] The Planner should use run_subagent tool to invoke each subagent
[INFO] Subagent profiles are located in .devin/agents/{name}/AGENT.md

[INFO] Example invocation for Planner:
  run_subagent(profile='technical-architecture', task='Evaluate {plan_file} against COMP-001 criteria')
  ...
```

**Impact**: Phase 5.5 is purely honor-system. No script validates that subagents actually ran. An agent can post `✅ Gate PLAN-5.5 PASS: 0 findings fixed, 0 findings deferred` without ever invoking a subagent.

**Fix**: Either (a) implement actual subagent invocation via Devin CLI subprocess calls, or (b) document Phase 5.5 as a manual step the Planner must perform (don't pretend it's automated).

---

### 🟡 New Hole #19 — Model optimization documented but not implemented

**Location**: `.Planner/workflows/PLAN_WORKFLOW.md` lines 455-458 vs `.devin/agents/*/AGENT.md`

**Problem**: The workflow doc claims model optimization:
```
**Subagent Model Optimization**:
- **Opus (Critical)**: Technical Architecture, Governance Compliance
- **Claude (Mid-tier)**: Domain Relevance, Cross-Team Impact
- **SWE (Cost-effective)**: Communication Quality
```

But ALL 5 AGENT.md files use `model: swe-1.6`:
```
$ grep "^model:" .devin/agents/*/AGENT.md
.devin/agents/communication-quality/AGENT.md:model: swe-1.6
.devin/agents/cross-team-impact/AGENT.md:model: swe-1.6
.devin/agents/domain-relevance/AGENT.md:model: swe-1.6
.devin/agents/governance-compliance/AGENT.md:model: swe-1.6
.devin/agents/technical-architecture/AGENT.md:model: swe-1.6
```

PR22 §22 line 438 also claims "Use expensive models (Opus) for critical competencies" — same contradiction.

**Impact**: The cost optimization rationale is false. All 5 subagents use the same model. The "cost-effective" claim is documentation-only.

**Fix**: Either update the AGENT.md files to use the documented models (Opus for technical-architecture and governance-compliance, Claude for domain-relevance and cross-team-impact, SWE for communication-quality), or update the docs to say all subagents use SWE-1.6 and remove the model optimization claims.

---

### 🟡 New Hole #20 — W rule count: 3 different numbers in same file

**Location**: `.Planner/workflows/PLAN_WORKFLOW.md` lines 750, 782, 23

**Problem**:
- Line 750: "W1-W9: Plan workflow design rules" (9 rules)
- Line 782: "W1-W4: Workflow design rules" (4 rules)
- Line 23 (index): W1 through W10 (10 rules)

Three different counts. The consistency commit (47c0cc8) updated the PR count to "PR1-PR22" everywhere but missed two W count references.

**Fix**: Update line 750 to "W1-W10" and line 782 to "W1-W10".

---

### 🟡 New Hole #21 — Rule index line numbers: 21 of 22 wrong

**Location**: `.Planner/rules/PLANNER_RULES.md` lines 9-32 (rule index table)

**Problem**: The consistency commit updated the count to "PR1-PR22" but the line numbers in the index table are still wrong. Verified every entry:

```
Line 35 (PR1):    BLANK
Line 52 (PR2):    BLANK
Line 69 (PR3):    BLANK
Line 86 (PR4):    BLANK
Line 103 (PR5):   BLANK
Line 121 (PR6):   BLANK
Line 139 (PR7):   BLANK
Line 157 (PR8):   BLANK
Line 175 (PR9):   BLANK
Line 193 (PR10):  BLANK
Line 211 (PR11):  BLANK
Line 229 (PR12):  BLANK
Line 247 (PR13):  BLANK
Line 265 (PR14):  BLANK
Line 283 (PR15):  BLANK
Line 301 (PR16):  BLANK
Line 319 (PR17):  BLANK
Line 338 (PR18):  BLANK
Line 364 (PR19):  BLANK
Line 385 (PR20):  BLANK
Line 405 (PR21):  BLANK
Line 428 (PR22):  ✅ CORRECT — "## §22 - Competency-Based Subagent Validation (PR22)"
```

Only PR22's line number is correct. Same issue in PLAN_WORKFLOW.md W rule index — W7 says line 129 (blank), W8 says line 149 (blank), etc.

**Impact**: Agents using the index to find a rule will land on blank lines. The index is useless.

**Fix**: Either regenerate line numbers with a script, or remove the line number column from the index (the section numbers §1-§22 are sufficient for navigation).

---

## Previous Holes — Status (from last review)

### Unfixed From Last Review (all 9 moderate holes)

| # | Hole | Status |
|---|------|--------|
| 5 | Missing Stop hook | ❌ Still missing |
| 6 | SessionStart hook doesn't inject context via `hookSpecificOutput.additionalContext` | ❌ Still prints to stdout |
| 7 | PostToolUse hook is a placeholder | ❌ Still just logs |
| 8 | Phase 0 documented as un-gated but code runs HG-16 + HG-20 | ❌ Still contradictory |
| 9 | HG-16 looks in `briefs/` but briefs live in `plans/` | ❌ Still wrong directory |
| 10 | Checkpoints committed to git with Windows paths | ❌ Still in git |
| 11 | Context budget numbers inconsistent (13k vs 10k vs 3k) | ❌ Still inconsistent |
| 12 | Duplicate reviewer workflow files | ❌ Still duplicated |
| 13 | Phase 6.4 numbering bug + binary majority vs weighted consensus | ❌ Still inconsistent |
| 14 | Soft gate list in Phase 6.4 code block incomplete | ❌ Still missing sg4, sg5 |

### New Holes Summary

| # | Hole | Severity |
|---|------|----------|
| 18 | Phase 5.5 script doesn't run subagents (vapor) | Moderate |
| 19 | Model optimization documented but not implemented (all use SWE-1.6) | Moderate |
| 20 | W rule count: 3 different numbers (W1-W9, W1-W4, W1-W10) | Minor |
| 21 | Rule index line numbers: 21 of 22 wrong | Moderate |

---

## What's Good About Phase 5.5

Despite the implementation holes, the **design** of Phase 5.5 is sound:

- ✅ **5 specialized subagent profiles** created in `.devin/agents/` with proper AGENT.md frontmatter (model, max-nesting, allow list)
- ✅ **Competency mapping** is correct: COMP-001 through COMP-005 with appropriate criteria (CRIT-001 through CRIT-013)
- ✅ **PR22 rule** added with proper structure (trigger, situation, judgment, detailed rule, evidence, evolution condition)
- ✅ **W10 workflow rule** added with BP evidence citation (Anthropic 90% improvement, AWS prescriptive guidance)
- ✅ **Phase 6.0 repositioned** as "Complementary to Phase 5.5" — good architectural separation (Phase 5.5 = domain expertise, Phase 6.0 = pattern recognition)
- ✅ **Gate runner updated** to include Phase 5.5 (empty hard gate list, which is correct for subagent validation)
- ✅ **Subagent permissions** are appropriately restricted (read, grep, web_search only — no write/exec)

The design follows the Anthropic multi-agent research pattern (subagents with isolated context windows for parallel evaluation). If the implementation matched the design, this would be a genuine improvement.

---

## Cumulative Hole Count

| Review | Critical | Moderate | Minor | Total |
|--------|----------|----------|-------|-------|
| Original (07df9de) | 5 | 3 | 6 | 14 |
| Re-review (63b3f90) | 1 (regressed) | 0 | 1 (new) | 2 |
| Hole analysis (cf78384) | 4 | 9 | 3 | 16 |
| **This re-scan (47c0cc8)** | **4** | **13** | **4** | **21** |

The trend is **wrong direction** — total holes increasing because new features add new holes faster than old ones get fixed.

---

## Top 6 Priorities (fix order)

### 1. Remove old config.json hooks block (Critical #1) — 5 min
Still production-breaking. Every file write triggers a crash.

### 2. Fix PreToolUse hook exit code (Critical #2) — 30 min
Still printing "block" but allowing writes. Trace the control flow.

### 3. Fix database_manager.py indentation (Critical #3) — 5 min
Still broken after 5 commits. De-indent 2 blocks.

### 4. Remove gitpush --confirm flag (Critical #4) — 5 min
Still bypasses Gate A10.

### 5. Implement or de-document Phase 5.5 (New #18) — 1 hour
Either make `run_competency_subagents.py` actually invoke subagents via Devin CLI, or change the script to clearly state "this is a manual step — Planner must invoke subagents via run_subagent tool" and add a gate that validates the `✅ Gate PLAN-5.5 PASS` line includes findings count > 0.

### 6. Fix rule index line numbers (New #21) — 10 min
21 of 22 PR line numbers are wrong. Either regenerate with a script or remove the line number column.

---

## Pattern Observation

The team is in a **feature-shipping velocity trap**. In the time since my original review (same day, ~12 hours), they've shipped:
- 5 critical bug fixes (commit d4c6ccb) — but introduced 1 regression
- 3 moderate + 6 minor fixes (commit 63b3f90) — but introduced the regression that became Critical #3
- 8 Tier 1/2/3 improvements (commits f4d54ae through b47b3db) — impressive volume
- 7 gitpush fixes (commits 457f1b8 through cf78384) — suggests instability
- Phase 5.5 subagent validation (commits 29b08f5, 47c0cc8) — design good, implementation vapor

But the 4 critical bugs I identified 2 reviews ago are still open. The team is adding features on top of a broken foundation. Each new feature adds surface area for new holes while the old holes remain.

**Recommendation**: Pause feature development. Spend one commit fixing the 4 critical bugs (estimated 45 minutes total). Then resume feature work on a stable foundation. The current trajectory means every new feature is built on quicksand — the PreToolUse hook doesn't block, the JSON exporter doesn't run, the config.json hooks block all writes, and the gitpush skill bypasses Gate A10. Adding Phase 5.5 subagent validation on top of that doesn't help if the foundation is broken.

---

## Bottom Line

The workflow now has 22 PR rules, 10 W rules, 20 hard gates, 7 soft gates, 4 hook events, 5 subagent profiles, a checkpoint system, spec-first validation, self-check phases, weighted consensus, goal decomposition, context budgets, and a pattern analysis pipeline. That's a genuinely impressive feature set.

But it has 4 critical bugs that make the enforcement claims false, and 13 moderate holes that make the documentation misleading. The latest Phase 5.5 addition is design-only — the script doesn't run subagents, the model optimization isn't implemented, and no gate validates that Phase 5.5 actually ran.

**The workflow is architecturally sophisticated but operationally leaky.** Fix the 4 critical bugs first. Everything else is secondary.

---

*End of re-scan analysis.*
