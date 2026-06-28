# Founding Vision — The Unnamed Project (Rev 4)

> **Status**: Pre-architecture, post-third-round-table. This revision incorporates findings from the third 6-AI round table review (4 substantive responses received) and the user's resolution of all flagged issues.

> **What changed since Rev 3**: P9 reframed — UIs are NOT part of the core. UIs (web/TUI/CLI/phone) are separate processes that consume the core's capability API. Option A from day one (no Option B → A migration). P6 changed — cloud relay uses login gate, not QR pairing. P7 changed — constructor arg cap raised from 7 to 15. P9 worker→user interrupt schema expanded (boolean, text, choice, file, multi_choice). Criterion 27 narrowed — event bus fault isolation excludes the Security Guard (accepted in-process risk). P14 added — provenance enforcement (cryptographic signatures + hash verification). Core Scope (v1) section added — concrete list of what's in/out of core. Criterion for no silent failures added. v1 targets Windows only; cross-platform deferred. Q27 (UI migration trigger) removed — moot under Option A. Q31 (packaging) and Q32 (debt register) added.

> **Reading time**: ~14 minutes.

---

## Preamble

This project has no name yet. That is deliberate — names constrain thinking. "Sovereign AI", "Jarvis", "Assistant", "Agent" all carry baggage. The round table may name it; for now it is **the project**.

This document is not a specification. It is a charter. Every architectural decision the round table debates must be tested against the principles below. If a proposal violates a principle, the principle wins. If a proposal satisfies every principle but the round table still rejects it, the principle is incomplete and must be amended before the next round.

---

## The Premise

Software is being rebuilt around models that did not exist three years ago and will be obsolete in three more. Most teams building these systems pick one provider, one memory store, one orchestration pattern, and ship. When the next model lands — different context window, different modality, different pricing, different protocol — they rewrite.

This project rejects that approach.

The aim is a **solid core that can adapt to all new things that come out**. The core is small, stable, and deliberately ignorant of what attaches to it. Memory, adapters, skills, and models are not part of the core — they are equal citizens plugged into it. A new memory paradigm invented next year means adding a backend, not editing the core. A new model provider launching tomorrow means adding an adapter, not editing the core. A new skill needed means adding a file, not editing the core.

The system must be **fundamentally modular and flexible**. Modularity means parts break rather than the whole thing. Flexibility means new things can be added easily. These two qualities are prioritised over simplicity. The core is small enough to be readable, but readability is a guideline, not a gate.

This is not a framework. Frameworks impose structure on others. This is a personal operating system built for one user (the developer), designed to absorb whatever the next decade throws at it without forcing a rewrite.

---

## Core Scope (v1)

The core is sacred. To prevent scope creep, the core's responsibilities are explicitly listed. Anything not on this list is pluggable. Adding an item to this list requires a core upgrade (round table review).

### In the core (sacred — v1)

1. **Composition root** — the single bootstrap file that wires all core components
2. **Event bus** — typed channels, in-process message routing
3. **Capability manifest parser** — reads TOML/JSON manifests from components
4. **Capability graph** — the in-memory index of what's plugged in
5. **Routing engine** — matches requests to components based on capabilities
6. **Lifecycle manager** — starts, health-checks, stops components
7. **TraceEmitter** — constructor-injected observability substrate
8. **Task state machine** — RECEIVED → QUEUED → EXECUTING → COMPLETE/FAILED
9. **DAG validator** — checks skill DAGs for acyclicity, type-matching
10. **Auth middleware** — login gate, session tokens
11. **Relay server** — E2EE endpoint for remote UIs
12. **Capability API** — the contract UIs consume to query state and submit tasks

### Outside the core (pluggable — v1)

- All adapters (OpenAI, Ollama, llama.cpp, etc.)
- All skills (calculator, websearch, etc.)
- All memory backends (Postgres, Qdrant, etc.)
- All workers (including the Security Guard)
- All UIs (web, TUI, CLI, phone — separate processes)
- All gateways (voice, IM, API)
- Model loading/unloading based on hardware (deferred to later plan)
- Self-correction / learning loops (skills, not core)
- Cross-platform packaging (v1 is Windows-only; other platforms later)

---

## Core Principles

### 1. The core is sacred.

The core grows reluctantly. Every line added must justify itself against the cost of every future adapter, skill, and memory backend having to live with it. If a feature can live outside the core, it must. If it cannot, the burden of proof is on adding it, not on leaving it out. The Core Scope (v1) list above is the canonical reference — anything not on it belongs outside.

### 2. Everything else is pluggable.

Adapters, skills, memory backends, model hosts, gateways, UIs — all are equal. None is more privileged than another. The system runs with any subset. A user with one local adapter and one skill has a working system. A user with twelve adapters, fifty skills, and four memory backends has the same core.

### 3. No provider lock-in.

Swap any component without touching the core or any other component. If removing one piece breaks another, the architecture has failed. The test is mechanical: delete any adapter file, any skill file, any memory backend file. The system must continue to start and serve the remaining capabilities, gracefully degrading any capabilities that depended on the deleted file.

### 4. Local-first by default, cloud by choice. Ship with minimum viable local capability.

The system runs fully offline with zero cloud dependencies and zero network calls. Cloud is an escalation, not a foundation. A user who never wants to touch a cloud API key still gets a working system. A user who wants to escalate a hard task to a frontier model can — but the cloud is a guest, not a host.

**Minimum viable local capability**: the system ships with at least two local model adapters (Ollama, llama.cpp) and at least one skill that can be invoked without external dependencies. The first-run experience must allow the user to issue at least one task and receive a meaningful response, even if degraded, without installing anything beyond the project itself. If the user has either Ollama or llama.cpp already installed, the system is fully functional on first run; if neither is installed, the system starts, surfaces a clear message via the orchestrator telling the user how to enable local inference, and remains usable for non-LLM tasks (file operations, terminal, etc.).

**v1 platform target**: Windows only. Cross-platform packaging (macOS, Linux) is deferred to a later plan. The architecture must not foreclose cross-platform support, but v1 ships Windows-first to reduce complexity.

### 5. Wire as you go — for implementations AND contracts.

No new horizontal capability until the existing stack is reachable and demonstrably improving outputs. A skill that is not wired is a skill that does not exist. An adapter that is not invoked is an adapter that does not exist. The system ships with what it uses, not with what it might someday use.

This principle applies to **contracts as well as implementations**. No contract (abstract interface, protocol definition, schema) is added to the core until at least one implementation of that contract is being wired in the current or immediately-next plan. Speculative contracts for hypothetical future modalities are forbidden — they bloat the sacred core with abstractions for capabilities that may never ship. When a new modality arrives, the contract is designed then, against the concrete needs of the actual implementation.

**Note**: This project has a single developer (the user). The "parallel development" concern that motivated contract sketches does not apply — the user designs contracts as they implement, since they are the only one writing code. No contract sketch mechanism is needed.

### 6. One user, one logical system, accessible from anywhere. All UIs connect to the same core.

Built for a single individual's context — their files, their tools, their domains, their habits. Not multi-tenant. Not enterprise. Not general-purpose. The user is the operator and the only operator.

The core runs on user-owned hardware. UIs (web, TUI, CLI, phone app) are **separate processes** that connect to the core via a local socket (for local UIs) or via a cloud relay (for remote UIs). The relay is **end-to-end encrypted (E2EE)**: the core generates an ephemeral public/private key pair on first install; the relay server is a blind packet forwarder that cannot inspect or alter payloads.

**Login gate**: the user creates a login (username + password) on the core during first-run setup. All UIs (local and remote) authenticate via this login. Session tokens are issued on successful auth and attached to every request. No anonymous connections. The phone app pairs by entering the core's address + user credentials — no physical QR scan required, no manual key exchange. This allows remote setup (user can pair the phone app from anywhere).

**All UIs connect to the same core. The core is the single source of truth.** There is no client-side state that can conflict. Concurrent UI submissions (e.g., user sends a message from the web UI and the phone app at the same instant) are queued by the orchestrator in receive order. A long-running task started on one UI is visible and controllable from any other UI. The user can open multiple Orchestrator windows (like opening multiple chat windows in a browser) — each is a separate view of the same core state.

The architecture must accommodate a future multi-machine core (multiple core instances syncing state) without requiring distributed consensus in v1. The user is the only operator, but may operate from multiple devices.

### 7. Modular and flexible core.

The core prioritises **modularity** (parts break rather than the whole thing) and **flexibility** (new things can be added easily) over simplicity. The core is small enough to be readable, but readability is a guideline, not a gate. The gates are: (a) any single component can crash without taking the system down (with the documented exception of the Security Guard — see P11); (b) any new adapter, skill, or memory backend can be added in one file without touching core code; (c) the dependency graph is acyclic; (d) no class in the core has more than 15 constructor arguments (generous cap to accommodate realistic dependency needs; the real protection against god-objects is the "no context bags" rule in P12).

### 8. UIs are NOT part of the core. UIs are separate processes consuming the core's capability API.

The UI is structured as a fixed 9-section sidebar mapping to the framework's own architecture:

- **Orchestrator** — the chat surface and the live view of routing decisions
- **Workers** — registered workers, status, recent activity
- **Tasks** — task queue, history, state per task, scheduled loops
- **Skills** — N8N-style canvas for composing atomic skills into composite skills
- **Memory** — backends plugged in, recent reads/writes, query interface
- **Models** — local and cloud models configured, VRAM usage, tier assignments
- **Adapters** — all adapters, status, cost, latency
- **Hardware** — CPU/GPU/RAM/VRAM, sandbox status, download queue
- **Options** — user settings, approval thresholds, sandbox policy, UI preferences

A bottom button opens a **Log drawer** with verbosity levels (ERROR/WARN/INFO/DEBUG/TRACE), filterable by level and component via checkboxes, searchable. This is the observability surface.

The 9 sidebar sections are fixed for v1 but may grow via core upgrade (round table review required to add a 10th). The sidebar is a controlled vocabulary — not fixed forever, but not auto-extended.

The UI is capability-driven at the panel level: each panel shows whatever is plugged into its capability class. The Skills panel shows whatever skills are registered. The Adapters panel shows whatever adapters are registered. Adding a new skill causes it to appear in the Skills panel on next render. Removing an adapter causes it to disappear. UIs may hard-code **capability class names** (the 9 sidebar sections) but must never hard-code **individual component names** (calculator_skill, openai_adapter).

**UIs are separate processes.** The web UI, TUI, CLI, and phone app each run as independent processes that connect to the core via a local socket (or cloud relay for remote). They consume the core's capability API — a stable contract that exposes: (1) a list of capabilities with their input/output schemas, (2) a task submission endpoint, (3) an event subscription mechanism for traces and state changes. UIs never import core types directly; they communicate via the API. A UI presentation change (new CSS theme, new TUI color scheme, new CLI help text, new phone app layout) requires zero edits to the core — the core doesn't even know about it.

**The user only ever talks to the orchestrator.** Workers never surface messages, explanations, or results directly to the user. Everything flows through the orchestrator: the orchestrator routes a task to a worker, the worker does the work and returns the result, the orchestrator synthesises and informs the user. The chat surface is uniquely in the Orchestrator panel. Other panels show *data* (worker status, task state, skill list) but not conversation. The Log drawer shows raw traces from all components but is observability, not conversation.

**Multiple Orchestrator windows are allowed.** The user can open multiple chat windows (like opening multiple tabs in a browser) — each is a separate view of the same core state, submitting tasks to the same orchestrator.

**Workers can request user input via structured events.** A worker that needs user confirmation (e.g., "Install pip package requests? [Y/n]") emits a `user_input_request` event with a structured schema. The schema supports multiple input types:
- `boolean` — Y/N confirmation
- `text` — free-text input
- `choice` — select one from a list of options
- `multi_choice` — select multiple from a list of options
- `file` — file picker (returns a path)

The orchestrator surfaces these in the chat, rendering them generically — the orchestrator doesn't need to understand "pip install," it just shows "Worker X requests Y/N confirmation: Install pip package requests?" or "Worker X requests file selection: Choose a file to upload." The user's response goes back through the orchestrator to the worker. This preserves "user only talks to orchestrator" while allowing structured worker→user interrupts without polluting the orchestrator with worker-specific logic.

**UI rendering approach**: Option A (UIs as separate processes consuming a capability API) from day one. No Option B → A migration needed. The web GUI is built first; CLI second; TUI third; phone app after that. Each is a separate process connecting to the same core.

### 9. Observability by default. No silent failures.

The core exposes traces, errors, and state introspection through a uniform contract. Components do not implement their own logging — they emit structured events via a TraceEmitter (constructor-injected, never global). The Log drawer renders these events with level filtering (ERROR/WARN/INFO/DEBUG/TRACE), component filtering (checkboxes per component), and search. Persistence to trace memory is automatic. The Orchestrator panel surfaces system state to the user without requiring them to read logs.

**Trace rate limiting**: high-frequency events (e.g., per-token traces from streaming adapters) are sampled or batched to prevent the Log drawer from flooding. The default sample rate is configurable in Options.

**No silent failures.** When the event bus isolates a fault (a component crashes, the bus keeps running), the failure is logged at ERROR level with full context — never silently swallowed. The orchestrator surfaces persistent failures to the user. The user can always see what's failing in the Log drawer; nothing is hidden to keep the system "running."

### 10. Security via reasoning, not just permissions. User chooses whether to scan. Security Guard is in-process (accepted risk).

The system has a default-deny stance for components not authored by the user or the orchestrator. A **Security Guard** worker — a lightweight expert model trained for safety assessment — reviews externally-sourced components when the user requests a scan. Components authored by the user or orchestrator are trusted by default. The Security Guard can approve, warn, or reject; warnings must be explicitly dismissed by the user (via the orchestrator) before the component runs. The Security Guard's verdict goes to the orchestrator, which informs the user. The user never sees the Security Guard's raw output; they see the orchestrator's synthesis.

**The user chooses whether to scan.** Scanning is not mandatory — it's a user-initiated action ("Scan this skill before running"). The system does not babysit the user. If the user trusts a skill, they can run it without scanning. If they're unsure, they can request a scan. The Security Guard is a tool the user can invoke, not a gate that blocks every install. Sandbox isolation is available as an additional layer for high-risk components, on top of the Security Guard's verdict.

**The Security Guard runs in-process as a regular worker** (no special process isolation). This is an accepted risk with user sign-off: the user understands that a malicious in-process peer could theoretically bypass the Security Guard, and accepts this trade-off in exchange for simplicity. The user is responsible for not installing obviously malicious code — the Security Guard is a reasoning aid, not a perimeter.

**Documented exception to event bus fault isolation (criterion 27)**: Because the Security Guard is in-process, a crash of the Security Guard can take down the event bus and the entire core process. This is the one accepted exception to the fault isolation guarantee. All other workers, skills, and adapters are expected to crash without taking down the bus. If the Security Guard crashes, the core restarts on next launch; in-flight task state is recovered from trace memory.

### 11. Dependency injection, no globals, no context bags.

All components receive their dependencies (adapters, memory router, trace emitter, etc.) via constructor arguments. Components never instantiate their own dependencies, never use `import` to reach across module boundaries for runtime state, never use module-level singletons. No `global` keyword in any production file. No "deferred violation" category — if a global seems unavoidable, STOP and redesign. One file (the composition root) is the only place that instantiates core components; every other file receives dependencies via constructor. This makes the full dependency graph auditable in one place.

**No context/bag objects that aggregate unrelated dependencies.** Each constructor argument must be a single, typed dependency (an adapter, a memory router, a trace emitter — not a `SystemContext` or `DependencyBag` containing many). Wrapping multiple dependencies into one fat parameter to bypass the constructor cap is forbidden — it recreates a global service locator while technically passing one argument. Static analysis test checks for context-object anti-pattern (a class with multiple untyped or loosely-typed fields passed as a single constructor arg).

### 12. Plain-English docstrings on every function.

Every `def` and `async def` (including methods) must have a docstring. The docstring's first line must be a complete sentence in plain English, comprehensible to someone with no programming knowledge, describing what the function does (not how). The first line must start with a verb (enforces "does what" framing) and be at least 10 words long (enforces substance). Multi-line docstrings should explain inputs, outputs, and errors in plain language. Jargon ("async", "await", "coroutine", "dispatch", "yield", "instantiate") must be replaced with plain equivalents ("send", "wait for", "running task", "send to", "produce", "create"). Ruff rule `D103` (missing docstring) plus a custom check (verb-first, ≥10 words on first line) enforced in CI; docstring quality beyond this is enforced by code review. This applies to AI-generated code (Devin) and human-contributed code equally.

### 13. Strong, robust.

The core does what it claims, without caveat. It fails gracefully, isolates faults, and recovers without manual intervention. When a component crashes (except the Security Guard — see P10), the system stays up, the error is reported via trace, and other components keep working. The orchestrator tells the user what happened (in plain language); it does not expose stack traces unless the user opens the Log drawer.

### 14. Provenance enforcement for external components.

Every external component (skill, adapter, memory backend) must carry a **provenance manifest** signed by the author or distributor. The manifest contains: component name, version, author identity (cryptographic public key), content hash of the component bundle, a list of dependencies (with their hashes and authors), and an optional "audited_by" field pointing to a third-party audit report. The core verifies the signature chain on installation and on every update. Unsigned components are rejected by default; the user can override this for local development, but the override is explicit and logged. Components authored by the user or orchestrator are exempt (trusted by default). This principle works alongside P10 (Security Guard) — provenance verifies *who* made the component, the Security Guard reasons about *what* it does.

---

## The Capability Surface

The core must **support** the following capability classes without prescribing their implementation. v1 may ship with one example of each class; the architecture must allow dozens more to be added later without friction.

### Memory — all types, treated as interchangeable backends

- **Vector memory** — semantic similarity search (Qdrant, pgvector, Chroma, FAISS, future).
- **Graph memory** — relationship and entity traversal (Neo4j, Memgraph, DuckDB graphs, future).
- **Relational memory** — structured records (Postgres, SQLite, DuckDB, future).
- **Document memory** — long-form notes and knowledge (Obsidian, Notion, markdown vaults, future).
- **Episodic memory** — conversation and event history, time-ordered.
- **Semantic memory** — facts and concepts distilled from episodes.
- **Procedural memory** — learned workflows, skill chains, automation patterns.
- **Working memory** — short-lived scratchpad for the current task, volatile.
- **Trace memory** — execution logs for retrospective improvement and debugging.

The contract must allow any of these to be added without the core knowing they exist. The core routes memory operations; backends fulfil them. A backend declares its capabilities (vector, graph, relational, document, etc.) in its manifest; the core routes queries to backends that declare the relevant capability. Cross-backend queries (vector + graph) are handled by the core as a scatter-gather pattern.

### Adapters — all model hosts, treated as interchangeable sources of intelligence

- **Cloud providers**: OpenAI, Anthropic, Google Gemini, Mistral, Cohere, Together, Groq, DeepSeek, HuggingFace Inference, xAI, future.
- **Local runtimes**: Ollama, LM Studio, llama.cpp, vLLM, MLX, future.
- **Protocols**: Model Context Protocol (MCP), Agent-to-Agent (A2A), OpenAI-compatible endpoints, Anthropic-compatible endpoints, future protocols not yet invented.
- **Custom**: user-defined adapters for private, fine-tuned, or in-house models.

A new adapter must be addable in a single file. The core must never import an adapter by name. The core must never assume a specific adapter is present. The system must function with zero adapters (degraded but running) and with twelve adapters (full capability). **v1 ships with at least Ollama and llama.cpp adapters** to satisfy the minimum viable local capability (P4).

### Skills — all capability classes, treated as interchangeable tools

- **File skills**: read, write, search, transform, watch.
- **Code skills**: execute, test, debug, refactor, review.
- **Web skills**: search, scrape, fetch, summarise, monitor.
- **Terminal skills**: shell, git, docker, system commands.
- **Communication skills**: email, calendar, messaging, voice, notifications.
- **Domain skills**: marine, finance, research, manufacturing, media production — whatever the user's domains are.
- **Meta skills**: planning, evaluation, self-correction, improvement loops, debate, retrospection.
- **Sensory skills**: audio capture, screenshot, clipboard, system profiling.

Skills have two natures: **atomic** (websearch, open-browser, register-email — single-step tools) and **composite** (create-email = open-browser → go-to-protonmail → register-email-account — a DAG of atomic skills). Composite skills are first-class citizens (saved, versioned, shareable) and ephemeral (build-run-discard); a "Save as Skill" action promotes ephemeral to first-class.

The Skills panel uses an N8N-style canvas for composing atomic skills into composite skills. Workers (not the orchestrator) decide which skills to invoke and execute them as DAGs. A composite skill is itself a skill — it can be nested, shared, versioned.

A new skill must be addable in a single file. The core must never hard-code a skill's name. Skills must be discoverable, invocable, and replaceable without touching the core.

### Models — all deployment modes, treated as interchangeable

- **Local models** — running on user hardware, fully offline.
- **Cloud models** — running on provider infrastructure, on-demand.
- **Hybrid models** — local for routing/triage, cloud for heavy lifting.
- **Federated models** — composed across multiple providers in a single request.
- **Trained expert models** — lightweight models specifically fine-tuned for narrow tasks (one expert per worker domain). The framework explicitly supports fine-tuning, training, and inference of task-specific experts.

The core must not assume any specific model is present. It must tolerate a world where the only model available is a 7B local, and a world where every frontier model is one call away.

**Model loading/unloading** based on system hardware (RAM %, VRAM %, user-configurable thresholds) is a planned feature for a **later plan**, not Plan 1. Plan 1 establishes the core architecture; the resource-aware model loader is built on top of that architecture in a follow-on plan.

### Workers — domain experts

Each worker is a domain expert. A worker has: a profile (worker_id, expertise, capabilities), an LLM adapter (the brain it runs on), and a set of skills it can invoke. Workers may use lightweight models specifically trained for their domain.

Workers receive tasks from the orchestrator. They decide which skills to invoke (sequentially or as a DAG), execute the work, and return the result. Workers never talk directly to the user. The orchestrator is the system's single voice.

One worker is the **Security Guard** — a lightweight expert model trained for safety assessment. It reviews externally-sourced components when the user requests a scan, returns a verdict (APPROVE/WARN/REJECT) to the orchestrator, and performs ongoing behavioural auditing on running components when invoked. The user chooses whether to scan — the Security Guard is a tool, not a mandatory gate.

### Gateways — interface surfaces

**Core UIs** (separate processes consuming the core's capability API per P8):
- **Web** — browser-based UI, served as a separate process. 9-section sidebar + Log drawer. Built first.
- **CLI** — terminal interface for scripting. Subcommands mirror the 9 sections. Built second.
- **TUI** — full-screen terminal interface. Same 9-section structure. Built third.
- **Phone app** — connects via cloud relay to the core. Same 9-section structure. Built after web/CLI/TUI.

**Pluggable gateways** (external, optional, route messages into the core):
- **Voice** — speech in, speech out, hands-free operation.
- **IM** — chat-based access (Telegram, Signal, future).
- **API** — programmatic access for other agents and external systems.
- **Future gateways** — added without touching the core.

---

## Non-Goals

This project is explicitly **NOT**:

- **A SaaS.** No hosting, no multi-tenant, no subscription tier, no usage metering.
- **A chatbot.** Conversation is one gateway among many, not the product.
- **Cloud-locked.** Any architecture that requires a specific cloud service to function is rejected.
- **Enterprise software.** No RBAC, no org charts, no compliance certifications.
- **A framework for others.** Built for one user (the developer).
- **Feature-complete at v1.** Capabilities are wired as the user needs them.
- **Opinionated about which adapter, skill, or memory backend is "best."** All are welcome.
- **A single-LLM wrapper.** A system that only works with one provider has failed its premise.
- **A rewrite of any existing project.** Patterns may be borrowed; code will not be.
- **A research project.** Must be usable daily.
- **Built for scale.** One user, one machine (or a small personal cluster eventually).
- **Multi-tenant.** One operator only. The user is the operator.
- **Distributed in v1.** Multi-machine core is designed-for-future, not built-now. Distributed consensus is explicitly out of scope.
- **Optimised for performance over modularity.** If a perf optimisation hurts modularity, modularity wins.
- **Babysitting the user.** The system does not force security scans, mandatory sandboxing, or permission prompts on every action. The user is responsible for their own choices; the Security Guard is a tool they can invoke, not a parent.
- **Speculative.** No contracts, interfaces, or abstractions are added for hypothetical future capabilities. Wire as you go applies to everything.
- **Cross-platform in v1.** v1 targets Windows only. macOS and Linux support deferred to a later plan.
- **Multi-developer.** v1 has a single developer (the user). Process rules assume solo development.

---

## Success Criteria

The core is solid if and only if all of the following are true.

### Modularity criteria (highest priority)

1. **Fault isolation test**: kill any skill mid-execution → system stays up, error is reported via trace, other skills keep working.
2. **Independence test**: stop any adapter → other adapters and all skills keep working.
3. **Delete any single non-core file** — the system starts without crashing, gracefully degrades capabilities that depended on it, and surfaces what's missing to the user.
4. **Acyclic dependency test**: CI checks the import graph; cycles fail the build.
5. **No globals**: `grep -rn "^global\|global _" core/` returns zero matches in production files. Static analysis test enforces this; CI fails on any violation.
6. **Constructor arg cap**: no class in the core has more than 15 constructor arguments. Static analysis test enforces this.
7. **No context bags**: no class has a constructor parameter that is a container object holding multiple unrelated dependencies. Static analysis test enforces this.
8. **Event bus fault isolation**: if the event bus crashes or deadlocks (excluding the Security Guard exception), the core restarts it automatically without losing in-flight task state. The Security Guard is the documented exception — if it crashes, the core process may crash, and recovery happens on next launch.

### Flexibility criteria (highest priority)

9. **Add a new adapter** in a single file, under 100 lines of code, without touching the core.
10. **Add a new skill** in a single file, under 100 lines of code, without touching the core.
11. **Add a new memory backend** in a single file, without touching the core.
12. **Swap any adapter, skill, or memory backend** without modifying any other component.
13. **A new model released tomorrow** — adapter added same day, no core changes.
14. **A new memory paradigm invented** — backend added without core changes.
15. **A new protocol (MCP successor, A2A variant) published** — adapter added without core changes.
16. **A new user domain** — skill added in one file, no core changes.
17. **Time-to-add**: from "I have a new adapter idea" to "it's plugged in and working" should be < 30 minutes for someone who's done it before.

### UI criteria

18. **Add a new skill** — it appears in the web UI, CLI, TUI, and phone app on next render, with zero edits to any UI file.
19. **Remove an adapter** — it disappears from the web UI, CLI, TUI, and phone app on next render, with zero edits to any UI file.
20. **No hard-coded individual component names in UI control flow**: `grep -rE '"(calculator|websearch|openai|ollama|postgres|qdrant)' web/ cli/ tui/ phone/` returns zero matches. Capability class names (the 9 sidebar sections) are permitted.
21. **UI presentation changes require zero core edits**: changes to `web/`, `cli/`, `tui/`, `phone/` must not touch `core/`. Enforced via CI: a PR that edits both `core/` and any UI presentation directory is rejected unless the core edit is independently justified (e.g., a capability API change, which is a core upgrade).

### Local-first criteria

22. **Run fully local** with zero cloud dependencies and zero network calls.
23. **Survive any single adapter disappearing** (provider bankruptcy, model deprecation, API change) without touching the core.
24. **Minimum viable local capability**: the system ships with at least two local model adapters (Ollama, llama.cpp) and at least one skill invocable without external dependencies. First-run allows the user to issue at least one task and receive a meaningful response without installing anything beyond the project (assuming Ollama or llama.cpp is present).

### Observability criteria

25. **Every component emits traces** via the constructor-injected TraceEmitter.
26. **Log drawer renders** all traces with level filtering, component filtering (checkboxes), and search.
27. **The orchestrator surfaces system state** to the user in plain language without requiring them to open the Log drawer.
28. **No silent failures**: every error is logged at ERROR level with full context. The event bus may isolate faults, but never silently swallows them. The user can always see what's failing.

### Security criteria

29. **External component review available**: every externally-sourced component (not authored by user or orchestrator) can be reviewed by the Security Guard worker when the user requests a scan.
30. **User chooses whether to scan**: scanning is not mandatory; the user can run any component without scanning if they choose. The system does not babysit.
31. **Ongoing behavioural audit available**: running components can be audited by the Security Guard when invoked, for suspicious patterns.
32. **Provenance enforcement**: every external component must carry a signed provenance manifest (author identity, content hash, dependency list). The core verifies signatures on install and update. Unsigned components are rejected by default; user can override for local development (override is explicit and logged).

### Code quality criteria

33. **Plain-English docstrings**: every `def` and `async def` has a docstring whose first line starts with a verb and is ≥10 words, comprehensible to a non-programmer. Ruff D103 + custom check enforced in CI.
34. **Composition root**: one file is the only place that instantiates core components. Every other file receives dependencies via constructor.
35. **Dependency injection only**: no module-level singletons, no `global` keyword, no deferred violations, no context bags.

### Longevity criteria

36. **The core, after one year of development**, is still readable in a single sitting by a competent reader. (Guideline, not a gate.)
37. **Rust-migratable**: contracts are language-agnostic (manifests, schemas, not Python-specific constructs). A future Rust core could satisfy the same contracts without breaking pluggables.

Criterion 3 (delete any file, system starts) is the most important test of modularity. Criterion 20 (no hard-coded individual component names) is the most important test of capability-driven UI. Criterion 21 (UI presentation changes require zero core edits) is the most important test of the UI/core separation. Criterion 28 (no silent failures) is the most important test of observability.

---

## Resolved Open Questions

The following open questions from Rev 1, Rev 2, and Rev 3 have been resolved. They are recorded here for the historical record; future revisions should not re-litigate them.

| Q | Question | Resolution | Source |
|---|---|---|---|
| Q5 | What is the boundary between skill and adapter? | **Adapter** = model-host connector. **Skill** = domain-specific capability. An MCP server is an adapter if it hosts model calls, a skill if it exposes tools; hybrids must declare both facets. A code-execution runtime is a skill. | Round table + user |
| Q6 | Central event bus vs direct calls? | **Event bus with typed channels.** In-process message bus. Direct calls forbidden. Bus is NOT an orchestrator; it is transparent infrastructure. Bus itself is fault-isolated (restarts on crash), with the documented exception of the Security Guard. | Round table + user |
| Q7 | Process isolation between skills? | **Same-process by default, opt-in sandbox per skill.** User decides trust level. Default for external components is "low" until user explicitly trusts. Security Guard scan is user-initiated, not mandatory. | Round table + user |
| Q10 | What language and runtime? | **Python for v1, Rust-migratable later.** Contracts are language-agnostic. | User |
| Q11 | What is the smallest possible core? | **LOC budget is a guideline, not a gate.** Hard gates: fault isolation, independence, acyclic deps, constructor arg cap of 15, no context bags. | Round table + user |
| Q12 | What does "decentralised" mean in practice? | **Question dropped — P8 was redundant.** | User |
| Q15 | What is the security model? | **Security Guard worker + user-initiated scan + provenance enforcement.** User/orchestrator-authored trusted by default. External components can be scanned if user requests. Security Guard runs in-process (accepted risk with user sign-off). External components must carry signed provenance manifests. | Round table + user |
| Q16 | How do UIs auto-populate without hard-coding component names? | **Capability-class-driven panels.** 9 sidebar sections are fixed capability class names. Panel contents populated dynamically from registry. | User |
| Q17 | Are UIs truly core, or are they core-hosted? | **UIs are NOT part of the core.** UIs are separate processes consuming the core's capability API. The capability API contract is sacred-core; UI presentation is entirely outside the core process. | Round table (unanimous Rev 3) + user (Rev 4 acceptance) |
| Q18 | What does a capability look like to a UI? | **Declared by the capability itself in its manifest.** Name, description, icon, input/output schemas. Core strips rendering-specific attributes before routing; UI receives them for rendering. | Round table |
| Q19 | Trained expert model lifecycle? | **Replaceable, versioned resources with explicit provenance, expiry, and fallback behavior.** Resource-aware loading/unloading deferred to later plan. | Round table + user |
| Q20 | Skill DAG execution model? | **DAG-based, not pipeline-based.** Each skill declares inputs (which can be outputs of other skills). Core builds a DAG from manifests on startup. Execution is topological. DAG validator is in the core; visual layout is in the UI. | Round table |
| Q21 | Cloud relay protocol? | **WebSocket-based, E2EE.** Core generates ephemeral key pair on first install. Login gate (username + password) for user auth. Relay server is blind packet forwarder — cannot inspect or alter payloads. | Round table + user |
| Q22 | Phone app scope? | **Thin remote, not thick client.** Connects via cloud relay, renders the web UI (responsive layout), with push notifications. No local inference, no local memory. Offline mode: caches last rendered UI state, shows "connection lost" overlay. | Round table |
| Q23 | Loop task persistence? | **Loop tasks stored in episodic memory as special records with cron expression and task definition.** Core's lifecycle manager reads them on startup, registers with in-process scheduler. | Round table |
| Q24 | Multi-machine core accommodation? | **State is local to one machine in v1.** Cloud relay is only cross-machine channel. Future multi-machine core (state sync) would require consensus layer — explicitly out of scope for v1. | Round table + user |
| Q25 | Worker-to-worker communication? | **Workers communicate through the event bus, never directly.** Worker A publishes event; Worker B subscribes and runs. Bus enforces acyclic routing. Private collaboration via ephemeral dynamic topics, still monitored by TraceEmitter. | Round table |
| Q26 | Composition root bootstrap? | **Single file (`main.py`) instantiates all core components explicitly.** No runtime magic, no auto-discovery, no implicit dependency resolution. All services instantiated and injected in topological order. | Round table |
| Q27 | UI rendering migration trigger (Option B → Option A)? | **Moot.** v1 starts with Option A (UIs as separate processes). No migration needed. | User (Rev 4) |
| Q28 | Skills canvas data model? | **Composite skill is a JSON document with nodes (atomic skill references with UUIDs) and edges (directed, with optional condition expressions in a simple DSL).** DAG validation (acyclicity, type-matching) is in the core; visual layout is in the UI. | Round table |
| Q29 | Worker expertise declaration? | **Structured taxonomy with a fixed set of top-level domains (coding, research, communication, system, security, domain-specific) and free-text sub-fields for specialization.** Orchestrator matches tasks to workers using a scoring algorithm that compares task tags to worker expertise tags. | Round table |
| Q30 | External component provenance? | **Directory-based (`skills/user/` vs `skills/external/`) plus cryptographic signature for external components.** User-authored components in `skills/user/` are trusted by default. External components in `skills/external/` must carry signed provenance manifests (P14). | Round table + user |

---

## Open Questions for the Round Table (Remaining)

The following remain open. The round table's job in the next review pass is to resolve or refine these.

**Q1 — What is the adapter contract?**
Proposed: capability-based discovery via static manifest (TOML or YAML) declaring capability categories plus a protocol/interface the core routes to. Not duck-typed, not a shared base class. Manifest is fixed-format declaration; interface is function signature contract enforced by runtime type checking.
**Trade-off**: manifests and runtime contract checks add ceremony.
**Status**: proposed, awaiting round table confirmation.

**Q2 — How are skills discovered and registered?**
Proposed: hybrid — directory scan on startup discovers skill directories, each containing a manifest (same format as Q1). Unit of skill is a directory. Decorator-based API offered as syntactic sugar that writes manifest automatically at build time.
**Trade-off**: directory scan means skill must be "installed" into known location.
**Status**: proposed, awaiting round table confirmation.

**Q3 — What is the memory abstraction?**
Proposed: capability-based, not universal interface. Backend declares capabilities in manifest. Core routes queries to backends that declare relevant capability. Cross-backend queries handled as scatter-gather.
**Trade-off**: scatter-gather introduces latency and potential inconsistency.
**Status**: proposed, awaiting round table confirmation.

**Q4 — How does the core route between adapters without knowing them?**
Proposed: capability advertisement via manifests. Each adapter advertises capabilities and priority/weight. Core inspects request requirements, routes to highest-priority adapter satisfying all. User can override priority per-request.
**Trade-off**: multi-capability requests require single adapter or composition.
**Status**: proposed, awaiting round table confirmation. **Note**: under this project's architecture, the orchestrator (not the core) routes; the orchestrator picks a worker, the worker picks an adapter. Q4 may need reframing.

**Q8 — How to handle adapter, skill, and memory versioning?**
Proposed: semantic versioning with capability negotiation. Each component declares version and capability set. On startup, core builds dependency graph, rejects system if two components declare incompatible versions. "Latest wins" only for cosmetic attributes, never for contracts.
**Trade-off**: strict version checking means single incompatible component prevents startup.
**Status**: proposed, awaiting round table confirmation.

**Q9 — How to test a system designed to support "everything"?**
Proposed: all three — conformance suites per capability class, contract tests against core's public contracts, property-based tests for invariants. CI gate requires conformance + contract tests to pass; property-based tests run on schedule.
**Trade-off**: conformance suites expensive to maintain as capability classes grow.
**Status**: proposed, awaiting round table confirmation.

**Q13 — How does the system learn and improve?**
Proposed: retrospective traces stored as ordered events in episodic and trace memory. System does not learn autonomously — learning loop is a skill, not a core capability. A "self-correction" skill reads traces, evaluates outcomes, produces procedural memory updates.
**Trade-off**: if user never installs self-correction skill, system never learns.
**Status**: proposed, awaiting round table confirmation.

**Q14 — What is the persistence story?**
Proposed: many stores, each owned by a memory backend. No single canonical store. Working memory (volatile, in-process) owned by core for duration of task. Episodic and trace memory written by core but stored in backends. Crash recovery: on restart, core replays last incomplete trace from trace memory, prompts user to resume or discard.
**Trade-off**: distributed state across backends makes atomic transactions across backends impossible.
**Status**: proposed, awaiting round table confirmation.

**Q31 — Packaging and distribution story.**
v1 targets Windows only. What is the packaging format? PyInstaller? Native binaries? Docker? How are native dependencies (Ollama, llama.cpp, Python runtime itself) handled? How does the user install the system on a fresh Windows machine? This affects first-run experience and is a Plan 1 consideration.

**Q32 — Debt register format and maintenance.**
The vision defers several items to later plans (model loading/unloading, cross-platform support, backup/recovery). A debt register tracks these deferrals. What format? Where does it live (a markdown file in the repo? a section in PLANS.md?)? Who maintains it (Devin at closing? the Prompt Creator at plan drafting?)? When must a deferred item be addressed (trigger conditions)?

---

## Closing

This project is a bet that the next decade of AI tooling will not be won by the team that picks the right model, but by the team that builds a core capable of absorbing whatever model comes next. The core must be modular enough to outlive its first generation of adapters, robust enough to run without any of them, and flexible enough that the user never has to ask permission to add a new one.

The round table's job is to find the architecture that makes this real. The job of this document is to make sure every member of the round table argues against the same target.

If the round table returns an architecture that satisfies every principle, passes every success criterion, and answers every open question — build it. If it returns an architecture that satisfies most but not all, name what is missing and send it back. Do not compromise on the principles to ship sooner. The whole point of the project is that the core outlives the rush.

---

## Revision history

- **Rev 1** (2026-06-27): Original vision document. 9 principles, 15 success criteria, 18 open questions. Sent to 6-AI round table.
- **Rev 2** (2026-06-27): Post-round-table revision. 4 panel responses + 13 user decisions. P8 dropped. P7 reframed. P9 reframed (OS shell). P6 clarified. P10/P11/P12/P13 added. 31 success criteria. 10 of 18 questions resolved; 8 carried forward; 8 new (Q19–Q26). Sent to round table for clean-pass check.
- **Rev 3** (2026-06-27): Post-second-round-table revision. 4 substantive panel responses + user resolution. P5 tightened. P4 clarified. P6 clarified (E2EE). P9 split into P9a + P9b. P10 clarified. P11 kept as in-process (accepted risk). P12 tightened. P13 tightened. 35 success criteria. All Q19–Q26 resolved. 4 new questions (Q27–Q30). Sent to round table for clean-pass check #2.
- **Rev 4** (2026-06-27): Post-third-round-table revision. 4 substantive panel responses + user resolution. P9 reframed again — UIs are NOT part of the core; UIs are separate processes consuming the core's capability API (Option A from day one, no migration). P6 changed — login gate replaces QR pairing. P7 changed — constructor arg cap raised from 7 to 15. P9 worker→user interrupt schema expanded (boolean, text, choice, file, multi_choice). Criterion 27 narrowed — event bus fault isolation excludes Security Guard. P14 added — provenance enforcement. Core Scope (v1) section added — concrete list of what's in/out of core. Criterion 28 added — no silent failures. v1 targets Windows only. Q27 removed (moot). Q31 (packaging) and Q32 (debt register) added. Sent to round table for clean-pass check #3.
