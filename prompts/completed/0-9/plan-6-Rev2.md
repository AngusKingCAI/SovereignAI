Depends on: prompt-5 (Scan 5)
Vision principles: P8 (UIs separate processes), P4 (local-first), P9 (observability)
Open questions resolved: none

---

## S0 — Opening

S0.1 — Run `/open`. Verify prompt-5 tag exists on origin. Confirm working copy is clean and on `main`. If the workflow is missing or fails, STOP and report.

S0.2 — Read `AGENTS.md` in full. Note: Landmines L1–L31 are inherited; new landmines start at L32.

S0.3 — Add new rules the Architect specified for this plan to `AGENTS.md` and commit before any coding step:
- **OR48**: The FastAPI web app runs as a separate process, not embedded in the core runtime. The web server imports from `sovereignai/` only via the public API surface (`CapabilityAPI`, protocols). It does not import core internals directly. Source: Plan 6.
- **OR49**: SSE connections authenticate via standard HTTP session cookie. No query-parameter tokens are used for auth. Source: Plan 6 Rev 2.
- **OR52**: Web-layer DTOs (in `web/schemas.py`) are the canonical HTTP contract. Core domain types are never returned directly from HTTP endpoints. Mapping functions convert between DTOs and core types. Source: Plan 6 Rev 2.

Commit: `docs: add OR48-OR49, OR52 for prompt-6`

---

## Plan Body

### S1 — Add runtime dependencies to txt/requirements.txt

Append to `txt/requirements.txt`:
```
fastapi>=0.110.0
uvicorn[standard]>=0.27.0
python-multipart>=0.0.9
jinja2>=3.1.0
```

Run `.venv/Scripts/pip.exe install -e .[dev]` to refresh the local environment.
Run `.venv/Scripts/pip-audit.exe --strict --requirement txt/requirements.txt` to verify no CVEs.

### S2 — Create web/schemas.py (HTTP DTOs)

Create `web/schemas.py` with Pydantic models that are the canonical HTTP contract:

```python
from pydantic import BaseModel
from typing import Optional
from uuid import UUID

class CapabilityResponseDTO(BaseModel):
    id: str
    name: str
    category: str
    description: str
    priority: int

class CapabilityQueryDTO(BaseModel):
    message: str

class TaskResponseDTO(BaseModel):
    task_id: str
    state: str
    result: Optional[str] = None
    error: Optional[str] = None

class TraceEventDTO(BaseModel):
    timestamp: str
    level: str
    component: str
    message: str
    trace_id: str
```

Per OR52: These DTOs are independent of core types. Mapping functions convert between DTOs and core types. A refactor of `Task` in the core does not break the HTTP contract.

### S3 — Create web/main.py (FastAPI application)

Create `web/main.py` with the following structure:

1. **FastAPI app instance** with CORS configured for `http://localhost:8000` and `http://127.0.0.1:8000` only.
2. **Static files**: Mount `web/static/` at `/static`.
3. **Templates**: Jinja2 templates from `web/templates/`.
4. **Startup event**: Call `build_container()` from `sovereignai.main`, store the container in `app.state.container`.
5. **Shutdown event**: Clean up (no-op for now; future plans may close connections).
6. **HTTP endpoints**:
   - `GET /` → render `index.html` template.
   - `GET /api/capabilities` → retrieve `CapabilityAPI` from container, call `query_capabilities()`, map to `CapabilityResponseDTO` list, return JSON.
   - `POST /api/tasks` → parse `CapabilityQueryDTO`, retrieve `CapabilityAPI`, call `submit_task()`, map result to `TaskResponseDTO`, return JSON.
   - `GET /api/tasks/{task_id}` → retrieve `CapabilityAPI`, call `get_task_state()`, map to `TaskResponseDTO`, return JSON.
7. **SSE endpoint** `GET /api/traces/stream`:
   - Set headers: `Content-Type: text/event-stream`, `Cache-Control: no-cache`, `Connection: keep-alive`.
   - Subscribe to `TraceEmitter` events by registering a callback that formats each event as SSE data (`data: <json>\n\n`).
   - On client disconnect: unsubscribe from TraceEmitter.
   - Auth: standard HTTP session cookie (same as all other endpoints).
   - Backpressure: maintain a max queue of 1000 events per client; drop oldest when exceeded.

Per OR48: `web/main.py` imports only `CapabilityAPI`, `AuthMiddleware`, `TraceEmitter`, and `build_container` from `sovereignai/`. No imports from `sovereignai/shared/` internals.

### S4 — Create web/templates/index.html

Create `web/templates/index.html`:
- `<!DOCTYPE html>` with `<meta charset="UTF-8">` and `<meta name="viewport" content="width=device-width, initial-scale=1.0">`.
- Title: "SovereignAI".
- Link to `styles.css`.
- Body structure:
  - `#app-header`: Title bar with "SovereignAI" and connection status indicator.
  - `#main-content`: Default view showing capability list from `/api/capabilities`.
  - `#task-section`: Input field + submit button for task submission.
  - `#task-status`: Displays current task state (polling `/api/tasks/{id}`).
  - `#log-drawer`: Collapsible bottom panel for trace events from SSE.
- Script tag loading `app.js`.

### S5 — Create web/static/app.js

Create `web/static/app.js` (vanilla JavaScript, no frameworks):

1. **On DOM load**: Fetch `/api/capabilities` and render as a bulleted list in `#main-content`.
2. **SSE connection**:
   - Create `EventSource('/api/traces/stream')`.
   - On `open`: update connection status to "Connected".
   - On `message`: parse JSON, append to `#log-drawer` with timestamp, level, component, message.
   - On `error`: update status to "Reconnecting...", `EventSource` auto-reconnects after default browser backoff.
   - Max reconnect: rely on browser's built-in exponential backoff (no manual counter needed).
3. **Task submission**:
   - On form submit: POST to `/api/tasks` with JSON body.
   - On success: start polling `/api/tasks/{task_id}` every 1s.
   - On state change: update `#task-status` text.
   - On COMPLETE or FAILED: stop polling, display result or error.
4. **Log drawer**:
   - Toggle button shows/hides the drawer.
   - Each trace entry is a `<div>` with CSS class per level (error, warn, info, debug, trace).

### S6 — Create web/static/styles.css

Create `web/static/styles.css`:
- Body: sans-serif font, dark theme (vision P8 implies a developer-focused UI).
- `#app-header`: fixed top, full width, 50px height, flex layout.
- `#main-content`: padding-top 60px, max-width 1200px, centered.
- `#log-drawer`: fixed bottom, full width, 200px height, collapsible (display toggle), overflow-y scroll, monospace font for trace entries.
- `.trace-error`: red text. `.trace-warn`: yellow. `.trace-info`: white. `.trace-debug`: gray. `.trace-trace`: dark gray.
- Responsive: min-width 320px support.

### S7 — Tests

Create `tests/test_web_server.py`:
1. `test_get_index_returns_200`: Use FastAPI `TestClient` to `GET /`, assert 200, assert body contains "SovereignAI".
2. `test_get_capabilities_returns_json_list`: Mock `CapabilityAPI.query_capabilities()` to return a list with one capability, assert JSON structure matches `CapabilityResponseDTO`.
3. `test_post_task_returns_task_id`: Mock `CapabilityAPI.submit_task()` to return a task ID, assert response matches `TaskResponseDTO`.
4. `test_get_task_state_returns_task`: Mock `CapabilityAPI.get_task_state()` to return a `Task`, assert JSON structure matches `TaskResponseDTO`.
5. `test_sse_receives_trace_events`: Use `TestClient` to `GET /api/traces/stream`, mock `TraceEmitter` to emit an event, assert SSE data format (`data: <json>`).
6. `test_sse_auth_required`: Request `/api/traces/stream` without session cookie, assert 401.
7. `test_dto_mapping_isolated`: Verify that changing a core `Task` field name does not break the HTTP response format.

Use `unittest.mock` to patch container retrieval so tests don't need a real DI container.

---

## STOP Conditions

- If `fastapi` or `uvicorn` fail to install, STOP and report.
- If SSE test hangs for more than 5 seconds, STOP (indicates async event loop issue).
- If any test fails, STOP.
- If `web/main.py` imports anything from `sovereignai/shared/` directly (violating OR48), STOP.
- If a core type is returned directly from an endpoint (violating OR52), STOP.

---

## Files WILL Create

- `web/main.py`
- `web/schemas.py`
- `web/templates/index.html`
- `web/static/app.js`
- `web/static/styles.css`
- `tests/test_web_server.py`

## Files WILL Edit

- `txt/requirements.txt` (append 4 lines)

## Files WILL NOT Edit

- Any file in `sovereignai/shared/` (core is sacred per P1)
- `sovereignai/main.py` (no `get_container()` needed — startup event calls `build_container()` directly)
- `.devin/workflows/*.md` (workflow changes require separate plan)
- `AGENTS.md` (except S0.3 rule addition)

---

## Closing

Run `/close`. Tag: `prompt-6`. Update CHANGELOG, PLANS.md.
