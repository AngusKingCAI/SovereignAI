---
name: verify
authority: AGENTS.md
description: Run after every file edit during plan execution. All supported file types.
argument-hint: "[file-path]"
triggers: ["user"]
allowed-tools:
  - read
  - grep
  - exec
  - edit
  - write
---

Operational Rules: See .agent/shared/OR_RULES.md
- Read UOR section (Universal) + VOR section (verify-specific)

Run `/verify` workflow after every file edit. STOP on any failure.

**FALLBACK**: If skill tool invocation fails, execute steps manually via exec tool with scripts.

1. Syntax check: `verify_syntax.py <file>`. STOP on error. (Supports: .py, .json, .toml, .yaml, .yml, .html, .htm, .css, .js)
2. If <file> is `.py`: Run ruff: `ruff check --fix <file>`. If still failing: STOP.
3. If <file> is `.py`: Import path check: `.agent/executor/scripts/check_import_paths.py` (if <file> is in app/sovereignai/). STOP on error.
4. OR checks: `or_checks/run_all.py` (if exists).
5. Landmine checks: `landmine_checks/run_all.py` (if exists).
6. Report: `<file>: OK` or `<file>: FAIL`.

Note: Test execution moved to `/close` skill for scoped testing based on modified files.
