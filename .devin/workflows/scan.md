# /scan Workflow

Run at scan prompts (5, 10, 15, 20...). Whole-repo scan. No new features. Fixes only. If structural problem requires design decisions, STOP.

## Steps

1. Run `/close` steps 1-8 (tests, ruff, mypy full repo, bandit, pip-audit, vulture, detect-secrets, AR checks). Additionally run auto-discovered tools from `pyproject.toml`/`.pre-commit-config.yaml`. For each tool: if exit≠0, STOP that tool's check, fix it, then continue. Do NOT cascade — once a tool passes (or is fixed), proceed to next tool. After all tools pass, continue to steps 2-13 regardless of what was found.

2. Scan `LANDMINES.md` — propose rules for any landmine without corresponding OR. If new OR added: append to OR14 always-on subset if it targets an 18.x failure class; otherwise note in plan brief.

3. Scan `CHANGELOG.md` — verify every plan in completed batch has entry.

4. Scan `PLANS.md` — verify baselines current, queue reflects state. Update if stale.

5. Scan all source for references to removed/renamed modules. Fix mechanically.

5.5. **Cross-reference check**: Extract all `OR\d+` and `AR\d+` tokens from PLANS.md, DEBT.md, DECISIONS.md, AI_HANDOFF.md (excluding sections marked with historical disclaimers). Diff against rules defined in AGENTS.md. Any token not defined in AGENTS.md = STOP. Exempt: CHANGELOG.md (has disclaimer), PLANS.md "Completed Prompts" table rows (historical, has disclaimer). `DEFINED=$(grep -oE '^(OR|AR)[0-9]+' AGENTS.md | sort); CITED=$(grep -rohE '(OR|AR)[0-9]+' PLANS.md DEBT.md DECISIONS.md AI_HANDOFF.md | sort -u); comm -23 <(echo "$CITED") <(echo "$DEFINED")` — output must be empty (manual review to exclude historical-table entries before STOPping).

6. Full test suite: `.venv/Scripts/python.exe -m pytest tests/ -vvv`

7. Verify coverage: `.venv/Scripts/python.exe -m pytest tests/ --cov=. --cov-report=term 2>&1 | tail -n 10` — STOP if dropped >5% from baseline.

8. Audit against `principles.md` (14 core + workflow principles). STOP on violations — architectural fixes require regular plan + Round Table.

9. Audit against `principles.md` success criteria (if any defined). STOP on failures.

10. Review `DEBT.md` — check trigger conditions. Flag met triggers for next plan.

11. Audit open questions in `principles.md` — move resolved ones to "Resolved" with note.

12. Final summary:
    ```
    === SCAN COMPLETE (prompt-{N}) ===
    Tools: pytest {count} pass, ruff {count}, mypy {count}, bandit {count}, pip-audit {count} CVE, vulture {count}, AR checks {pass/fail}
    Fixes: {list}
    Vision: 14/14 pass / {count} violations
    Criteria: 40/40 pass / {count} failures
    DEBT: {count} reviewed, {count} flagged
    Open questions: {count} resolved, {count} remain
    ```

13. Close bash: `taskkill //F //IM bash.exe`
