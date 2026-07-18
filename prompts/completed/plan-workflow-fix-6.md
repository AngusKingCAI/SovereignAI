Depends on: workflow-fix-5
Vision principles: P1, P5, P11
Open questions resolved: none

---

## S0 — Opening

- S0.1: Run `/open`
- S0.2: Read `AGENTS.md` in full
- S0.3: Check `.agent/executor/suggestions/` for new rule proposals from workflow-fix-5 execution
- S0.4: Check `.agent/shared/DEBT.md` for non-rule deferred items

---

## S1 — Evaluate Executor Suggestions from workflow-fix-5

- S1.1: Read all files in `.agent/executor/suggestions/` (not .gitkeep)
- S1.2: For each suggestion, evaluate per RULE_LIFECYCLE.md TRIAGE criteria:
  - Is it a recurring error pattern? (appears in 2+ execution logs)
  - Does it have a clear detection script?
  - Does it have a clear fix?
- S1.3: Accept valid suggestions as new OR rules:
  - Add OR rule to relevant SKILL.md
  - Add detection script to `or_checks/`
  - Update `ARCHITECTURE.md` if AR rule
- S1.4: Reject invalid suggestions:
  - Document reason in suggestion file
  - Move to `.agent/executor/suggestions/archived/`
- S1.5: Run `/verify` on modified skills and scripts

---

## S2 — Fix Test Path Mismatches (Skipped from workflow-fix-5)

- S2.1: Read `.agent/executor/tests/test_ar_checks.py`
- S2.2: Replace `Path("sovereignai/...")` with `Path("app/sovereignai/...")` for all temp file creation paths
- S2.3: Replace `scripts/ar_checks/...` with `.agent/executor/scripts/ar_checks/...` for all script invocation paths
- S2.4: Replace `scripts/ar_checks/check_tracing_allowlist.txt` with `.agent/executor/scripts/ar_checks/check_tracing_allowlist.txt`
- S2.5: Read `.agent/executor/tests/test_ar7_no_core_imports_in_ui.py`
- S2.6: Replace `sovereignai/shared/capability_api.py` with `app/sovereignai/shared/capability_api.py`
- S2.7: Read `.agent/executor/tests/test_composition_root.py`
- S2.8: Replace `sovereignai/main.py` with `app/sovereignai/main.py`
- S2.9: Read `.agent/executor/tests/test_skill_discovery.py`
- S2.10: Replace `sovereignai/skills/official` with `app/sovereignai/skills/official`
- S2.11: Read `.agent/executor/tests/test_skill_manifest.py`
- S2.12: Replace `sovereignai/skills/official/file_read/manifest.toml` with `app/sovereignai/skills/official/file_read/manifest.toml`
- S2.13: Run `pytest .agent/executor/tests/test_ar_checks.py -v` — must pass
- S2.14: Run `pytest .agent/executor/tests/test_ar7_no_core_imports_in_ui.py -v` — must pass
- S2.15: Run `pytest .agent/executor/tests/test_composition_root.py -v` — must pass
- S2.16: Run `pytest .agent/executor/tests/test_skill_discovery.py -v` — must pass
- S2.17: Run `pytest .agent/executor/tests/test_skill_manifest.py -v` — must pass
- S2.18: Run `/verify` on all modified test files

---

## S3 — Fix AR Check Script Paths (Skipped from workflow-fix-5)

- S3.1: Read all `.agent/executor/scripts/ar_checks/*.py` files
- S3.2: Replace `sovereignai/` with `app/sovereignai/` in all script paths
- S3.3: Replace `scripts/ar_checks/` with `.agent/executor/scripts/ar_checks/` in all script paths
- S3.4: Run each modified script in isolation — must exit 0
- S3.5: Run `ar_checks/run_all.py` — must pass with 0 failures
- S3.6: Run `/verify` on modified scripts

---

## S4 — Add OR Rule for Error Pattern Detection

- S4.1: Read `.devin/skills/verify/SKILL.md` step 7
- S4.2: Add formal OR rule: `ORXX. Error pattern detection — if same error appears 2+ times in execution, run suggest_rule.py`
- S4.3: Define "same error" as: same error message substring OR same script failure OR same command syntax error
- S4.4: Add detection logic to `or_checks/` or document in skill
- S4.5: Run `/verify` on `verify/SKILL.md`

---

## S5 — Add OR Rule for Architect Suggestion Review

- S5.1: Read `.agent/architect/AI_HANDOFF.md` S0.3 and step 4
- S5.2: Add formal OR rule: `ORXX. Architect must evaluate all suggestions before creating plan — if suggestions exist, read and evaluate per RULE_LIFECYCLE.md TRIAGE`
- S5.3: Add to `open/SKILL.md`: "S0.3: If suggestions exist, evaluate before proceeding"
- S5.4: Run `/verify` on `AI_HANDOFF.md` and `open/SKILL.md`

---

## S6 — Verify Full Workflow Consistency

- S6.1: Run `check_rule_crossrefs.py` — must pass with 0 undefined citations
- S6.2: Run `ar_checks/run_all.py` — must pass with 0 failures
- S6.3: Run `or_checks/run_all.py` — must pass
- S6.4: Run `landmine_checks/run_all.py` — must pass
- S6.5: Run `verify_close.py` — must pass with all checks green
- S6.6: Run `get_current_plan.py` — must return correct plan or empty (not error)
- S6.7: Run full test suite: `pytest .agent/executor/tests -v --timeout=30` — document remaining failures

---

## S7 — Update CHANGELOG and Documentation

- S7.1: Prepend `CHANGELOG.md` with workflow-fix-6 entry documenting test path fixes, suggestion evaluation, new OR rules
- S7.2: Update `PLANS.md` with plan entry
- S7.3: Verify no new DEBT items created

---

## Closing

- S7.4: Run `/close`
