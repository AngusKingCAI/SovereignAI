Depends on: prompt-20.9.3
Vision principles: 1 (local-first), 7 (privacy)
Open questions resolved: none

## WILL edit
- `txt/requirements.txt` — upgrade diskcache, setuptools
- `sovereignai/shared/routing_engine.py` — add health_check caching
- `sovereignai/shared/generate.py` — add timeout parameter
- `tests/` — add timeout tests
- `DEBT.md` — mark resolved items
- `CHANGELOG.md` — append per OR73
- `PLANS.md` — update baseline
- `prompts/plan-20.9.4-Rev0.md` — move to completed/ at /close

## WILL NOT edit
- TUI panels, hardware probe, memory backends (handled in 20.9.1-3). Security Guard (new feature, not debt). If scope expands, STOP.

## S0 — Opening

S0.1: Run `/open`. Read `AGENTS.md` in full.
S0.2: Read `DEBT.md`. Identify items this plan resolves.
S0.3: No new rules.
S0.4: Begin Phase 1.

## S1 — CVE Remediation

S1.1: Upgrade `diskcache` to patched version (check CVE-2025-69872 fix)
S1.2: Upgrade `setuptools` to latest secure version
S1.3: Run `pip-audit` to verify no critical/high CVEs
S1.4: Commit: `git add -A && git commit -m "security: upgrade diskcache and setuptools per CVEs"`

## S2 — Routing Engine Caching

S2.1: Add `health_check_cache: TTLCache` to `RoutingEngine`
S2.2: Cache health_check results for 30 seconds
S2.3: Add cache invalidation on adapter state change

S2.4: Commit: `git add -A && git commit -m "perf: health_check caching in RoutingEngine"`

## S3 — Generate Timeout

S3.1: Add `timeout_seconds: float = 30.0` parameter to `generate()`
S3.2: Implement timeout using `signal` (Unix) / `threading.Timer` (Windows)
S3.3: Add tests for timeout behavior

S3.4: Commit: `git add -A && git commit -m "feat: generate() timeout parameter"`

## S4 — Update DEBT.md

S4.1: Mark resolved:
- diskcache CVE-2025-69872 → Resolved at prompt-20.9.4
- setuptools vulnerabilities → Resolved at prompt-20.9.4
- health_check caching in RoutingEngine → Resolved at prompt-20.9.4
- generate() timeout → Resolved at prompt-20.9.4
- generate() timeout implementation → Resolved at prompt-20.9.4

S4.2: Commit: `git add -A && git commit -m "docs: mark security/arch DEBT items resolved"`

## S5 — /close

S5.1: Run `/close`.
