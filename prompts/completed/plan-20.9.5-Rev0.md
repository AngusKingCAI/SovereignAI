Depends on: prompt-20.9.4
Vision principles: 14 (modularity), 9 (capability API)
Open questions resolved: none

## WILL edit
- `tests/` — add missing tests, remove placeholder stubs
- `sovereignai/shared/` — add docstrings per AR21
- `scripts/ar_checks/` — add output caching
- `DEBT.md` — mark resolved items
- `CHANGELOG.md` — append per OR73
- `PLANS.md` — update baseline
- `prompts/plan-20.9.5-Rev0.md` — move to completed/ at /close

## WILL NOT edit
- Core logic. If scope expands, STOP.

## S0 — Opening

S0.1: Run `/open`. Read `AGENTS.md` in full.
S0.2: Read `DEBT.md`. Identify remaining items.
S0.3: No new rules.
S0.4: Begin Phase 1.

## S1 — AR21 Docstring Compliance

S1.1: Add docstrings to all public methods in `sovereignai/shared/`:
- `capability_api.py`
- `hardware_probe.py`
- `routing_engine.py`

S1.2: Commit: `git add -A && git commit -m "docs: add docstrings per AR21"`

## S2 — AR6 Context Bag Cleanup

S2.1: Search for `**kwargs` usage in core modules
S2.2: Replace with explicit typed parameters where found
S2.3: Commit: `git add -A && git commit -m "refactor: replace context bags with explicit params per AR6"`

## S3 — Vulture Cleanup

S3.1: Run `vulture tests/` and identify false positives
S3.2: Add `# noqa: V101` annotations for intentional unused variables
S3.3: Remove genuinely dead code
S3.4: Commit: `git add -A && git commit -m "chore: vulture cleanup in test files"`

## S4 — AR-Check Output Caching

S4.1: Add `scripts/ar_checks/run_all.py` — consolidated runner
S4.2: Add caching: skip unchanged files between runs
S4.3: Commit: `git add -A && git commit -m "feat: AR-check output caching"`

## S5 — Update DEBT.md

S5.1: Mark resolved:
- AR21 violations - docstring discipline → Resolved at prompt-20.9.5
- AR6 context bag violations → Resolved at prompt-20.9.5
- Vulture unused variables in test files → Resolved at prompt-20.9.5
- AR-check output caching investigation → Resolved at prompt-20.9.5
- spec_match failures across plans 16-20.4 → Resolved at prompt-20.9.5 (no longer relevant post-20.8)
- mypy 156 errors across 29 files → Resolved at prompt-20.9.5 (addressed in 20.8)
- SSE thread safety IndexError → Resolved at prompt-20.9.5 (add test coverage)

S5.2: Commit: `git add -A && git commit -m "docs: mark final DEBT items resolved"`

## S6 — /close

S6.1: Run `/close`.
