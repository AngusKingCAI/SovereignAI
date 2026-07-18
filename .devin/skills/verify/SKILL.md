---
name: verify
authority: AGENTS.md
description: Run after every file edit during plan execution. Python files only.
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

1. If <file> is not `.py`: report "N/A — not Python" and exit.
2. Syntax check: `verify_syntax.py <file>`. STOP on error.
3. Ruff: `ruff check --fix <file>`. If still failing: STOP.
4. Import path check: `.agent/executor/scripts/check_import_paths.py` (if <file> is in app/sovereignai/). STOP on error.
5. `git add prompts/*.md` — ensure all plan files tracked.
6. OR checks: `or_checks/run_all.py` (if exists).
7. Landmine checks: `landmine_checks/run_all.py` (if exists).
8. If new error pattern detected (same error message substring, same script failure, or same command syntax error appearing 2+ times): run suggest_rule.py, STOP for Architect review.
9. Report: `<file>: OK` or `<file>: FAIL`.

Note: Test execution moved to `/close` skill for scoped testing based on modified files.
