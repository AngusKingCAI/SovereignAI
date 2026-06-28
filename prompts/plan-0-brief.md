# Round Table Brief — Plan 0 (Prompt-0 Remediation)

Per the scaffold in AI_HANDOFF.md.

---

## Part 1: Roles/Rules

- Your job is to find issues, not rewrite the plan.
- Assume this plan will fail — identify how.
- Each issue must include a concrete failure scenario.
- End your response with `**Panelist**: <your name/model>`. Anonymous responses will be flagged but still adjudicated; named responses are preferred for accountability.

---

## Part 2: Context

### Plan Scope Summary

Plan 0 is a pre-Plan 1 mechanical fix-up. It resolves an incomplete bootstrap state before the first real code plan begins. Scope:

1. **Fix path references** — `AI_HANDOFF.md` and `PLANS.md` reference `.windsurf/workflows/` but the actual directory is `.devin/workflows/`. Edit the two docs to match reality. No directory moves.
2. **Fix branch name** — `.devin/workflows/open.md` and `close.md` reference `master` but the actual default branch is `main`. Update both workflow files.
3. **Create 4 missing governance docs** — `CHANGELOG.md`, `LANDMINES.md`, `DECISIONS.md`, `DEBT.md`. These are required by the 12-document governance set but were absent from the repo.
4. **Create infrastructure files** — `pyproject.toml` (tool config), `.pre-commit-config.yaml` (hooks), `txt/vulture-whitelist.txt`, `txt/.secrets.baseline`.
5. **Create directory structure** — `prompts/`, `logs/`, `tests/`, `sovereignai/` subdirectories with `.gitkeep` files for git tracking.
6. **Commit and tag** — `git commit`, `git tag prompt-0`, push to origin, verify.

### Key Dependencies

- None. This is bootstrap. No prior plans, no prior code.
- The Executor's working tree is `C:/SovereignAI/` on Windows.

### Author's Reasoning (attack this, not the conclusion)

My reasoning for this design:

1. **Path fix strategy**: I originally proposed moving `.devin/workflows/` to `.windsurf/workflows/` to match the handoff. The user corrected me: edit the docs instead, keep the directory. This is simpler — one edit per file vs. move + delete + edit. The risk is that `.devin/` is a non-standard name; future contributors might expect `.windsurf/`. But for a single-developer project, consistency with the existing directory is more important than consistency with the handoff template.

2. **Governance doc content**: `LANDMINES.md` carries L1–L23 inherited from the predecessor project (sovere-ai). These are real patterns that already happened. I included them because the Executor needs diagnostic context for rules that reference them (OR5, OR3, OR7, etc.). The risk is stale landmines — patterns that won't recur in this project. But since the rules already cite them, the landmines must exist for the cross-reference to resolve.

3. **pyproject.toml choices**: I configured `ruff`, `mypy`, `pytest`, `bandit`, `vulture`, `detect-secrets` all in one file. The risk is over-configuration before any code exists — the Executor might need to tweak these as code emerges. I set `line-length = 100` and `target-version = "py311"` as conservative defaults. I excluded `D100` (missing docstring in public module) and `D104` (missing docstring in public package) from ruff because empty `__init__.py` files in the scaffold don't need docstrings yet.

4. **.secrets.baseline**: I suggested creating a minimal baseline and updating it after `detect-secrets` is installed. The risk is that the baseline format might be wrong if created manually. The alternative is to install detect-secrets first, then generate the baseline. But that requires network access and package installation, which the Executor can do during the plan.

5. **No Round Table skip**: I considered skipping Round Table for this mechanical plan (per scan prompt exemption), but the user explicitly requested a brief. The plan contains no architectural decisions — it's purely mechanical — so the Round Table's value is limited. I'm providing the brief because the user asked, but I expect few substantive findings.

### Named Open Questions for Reviewer Engagement

1. **Should `.devin/workflows/` be renamed to `.windsurf/workflows/` instead of editing the docs?** The handoff says `.windsurf/`, the repo has `.devin/`. Which is the source of truth? What breaks if we keep `.devin/` forever?

2. **Are the L1–L23 inherited landmines still relevant?** These come from a predecessor project with a different codebase and different Executor. Do they provide value, or are they cargo-culted failure patterns that might not apply?

3. **Is the pyproject.toml configuration premature?** We have no code, no tests, no dependencies installed yet. Should the tool configuration be deferred to Plan 1 (when the first code is written), or is it correct to establish it now?

4. **Should the `.gitkeep` approach be replaced with `__init__.py` files?** Python packages conventionally use `__init__.py` (even empty ones) rather than `.gitkeep`. The plan uses `.gitkeep` because the directories might not all be Python packages (e.g., `logs/`, `prompts/`). Is this the right call?

5. **Is the commit message scope correct?** The plan bundles path fixes, governance docs, infrastructure files, and directory structure into a single commit. Should this be split into multiple commits (e.g., one for fixes, one for new docs, one for infrastructure)?

### Architect's Confidence

- Path and branch fixes: **95% confident** — mechanical, low risk.
- Governance doc content: **80% confident** — inherited landmines might be stale, but the format is correct.
- pyproject.toml configuration: **65% confident** — will likely need tuning once code exists.
- Directory structure: **90% confident** — matches the vision's Core Scope (v1) list.
- Overall plan: **85% confident** — this is a mechanical fix-up, not an architecture decision.

### Vision Principle Compliance

This plan satisfies:
- **P1 (sacred core)** — establishes the governance framework that protects the core from scope creep.
- **P2 (pluggable)** — directory structure reserves slots for adapters, skills, memory backends.
- **P5 (wire as you go)** — no speculative code, only infrastructure needed for Plans 1–4.
- **P7 (modular core)** — directory layout enforces layer separation (orchestrator/, managers/, workers/, etc.).

This plan does not affect:
- P3 (no provider lock-in) — no adapters exist yet.
- P4 (local-first) — no runtime exists yet.
- P6–P14 — not applicable at bootstrap.

---

## Part 3: Answer Format

Structure your response flexibly. Suggested sections:

1. **Pre-mortem** — "Assume this plan failed in 6 months. List the most plausible reasons."
2. **Issues by severity** — CRITICAL / HIGH / MEDIUM / LOW, with concrete failure scenarios.
3. **Other concerns** — Anything not captured above.
4. **Sign-off** — `**Panelist**: <name/model>` (mandatory per GR3).

You may respond with "No issues found" if you find nothing substantive. Do not invent problems to fill space. Each issue must cite a concrete failure scenario and evidence from the codebase or plan.

Ban style/formatting/speculative-future/feature-request comments — substance only.

---

*Brief for Plan 0 — Prompt-0 Remediation. Rev1. Architect draft.*
