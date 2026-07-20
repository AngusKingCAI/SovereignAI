Depends on: plan-fix-6-Rev1
Vision principles: P3 (Reliability), P7 (Testability), P11 (Quality)
Open questions resolved: none

## S0 — Opening

S0.0: Clone latest repo. Verify plan-fix-6-Rev1 completed.
S0.1: Run `/open`
S0.2: Read `AGENTS.md` in full
S0.3: Check `.agent/shared/DEBT.md`
S0.4: Run `pytest .agent/executor/tests/ -v --tb=short -r s` — catalog all skipped tests with reasons

## F1 — Fix Missing File/Directory Skips (8 tests)

**Problem**: test_skill_manifest.py (5 skips) and test_skill_discovery.py (3 skips) skip because manifest/skills directories not found.

F1.1: Read `test_skill_manifest.py` — identify expected manifest file paths
F1.2: Create missing manifest fixture files or mock paths in test setup
F1.3: Read `test_skill_discovery.py` — identify expected skills directory
F1.4: Create mock skills directory structure or update test to use temp directory
F1.5: Run `pytest .agent/executor/tests/app_tests/test_skill_manifest.py .agent/executor/tests/app_tests/test_skill_discovery.py -v` — verify 0 skips

## F2 — Fix Script/Hardcoded Path Skips (4 tests)

**Problem**: test_ar_checks.py (2), test_check_rule_crossrefs.py (1), test_get_current_plan.py (1) skip due to hardcoded paths.

F2.1: Read `test_ar_checks.py` — identify hardcoded path assumptions
F2.2: Refactor tests to use `tmp_path` fixture or `monkeypatch` for path isolation
F2.3: Read `test_check_rule_crossrefs.py` — same approach
F2.4: Read `test_get_current_plan.py` — same approach
F2.5: Run `pytest .agent/executor/tests/test_ar_checks.py .agent/executor/tests/test_check_rule_crossrefs.py .agent/executor/tests/test_get_current_plan.py -v` — verify 0 skips

## F3 — Fix UI Not-Yet-Created Skips (3 tests)

**Problem**: test_ar7_no_core_imports_in_ui.py skips because Capability API and UI directories don't exist.

F3.1: Read `test_ar7_no_core_imports_in_ui.py` — identify expected UI paths
F3.2: Check if UI files now exist (they were created in earlier plans)
F3.3: If UI exists: remove skips, run tests. If UI still missing: document in DEBT.md as deferred
F3.4: Run `pytest .agent/executor/tests/test_ar7_no_core_imports_in_ui.py -v` — verify

## F4 — Fix Deferred/TODO Skips (3 tests)

**Problem**: test_p4_compliance.py skips because tests require temporary manifest/DEBT.md modifications.

F4.1: Read `test_p4_compliance.py` — identify what temporary modifications are needed
F4.2: Use `tmp_path` and file copying to create isolated test copies of manifest/DEBT.md
F4.3: Run modifications on temp copies, verify, no impact on real files
F4.4: Run `pytest .agent/executor/tests/app_tests/test_p4_compliance.py -v` — verify 0 skips

## F5 — Convert Environment-Dependent Skips to Conditional (34 tests)

**Problem**: 34 tests skip because they require external services (web stack, Ollama, HF API, LLaMA.cpp).

F5.1: Read all skipped environment-dependent tests:
  - test_options_panel.py (4)
  - test_web_ui_integration.py (4)
  - test_first_run_adapter_check.py (4)
  - test_hf_database.py (1)
  - test_ollama_service.py (2)
  - test_hardware_panel.py (5)
  - test_skills_api.py (3)
  - test_models_panel.py (5)
  - test_llama_cpp_adapter.py (1)
  - test_first_run.py (5)
F5.2: Replace `@pytest.mark.skip` with `pytest.skip` guards that check environment:
  ```python
  if not os.environ.get('SOVEREIGNAI_FULL_STACK_TESTS'):
      pytest.skip("Requires full stack — set SOVEREIGNAI_FULL_STACK_TESTS=1 to run")
  ```
F5.3: This converts "always skip" to "skip unless explicitly enabled" — tests can run in CI if env var set
F5.4: Run `pytest .agent/executor/tests/app_tests/ -v -r s` — verify skip count reduced

## F6 — Fix TODO Comments in test_ar_checks.py

F6.1: Read `.agent/executor/tests/test_ar_checks.py` — find TODO(prompt-20.7.1) comments
F6.2: Either implement the skipped tests or document why permanently deferred
F6.3: Remove outdated TODO references to old plan numbers
F6.4: Run `pytest .agent/executor/tests/test_ar_checks.py -v` — verify

## F7 — Fix Invalid Escape Sequences (Warnings)

F7.1: Search for invalid escape sequences: `grep -r '\\[bfnrtv]' --include='*.py' .agent/executor/tests/`
F7.2: Fix by using raw strings `r'...'` or double backslashes `\`
F7.3: Run `python -m compileall .agent/executor/tests/ -q` — verify no SyntaxWarning

## F8 — Regression Prevention

F8.1: Run full test suite: `pytest .agent/executor/tests/ -v --tb=short -r s`
F8.2: Target: 0 failures, minimize skips (only environment-dependent with clear env var guards)
F8.3: Document any tests that MUST remain skipped in test file docstrings with clear rationale

## Closing

Run `/close`
