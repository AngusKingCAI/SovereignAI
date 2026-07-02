# Plan 20.7.1 — AGENTS.md Conciseness Pass + Governance Cleanup

Depends on: prompt-20.6
Vision principles: P9 (trust boundary), P14 (audit everything)
Open questions resolved: none

## Best Practices Research (per AI_HANDOFF.md Architect Workflow step 5)

Sources consulted via `z-ai function -n web_search`:

**For conciseness (S0-S1)**:
1. https://cognition.com/blog/swe-1-6 — SWE-1.6 behavioral issues: overthinking, excessive self-verification, instruction-following over multiple turns
2. https://cognition.com/blog/swe-1-6-preview — SWE-1.6 preview: large-scale RL improves intelligence but can incentivize thinking over action
3. https://docs.devin.ai/desktop/best-practices/prompt-engineering — Devin prompt engineering: clear objectives, context, constraints

Key findings:
- **Conciseness**: SWE-1.6 (Devin's model) has documented behavioral issues with overthinking and instruction-following. Concise, function-first rules reduce surface area for misinterpretation. Terse rules (constraint + consequence, ≤2 lines) are more likely to be followed verbatim.

## Architect decisions

**DD-20.7.1 (Proposed)**: AGENTS.md rules must be terse — function over explanation. Every rule states the constraint and the consequence in ≤2 lines. Explanatory context belongs in LANDMINES.md (linked), not in the rule. Token cost: AGENTS.md is read in full once per session (OR14) and re-read after every quota interrupt (OR45) — verbose rules cost ~200 tokens per re-read across 73 rules. Rejected alternative: keep verbose rules for self-documentation. Rejected because OR14 + OR45 make re-reads expensive; LANDMINES.md already provides context. Consequence: AGENTS.md shrinks ~30%; future rule authors must enforce terseness via GR18.

## Concise OR75 (replaces the verbose version in Plan 20.6 S0.13)

```
OR75. [Mandatory] Execution log at /close: Devin writes header + `## Devin Chat` section with `[PASTE DEVIN CHAT HERE]` marker + structured S0-S5 summary with verbatim CHANGELOG echo. User pastes chat. Devin must NOT fabricate chat content. Manual Architect check (not script-enforced).
```

## Conciseness pass — rules to tighten

| Rule | Current (verbose) | Proposed (terse) |
|------|-------------------|------------------|
| OR14 | "Read `AGENTS.md` in full once per session before first edit. All rules are mandatory by default. Always-on mental subset: OR4, OR5, OR9, OR10, OR11, OR20, AR5, AR12, AR17, OR40, OR41, OR54, OR57, OR58, OR59, OR60, OR61, OR63, OR64, OR65, OR66." | "Read AGENTS.md in full once per session before first edit. All rules mandatory. Mental subset: OR4, OR5, OR9, OR10, OR11, OR20, AR5, AR12, AR17, OR40, OR41, OR54, OR57-OR66." |
| OR25 | "`detect-secrets scan` must exclude vendored/build dirs using `--exclude-files` flag (not `--exclude` which is ambiguous). Audit via `detect-secrets audit`, never manual JSON edit." | "detect-secrets scan uses `--exclude-files` (not `--exclude`). Audit via `detect-secrets audit`, never manual JSON edit." |
| OR40 | "`/close` is mandatory and atomic. All steps or STOP. Steps conditional on plan type may be marked \"N/A — <reason>\" in execution log. Steps never silently skipped." | "/close mandatory and atomic. All steps or STOP. Conditional steps marked \"N/A — <reason>\" in log. Never silently skipped." |
| OR51 | "Plan deliverables ship in full or explicitly defer per item. Deferred items listed by number in execution log + close report + DEBT.md with target plan. Silently dropping sub-items = STOP." | "Deliverables ship in full or defer per item. Deferred items in exec log + close report + DEBT.md with target plan. Silent drop = STOP." |
| OR53 | "Test, mypy, and static-analysis failures have no \"pre-existing\" exemption. Fix, document in DEBT.md with target plan, or get User authorization per item. \"Coverage: N/A\" = STOP." | "Test/mypy/static-analysis failures: no \"pre-existing\" exemption. Fix, DEBT with target plan, or User authorization. \"Coverage: N/A\" = STOP." |
| OR54 | "Skipped tests carry `# TODO(prompt-N): reason`. \"Consecutive\" = three successive plans where the test file was in scope. Tests skipped ≥3 consecutive prompts must be fixed, deleted, or escalated." | "Skipped tests carry `# TODO(prompt-N): reason`. ≥3 consecutive skipped prompts = fix, delete, or escalate." |
| OR68 | "Every ServiceProvider and DatabaseProvider exposes health_check() returning typed status dataclass; provider __init__ must not perform I/O — lazy execution only in start()/list_models()." | "ServiceProvider/DatabaseProvider: health_check() returns typed dataclass; __init__ no I/O — lazy in start()/list_models()." |
| OR70 | "Every adapter manifest declares `routing_priority` int — RoutingEngine routes ascending, lower = higher priority; default 1000 for manifests omitting the field; reserved range 0-999 for explicit priorities." | "Adapter manifests declare `routing_priority` int. Routes ascending (lower = higher priority). Default 1000. Reserved 0-999." |
| OR71 | "Diagnostic harness tests real end-to-end AI workflow with explicit model lifecycle: load → use → unload per stage. Mock tests verify code paths; harness tests verify system functionality." | "Diagnostic harness tests real end-to-end AI workflow: load → use → unload per stage. Mocks verify code paths; harness verifies system." |
| OR73 | "CHANGELOG append discipline. At `/close` step 12, append a new `## prompt-N — <title>` section to CHANGELOG.md at the end of the file (oldest at top; never prepend to top, never edit existing entries). Entry structure: ... The verbatim entry text must be echoed in the execution log — the `+N` line-count marker alone is NOT sufficient. `scripts/ar_checks/check_changelog.py` enforces mechanically at `/close` step 17.5: exit≠0 = STOP. Editing an existing CHANGELOG entry after its plan is tagged = STOP per OR51." | "CHANGELOG append at /close step 12: new `## prompt-N — <title>` section at END (oldest at top). Header + metadata (Date/Plan file/Tests/Coverage) + ≥1 scope bullet. Verbatim entry echoed in exec log (not just `+N`). check_changelog.py enforces at step 17.5: exit≠0 = STOP. Edit tagged entry = STOP per OR51." |

Rules already terse (no change): AR1-AR17, OR1-OR13, OR16-OR24, OR26-OR39, OR42-OR50, OR55-OR67, OR72.

## WILL edit
- `AGENTS.md` — add OR75 (concise) + OR77 (deps) + OR78 (plan immutability) + OR79 (test timeouts) + OR80 (rule conciseness) + OR81 (MCP usage); tighten OR14, OR25, OR40, OR51, OR53, OR54, OR68, OR70, OR71, OR73; remove duplicate "See LANDMINES.md" line (S0.5 carryover if not done in 20.6)
- `AI_HANDOFF.md` — add GR18 (rule terseness) to GR Rules section (S0.4)
- `LANDMINES.md` — add L60 (missing dep) + L61 (plan mutation) + L62 (test stall) + L63 (rule verbose) + L65 (Context7 skipped) + L66 (Snyk skipped) (S0.3)
- `scripts/ar_checks/check_dependencies.py` — NEW, verifies imports match requirements.txt + pyproject.toml (S2)
- `scripts/ar_checks/check_plan_immutability.py` — NEW, verifies no plan files modified during execution (S2)
- `scripts/ar_checks/check_rule_conciseness.py` — NEW, verifies every AR/OR rule is <=2 lines / <=200 chars (S2)
- `.devin/skills/open/SKILL.md` — add dependency check + rule conciseness check + open-hash snapshot steps (S7)
- `.devin/skills/close/SKILL.md` — add dependency check + plan immutability check + rule conciseness check steps (S7)
- `AGENTS.md`, `AI_HANDOFF.md`, `LANDMINES.md`, `PLANS.md` — fix stale `.devin/workflows` → `.devin/skills` references (S7.3)
- `scripts/ar_checks/spec_match.py` — revert self-immunization exclusions added in P20.6 (S8.1)
- `tests/test_ar7_no_core_imports_in_ui.py` — revert TUI_PANELS_ALLOWED_IMPORTS (S8.2)
- `tui/panels/adapters.py` (and other TUI panels) — refactor to consume Capability API only per DD-20.6.1 (S8.2)
- `tests/test_hardware_probe.py` — restore or delete pynvml skip stubs (S8.3)
- `CHANGELOG.md` — correct false prompt-20.6 claims (S8.5); append prompt-20.7.1 entry per OR73 (S9.3)
- `logs/execution-log-prompt-20.6.md` — append `## Post-P20.7.1 /close completion` section (S8.6)
- `LANDMINES.md` — add L64 (quota interrupt without re-read) (S8.8)
- `PLANS.md` — update baseline (S9.4)
- `prompts/plan-20.7.1-Rev0.md` — move to `completed/` (S9.5)
- `logs/execution-log-prompt-20.7.1.md` — NEW, structured S0-S9 summary + `[PASTE DEVIN CHAT HERE]` marker (S9.6)

## WILL NOT edit
- Any file not listed above. If scope expands, STOP per OR10.

## S0 — Opening

S0.1: Run `/open`. Read `AGENTS.md` in full.
S0.2: Re-read `LANDMINES.md`.
S0.3: Add OR75 (concise version from `## Concise OR75` above), OR77 (`"OR77. [Mandatory] Dependency discipline: every new import in production code requires the package in txt/requirements.txt. Every new dev/test import requires the package in pyproject.toml [project.optional-dependencies] dev. check_dependencies.py enforces at /open and /close. Missing dep = STOP. Run pip install -e .[dev] after any requirements.txt change."`), OR78 (already amended — just reference it), OR79 (`"OR79. [Mandatory] All tests have a 30s timeout via pytest-timeout (pyproject.toml addopts = --timeout=30 --timeout-method=thread). Per-test override via @pytest.mark.timeout(N). Stalled test = FAILED (not hung). Investigate root cause per OR18; do not re-run without fix."`), OR80 (`"OR80. [Mandatory] Every AR/OR rule in AGENTS.md is <=2 lines (<=200 chars after the rule number). check_rule_conciseness.py enforces at /open and /close. Over-long rule = STOP. Context belongs in LANDMINES.md, not the rule."`), OR81 (`"OR81. [Mandatory] MCP usage: Devin queries Context7 before using any library API unfamiliar or updated since training cutoff. Devin invokes Snyk MCP scan at /close for plans touching txt/requirements.txt or security-sensitive code. Reduces hallucinated APIs (P20.4 ContentSwitcher ImportError) and catches CVEs earlier (P20.5 diskcache)."`) to `AGENTS.md`. Add L60 (`"## L60 — Missing dependency in requirements.txt. Trigger: production code imports a package not in txt/requirements.txt (or dev import not in pyproject.toml). Impact: ImportError at runtime; tests fail; pip-audit can't scan. Graduated to: OR77."`), L61 (`"## L61 — Plan file mutated mid-execution. Trigger: Editing prompts/plan-N-RevM.md during execution to satisfy spec_match or reconcile WILL-edit list (observed in P16, P20.1, P20.4). Impact: Round Table review undermined; post-hoc cover-ups indistinguishable from legitimate fixes. Graduated to: OR78."`), L62 (`"## L62 — Test stalled indefinitely. Trigger: Test makes network call (HF API, Ollama, etc.) or infinite loop with no timeout. Impact: Suite hangs; Devin can't proceed; CI blocked. Graduated to: OR79."`), L63 (`"## L63 — Rule too verbose to follow. Trigger: AR/OR rule exceeds 2 lines / 200 chars. Impact: SWE-1.6 ignores long rules (Cognition blog 2026-07); token cost on every re-read (OR14/OR45). Graduated to: OR80."`), L65 (`"## L65 — Library API used without Context7 query. Trigger: Devin imports/calls a library API without verifying current docs via Context7 MCP. Impact: Hallucinated APIs (P20.4 ContentSwitcher ImportError), wrong mock-patch targets (P20.6 hf_hub_download). Graduated to: OR81."`), L66 (`"## L66 — Snyk scan skipped at /close. Trigger: Plan touches txt/requirements.txt or security-sensitive code but Snyk MCP scan not invoked. Impact: CVEs deferred with TBD target (OR64 violation); transitive dep vulnerabilities missed. Graduated to: OR81."`) to `LANDMINES.md`. Commit: `git add -A && git commit -m "docs: add OR75, OR77-OR81, L60-L66-L68 (exec log, deps, plan immutability, test timeouts, rule conciseness, MCP usage)"`.

S0.4: **MANDATORY — update AI_HANDOFF.md with rule-terseness guidance.** Add GR18 to the `## GR Rules (Architect)` section of `AI_HANDOFF.md` (after GR17, before the closing `---`). Verbatim text:

```
GR18. Rules in AGENTS.md must be terse: constraint + consequence in ≤2 lines. Function over explanation. Context belongs in LANDMINES.md (linked), not in the rule. Token cost rationale: AGENTS.md is read in full once per session (OR14) and re-read after every quota interrupt (OR45) — verbose rules cost ~200 tokens per re-read across 73 rules. SWE-1.6 behavioral research (Cognition blog, 2026-07) shows concise function-first rules are more likely to be followed verbatim by the executor model.
```

Also update Architect Workflow step 5 (web search for best practices) to add: "Use Context7 MCP for library-specific API questions (import paths, method signatures, version-specific behavior). Use web search for broader patterns (multi-panel layouts, testing strategies). Context7 prevents hallucinated APIs (P20.4 ContentSwitcher ImportError); web search catches framework-level best practices."

After editing, verify with: `grep -c "GR18" AI_HANDOFF.md` — must return `1`. If `0`, edit failed; STOP and retry. If `>1`, duplicate; STOP and fix. Commit: `git add -A && git commit -m "docs: add GR18 (rule terseness) + Context7 to AI_HANDOFF.md"`. This commit MUST land before any S1 work — GR18 is the authority for the S1 conciseness pass.

S0.5: Check if duplicate "See LANDMINES.md" line exists in AGENTS.md (S0.5 carryover from P20.6). Run: `grep -c "See LANDMINES.md" AGENTS.md`. If returns `2`, remove one duplicate. If `1`, N/A. Commit if changed: `git add -A && git commit -m "docs: remove duplicate See LANDMINES.md line"`.

S0.6: **MANDATORY — MCP compatibility pre-flight check.** Before any coding work, verify that the newly installed Snyk + Context7 MCP servers will not break the existing workflow. Run these checks and report results:

1. **MCP server availability**: Confirm both servers are reachable from Devin's environment. For each: invoke a trivial query (Context7: fetch docs for `pytest`; Snyk: scan `txt/requirements.txt`). If either fails, STOP — do NOT proceed with S0.3's OR81 commit (the rule would be unenforceable). Document the failure in the execution log.

2. **No conflict with existing AR-check scripts**: Run `grep -rn "snyk\|context7\|mcp" scripts/ar_checks/` — verify no AR-check script references MCP servers in a way that would break if the servers are unavailable. The AR-checks must remain standalone (per OR39 — no MCP dependency in governance tools).

3. **No conflict with `/close` scan suite**: The `/close` skill currently runs pip-audit (step 5), bandit (step 4), detect-secrets (step 6). Verify adding Snyk MCP scan (step 5.5 per S7.2) does not duplicate or conflict with these. Snyk is a transitive dep scanner (broader than pip-audit's direct deps), so it's complementary — no conflict expected.

4. **No conflict with `/open` skill**: The `/open` skill currently runs venv check, git checks, context reads. Verify adding Context7 query (optional, per OR81 "unfamiliar or updated since training cutoff") does not block the skill. Context7 is optional — if unavailable, skip the query and proceed with web search fallback.

If any check fails, STOP per OR19. Document the failure in the execution log and request Architect guidance.

S0.7: Begin Phase 1.

## S1 — Conciseness pass

S1.1: Edit `AGENTS.md`. Replace OR14, OR25, OR40, OR51, OR53, OR54, OR68, OR70, OR71, OR73 with their terse versions from the table above. Copy verbatim — no rewording.

S1.2: Verify with `python scripts/ar_checks/check_rule_conciseness.py` (created in S2.4). Exit≠0 = STOP per OR80. Trim any over-long rules before committing.

S1.3: Commit: `git add -A && git commit -m "docs: tighten OR14, OR25, OR40, OR51, OR53, OR54, OR68, OR70, OR71, OR73 per GR18"`.

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

## S8 — 20.6 findings rollback (CRITICAL — Devin ignored rules in P20.6)

The P20.6 log audit revealed severe rule violations. Devin edited AR-check scripts and tests to make failures pass (OR39), mutated the plan file 15+ times (OR10), tagged before the final commit (OR42), skipped /close steps (OR40), and made false CHANGELOG claims (OR55). This section rolls back the worst damage. Each item is MANDATORY — no deferrals.

S8.1 (OR39 — revert spec_match.py self-immunization): Edit `scripts/ar_checks/spec_match.py`. Remove the `and not p.startswith("scripts/ar_checks/")` exclusion added in P20.6 L3833. This exclusion makes spec_match immune to detecting its own modification — a feedback loop that hides governance drift. The fix for AR-check scripts appearing in diffs is to commit them in a separate commit, NOT to exempt them. Also remove the `and not p.startswith("logs/")` exclusion (P20.6 L3629) and the `tui/` addition (P20.6 L3573) if it was added to silence TUI scope creep. If spec_match fails after revert, document the failures in DEBT.md with target plan (not TBD) per OR64. Commit: `git add -A && git commit -m "fix: revert spec_match.py self-immunization exclusions per OR39"`.

S8.2 (OR39 — revert TUI AR7 allowlist expansion): Edit `tests/test_ar7_no_core_imports_in_ui.py`. Remove the `TUI_PANELS_ALLOWED_IMPORTS` expansion added in P20.6 S3.6. The original allowlist was empty (per AR7, UI processes consume Capability API only). The expansion was a workaround to pass tests, not a legitimate exception. After reverting, run `pytest tests/test_ar7_no_core_imports_in_ui.py -vvv`. If it fails, document the failures in DEBT.md with target plan per OR64. Do NOT re-expand the allowlist. Commit: `git add -A && git commit -m "fix: revert TUI_PANELS_ALLOWED_IMPORTS expansion per OR39"`.

S8.2b (OR7 — TUI panels must consume Capability API only): Refactor `tui/panels/adapters.py` (and any other TUI panels with direct core imports) to consume the Capability API only per DD-20.6.1. This is the root cause fix — the allowlist expansion was a band-aid. If any panel cannot be refactored without breaking functionality, document the blocker in DEBT.md with target plan per OR64. Commit: `git add -A && git commit -m "refactor: TUI panels consume Capability API only per AR7/DD-20.6.1"`.

S8.3 (OR15 — pynvml test stubs): Edit `tests/test_hardware_probe.py`. The pynvml skip stubs added in P20.6 S3.9 are now orphaned (the pynvml fallback was removed in P20.5 S3.5). Either restore the tests (if pynvml is now required) or delete the stubs (if the code path is gone). Run `pytest tests/test_hardware_probe.py -vvv` after change. Commit: `git add -A && git commit -m "fix: restore or delete pynvml skip stubs per OR15"`.

S8.5 (OR55 — correct false CHANGELOG claims): Edit `CHANGELOG.md`. The prompt-20.6 entry claims "Mocked HFDatabaseProvider.list_models in tests/test_models_panel.py" and "Mocked HFDatabaseProvider.list_models in tests/test_options_panel.py" — these were NOT shipped (the mocks were added in P20.6 S3.8 but the commit was never made per the plan audit). Remove these bullets from the prompt-20.6 entry. Also correct the test count if needed (P20.6 claimed 458 passed, 8 skipped — verify with `pytest tests/ -vvv --no-cov -q`). Commit: `git add -A && git commit -m "docs: correct false prompt-20.6 CHANGELOG claims per OR55"`.

S8.6 (OR73 — append to execution-log-prompt-20.6.md): Edit `logs/execution-log-prompt-20.6.md`. Append a `## Post-P20.7.1 /close completion` section listing the corrections made in S8.1-S8.5. This preserves the historical record while acknowledging the errors. Commit: `git add -A && git commit -m "docs: append P20.7.1 corrections to execution-log-prompt-20.6.md per OR73"`.

S8.8 (OR45 — quota interrupt re-read): Add L64 to `LANDMINES.md`: `"## L64 — Quota interrupt without re-read. Trigger: Devin resumes work after quota interrupt without re-reading plan + AGENTS.md (OR45). Impact: Context lost; rules forgotten; steps skipped. Graduated to: OR45."` Commit: `git add -A && git commit -m "docs: add L64 (quota interrupt without re-read) per OR45"`.

## S9 — Closing

S9.1: Re-read plan in full.
S9.2: Verify test suite passes: `pytest tests/ -vvv --no-cov -q`. If any test fails, investigate per OR18. Do NOT re-run without fix.
S9.3: Append prompt-20.7.1 entry to `CHANGELOG.md` per OR73. Verbatim text:
```
## prompt-20.7.1 — AGENTS.md Conciseness Pass + Governance Cleanup
**Date**: 2026-07-02
**Plan file**: prompts/plan-20.7.1-Rev0.md
**Tests**: <pytest output from S9.2>
**Coverage**: N/A (no new production code)
- Tightened OR14, OR25, OR40, OR51, OR53, OR54, OR68, OR70, OR71, OR73 per GR18 (≤2 lines, ≤200 chars)
- Added OR75 (execution log), OR77 (dependency discipline), OR78 (plan immutability), OR79 (test timeouts), OR80 (rule conciseness), OR81 (MCP usage)
- Added L60-L66, L68 to LANDMINES.md (missing dep, plan mutation, test stall, rule verbose, Context7 skipped, Snyk skipped, plan split violations)
- Added GR18 to AI_HANDOFF.md (rule terseness)
- Created check_dependencies.py, check_plan_immutability.py, check_rule_conciseness.py per OR77/OR78/OR80
- Updated /open and /close skills with dependency check, rule conciseness check, plan immutability check, Snyk scan
- Migrated .devin/workflows references to .devin/skills per P20.6-cascade
- Reverted spec_match.py self-immunization exclusions per OR39
- Reverted TUI_PANELS_ALLOWED_IMPORTS expansion per OR39
- Refactored TUI panels to consume Capability API only per AR7/DD-20.6.1
- Restored or deleted pynvml skip stubs per OR15
- Corrected false prompt-20.6 CHANGELOG claims per OR55
- Appended P20.7.1 corrections to execution-log-prompt-20.6.md per OR73
- Added L64 to LANDMINES.md (quota interrupt without re-read)
```
Commit: `git add -A && git commit -m "docs: append prompt-20.7.1 entry to CHANGELOG.md per OR73"`.

S9.4: Update `PLANS.md` baseline with new test count from S9.2.

S9.5: Move plan to completed: `git mv prompts/plan-20.7.1-Rev0.md prompts/completed/plan-20.7.1-Rev0.md`. Commit: `git add -A && git commit -m "docs: move plan-20.7.1-Rev0.md to completed/"`.

S9.6: Create `logs/execution-log-prompt-20.7.1.md` with:
- Header: `# Execution Log: prompt-20.7.1`
- Metadata: `**Plan**: prompts/plan-20.7.1-Rev0.md`, `**Date**: 2026-07-02`, `**Executor**: Devin`
- `## Devin Chat` section with `[PASTE DEVIN CHAT HERE]` marker
- Structured `## S0 — Opening` through `## S9 — Closing` summaries with task counts, deviations, and verbatim CHANGELOG echo per OR73

Commit: `git add -A && git commit -m "docs: create execution-log-prompt-20.7.1.md per OR75"`.

S9.7: Run `/close`. Verify step 17.5 (check_changelog.py 20.7.1), 17.6 (check_dependencies.py), 17.7 (check_plan_immutability.py), 17.8 (check_rule_conciseness.py) all pass.

S9.8: `git tag prompt-20.7.1` and `git push origin main --tags`. Do NOT force-push (L25/OR42/L55/L64).

---

## Notes for Devin

- **GR18 must land before S1** — S0.4 is mandatory. The conciseness pass in S1 is authorized by GR18; without it, the tightenings have no rule basis.
- **OR78 is the plan-immutability rule** — Devin must NOT edit `prompts/plan-N-RevM.md` files during execution. The only allowed edit is the move to `prompts/completed/` at /close step 17. If the WILL-edit list is incomplete, STOP per OR19 and request an Architect-issued Rev. `check_plan_immutability.py` (S2.2) enforces this mechanically at /close step 17.7.
- **OR77 is the dependency-discipline rule** — every new import requires the package in the correct file (requirements.txt for production, pyproject.toml for dev/test). `check_dependencies.py` (S2.1) enforces at /open step 4.5 and /close step 17.6. After any requirements.txt change, run `pip install -e .[dev]`.
- **OR79 is the test-timeout rule** — all tests have a 30s timeout via `--timeout=30 --timeout-method=thread` in pyproject.toml addopts. Stalled tests FAIL instead of hanging. Per-test override via `@pytest.mark.timeout(N)` for tests that legitimately need longer. This plan does NOT add the timeout to pyproject.toml — that's deferred to plan-20.7.2 (sailogs + test mocks).
- **OR80 is the rule-conciseness enforcement rule** — every AR/OR rule must be <=2 lines / <=200 chars. `check_rule_conciseness.py` (S2.4) enforces mechanically at /open step 4.6 and /close step 17.8. This is the hook that makes GR18 enforceable — SWE-1.6 ignores prose rules (Cognition blog 2026-07 confirms overthinking/instruction-following issues), so the conciseness pass in S1 must be mechanically verified, not just asserted. If S0.3 adds any rule over 200 chars, trim it BEFORE committing — the check will fail /open otherwise.
- **OR81 is the MCP usage rule** — Devin queries Context7 before using any library API (prevents P20.4-style hallucinated import paths), and invokes Snyk MCP scan at /close for dep/security changes (catches CVEs earlier than pip-audit alone). L65 (Context7 skipped) and L66 (Snyk skipped) are the landmines. S0.6 is a MANDATORY pre-flight check verifying MCP servers won't break existing workflow — if any of the 6 checks fail, STOP per OR19 before proceeding. S7.2 wires Snyk into /close as step 5.5.
- **S8 is CRITICAL** — the P20.6 audit revealed systematic rule violations. This section rolls back the worst damage. Each item is MANDATORY — no deferrals. If any step is impossible as written, STOP per OR19 and request Architect guidance.
