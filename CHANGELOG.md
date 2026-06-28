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
