# ARCHITECTURE.md — SovereignAI Architecture Constraints

Authority: `.agent/architect/PRINCIPLES.md`. Propose changes via plan body instruction (Executor writes) or Round Table.

---

## Loading Guidance

**For Architects**: Read in full at session start. Reference AR rules by ID in plans.

**For Executors**: Load on-demand when plan references specific AR rules.

**For Skills**: Reference AR IDs only. Full text lives here; skills do not duplicate.

---

## Component Boundaries

AR1. Owner ↔ Orchestrator only. Chain: Orchestrator → Manager → Worker. Bypass allowed for single-Worker, single-capability, no-state tasks.

AR2. Workers query Librarian directly for memory. No component queries a memory backend directly.

AR3. All model inference routes through Adapters. No component loads weights or calls inference endpoints directly.

AR4. No component references another by hard-coded name. Discovery via capability graph. Exemptions: `app/sovereignai/main.py`, tests, manifests.

AR5. External MCP servers wrapped as adapters before use. No direct MCP calls.

AR6. Adapters register tools in capability graph at startup. Failed health check = graceful typed error, not silent.

AR12. FastAPI web app runs as separate process. Imports from `app/sovereignai/` only via public API surface.

AR21. [RETIRED] Docstring discipline — required docstrings with specific formatting (≥10 words, verb-first, no jargon). Retired in workflow rev 12; docstrings now prohibited per AR11.

---

## Resilience & Health

AR7. Workers circuit-break: >50 errors in 10s = unload. No auto-restart.

AR8. All traces/logs to local SSD via TraceEmitter. No external telemetry. Ever.

AR9. All skill authoring methods produce identical output: manifest + code + DAG.

AR10. External components copied to local disk before use. No runtime remote-only calls.

AR15. Adapters declare `health_check()`. Failed check = DEGRADED status, not skipped.

AR16-AR20. Reserved. Never assigned.

---

## Data & Interface Contracts

AR11. Docstrings not required (D-rules disabled in ruff). Self-documenting names preferred.

AR13. SSE auth via HTTP session cookie. No query-param tokens.

AR14. Web-layer DTOs in `app/web/schemas.py`. Core types never returned directly from HTTP.

---

## Constraint Verification

| Rule | Script | Status | Note |
|------|--------|--------|------|
| AR1 | — | Design-time | Enforced by architecture review |
| AR2 | — | Design-time | Enforced by architecture review |
| AR3 | — | Design-time | Enforced by architecture review |
| AR4 | `no_hardcoded_component_names.py`, `check_ar4_allowlist.py` | Per-close | UI-layer import restrictions; `main.py` exemption allowlist diff |
| AR5 | — | Design-time | Enforced by architecture review |
| AR6 | — | Design-time | Enforced by startup code pattern |
| AR7 | — | Design-time | Runtime circuit-breaker behavior |
| AR8 | `check_tracing.py` | Per-close | No external telemetry audit |
| AR9 | — | Design-time | Enforced by skill authoring pattern |
| AR10 | `check_p4_compliance.py` | Per-close | Local-first compliance |
| AR11 | — | Design-time | Enforced by ruff D-rules disabled |
| AR12 | `ui_does_not_touch_core.py` | Per-close | UI/core separation |
| AR13 | `check_tracing.py` | Per-close | SSE auth audit |
| AR14 | `check_p4_compliance.py` | Per-close | Web DTO compliance |
| AR15 | `check_component_manifest_kwargs_ar15.py` | Per-close | Adapter manifest validation |
| AR21 | — | — | Retired rule - no check needed |
| P11 | `no_context_bags.py` | Per-close | No context bags (PRINCIPLES.md) |

*Extend `check_rule_crossrefs.py` to auto-populate this table from script metadata.*

---

*Propose changes via plan body instruction (Executor writes) or Round Table.*
