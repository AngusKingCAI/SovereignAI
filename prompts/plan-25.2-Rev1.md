# Plan 25.2 — Fix Test Environment & Clear False Debts

**Depends on:** 25.1
**Vision principles:** P4 (stability), P13 (test-driven)
**AR rules:** AR4 (DI container), AR11 (no docstrings)
**OR rules:** UOR-1, UOR-2, UOR-3, COR-1
**Open questions resolved:** none

---

## S0 — Opening

S0.0: Clone latest repo. Verify execution log for plan-25.1-rev1.
S0.1: Run `/open`
S0.2: Read `AGENTS.md` in full
S0.3: Read plan header AR rules from `.agent/executor/ARCHITECTURE.md` (AR4, AR11)
S0.4: Read plan header OR rules from `.agent/executor/OR_RULES.md` (UOR-1, UOR-2, UOR-3, COR-1)
S0.5: Read `.agent/shared/DEBT.md` for deferred items

---

## S1 — Diagnose Test Environment

1. Run `python -m pytest --version` to verify pytest is installed
2. Run `python -m pytest .agent/executor/tests/ -x --tb=short` to reproduce the failure
3. Capture the exact error: pytest-timeout plugin failure, missing dependency, or version incompatibility
4. Check `pyproject.toml` `[project.optional-dependencies] dev` section for version conflicts
5. Document the root cause in the execution log

`/verify` after this step.

---

## S2 — Fix pytest-timeout

If pytest-timeout fails to load:
1. Check if `pytest-timeout>=2.0` is compatible with installed pytest version
2. If incompatible: update to `pytest-timeout>=2.3.0` (or latest stable) in `pyproject.toml`
3. If not needed: remove `pytest-timeout` from dev dependencies and remove `--timeout=300 --timeout-method=thread` from `tool.pytest.ini_options.addopts`
4. Run `pip install -e .[dev]` to reinstall
5. Re-run `python -m pytest --version` to confirm clean load

`/verify` after this step.

---

## S3 — Verify DEBT-3 (DIContainer Circular Import)

1. Read `app/sovereignai/di/container.py` top-to-bottom
2. Trace all import statements — check for circular imports between:
   - `container.py` → any module that imports `container.py`
   - `main.py` → `container.py` → any module imported by `main.py`
3. Run `python -c "from sovereignai.di.container import DIContainer"` to verify clean import
4. If circular import exists: document the cycle, plan fix for Plan 25.3 or later
5. If no circular import: DEBT-3 is false — mark as "Resolved (false debt)" in DEBT.md

`/verify` after this step.

---

## S4 — Clear DEBT-1 (False Debt)

1. Verify `diskcache` is NOT in `app/txt/requirements.txt`
2. Verify `diskcache` is NOT imported in any `.py` file under `app/`
3. Verify `TaskGraphCache` uses SQLite directly (not diskcache)
4. Delete DEBT-1 entry from `.agent/shared/DEBT.md`
5. Document: "DEBT-1 deleted — diskcache is not a project dependency"

`/verify` after this step.

---

## S5 — Run Full Test Suite Baseline

1. Run `python -m pytest .agent/executor/tests/ -v --tb=short`
2. Capture: total tests, passed, failed, errors, skipped
3. Run `python -m pytest .agent/executor/tests/app_tests/ -v --tb=short`
4. Capture same metrics
5. Run `python -m pytest .agent/executor/tests/sovereignai/ -v --tb=short`
6. Capture same metrics
7. Document full results in execution log

If tests fail: STOP. Do not proceed to S6. Document failures for Plan 25.3.

`/verify` after this step.

---

## S6 — Static Analysis Pass

1. Run `ruff check .`
2. Run `mypy` on modified files only
3. Run `bandit -r app/`
4. All must pass. If any fail: fix or STOP.

`/verify` after this step.

---

## S7 — AR Checks

1. Run `.agent/executor/scripts/ar_checks/run_all.py`
2. All must pass. If any fail: fix or STOP.

`/verify` after this step.

---

## S8 — Update DEBT.md

1. Remove DEBT-1 (false debt)
2. Update DEBT-3 status: "Resolved (false debt)" or "Confirmed — fix in Plan 25.3"
3. Add note: "DEBT-10 remains open — target Plan 25.3"
4. Prepend `.agent/shared/CHANGELOG.md` with plan summary

`/verify` after this step.

---

## Closing

Run `/close`. HARD GATE: verify_close.py must pass.

---

## Expected Outcomes

- pytest loads and runs without plugin failures
- DEBT-1 deleted from DEBT.md
- DEBT-3 status confirmed (resolved or documented for next plan)
- Full test suite baseline established (pass/fail counts documented)
- All static analysis passes
- CHANGELOG.md prepended with plan summary
