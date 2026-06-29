# Plan 16 — Logging & Observability: Fix Log Drawer + Add Orchestrator "Thinking"

**Special plan**: UI/functional fix. Round Table vetoed (per User decision — iterate directly with Devin).

Depends on: prompt-15.1
Vision principles: P9 (observability by default), P13 (strong, robust)
Open questions resolved: none

---

## S0 — Opening

**S0.1** — Run `/open`. Verify `prompt-15.1` tag exists on origin. Confirm clean working copy on `main`. Activate venv (OR45).

**S0.2** — Read `AGENTS.md` in full. Note OR71 (verbatim), OR75/OR80/OR83 (`git add -A`), OR86 (backend + UI in same plan), OR88 (investigate every "Command errored").

**S0.3** — No new rules this plan. Proceed to S1.

---

## S1 — Diagnose and fix the Log Drawer

### Current state (verified by Architect)

**Backend works:**
- SSE stream at `/api/traces/stream` emits events ✅
- 18 events emitted during a 8-second test (startup + task dispatch) ✅
- TraceEmitter.emit() works ✅
- `subscribe_callback` exists on TraceEmitter ✅

**Frontend has the wiring but may have issues:**
- `EventSource('/api/traces/stream')` connects ✅ (no `withCredentials` needed — same-origin, cookies sent automatically)
- `addEventListener('message', ...)` pushes to `traces` array and calls `renderTraces()` ✅
- `renderTraces()` filters by level checkboxes + search, renders to `#log-content` ✅
- Log drawer is CLOSED by default (`height: 0`, only opens when user clicks "Logs" button) — **this may be the issue: user doesn't know to click "Logs"**
- `filterTraces()` in `logic.js` filters by level + search + component ✅

### S1.1 — Fix: make the log drawer visible by default

**File**: `web/templates/index.html`

The log drawer is closed by default (`height: 0`). Users don't see it and think logging is broken. Open it by default with a reasonable height.

**Find**:
```html
<div id="log-drawer">
```

**Change to**:
```html
<div id="log-drawer" class="open">
```

### S1.2 — Fix: ensure level checkboxes match TraceLevel values

**File**: `web/templates/index.html`

The checkboxes use `data-level="ERROR"`, `data-level="WARN"`, etc. (uppercase). But the SSE stream sends `"level": "warn"` (lowercase — it's `TraceLevel.value` which is lowercase per the StrEnum). The `filterTraces` function compares `filters.levels` (uppercase from checkboxes) against `t.level` (lowercase from SSE). **This is a case mismatch — no traces will ever pass the filter.**

**Find**:
```html
<label><input type="checkbox" checked data-level="ERROR"> ERROR</label>
<label><input type="checkbox" checked data-level="WARN"> WARN</label>
<label><input type="checkbox" checked data-level="INFO"> INFO</label>
<label><input type="checkbox" data-level="DEBUG"> DEBUG</label>
<label><input type="checkbox" data-level="TRACE"> TRACE</label>
```

**Change to** (lowercase to match TraceLevel.value):
```html
<label><input type="checkbox" checked data-level="error"> ERROR</label>
<label><input type="checkbox" checked data-level="warn"> WARN</label>
<label><input type="checkbox" checked data-level="info"> INFO</label>
<label><input type="checkbox" data-level="debug"> DEBUG</label>
<label><input type="checkbox" data-level="trace"> TRACE</label>
```

### S1.3 — Fix: add component filter checkboxes

**File**: `web/templates/index.html` + `web/static/app.js`

The `filterTraces` function supports component filtering (`filters.components`), but the UI doesn't have component checkboxes. Add a component filter row that dynamically populates from the traces received.

**Add to `index.html`** after the search input:
```html
<div id="log-components"></div>
```

**Add to `app.js`** in the `renderTraces` function (or a new `updateComponentFilters` function):
```javascript
function updateComponentFilters() {
    const components = [...new Set(traces.map(t => t.component))].sort();
    const container = document.getElementById('log-components');
    if (!container) return;

    // Only add checkboxes for components not already present
    const existing = new Set(Array.from(container.querySelectorAll('input[type="checkbox"][data-component]'))
        .map(cb => cb.getAttribute('data-component')));

    components.forEach(comp => {
        if (!existing.has(comp)) {
            const label = document.createElement('label');
            const cb = document.createElement('input');
            cb.type = 'checkbox';
            cb.checked = true;
            cb.setAttribute('data-component', comp);
            cb.addEventListener('change', renderTraces);
            label.appendChild(cb);
            label.appendChild(document.createTextNode(' ' + comp));
            container.appendChild(label);
        }
    });
}
```

**Update `renderTraces`** to include component filter:
```javascript
function renderTraces() {
    const logContent = document.getElementById('log-content');
    const filters = {
        levels: Array.from(document.querySelectorAll('#log-controls input[type="checkbox"][data-level]:checked'))
            .map(cb => cb.getAttribute('data-level')),
        components: Array.from(document.querySelectorAll('#log-components input[type="checkbox"][data-component]:checked'))
            .map(cb => cb.getAttribute('data-component')),
        search: document.getElementById('log-search').value.toLowerCase()
    };

    // Update component filters (add new components seen in traces)
    updateComponentFilters();

    const filteredTraces = filterTraces(traces, filters);

    logContent.innerHTML = '';
    filteredTraces.forEach(trace => {
        const entry = document.createElement('div');
        entry.className = `trace-entry trace-${trace.level}`;
        entry.textContent = `[${trace.timestamp}] [${trace.level.toUpperCase()}] [${trace.component}] ${trace.message}`;
        logContent.appendChild(entry);
    });

    const isAtBottom = logContent.scrollHeight - logContent.scrollTop === logContent.clientHeight;
    if (isAtBottom) {
        logContent.scrollTop = logContent.scrollHeight;
    }
}
```

### S1.4 — Fix: add SSE error handling

**File**: `web/static/app.js`

The SSE connection has no error handling. If the connection drops, the user sees nothing. Add reconnection.

**Find**:
```javascript
    eventSource.addEventListener('open', () => {
        console.log('SSE connection opened');
    });
```

**Add after the `message` and `gap` event listeners**:
```javascript
    eventSource.addEventListener('error', () => {
        console.error('SSE connection error');
        eventSource.close();
        // Reconnect after 3 seconds
        setTimeout(() => {
            console.log('SSE reconnecting...');
            setupSSE();
        }, 3000);
    });
```

### S1.5 — Verify the log drawer works end-to-end

After the fixes, start the server and verify:
1. Log drawer is visible by default
2. Trace events appear in the log drawer in real-time
3. Level filters work (uncheck "DEBUG" → debug events disappear)
4. Component filters work (uncheck a component → that component's events disappear)
5. Search works (type "CapabilityGraph" → only matching events show)
6. SSE reconnects after server restart

---

## S2 — Add Orchestrator "Thinking" Display

### S2.1 — Add "working..." status with expandable trace view

**File**: `web/static/app.js` + `web/templates/index.html`

When a task is dispatched, the Orchestrator panel shows "working..." which the user can click to expand and see live trace events for that task (filtered by `correlation_id` or `task_id`).

**Add to `index.html`** in the Orchestrator panel:
```html
<div id="orchestrator-thinking" style="display: none;">
    <div id="thinking-header" onclick="toggleThinking()">
        <span id="thinking-status">Working...</span>
        <span id="thinking-arrow">▼</span>
    </div>
    <div id="thinking-content" style="display: none;"></div>
</div>
```

**Add to `app.js`**:
```javascript
let currentTaskId = null;

function showThinking(taskId) {
    currentTaskId = taskId;
    document.getElementById('orchestrator-thinking').style.display = 'block';
    document.getElementById('thinking-status').textContent = 'Working...';
    document.getElementById('thinking-content').style.display = 'none';
}

function hideThinking() {
    document.getElementById('orchestrator-thinking').style.display = 'none';
    currentTaskId = null;
}

function toggleThinking() {
    const content = document.getElementById('thinking-content');
    const arrow = document.getElementById('thinking-arrow');
    if (content.style.display === 'none') {
        content.style.display = 'block';
        arrow.textContent = '▲';
        renderThinkingTraces();
    } else {
        content.style.display = 'none';
        arrow.textContent = '▼';
    }
}

function renderThinkingTraces() {
    if (!currentTaskId) return;
    const content = document.getElementById('thinking-content');
    // Filter traces by this task's ID (correlation_id or task_id)
    const taskTraces = traces.filter(t =>
        t.task_id === currentTaskId || t.trace_id === currentTaskId
    );
    content.innerHTML = '';
    taskTraces.forEach(trace => {
        const entry = document.createElement('div');
        entry.className = `trace-entry trace-${trace.level}`;
        entry.textContent = `[${trace.level.toUpperCase()}] [${trace.component}] ${trace.message}`;
        content.appendChild(entry);
    });
    content.scrollTop = content.scrollHeight;
}

// Update thinking display when new traces arrive
// Add this to the SSE message handler, after renderTraces():
if (currentTaskId) {
    renderThinkingTraces();
}
```

**Update the dispatch handler** (in `setupChatForm`):
After a successful dispatch, call `showThinking(taskId)`. When the task completes (detected via task state change event or polling), call `hideThinking()` and show the result.

### S2.2 — Add task state polling for completion

**File**: `web/static/app.js`

After dispatching a task, poll `/api/tasks/{task_id}` every 2 seconds until the task reaches a terminal state (COMPLETE or FAILED), then update the Orchestrator panel with the result.

```javascript
async function pollTaskCompletion(taskId) {
    const maxPolls = 150; // 5 minutes at 2s intervals
    for (let i = 0; i < maxPolls; i++) {
        await new Promise(resolve => setTimeout(resolve, 2000));
        try {
            const response = await fetch(`/api/tasks/${taskId}`, { credentials: 'same-origin' });
            if (!response.ok) continue;
            const task = await response.json();
            if (task.state === 'complete' || task.state === 'failed') {
                hideThinking();
                displayTaskResult(task);
                return;
            }
            // Update thinking status with current state
            document.getElementById('thinking-status').textContent =
                `Working... (${task.state})`;
        } catch (error) {
            console.error('Task poll failed:', error);
        }
    }
    hideThinking();
    displayTaskResult({ state: 'timeout', error: 'Task did not complete within 5 minutes' });
}

function displayTaskResult(task) {
    const chatLog = document.getElementById('chat-log');
    const entry = document.createElement('div');
    entry.className = `chat-message chat-${task.state === 'complete' ? 'response' : 'error'}`;
    if (task.state === 'complete') {
        entry.textContent = task.result || 'Task completed successfully.';
    } else {
        entry.textContent = `Task failed: ${task.error || 'Unknown error'}`;
    }
    chatLog.appendChild(entry);
    chatLog.scrollTop = chatLog.scrollHeight;
}
```

---

## S3 — Add REST Trace API for Historical Queries

### S3.1 — Add `/api/traces` REST endpoint

**File**: `web/main.py`

The SSE stream only shows live events. For the Task detail view and Memory panel, we need a REST endpoint to query historical traces.

```python
@app.get("/api/traces", dependencies=[Depends(get_current_user)])
async def get_traces(
    request: Request,
    task_id: str | None = None,
    level: str | None = None,
    component: str | None = None,
    limit: int = 100,
    offset: int = 0,
) -> list[dict]:
    """Query historical trace events with optional filters.

    Args:
        task_id: Filter by task ID (correlation_id).
        level: Filter by trace level (error, warn, info, debug, trace).
        component: Filter by component name.
        limit: Maximum number of results (default 100, max 1000).
        offset: Pagination offset.
    """
    container: Any = request.app.state.container
    trace: Any = container.retrieve(TraceEmitter)

    events = trace.get_events(
        level=TraceLevel(level) if level else None,
        component=component,
    )

    # Filter by task_id if provided
    if task_id:
        events = [e for e in events if str(e.correlation_id) == task_id]

    # Apply pagination
    limit = min(limit, 1000)
    paginated = events[offset:offset + limit]

    return [
        {
            "timestamp": e.timestamp.isoformat(),
            "level": e.level.value,
            "component": e.component,
            "message": e.message,
            "correlation_id": str(e.correlation_id),
        }
        for e in paginated
    ]
```

### S3.2 — Add `/api/traces/{task_id}` for task-specific traces

```python
@app.get("/api/traces/{task_id}", dependencies=[Depends(get_current_user)])
async def get_traces_for_task(
    request: Request,
    task_id: str,
) -> list[dict]:
    """Get all trace events for a specific task."""
    container: Any = request.app.state.container
    trace: Any = container.retrieve(TraceEmitter)

    events = trace.get_events()
    task_events = [e for e in events if str(e.correlation_id) == task_id]

    return [
        {
            "timestamp": e.timestamp.isoformat(),
            "level": e.level.value,
            "component": e.component,
            "message": e.message,
            "correlation_id": str(e.correlation_id),
        }
        for e in task_events
    ]
```

---

## S4 — Improve Log Drawer CSS

**File**: `web/static/styles.css`

Make the log drawer more usable:
- Default height 200px (not 250px — less screen real estate)
- Add a resize handle (CSS `resize: vertical`)
- Add a "clear" button that's more visible
- Add count badge showing total events

```css
#log-drawer {
    position: fixed;
    bottom: 0;
    left: 200px;
    right: 0;
    height: 0;
    background-color: #1e1e1e;
    border-top: 2px solid #3d3d3d;
    display: flex;
    flex-direction: column;
    z-index: 1000;
    transition: height 0.2s ease;
    resize: vertical;
    overflow: hidden;
}

#log-drawer.open {
    height: 200px;
}

#log-controls {
    display: flex;
    align-items: center;
    padding: 8px 12px;
    background-color: #2d2d2d;
    border-bottom: 1px solid #3d3d3d;
    gap: 12px;
    flex-wrap: wrap;
}

#log-controls label {
    font-size: 11px;
    color: #aaa;
    cursor: pointer;
}

#log-components {
    display: flex;
    gap: 8px;
    flex-wrap: wrap;
    margin-left: 8px;
}

#log-content {
    flex: 1;
    overflow-y: auto;
    padding: 8px 12px;
    font-family: 'Consolas', 'Courier New', monospace;
    font-size: 12px;
    line-height: 1.4;
}

.trace-entry {
    padding: 2px 4px;
    border-bottom: 1px solid #2a2a2a;
    word-break: break-word;
}

.trace-error { color: #ff6b6b; }
.trace-warn { color: #ffd93d; }
.trace-info { color: #e0e0e0; }
.trace-debug { color: #888; }
.trace-trace { color: #666; }

#log-toggle {
    position: fixed;
    bottom: 0;
    right: 12px;
    z-index: 1001;
    padding: 4px 12px;
    background-color: #3d3d3d;
    border: 1px solid #4d4d4d;
    border-bottom: none;
    color: #ccc;
    cursor: pointer;
    font-size: 12px;
    border-radius: 4px 4px 0 0;
}

#log-toggle:hover {
    background-color: #4d4d4d;
}

#thinking-header {
    padding: 8px 12px;
    background-color: #2d2d2d;
    border: 1px solid #3d3d3d;
    border-radius: 4px;
    cursor: pointer;
    margin: 8px 0;
    display: flex;
    justify-content: space-between;
    align-items: center;
}

#thinking-content {
    max-height: 300px;
    overflow-y: auto;
    padding: 8px 12px;
    background-color: #1e1e1e;
    border: 1px solid #3d3d3d;
    border-radius: 4px;
    font-family: 'Consolas', 'Courier New', monospace;
    font-size: 12px;
}
```

---

## S5 — Tests

- `tests/test_log_drawer_integration.py`: Test that the SSE stream emits events, the REST trace API returns filtered results, and the task-specific trace endpoint works.
- `tests/test_rest_traces.py`: Test `/api/traces` with level, component, task_id filters + pagination.
- `tests/test_thinking_display.py`: Test that dispatch triggers the thinking display and task polling detects completion.

---

## S6 — Run full verification

Standard scan tool suite. Per OR77, coverage must stay ≥89%. Per OR83, use `git add -A`. Per OR86, this plan includes both backend (REST API) and UI (log drawer fix + thinking display) — compliant.

---

## STOP Conditions

- If the log drawer does not display trace events after S1 fixes, STOP.
- If the SSE stream does not reconnect after server restart, STOP.
- If the "thinking" display does not show task-specific traces, STOP.
- If any test fails, STOP.
- If coverage <89%, STOP (per OR77).

---

## Files WILL Edit

- `web/templates/index.html` (S1.1, S1.2, S1.3, S2.1, S4 — log drawer open by default, lowercase levels, component filters, thinking display, CSS)
- `web/static/app.js` (S1.3, S1.4, S2.1, S2.2 — component filters, SSE error handling, thinking display, task polling)
- `web/static/styles.css` (S4 — log drawer CSS improvements)
- `web/main.py` (S3 — REST trace API endpoints)

## Files WILL Create

- `tests/test_log_drawer_integration.py`
- `tests/test_rest_traces.py`
- `tests/test_thinking_display.py`

## Files WILL NOT Edit

- Any file in `sovereignai/shared/` (core is sacred)
- `sovereignai/main.py` (unless needed for trace backend wiring — should already be fixed in 15.1)
- `txt/requirements.txt`
- `project-vision-Rev5.md`

---

## Closing

Run `/close`. Tag: `prompt-16`. Per OR83, use `git add -A`. Per OR76, verify tag is empty before creating. Per OR71, re-read `close.md` fresh.
