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
3. Lightweight checks: `python .agent/executor/scripts/check_all_lightweight.py <file>`. STOP on error. (Combines syntax, import paths)
4. If <file> is `.py`: Run ruff: `ruff check --fix <file>`. If still failing: STOP.
5. If <file> is `.py`: Run mypy: `mypy <file>`. STOP on error.
6. OR checks: `or_checks/run_all.py` (if exists).
7. Landmine checks: `landmine_checks/run_all.py` (if exists).
8. **Trace log entry: Verify `.agent/executor/traces/trace-plan-{N}.jsonl` exists and can receive a new entry. The heavy deliverable audit is deferred to `/close`'s `verify_execution.py --final`. (UOR-4, lightweight check per VOR-1)**
9. **Append verification result to trace: `.agent/executor/traces/trace-plan-{N}.jsonl` with timestamp, phase, step, file, checks, result. (Invariant 12)**
10. **Manually run `.agent/executor/hooks/append_trace.py --skill verify --plan {N}` to log /verify invocation. (Invariant 12 — fallback if config.json hook fails)**
11. Report: `<file>: OK` or `<file>: FAIL`.

Note: Test execution moved to `/close` skill for scoped testing based on modified files.
