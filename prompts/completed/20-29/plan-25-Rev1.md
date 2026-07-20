Depends on: 24
Vision principles: P4 (Local-first), P7 (Modular and robust), P9 (Observability), P13 (Strong and robust)
Open questions resolved: none

# Plan 25 — Scan & Cleanup (Whole-Repo Verification)

S0 — Opening
- S0.0: Clone latest repo, verify execution log state.
- S0.1: Run `/open`
- S0.2: Read `AGENTS.md` in full.
- S0.3: Check `.agent/shared/DEBT.md` for deferred items.
- S0.4: Read `.agent/shared/LANDMINES.md` for active patterns.

S1 — Fix Import Paths (M1 landmine)
- S1.1: Run `check_import_paths.py`. Record all `app.sovereignai.*` violations.
- S1.2: Fix all 13 files: replace `from app.sovereignai.` with `from sovereignai.` and `import app.sovereignai.` with `import sovereignai.`.
- S1.3: Add missing `__init__.py` to:
  - app/sovereignai/skills/external/
  - app/sovereignai/skills/user/
  - app/sovereignai/skills/official/file_write/
  - app/sovereignai/skills/official/file_read/
  - app/sovereignai/skills/official/file_search/
- S1.4: Run `/verify` on each changed file. STOP on error.

S2 — Fix Test Discovery (testpaths)
- S2.1: Edit `pyproject.toml` [tool.pytest.ini_options] testpaths:
  - Add `.agent/executor/tests/sovereignai/` to testpaths list.
- S2.2: Verify no test directory named `sovereignai/` shadows installed package (M6 landmine). Current `tests/sovereignai/` is OK (under `.agent/executor/`).
- S2.3: Run `/verify` on pyproject.toml.

S3 — Fix Governance Docs
- S3.1: Remove duplicate COR-1 from `.agent/shared/OR_RULES.md` (keep first, delete second identical block).
- S3.2: Run `/verify` on OR_RULES.md.

S4 — Implement Landmine Checks
- S4.1: Replace stub `landmine_checks/run_all.py` with actual runner that:
  - Discovers all scripts in `landmine_checks/` directory.
  - Runs each script, captures output.
  - Exits 0 only if ALL pass, exits 1 if ANY fail.
  - Uses same caching pattern as `ar_checks/run_all.py`.
- S4.2: Create `landmine_checks/check_m1_import_paths.py` — wraps `check_import_paths.py` with landmine output format.
- S4.3: Create `landmine_checks/check_m6_namespace_collision.py` — verifies no test directory shadows installed package.
- S4.4: Run `/verify` on each new script.

S5 — Run Full Test Suite
- S5.1: Run `pytest .agent/executor/tests/app_tests/ -q --tb=short`. Record pass/fail/skip.
- S5.2: Run `pytest .agent/executor/tests/sovereignai/ -q --tb=short`. Record pass/fail/skip.
- S5.3: Run `pytest .agent/executor/tests/ -q --tb=short` (architect/executor tests). Record pass/fail/skip.
- S5.4: Run full suite: `pytest .agent/executor/tests/ .agent/executor/tests/app_tests/ .agent/executor/tests/sovereignai/ -q --tb=short`.
- S5.5: If ANY failure: fix or document with pytest.skip per M5. STOP if unfixable.

S6 — Static Analysis
- S6.1: Run `ruff check .`. Fix all errors. STOP if >0 remain.
- S6.2: Run `mypy app/sovereignai/ app/web/ app/tui/`. Fix all errors. STOP if >0 remain.
- S6.3: Run `bandit -r app/sovereignai/`. Review all findings. Document acceptable nosec with justification.
- S6.4: Run `pip-audit`. Review CVEs. Document per DEBT-1.
- S6.5: Run `vulture app/sovereignai/`. Review dead code. Remove or justify.
- S6.6: Run `detect-secrets scan`. Review hits. Add to `.secrets.baseline` if false positive.

S7 — AR Checks
- S7.1: Run `ar_checks/run_all.py`. Fix all failures. STOP if any remain.
- S7.2: Verify AR7 (circuit-breaker), AR8 (tracing), AR10 (local-first), AR12 (UI separation), AR14 (DTOs) all pass.

S8 — OR Checks
- S8.1: Run `or_checks/run_all.py`. Fix all failures. STOP if any remain.

S9 — Landmine Checks
- S9.1: Run `landmine_checks/run_all.py` (now implemented). Fix all failures. STOP if any remain.

S10 — Cross-Reference & Placeholders
- S10.1: Run `check_rule_crossrefs.py`. Fix undefined citations. STOP on failure.
- S10.2: Run `check_placeholders.py`. Remove all TODO/FIXME/XXX. STOP on hit.

S11 — verify_close.py Hard Gate
- S11.1: Run `verify_close.py`. Must exit 0.
- S11.2: If fail: fix root cause, retry. STOP if unfixable.

S12 — Close
- S12.1: Run `/close`. STOP on any failure.
