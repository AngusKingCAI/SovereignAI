# LANDMINES.md — SovereignAI Failure Patterns

Append-only. Selected landmines (L1–L9, L11, L12, L17) inherited from sovereign-ai (predecessor project) — these are the entries referenced in `AGENTS.md`'s landmine-to-rule table. L10, L13–L16, L18–L23 were not graduated to rules in SovereignAI and are not carried forward. New landmines for SovereignAI start at L24.

Entries below are placeholder records for the inherited landmines referenced in `AGENTS.md`'s landmine-to-rule table. Each entry records the inherited trigger pattern and impact; SovereignAI-specific triggers will be appended as they occur. Per AGENTS.md: "Keep entries concise — trigger and impact only. No narrative."

---

## L1 — replace_all corrupts adjacent lines
**Trigger**: Inherited from sovereign-ai predecessor. Specific SovereignAI trigger TBD.
**Impact**: `AGENTS.md` or other structured markdown becomes structurally invalid. Requires manual restoration from git.
**Graduated to**: OR5.

## L2 — Parallel scan tools corrupt output streams
**Trigger**: Inherited from sovereign-ai predecessor. Specific SovereignAI trigger TBD.
**Impact**: Output streams from pytest/ruff/mypy/bandit/pip-audit/vulture interleave when run in parallel, producing unreadable output. Requires re-running all tools sequentially.
**Graduated to**: OR3.

## L3 — PowerShell -replace corrupts structured markdown
**Trigger**: Inherited from sovereign-ai predecessor. Specific SovereignAI trigger TBD (SovereignAI uses Git Bash per OR1, so this should not recur — retained for diagnostic context).
**Impact**: Markdown table formatting destroyed when edited with PowerShell `Set-Content` + `-replace`.
**Graduated to**: OR7.

## L4 — Temp files left in repo root get committed
**Trigger**: Inherited from sovereign-ai predecessor. Specific SovereignAI trigger TBD.
**Impact**: Temp file committed to repo. Requires follow-up commit to remove.
**Graduated to**: OR13, OR21.

## L5 — Vulture flags unused test fixtures incorrectly
**Trigger**: Inherited from sovereign-ai predecessor. Specific SovereignAI trigger TBD.
**Impact**: False positive. Parameter was required by pytest's parametrize decorator.
**Graduated to**: OR19.

## L6 — Naive/aware datetime mixing
**Trigger**: Inherited from sovereign-ai predecessor. Specific SovereignAI trigger TBD.
**Impact**: Type error when comparing `datetime.utcnow()` with `datetime.now(timezone.utc)`. Mypy flagged the mismatch.
**Graduated to**: OR20.

## L7 — Stale baselines propagate through plans
**Trigger**: Inherited from sovereign-ai predecessor. Specific SovereignAI trigger TBD.
**Impact**: Baseline drift. Subsequent plan starts with wrong expected test count, causing false STOP.
**Graduated to**: OR17.

## L8 — Scope drift: editing files outside declared scope
**Trigger**: Inherited from sovereign-ai predecessor. Specific SovereignAI trigger TBD.
**Impact**: Unplanned changes in commit. Difficult to trace which plan produced which change.
**Graduated to**: OR16, OR22.

## L9 — Interface changes break existing tests during type remediation
**Trigger**: Inherited from sovereign-ai predecessor. Specific SovereignAI trigger TBD.
**Impact**: Tests failed. Required either test updates (out of scope) or compatibility shim.
**Graduated to**: OR27.

## L11 — Bypassed pre-commit hooks with --no-verify
**Trigger**: Inherited from sovereign-ai predecessor. Specific SovereignAI trigger TBD.
**Impact**: Committed code with known style violation. Required follow-up fix.
**Graduated to**: OR32.

## L12 — Hiding type errors by excluding files from hooks
**Trigger**: Inherited from sovereign-ai predecessor. Specific SovereignAI trigger TBD.
**Impact**: Type error hidden permanently. File never type-checked again.
**Graduated to**: OR33.

## L17 — Plan steps executed/marked complete out of order
**Trigger**: Inherited from sovereign-ai predecessor. Specific SovereignAI trigger TBD.
**Impact**: Step marked complete based on work done in a different section. Required replan.
**Graduated to**: OR34.

---

## Process for capturing new landmines (L24+)

At `/close` step 11, if a new failure pattern was discovered during the plan, append an entry in this format:

```markdown
## L{n} — <one-line title of the failure pattern>

**Trigger**: <Plan #, step, specific command/file/context — be concrete>
**Impact**: <What broke as a result>
```

Keep entries concise — trigger and impact only. No narrative, no cross-references to other plans. No proposed fixes or rules — those come from the Architect via `AGENTS.md`.
