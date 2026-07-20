---
name: verify
authority: AGENTS.md
description: Run after every step during plan execution, not just file edits. All supported file types.
argument-hint: "[file-path]"
triggers: ["user", "model"]
allowed-tools:
  - read
  - grep
  - exec
  - edit
  - write
---

Operational Rules: See .agent/executor/OR_RULES.md
- Read UOR section (Universal: UOR-1, UOR-2, UOR-3, UOR-4, UOR-5, UOR-6) + VOR section (verify-specific)

Run `/verify` workflow after every step, not just file edits. STOP on any failure.

1. **Manually run `.agent/executor/hooks/check_manifest.py --file <file> --plan {N}` before editing. (UOR-5, Invariant 7 — fallback if config.json hook fails)**
2. **Manually run `.agent/executor/hooks/append_trace.py --action file_edit --file <file> --plan {N}` after file modification. (Invariant 12 — fallback if config.json hook fails)**
3. Syntax check: `verify_syntax.py <file>`. STOP on error. (Supports: .py, .json, .toml, .yaml, .yml, .html, .htm, .css, .js)
4. If <file> is `.py`: Run ruff: `ruff check --fix <file>`. If still failing: STOP.
5. If <file> is `.py`: Import path check: `.agent/executor/scripts/check_import_paths.py` (if <file> is in app/sovereignai/). STOP on error.
6. If <file> is `.py`: Run mypy: `mypy <file>`. STOP on error.
7. OR checks: `or_checks/run_all.py` (if exists).
8. Landmine checks: `landmine_checks/run_all.py` (if exists).
9. **Phase gate check: Run `python .agent/executor/scripts/verify_execution.py --phase-gate <plan_id>` to verify deliverables against manifest. If any deliverable missing or check fails: STOP. (UOR-4)**
10. **Append verification result to trace: `.agent/executor/traces/trace-plan-{N}.jsonl` with timestamp, phase, step, file, checks, result. (Invariant 12)**
11. **Manually run `.agent/executor/hooks/append_trace.py --skill verify --plan {N}` to log /verify invocation. (Invariant 12 — fallback if config.json hook fails)**
12. Report: `<file>: OK` or `<file>: FAIL`.

Note: Test execution moved to `/close` skill for scoped testing based on modified files.
