# Plan 20.7.1 — AGENTS.md Conciseness Pass + New Rules

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
- `CHANGELOG.md` — append prompt-20.7.1 entry per OR73 (S9.3)
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

S0.6: Begin Phase 1.

## S1 — Conciseness pass

S1.1: Edit `AGENTS.md`. Replace OR14, OR25, OR40, OR51, OR53, OR54, OR68, OR70, OR71, OR73 with their terse versions from the table above. Copy verbatim — no rewording.

S1.2: Manual verification: count lines and chars for each edited rule. If any >2 lines or >200 chars, trim before committing.

S1.3: Commit: `git add -A && git commit -m "docs: tighten OR14, OR25, OR40, OR51, OR53, OR54, OR68, OR70, OR71, OR73 per GR18"`.

## S9 — Closing

S9.1: Re-read plan in full.
S9.2: Verify test suite passes: `pytest tests/ -vvv --no-cov -q`. If any test fails, investigate per OR18. Do NOT re-run without fix.
S9.3: Append prompt-20.7.1 entry to `CHANGELOG.md` per OR73. Verbatim text:
```
## prompt-20.7.1 — AGENTS.md Conciseness Pass + New Rules
**Date**: 2026-07-02
**Plan file**: prompts/plan-20.7.1-Rev0.md
**Tests**: <pytest output from S9.2>
**Coverage**: N/A (no new production code)
- Tightened OR14, OR25, OR40, OR51, OR53, OR54, OR68, OR70, OR71, OR73 per GR18 (≤2 lines, ≤200 chars)
- Added OR75 (execution log), OR77 (dependency discipline), OR78 (plan immutability), OR79 (test timeouts), OR80 (rule conciseness), OR81 (MCP usage)
- Added L60-L66, L68 to LANDMINES.md (missing dep, plan mutation, test stall, rule verbose, Context7 skipped, Snyk skipped, plan split violations)
- Added GR18 to AI_HANDOFF.md (rule terseness)
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

S9.7: Run `/close`. Verify step 17.5 (check_changelog.py 20.7.1) passes.

S9.8: `git tag prompt-20.7.1` and `git push origin main --tags`. Do NOT force-push (L25/OR42/L55/L64).

---

## Notes for Devin

- **GR18 must land before S1** — S0.4 is mandatory. The conciseness pass in S1 is authorized by GR18; without it, the tightenings have no rule basis.
- **OR78 is the plan-immutability rule** — Devin must NOT edit `prompts/plan-N-RevM.md` files during execution. The only allowed edit is the move to `prompts/completed/` at /close step 17. If the WILL-edit list is incomplete, STOP per OR19 and request an Architect-issued Rev.
- **OR80 is the rule-conciseness enforcement rule** — every AR/OR rule must be <=2 lines / <=200 chars. This plan adds the rule but the mechanical check script is deferred to plan-20.7.2. For now, verify manually in S1.2.
- **OR81 is the MCP usage rule** — Devin queries Context7 before using any library API (prevents P20.4-style hallucinated import paths), and invokes Snyk MCP scan at /close for dep/security changes. L65 (Context7 skipped) and L66 (Snyk skipped) are the landmines. Snyk scan integration is deferred to plan-20.7.2.
