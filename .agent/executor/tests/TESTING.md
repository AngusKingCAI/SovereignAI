# Testing Best Practices

This document contains testing best practices for the SovereignAI executor workflow.

## Iterative Testing

Use `run_failing_tests.py` for faster iteration:
- First run: `run_failing_tests.py <test_path> --full` to establish baseline and cache failures
- On retry: `run_failing_tests.py <test_path>` to run only cached failing tests
- When cached run passes: cache auto-clears; next run without `--full` does full suite
- Final verification: `run_failing_tests.py <test_path> --full` to force full suite and confirm no regressions
- This reduces iteration time from 60s to <5s per fix

## Test Requirements

- Full suite is required at close for final verification - no exceptions
- Test failures should be fixed individually with targeted re-runs, not blanket full-suite retries
- Coverage ≥90% at `/close` - no exemptions

## Deterministic Test Ordering

Tests are sorted deterministically by module path, class name, and function name to prevent flaky tests caused by execution order dependencies. This is configured in `.agent/executor/tests/conftest.py` and ensures consistent test execution order across runs, making failures reproducible and easier to debug.

The conftest.py also provides:
- Automatic DI container isolation between tests
- Memory tracking during test execution
- Detection of order-dependent failures

## Test Organization

Tests are organized in the following structure:
- `.agent/executor/tests/` - Executor-specific tests
- `.agent/executor/tests/app_tests/` - SovereignAI application tests
- `.agent/executor/tests/sovereignai/` - SovereignAI integration tests
- `.agent/executor/tests/conformance/` - Adapter and skill conformance tests
- `.agent/executor/tests/contracts/` - Contract tests for interfaces
- `.agent/executor/tests/property/` - Property-based tests