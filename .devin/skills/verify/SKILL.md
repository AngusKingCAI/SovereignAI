---
name: verify
description: Run after every file edit during plan execution.
argument-hint: "[file-path]"
allowed-tools:
  - read
  - grep
  - glob
  - exec
  - edit
  - write
---

Run the /verify workflow after every file edit during plan execution.

## Steps

1. Syntax check edited file: `.venv/Scripts/python.exe scripts/verify_syntax.py <file>`. STOP on syntax error. Error format: `FAIL: <file>:<line>: <error>`. Fix before proceeding.

2. Ruff on edited file (Python only): `.venv/Scripts/ruff.exe check <file>` — if auto-fixable: `ruff check --fix <file>` and re-verify. If not: STOP.

3. `git add prompts/*.md` — ensure ALL plan files in prompts/ are added to git (tracked or untracked). This prevents treating untracked plan files as cleanup artifacts per L69. Do this on every verify to catch any intermediate pushes.

4. Report: `<file>: OK` or `<file>: FAIL`
