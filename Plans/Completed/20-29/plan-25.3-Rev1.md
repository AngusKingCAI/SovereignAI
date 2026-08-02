# Plan 25.3 — Fix All Test Failures, Skipped Tests & Clear Remaining Debt

**Depends on:** 25.2
**Vision principles:** P4 (stability), P7 (modularity), P13 (test-driven)
**AR rules:** AR4 (DI container), AR7 (no core imports in UI), AR11 (no docstrings), AR14 (import paths)
**OR rules:** UOR-1, UOR-2, UOR-3, VOR-1, VOR-2, COR-1
**Open questions resolved:** none

---

## S0 — Opening

S0.0: Clone latest repo. Verify execution log for plan-25.2-rev1.
S0.1: Run `/open`
S0.2: Read `AGENTS.md` in full
S0.3: Read plan header AR rules from `.agent/executor/ARCHITECTURE.md` (AR4, AR7, AR11, AR14)
S0.4: Read plan header OR rules from `.agent/executor/OR_RULES.md` (UOR-1, UOR-2, UOR-3, VOR-1, VOR-2, COR-1)
S0.5: Read `.agent/shared/DEBT.md` for deferred items

---

## S1 — Establish Failure Baseline

1. Run `python -m pytest .agent/executor/tests/ -v --tb=short`
2. Capture: total tests, passed, failed, errors, skipped
3. Group failures by category:
   - EventBus timing (test_async_delivery.py, test_event_bus.py, test_task_state_machine.py)
   - SymbolMap attribute (test_symbol_map.py, test_symbol_map_degraded.py, test_symbol_map_tree_sitter.py)
   - Department Manager abstract method (test_department_manager.py)
   - AR7 violation (test_ar7_no_core_imports_in_ui.py)
   - TraceLevel mapping (test_state_machine_properties.py)
   - Other (graph_memory, file permissions, typing, hardware probe)
4. Document exact error messages and line numbers in execution log

`/verify` after this step.

---

## S2 — Fix EventBus Timing (10 failures)

**Root cause:** Tests expect specific timing behavior that doesn't match implementation.

1. Read `app/sovereignai/shared/event_bus.py` — trace `_drain_task`, `publish_async`, `start`, `stop`
2. **test_sync_handler_runs_in_thread**: Handler runs via `asyncio.to_thread()` in `_drain_task` (line 304). Test sleeps 0.5s but handler may not execute if queue isn't processed. Fix: increase sleep to 2.0s OR verify queue processing before assertion.
3. **test_queue_full_drops_newest**: `_drop_counters` is populated (line 141) but test checks `key.startswith("test-event_")`. Verify counter key format matches test expectation. Fix counter key or test assertion.
4. **test_circuit_breaker_on_error_counter_only**: Circuit breaker trips at >50 errors (line 314) but test sends 60 events. Handler should process at least 1 before breaker trips. Fix: verify drain task processes queue before breaker, or adjust test expectation.
5. **test_drain_task_crash_recovery**: Crash handler should process 5 events, recover after 3 crashes. Verify `_drain_task` continues after exception (line 306 increments error counter, loop continues). Fix: ensure exception doesn't break drain loop.
6. **test_critical_queue_overflow_sqlite**: Critical events overflow to SQLite when queue full. Verify `_critical_overflow_db` write path.
7. **test_overflow_dir_cleaned_on_stop**: Auto-created overflow dir cleaned on stop (line 341-342). Verify `self._owns_overflow_dir` flag.
8. **test_user_provided_overflow_dir_not_deleted**: User-provided dir persists. Verify flag logic.
9. **test_publish_internal_safe_after_stop**: `_safe_publish_internal` returns silently after stop (line 223-234). Verify.
10. **test_call_soon_threadsafe_loop_closed_handled**: Closed loop handled gracefully. Verify `RuntimeError` caught.
11. Re-run all 10 EventBus tests: `python -m pytest .agent/executor/tests/app_tests/test_async_delivery.py -v`

`/verify` after each fix.

---

## S3 — Fix SymbolMap Attribute (7 failures)

**Root cause:** `_TREE_SITTER_AVAILABLE` is module-level variable (line 22) but tests access as `SymbolMap._TREE_SITTER_AVAILABLE` (class attribute, line 49).

1. Read `app/sovereignai/indexing/symbol_map.py` lines 20-55
2. Verify `_TREE_SITTER_AVAILABLE` is set at module level (line 22) and also as class attribute (line 49)
3. If class attribute assignment fails (ImportError in try block sets module-level but not class-level): fix by ensuring class attribute is always set, even when tree-sitter import fails
4. Alternative: change tests to access module-level variable instead of class attribute
5. Re-run: `python -m pytest .agent/executor/tests/sovereignai/test_symbol_map.py -v`

`/verify` after this step.

---

## S4 — Fix Department Manager Abstract Method (4 failures)

**Root cause:** `DepartmentManager` has abstract method `build_context` but test mocks don't implement it.

1. Read `app/sovereignai/managers/base.py` — find `DepartmentManager` class and `build_context` abstract method
2. Read `test_department_manager.py` — find mock classes
3. Add `build_context` implementation to test mocks, or make method non-abstract if not required
4. Re-run: `python -m pytest .agent/executor/tests/sovereignai/test_department_manager.py -v`

`/verify` after this step.

---

## S5 — Fix AR7 Violation Test (2 failures)

**Root cause:** `test_ar7_no_core_imports_in_ui.py` throws `UnicodeDecodeError` reading `app/tui/panels/workers.py`.

1. Read the AR7 test file: `.agent/executor/tests/ar_checks/test_ar7_no_core_imports_in_ui.py`
2. Verify file encoding: `file app/tui/panels/workers.py`
3. Fix: add `encoding='utf-8'` to `open()` call in test, or fix file encoding
4. Verify workers.py doesn't import `sovereignai.managers.coding` (DEBT-10 was fixed in Plan 25.2)
5. Re-run: `python -m pytest .agent/executor/tests/ar_checks/test_ar7_no_core_imports_in_ui.py -v`

`/verify` after this step.

---

## S6 — Fix TraceLevel Mapping (1 failure)

**Root cause:** `test_state_machine_properties.py` — missing `TraceLevel.CRITICAL` in priority mapping.

1. Read `app/sovereignai/shared/types.py` — find `TraceLevel` enum
2. Read `app/sovereignai/shared/task_state_machine.py` — find priority mapping
3. Add `TraceLevel.CRITICAL` to priority mapping, or adjust test if CRITICAL shouldn't be included
4. Re-run: `python -m pytest .agent/executor/tests/sovereignai/test_state_machine_properties.py -v`

`/verify` after this step.

---

## S7 — Fix Remaining 16 Misc Failures

Triage individually:

1. **GraphMemory protocol**: Read `test_graph_memory.py` — fix protocol mismatch
2. **File permissions**: Read `test_file_permissions.py` — fix permission assertions for Windows
3. **AgentErrorObservation typing**: Read `test_agent_error_observation.py` — fix type annotations
4. **Hardware probe exceptions**: Read `test_hardware_probe.py` — mock hardware detection or handle missing hardware
5. Run each failing test individually, fix or document as platform-specific skip

`/verify` after each fix batch.

---

## S8 — Fix Skipped Tests (56 skipped)

1. Run `python -m pytest .agent/executor/tests/ -v --collect-only` to identify all skipped tests
2. Categorize skips:
   - **Conditional skips** (tree-sitter, hardware, platform): keep if justified, document reason
   - **Broken skips** (test incomplete, fixture missing): fix and unskip
   - **Deprecated skips** (feature removed): delete test
3. Fix broken skips:
   - Missing fixtures: add to conftest.py
   - Incomplete tests: complete implementation
   - Platform-specific: add proper skipif decorator
4. Target: ≤10 justified skips remaining

`/verify` after this step.

---

## S9 — Clear Remaining DEBT (4-9)

1. **DEBT-4** (UI implementations): Check if web/tui are functional. If not, keep as debt with target plan.
2. **DEBT-5** (P4 compliance test isolation): Check if P4 tests are isolated. Fix or document.
3. **DEBT-6** (Librarian.handle_event): Check implementation status. Fix or keep.
4. **DEBT-7** (TUI cookie auth): Check SSE auth. Fix or keep.
5. **DEBT-8** (Web UI consumer): Check SSE consumer. Fix or keep.
6. **DEBT-9** (Cross-task graph memory): Check graph memory. Fix or keep.
7. Update `.agent/shared/DEBT.md` — mark resolved items, update status on remaining

`/verify` after this step.

---

## S10 — Full Suite Verification

1. Run `python -m pytest .agent/executor/tests/ -v`
2. Target: 0 failures, ≤10 justified skips
3. Run `ruff check .`
4. Run `mypy` on modified files
5. Run `bandit -r app/`
6. Run `.agent/executor/scripts/ar_checks/run_all.py`
7. All must pass. If any fail: fix or STOP.

`/verify` after this step.

---

## S11 — Update DEBT.md & CHANGELOG

1. Update `.agent/shared/DEBT.md` — mark all resolved debts
2. Prepend `.agent/shared/CHANGELOG.md` with plan summary
3. Update `.agent/shared/PLANS.md` — mark 25.3 Completed

`/verify` after this step.

---

## Closing

Run `/close`. HARD GATE: verify_close.py must pass.

---

## Expected Outcomes

- 0 test failures
- ≤10 justified skipped tests
- All DEBT items resolved or documented with clear targets
- All static analysis passes
- All AR checks pass
- CHANGELOG.md prepended with plan summary
- Clean working tree, ready for Plan 26
