# SovereignAI UI Specification v1.0

## Overview

This document defines the complete user interface for SovereignAI v1.0 — a local-first, modular AI assistant. The UI is a single-page application (SPA) built with vanilla HTML/CSS/JS served by FastAPI. All panels share a common layout: **left sidebar navigation** + **main content area**.

---

## Global Layout

```
+----------------------------------------------------------+
|  [SovereignAI]  |  Panel Title  |  [User Menu]  |
+-----------------+---------------+-----------------+
|                 |                                    |
|  Orchestrator   |    MAIN CONTENT AREA               |
|  Workers        |                                    |
|  Tasks          |    (varies by panel)               |
|  Skills         |                                    |
|  Memory         |                                    |
|  Models         |                                    |
|  Adapters       |                                    |
|  Hardware       |                                    |
|  Options        |                                    |
|  Logs           |                                    |
|                 |                                    |
+-----------------+------------------------------------+
```

### Left Sidebar
- **Width**: 180px fixed
- **Background**: Dark theme (#1a1a1a)
- **Active item**: Highlighted with left border accent
- **Font**: System sans-serif, 14px
- **Items** (in order):
  1. Orchestrator
  2. Workers
  3. Tasks
  4. Skills
  5. Memory
  6. Models
  7. Adapters
  8. Hardware
  9. Options
  10. Logs

### Main Content Area
- **Background**: Slightly lighter dark (#222222)
- **Padding**: 20px
- **Scroll**: Auto when content overflows

### Location Bar Pattern
Every panel displays a breadcrumb location bar below the header: `Host:Panel[:Subcontext]`
- **Host**: Always `Localhost` in v1 (future: remote instances)
- **Panel**: Current sidebar panel name (Orchestrator, Workers, Tasks, etc.)
- **Subcontext**: Panel-specific context — backend (Memory), provider+format (Models), department (Workers), component (Hardware)
- Updates dynamically when tabs or selections change within the panel

---

## 1. Orchestrator Panel

The primary chat interface — the **only** conversational surface in the application. The Orchestrator is the CEO of SovereignAI: it translates the Owner's natural language into structured department requests, routes them to the correct department Managers, and synthesizes deliverables back into plain-language responses. It does not perform domain work itself — it delegates everything to departments.

```
+----------------------------------------------------------+
|  [SovereignAI]  |  Orchestrator  |  [User Menu]         |
+-----------------+----------------+------------------------+
|                 |  Localhost:Orchestrator                 |
|  Orchestrator   |  [Tab 1] [Tab 2] [+]  |  [Model ▼]      |
|  Workers        |                                          |
|  Tasks          |  +------------------------------------+  |
|  Skills         |  |  User: Fix the login bug           |  |
|  Memory         |  |  Assistant: Routed to Coding Dept  |  |
|  Models         |  |  [View Change Plan]                  |  |
|  Adapters       |  |                                    |  |
|  Hardware       |  |  Coding Deliverable ready           |  |
|  Options        |  |  Files: src/auth/routes.py (+3/-1)  |  |
|  Logs           |  |  Tests: 47 passed, 0 failed         |  |
|                 |  |  [Approve] [View Diff] [Reject]     |  |
|                 |  +------------------------------------+  |
|                 |                                          |
|                 |  [Message...                   ] [Send] |
+-----------------+------------------------------------------+
```

### Elements

| Element | Description |
|---------|-------------|
| **Location Bar** | `Localhost:Orchestrator` — breadcrumb showing Host:Panel. |
| **Conversation Tabs** | Horizontal tabs. Each tab = separate conversation thread with its own `conversation_id`. Close button (×) on each tab. |
| **New Tab Button (+)** | Creates new conversation with fresh `conversation_id`. |
| **Model Selector** | Dropdown listing available models from `/api/models`. Persists per conversation. Selected model handles intent translation and synthesis. |
| **Chat History** | Scrollable message list. User messages right-aligned, assistant left-aligned. |
| **Routing Trace** | Light inline indicator per assistant response: "Routed to Coding Department" / "Routed to Research, then Communication". Distinct from full Logs panel. |
| **Structured Input Requests** | Inline interactive elements for worker→user interrupts: buttons (boolean/choice), text field, file picker, checkboxes (multi_choice). |
| **Deliverable Cards** | Embedded summaries of department deliverables (code diffs, research reports, training results) with action buttons — not raw dumps. |
| **Message Input** | Single-line text input at bottom. Expands for multi-line (Shift+Enter). |
| **Send Button** | Submits message to `/api/dispatch` with selected model and conversation context. |

### Orchestrator Behavior

- **Single conversational surface:** No other panel (Workers, Tasks, Skills, Memory, Models, Adapters, Hardware, Options, Logs) contains chat. All Owner-facing conversation happens here.
- **Intent translation:** Converts "fix the login bug" → structured `CodingTask` with acceptance criteria, target project, and inferred scope.
- **Department routing:** Single-department requests route directly. Multi-department requests are sequenced (e.g., Coding → Communication for "build feature, then announce it").
- **No silent failures:** If a department degrades or fails, the Orchestrator surfaces it plainly in the chat response, not buried in logs.
- **Multiple windows:** Each open Orchestrator window subscribes to the same underlying conversation state; sending from one updates all.

### Backend Integration
- `GET /api/models` — populate model selector
- `POST /api/dispatch` — send message (includes `model_id`, `conversation_id`, structured department request)
- `GET /api/conversations/{id}` — load chat history
- `GET /api/orchestrator/routing-trace/{request_id}` — light routing trace per exchange

---
## 2. Workers Panel

Displays all registered workers organized by department with location breadcrumb.

```
+----------------------------------------------------------+
|  [SovereignAI]  |  Workers  |  [User Menu]               |
+-----------------+----------+-----------------------------+
|                 |  Localhost:Workers                     |
|  Orchestrator   |  [Coding Department] [Library]          |
|  Workers        |  [Education Department] [Research Dept] |
|  Tasks          |                                          |
|  Skills         |  +---------------+  +---------------+     |
|  Memory         |  | Coding Manager|  | Python Coder  |     |
|  Models         |  | [Model]       |  | [Model]       |     |
|  Adapters       |  | [Options]     |  | [Options]     |     |
|  Hardware       |  +---------------+  +---------------+     |
|  Options        |  +---------------+  +---------------+     |
|  Logs           |  | C++ Coder     |  | Rust Coder    |     |
|                 |  | [Model]       |  | [Model]       |     |
|                 |  | [Options]     |  | [Options]     |     |
|                 |  +---------------+  +---------------+     |
+-----------------+------------------------------------------+
```

### Elements

| Element | Description |
|---------|-------------|
| **Location Bar** | Breadcrumb showing `Host:Panel` — e.g. `Localhost:Workers`. |
| **Department Tabs** | Coding Department, Library, Education Department, Research Department — horizontal tabs. Active tab has filled background. |
| **Worker Cards** | Grid layout. Each card shows: worker name, [Model] button, [Options] button. Cards have border with slight shadow. |
| **Model Button** | Opens model assignment modal for this worker |
| **Options Button** | Opens worker configuration panel |

### Department Tab Behavior
- **Tab click** → filters worker cards to show only workers in that department
- **Active department** → tab background filled, worker cards displayed below
- **Default state**: Coding Department selected

### Backend Integration
- `GET /api/workers?department={name}` — list workers filtered by department
- `POST /api/departments` — create new department
- `GET /api/departments` — list all departments

---
## 3. Tasks Panel

Visualizes the task pipeline across all departments and allows manual task creation. Tasks are the universal work unit — every department's operations (Coding Tasks, Research Jobs, Training Runs) surface here.

```
+----------------------------------------------------------+
|  [SovereignAI]  |  Tasks  |  [User Menu]                 |
+-----------------+---------+------------------------------+
|                 |  Localhost:Tasks                        |
|  Orchestrator   |  [Create Task] [Refresh] [Filter ▼]     |
|  Workers        |                                          |
|  Tasks          |  ID        | Dept      | State    | Age  |
|  Skills         |  ----------+-----------+----------+------|
|  Memory         |  task-001  | Coding    | COMPLETE | 2m   |
|  Models         |  task-002  | Research  | EXECUTING| 15m  |
|  Adapters       |  task-003  | Education | AWAITING | 30m  |
|  Hardware       |  task-004  | Coding    | QUEUED   | 1m   |
|  Options        |  task-005  | Research  | FAILED   | 45m  |
|  Logs           |  task-006  | Education | DATASET  | 5m   |
|                 |                                          |
|                 |  Pipeline: RECEIVED → QUEUED → EXECUTING |
|                 |            → COMPLETE / FAILED           |
+----------------------------------------------------------+
```

### Elements

| Element | Description |
|---------|-------------|
| **Location Bar** | `Localhost:Tasks` — breadcrumb showing Host:Panel. |
| **Create Task Button** | Opens modal to manually submit a task to any department. |
| **Refresh Button** | Re-fetches task list. |
| **Filter Dropdown** | Filter by department, state, or date range. |
| **Task Table** | Columns: ID, Department, State, Age (time since creation). Sortable. |
| **State Colors** | RECEIVED (gray), QUEUED (yellow), EXECUTING (blue), COMPLETE (green), FAILED (red), AWAITING_BRIEF (orange — Education waiting on Research), DATASET_CONSTRUCTION (purple — Education), TRAINING (purple), EVALUATING (purple), EXPORTING (purple). |
| **Pipeline Diagram** | Static visual showing task lifecycle. |
| **Task Detail** | Click a task row to expand: stage progress, live logs, deliverable preview, cancel button. |

### Department-Specific Task States

| Department | Additional States |
|------------|-------------------|
| **Coding** | PLANNING, IMPLEMENTATION, TESTING, REVIEW, AWAITING_APPROVAL |
| **Research** | PLANNING, SOURCE_DISCOVERY, DEEP_RETRIEVAL, EVALUATION, FACT_CHECKING, SYNTHESIS |
| **Education** | AWAITING_BRIEF, DATASET_CONSTRUCTION, TRAINING, EVALUATING, EXPORTING, QUALITY_GATE_FAILED |
| **Library** | OBSERVING, CLASSIFYING, LINKING, INDEXING |

### Backend Integration
- `GET /api/tasks` — list all tasks across all departments
- `POST /api/tasks` — create new task manually
- `GET /api/tasks/{id}` — get task details with stage progress
- `POST /api/tasks/{id}/cancel` — cancel a running task

---
## 4. Skills Panel

Displays registered skills organized by category. Skills are the tools departments use — terminal access, file operations, web search, git, test runners. None are owned by any department; all are registered externally and consumed via the capability graph.

```
+----------------------------------------------------------+
|  [SovereignAI]  |  Skills  |  [User Menu]                |
+-----------------+----------+-----------------------------+
|                 |  Localhost:Skills                      |
|  Orchestrator   |  [Tools] [Adapters] [Internal] [User]  |
|  Workers        |  [+]                                    |
|  Tasks          |                                          |
|  Skills         |  +------------------+  +----------------+|
|  Memory         |  | terminal_skill   |  | file_read      ||
|  Models         |  | v1.2.0           |  | v0.9.1         ||
|  Adapters       |  | [Run] [Config]   |  | [Run] [Config] ||
|  Hardware       |  +------------------+  +----------------+|
|  Options        |  +------------------+  +----------------+|
|  Logs           |  | web_search_skill |  | git_commit     ||
|                 |  | v0.1.0           |  | v1.0.0         ||
|                 |  | [Run] [Config]   |  | [Run] [Config] ||
|                 |  +------------------+  +----------------+|
+-----------------+------------------------------------------+
```

### Elements

| Element | Description |
|---------|-------------|
| **Location Bar** | `Localhost:Skills` — breadcrumb showing Host:Panel. |
| **Category Tabs** | Tools (terminal, file ops), Adapters (web search, APIs), Internal (self-correction, tracing), User (custom skills). |
| **Install Skill (+)** | Upload new skill package (ZIP with manifest + code). |
| **Skill Cards** | Name, version, [Run] button (manual invocation), [Config] button (settings). |
| **Skill Manifest** | Each skill declares: capabilities provided, required adapters, health check endpoint. |

### Backend Integration
- `GET /api/capabilities?category=skill` — list skills
- `POST /api/skills/install` — upload new skill
- `POST /api/skills/{id}/invoke` — manual invocation
- `GET /api/skills/{id}/config` — read configuration
- `POST /api/skills/{id}/config` — update configuration

---
## 5. Memory Panel

Memory exploration interface with backend switching, view mode controls, and multi-format visualization.

```
+----------------------------------------------------------+
|  [SovereignAI]  |  Memory  |  [User Menu]                |
+-----------------+----------+-----------------------------+
|                 |  Localhost:Memory:Sqlite                 |
|  Orchestrator   |  [Sqlite] [Obsidian]                     |
|  Workers        |  [○] [≡] [Aa] [☐] [⊞]                  |
|  Tasks          |  [Neural Map] [List] [Other Format]      |
|  Skills         |                                          |
|  Memory         |                                          |
|  Models         |                                          |
|  Adapters       |                    Neural Map            |
|  Hardware       |                                          |
|  Options        |                                          |
|  Logs           |                                          |
|                 |                                          |
+-----------------+------------------------------------------+
```

### Elements

| Element | Description |
|---------|-------------|
| **Location Bar** | Breadcrumb showing `Host:Panel:Backend` — e.g. `Localhost:Memory:Sqlite`. Updates when backend or panel changes. |
| **Backend Tabs** | Sqlite, Obsidian — horizontal tabs selecting the active memory storage backend. Active tab has filled background. |
| **Toolbar** | Icon row: ○ Toggle switch (view mode on/off), ≡ List/menu (layout options), Aa Text formatting (font/size settings), ☐ Checkboxes (multi-select mode), ⊞ Grid view (column layout toggle). |
| **View Tabs** | Neural Map, List, Other Format — secondary tab row below toolbar. Switches the main content visualization mode. |
| **Neural Map** | Interactive force-directed graph of memory nodes and relationships. Placeholder text shown when empty. |
| **Node** | Represents a memory episode, concept, or entity |
| **Edge** | Represents relationship between memories |

### Toolbar Icon Details

| Icon | Name | Function |
|------|------|----------|
| ○ | Toggle Switch | Switches between two primary view states (e.g. graph vs simplified) |
| ≡ | List/Menu | Opens layout options dropdown (compact, comfortable, spacious) |
| Aa | Text Settings | Opens font size / family selector |
| ☐ | Checkbox Mode | Enables multi-select for bulk operations on memory items |
| ⊞ | Grid View | Toggles between single-pane and multi-column grid layout |

### Neural Map Interaction
- **Click node** — show details panel with episode content, timestamp, source
- **Drag node** — rearrange graph layout
- **Scroll** — zoom in/out
- **Double-click** — expand connected nodes

### Data Flow
1. Memory adapters (episodic, procedural, trace, working) store data in selected backend
2. Librarian indexes and creates graph relationships
3. Neural Map visualizes the graph using D3.js or Cytoscape.js
4. List view shows tabular data for search/filter

### Backend Integration
- `GET /api/memory/backends` — list available backends
- `GET /api/memory/graph` — get graph data (nodes + edges)
- `GET /api/memory/episodes` — list episodes (List view)
- `POST /api/memory/search` — search memory content

---
## 6. Models Panel

Multi-provider model browser with two-level tab navigation and location breadcrumb.

```
+----------------------------------------------------------+
|  [SovereignAI]  |  Models  |  [User Menu]                |
+-----------------+----------+-----------------------------+
|                 |  Localhost:Models:Huggingface:GGUF    |
|  Orchestrator   |  [Hugging Face] [Ollama] [Models.dev]  |
|  Workers        |  [GGUF] [Pytorch] [Safetensors]         |
|  Tasks          |                                          |
|  Skills         |                                          |
|  Memory         |                                          |
|  Models         |                                          |
|  Adapters       |                                          |
|  Hardware       |                                          |
|  Options        |                                          |
|  Logs           |                                          |
|                 |                                          |
+-----------------+------------------------------------------+
```

### Elements

| Element | Description |
|---------|-------------|
| **Location Bar** | Breadcrumb showing `Host:Panel:Provider:Format` — e.g. `Localhost:Models:Huggingface:GGUF`. Updates when provider or format tab changes. |
| **Provider Tabs** | Hugging Face, Ollama, Models.dev — top-level horizontal tabs. Active tab has filled background. Selects which provider's model catalog to display. |
| **Format Sub-Tabs** | GGUF, Pytorch, Safetensors — second-level horizontal tabs below provider tabs. Filters models by file format within the selected provider. |
| **Content Area** | Model listing table/cards. Empty when no models fetched. |

### Two-Level Tab Behavior
- **Provider tab click** → updates Location Bar provider segment, loads provider's model cache, resets format sub-tab to default (GGUF)
- **Format sub-tab click** → updates Location Bar format segment, filters displayed models by file extension
- **Default state**: Hugging Face → GGUF selected

### Backend Integration
- `GET /api/models?provider={name}&format={fmt}` — list from local cache
- `POST /api/models/fetch` — run scraper for provider
- `POST /api/models/pull` — download model file
- `GET /api/models/cache/status` — last updated, model count per provider

---
## 7. Adapters Panel

Shows registered adapters with health status.

```
+----------------------------------------------------------+
|  Adapters                                                  |
+------------------------------------------------------------+
|                                                            |
|  Name              | Status      | Capabilities | Actions   |
|--------------------+-------------+--------------+-----------|
|  llama_cpp_adapter | HEALTHY 🟢  | model_inference| [Test]  |
|  ollama_adapter    | HEALTHY 🟢  | model_inference| [Test]  |
|  episodic_memory   | HEALTHY 🟢  | memory       | [Test]  |
|  websearch_skill   | HEALTHY 🟢  | tool         | [Test]  |
|                                                            |
|  [Register Adapter]                                        |
+------------------------------------------------------------+
```

### Elements

| Element | Description |
|---------|-------------|
| **Status Indicator** | HEALTHY (green), DEGRADED (yellow), UNAVAILABLE (red) |
| **Capabilities** | Comma-separated capability names |
| **Test Button** | Runs adapter health check |
| **Register Adapter** | Manual adapter registration |

### Backend Integration
- `GET /api/capabilities?category=adapter` — list adapters
- `POST /api/adapters/register` — register new adapter

---

## 8. Hardware Panel

Hardware resource monitoring with component tabs, worker usage cards, and system-wide graphs.

```
+----------------------------------------------------------+
|  [SovereignAI]  |  Hardware  |  [User Menu]              |
+-----------------+----------+-----------------------------+
|                 |  Localhost:Hardware                    |
|  Orchestrator   |  [GPU1] [GPU2] [CPU] [RAM] [HDD] [Network] |
|  Workers        |                                          |
|  Tasks          |  Utilisation: 20% GPU Memory 20/100GB   |
|  Skills         |  Temperature 20c                         |
|  Memory         |                                          |
|  Models         |  +---------------+ +---------------+     |
|  Adapters       |  | Worker 1      | | Worker 2      |     |
|  Hardware       |  | Usage Graph   | | Usage Graph   |     |
|  Options        |  +---------------+ +---------------+     |
|  Logs           |  Utilisation 5%   Utilisation 5%          |
|                 |  +---------------+ +---------------+     |
|                 |  | Worker 3      | | Worker 4      |     |
|                 |  | Usage Graph   | | Usage Graph   |     |
|                 |  +---------------+ +---------------+     |
|                 |  Utilisation 5%   Utilisation 5%          |
|                 |                                          |
|                 |  +------------------------------------+  |
|                 |  |         TEMPERATURE GRAPH          |  |
|                 |  +------------------------------------+  |
|                 |                                          |
|                 |  +------------------------------------+  |
|                 |  |           USAGE GRAPH              |  |
|                 |  +------------------------------------+  |
+-----------------+------------------------------------------+
```

### Elements

| Element | Description |
|---------|-------------|
| **Location Bar** | Breadcrumb showing `Host:Panel` — e.g. `Localhost:Hardware`. |
| **Component Tabs** | GPU1, GPU2, CPU, RAM, HDD, Network — horizontal tabs selecting which hardware component to focus on. Active tab has filled background. |
| **Summary Line** | Key metrics for active component: `Utilisation: X%`, `GPU Memory Y/ZGB`, `Temperature Xc` |
| **Worker Usage Cards** | 2×2 grid of cards showing per-worker resource usage. Each card: worker name, mini usage graph, utilisation percentage below. |
| **Temperature Graph** | Large area chart showing temperature history across all workers/components over time |
| **Usage Graph** | Large area chart showing overall resource utilisation history over time |

### Component Tab Behavior
- **Tab click** → updates summary line metrics, filters worker cards to show relevant workers for that component, switches graph data source
- **GPU tabs** → show GPU memory, temperature, CUDA utilisation
- **CPU tab** → show core count, clock speed, thread utilisation
- **RAM tab** → show used/total, speed, type
- **HDD tab** → show used/total, drive model, type
- **Network tab** → show adapter name, SSID, protocol, IP, signal strength

### Backend Integration
- `GET /api/hardware` — static snapshot
- `GET /api/hardware/stream` — SSE stream for real-time updates

---
## 9. Options Panel

System configuration, database/service management, and department-specific settings. The Owner configures execution policies, source authority, retention rules, and approval thresholds here.

```
+----------------------------------------------------------+
|  [SovereignAI]  |  Options  |  [User Menu]               |
+-----------------+-----------+------------------------------+
|                 |  Localhost:Options                      |
|  Orchestrator   |  [Databases] [Services] [Adapters]       |
|  Workers        |  [Skills] [Coding Dept] [Research Dept]  |
|  Tasks          |  [Education Dept] [Library] [Security]   |
|  Skills         |                                          |
|  Memory         |  DATABASES TAB:                          |
|  Models         |  +------------------+  +----------------+|
|  Adapters       |  | HuggingFace      |  | Ollama         ||
|  Hardware       |  | Status: Healthy  |  | Status: Stopped||
|  Options        |  | Models: 1,247    |  | Models: 0      ||
|  Logs           |  | [Fetch] [Uninstall] | [Start] [Stop] ||
|                 |  +------------------+  +----------------+|
|                 |                                          |
|                 |  CODING DEPT TAB:                        |
|                 |  Auto-commit low-risk: [☑]               |
|                 |  Terminal sandbox: [Docker ▼]            |
|                 |  Max review cycles: [3 ▼]                |
+-----------------+------------------------------------------+
```

### Elements

| Element | Description |
|---------|-------------|
| **Location Bar** | `Localhost:Options` — breadcrumb showing Host:Panel. |
| **Category Tabs** | Databases, Services, Adapters, Skills, Coding Dept, Research Dept, Education Dept, Library, Security. |
| **Database Cards** | Name, status, model count, last updated, [Fetch], [Uninstall]. |
| **Service Cards** | Name, status, PID, port, uptime, memory, [Start], [Stop]. |
| **Department Settings** | Per-department configuration panels: execution policy, approval thresholds, model preferences, source authority tiers. |
| **Source Authority** | Research Department trust tier management — promote/demote domains. |
| **Retention Policy** | Memory retention rules, pruning schedules, consent defaults. |

### Department Configuration Panels

| Panel | Settings |
|-------|----------|
| **Coding Dept** | Auto-commit policy, terminal sandbox mode, max review cycles, per-action approval rules |
| **Research Dept** | Default search depth, source tier priority, max concurrent workers, authority DB |
| **Education Dept** | Default training backend, base model, GGUF quantization, checkpoint retention, synthetic data teacher |
| **Library** | Retention policy, consent defaults, graph pruning schedule, distillation thresholds |
| **Security** | Blocklist management, execution policy overrides, audit log viewer |

### Backend Integration
- `GET /api/databases` — list databases
- `POST /api/databases/{name}/fetch` — run fetcher
- `POST /api/databases/{name}/uninstall` — remove database
- `GET /api/services` — list services
- `POST /api/services/{name}/start` — start service
- `POST /api/services/{name}/stop` — stop service
- `GET /api/options/{department}` — read department settings
- `POST /api/options/{department}` — update department settings

---
## 10. Logs Panel

Real-time trace event viewer with filtering. Consumes `/api/traces/stream` SSE — the same stream the Library observes for memory building. All components emit structured trace events via the constructor-injected TraceEmitter (P9 — observability by default).

```
+----------------------------------------------------------+
|  [SovereignAI]  |  Logs  |  [User Menu]                   |
+-----------------+--------+-------------------------------+
|                 |  Localhost:Logs                        |
|  Orchestrator   |  Level: [All ▼]  Component: [All ▼]    |
|  Workers        |  [🔍 Search]  [⏸ Pause]  [⏵ Resume]    |
|  Tasks          |                                          |
|  Skills         |  Timestamp      | Lvl | Component      |
|  Memory         |  ---------------+-----+----------------|
|  Models         |  19:45:32       | INFO| ModelCatalog   |
|  Adapters       |  19:45:33       | WARN| conformance    |
|  Hardware       |  19:46:01       | DEBUG| CapabilityGraph|
|  Options        |  19:46:15       | ERROR| CodingManager  |
|  Logs           |  19:46:16       | INFO| EducationMgr   |
|                 |  ...            | ... | ...            |
+----------------------------------------------------------+
```

### Elements

| Element | Description |
|---------|-------------|
| **Location Bar** | `Localhost:Logs` — breadcrumb showing Host:Panel. |
| **Level Filter** | All, ERROR, WARN, INFO, DEBUG, TRACE. |
| **Component Filter** | Dropdown populated from unique components (CodingManager, ResearchManager, EducationManager, Librarian, etc.). |
| **Search** | Text search across messages. |
| **Pause/Resume** | Pauses real-time SSE updates; Resume reconnects. |
| **Log Table** | Columns: Timestamp, Level (color-coded), Component, Message. |
| **Trace Detail** | Click a row to expand: full structured payload, correlation ID, originating task/job ID. |

### Color Coding

| Level | Color | Usage |
|-------|-------|-------|
| ERROR | Red | Component failures, exceptions, blocked operations |
| WARN | Yellow | Degraded operations, retries, policy violations |
| INFO | Green | Normal operations, state transitions, completions |
| DEBUG | Gray | Detailed internal state, worker assignments, stage progress |
| TRACE | Light gray | Verbose per-event logging, function entry/exit |

### Backend Integration
- `GET /api/traces/history` — initial load (recent N events)
- `GET /api/traces/stream` — SSE for real-time events
- `GET /api/traces/search?q={query}` — text search
- `GET /api/traces/component/{name}` — filter by component

---
## Color Scheme

| Element | Hex | Usage |
|---------|-----|-------|
| Background (sidebar) | #1a1a1a | Sidebar background |
| Background (main) | #222222 | Main content background |
| Background (card) | #2a2a2a | Card/panel backgrounds |
| Text (primary) | #e0e0e0 | Headings, primary text |
| Text (secondary) | #888888 | Labels, metadata |
| Accent (blue) | #4a9eff | Model selector, Send button, active states |
| Accent (red) | #ff4a4a | Tabs, close buttons, errors |
| Accent (green) | #4aff4a | Healthy status, success |
| Accent (yellow) | #ffaa4a | Warnings, queued states |
| Border | #333333 | Card borders, dividers |

---

## Responsive Behavior

- **Desktop (>1024px)**: Full layout as shown
- **Tablet (768-1024px)**: Sidebar collapses to icon-only (hover to expand)
- **Mobile (<768px)**: Sidebar becomes hamburger menu, cards stack vertically

---

## Accessibility

- All interactive elements have `:focus` states
- Color is not the sole indicator of status (icons + text)
- ARIA labels on all buttons and form elements
- Keyboard navigation: Tab cycles through interactive elements, Enter activates

---

## Backend API Summary

| Endpoint | Method | Panel | Description |
|----------|--------|-------|-------------|
| `/api/models` | GET | Models, Orchestrator | List available models |
| `/api/models/pull` | POST | Models | Download model |
| `/api/workers` | GET | Workers | List workers |
| `/api/departments` | GET/POST | Workers | List/create departments |
| `/api/tasks` | GET/POST | Tasks | List/create tasks |
| `/api/capabilities` | GET | Skills, Adapters | List capabilities |
| `/api/databases` | GET | Options | List databases |
| `/api/databases/{name}/fetch` | POST | Options | Run fetcher |
| `/api/databases/{name}/uninstall` | POST | Options | Remove database |
| `/api/services` | GET | Options | List services |
| `/api/services/{name}/start` | POST | Options | Start service |
| `/api/services/{name}/stop` | POST | Options | Stop service |
| `/api/hardware` | GET | Hardware | Static snapshot |
| `/api/hardware/stream` | GET | Hardware | Real-time SSE stream |
| `/api/traces/history` | GET | Logs | Recent trace events |
| `/api/traces/stream` | GET | Logs | Real-time SSE stream |
| `/api/dispatch` | POST | Orchestrator | Send chat message |
| `/api/auth/status` | GET | Global | Check auth status |

---

## Deferred UI Work

The following panels are placeholders or partially implemented:

| Panel | Status | Deferred To |
|-------|--------|-------------|
| Orchestrator | Chat surface functional, no structured input rendering | Plan 21 |
| Workers | Department tabs present, worker cards static | Plan 21 |
| Tasks | Table present, no stage progress detail view | Plan 21 |
| Models | Two-level tabs present, content area empty | Plan 21 |
| Skills | Category tabs present, cards static | Plan 22 |
| Adapters | Empty state | Plan 22 |
| Hardware | Component tabs present, graphs placeholder | Plan 22 |
| Options | Category tabs present, department settings not wired | Plan 23 |
| Memory | Backend/view tabs present, Neural Map placeholder | Plan 24+ (Librarian + Neural Map) |
| Logs | Table present, no component filtering | Plan 21 |

## UI Implementation Order

| Plan | Panels | Key Features |
|------|--------|--------------|
| Plan 21 | Orchestrator, Workers, Models, Tasks, Logs | Conversation tabs, model selector, department tabs, two-level model tabs, task state colors, log filtering |
| Plan 22 | Skills, Adapters, Hardware | Category tabs, health status, worker usage cards, temperature/usage graphs |
| Plan 23 | Options | Database/service actions, department configuration panels, source authority, retention policy |
| Plan 24+ | Memory | Neural Map graph visualization (D3.js/Cytoscape), backend switching, entity traversal |

---

*Document version: 1.2*
*Date: 2026-07-01 (revised with department specs)*
*Author: Architect (SovereignAI)*
