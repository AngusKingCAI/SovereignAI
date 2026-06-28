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
