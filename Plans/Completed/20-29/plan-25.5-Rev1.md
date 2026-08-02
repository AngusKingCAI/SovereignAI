Depends on: Plan 25.4
Vision principles: P13 (Strong and robust)
AR rules: none
OR rules: UOR-1, VOR-2
Open questions resolved: none

## S0 — Opening

S0.0: Clone latest repo. Verify Plan 25.4 state.
S0.1: Run `/open`
S0.2: Read `AGENTS.md`
S0.3: Read UOR-1, VOR-2 from `.agent/executor/OR_RULES.md`.
S0.4: Read `.agent/shared/DEBT.md` — no debt items triggered.

## S1 — Fix get_scoped_tests.py

S1.1: Read `.agent/executor/scripts/get_scoped_tests.py`.
S1.2: Change `git diff --name-only HEAD` to `git log --name-only -1 --pretty=format:`.
   Executor commits after edits; working tree is always clean.
S1.3: Update `sovereignai` scope to include ALL test directories:
   [".agent/executor/tests/app_tests/", ".agent/executor/tests/sovereignai/",
   ".agent/executor/tests/conformance/", ".agent/executor/tests/contracts/",
   ".agent/executor/tests/property/"]
S1.4: Update `architect` scope to return only top-level tests:
   [".agent/executor/tests/test_*.py"]
S1.5: Add test-only change detection.
S1.6: Run `/verify` on the script.

## S2 — Fix test_document_hygiene.py

S2.1: Read `.agent/executor/tests/test_document_hygiene.py`.
S2.2: Update `test_plans_table_completeness` to check for "## Recent History" instead of "## Recent Completed".
S2.3: Update `test_plans_baseline_reconciliation_completeness` to check for baseline in new PLANS.md format.
S2.4: Run `/verify` on the test file.

## S3 — Fix Hardware Probe Tests

S3.1: Read `.agent/executor/tests/app_tests/test_hardware_probe.py`.
S3.2: Identify root cause of import/exception failures.
S3.3: Fix test assertions to match actual error handling behavior.
S3.4: Run `/verify` on the test file.

## S4 — Fix TUI Memory Panel AR7 Tests

S4.1: Read `.agent/executor/tests/app_tests/test_tui_memory_panel_ar7.py`.
S4.2: Fix TypeError in `test_memory_panel_uses_capability_api`.
S4.3: Run `/verify` on the test file.

## S5 — Fix TUI Main Tests

S5.1: Read `.agent/executor/tests/app_tests/tui/test_tui_main.py`.
S5.2: Fix TypeError in `test_tui_lazy_panel_loading`.
S5.3: Run `/verify` on the test file.

## S6 — Verify All Fixes

S6.1: Run `pytest .agent/executor/tests/test_document_hygiene.py -v`.
S6.2: Run `pytest .agent/executor/tests/app_tests/test_hardware_probe.py -v`.
S6.3: Run `pytest .agent/executor/tests/app_tests/test_tui_memory_panel_ar7.py -v`.
S6.4: Run `pytest .agent/executor/tests/app_tests/tui/test_tui_main.py -v`.
S6.5: STOP on any failure.

## Closing

Run `/close`. Use COR-1: run full test suite `pytest .agent/executor/tests/`.
