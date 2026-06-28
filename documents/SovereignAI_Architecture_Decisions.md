# SovereignAI — Architecture Decisions Document

**Date:** 2026-06-28  
**Status:** Theoretical sketch — ready for GLM prompt creation & Round Table review  
**Scope:** All architectural decisions made during the theoretical design session.

---

## 1. The Company Metaphor

SovereignAI is structured as a company. The user is the Owner. Every entity has a company role.

| Entity | Company Role | Notes |
|--------|-------------|-------|
| **Owner (User)** | Business owner | Has full authority. Can override any decision, replace any entity, or take direct control. |
| **Orchestrator (CEO)** | CEO | Receives vague human input, cleans it into structured measurable prompts, delegates to departments. Never lets workers message the user directly. |
| **Department Managers** | Department heads | Temporary by default, promoted to permanent if useful. Spawned per task or per department. Break objectives into sub-tasks, assign workers, synthesize results. |
| **Workers** | Employees | Execute skills. Memory-agnostic — ask Manager for data, Manager asks Librarian. Circuit breaker: >50 errors in 10 seconds = unloaded. |
| **Librarian** | Chief Information Officer / Records Manager | Lives in Memory panel. Maintains index of what data lives where. Routes plain-English data queries to correct backend. Other managers query the Librarian, not memory directly. |
| **Security Guard** | Internal Audit / Compliance | Cross-cutting. Not a department. Can inspect any worker, adapter, or memory backend. Lives in Options panel. |

**v1 Departments:** Research, Engineering, Communication, Operations.

**Chain of command:** Owner → CEO → Manager → Worker. Owner can bypass in emergencies. Workers never talk to Owner directly.

---

## 2. The 9 Panels

| # | Panel | Company Function | What's Inside |
|---|-------|-----------------|---------------|
| 1 | **Orchestrator** | CEO's Office | Primary chat. CEO translates human input → structured prompts. Multiple windows allowed (hybrid model — shared memory, per-window focus). Real-time conversation. |
| 2 | **Workers** | Org Chart | Departments (Research, Engineering, Communication, Operations), Managers, Workers. Security Guard as cross-cutting audit overlay. Click to inspect workload, errors, assignments. |
| 3 | **Tasks** | Operations & Scheduling | Loop/schedule manager. Recurring, scheduled, permanent, triggered tasks. Status, history, next run. Mini-graph showing involved departments. |
| 4 | **Skills** | Training Catalog & Composer | **Atomic** (single tools), **Composite** (multi-step DAGs), **Templates** (pre-built). Providers: [Local], [GitHub], [MCP Directory], [PulseMCP]. Multi-tab authoring: Canvas, Code, Template, Conversation, Import. |
| 5 | **Memory** | Records Department | **Backends** (list view: Postgres, Qdrank, Obsidian, SQLite, etc.) + **Topology** (interactive neural network graph). Center = Orchestrator. Outer = memory backends. Workers as intermediate nodes. Click/drag to grant/revoke access. Librarian manages the topology. |
| 6 | **Models** | HR / Talent Pool | Provider tabs: [Hugging Face], [Ollama], [OpenAI], [Anthropic], [llama.cpp], [Local Files], [Add Provider...]. Per-model: load/unload, VRAM usage, set as default for department. |
| 7 | **Adapters** | Vendor Relations | MCP servers and native adapters wrapped for SovereignAI. Provider tabs: [MCP Directory], [GitHub], [Local]. Each adapter registers tools in capability graph. |
| 8 | **Hardware** | Facilities / IT | CPU, GPU, RAM, disk, temperature, power. Model loading controls. |
| 9 | **Options** | Policies & Compliance | Auth (login gate, argon2, rate limiting), Security Guard settings, cloud relay config, API keys, user preferences (auto vs ask user), theme, notifications. |

---

## 3. Memory Architecture

**Model: Categorized routing, not universal replication.**

Each data type has a primary backend. The Librarian routes queries. No forced "write to all."

| Data Type | Primary Backend | Secondary/Indexed | Read Path |
|-----------|---------------|-------------------|-----------|
| Chat history | Postgres / SQLite | Vector DB (embedded), Full-Text | Postgres (history), Vector (semantic recall), Full-Text (keyword) |
| User notes / docs | Filesystem (Obsidian) | Vector DB, Full-Text | Filesystem (raw), Vector (semantic), Full-Text (keyword) |
| Task state / DAGs | Postgres | — | Postgres |
| System logs / traces | SQLite FTS / Full-Text | — | Full-Text |
| Embeddings / RAG | Qdrank / Qdrant | — | Vector DB |
| Entity relationships | Lightweight in-memory graph | — | Graph traversal |
| Config / secrets | SQLite key-value | — | Direct read |

**Hybrid search for RAG:** Vector (semantic) + Full-Text (BM25) + RRF re-ranking. Not vector-only.

---

## 4. First-Run Experience

Setup wizard on first launch:
1. Prompt to download an adapter (Ollama, llama.cpp, etc.)
2. Prompt to download a model (or use defaults)
3. Configure login for web/cloud relay access
4. Optional: create first loop or skill

**Ships with:** At least one skill invocable without external dependencies (built-in, no download needed).

---

## 5. Skill Authoring (Multi-Tab)

The Skills panel has a "Compose" sub-view with tabs:

| Tab | Mode | For Whom |
|-----|------|----------|
| **Canvas** | Visual drag-and-drop (N8N-style) | Non-programmers, visual thinkers |
| **Code** | Python skill with manifest | Developers |
| **Template** | Start from pre-built, fill blanks | Quick starts |
| **Conversation** | Describe to CEO, CEO generates | Natural language users |
| **Import** | Pull from GitHub, MCP Directory, local file | Reuse |

All tabs produce the same underlying format (manifest + code + DAG definition).

---

## 6. QA Strategy

Hybrid:
- **User-driven:** User tests features, reports issues, approves/rejects behavior.
- **CEO/Manager-driven:** CEO and Managers run conformance tests, contract tests, property tests as part of task execution. Test results logged to SSD.

No separate "QA Department" worker for v1.

---

## 7. CI/CD

Devin pushes code in the `/close` command. No separate CI/CD pipeline. Devin commits to `AngusKingCAI/SovereignAI`.

---

## 8. Error Handling & Logging

- **Circuit breaker:** Worker >50 errors in 10 seconds = unloaded.
- **Diagnostics:** Logs are the primary diagnostic tool. No special disaster recovery worker.
- **Storage:** All traces logged to SSD. Local only. No external telemetry.
- **Log drawer:** Bottom of every panel, verbosity levels, filterable.

---

## 9. Phone App

Full system control. Not just messaging. Connects via cloud relay (E2EE WebSocket) or local network. User can approve/reject tasks, view all panels, manage loops.

---

## 10. Multi-Window Orchestrator

**Hybrid model:** Shared memory (all windows see the same CEO, same task state, same memory), but each window can have a different "focus" or active task. Like multiple browser tabs on the same session, each on a different page.

---

## 11. Backup

**None for v1.** Backup is the user's problem. Can be revisited in later plans.

---

## 12. MCP Ecosystem Integration

- **MCP servers** expose tools, resources, and prompts. SovereignAI wraps them as **adapters**.
- **Adapters** register tools in the capability graph.
- **Skills** consume tools from adapters (and native tools) to build composite workflows.
- **Skill marketplace** queries MCP registries (MCP Directory, PulseMCP, GitHub) for discoverable tools.
- **Local-first:** All installed MCP servers are copied locally to `adapters/external/` or `skills/external/`.

---

## 13. Open Questions for GLM / Round Table

1. What is the exact manifest format for skills? TOML? JSON? What fields?
2. What is the built-in skill for first-run? Calculator? File reader? "Hello world" chat?
3. What does the Security Guard actually scan? Code signatures? Behavior patterns? Both?
4. How does the CEO's "prompt creation" function work in practice? Is it a system prompt? A separate LLM call? A template?
5. What is the exact loop definition language? Cron syntax? Natural language? Structured JSON?
6. How does the capability graph represent composite skills? As nodes? As edges? As subgraphs?
7. What is the inter-process communication protocol? Local socket? TCP? Named pipes? gRPC?
8. How does the cloud relay authenticate? Username/password only? E2EE key exchange?
9. What is the v1 test suite? pytest? unittest? How does Devin run it?
10. What is the exact file structure on disk? `C:/SovereignAI/` — what subdirectories?

---

*End of document.*
