# Plan 18.3 Test Triage

## Summary
- **Total tests run**: 418 (380 passed, 26 failed, 12 skipped)
- **Failure count**: 26 (not 46 as mentioned in plan)
- **Date**: 2026-06-30

## Failure Classification

### Class 1: Windows File Lock (1 failure)
**Test**: `tests/databases/test_huggingface_schema.py::test_ensure_latest_schema`
- **Error**: `PermissionError: [WinError 32] The process cannot access the file because it is being used by another process: 'C:\\Users\\King\\AppData\\Local\\Temp\\tmp61c9wziv\\models.db'`
- **Root cause**: SQLite file not properly closed before temp cleanup on Windows
- **Fix**: Ensure `conn.close()` is called in finally block, or use `:memory:` SQLite for tests

### Class 2: Thread-local Attribute Not Initialized (1 failure)
**Test**: `tests/shared/test_correlation_id.py::test_copy_correlation_id_to_thread`
- **Error**: `AttributeError: '_thread._local' object has no attribute 'captured_id'`
- **Root cause**: Thread-local attribute not initialized in `__init__` of correlation module
- **Fix**: Initialize the thread-local attribute in `__init__` or use `getattr` with default

### Class 3: AR7 Violation - UI Imports Core (1 failure)
**Test**: `tests/test_ar7_no_core_imports_in_ui.py::test_ui_directories_do_not_import_core_internals[web]`
- **Error**: `AssertionError: C:\SovereignAI\web\hardware_probe.py imports forbidden package: {'sovereignai.shared.trace_emitter.TraceEmitter', 'sovereignai.shared.trace_emitter.TraceLevel', 'sovereignai.shared.trace_emitter'}`
- **Root cause**: `web/hardware_probe.py` directly imports `sovereignai.shared.trace_emitter`, violating AR7
- **Fix**: Either lazy import behind function boundary, refactor to receive trace via DI, or add to AR7 allowlist with justification

### Class 4: 422 Unprocessable Entity - Missing app.state.container (23 failures)
All these tests fail with 422 status, indicating the test fixture doesn't set up `app.state.container`:

**Tests**:
1. `tests/web/test_endpoint_tracing.py::test_endpoint_tracing_info_at_entry`
2. `tests/web/test_endpoint_tracing.py::test_endpoint_tracing_debug_at_exit`
3. `tests/web/test_endpoint_tracing.py::test_correlation_id_propagation`
4. `tests/web/test_hierarchical_catalog.py::test_hierarchical_catalog_orgs`
5. `tests/web/test_hierarchical_catalog.py::test_hierarchical_catalog_families`
6. `tests/web/test_hierarchical_catalog.py::test_hierarchical_catalog_versions`
7. `tests/web/test_hierarchical_catalog.py::test_hierarchical_catalog_variants`
8. `tests/web/test_hierarchical_catalog.py::test_hierarchical_catalog_sorting`
9. `tests/web/test_hierarchical_catalog.py::test_hierarchical_catalog_file_type_filter`
10. `tests/web/test_models_category_badge.py::test_category_badge_nlp`
11. `tests/web/test_models_category_badge.py::test_category_badge_multimodal`
12. `tests/web/test_models_category_badge.py::test_category_badge_computer_vision`
13. `tests/web/test_models_filter.py::test_category_filter`
14. `tests/web/test_models_filter.py::test_vram_fit_filter`
15. `tests/web/test_models_filter.py::test_quant_level_filter`
16. `tests/web/test_models_filter.py::test_search_filter`
17. `tests/web/test_models_hierarchical.py::test_hierarchical_catalog_structure`
18. `tests/web/test_models_hierarchical.py::test_lazy_loading_org_level`
19. `tests/web/test_models_hierarchical.py::test_lazy_loading_family_level`
20. `tests/web/test_models_sort.py::test_sort_by_name_ascending`
21. `tests/web/test_models_sort.py::test_sort_by_name_descending`
22. `tests/web/test_models_sort.py::test_sort_by_size_ascending`
23. `tests/web/test_models_sort.py::test_sort_by_size_descending`

- **Error**: `assert 422 == 200` (or `assert 422 in [200, 401]`)
- **Root cause**: Test fixtures don't initialize `app.state.container` via `build_container()`. The web app expects this to be set for dependency injection.
- **Fix**: Update test fixtures to call `build_container()` and set `app.state.container`

## Fix Order
1. **Class 4** (23 failures) - Fix test fixtures to set up container (highest impact)
2. **Class 3** (1 failure) - Fix AR7 violation in hardware_probe.py
3. **Class 2** (1 failure) - Fix thread-local initialization
4. **Class 1** (1 failure) - Fix Windows file lock in schema test
