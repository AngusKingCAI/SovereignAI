Depends on: 25
Vision principles: P4 (Local-first), P7 (Modular and robust), P13 (Strong and robust)
Open questions resolved: none

# Plan 25.1 — Clear Remaining Debts & Mypy Errors

S0 — Opening
- S0.0: Clone latest repo, verify execution log state.
- S0.1: Run `/open`
- S0.2: Read `AGENTS.md` in full.
- S0.3: Read `.agent/shared/DEBT.md` in full. Read `.agent/shared/DECISIONS.md` in full.
- S0.4: Read `.agent/shared/LANDMINES.md` for active patterns.

S1 — Fix Final 2 Mypy Errors
- S1.1: Read `app/sovereignai/managers/coding.py` L120-148.
- S1.2: Fix L144 — `t.provides[0].name` mypy sees `t` as `object`. Add explicit type annotation:
  ```python
  from typing import cast
  tools = [cast(ComponentManifest, manifest_map.get(skill_id)) ...]
  ```
  Or use `getattr(t, 'provides', [])` pattern.
- S1.3: Run `/verify` on coding.py. STOP if mypy still fails.
- S1.4: Read `app/sovereignai/main.py` L235-255.
- S1.5: If `create_react_loop` reference exists and is undefined: remove or define it. If error is stale (line shifted), run mypy to confirm.
- S1.6: Run `/verify` on main.py. STOP if mypy still fails.
- S1.7: Run `mypy app/sovereignai/` — must report 0 errors. STOP if >0.

S2 — Resolve DEBT-10 (AR7 Violation)
- S2.1: Read DEBT-10 description. Determine if violation is:
  a) Fixable in this plan (move UI code out of core), or
  b) Must remain deferred (document justification).
- S2.2: If fixable: identify files causing violation, extract UI logic to app/web/ or app/tui/, update imports.
- S2.3: If deferred: update DEBT-10 status to "Deferred" with justification and target plan.
- S2.4: Run AR checks (`ar_checks/run_all.py`). Must pass. STOP on failure.

S3 — Review All Open Debts
- S3.1: For each open debt (DEBT-1, 3-10):
  - Check if trigger condition has been met.
  - If resolved by Plan 25 work: mark resolved, move to CHANGELOG.
  - If still valid: confirm severity/priority/status are current.
  - If obsolete: remove with justification.
- S3.2: Run `/verify` on DEBT.md.

S4 — Verify Clean State
- S4.1: Run `ruff check .` — must be 0 errors. STOP if >0.
- S4.2: Run `mypy app/sovereignai/ app/web/ app/tui/` — must be 0 errors. STOP if >0.
- S4.3: Run `bandit -r app/sovereignai/` — review findings. Document acceptable nosec.
- S4.4: Run full pytest suite: `pytest .agent/executor/tests/ .agent/executor/tests/app_tests/ .agent/executor/tests/sovereignai/ -q --tb=short`.
- S4.5: All tests must pass. STOP if any failure.
- S4.6: Run AR checks, OR checks, landmine checks. All must pass. STOP on failure.
- S4.7: Run `verify_close.py`. Must exit 0. STOP if fail.

S5 — Close
- S5.1: Run `/close`. STOP on any failure.
