# LANDMINES.md — Executor Failure Patterns

Prepend-only (newest at top). Each entry: pattern, detection, mitigation.

Naming: C{n} = Critical, H{n} = High, M{n} = Medium, L{n} = Low.

---

## Active Patterns

### Critical — Blocks delivery. Fix before Round Table (GR8).

| ID | Pattern | Detection | Mitigation |
|----|---------|-----------|------------|

### High — Blocks delivery. Fix before Round Table (GR8).

| ID | Pattern | Detection | Mitigation |
|----|---------|-----------|------------|
| H1 | Repeatedly restarting long-running commands instead of waiting | Multiple pytest/test invocations within short time window; "Stopped waiting for output" messages | Use run_in_background=true with timeout=300000 for first invocation; poll existing shell_id; read overflow file if truncated |

### Medium — Address or document.

| ID | Pattern | Detection | Mitigation |
|----|---------|-----------|------------|
| M1 | Dual import paths break protocol isinstance | Files in app/sovereignai/ using app.sovereignai.* imports instead of sovereignai.* imports | All source files in app/sovereignai/ must use sovereignai.* imports (matches installed package name). Use fix_import_paths.py script to standardize. Detection: check_import_paths.py script. |
| M2 | AR7/discovery allowlists must be updated when new sovereignai.* UI imports added | test_ar7_no_core_imports_in_ui.py failures for new imports in app/web, app/tui, etc. | When adding new sovereignai.* imports to UI files, update WEB_MAIN_ALLOWED_IMPORTS and TUI_ALLOWED_IMPORTS in test_ar7_no_core_imports_in_ui.py |
| M3 | AR check ALLOWLIST must include all legitimate plan artifact paths | spec_match.py failures for valid plan files | Add new plan artifact paths (app/tui, app/web, pyproject.toml, etc.) to ALLOWLIST in scripts/ar_checks/spec_match.py |
| M4 | Test scope confusion between architect/executor and sovereignai tests | Running wrong test suite for changes made | Tests are now separated: .agent/executor/tests/ for architect/executor, .agent/executor/tests/sovereignai/ for sovereignai. Use get_scoped_tests.py to auto-detect correct scope based on git changes. |
| M5 | Environment-specific tests failing due to missing external dependencies | Tests requiring GPU, external services, or specific binaries failing | Per S7.4, use pytest.skip with clear condition descriptions for environment-specific tests, not pytest.mark.skip.

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
