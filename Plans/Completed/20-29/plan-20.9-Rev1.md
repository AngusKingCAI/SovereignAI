Depends on: prompt-20.8
Vision principles: A8 (no hidden complexity), workflow efficiency
Open questions resolved: none

## S0 — Opening

- S0.1: Run `/open`
- S0.2: Read `AGENTS.md` in full
- S0.3: Add new rules if needed, commit before coding

## S1 — Create Workflow Optimization Scripts

- S1.1: Create `scripts/verify_syntax.py` to consolidate 7 file type syntax checks (Python, JSON, YAML, TOML, HTML, CSS, JavaScript)
- S1.2: Create `scripts/check_rule_crossrefs.py` to replace complex shell pipeline for OR/AR cross-reference checking
- S1.3: Create `scripts/check_ar7_allowlist.py` to replace awk/grep pipeline for AR7 allowlist diff checking
- S1.4: Create `scripts/get_current_plan.py` to replace fragile `ls -v | tail -n 1` pattern
- S1.5: Run ruff on all new scripts and fix any issues
- S1.6: Verify each script with syntax check

## S2 — Update Workflow Files

- S2.1: Update `close/SKILL.md` Step 0 to use `scripts/get_current_plan.py`
- S2.2: Update `close/SKILL.md` Step 11 to use `scripts/check_ar7_allowlist.py`
- S2.3: Update `close/SKILL.md` Step 12 to shorten CHANGELOG template
- S2.4: Update `close/SKILL.md` Step 16 to remove advisory text
- S2.5: Update `open/SKILL.md` Step 8 to add concrete ambiguity criteria
- S2.6: Update `open/SKILL.md` Steps 12-13 to combine rules/landmines commits
- S2.7: Update `open/SKILL.md` incremental verification steps to number them 46-50
- S2.8: Update `scan/SKILL.md` Step 5 to add specific search patterns
- S2.9: Update `scan/SKILL.md` Step 5.5 to use `scripts/check_rule_crossrefs.py`
- S2.10: Update `scan/SKILL.md` Step 12 to use dynamic summary template
- S2.11: Update `verify/SKILL.md` Step 1 to use `scripts/verify_syntax.py`
- S2.12: Update `verify/SKILL.md` Step 3 to add specific error format

## S3 — Update Governance Files

- S3.1: Condense AR11 in `AGENTS.md`: "No docstrings (D103 disabled). Self-documenting names required."
- S3.2: Condense AR22 in `AGENTS.md`: "Every function with side effects emits ≥1 trace event. Mechanical classification via check_tracing.py; no self-exemptions."
- S3.3: Condense AR29 in `AGENTS.md`: "Diagnostic harness: load → use → unload per stage. Mocks verify paths; harness verifies system."
- S3.4: Add D6-Correction to `DECISIONS.md` for stale rule reference (AR17→AR11, AR21 removed)

## S4 — Create Test Coverage

- S4.1: Create `tests/test_verify_syntax.py` with tests for file syntax verification
- S4.2: Create `tests/test_check_rule_crossrefs.py` with tests for cross-reference checking
- S4.3: Create `tests/test_check_ar7_allowlist.py` with tests for AR7 allowlist checking
- S4.4: Create `tests/test_get_current_plan.py` with tests for plan resolution
- S4.5: Run all new tests and ensure they pass

## S5 — Update Support Files

- S5.1: Update `scripts/ar_checks/spec_match.py` allowlist to include new scripts and test files
- S5.2: Update `scripts/ar_checks/spec_match.py` allowlist to include efficiency-audit-brief.md deletion

## S6 — Verification

- S6.1: Run full test suite: `pytest tests/ -q`
- S6.2: Run ruff check on all modified files
- S6.3: Verify all scripts pass syntax checks
- S6.4: Run `scripts/check_rule_crossrefs.py` to verify no undefined rule citations

## Closing

Run `/close`
