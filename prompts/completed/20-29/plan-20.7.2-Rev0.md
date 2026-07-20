# Plan 20.7.2 — AR-Check Scripts + Skills Integration

Depends on: prompt-20.7.1
Vision principles: P9 (trust boundary), P14 (audit everything)
Open questions resolved: none

## WILL edit
- `scripts/ar_checks/check_dependencies.py` — NEW, verifies imports match requirements.txt + pyproject.toml (S2)
- `scripts/ar_checks/check_plan_immutability.py` — NEW, verifies no plan files modified during execution (S2)
- `scripts/ar_checks/check_rule_conciseness.py` — NEW, verifies every AR/OR rule is <=2 lines / <=200 chars (S2)
- `.devin/skills/open/SKILL.md` — add dependency check + rule conciseness check + open-hash snapshot steps (S7)
- `.devin/skills/close/SKILL.md` — add dependency check + plan immutability check + rule conciseness check steps (S7)
- `AGENTS.md`, `AI_HANDOFF.md`, `LANDMINES.md`, `PLANS.md` — fix stale `.devin/workflows` → `.devin/skills` references (S7.3)
- `CHANGELOG.md` — append prompt-20.7.2 entry per OR73 (S9.3)
- `PLANS.md` — update baseline (S9.4)
- `prompts/plan-20.7.2-Rev0.md` — move to `completed/` (S9.5)
- `logs/execution-log-prompt-20.7.2.md` — NEW, structured S0-S9 summary + `[PASTE DEVIN CHAT HERE]` marker (S9.6)

## WILL NOT edit
- Any file not listed above. If scope expands, STOP per OR10.

## S0 — Opening

S0.1: Run `/open`. Read `AGENTS.md` in full.
S0.2: Re-read `LANDMINES.md`.
S0.3: Begin Phase 1.

## S2 — AR-check scripts

S2.1: Create `scripts/ar_checks/check_dependencies.py`. Functionality:
- Parse all `.py` files in `sovereignai/`, `databases/`, `services/`, `web/`, `tui/`, `adapters/`, `tests/`.
- Extract all `import` statements (including `from X import Y`).
- Parse `txt/requirements.txt` and `pyproject.toml [project.optional-dependencies] dev`.
- For each import, verify the package is in the correct file:
  - Production code (sovereignai/, databases/, services/, web/, tui/, adapters/): package must be in `txt/requirements.txt`.
  - Dev/test code (tests/): package must be in `pyproject.toml [project.optional-dependencies] dev` OR `txt/requirements.txt` (if used in production too).
- Stdlib exemptions: `os`, `sys`, `json`, `pathlib`, `threading`, `datetime`, `typing`, `dataclasses`, `collections`, `uuid`, `re`, `math`, `time`, `random`, `functools`, `itertools`, `contextlib`, `asyncio`, `concurrent.futures`.
- Exit 0 if all deps accounted for, exit 1 if any missing. Print missing deps with file location.

S2.2: Create `scripts/ar_checks/check_plan_immutability.py`. Functionality:
- Accept CLI arg: `--open-hash <git-hash>`.
- Run `git diff --name-only <open-hash> HEAD`.
- Filter for files matching `prompts/plan-*.md`.
- If any matches found, exit 1 with error message listing the modified plan files.
- Exit 0 if no plan files modified.

S2.3: Create `scripts/ar_checks/check_rule_conciseness.py`. Functionality:
- Parse `AGENTS.md`.
- For each AR/OR rule (lines matching `^AR\d+\. \[Mandatory\]` or `^OR\d+\. \[Mandatory\]`):
  - Count lines until next rule or end of file.
  - If >2 lines, exit 1 with rule number and line count.
  - Count characters after the rule number (including space after period). If >200 chars, exit 1 with rule number and char count.
- Exit 0 if all rules pass.

S2.4: Verify all three scripts are executable: `python scripts/ar_checks/check_dependencies.py`, `python scripts/ar_checks/check_plan_immutability.py --open-hash HEAD`, `python scripts/ar_checks/check_rule_conciseness.py`. Exit≠0 on any = STOP per OR77/OR78/OR80.

S2.5: Commit: `git add -A && git commit -m "feat: add check_dependencies.py, check_plan_immutability.py, check_rule_conciseness.py per OR77/OR78/OR80"`.

## S7 — Skills integration (.devin/skills/, NOT .devin/workflows/)

**Note**: The user switched from Cascade to Devin Local mid-P20.6. The `.devin/workflows/*.md` files were migrated to `.devin/skills/{open,close,scan,verify}/SKILL.md`. All S7 edits target the NEW `.devin/skills/` paths. Do NOT edit `.devin/workflows/` — it no longer exists. Verify with `ls .devin/skills/` before editing.

S7.1: Edit `.devin/skills/open/SKILL.md`. In the `## Pre-flight` section, add after step 4 (venv check): `4.5. Run python scripts/ar_checks/check_dependencies.py. Exit≠0 = STOP per OR77. If missing deps, add to txt/requirements.txt (production) or pyproject.toml [project.optional-dependencies] dev (dev/test), then run .venv/Scripts/pip.exe install -e .[dev] and re-run check.` Also add: `4.6. Run python scripts/ar_checks/check_rule_conciseness.py. Exit≠0 = STOP per OR80. Trim over-long rules per GR18 before proceeding.` Also add: `4.7. Snapshot open hash: echo $(git rev-parse HEAD) > .open_hash. Used by /close step 17.7 for plan immutability check.` Commit: `git add -A && git commit -m "feat: add dependency check + rule conciseness check + open-hash snapshot to /open skill"`.

S7.2: Edit `.devin/skills/close/SKILL.md`. After step 5 (pip-audit), add: `5.5. Invoke Snyk MCP scan on txt/requirements.txt + changed Python files. Document any new findings in DEBT.md with explicit target plan (not TBD — per OR64). Exit≠0 on CRITICAL/HIGH Snyk findings = STOP per OR81/L66.` Then after step 17.5 (check_changelog.py), add: `17.6. Run python scripts/ar_checks/check_dependencies.py. Exit≠0 = STOP per OR77.` Then: `17.7. Run python scripts/ar_checks/check_plan_immutability.py $(cat .open_hash). Exit≠0 = STOP per OR78. Plan files must not be edited during execution.` Then: `17.8. Run python scripts/ar_checks/check_rule_conciseness.py. Exit≠0 = STOP per OR80.` Then: `17.9. rm .open_hash`. Commit: `git add -A && git commit -m "feat: add Snyk scan + dependency check + plan immutability check + rule conciseness check to /close skill"`.

S7.3 (fix stale `.devin/workflows` references): Scan the repo for any remaining `.devin/workflows` references in non-historical files. Run: `grep -rn "\.devin/workflows" --include="*.md" --include="*.py" --include="*.toml" . | grep -v "prompts/completed/" | grep -v "logs/"`. For each match, update `.devin/workflows` → `.devin/skills` (and `workflows/open.md` → `skills/open/SKILL.md`, etc.). Key files to check: `AGENTS.md`, `AI_HANDOFF.md`, `LANDMINES.md`, `PLANS.md`, `scripts/ar_checks/spec_match.py` (allowlist already updated to `.devin/skills/` per L98 — verify), `scripts/ar_checks/check_tracing_allowlist.txt`. Historical files in `prompts/completed/` and `logs/` are exempt (append-only per OR46). Commit: `git add -A && git commit -m "docs: migrate .devin/workflows references to .devin/skills"`.

## S9 — Closing

S9.1: Re-read plan in full.
S9.2: Verify test suite passes: `pytest tests/ -vvv --no-cov -q`. If any test fails, investigate per OR18. Do NOT re-run without fix.
S9.3: Append prompt-20.7.2 entry to `CHANGELOG.md` per OR73. Verbatim text:
```
## prompt-20.7.2 — AR-Check Scripts + Skills Integration
**Date**: 2026-07-02
**Plan file**: prompts/plan-20.7.2-Rev0.md
**Tests**: <pytest output from S9.2>
**Coverage**: N/A (no new production code)
- Created check_dependencies.py, check_plan_immutability.py, check_rule_conciseness.py per OR77/OR78/OR80
- Updated /open and /close skills with dependency check, rule conciseness check, plan immutability check, Snyk scan
- Migrated .devin/workflows references to .devin/skills per P20.6-cascade
```
Commit: `git add -A && git commit -m "docs: append prompt-20.7.2 entry to CHANGELOG.md per OR73"`.

S9.4: Update `PLANS.md` baseline with new test count from S9.2.

S9.5: Move plan to completed: `git mv prompts/plan-20.7.2-Rev0.md prompts/completed/plan-20.7.2-Rev0.md`. Commit: `git add -A && git commit -m "docs: move plan-20.7.2-Rev0.md to completed/"`.

S9.6: Create `logs/execution-log-prompt-20.7.2.md` with:
- Header: `# Execution Log: prompt-20.7.2`
- Metadata: `**Plan**: prompts/plan-20.7.2-Rev0.md`, `**Date**: 2026-07-02`, `**Executor**: Devin`
- `## Devin Chat` section with `[PASTE DEVIN CHAT HERE]` marker
- Structured `## S0 — Opening` through `## S9 — Closing` summaries with task counts, deviations, and verbatim CHANGELOG echo per OR73

Commit: `git add -A && git commit -m "docs: create execution-log-prompt-20.7.2.md per OR75"`.

S9.7: Run `/close`. Verify step 17.5 (check_changelog.py 20.7.2), 17.6 (check_dependencies.py), 17.7 (check_plan_immutability.py), 17.8 (check_rule_conciseness.py) all pass.

S9.8: `git tag prompt-20.7.2` and `git push origin main --tags`. Do NOT force-push (L25/OR42/L55/L64).

---

## Notes for Devin

- **OR77 is the dependency-discipline rule** — every new import requires the package in the correct file (requirements.txt for production, pyproject.toml for dev/test). `check_dependencies.py` (S2.1) enforces at /open step 4.5 and /close step 17.6. After any requirements.txt change, run `pip install -e .[dev]`.
- **OR78 is the plan-immutability rule** — Devin must NOT edit `prompts/plan-N-RevM.md` files during execution. The only allowed edit is the move to `prompts/completed/` at /close step 17. `check_plan_immutability.py` (S2.2) enforces this mechanically at /close step 17.7.
- **OR80 is the rule-conciseness enforcement rule** — every AR/OR rule must be <=2 lines / <=200 chars. `check_rule_conciseness.py` (S2.4) enforces mechanically at /open step 4.6 and /close step 17.8.
- **OR81 is the MCP usage rule** — S7.2 wires Snyk into /close as step 5.5. Snyk MCP scan is invoked on txt/requirements.txt + changed Python files. Exit≠0 on CRITICAL/HIGH findings = STOP per OR81/L66.
