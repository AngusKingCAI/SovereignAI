# CHANGELOG — SovereignAI

Chronological change log. Append-only. Oldest entry at top, newest at bottom.

---

## prompt-0 — Bootstrap: Governance docs and infrastructure

**Date**: 2026-06-28
**Plan file**: prompts/plan-0-Rev3.md

**Files changed**:
- AGENTS.md (added OR39)
- .devin/workflows/open.md (fixed master -> main)
- documents/project-vision-Rev5.md (fixed title + revision history — metadata only)
- PLANS.md (state update: prompt-0 complete, Plan 1 active)
- README.md (new, minimal)
- .gitignore (new)
- CHANGELOG.md (new)
- LANDMINES.md (new)
- DECISIONS.md (new)
- DEBT.md (new)
- pyproject.toml (new)
- txt/requirements.txt (new, empty with header comment)
- .pre-commit-config.yaml (new)
- txt/vulture-whitelist.txt (new, empty)
- txt/.secrets.baseline (new, generated)
- Directory structure: sovereignai/ + UI peers + adapters/external + skills/user + skills/external

**Results**:
- Tests: N/A (no code)
- Ruff: N/A (no Python code yet)
- Mypy: N/A (no Python code yet)
- Bandit: N/A (no Python code yet)
- pip-audit: 0 CVEs (scanned txt/requirements.txt only — empty file, no runtime deps)
- Vulture: N/A (no Python code yet)
- Detect-secrets: pass (baseline established and audited)

**Notes**:
- Bootstrap commit establishing 12-document governance set + infrastructure scaffolding.
- No code, no tests. Architecture and process documentation only.
- AR4's `dependency-injector` reference recorded in DECISIONS.md D2 as pending separate debate.
- Rev5 title fixed (was byte-identical to Rev4).

## prompt-0.1 — Post-execution cleanup

**Date**: 2026-06-28
**Plan file**: prompts/plan-0.1-Rev1.md

**Files changed**:
- AGENTS.md (added OR40, OR41, OR42, OR43; updated landmine-to-rule table with L24–L27)
- .devin/workflows/close.md (fixed core/ -> sovereignai/ in step 8; added "mandatory even for docs-only plans" note to step 21; added N/A handling note to Steps header)
- LANDMINES.md (appended L24, L25, L26, L27; updated header to reflect new range)
- PLANS.md (fixed plan-1 file reference: plan-1-Rev1.md -> plan-1.md; state update)
- prompts/plan-0-Rev2.md (deleted)
- prompts/plan-0-Rev3.md (renamed to prompts/plan-0.md)
- prompts/plan-0-brief.md (deleted — Round Table review complete, brief not preserved in repo)

**Results**:
- Tests: N/A (no code)
- Ruff: N/A (no Python code)
- Mypy: N/A (no Python code)
- Bandit: N/A (no Python code)
- pip-audit: 0 CVEs (txt/requirements.txt unchanged from prompt-0 — still empty)
- Vulture: N/A (no Python code)
- Detect-secrets: pass (baseline unchanged from prompt-0)

**Notes**:
- Mechanical cleanup plan addressing issues discovered during Plan 0 execution.
- 4 new OR rules (OR40–OR43) capture shell/tooling workarounds observed in Git Bash on Windows.
- 4 new landmines (L24–L27) record the specific failure patterns from Plan 0.
- Workflow file fixes: /close step 8 references sovereignai/ instead of core/; /close step 21 and Steps header clarify N/A handling.
- Repo hygiene: prompts/ directory now contains only prompts/plan-0.md (canonical name per AI_HANDOFF.md).
- No Round Table review (scan-prompt exemption per AI_HANDOFF.md).

## prompt-0.2 — Environment + doc drift cleanup

**Date**: 2026-06-28
**Plan file**: prompts/plan-0.2-Rev1.md

**Files changed**:
- AGENTS.md (added OR44, OR45; updated landmine-to-rule table with L28, L29)
- .devin/workflows/open.md (added venv activation step 3 per OR45; fixed master->main in step 2 if still present)
- .devin/workflows/close.md (added venv prerequisite note to Steps section)
- pyproject.toml (fixed ruff config: [tool.ruff.pydocstyle] -> [tool.ruff.lint.pydocstyle])
- PLANS.md (fixed landmine range in cross-references; fixed baseline notes wording; updated date)
- LANDMINES.md (appended L28, L29; updated header; updated process section header)
- .venv/ (created — gitignored, not committed)

**Results**:
- Tests: N/A (no code, no tests/test_*.py files)
- Ruff: 0 errors (deprecation warning resolved)
- Mypy: N/A (no Python code)
- Bandit: 0 findings
- pip-audit: 0 CVEs (txt/requirements.txt still empty)
- Vulture: N/A (no Python code)
- Detect-secrets: pass (baseline unchanged)

**Notes**:
- Mechanical cleanup plan addressing issues discovered during prompt-0.1 execution.
- 2 new OR rules: OR44 (workflow files are structured markdown — OR7 applies), OR45 (project-local venv at .venv/ is canonical Python environment).
- 2 new landmines: L28 (sed on workflow files), L29 (python/pip PATH mismatch).
- Environment fix: created .venv/ via `py -3.11 -m venv .venv`, installed dev deps via `pip install -e .[dev]`. Verified `python -m pytest --version` works (no more "No module named pytest").
- Ruff config fix: moved [tool.ruff.pydocstyle] to [tool.ruff.lint.pydocstyle] per ruff deprecation warning.
- PLANS.md doc drift fix: landmine range updated to reflect L24-L29; baseline notes wording clarified.
- No Round Table review (scan-prompt exemption per AI_HANDOFF.md).

## prompt-0.3 — Venv path + workflow file cleanup

**Date**: 2026-06-28
**Plan file**: prompts/plan-0.3-Rev1.md

**Files changed**:
- AGENTS.md (added OR46; revised OR45 to reference OR46; updated landmine-to-rule table with L30)
- .devin/workflows/open.md (added step 3: venv verification + creation if missing; renumbered subsequent steps)
- .devin/workflows/verify.md (updated python and ruff commands to use .venv/Scripts/ absolute paths)
- .devin/workflows/close.md (added venv prerequisite note; updated steps 1-7 to use .venv/Scripts/ absolute paths; fixed step 5 pip-audit to use --requirement per OR39)
- .devin/workflows/scan.md (updated steps 1, 6, 7 to use .venv/Scripts/ absolute paths)
- LANDMINES.md (appended L30; updated header; updated process section header)

**Results**:
- Tests: N/A (no code, no tests/test_*.py files)
- Ruff: 0 errors
- Mypy: N/A (no Python code)
- Bandit: 0 findings
- pip-audit: 0 CVEs (txt/requirements.txt still empty)
- Vulture: N/A (no Python code)
- Detect-secrets: pass (baseline unchanged)

**Notes**:
- Mechanical cleanup plan addressing issues discovered during prompt-0.2 execution.
- 1 new OR rule: OR46 (workflow commands use absolute venv paths, not source activate).
- 1 new landmine: L30 (source activate does not persist in Git Bash on Windows).
- Workflow files: all 4 (.devin/workflows/open.md, verify.md, close.md, scan.md) updated to use .venv/Scripts/python.exe, .venv/Scripts/ruff.exe, etc. instead of relying on PATH.
- /close step 5 fix: pip-audit now uses --requirement txt/requirements.txt per OR39 (was previously environment scan — residual issue from prompt-0.2).
- /open step 3 added: verifies .venv/ exists, creates it if missing.
- No prompts/ files deleted — Rev-suffixed plan files (plan-0.1-Rev1.md, plan-0.2-Rev1.md) are kept per AI_HANDOFF.md line 96 ("All Revs are kept forever — no deletion. The prompts/ directory accumulates the full history.").
- Observation (no action): prompts/plan-0.md lacks Rev suffix while plan-0.1-Rev1.md and plan-0.2-Rev1.md have suffixes. Handoff has internally conflicting guidance (line 58 says Rev suffix; line 108 says strip suffix on copy). User should decide which interpretation is canonical before Plan 1 starts.
- No Round Table review (scan-prompt exemption per AI_HANDOFF.md).

## prompt-0.4 — Mypy filtering + kill bash at start

**Date**: 2026-06-28
**Plan file**: prompts/plan-0.4-Rev1.md

**Files changed**:
- AGENTS.md (added OR47; updated landmine-to-rule table with L31)
- .devin/workflows/open.md (added step 1: kill orphaned bash.exe processes from previous sessions; renumbered subsequent steps 2-8)
- .devin/workflows/close.md (updated step 3: mypy filters to .py files only per OR47; updated step 21: stronger mandatory language with STOP CONDITION)
- LANDMINES.md (appended L31; updated header; updated process section header)

**Results**:
- Tests: N/A (no code, no tests/test_*.py files)
- Ruff: 0 errors
- Mypy: N/A (no .py files edited this plan — per OR47, mypy is not invoked on markdown files)
- Bandit: 0 findings
- pip-audit: 0 CVEs (txt/requirements.txt still empty)
- Vulture: N/A (no Python code)
- Detect-secrets: pass (baseline unchanged)

**Notes**:
- Mechanical cleanup plan addressing issues discovered during prompt-0.3 execution.
- 1 new OR rule: OR47 (mypy is invoked on .py files only — never markdown or other non-Python files).
- 1 new landmine: L31 (mypy fails when passed markdown files).
- /open workflow: added step 1 (kill orphaned bash.exe from previous sessions). Subsequent steps renumbered 2-8. Kill bash at start cleans orphans from crashed/interrupted previous sessions; kill bash at /close step 21 cleans current session. Both are mandatory.
- /close step 3 fix: mypy now filters edited files to .py only via `git diff --name-only HEAD~1 | grep '\.py$'`. If no .py files were edited, mypy is N/A.
- /close step 21 fix: stronger language — "STOP CONDITION: the plan is NOT complete until this step executes. Do not report 'Plan X Complete' until step 21 has run."
- No Round Table review (scan-prompt exemption per AI_HANDOFF.md).
## prompt-1 — Core scaffold (Event Bus, TraceEmitter, DI container, types, Composition Root)

**Date**: 2026-06-28
**Plan file**: prompts/plan-1-Rev3.md

**Files changed**:
- txt/requirements.txt (NO change in Rev2 — dependency-injector removed per Finding 5; remains empty)
- sovereignai/shared/__init__.py (new — marks shared/ as package)
- sovereignai/shared/types.py (new — frozen dataclasses: TraceLevel, TraceEvent, Channel, Event, ComponentId, helpers)
- sovereignai/shared/event_bus.py (new — in-order per channel, no silent failures per P10; imports TraceEmitter from trace_emitter.py per Finding 1)
- sovereignai/shared/trace_emitter.py (new — singleton observability surface, NOT a context bag per AR6; correlation_id typed per Finding 4)
- sovereignai/shared/container.py (new — passive typed DI registry, no auto-wiring per A8; thread-safe via Lock per Finding 3)
- sovereignai/main.py (new — incremental Composition Root, wires Plan 1 components only per A3; smoke test uses TraceLevel.INFO per Finding 2)
- tests/test_event_bus.py (new — 6 tests: ordering, fault isolation, channel isolation)
- tests/test_trace_emitter.py (new — 6 tests: emit, filter, bounded, thread-safe)
- tests/test_di_container.py (new — 5 tests: singleton, factory, precedence, missing; +1 thread-safety test per Finding 3 = 6 tests)
- tests/test_composition_root.py (new — 5 tests: populated, singleton retrieval, wiring, smoke)
- DEBT.md (add AR4 amendment deferral per Finding 5)
- PLANS.md (set test + static analysis baselines)

**Results**:
- Tests: 23 passed (6 event_bus + 6 trace_emitter + 6 di_container + 5 composition_root)
- Ruff: 0 errors
- Mypy: 0 errors (file-scoped per OR2 — 5 source files checked with --explicit-package-bases)
- Bandit: 49 Low (B101: assert_used) — all test assertions, expected
- pip-audit: 0 CVEs (txt/requirements.txt remains empty — no runtime deps per Rev2 Finding 5)
- Vulture: 0 findings (high-confidence ≥80)
- Detect-secrets: pass (baseline unchanged from prompt-0)

**Notes**:
- First code plan — established core scaffold for Plans 2–4 to build on.
- All Round Table Rev2 findings addressed (Finding 1: EventBus import fix; Finding 2: main.py smoke test TraceLevel.INFO; Finding 3: DIContainer thread-safety via Lock; Finding 4: TraceEmitter correlation_id typed; Finding 5: dependency-injector removed, DEBT entry added).
- Test baseline established at 22 tests exactly as planned.
- Static analysis baselines established for all tools.
- Q9 (test strategy) and Q32 (DEBT format) resolved.
