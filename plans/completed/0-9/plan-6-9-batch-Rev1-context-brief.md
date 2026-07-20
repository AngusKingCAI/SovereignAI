# Round Table Brief — SovereignAI Plans 6–9 Batch

**Brief type**: Batch context brief covering Plans 6, 7, 8, 9.
**Batch scope**: Web UI stack — from HTTP transport to interactive end-to-end task submission.
**Scaffold**: Per AI_HANDOFF.md 3-part scaffold.

---

## Part 1 — Roles/Rules

- Your job is to find issues, not rewrite the plan.
- Assume this plan will fail — identify how.
- Each issue must include a concrete failure scenario.
- End your response with `**Panelist**: <your name/model>`.
- Anonymous responses will be flagged but still adjudicated; named responses are preferred for accountability.

---

## Part 2 — Context

### What is being reviewed

Plans 6–9 build the Web UI stack on top of the 9 core components completed in Plans 1–4. This is the first batch that touches UI code, introduces runtime dependencies, and implements the Orchestrator layer.

### Cross-plan dependency map

```
Plan 6 (HTTP Transport + Web Server)
  │─> Plan 7 (Orchestrator + Skills)
  │     │─> Plan 8 (9-Panel UI + Log Drawer)
  │           │─> Plan 9 (Auth Integration + End-to-End)
```

- Plan 6 MUST complete before Plan 7 — the web server must exist before the Orchestrator can receive HTTP requests.
- Plan 7 MUST complete before Plan 8 — the 9-panel UI needs the Orchestrator's API to populate panels.
- Plan 8 MUST complete before Plan 9 — auth integration requires the UI structure to exist.

### Plan scope summary

| Plan | Scope | New Files | Runtime Deps Added |
|------|-------|-----------|-------------------|
| **6** | FastAPI web server, Capability API over HTTP, WebSocket for traces, minimal HTML/JS page | `web/main.py`, `web/static/index.html`, `web/static/app.js`, `web/static/styles.css`, `web/templates/index.html`, `tests/test_web_server.py` | `fastapi`, `uvicorn[standard]`, `python-multipart`, `jinja2` |
| **7** | Orchestrator (CEO) scaffold, Web Search skill, Ollama adapter, hardware detection | `sovereignai/orchestrator/orchestrator.py`, `skills/user/websearch_skill/`, `adapters/external/ollama_adapter/`, `sovereignai/shared/hardware_probe.py`, `tests/test_orchestrator.py`, `tests/test_websearch_skill.py`, `tests/test_ollama_adapter.py`, `tests/test_hardware_probe.py` | `ollama`, `httpx`, `psutil` |
| **8** | 9-panel sidebar UI, Log drawer with trace rendering, panel navigation, vanilla JS frontend | `web/static/panels.js`, `web/templates/index.html` (enhanced), `tests/test_web_ui_panels.py`, `tests/test_log_drawer.py` | None |
| **9** | Auth integration (login page, session middleware), end-to-end task submission via web UI, error handling | `web/static/auth.js`, `web/templates/login.html`, `web/templates/register.html`, `tests/test_web_auth.py`, `tests/test_e2e_task_submission.py`, `tests/test_first_run.py` | None |

### Key dependencies

- Plan 6 builds on: CapabilityAPI (Plan 4), AuthMiddleware (Plan 4), TraceEmitter (Plan 1), EventBus (Plan 1).
- Plan 7 builds on: CapabilityGraph (Plan 2), RoutingEngine (Plan 3), TaskStateMachine (Plan 3), LifecycleManager (Plan 3), DIContainer (Plan 1).
- Plan 8 builds on: Plan 6's web server + Plan 7's Orchestrator API.
- Plan 9 builds on: Plan 6's auth middleware + Plan 8's UI structure.

### Author's reasoning (attack this — don't ratify the conclusion)

**My reasoning for FastAPI over Starlette:** FastAPI adds Pydantic validation and auto-generated OpenAPI docs, which are valuable for a Capability API that UIs will consume. The dependency overhead is ~4 packages (fastapi, starlette, pydantic, uvicorn) vs. Starlette's 1 (starlette + uvicorn). For a single-developer project where API contracts matter, the DX win justifies the dep cost. The `fastapi` package itself is thin — it delegates to Starlette and Pydantic. If deps become a concern later, we can migrate to Starlette directly (the API surface is compatible).

**My reasoning for WebSocket from day one:** The vision (P8, Q21) specifies WebSocket for real-time communication. Implementing HTTP polling first and migrating to WebSocket later is a rewrite of the frontend's event handling. Doing WebSocket from Plan 6 means the frontend's event architecture is correct from the start. The cost is minimal — FastAPI's `@app.websocket` is as simple as `@app.get`.

**My reasoning for strict auth even on localhost:** The vision (P6) says "login gate for all UI connections." Relaxing this for localhost creates a special case that the auth middleware must handle, adding complexity. A single auth path (always login) is simpler. The first-run experience creates credentials once; subsequent launches auto-login via session cookie.

**My reasoning for Ollama as the first adapter:** Ollama is the most mature local model runtime (official Python SDK, REST API, Windows support). It satisfies P4's "minimum viable local capability" requirement. The adapter uses the `ollama` Python library (not raw HTTP) for simplicity, but wraps it behind the capability graph so swapping to llama.cpp later requires only a new adapter file.

**My reasoning for stdlib `urllib` for web search:** The web search skill makes HTTP requests to search engines. Using `urllib` (stdlib) avoids adding `requests` or `httpx` as a runtime dependency for a single skill. If the skill needs async or advanced features later, we can upgrade. This keeps the skill lightweight and dependency-free.

### Named open questions for the reviewer

1. **FastAPI dependency weight**: Is adding 4 runtime packages (fastapi, pydantic, uvicorn, python-multipart) acceptable for v1's "minimal deps" philosophy? Could we achieve the same with Starlette + manual Pydantic and save 1-2 packages?

2. **WebSocket vs SSE**: WebSocket gives bidirectional communication but requires connection management (reconnect logic, heartbeat). Server-Sent Events (SSE) is unidirectional (server→client) but simpler and auto-reconnects. For trace streaming, SSE might be sufficient since the client doesn't need to send data over the socket. Should we use SSE for traces and HTTP for everything else?

3. **Orchestrator scope creep**: Plan 7's Orchestrator is described as "minimal" — accepts text, routes to a skill. But the vision describes the Orchestrator as a full CEO that "cleans vague human input into structured measurable prompts." Is our minimal Orchestrator too minimal? Will it require a rewrite when we add real LLM-based orchestration later?

4. **Hardware detection in Plan 7**: Hardware detection (CPU, RAM, GPU, VRAM) requires platform-specific code. On Windows, this means `wmic`, `psutil`, or `GPUtil`. Adding `psutil` as a dependency is common but violates the "minimal deps" ethos. Using `wmic` via subprocess is Windows-only and fragile. What's the right trade-off?

5. **Skill manifest for Web Search**: The web search skill needs a manifest (per Plan 2's manifest format). But it's a user-authored skill, not an external component. Does it need a provenance manifest (P14)? If not, how do we distinguish user-authored from external skills in the capability graph?

6. **Ollama adapter error handling**: If Ollama is not installed or running, the adapter must fail gracefully. Should the adapter register itself in the capability graph even when Ollama is unavailable (with a DEGRADED status), or should it skip registration entirely? The former lets the UI show "Ollama: unavailable"; the latter hides it completely.

### Architect's confidence by plan

- **Plan 6: 85% confident** — FastAPI + WebSocket is well-trodden territory. Risk: dependency bloat.
- **Plan 7: 65% confident** — Orchestrator design is the most uncertain. Risk: scope creep into full LLM orchestration. Hardware detection is also uncertain.
- **Plan 8: 80% confident** — Vanilla JS 9-panel UI is straightforward. Risk: CSS/layout complexity for the Log drawer.
- **Plan 9: 75% confident** — Auth integration is well-understood. Risk: session cookie + WebSocket auth interaction.

### Vision principle compliance

| Plan | Principles Satisfied | Notes |
|------|---------------------|-------|
| 6 | P8 (UIs separate processes), P4 (local-first), P9 (observability via WebSocket traces) | Web server is a separate process consuming Capability API |
| 7 | P5 (wire as you go), P4 (minimum viable local capability), P2 (pluggable adapters/skills) | First adapter + first skill prove the plugin architecture |
| 8 | P8 (9-panel sidebar), P9 (Log drawer) | UI structure matches vision exactly |
| 9 | P6 (login gate), P9 (no silent failures), P13 (strong/robust) | Auth enforced, error handling in UI |

---

## Part 3 — Answer Format

Respond with:
1. **Issues found** (CRITICAL / HIGH / MEDIUM / LOW) — each with a concrete failure scenario.
2. **Other concerns** — anything not covered above.
3. **Clean pass** or **No issues found** — explicitly state if you find nothing.

End with: `**Panelist**: <your name/model>`
