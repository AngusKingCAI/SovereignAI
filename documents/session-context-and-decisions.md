# SovereignAI — Session Context & Decisions Document

**Last updated**: 2026-06-29
**Purpose**: Give a new GLM chat full context to continue without re-reading every log and adjudication. Copy this file into the new chat's upload folder.

---

## 1. Project Overview

SovereignAI is a local-first, modular AI assistant framework for a single user. Python v1, Rust-migratable later. Windows-only for v1. Runs locally by default, escalates to cloud when needed.

**Repo**: https://github.com/AngusKingCAI/SovereignAI · **Branch**: `main`
**Executor tree**: `C:/SovereignAI/` · **Architect review clone**: `/home/z/my-project/sovereignai-review/`
**Canonical vision**: `documents/project-vision-Rev5.md` (locked — 14 principles, 40 success criteria)
**Governance**: `AGENTS.md` (AR + OR rules), `LANDMINES.md` (failure patterns), `AI_HANDOFF.md` (process guide)

---

## 2. Current State (after prompt-14)

### Completed prompts
| Prompt | Tag | Description | Tests | Coverage |
|---|---|---|---|---|
| prompt-0 through prompt-0.4 | various | Bootstrap + governance patches | N/A | N/A |
| prompt-1 | prompt-1 | Core scaffold (EventBus, TraceEmitter, DI, Composition Root) | 22 | N/A |
| prompt-2 | prompt-2 | Discovery layer (manifest parser, capability graph) | 40 | N/A |
| prompt-3 | prompt-3 | Execution layer (routing, lifecycle, task state machine, DAG validator) | 75 | N/A |
| prompt-4 | prompt-4 | Interface layer (Auth, CapabilityAPI, Relay placeholder) | 107 | N/A |
| prompt-5 | prompt-5 | Scan 5 | 106 | 96% |
| prompt-6 | prompt-6 | FastAPI Web UI | 117 | N/A |
| prompt-7 | prompt-7 | MessageDispatcher, WebSearchSkill, OllamaAdapter, HardwareProbe | 149 | N/A |
| prompt-8 | prompt-8 | 9-panel sidebar UI with observability | 158 | N/A |
| prompt-9 | prompt-9 | Web Authentication | 169 | N/A |
| prompt-10 through 10.5 | various | Scan 10 + governance patches (OR71-85, L32-39, close.md fixes, Web UI hotfixes) | 183 | 94% |
| prompt-11 | prompt-11 | Memory layer (Librarian + 4 backends + crash recovery) | ~250 | ~93% |
| prompt-12 | prompt-12 | Versioning (SemVer, negotiator, compatibility matrix) | ~280 | ~92% |
| prompt-13 | prompt-13 | Test framework (conformance, contract, property tests) | ~290 | ~91% |
| prompt-14 | prompt-14 | Education department (Teacher worker, self-correction skill) | 320 | 91% |

### Current baselines
- **Tests**: 320 passed, 9 skipped
- **Coverage**: 91% (floor: 89% per OR77)
- **Ruff**: 0 errors
- **Mypy**: 0 errors
- **Bandit**: 636 Low (B101 — test assertions), 2 Medium (B615 — HuggingFace, `#nosec` added)
- **Vulture**: 0 findings
- **detect-secrets**: pass

### Next in queue
| Slot | Plan | Description |
|---|---|---|
| 1 | Scan 15 | Third whole-repo scan — fix close.md `git rm` bug, add OR86, scan |
| 2 | Plan 16 | Logging & observability — fix Log Drawer, add Orchestrator "thinking", verify trace persistence, add REST trace API |
| 3 | Plan 17 | Memory panel API + UI wiring |
| 4 | Plan 18 | Tasks panel — active/scheduled/completed tabs + task detail + manual task creation |
| 5 | Plan 19 | Tools panel — list + run tools with input schema forms |
| 6 | Scan 20 | Fourth whole-repo scan |

---

## 3. Governance Rules (current count: 20 AR + ~80 OR + 40 landmines)

Key rules added in recent patches:

| Rule | What it does | Source |
|---|---|---|
| OR71 | Run workflow commands verbatim — re-read close.md fresh, don't paraphrase | L32 |
| OR75/OR80/OR83 | `git add -A` for ALL commits — no explicit `git add <file>` lists | L34, L35 |
| OR76 | No premature tags — verify `git tag --list prompt-{N}` is empty before creating | L36 |
| OR77 | Coverage mandatory at `/close` — STOP if >5% drop from baseline | L37 |
| OR78 | Bandit Low count reconciliation at every `/close` | L38 |
| OR79 | Re-read plan + AGENTS.md after quota exhaustion | L39 |
| OR82 | Never `git mv` — use `mv` + `git add -A` + verify `git ls-files` | L34 |
| OR84 | Rule numbers are NEVER renumbered — gaps are permanent | Numbering policy |
| OR86 | Backend + UI in the same plan — no backend capability without a UI surface | UI questionnaire |

**L40 (pending fix in Scan 15)**: close.md Step 17 said "run `git rm`" which DELETES files. Fixed to auto-run `git add -A` instead.

---

## 4. Architectural Decisions

### 4.1 Company metaphor
SovereignAI is structured as a company:
- **Owner (User)** → **Orchestrator (CEO)** → **Department Managers** → **Workers**
- Workers never talk to Owner directly — everything routes through Orchestrator
- v1 Departments: Coding, Research, Education, Library (Communication/Operations deferred — use adapters for external comms like Telegram/Google)
- Initial implementation: 1 Manager + 1 Worker per department, expand later

### 4.2 Department specs (in `documents/`)
Five detailed spec files exist:
- `SovereignAI_Orchestrator_Spec.md` — CEO's office, intent translation, routing
- `SovereignAI_Coding_Department_Spec.md` — software development (Reader/Planner/Writer/Test/Review/Debug workers)
- `SovereignAI_Research_Department_Spec.md` — multi-source research (Source Discovery/Deep Retrieval/Evaluation/Synthesis/Fact-Check workers)
- `SovereignAI_Library_Department_Spec.md` — memory/documentation (observes trace stream, builds episodic records unprompted)
- `SovereignAI_Education_Department_Spec.md` — expert model training (QLoRA, pruning, distillation, GGUF export)

**Implementation order**: Library first (foundational), then Coding (most useful), then Research, then Education (last — depends on Research + Models panel + ML infra).

### 4.3 Models panel
Full design reference at `/home/z/my-project/download/models-panel-design-reference.md`. Key decisions:
- Pluggable adapter (`adapters/internal/model_catalog/`), NOT core (per P1)
- Standalone SQLite (`~/.sovereignai/model_catalog.db`), NOT a memory backend
- Sync runs as a task via TaskStateMachine, NOT a custom endpoint
- VRAM badges: "VRAM" / "VRAM + RAM" / "N/A"
- [Installed] tab alongside provider tabs
- 4-plan arc: catalog foundation (Ollama) → downloader → verifier → HuggingFace + multi-provider
- Deferred until after core is complete (earliest: Plans 16-19)

### 4.4 Memory architecture
- 4 memory types: episodic (SQLite), procedural (JSON), trace (SQLite), working (in-process)
- Each backend owns a separate file: `~/.sovereignai/episodic.db`, `trace.db`, `procedural_memory.json`
- Librarian routes by capability name string (not a closed enum)
- Crash recovery: shutdown marker file, auto-discard incomplete tasks, no side-effect replay
- Library Department subscribes to trace stream → builds episodic memory from observations (departments never explicitly write to memory)

### 4.5 Versioning
- Core components (`core = true` in manifest, installed inside sovereignai package): strict versioning, fatal on mismatch
- Plugins: lenient versioning, disable on mismatch
- `core = true` is IGNORED for components outside the sovereignai package directory (prevents third-party spoofing)
- Compatibility matrix: standalone JSON with content_hash tracking, backup file, atomic writes

### 4.6 Conformance testing
- Runner lives in `sovereignai/conformance/` (runtime-safe, shipped in production)
- Test suites live in `tests/conformance/` (pytest-discoverable)
- Gate is fail-CLOSED for first-party components, fail-OPEN for third-party
- Third-party tests discovered via Python entry points
- LRU cache (maxsize=1024) for conformance results

---

## 5. UI Decisions (from questionnaire, 2026-06-29)

### 5.1 Panel status
| # | Panel | Status | Target |
|---|---|---|---|
| 1 | Orchestrator | ✅ Works | Add "working..." expandable status showing live trace events for the task (like GLM's UI) |
| 2 | Workers | ✅ Works (flat list) | Rename to "Departments" later; for now keep "Workers" label. Tabs per department, click to expand Manager + Workers, click worker → settings tabs [Model] [Rules] [Datasets] [History] |
| 3 | Tasks | ✅ Works (empty) | 3 tabs: Active, Scheduled, Completed. Click task → detail (initial prompt, Orchestrator translation, departments, workers, memory used). User can manually create tasks bypassing Orchestrator. N8N flow later. |
| 4 | Skills | ✅ Works (1 skill) | Split into Tools tab (atomic, first priority) + Skills tab (composite, later). Tools have "Run" button with input schema form. |
| 5 | Memory | ❌ 404 | Tabs per memory type (Episodic, Procedural, Trace, Working). Simple list view first, grouped by category (Chat Logs, Websites, PDFs). Neural network map later. |
| 6 | Models | ❌ Placeholder | Full catalog per models-panel-spec. Provider tabs → family → model → version. [Installed] tab. Pull/verify. Deferred to Plans 16-19 arc. |
| 7 | Adapters | ✅ Works | Show all adapters with health status + registered tools. Management (install/remove) later. |
| 8 | Hardware | ✅ Works | Keep as-is for now. Real-time usage + model loading controls later. |
| 9 | Options | ✅ Partial (auth) | Keep as-is for now. Full settings later. |

### 5.2 Key UI principles
- **Log/trace stream is the central nervous system** — everything reads from it:
  - Log Drawer: ALL events, raw, filterable
  - Orchestrator "thinking": filtered by task_id, human-readable
  - Task detail: filtered by task_id, execution history
  - Library: observed → episodic memory
  - Memory panel: persisted traces, browsable
- **OR86**: Backend + UI in the same plan (no backend without UI)
- **Empty panels**: show "Not yet available" with description
- **Ad-hoc API format**: no standard envelope, each endpoint returns its own shape

---

## 6. Process Decisions

### 6.1 Current phase
- **Round Table vetoed** for the UI/functional batch (Plans 16-19). User iterates directly with Devin.
- GLM drafts initial prompts, then steps back. Devin reports when working or stuck.
- Scan 15 (prompt-15) is the last governance plan before UI work starts.

### 6.2 Plan structure (Rev10 fix)
Plans have this structure (fixed after prompt-13 close failure):
```
## S0 — Opening
## Plan Body (S1–Sn)
## Closing          ← RIGHT after body, so Executor runs /close immediately
## STOP Conditions  ← Reference appendix
## Files WILL Create/Edit/NOT Edit  ← Reference appendix
```
No Adjudication summary (removed — it's Architect-only context that confused the Executor).

### 6.3 close.md Step 17 fix (pending Scan 15)
The `git rm` instruction in Step 17's verification check was DELETING files instead of moving them. Fixed to auto-run `git add -A`. Scan 15 applies this fix.

### 6.4 Numbering policy (OR84)
Rule and landmine numbers are NEVER renumbered. Gaps from retired slots are permanent. New rules: OR87+. New landmines: L41+. New decisions: D6+.

---

## 7. Open Items

### 7.1 Deferred to DEBT.md
- Cross-process GPU lock (Plan 14 limitation — Ollama can starve during fine-tuning)
- Procedural memory consumer wiring (RoutingEngine reads procedural memory — future plan)
- Full PII filter (Plan 14 has minimal regex; proper filter deferred)
- Full model versioning/rollback (Plan 14 has basic registry; full versioning deferred)
- Dedicated task-state ledger (crash recovery currently depends on trace DB)
- Batched/background trace inserts (currently synchronous SQLite writes)
- Separate `sovereignai-education` package (optional extras work for v1)
- Communication/Operations departments (deferred — use adapters for external comms)

### 7.2 Known issues
- Memory panel 404 (no `/api/memory` endpoint — Plan 17 will fix)
- Models panel placeholder (deferred to Plans 16-19 arc)
- Log Drawer may not be rendering events correctly (Plan 16 will fix)
- `trace_emitter.py` needs `subscribe_callback` method (added in Plan 11, verify it works)
- Bandit 2 Medium findings (B615 — HuggingFace downloads, `#nosec` added, acceptable)

### 7.3 Documents in `documents/` folder
- `SovereignAI_Architecture_Decisions.md` — company metaphor, 9 panels, memory architecture, QA strategy
- `SovereignAI_Orchestrator_Spec.md` — CEO's office spec
- `SovereignAI_Coding_Department_Spec.md` — coding department spec
- `SovereignAI_Research_Department_Spec.md` — research department spec
- `SovereignAI_Library_Department_Spec.md` — library/memory department spec
- `SovereignAI_Education_Department_Spec.md` — education/ML department spec
- `models-panel-spec.md` — Models panel catalog implementation spec
- `project-vision-Rev5.md` — canonical vision (locked)

### 7.4 Deliverables in `/home/z/my-project/download/`
- `plan-15-Rev1.md` — Scan 15 (next to execute)
- `close-md-step17-fix-L40.md` — fix for close.md git rm bug (applied by Scan 15)
- `models-panel-design-reference.md` — locked architectural decisions for Models panel
- `department-specs-assessment.md` — Architect's review of the 5 department specs
- `ui-structure-questionnaire.md` — UI decisions questionnaire (answered in this document)
- `plan-11-14-batch-Rev5/6/7/8/9-adjudication.md` — Round Table adjudication logs
- Various other plan files, diagnosis reports, and analysis docs from the session

---

## 8. How to continue in a new chat

1. **Clone the repo** (if not already): `git clone https://github.com/AngusKingCAI/SovereignAI.git` → `/home/z/my-project/sovereignai-review/`
2. **Fetch latest**: `git fetch origin && git reset --hard origin/main`
3. **Read this document** end-to-end
4. **Read in order**: `AI_HANDOFF.md` → `project-vision-Rev5.md` → `PLANS.md` → `AGENTS.md`
5. **Check the queue**: Scan 15 is next, then Plans 16-19 (UI/functional batch)
6. **Note the process change**: Round Table is vetoed for the UI batch. GLM drafts, Devin executes, User reports back.

---

## 9. Revision History

- **2026-06-29**: Created. Captures all decisions from the session: close.md fix, UI questionnaire answers, department spec assessment, process veto for UI batch, numbering policy, plan structure fix.
