# Plan 20.4 — TUI Skeleton with Real Backend Integration

```
Depends on: prompt-20.3
Vision principles: P2 (modularity), P4 (testability), P6 (local-first), P9 (observability), P13 (fail gracefully)

Open questions resolved: none
```

---

## S0 — Opening
- **S0.1**: Run `/open`
- **S0.2**: Read `AGENTS.md` in full
- **S0.3**: Add OR72 to AGENTS.md: "TUI is a first-class UI consuming the same capability API as the WebUI. TUI panels must display real backend state, not placeholder text." Commit.

---

## S1 — Create TUI Skeleton (`tui/main.py`)
- **S1.1**: Textual App with `ContentSwitcher` for panel switching
- **S1.2**: Left sidebar: 10 `Button` widgets (Orchestrator, Workers, Tasks, Skills, Memory, Models, Adapters, Hardware, Options, Logs)
- **S1.3**: Each button switches `ContentSwitcher.current` to corresponding panel ID
- **S1.4**: Location bar `Static` widget updates on panel switch: `Localhost:{Panel}`
- **S1.5**: Import `build_container()` from `sovereignai.main`, store in app state
- **S1.6**: Run `python tui/main.py`, verify all 10 panels render

---

## S2 — Options Panel (`tui/panels/options.py`)
- **S2.1**: Retrieve `DatabaseRegistry` and `ServiceRegistry` from container
- **S2.2**: Display services as `DataTable`: Name, Status, PID, Port, Uptime
- **S2.3**: Status color-coded: running=green, stopped=red
- **S2.4**: [Start] / [Stop] buttons per service row
- **S2.5**: Button handlers call registry start/stop methods, refresh table
- **S2.6**: Display databases as second `DataTable`: Name, Status, Model Count, Last Updated
- **S2.7**: [Fetch] / [Uninstall] buttons per database row

---

## S3 — Memory Panel (`tui/panels/memory.py`)
- **S3.1**: Retrieve all 4 memory backends from container
- **S3.2**: Display `DataTable` with columns: Backend, Records, Last Write
- **S3.3**: Query each backend count, populate table
- **S3.4**: [Refresh] button re-queries all backends
- **S3.5**: [Test Write] button: store test record, verify retrieve, show result
- **S3.6**: `RichLog` at bottom shows trace events from TraceMemoryBackend

---

## S4 — Hardware Panel (`tui/panels/hardware.py`)
- **S4.1**: Retrieve `HardwareProbe` from container
- **S4.2**: Display `Static` cards: CPU (usage, model, cores), Memory (used/total, speed), GPU (usage, VRAM, temp), Disk (used/total), Network (adapter, SSID, IP)
- **S4.3**: [Refresh] button re-runs probe, updates all cards
- **S4.4**: `DataTable` for process list: Name, PID, CPU%, Mem%

---

## S5 — Logs Panel (`tui/panels/logs.py`)
- **S5.1**: Retrieve `TraceEmitter` from container
- **S5.2**: `RichLog` widget displays real-time trace events
- **S5.3**: Subscribe to TraceEmitter events, append to log with color coding
- **S5.4**: Level filter buttons: [All] [ERROR] [WARN] [INFO] [DEBUG]
- **S5.5**: Verify 100% verbosity: all events from all components appear

---

## S6 — Adapters Panel (`tui/panels/adapters.py`)
- **S6.1**: Retrieve `CapabilityGraph`, filter adapters
- **S6.2**: Display `DataTable`: Name, Status, Capabilities
- **S6.3**: [Health Check] button per adapter: runs real health_check(), updates status
- **S6.4**: [Load Model] / [Unload Model] buttons for model adapters

---

## S7 — Skills Panel (`tui/panels/skills.py`)
- **S7.1**: Retrieve `CapabilityGraph`, filter skills
- **S7.2**: Display `DataTable`: Name, Version, Category
- **S7.3**: [Invoke] button per skill: calls skill with test input, shows result
- **S7.4**: Test `websearch_skill`: invoke with "test query", display response

---

## S8 — Install Test Manager and Worker
- **S8.1**: Create `tui/test_workers/test_manager.py`: simple manager that reads from WorkingMemory, assigns tasks
- **S8.2**: Create `tui/test_workers/test_worker.py`: simple worker that reads tasks, calls adapter generate(), saves results
- **S8.3**: Register both in `CapabilityGraph` via container
- **S8.4**: Test: manager receives prompt → assigns to worker → worker generates → saves result → manager reads → approves

---

## S9 — Orchestrator Panel (`tui/panels/orchestrator.py`)
- **S9.1**: `Input` widget for user message, [Send] button
- **S9.2**: `RichLog` for chat history (user right, assistant left)
- **S9.3**: Send handler: calls `MessageDispatcher.dispatch()`, displays response
- **S9.4**: Model selector `Select` widget: populate from `CapabilityGraph` adapters
- **S9.5**: Conversation tabs: `Tabs` widget, [+] new tab, [×] close tab

---

## S10 — Models Panel (`tui/panels/models.py`)
- **S10.1**: Retrieve `ModelCatalog`, list available models
- **S10.2**: Display `DataTable`: Name, Size, Quantization, Status
- **S10.3**: [Pull] button: calls `ollama pull` for selected model
- **S10.4**: [Load] / [Unload] buttons: call adapter load/unload

---

## S11 — Workers Panel (`tui/panels/workers.py`)
- **S11.1**: Retrieve workers from `CapabilityGraph`
- **S11.2**: Display `DataTable`: Name, Department, Model, Status
- **S11.3**: [Assign Model] button per worker: opens model selector
- **S11.4**: [Test] button: sends test task to worker, shows result

---

## S12 — Tasks Panel (`tui/panels/tasks.py`)
- **S12.1**: Retrieve `TaskStateMachine`, list tasks
- **S12.2**: Display `DataTable`: ID, Department, State, Age
- **S12.3**: State color-coded: RECEIVED=gray, QUEUED=yellow, EXECUTING=blue, COMPLETE=green, FAILED=red
- **S12.4**: [Create Task] button: opens modal, submits to state machine
- **S12.5**: [Cancel] button: cancels running task

---

## S13 — Scan and Close
- **S13.1**: Run `pytest` — must be ≥90%, no failures
- **S13.2**: Run `ruff` — must be 0 errors
- **S13.3**: Run `mypy` on `tui/` — 0 errors
- **S13.4**: Run harness: all 12 stages PASS
- **S13.5**: Update `CHANGELOG.md`, `PLANS.md`, `DEBT.md`
- **S13.6**: Run `/verify`, `/close`
