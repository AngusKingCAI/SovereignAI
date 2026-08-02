# Batch Brief — Plans 16-19 (Rev 1)

## 1. Context
- **Baseline**: prompt-15.1 cleanup (AR17 no-docstrings, D7 no-OR-refs, principles.md as 32-line authority).
- **Repo**: 320 tests, 89% coverage. 90% floor at every /close.
- **Sidebar**: 9 tabs active. Logs becomes 10th.

## 2. Plans in this batch
| Plan | Title | Depends on | Vision principles |
|---|---|---|---|
| 16 | Foundation + Governance + Logs Panel | Scan 15 | P9, P11, P8 |
| 17 | Provider Framework + HF Database + Ollama Service | 16 | P2, P3, P4, P5 |
| 18 | Models Panel + Hardware Panel + Tok/s + VRAM Badges | 17 | P2, P8, P4 |
| 19 | llama.cpp Adapter (P4 Minimum Viable Local) | 18 | P3, P4, P5 |

**Chain**: linear 16→17→18→19. Plan N STOP → all downstream STOP (binary).

## 3. Decisions proposed

| DD-ID | Status | Rule | Alt rejected | Consequence |
|---|---|---|---|---|
| DD1 | Proposed | Logs = 10th sidebar tab, consumes `/api/traces` SSE only (OR66) | overlay/drawer | sidebar grows; loses vertical space |
| DD2 | Proposed | `databases/` and `services/` root-level packages (OR67); core provides registries only | nest under `sovereignai/` | two top-level package trees; aligns P5 |
| DD3 | Proposed | P4 minimum viable local = Ollama + llama.cpp; first-run functional if either installed | ship Ollama only, defer llama.cpp | Plan 19 larger; satisfies P3 sooner |
| DD4 | Proposed | `tok/s = bandwidth ÷ active_bytes × 0.65`; active_bytes_per_param: q4=0.5, q5=0.625, q8=1.0, fp16=2.0, unknown=1.5 | defer until empirical benchmarking | displayed tok/s approximate; validate post-Plan-19 |
| DD5 | Proposed | routing_priority: Ollama=10 preferred, llama.cpp=20 failover (OR70) | llama.cpp preferred (lower overhead) | requires Ollama for optimal UX |

**OR66** (P16): Logs consumes `/api/traces` SSE only. Alt: direct TraceEmitter import. Conseq: HTTP round-trip latency. Aligns AR7.
**OR67** (P17): `databases/` and `services/` root-level. Alt: nest in `sovereignai/`. Conseq: longer imports. Satisfies P5.
**OR68** (P17): providers expose `health_check()` returning typed dataclass. Alt: dict. Conseq: more types. Aligns AR6.
**OR69** (P18): Models + Hardware panels consume capability API only. Alt: direct imports. Conseq: more endpoints. Preserves AR7.
**OR70** (P19): adapter manifests declare `routing_priority` int. Alt: per-call hints. Conseq: static priority. Aligns P3.

## 4. Decisions carried forward
D1-D7 (see DECISIONS.md) — all Active.

## 5. Questions for Round Table
- **Q1**: How should llama.cpp adapter detect missing native deps (CUDA) before model load? Import try/except? PATH probe? `shutil.which`?
- **Q2**: HF list_models() 1hr cache appropriate for power users? Configurable duration?
- **Q3**: Is approximate tok/s (heuristic 0.65 multiplier) worse than no tok/s display?
- **Q4**: Should Plan 19 RoutingEngine.route() explicitly handle "single adapter installed" case?
- **Q5**: Could spec_match.py `tests/**` exemption permit scope creep via test files smuggling production changes?

## 6. Open questions resolved
**None.** Snapshot: 5 vision open (Q1, Q2, Q8, Q13, Q31).

## 7. Risks flagged (landmine pre-screen per GR12)
- **R1** (L37): Plan 19 llama.cpp — ensure no `# TODO`/`pass` ships without DEBT.md entry.
- **R2** (L8): Plan 16 spec_match.py test exemption — see Q5.
- **R3** (L22): Plan 16 check_tracing.py exemptions (`__init__`, `@property`, pure queries) — verify don't hide violations.
- **R4** (L30): Plan 17 `if not _test_mode` guards — verify new providers follow.
- **R5** (L42, L44): Plans 16/17/18 edit web files — close.md step 15 browser smoke test mandatory.

## 8. Coverage target
≥90% at every /close. Current 89% — Plan 16 must lift to ≥90%.

## 9. Round Table protocol
Clean pass = no unaddressed CRITICAL/HIGH. Each rev brings new evidence. No re-litigating settled findings. Evidence-less items auto-dropped. Re-proposing rejected DD-IDs requires new evidence (GR10). Quorum: majority of assigned panelists return verdict (GR13).

## 10. Superseded decisions
None this rev.
