Depends on: workflow-fix-2
Vision principles: P1, P5, P11
Open questions resolved: none

---

## S0 — Opening

- S0.1: Run `/open`
- S0.2: Read `AGENTS.md` in full
- S0.3: Check `.agent/executor/suggestions/` for new rule proposals
- S0.4: Check `.agent/shared/DEBT.md` for non-rule deferred items

---

## S1 — Break Circular Authority References

- S1.1: Read `RULE_LIFECYCLE.md` authority line
- S1.2: Remove AI_HANDOFF.md reference from RULE_LIFECYCLE.md authority; keep PRINCIPLES.md only
- S1.3: Read `ARCHITECTURE.md` authority line
- S1.4: Remove PRINCIPLES.md reference from ARCHITECTURE.md authority; add note: "Propose changes via `.agent/shared/DEBT.md` or Round Table per PRINCIPLES.md P11"
- S1.5: Verify no document references another as authority that references it back
- S1.6: Run `/verify` on both files

---

## S2 — Fix CHANGELOG Date Gaps

- S2.1: Read `CHANGELOG.md` full content
- S2.2: For each entry missing `**Date**:` header, add date based on:
  - Plan file date from `prompts/` directory
  - Git commit history if available
  - Or mark as `**Date**: UNKNOWN` if no source can be determined
- S2.3: Add validation to `check_changelog.py` to enforce `**Date**:` header on every entry
- S2.4: Run `/verify` on `CHANGELOG.md`
- S2.5: Run `check_changelog.py` to confirm enforcement works

---

## S3 — Fix Missing Referenced Files

- S3.1: Remove `project-vision-Rev5.md` reference from PRINCIPLES.md if file cannot be found in git history
- S3.2: Fix `shared/container.py` reference in DECISIONS.md to correct path (`app/sovereignai/shared/container.py` or remove if module doesn't exist)
- S3.3: Add path validation to `check_rule_crossrefs.py` to verify referenced files exist
- S3.4: Run `/verify` on modified files

---

## S4 — Add Script Direct-Invocation Documentation

- S4.1: Read `ARCHITECTURE.md` constraint verification table
- S4.2: Add a note column indicating which skill step indirectly invokes each check script via `run_all.py`
- S4.3: Verify all AR check scripts are executable standalone (add `if __name__ == '__main__'` blocks where missing)
- S4.4: Run `/verify` on `ARCHITECTURE.md`

---

## S5 — Resolve TODO/FIXME Markers

- S5.1: Read `test_ar_checks.py` TODOs
- S5.2: Either implement skipped tests or document why they are permanently skipped with `reason="Permanently skipped: <explanation>"`
- S5.3: Verify `check_placeholders.py` TODO/FIXME references are intentional (pattern matching, not actual code debt)
- S5.4: Run `/verify` on modified test files
- S5.5: Run scoped pytest for test files

---

## S6 — Verify Full Cross-Document Consistency

- S6.1: Run `check_rule_crossrefs.py` — must pass with 0 undefined citations
- S6.2: Run `ar_checks/run_all.py` — must pass
- S6.3: Run `or_checks/run_all.py` — must pass
- S6.4: Run `landmine_checks/run_all.py` — must pass
- S6.5: Verify no circular authority references remain
- S6.6: Verify all CHANGELOG entries have dates

---

## Closing

- S6.7: Run `/close`
