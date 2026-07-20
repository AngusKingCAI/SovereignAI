# LANDMINES.md — Executor Failure Patterns

Prepend within severity bucket (newest at top within each severity level). Each entry: pattern, detection, mitigation.

Naming: C{n} = Critical, H{n} = High, M{n} = Medium, L{n} = Low.

---

## Active Patterns

### Critical — Blocks delivery. Fix before Round Table (GR8).

| ID | Pattern | Detection | Mitigation |
|----|---------|-----------|------------|

### High — Blocks delivery. Fix before Round Table (GR8).

| ID | Pattern | Detection | Mitigation |
|----|---------|-----------|------------|
| H1 | Repeatedly restarting long-running commands instead of waiting | Multiple pytest/test invocations within short time window; "Stopped waiting for output" messages | Use background execution mode with timeout=300000 for first invocation; poll existing process identifier; read output truncation file if truncated |

### Medium — Address or document.

| ID | Pattern | Detection | Mitigation |
|----|---------|-----------|------------|
| M7 | AR check scripts with hardcoded relative paths break across CWDs | `run_all.py` failures with path-not-found errors referencing drive root (e.g., `C:\app\...`) | All AR check scripts MUST use `Path(__file__).parent` chain for repo-root-relative paths. Audit existing scripts and refactor any using `Path.cwd()` or bare relative paths. |
| M8 | Execution logs containing only headers (no body content) | `verify_close.py` line-count check on log files | Executor MUST paste full transcript. Empty/incomplete logs = STOP at `/close`. |
| M1 | Dual import paths break protocol isinstance | Files in app/sovereignai/ using app.sovereignai.* imports instead of sovereignai.* imports | All source files in app/sovereignai/ must use sovereignai.* imports (matches installed package name). Use .agent/executor/scripts/fix_import_paths.py script to standardize. Detection: .agent/executor/scripts/check_import_paths.py script. |
| M2 | AR4/discovery allowlists must be updated when new sovereignai.* UI imports added | test_ar4_no_core_imports_in_ui.py failures for new imports in app/web, app/tui, etc. | When adding new sovereignai.* imports to UI files, update WEB_MAIN_ALLOWED_IMPORTS and TUI_ALLOWED_IMPORTS in test_ar4_no_core_imports_in_ui.py |
| M3 | AR check ALLOWLIST must include all legitimate plan artifact paths | spec_match.py failures for valid plan files | Add new plan artifact paths (app/tui, app/web, pyproject.toml, etc.) to ALLOWLIST in scripts/ar_checks/spec_match.py |
| M4 | Test scope confusion between architect/executor and sovereignai tests | Running wrong test suite for changes made | Tests are now separated: .agent/executor/tests/ for architect/executor, .agent/executor/tests/app_tests/ for sovereignai. Use .agent/executor/scripts/get_scoped_tests.py to auto-detect correct scope based on git changes. |
| M5 | Environment-specific tests failing due to missing external dependencies | Tests requiring GPU, external services, or specific binaries failing | Per S7.4, use pytest.skip with clear condition descriptions for environment-specific tests, not pytest.mark.skip. |
| M6 | Namespace package collision — test directory shadows installed package | Test directory named after installed package (e.g., sovereignai/) creates namespace package that shadows app/sovereignai/, breaking isinstance() on all dataclasses/protocols | Never create test directory matching package name. Use non-conflicting names (e.g., app_tests instead of sovereignai). Update pyproject.toml testpaths accordingly. |

### Low — Architect discretion.

| ID | Pattern | Detection | Mitigation |
|----|---------|-----------|------------|

---

## Graduated Patterns

| ID | Pattern | Resolved By | Date |
|----|---------|-------------|------|

---

## Template

```markdown
## {C|H|M|L}{n} — <title>

**Pattern**: <what the Executor did wrong>
**Detection**: <how the Architect or script catches it>
**Mitigation**: <how to prevent recurrence>
```
