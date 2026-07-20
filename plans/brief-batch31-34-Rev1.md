# Brief — Batch 31-34 Rev 1

## 1. Context

Baseline: Plans 26-29 drafted (Rev 5), pending execution. Plan 25.5 completed: 643 passed, 52 skipped, ruff 0, mypy 0. Plan 30 completed (scan plan). DEBT-6 (Librarian.handle_event), DEBT-7 (TUI cookie auth), DEBT-8 (Web UI SSE consumer), DEBT-9 (Cross-task graph memory) open.

## 2. Plans in this batch

| # | Title | Depends on | Vision principles | AR rules | OR rules |
|---|-------|-----------|-------------------|----------|----------|
| 31 | Web API Integration | 26-29 | P8, P11, P13, P14 | AR4, AR12, AR13, AR14 | UOR-1, UOR-2 |
| 32 | TUI Integration | 31, 26, 28 | P8, P11, P13 | AR7, AR12 | UOR-1, UOR-2 |
| 33 | Agent Lifecycle | 31-32, 24, 22 | P1, P3, P7, P11, P13 | AR1, AR4, AR6, AR7, AR8, AR15 | UOR-1, UOR-2 |
| 34 | Librarian Events & Cross-Task Memory | 33, 22, 24 | P1, P2, P9, P13 | AR1, AR2, AR8 | UOR-1, UOR-2 |

## 3. Rules carried forward

AR1-AR15 (see `.agent/executor/ARCHITECTURE.md`), UOR-1-UOR-3, VOR-1-VOR-2, COR-1-COR-2, SOR-1 (see `.agent/executor/OR_RULES.md`), M1-M8 (see `.agent/shared/LANDMINES.md`).

## 4. Questions for Round Table

- Q-RT.1: Plan 31 S2.3 SSE `/api/orchestrator/stream` — does this duplicate Plan 28 S4.2 `/api/options/stream` endpoint pattern? Should we unify SSE infrastructure?
- Q-RT.2: Plan 32 S4 cookie auth — has textual's HTTP client capability been verified since DEBT-7 was opened? If still blocked, should we defer TUI SSE entirely?
- Q-RT.3: Plan 33 S1.3 startup sequence — is the ordering correct? Should ModelRegistry before Orchestrator, or vice versa?
- Q-RT.4: Plan 34 S3.4 merge strategy (name+type dedup) — sufficient for v1, or need UUID-based entity identity?
- Q-RT.5: Plan 34 S5.1 `/api/memory/graph` — should this be under `/api/librarian/` per AR1 (Owner↔Orchestrator only)?

## 5. Open questions resolved

DD-31.1 (Web DTO mandatory), DD-31.2 (CORS same-origin), DD-31.3 (Health aggregation endpoint), DD-31.4 (SSE broker ownership), DD-31.5 (Idempotency session scoping), DD-31.6 (Bootstrap auth flow), DD-31.7 (Rate limit storage), DD-31.8 (SSE not_ready semantics). DD-32.1 (TUI cookie jar), DD-32.2 (Panel refresh strategy), DD-32.3 (Degraded badge), DD-32.4 (Shutdown detection fallbacks), DD-32.5 (File sentinel protocol), DD-32.6 (Error classification), DD-32.7 (DEBT-7 spike mandatory). DD-33.1 (Degraded start), DD-33.2 (Shutdown timeout budget), DD-33.3 (Circuit breaker thresholds), DD-33.4 (Hook phase gating), DD-33.5 (Health cache TTL), DD-33.6 (Force-kill budget calc), DD-33.7 (Sentinel file lifecycle), DD-33.8 (Constructor arg limit), DD-33.9 (DI sub-composers). DD-34.1 (Entity dedup merge), DD-34.2 (Episodic consumer scope), DD-34.3 (Persistent graph file path), DD-34.4 (API exposure under /api/memory), DD-34.5 (Subscriber dedup mechanism), DD-34.6 (Write serialization), DD-34.7 (Performance budget validation).

## 6. Risks flagged

- R1: DEBT-7 (TUI cookie auth) may block Plan 32 S4 if textual cannot attach headers. Mitigation: document limitation, defer SSE panels to v2.
- R2: Plan 33 S1 startup sequence ordering — if ModelRegistry needs Orchestrator for sync triggers, circular dependency possible.
- R3: Plan 34 S3 persistent graph merge — name+type dedup may merge distinct entities with same name. Mitigation: log conflicts, user review in v2.
- R4: Plan 34 S5.1 `/api/memory/graph` may violate AR1 (Owner↔Orchestrator only). Mitigation: route through Orchestrator facade if Q-RT.5 confirms.
- Landmine pre-screen: M1-M8 addressed. M2: Plan 32 updates TUI_ALLOWED_IMPORTS. M3: new plan artifact paths added to ALLOWLIST. M7: all new AR check scripts use `Path(__file__).parent` chain. M8: `/close` verify_close.py enforces non-empty logs.

## 7. Coverage target

≥90% per plan. Test files: Plan 31 ~5 files, Plan 32 ~5 files, Plan 33 ~5 files, Plan 34 ~5 files.

## 8. Round Table protocol reminder

Full first-pass prompt per GR10. Severity: CRITICAL/HIGH block; MEDIUM address or document; LOW Architect discretion. Majority verdict per plan (Pass/Conditional/Block) before delivery (GR9). Conditional/block needs GR3 reasoning. No host paths (GR4). Sign every response: `**Panelist**: <name/model>`. Find issues, not fixes.

## 9. Superseded rules

None in this batch.
