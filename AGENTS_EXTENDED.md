# AGENTS_EXTENDED.md

**Reference rules** — read when AGENTS.md is ambiguous or when a specific
technical detail is needed. Not loaded at session start. Consult on-demand.

Authority: `.agent/architect/PRINCIPLES.md` · Ambiguous → read `.agent/shared/LANDMINES.md`

---

## Extended Architecture Rules (AR16–AR30)

AR16. Capability classes have conformance tests. Fail-closed for first-party, fail-open for third-party. <100ms each, cached per `(component_id, content_hash)`.

AR17. Contract tests verify backward compatibility. Failure blocks build.

AR18. Property-based tests run every commit. CI gate blocker.

AR19. Memory backends pluggable via adapter interface. No direct backend references in core.

AR20. EventBus typed. No `Any` payloads. Subscribers declare `EventT`.

AR21. DatabaseRegistry caches connection pools. No per-query connections.

AR22. ServiceRegistry health checks every 30s. Unhealthy >3 cycles = DEGRADED.

AR23. RoutingEngine shortest-path with capability-weighted edges. No hard-coded routes.

AR24. ModelCatalog validates model paths at startup. Invalid path = DEGRADED, not crash.

AR25. HardwareProbe non-blocking. No synchronous I/O in probe threads.

AR26. DAGValidator checks cycles before execution. Cycle = typed error, not hang.

AR27. FileTraceSubscriber batches writes. No per-trace fsync.

AR28. Container resolves via type hints. No string-based service lookup.

AR29. TokSampler rate-limits per model. Exceeded = queue, not drop.

AR30. QuantPriority enum drives scheduling. No numeric priority literals.

---

## Extended Operational Rules (OR31–OR63)

OR31. Pre-commit hooks run before every commit. Failure = STOP. No `--no-verify`.

OR32. CHANGELOG prepend only. Never append. Latest prompt at top.

OR33. Plan files moved to `prompts/completed/` before tag. Glob: `plan-{N}-Rev*.md`.

OR34. Execute plan steps in strict numerical order. No reordering based on perceived convenience.

OR35. UI changes require DOM verification + screenshot capture before commit.

OR36. AR check scripts run in sequence. Any failure = STOP. No partial passes.

OR37. Test timeouts: 30s default via pytest-timeout. Per-test override via `@pytest.mark.timeout(N)`.

OR38. Snyk MCP scan on requirements + changed files. CRITICAL/HIGH = STOP.

OR39. Vulture whitelist in `.agent/executor/txt/vulture-whitelist.txt`. New findings = STOP.

OR40. Detect-secrets baseline in `.agent/executor/txt/.secrets.baseline`. New secrets = STOP.

OR41. Bandit baseline in `.agent/executor/bandit/baseline.json`. New findings = STOP.

OR42. Pip-audit strict mode. CVE in requirements = STOP.

OR43. Mypy on changed files only (non-scan). Full suite at scan prompts.

OR44. Ruff check entire repo. No exclusions.

OR45. Spec match script validates plan vs implementation. Exit≠0 = STOP.

OR46. AR7 allowlist checked before UI changes. Unapproved addition = STOP.

OR47. Placeholder detection in source. Any hit = STOP.

OR48. Plan immutability: no content modification during split. Script-enforced.

OR49. Dependency check before commit. Exit≠0 = STOP.

OR50. Rule conciseness check. Exit≠0 = STOP.

OR51. Changelog check validates position and format. Exit≠0 = STOP.

OR52. Test mode hooks checked. Exit≠0 = STOP.

OR53. No globals in `app/sovereignai/`. Script-enforced.

OR54. Constructor arg cap ≤15. Script-enforced.

OR55. No context bags. Script-enforced.

OR56. No hardcoded component names in UI layers. Script-enforced.

OR57. UI does not touch core directly. Script-enforced.

OR58. Tracing allowlist compliance. Script-enforced.

OR59. P4 compliance check. Script-enforced.

OR60. Component manifest kwargs check. Script-enforced.

OR61. Scoped test resolution via `.agent/executor/scripts/get_scoped_tests.py`. Empty scope + .py changes = STOP.

OR62. Scan plan detection via `.agent/executor/scripts/is_scan_plan.py`. Drives test scope per OR29.

OR63. Security findings documented in DEBT.md with target plan. "TBD" = STOP.
