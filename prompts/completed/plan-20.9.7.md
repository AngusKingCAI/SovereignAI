Depends on: none
Vision principles: P8 (UIs are separate processes), P1 (core is sacred)
Open questions resolved: none

WILL edit:
- sovereignai/shared/types.py (add typed result dataclasses)
- sovereignai/shared/capability_api.py (add query_memory method)
- tests/test_tui_memory_panel_ar7.py (new test file)
- DEBT.md (mark TUI AR7 items resolved)
- CHANGELOG.md (add prompt-20.9.7 entry)
- PLANS.md (update baseline)
- scripts/ar_checks/spec_match.py (fix ruff issues)

S0 -- Opening
S0.1: Run `/open`
S0.2: Read `AGENTS.md` AR7, AR12, AR27 in full
S0.3: Read `tui/panels/memory.py` in full
S0.4: Read `sovereignai/shared/capability_api.py` in full

S1 -- Extend CapabilityAPI with memory queries
S1.1: Add `CapabilityAPI.query_memory(memory_type, query, limit)` method
S1.2: Route to correct backend via `memory_routing` (episodic->episodic_backend, etc.)
S1.3: Return typed `MemoryQueryResult` (not raw backend objects)
S1.4: Add `CapabilityAPI.write_memory_test()` for test write (existing functionality, moved from direct backend access)
S1.5: Run `/verify`

S2 -- Refactor TUI memory panel
S2.1: Replace direct `EpisodicMemoryBackend` import with `CapabilityAPI` calls
S2.2: Replace direct `ProceduralMemoryBackend` import with `CapabilityAPI` calls
S2.3: Replace direct `WorkingMemoryBackend` import with `CapabilityAPI` calls
S2.4: Keep `TraceBackend` access via `CapabilityAPI.stream_traces()` (already exists)
S2.5: Update `render()` to use `CapabilityAPI.query_memory()` for statistics
S2.6: Update `action_write_test_memory()` to use `CapabilityAPI.write_memory_test()`
S2.7: Run `/verify`

S3 -- Tests
S3.1: Add `test_tui_memory_panel_ar7.py`
S3.2: Test: panel renders with CapabilityAPI mock, no direct backend imports
S3.3: Test: memory query returns correct data via API
S3.4: Test: test write succeeds via API
S3.5: Run full test suite, verify no regressions

S4 -- Update DEBT
S4.1: Mark DEBT #6, #7, #8, #9, #15 as resolved at prompt-20.9.7
S4.2: Run `/verify`

Closing: Run `/close`
