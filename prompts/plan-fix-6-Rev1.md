Depends on: plan-fix-5-Rev1
Vision principles: P3 (Reliability), P11 (Quality)
Open questions resolved: none

## S0 — Opening

S0.0: Clone latest repo. Verify plan-fix-5-Rev1 completed.
S0.1: Run `/open`
S0.2: Read `AGENTS.md` in full
S0.3: Check `.agent/shared/DEBT.md`
S0.4: Run `grep -r 'Devin' --include='*.md' .devin/skills/` — catalog hardcoded references

## F1 — Fix Plan 22 Forward Dependency

**Problem**: Plan 22 references Plan 24's TaskGraphCache but Plan 24 is queued later.

F1.1: Read `prompts/plan-22-Rev11.md`
F1.2: Edit `Depends on:` header from "Plan 21" to "Plan 21, Plan 24"
F1.3: Run `pytest .agent/executor/tests/test_document_hygiene.py -v` — verify pass

## F2 — Standardize Plan Filename Convention

**Problem**: 3 plans use lowercase "rev" in filename.

F2.1: Rename:
  - prompts/plan-22-rev11.md → prompts/plan-22-Rev11.md (completed)
  - prompts/plan-23-rev11.md → prompts/plan-23-Rev11.md (completed)
  - prompts/plan-24-rev11.md → prompts/plan-24-Rev11.md (completed)
F2.2: Update any internal references to old filenames
F2.3: Run `pytest .agent/executor/tests/test_document_hygiene.py -v` — verify pass

## F3 — Remove Devin Hardcoding from Skills

**Problem**: close/SKILL.md says "Executor: Devin".

F3.1: Edit close/SKILL.md step 11: replace "Executor: Devin" with "Executor: {executor-name}" (completed)
F3.2: Edit LANDMINES.md H1: replace Devin-specific API terms with generic equivalents (completed)
F3.3: Edit VOR-2 in OR_RULES.md similarly (completed)
F3.4: Run `pytest .agent/executor/tests/test_document_hygiene.py -v` — verify pass

## F4 — Fix /verify git add Mixing Concerns

**Problem**: verify/SKILL.md step 5 runs `git add prompts/*.md` mid-verify.

F4.1: Remove step 5 from verify/SKILL.md (completed)
F4.2: Verify close/SKILL.md step 13 already handles staging (confirmed)
F4.3: Run `pytest .agent/executor/tests/test_document_hygiene.py -v` — verify pass

## F5 — Fix scan/SKILL.md Self-Contained Claim

**Problem**: Claims "Self-contained — does not invoke /close" but uses verify_close.py.

F5.1: Edit scan/SKILL.md: replace "Self-contained" with "Self-contained except for shared verify_close.py hard gate." (completed)
F5.2: Run `pytest .agent/executor/tests/test_document_hygiene.py -v` — verify pass

## F6 — Fix STOP Recovery Semantics

**Problem**: close/SKILL.md steps 5–9 say "STOP on failure" but only step 10 is "HARD GATE".

F6.1: Edit close/SKILL.md: add recovery note — "Non-HARD-GATE STOP (steps 1–9): fix and retry. HARD-GATE STOP (step 10): abort, do not commit." (completed)
F6.2: Run `pytest .agent/executor/tests/test_document_hygiene.py -v` — verify pass

## Closing

Run `/close`
