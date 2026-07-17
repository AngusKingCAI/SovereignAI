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

Run `/verify` workflow after every file edit. STOP on any failure.

1. If <file> is not `.py`: report "N/A — not Python" and exit.
2. Syntax check: `verify_syntax.py <file>`. STOP on error.
3. Ruff: `ruff check --fix <file>`. If still failing: STOP.
4. `git add prompts/*.md` — ensure all plan files tracked.
5. Report: `<file>: OK` or `<file>: FAIL`.
