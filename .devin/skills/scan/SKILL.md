---
name: scan
description: Run at scan prompts (5, 10, 15, 20...). Whole-repo scan. No new features. Fixes only.
argument-hint: "[plan-number]"
allowed-tools:
  - read
  - grep
  - glob
  - exec
  - edit
  - write
---

Run the /scan workflow for the current plan. Whole-repo scan. No new features. Fixes only. If structural problem requires design decisions, STOP.

## Steps

1. Run `/close` skill steps 1-8 (tests, ruff, mypy full repo, bandit, pip-audit, vulture, detect-secrets, AR checks). Additionally run auto-discovered tools from `pyproject.toml`/`.pre-commit-config.yaml`. For each tool: if exit≠0, STOP that tool's check, fix it, then continue. Do NOT cascade — once a tool passes (or is fixed), proceed to next tool. After all tools pass, continue to steps 2-13 regardless of what was found.

2. Scan `.agent/shared/LANDMINES.md` — propose rules for any landmine without corresponding OR. If new OR added: prepend to OR14 always-on subset if it targets an 18.x failure class; otherwise note in plan brief.

3. Scan `.agent/shared/CHANGELOG.md` — verify every plan in completed batch has entry.

4. Scan `.agent/executor/PLANS.md` — verify baselines current, queue reflects state. Update if stale.

5. Scan all source for references to removed/renamed modules. Fix mechanically. Search patterns: `grep -r 'from removed_module' --include='*.py' .` for each known removed module.

5.5. **Cross-reference check**: `.venv/Scripts/python.exe .agent/executor/scripts/check_rule_crossrefs.py` — STOP if exit≠0. Checks .agent/executor/PLANS.md, .agent/shared/DEBT.md, .agent/shared/DECISIONS.md, .agent/architect/AI_HANDOFF.md for undefined OR/AR citations. Excludes historical sections automatically.

6. Full test suite with 5-minute timeout: `.venv/Scripts/python.exe -m pytest .agent/executor/tests/ -q --tb=no 2>&1 | tail -20` — STOP on failure. Use 300000ms timeout (suite runtime ~183s, needs headroom). Per OR29, scan plans run full suite with summary-line isolation. Next read call: timeout 300000.

7. Verify coverage: `.venv/Scripts/python.exe -m pytest .agent/executor/tests/ --cov=. --cov-report=term 2>&1 | tail -n 10` — STOP if dropped >5% from baseline.

8. Audit against `.agent/architect/PRINCIPLES.md` (14 core + workflow principles). STOP on violations — architectural fixes require regular plan + Round Table.

9. Audit against `.agent/architect/PRINCIPLES.md` success criteria (if any defined). STOP on failures.

10. Review `.agent/shared/DEBT.md` — check trigger conditions. Flag met triggers for next plan.

11. Audit open questions in `.agent/architect/PRINCIPLES.md` — move resolved ones to "Resolved" with note.

12. Final summary:
   ```
   === SCAN COMPLETE (prompt-{N}) ===
   Tools: pytest {count} pass, ruff {count}, mypy {count}, bandit {count}, pip-audit {count} CVE, vulture {count}, AR checks {pass/fail}
   Fixes: {list}
   Vision: {principles count}/{total} pass / {count} violations
   Criteria: {criteria count}/{total} pass / {count} failures
   DEBT: {count} reviewed, {count} flagged
   Open questions: {count} resolved, {count} remain
   ```

13. Close bash: `taskkill //F //IM bash.exe`
