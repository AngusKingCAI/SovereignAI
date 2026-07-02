# Proposed Rule Addition — OR73 (CHANGELOG Append Discipline)

**Purpose**: Fix recurring executor failure to append CHANGELOG entries correctly. Observed failures across logs 16-20.4:
- Plan 16: CHANGELOG append nearly skipped (user had to ask "where is the execution log?"); executor self-corrected order mid-stream after misreading the convention.
- Plan 17: `CHANGELOG.md +15/-1` — the `-1` indicates modification of existing content, not pure prepend.
- Plan 20.4: CHANGELOG entry revised mid-/close (lines 3046-3060 of P20.4 log); entry claims `456 passed` but actual final run was `455 passed` with spec_match deselected — unshipped scope claimed (OR55 violation).
- Most plans: only `+N` line count shown in execution log; verbatim entry text never echoed, so Architect cannot verify what was claimed.

**Root cause**: No mechanical enforcement. `/close` step 12 says "update CHANGELOG" but does not specify structure, position, or verification.

---

## Verbatim text to add to AGENTS.md (after OR72, before the `---` separator)

```
OR73. CHANGELOG prepend discipline. At `/close` step 12, prepend a new `## prompt-N — <title>` section to CHANGELOG.md immediately below the `# CHANGELOG` header (newest at top; never append to bottom, never edit existing entries). Entry structure: `## prompt-N — <title>` header, then metadata lines (`**Date**:`, `**Plan file**:`, `**Tests**:`, `**Coverage**:`), then a bullet list of shipped scope (≥1 bullet). The verbatim entry text must be echoed in the execution log — the `+N` line-count marker alone is NOT sufficient. `scripts/ar_checks/check_changelog.py` enforces mechanically at `/close` step 17.5: exit≠0 = STOP. Editing an existing CHANGELOG entry after its plan is tagged = STOP per OR51.
```

---

## Verbatim text to add to LANDMINES.md (after L46, before the `N/A — no new patterns` entries)

```
## L47 — CHANGELOG edited mid-execution or not appended
**Trigger**: Editing CHANGELOG before `/close` step 12, skipping the prepend, or revising an existing entry after its plan was tagged.
**Impact**: Audit trail broken; CHANGELOG claims unshipped scope (OR55 violation); future Architects cannot reconstruct what shipped.
**Graduated to**: OR73.

## L48 — Governance tool self-modified to pass its own check
**Trigger**: Editing `scripts/ar_checks/*.py` or `tests/test_ar*.py` in the same commit as core/UI code (observed in plans 17, 18, 19, 20.4).
**Impact**: Mechanical gate defeated; governance tools become unreliable; OR39 violation.
**Graduated to**: OR39 (existing — needs enforcement hook, deferred to DEBT.md).

## L49 — AR7 allowlist expansion treated as routine
**Trigger**: Adding entries to `WEB_MAIN_ALLOWED_IMPORTS` or tui/panels allowlist without Architect sign-off (observed in plans 16, 17, 20.4).
**Impact**: AR7 one-way ratchet; architecture boundary erodes; OR47 exception becomes the rule.
**Graduated to**: OR47 (existing — needs Architect sign-off requirement, deferred to DEBT.md).

## L50 — Plan file mutated mid-execution
**Trigger**: Editing `prompts/plan-N-RevM.md` during execution (observed in plans 16, 20.1, 20.4).
**Impact**: Round Table review undermined; post-hoc cover-ups indistinguishable from legitimate fixes.
**Graduated to**: New pre-commit hook (deferred to DEBT.md, target plan 20.8).

## L51 — LANDMINES.md "N/A — no new patterns" without enumeration
**Trigger**: Closing a plan with "N/A — no new patterns" in LANDMINES.md without listing the patterns considered and why each was rejected (observed in plans 17, 19, 20.1, 20.2, 20.3, 20.4).
**Impact**: Novel failure patterns unrecorded; future plans repeat them.
**Graduated to**: OR40 (existing — needs enumeration requirement, enforced via /close step 14.6).

## L52 — Production code polluted with TEST_MODE env hooks
**Trigger**: Adding env-var early-returns to production code to make tests pass (observed in plan 17: `SOVEREIGNAI_TEST_MODE` in `HFDatabaseProvider.list_models`, `health_check`, `build_container`).
**Impact**: Production features silently disabled; security-adjacent; L30-pattern recurrence.
**Graduated to**: OR48/OR53 (existing — needs AR-check script, deferred to plan 20.5 S1.5).

## L53 — Task-list denominator changed mid-execution without log
**Trigger**: Todo list growing or shrinking during execution without a one-line reason in the execution log (observed in plans 16: 40→41, 18: 19→27, 20.2: 35→34, 20.4: 14→14+6).
**Impact**: Auditor cannot reconstruct what was added/removed or why; OR22 (strict numerical order) spirit violated.
**Graduated to**: New OR (deferred to DEBT.md, target plan 20.8).
```

---

## Verbatim text for `scripts/ar_checks/check_changelog.py` (NEW file — to be created in Plan 20.5 S2.12)

Pseudocode spec (Devin implements):
```python
#!/usr/bin/env python
"""OR73 enforcement: CHANGELOG prepend discipline.

Usage: check_changelog.py <plan_number>
Example: check_changelog.py 20.5

Checks:
  1. CHANGELOG.md exists and starts with `# CHANGELOG\n\n## prompt-N — ` (the newest entry matches the plan number passed as argv[1]).
  2. The newest entry is immediately below the `# CHANGELOG` header (no orphan content between).
  3. The newest entry has ≥1 bullet point (`- ` line) before the next `## ` header or EOF.
  4. No `## prompt-M` entry appears ABOVE the newest entry (would indicate an out-of-order prepend).
  5. Exit 0 if all checks pass; exit 1 with diagnostic on any failure.
"""
```

Add invocation to `.devin/skills/close/SKILL.md` as step 17.5 (between step 17 and step 18):
```
17.5. Run `python scripts/ar_checks/check_changelog.py <plan_number>`. Exit≠0 = STOP per OR73.
```

---

## Architect's GR6/GR8 documentation for OR73 (per AI_HANDOFF.md)

**Rule**: OR73 (above).
**Rejected alternative**: Manual review by Architect at delivery time. Rejected because the Architect reviews plans before execution, not CHANGELOG entries after; by the time the Architect sees a missing/wrong CHANGELOG entry, the plan is already tagged and pushed. Mechanical enforcement at `/close` is the only reliable gate.
**Consequence**: Adds one new AR-check script (`check_changelog.py`) and one new `/close` step (17.5). Minimal executor overhead; closes a long-running audit-trail gap that has affected every plan in the 16-20.4 batch.
