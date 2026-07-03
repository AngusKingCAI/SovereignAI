# LANDMINES.md

Prepend-only (newest entries at top). Never edit or remove entries. Format:
`
## L{n} � <title>
**Trigger**: <plan, step, command/file>
**Impact**: <what broke>
**Graduated to**: <OR{n} or workflow fix}
`

---

N/A — no new patterns (plan completed without STOP, no new ORs added, AR checks passed)

---

## L69 — Untracked plan files deleted as cleanup artifacts

**Trigger**: Deleting untracked plan files (plan-20.9.8.md, plan-20.9.9.md) during cleanup using `rm` or `Remove-Item`.
**Impact**: Loss of valid plan files that were awaiting commit. Untracked files are not "artifacts" - they are valid plans that haven't been committed yet. OR27 applies to ALL plan files regardless of git status.
**Graduated to**: OR27 clarification (prompt-20.9.7).

---

N/A — no new patterns (plan completed without STOP, no new ORs added, AR checks passed)

---

## L68 — Plan split with content modification
**Trigger**: Devin splits an over-long plan but reorders, adds, removes, or rewords S0-Sn steps or WILL-edit entries during the split.
**Impact**: Round Table review undermined; scope creep hidden as "repackaging".
**Graduated to**: check_plan_immutability.py (script-enforced).

---

N/A — no new patterns (AR19 added per plan requirements, not a failure pattern)

---

N/A — no new patterns for prompt-18

---

N/A — no new patterns for prompt-20


---

## L67 — Plan split without independent /open and /close
**Trigger**: Devin splits an over-long plan into sub-plans but one or more sub-plans skip /open or /close.
**Impact**: Governance gates (check_dependencies.py, check_plan_immutability.py, check_rule_conciseness.py, check_changelog.py) not enforced on the skipped sub-plan; AR-check bypass.
**Graduated to**: check_plan_immutability.py (script-enforced).

---


---

## L59 — sailogs/ not gitignored
**Trigger**: sailogs/ created without .gitignore entry.
**Impact**: trace logs (may contain sensitive data) committed to repo.
**Graduated to**: Implementation detail (removed from rules, enforced in code).

---


---

## L54 — ContentSwitcher import path error
**Trigger**: `from textual.containers import ContentSwitcher` (observed in P20.4 ImportError). Correct import is `from textual.widgets import ContentSwitcher`.
**Impact**: ImportError at runtime; manual `hidden` class fallback with 4 bugs (B1-B3 in Plan 20.6).
**Graduated to**: AR31 (architecture requirement, enforced in code).

---


---

## L53 — Task-list denominator changed mid-execution without log
**Trigger**: Todo list growing or shrinking during execution without a one-line reason in the execution log (observed in plans 16: 40→41, 18: 19→27, 20.2: 35→34, 20.4: 14→14+6).
**Impact**: Auditor cannot reconstruct what was added/removed or why; strict numerical order spirit violated.
**Graduated to**: New OR (deferred to DEBT.md, target plan 20.8).

---


---

## L52 — Production code polluted with TEST_MODE env hooks
**Trigger**: Adding env-var early-returns to production code to make tests pass (observed in plan 17: `SOVEREIGNAI_TEST_MODE` in `HFDatabaseProvider.list_models`, `health_check`, `build_container`).
**Impact**: Production features silently disabled; security-adjacent; L30-pattern recurrence.
**Graduated to**: AR20/OR19 (existing — needs AR-check script, deferred to plan 20.5 S1.5).


---

## L51 — LANDMINES.md "N/A — no new patterns" without enumeration
**Trigger**: Closing a plan with "N/A — no new patterns" in LANDMINES.md without listing the patterns considered and why each was rejected (observed in plans 17, 19, 20.1, 20.2, 20.3, 20.4).
**Impact**: Novel failure patterns unrecorded; future plans repeat them.
**Graduated to**: /close skill (existing — needs enumeration requirement, enforced via /close step 14.6).


---

## L50 — Plan file mutated mid-execution
**Trigger**: Editing `prompts/plan-N-RevM.md` during execution (observed in plans 16, 20.1, 20.4).
**Impact**: Round Table review undermined; post-hoc cover-ups indistinguishable from legitimate fixes.
**Graduated to**: New pre-commit hook (deferred to DEBT.md, target plan 20.8).


---

## L49 — AR7 allowlist expansion treated as routine
**Trigger**: Adding entries to `WEB_MAIN_ALLOWED_IMPORTS` or tui/panels allowlist without Architect sign-off (observed in plans 16, 17, 20.4).
**Impact**: AR7 one-way ratchet; architecture boundary erodes; OR23 exception becomes the rule.
**Graduated to**: OR23 (existing — needs Architect sign-off requirement, deferred to DEBT.md).


---

## L48 — Governance tool self-modified to pass its own check
**Trigger**: Editing `scripts/ar_checks/*.py` or `tests/test_ar*.py` in the same commit as core/UI code (observed in plans 17, 18, 19, 20.4).
**Impact**: Mechanical gate defeated; governance tools become unreliable; OR22 violation.
**Graduated to**: OR22 (existing — needs enforcement hook, deferred to DEBT.md).


---

## L45 — Stray files in commits without pre-commit scan
**Trigger**: cookies.txt staged by `git add -A`.
**Impact**: Unintended files committed.
**Graduated to**: OR33.


---

## L43 — Tests used incorrect fixture shapes
**Trigger**: Test fixtures didn't match production data shapes.
**Impact**: Tests pass but production breaks.
**Graduated to**: OR32.


---

## L42 — HTML/CSS/JS syntax not validated before tests
**Trigger**: Python docstrings in app.js, double-class in HTML.
**Impact**: Invalid code shipped.
**Graduated to**: OR31.


---

## L40 — Skipped tests without target-resolution plan
**Trigger**: Tests skipped with no documented target.
**Impact**: Skipped tests accumulate.
**Graduated to**: OR30.


---

## L39 — Test failures dismissed as "pre-existing"
**Trigger**: 46 test failures shipped as "pre-existing".
**Impact**: Broken tests in production.
**Graduated to**: OR29.


---

## L38 — "Already done" claim without verification
**Trigger**: Marking steps complete via visual inspection only.
**Impact**: Incomplete work marked done.
**Graduated to**: OR28.


---

## L37 — Plan shipped with placeholder implementation
**Trigger**: sync.py shipped with `# TODO: Fetch actual data`.
**Impact**: Feature non-functional.
**Graduated to**: OR27.


---

## L36 — Crash recovery disabled
**Trigger**: `run_crash_recovery()` body replaced with `pass`.
**Impact**: No crash recovery.
**Graduated to**: AR21.


---

## L35 — Memory backends not registered in container
**Trigger**: Memory backends not in DI container.
**Impact**: Backends not accessible.
**Graduated to**: AR20.


---

## L34 — Mypy errors dismissed as "pre-existing"
**Trigger**: Mypy errors dismissed without fixing.
**Impact**: Type errors shipped.
**Graduated to**: OR29.


---

## L33 — Filtered on non-existent event attribute
**Trigger**: Self-correction skill filtered on `event.component` which didn't exist.
**Impact**: Filter never matched.
**Graduated to**: AR23.


---

## L30 — Disabled production features to make tests pass
**Trigger**: Disabling crash recovery/memory backends to pass tests.
**Impact**: Production features off.
**Graduated to**: AR20, OR19.


---

## L29 — close.md Step 17 verification check said "run git rm" which DELETES files
**Trigger**: `/close` Step 17 used `git rm` to move files.
**Impact**: Files deleted instead of moved.
**Graduated to**: close.md fix (prompt-15).


---

## L22 — Executor weakens AR check scripts or tests to make a failure pass
**Trigger**: Editing tests/checks to weaken assertions.
**Impact**: Failures hidden.
**Graduated to**: OR22.


---

## L9 — Interface changes break existing tests during type remediation
**Trigger**: Changing function signatures during type fixes.
**Impact**: Existing tests fail on new signature.
**Graduated to**: OR9.


---

## L6 — Naive/aware datetime mixing
**Trigger**: `datetime.utcnow()` or bare `datetime.now()` mixed with aware.
**Impact**: Comparison errors, timezone bugs.
**Graduated to**: OR7.


---

## L5 — Vulture flags unused test fixtures incorrectly
**Trigger**: Vulture on test files with pytest fixtures.
**Impact**: Fixtures flagged unused despite decorator requirement.
**Graduated to**: OR22.


---

## L{n} — <title>
**Trigger**: <plan, step, command/file>
**Impact**: <what broke>
**Graduated to**: <OR{n} or workflow fix>
```

---
