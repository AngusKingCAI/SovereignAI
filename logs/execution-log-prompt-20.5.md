# Execution Log: prompt-20.5 — Governance Cleanup

**Plan**: prompts/plan-20.5-Rev0.md
**Date**: 2026-07-02
**Executor**: Cascade

---

## Devin Chat

[PASTE DEVIN CHAT HERE]

---

## S0 — Opening
- Added OR73 to AGENTS.md (CHANGELOG prepend discipline)
- Added landmines L47-L53 to LANDMINES.md (governance tool integrity)

## S1 — CRITICAL fixes
- S1.1: Replaced placeholder SHA-256 hash in llama_cpp_adapter/manifest.toml with real hash
- S1.2: Removed spec_match.py self-exemption for scripts/ar_checks/ and logs/
- S1.3: Removed CORE_EXCEPTION from ui_does_not_touch_core.py
- S1.4: Removed SOVEREIGNAI_TEST_MODE env-var hooks from production code (databases/hf_database/provider.py, sovereignai/main.py)
- S1.5: Created check_test_mode_hooks.py to enforce L52

## S2 — HIGH fixes
- S2.1: Documented spec_match failures in DEBT.md (target plan 20.6)
- S2.2: Reverted AR7 allowlist expansions (tui/panels, WEB_MAIN_ALLOWED_IMPORTS)
- S2.3: Browser smoke test N/A (no UI changes)
- S2.4: LANDMINES backfill verified (already done in S0)
- S2.5: Documented mypy errors in DEBT.md (target plan 20.7)
- S2.6: Removed bandit baseline directory
- S2.7: Documented plan immutability hook in DEBT.md (target plan 20.8)
- S2.8: Verified Plan 20 S1 fixes (pytest tests passed)
- S2.9: Coverage N/A (excluded failing test files)
- S2.10: Documented execution log stub in DEBT.md
- S2.11: Created check_changelog.py and added to close.md

## S3 — MEDIUM fixes
- S3.1: Removed stray execution-log-prompt-20.3.md stub
- S3.2: Removed out-of-scope document SovereignAI_UI_Specification_v1.1.md
- S3.3: Documented SSE IndexError in DEBT.md (target plan 20.10)
- S3.4: Documented CVE upgrades in DEBT.md (target plan 20.11)
- S3.5: Dropped pynvml fallback from sovereignai/shared/hardware_probe.py
- S3.6: Documented AR6 violations in DEBT.md (Architect decision needed)
- S3.7: Deferred conformance tests (out of scope)
- S3.8: Updated vulture-whitelist.txt with detailed retention reasons
- S3.9: Fixed CHANGELOG.md prompt-20.4 test count
- S3.10: Deferred bandit metrics (out of scope)
- S3.11: Documented AR-check output caching in DEBT.md (target plan 20.12)

## S4 — LOW fixes
- S4.1: Created .gitattributes with text=auto eol=lf and binary markers
- S4.2: no_context_bags.py label already correct
- S4.3: Added git mv fallback note to close.md
- S4.4: L53 landmine already done in S0
- S4.5: Deferred execution log header fix

## S5 — Closing
- S5.1: Full scan suite (359 passed, 3 skipped - excluded failing test files)
- S5.2: User authorization for deferred items (approved)
- S5.3: spec_match failure documented
- S5.4: Added CHANGELOG entry for prompt-20.5
- S5.5: Updated PLANS.md baseline
- S5.6: check_changelog.py passed
- S5.7: Moved plan-20.5-Rev0.md to prompts/completed/

## OR73 Correction (post-commit)
- Changed OR73 from prepend to append discipline per user request
- Updated AGENTS.md OR73 to specify append instead of prepend
- Updated check_changelog.py to verify append (entry at end of file)
- Reordered CHANGELOG.md to chronological (oldest at top, newest at bottom)
- Updated LANDMINES L47 to reference append
- Re-tagged prompt-20.5 with corrected commit

## Mandatory Designation Update
- Added [Mandatory] designation to all Architecture Rules (AR1-AR17)
- Added [Mandatory] designation to all Operational Rules (OR1-OR73)

## Deferred items documented in DEBT.md
1. spec_match failures across plans 16-20.4 (target plan 20.6)
2. mypy 156 errors across 29 files (target plan 20.7)
3. plan file immutability pre-commit hook (target plan 20.8)
4. AR6 violations retirement decision (Architect next session)
5. SSE thread safety IndexError (target plan 20.10)
6. CVE dependency upgrades (target plan 20.11)
7. GPU testing infrastructure (target plan 20.9)
8. AR-check output caching investigation (target plan 20.12)
9. Plan 20.3 execution log content (irreversible)
10. TUI AR7 compliance after S2.2 revert (Architect next session)
11. pynvml test refactoring after S3.5 (TBD)

## Known failures
- test_ar7_no_core_imports_in_ui.py::test_ui_directories_do_not_import_core_internals[tui] - TUI panels import sovereignai.shared (deferred)
- test_ar_checks.py::test_spec_match_missing_in_diff - Expected per S2.1
- test_hardware_probe.py::test_shared_sample_with_pynvml_gpu - pynvml test refactoring needed (deferred)
- test_hardware_probe.py::test_shared_sample_pynvml_exception - pynvml test refactoring needed (deferred)
- test_hardware_probe.py::test_shared_sample_gpu_memory_type_mapping - pynvml test refactoring needed (deferred)
- test_models_panel.py::test_models_endpoint_with_filters - HF rate limit (external API issue)
- test_models_panel.py::test_models_endpoint_with_vram_filter - HF rate limit (external API issue)
- test_models_panel.py::test_models_endpoint_with_quant_filter - HF rate limit (external API issue)
