## prompt-17.2 — Fix Model Pull + Organize HF Catalog by Family

**Date**: 2026-06-30
**Plan file**: prompts/plan-17.2-Rev1.md

**Files changed**:
- web/main.py
- web/static/app.js
- web/static/styles.css
- sovereignai/shared/hf_catalog.py

**Results**:
- Tests: 303 passed, 32 failed, 10 skipped (pre-existing auth test failures)
- Ruff: 1 finding (pre-existing SIM105 in auth.py)
- Mypy: 4 findings (pre-existing in config_loader.py, main.py)
- Bandit: 0 findings
- Vulture: 0 findings
- Detect-secrets: pass

**Notes**:
- Fixed pull buttons to show error feedback via status polling
- Organized 45K HF models by family (Meta / Llama, Google / Gemma, etc.)
- Added pagination with "Load More" button (50 models per page)
