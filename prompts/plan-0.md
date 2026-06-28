# Plan 0 — Prompt-0 Remediation (Bootstrap Fix-Up)

**Special plan**: Pre-Plan 1 cleanup. Fixes the incomplete prompt-0 bootstrap state so Plans 1–4 can proceed cleanly.

Depends on: none
Vision principles: 1 (sacred core), 2 (pluggable), 5 (wire as you go), 7 (modular core)
Open questions resolved: Q32 (debt register format — DEBT.md scaffold)

---

## S0 — Opening

**S0.1** — Run `/open` workflow from `.windsurf/workflows/open.md`. Skip previous tag verification (Plan 0).

**S0.2** — Read `AGENTS.md` in full.

**S0.3** — No new rules this plan. Proceed.

---

## S1 — Fix Path Discrepancy: `.devin/` → `.windsurf/`

**Problem**: Workflows live in `.devin/workflows/` but `AI_HANDOFF.md` and `PLANS.md` reference `.windsurf/workflows/`.

**Fix**:
1. Create `.windsurf/workflows/` directory
2. Move all files from `.devin/workflows/` to `.windsurf/workflows/`
3. Delete `.devin/` directory
4. Edit `AI_HANDOFF.md`: replace `.devin/workflows` with `.windsurf/workflows`
5. Edit `PLANS.md`: replace `.devin/workflows` with `.windsurf/workflows`

After each edit, run `/verify`.

---

## S2 — Fix Branch Name: `master` → `main`

**Problem**: `.windsurf/workflows/open.md` and `close.md` reference `master` branch, but actual default branch is `main`.

**Fix**:
- In `.windsurf/workflows/open.md` line 14: change `master` to `main`
- In `.windsurf/workflows/close.md` line 143: change `master` to `main`

After each edit, run `/verify`.

---

## S3 — Create Missing Governance Documents

Create 4 files. Content for each is provided below.

### S3.1 — `CHANGELOG.md`

```markdown
# CHANGELOG — SovereignAI

Chronological change log. Append-only. Oldest entry at top, newest at bottom.

---

## prompt-0 — Bootstrap: Governance docs

**Date**: 2026-06-28
**Plan file**: N/A (bootstrap)

**Files changed**:
- AI_HANDOFF.md
- AGENTS.md
- PLANS.md
- project-vision-Rev5.md
- .windsurf/workflows/open.md
- .windsurf/workflows/verify.md
- .windsurf/workflows/close.md
- .windsurf/workflows/scan.md

**Results**:
- Tests: N/A (no code)
- Ruff: N/A
- Mypy: N/A
- Bandit: N/A
- Vulture: N/A
- Detect-secrets: N/A

**Notes**:
- Initial bootstrap commit containing 12 governance documents.
- No code. No tests. Architecture and process documentation only.
```

### S3.2 — `LANDMINES.md`

```markdown
# LANDMINES.md — SovereignAI Failure Patterns

Append-only. L1–L23 inherited from sovereign-ai (predecessor project). New landmines start at L24.

## L1 — replace_all corrupts adjacent lines
**Trigger**: Plan 1, S2, using `replace_all` on `AGENTS.md` to update a rule number.
**Impact**: `AGENTS.md` became structurally invalid. Required manual restoration from git.

## L2 — Parallel scan tools corrupt output streams
**Trigger**: Plan 2, `/close` step 3, running `ruff check . & mypy . & bandit -r . &` in parallel.
**Impact**: Output streams interleaved. Required re-running all tools sequentially.

## L3 — PowerShell -replace corrupts structured markdown
**Trigger**: Plan 3, S4, using PowerShell `Set-Content` with `-replace` to edit `PLANS.md`.
**Impact**: Markdown table formatting destroyed. Required manual reconstruction.

## L4 — Temp files left in repo root get committed
**Trigger**: Plan 4, `/close` step 9, writing temp file to repo root instead of dedicated temp directory.
**Impact**: Temp file committed to repo. Required follow-up commit to remove.

## L5 — Vulture flags unused test fixtures incorrectly
**Trigger**: Plan 2, `/close` step 6, vulture reported `fixture_param` as unused in test file.
**Impact**: False positive. Parameter was required by pytest's parametrize decorator.

## L6 — Naive/aware datetime mixing
**Trigger**: Plan 3, S2, using `datetime.utcnow()` in event timestamp.
**Impact**: Type error when comparing with `datetime.now(timezone.utc)`. Mypy flagged the mismatch.

## L7 — Stale baselines propagate through plans
**Trigger**: Plan 4, `/open` step, test count differed from `PLANS.md` baseline but was not updated.
**Impact**: Baseline drift. Plan 5 started with wrong expected test count, causing false STOP.

## L8 — Scope drift: editing files outside declared scope
**Trigger**: Plan 3, S3, discovered unrelated file needed fix and edited it without STOP.
**Impact**: Unplanned changes in commit. Difficult to trace which plan produced which change.

## L9 — Interface changes break existing tests during type remediation
**Trigger**: Plan 4, S2, fixing mypy type error required changing function signature. Broke 3 existing tests.
**Impact**: Tests failed. Required either test updates (out of scope) or compatibility shim.

## L11 — Bypassed pre-commit hooks with --no-verify
**Trigger**: Plan 2, `/close` step 15, pre-commit hook failed on unrelated file. Used `--no-verify` to bypass.
**Impact**: Committed code with known style violation. Required follow-up fix.

## L12 — Hiding type errors by excluding files from hooks
**Trigger**: Plan 3, `/close` step 3, mypy failed on out-of-scope file. Edited `.pre-commit-config.yaml` to exclude the file instead of reporting.
**Impact**: Type error hidden permanently. File never type-checked again.

## L17 — Plan steps executed/marked complete out of order
**Trigger**: Plan 4, S2 and S5, S2 edited a governance doc that S5 also needed to edit. Marked S5 complete based on S2's work.
**Impact**: S5 was never actually executed. Missing verification steps. Required replan.
```

### S3.3 — `DECISIONS.md`

```markdown
# DECISIONS.md — SovereignAI Architectural Decisions

Append-only. Each entry: context, options considered, decision, rationale, trade-offs.

---

## D1 — Python for v1, Rust migration deferred

**Context**: Language choice for initial implementation.
**Options considered**: A) Python for v1, migrate to Rust later; B) Rust from day one; C) Hybrid — core in Rust, adapters in Python
**Decision**: Option A — Python for v1.
**Rationale**: Speed of iteration for a single developer. Python's ecosystem (FastAPI, pydantic, pytest, ruff, mypy) provides mature tooling. Contracts are language-agnostic; future Rust rewrite is not precluded.
**Trade-offs**: Slower runtime, higher memory usage, GIL limits parallelism. Acceptable for v1 single-user local-first target.
**Status**: Active. Revisit after Plan 20+.

---

## D2 — dependency-injector for DI container

**Context**: AR4 requires a DI container. Need to choose a library.
**Options considered**: A) `dependency-injector`; B) Manual DI in Composition Root; C) `injector`
**Decision**: Option A — `dependency-injector`.
**Rationale**: Mature library with explicit factory and singleton support. Matches AR4 requirement for DI-managed singletons (Orchestrator, Librarian) and factories (Managers, Workers). Well-documented, actively maintained.
**Trade-offs**: External dependency. If abandoned, manual DI is the fallback.
**Status**: Active.

---

## D3 — Windows-only for v1

**Context**: Platform target per P4.
**Options considered**: A) Windows-only v1, cross-platform later; B) Cross-platform from day one
**Decision**: Option A — Windows-only for v1.
**Rationale**: Single developer on Windows. Reduces complexity. Architecture must not foreclose cross-platform support.
**Trade-offs**: Linux/macOS users cannot run v1. Path handling uses forward slashes (Windows accepts both).
**Status**: Active. Revisit for packaging plan (Q31).
```

### S3.4 — `DEBT.md`

```markdown
# DEBT.md — SovereignAI Deferred Items

Append-only. Each entry: deferred at, reason, trigger condition, target plan.

---

## Deferred: Security Guard implementation
**Deferred at**: prompt-0 (bootstrap)
**Reason**: Security Guard is not pertinent to the core yet. It will be implemented as a Worker later, not as core infrastructure.
**Trigger condition**: When Worker lifecycle and skill authoring are stable (post Plan 4)
**Target plan**: TBD (post Plan 4)

---

## Deferred: Cross-platform packaging
**Deferred at**: prompt-0 (bootstrap)
**Reason**: v1 is Windows-only per P4. Cross-platform packaging adds complexity not needed for initial validation.
**Trigger condition**: When core is stable and Windows packaging is working
**Target plan**: Q31 (post Plan 4)

---

## Deferred: Model loading/unloading based on hardware
**Deferred at**: prompt-0 (bootstrap)
**Reason**: VRAM management, GPU detection, and dynamic model loading are advanced features. Core needs to exist first.
**Trigger condition**: When local model adapters (Ollama, llama.cpp) are wired and working
**Target plan**: TBD (post Plan 4)

---

## Deferred: Self-correction / learning loops
**Deferred at**: prompt-0 (bootstrap)
**Reason**: Learning and improvement (Q13) is a skill-level concern, not core. The retrospective trace skill will be built once the skill framework exists.
**Trigger condition**: When skill framework (Plan 2+) is stable
**Target plan**: TBD (post Plan 4)
```

After creating each file, run `/verify`.

---

## S4 — Create Missing Infrastructure Files

### S4.1 — `pyproject.toml`

```toml
[build-system]
requires = ["setuptools>=61.0", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "sovereignai"
version = "0.1.0"
description = "Local-first, modular AI assistant framework"
readme = "README.md"
requires-python = ">=3.11"
license = {text = "MIT"}
authors = [{name = "AngusKingCAI"}]

[project.optional-dependencies]
dev = [
    "pytest>=7.0",
    "pytest-cov>=4.0",
    "ruff>=0.4.0",
    "mypy>=1.0",
    "bandit>=1.7",
    "pip-audit>=2.0",
    "vulture>=2.0",
    "detect-secrets>=1.0",
    "pre-commit>=3.0",
]

[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py", "*_test.py"]
python_classes = ["Test*"]
python_functions = ["test_*"]
addopts = "-vvv"

[tool.ruff]
line-length = 100
target-version = "py311"
select = ["E", "F", "W", "D", "I", "N", "UP", "B", "C4", "SIM"]
ignore = ["D100", "D104"]

[tool.ruff.pydocstyle]
convention = "google"

[tool.mypy]
python_version = "3.11"
warn_return_any = true
warn_unused_configs = true
disallow_untyped_defs = true
ignore_missing_imports = true

[tool.bandit]
exclude_dirs = [".venv", "venv", "env", ".git", "node_modules", "__pycache__", "build", "dist", ".tox", ".eggs", ".pytest_cache"]

[tool.vulture]
min_confidence = 80
exclude = [".venv", "venv", "env", ".git", "node_modules", "__pycache__", "build", "dist", ".tox", ".eggs", ".pytest_cache", ".mypy_cache", ".ruff_cache", "htmlcov"]
```

### S4.2 — `.pre-commit-config.yaml`

```yaml
repos:
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.4.0
    hooks:
      - id: ruff
        args: [--fix]
      - id: ruff-format

  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.10.0
    hooks:
      - id: mypy
        additional_dependencies: [types-all]

  - repo: https://github.com/PyCQA/bandit
    rev: 1.7.8
    hooks:
      - id: bandit
        args: ["-r", ".", "-ll"]

  - repo: https://github.com/Yelp/detect-secrets
    rev: v1.5.0
    hooks:
      - id: detect-secrets
        args: ['--baseline', 'txt/.secrets.baseline']
```

### S4.3 — `txt/vulture-whitelist.txt`

```
# Vulture whitelist — SovereignAI
# Add symbols here that vulture falsely flags as unused
# Format: symbol_name  # reason

# pytest fixtures often flagged incorrectly
fixture_param  # pytest parametrize decorator parameter
```

### S4.4 — `txt/.secrets.baseline`

Create as JSON with empty results. Use `detect-secrets scan` to generate the proper format, or create a minimal baseline:

```bash
detect-secrets scan --all-files > txt/.secrets.baseline
```

If detect-secrets is not installed yet, create a minimal baseline file and update it after installing dependencies.

After creating each file, run `/verify`.

---

## S5 — Create Directory Structure

Create empty directories with `.gitkeep` files:

```
prompts/
logs/
tests/
sovereignai/
sovereignai/orchestrator/
sovereignai/managers/
sovereignai/workers/
sovereignai/librarian/
sovereignai/adapters/
sovereignai/skills/
sovereignai/panels/
sovereignai/shared/
sovereignai/web/
sovereignai/cli/
sovereignai/tui/
sovereignai/phone/
```

---

## S6 — Update PLANS.md

1. Update "Last updated" line to today's date
2. Ensure `prompt-0` row in "Completed Prompts" is accurate
3. Mark Plan 1 as "🔜 Ready to draft" in queue

After edit, run `/verify`.

---

## S7 — Commit and Tag Prompt-0

**STOP condition**: If any `/verify` step failed, STOP and report before committing.

1. Stage all changes:
   ```
   git add -A
   ```

2. Commit:
   ```
   git commit -m "prompt-0: Bootstrap governance docs and infrastructure

   - Fix .devin/ -> .windsurf/ path discrepancy
   - Fix master -> main branch references
   - Add missing governance docs: CHANGELOG.md, LANDMINES.md, DECISIONS.md, DEBT.md
   - Add pyproject.toml, .pre-commit-config.yaml
   - Add txt/vulture-whitelist.txt, txt/.secrets.baseline
   - Create directory structure for Plans 1-4"
   ```

3. Tag:
   ```
   git tag prompt-0
   git tag --list prompt-0
   ```
   If empty, STOP.

4. Push:
   ```
   git push origin main
   git push origin prompt-0
   ```

5. Verify on origin:
   ```
   git ls-remote --tags origin | grep "prompt-0"
   ```
   If empty, STOP.

---

## S8 — Update PLANS.md Active Plan

Mark prompt-0 as complete and set Plan 1 as active.

---

## Closing

Run `/close` workflow from `.windsurf/workflows/close.md`.

Since this is a docs-only plan with no code, the test suite step will report N/A. All other steps should run on the new files.

**Expected results**:
- Tests: N/A (no code)
- Ruff: 0 findings
- Mypy: N/A (no Python code yet)
- Bandit: N/A (no Python code yet)
- pip-audit: Run on dependencies from pyproject.toml
- Vulture: N/A (no Python code yet)
- Detect-secrets: Pass (baseline established)

After `/close` completes, create `logs/execution-log-prompt-0.md` with header template. User will paste execution log content.

---

## Files WILL Create

- `CHANGELOG.md`
- `LANDMINES.md`
- `DECISIONS.md`
- `DEBT.md`
- `pyproject.toml`
- `.pre-commit-config.yaml`
- `txt/vulture-whitelist.txt`
- `txt/.secrets.baseline`
- `prompts/.gitkeep`
- `logs/.gitkeep`
- `tests/.gitkeep`
- `sovereignai/` subdirectories with `.gitkeep`

## Files WILL Edit

- `AI_HANDOFF.md` (fix .devin -> .windsurf reference)
- `PLANS.md` (fix .devin -> .windsurf reference, update state)
- `.windsurf/workflows/open.md` (fix master -> main)
- `.windsurf/workflows/close.md` (fix master -> main)

## Files WILL NOT Edit

- `AGENTS.md` (no new rules this plan)
- `project-vision-Rev5.md` (locked, no edits)
- Any existing documents in `documents/` (archived history)

---

*Plan 0 — Prompt-0 Remediation. Rev1. Architect draft.*
