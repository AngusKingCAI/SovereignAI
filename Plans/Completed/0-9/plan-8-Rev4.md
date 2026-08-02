Depends on: prompt-7
Vision principles: P8 (9-panel sidebar), P9 (observability)
Open questions resolved: none

---

## Adjudication Log (Rev3 → Rev4)

### Finding 6 — `event: gap` requires `addEventListener` (Qwen #6 — CRITICAL)
**Action**: ACCEPTED. S2 must specify `eventSource.addEventListener('gap', handleGap)` — `onmessage` does NOT receive custom event types.

### Finding 5 — `event: task_state` requires `addEventListener` (Qwen #4 — CRITICAL)
**Action**: ACCEPTED. S2 must specify `eventSource.addEventListener('task_state', handleTaskState)`.

### Finding 8 — `/api/workers` uses non-existent `CapabilityCategory.WORKER` (Kimi H2 — HIGH)
**Action**: ACCEPTED. Use `ICapabilityIndex.list_all_components()` and filter by category `TOOL` (skills are registered as TOOL capabilities). Rename endpoint to `/api/components` or filter client-side.

### Verdict: All CRITICAL/HIGH issues fixed.

---

## Adjudication Log (Rev2 → Rev3)

Per GR4. 6 panelist responses received. The following Rev2 issues were accepted and fixed.

### Finding 15 — Panel navigation tests untestable via TestClient (Kimi M6, Qwen)
**Severity**: MEDIUM
**Action**: ACCEPTED. `showPanel` and `filterTraces` extracted to `logic.js` as pure functions. Tests reimplement logic in Python. DOM interaction tests documented as requiring headless browser (deferred to DEBT).

### Finding 22 — `innerHTML` XSS risk in Log drawer (MiniMax D5)
**Severity**: MEDIUM
**Action**: ACCEPTED. All trace rendering must use `textContent`, NOT `innerHTML`. This prevents XSS if trace messages contain user-controlled content.

### Finding 23 — No deep-link restoration on page load (MiniMax E4)
**Severity**: LOW
**Action**: ACCEPTED. Add `DOMContentLoaded` handler that reads `location.hash` and calls `showPanel()`.

### Finding 19 — Mixed SSE+polling transport race (MiniMax A3)
**Severity**: HIGH
**Action**: ACCEPTED. Task state updates now also sent via SSE channel (`event: task_state\ndata: {...}`). Chat UI listens for these events instead of (or in addition to) polling. This synchronizes the two transports.

### Verdict
All HIGH/MEDIUM issues fixed. Plan 8 Rev3 is ready for execution.

---

## S0 — Opening

S0.1 — Run `/open`. Verify prompt-7 tag exists on origin. Confirm working copy is clean and on `main`.

S0.2 — Read `AGENTS.md` in full.

S0.3 — No new rules for this plan.

---

## Plan Body

### S1 — Enhance web/templates/index.html

Replace the minimal page with the 9-panel sidebar structure:

```html
<body>
  <nav id="sidebar">
    <div class="sidebar-header">SovereignAI</div>
    <ul class="sidebar-nav">
      <li data-panel="orchestrator" class="active">Orchestrator</li>
      <li data-panel="workers">Workers</li>
      <li data-panel="tasks">Tasks</li>
      <li data-panel="skills">Skills</li>
      <li data-panel="memory">Memory</li>
      <li data-panel="models">Models</li>
      <li data-panel="adapters">Adapters</li>
      <li data-panel="hardware">Hardware</li>
      <li data-panel="options">Options</li>
    </ul>
    <button id="log-toggle">Logs</button>
  </nav>

  <main id="main-content">
    <section id="panel-orchestrator" class="panel active">
      <h2>Orchestrator</h2>
      <div id="chat-messages"></div>
      <form id="chat-form"><input type="text" id="chat-input" placeholder="Message..."><button>Send</button></form>
    </section>
    <!-- 8 more sections, one per panel, all hidden by default except orchestrator -->
  </main>

  <div id="log-drawer">
    <div id="log-controls">
      <label><input type="checkbox" checked data-level="ERROR"> ERROR</label>
      <label><input type="checkbox" checked data-level="WARN"> WARN</label>
      <label><input type="checkbox" checked data-level="INFO"> INFO</label>
      <label><input type="checkbox" data-level="DEBUG"> DEBUG</label>
      <label><input type="checkbox" data-level="TRACE"> TRACE</label>
      <input type="text" id="log-search" placeholder="Search traces...">
      <button id="log-clear">Clear</button>
    </div>
    <div id="log-content"></div>
  </div>
</body>
```

Each panel section contains placeholder content appropriate to its function:
- **Orchestrator**: Chat interface (existing from Plan 6, enhanced).
- **Workers**: Empty `<ul id="workers-list">`, populated from API.
- **Tasks**: Empty `<ul id="tasks-list">`, populated from API.
- **Skills**: Empty `<ul id="skills-list">`, populated from API.
- **Memory**: `<p>Memory panel — deferred to Librarian implementation.</p>`
- **Models**: `<p>Models panel — deferred to model management plan.</p>`
- **Adapters**: Empty `<ul id="adapters-list">`, populated from API.
- **Hardware**: Empty `<div id="hardware-info">`, populated from API.
- **Options**: `<p>Options panel — deferred to settings plan.</p>`

### S2 — Enhance web/static/app.js

Refactor into modular structure:

1. **Panel navigation**:
   ```javascript
   function showPanel(name) {
     document.querySelectorAll('.panel').forEach(p => p.classList.remove('active'));
     document.getElementById('panel-' + name).classList.add('active');
     document.querySelectorAll('.sidebar-nav li').forEach(li => li.classList.remove('active'));
     document.querySelector('[data-panel="' + name + '"]').classList.add('active');
     history.pushState(null, '', '#' + name);
   }
   ```
   - Click sidebar item → call `showPanel()`.
   - On `popstate` (browser back/forward) → parse hash, call `showPanel()`.
   - **Per Finding 23**: On `DOMContentLoaded` → parse `location.hash`, call `showPanel(hash || 'orchestrator')` for deep-link restoration.

2. **Panel content loaders**:
   - `loadWorkers()`: Fetch `/api/workers`, render list.
   - `loadTasks()`: Fetch `/api/tasks`, render list with status badges.
   - `loadSkills()`: Fetch `/api/capabilities`, filter category="skill", render list.
   - `loadAdapters()`: Fetch `/api/capabilities`, filter category="adapter", render list.
   - `loadHardware()`: Fetch `/api/hardware`, render `HardwareInfo` fields.
   - Orchestrator panel: existing chat form from Plan 6, now POSTs to `/api/dispatch` instead of `/api/tasks`.

3. **Log drawer enhancements**:
   - Level filter: checkbox change → re-render visible traces.
   - Search filter: input change → filter traces by message content.
   - Component filter: multi-select dropdown (populated from unique components seen in traces).
   - Clear button: empties `#log-content`.
   - Auto-scroll: if user is at bottom, scroll to new trace; if user scrolled up, don't jump.
   - Max 1000 traces in memory; drop oldest when limit exceeded.

4. **SSE trace handling** (updated from Plan 6):
   - Store all received traces in memory array.
   - **Per Finding 6 (Rev4)**: Use `eventSource.addEventListener('message', handleMessage)` for trace events, `eventSource.addEventListener('gap', handleGap)` for gap markers, and `eventSource.addEventListener('task_state', handleTaskState)` for task state updates. Do NOT use `onmessage` — it does NOT receive custom event types.
   - On new trace: apply filters (level, search, component), append if passes.
   - **Per Finding 22**: All trace rendering uses `textContent`, NOT `innerHTML`.
   - **Per Finding 5 (Plan 6)**: Handle `event: gap` by rendering a visual separator ("--- N events dropped ---").
   - Max 1000 traces in memory; drop oldest when limit exceeded.
   - SSE auto-reconnect handled by browser.
   - **Per Finding 15 (Rev4)**: On SSE error, check auth status via `fetch('/api/auth/status')`. If 401, close EventSource and redirect to `/login`. Do NOT let browser auto-reconnect infinitely.
5. **Per Finding 19: Task state via SSE**:
   - Listen for `event: task_state` SSE messages.
   - On receipt: update chat UI task status immediately (no polling delay).
   - Still poll `/api/tasks/{id}` as fallback every 5s (not 1s — SSE is primary).

### S3 — Enhance web/static/styles.css

- `#sidebar`: fixed left, 200px width, 100vh, dark background, flex column.
- `.sidebar-nav li`: padding 12px 20px, hover highlight, active state (left border accent).
- `#main-content`: margin-left 200px, min-height 100vh, padding 20px.
- `.panel`: display none; `.panel.active`: display block.
- `#log-drawer`: fixed bottom, left 200px, right 0, height 0 → 250px (transition), z-index 100.
- `#log-drawer.open`: height 250px.
- `#log-content`: height 200px, overflow-y scroll, monospace, font-size 12px.
- `.trace-entry`: padding 4px 8px, border-bottom 1px solid #333.
- Responsive: `@media (max-width: 768px)` — sidebar becomes top nav bar, panels stack.

### S4 — Add API endpoints to web/main.py

```python
@app.get("/api/workers")
async def get_workers():
    """Return all registered components from the capability graph."""
    # Per Finding 8 (Rev4): CapabilityCategory.WORKER does not exist.
    # Use list_all_components() and return all — UI filters client-side.
    graph = container.retrieve(ICapabilityIndex)
    components = graph.list_all_components()
    return [{"id": str(c.component_id), "name": c.version, "category": c.provides[0].category.value if c.provides else "unknown"} for c in components]

@app.get("/api/tasks")
async def get_tasks():
    """Return all tasks from the task state machine."""
    tsm = container.retrieve(TaskStateMachine)
    return [TaskResponseDTO(
        task_id=str(t.id),
        state=t.state.value,
        result=t.result,
        error=t.error,
    ) for t in tsm.list_tasks()]
```

Per OR48: These endpoints use only public API types retrieved from the container. No direct imports of core internals.

### S5 — Tests

- `tests/test_web_ui_panels.py`:
  - `test_all_panels_render`: Use `TestClient` to GET `/`, assert all 9 panel sections exist in HTML.
  - `test_panel_navigation`: Simulate clicking sidebar items via JS evaluation (or test the `showPanel` function directly if exposed globally).
  - `test_orchestrator_panel_has_chat_form`: Assert chat input and submit button exist.
  - `test_log_drawer_toggle`: Assert log drawer is hidden by default, visible after toggle click.

- `tests/test_log_drawer.py`:
  - `test_trace_filter_by_level`: Mock SSE messages with different levels, apply filter, assert only matching levels visible.
  - `test_trace_search`: Mock messages, type in search box, assert only matching messages visible.
  - `test_trace_component_filter`: Mock messages from different components, select component, assert filter works.
  - `test_trace_memory_limit`: Send 1001 trace messages, assert only 1000 retained.

Use FastAPI `TestClient` for HTML structure tests. For JS filter logic, extract pure functions to `web/static/logic.js` that can be tested via `js2py` or by porting to Python test fixtures.

### S6 — Create web/static/logic.js (testable pure functions)

Extract filter logic to pure functions:
```javascript
function filterTraces(traces, filters) {
  return traces.filter(t => {
    if (!filters.levels.includes(t.level)) return false;
    if (filters.search && !t.message.includes(filters.search)) return false;
    if (filters.components.length && !filters.components.includes(t.component)) return false;
    return true;
  });
}
```

This function can be tested in Python by reimplementing it as a test fixture (the logic is trivial enough to mirror).

---

## STOP Conditions

- If any panel requires more than 2 API calls to populate initial state, STOP — design is too chatty.
- If CSS layout breaks at 1280x720 resolution (minimum supported), STOP.
- If any test fails, STOP.
- If `web/main.py` imports from `sovereignai/shared/` directly, STOP (OR48 violation).

---

## Files WILL Create

- `web/static/logic.js`
- `tests/test_web_ui_panels.py`
- `tests/test_log_drawer.py`

## Files WILL Edit

- `web/templates/index.html` (replace minimal page with 9-panel structure)
- `web/static/app.js` (refactor to modular panel system)
- `web/static/styles.css` (add sidebar + panel + log drawer styles)
- `web/main.py` (add 2 endpoints)

## Files WILL NOT Edit

- Any file in `sovereignai/shared/`
- `AGENTS.md` (no new rules)

---

## Closing

Run `/close`. Tag: `prompt-8`.
