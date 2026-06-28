# Founding Vision — The Unnamed Project (Rev 2)

> **Status**: Pre-architecture, post-round-table. This revision incorporates findings from the first 6-AI round table review (4 responses received) and the user's architecture clarifications (13 decisions captured). It is the second revision; Rev 1 was the original vision document the round table argued against.

> **What changed since Rev 1**: P8 (Decentralised) dropped as redundant. P7 reframed (modularity + flexibility over simplicity). P9 reframed (OS shell with 9 sections, not chat interface). P6 clarified (cloud-relayed multi-device). P10 (Observability) added. P11 (Security via Security Guard worker) added. Success criteria 12 and 15 refined. New criteria added for fault isolation, independence, acyclic deps, Security Guard review, docstrings. 10 of 18 open questions resolved; 8 carried forward; 4 new questions added.

> **Reading time**: ~10 minutes.

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

This is not a framework. Frameworks impose structure on others. This is a personal operating system built for one user, designed to absorb whatever the next decade throws at it without forcing a rewrite.

---

## Core Principles

### 1. The core is sacred.

The core grows reluctantly. Every line added must justify itself against the cost of every future adapter, skill, and memory backend having to live with it. If a feature can live outside the core, it must. If it cannot, the burden of proof is on adding it, not on leaving it out.

### 2. Everything else is pluggable.

Adapters, skills, memory backends, model hosts, gateways — all are equal. None is more privileged than another. The system runs with any subset. A user with one local adapter and one skill has a working system. A user with twelve adapters, fifty skills, and four memory backends has the same core.

### 3. No provider lock-in.

Swap any component without touching the core or any other component. If removing one piece breaks another, the architecture has failed. The test is mechanical: delete any adapter file, any skill file, any memory backend file. The system must continue to start and serve the remaining capabilities, gracefully degrading any capabilities that depended on the deleted file.

### 4. Local-first by default, cloud by choice.

The system runs fully offline with zero cloud dependencies and zero network calls. Cloud is an escalation, not a foundation. A user who never wants to touch a cloud API key still gets a working system. A user who wants to escalate a hard task to a frontier model can — but the cloud is a guest, not a host.

### 5. Wire as you go.

No new horizontal capability until the existing stack is reachable and demonstrably improving outputs. A skill that is not wired is a skill that does not exist. An adapter that is not invoked is an adapter that does not exist. The system ships with what it uses, not with what it might someday use. This principle applies to *implementations*, not *contracts* — contracts may be designed ahead to anticipate future modalities; implementations are wired only when used.

### 6. One user, one logical system, accessible from anywhere.

Built for a single individual's context — their files, their tools, their domains, their habits. Not multi-tenant. Not enterprise. Not general-purpose. The user is the operator and the only operator. The core runs on user-owned hardware. UIs connect locally or via a dumb cloud relay (data stays on the core machine; the relay only routes packets). The architecture must accommodate a future multi-machine core (multiple core instances syncing state) without requiring distributed consensus in v1. The user is the only operator, but may operate from multiple devices.

### 7. Modular and flexible core.

The core prioritises **modularity** (parts break rather than the whole thing) and **flexibility** (new things can be added easily) over simplicity. The core is small enough to be readable, but readability is a guideline, not a gate. The gates are: (a) any single component can crash without taking the system down; (b) any new adapter, skill, or memory backend can be added in one file without touching core code; (c) the dependency graph is acyclic; (d) no class in the core has more than 7 constructor arguments.

### 8. UIs are core. The UI is an operating system shell.

The web UI, TUI, CLI, and a phone app are **part of the core**, not pluggable components. They are the lens through which the user sees the system. The UI is structured as a fixed 9-section sidebar mapping to the framework's own architecture:

- **Orchestrator** — the chat surface and the live view of routing decisions
- **Workers** — registered workers, status, recent activity
- **Tasks** — task queue, history, state per task, scheduled loops
- **Skills** — N8N-style canvas for composing atomic skills into composite skills
- **Memory** — backends plugged in, recent reads/writes, query interface
- **Models** — local and cloud models configured, VRAM usage, tier assignments
- **Adapters** — all adapters, status, cost, latency
- **Hardware** — CPU/GPU/RAM/VRAM, sandbox status, download queue
- **Options** — user settings, approval thresholds, sandbox policy, UI preferences

A bottom button opens a **Log drawer** with verbosity levels (ERROR/WARN/INFO/DEBUG/TRACE), filterable by level and component, searchable. This is the observability surface.

The 9 sidebar sections are fixed for v1 but may grow via core upgrade (round table review required to add a 10th). The sidebar is a controlled vocabulary — not fixed forever, but not auto-extended.

The UI is capability-driven at the panel level: each panel shows whatever is plugged into its capability class. The Skills panel shows whatever skills are registered. The Adapters panel shows whatever adapters are registered. Adding a new skill causes it to appear in the Skills panel on next render. Removing an adapter causes it to disappear. UIs may hard-code **capability class names** (the 9 sidebar sections) but must never hard-code **individual component names** (calculator_skill, openai_adapter).

The user only ever talks to the orchestrator. Workers never surface messages, explanations, or results directly to the user. Everything flows through the orchestrator: the orchestrator routes a task to a worker, the worker does the work and returns the result, the orchestrator synthesises and informs the user. The chat surface is uniquely in the Orchestrator panel. Other panels show *data* (worker status, task state, skill list) but not conversation. The Log drawer shows raw traces from all components but is observability, not conversation.

### 9. Observability by default.

The core exposes traces, errors, and state introspection through a uniform contract. Components do not implement their own logging — they emit structured events via a TraceEmitter (constructor-injected, never global). The Log drawer renders these events with level filtering. Persistence to trace memory is automatic. The Orchestrator panel surfaces system state to the user without requiring them to read logs.

### 10. Security via reasoning, not just permissions.

The system has a default-deny stance for components not authored by the user or the orchestrator. A **Security Guard** worker — a lightweight expert model trained for safety assessment — reviews every externally-sourced component before it runs. Components authored by the user or orchestrator are trusted by default. The Security Guard can approve, warn, or reject; warnings must be explicitly dismissed by the user (via the orchestrator) before the component runs. The Security Guard's verdict goes to the orchestrator, which informs the user. The user never sees the Security Guard's raw output; they see the orchestrator's synthesis. Ongoing behavioural auditing is performed on all running components. Sandbox isolation is available as an additional layer for high-risk components, on top of the Security Guard's verdict.

### 11. Dependency injection, no globals.

All components receive their dependencies (adapters, memory router, trace emitter, etc.) via constructor arguments. Components never instantiate their own dependencies, never use `import` to reach across module boundaries for runtime state, never use module-level singletons. No `global` keyword in any production file. No "deferred violation" category — if a global seems unavoidable, STOP and redesign. One file (the composition root) is the only place that instantiates core components; every other file receives dependencies via constructor. This makes the full dependency graph auditable in one place.

### 12. Plain-English docstrings on every function.

Every `def` and `async def` (including methods) must have a docstring. The docstring's first line must be a complete sentence in plain English, comprehensible to someone with no programming knowledge, describing what the function does (not how). Multi-line docstrings should explain inputs, outputs, and errors in plain language. Jargon ("async", "await", "coroutine", "dispatch", "yield", "instantiate") must be replaced with plain equivalents ("send", "wait for", "running task", "send to", "produce", "create"). Ruff rule `D103` (missing docstring) is enforced in CI; docstring quality is enforced by code review. This applies to AI-generated code (Devin) and human-contributed code equally.

### 13. Strong, robust.

The core does what it claims, without caveat. It fails gracefully, isolates faults, and recovers without manual intervention. When a component crashes, the system stays up, the error is reported via trace, and other components keep working. The orchestrator tells the user what happened (in plain language); it does not expose stack traces unless the user opens the Log drawer.

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

A new adapter must be addable in a single file. The core must never import an adapter by name. The core must never assume a specific adapter is present. The system must function with zero adapters (degraded but running) and with twelve adapters (full capability).

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

### Workers — domain experts

Each worker is a domain expert. A worker has: a profile (worker_id, expertise, capabilities), an LLM adapter (the brain it runs on), and a set of skills it can invoke. Workers may use lightweight models specifically trained for their domain.

Workers receive tasks from the orchestrator. They decide which skills to invoke (sequentially or as a DAG), execute the work, and return the result. Workers never talk directly to the user. The orchestrator is the system's single voice.

One worker is the **Security Guard** — a lightweight expert model trained for safety assessment. It reviews every externally-sourced component before it runs, returns a verdict (APPROVED/WARN/REJECT) to the orchestrator, and performs ongoing behavioural auditing.

### Gateways — interface surfaces

**Core UIs** (part of the core, capability-driven):
- **Web** — browser-based UI, served locally. 9-section sidebar + Log drawer.
- **TUI** — full-screen terminal interface. Same 9-section structure.
- **CLI** — terminal interface for scripting. Subcommands mirror the 9 sections.
- **Phone app** — connects via cloud relay to the core. Same 9-section structure.

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
- **A framework for others.** Built for one user.
- **Feature-complete at v1.** Capabilities are wired as the user needs them.
- **Opinionated about which adapter, skill, or memory backend is "best."** All are welcome.
- **A single-LLM wrapper.** A system that only works with one provider has failed its premise.
- **A rewrite of any existing project.** Patterns may be borrowed; code will not be.
- **A research project.** Must be usable daily.
- **Built for scale.** One user, one machine (or a small personal cluster eventually).
- **Multi-tenant.** One operator only. The user is the operator.
- **Distributed in v1.** Multi-machine core is designed-for-future, not built-now. Distributed consensus is explicitly out of scope.
- **Optimised for performance over modularity.** If a perf optimisation hurts modularity, modularity wins.

---

## Success Criteria

The core is solid if and only if all of the following are true.

### Modularity criteria (highest priority)

1. **Fault isolation test**: kill any skill mid-execution → system stays up, error is reported via trace, other skills keep working.
2. **Independence test**: stop any adapter → other adapters and all skills keep working.
3. **Delete any single non-core file** — the system starts without crashing, gracefully degrades capabilities that depended on it, and surfaces what's missing to the user.
4. **Acyclic dependency test**: CI checks the import graph; cycles fail the build.
5. **No globals**: `grep -rn "^global\|global _" core/` returns zero matches in production files. Static analysis test enforces this; CI fails on any violation.
6. **Constructor arg cap**: no class in the core has more than 7 constructor arguments. Static analysis test enforces this.

### Flexibility criteria (highest priority)

7. **Add a new adapter** in a single file, under 100 lines of code, without touching the core.
8. **Add a new skill** in a single file, under 100 lines of code, without touching the core.
9. **Add a new memory backend** in a single file, without touching the core.
10. **Swap any adapter, skill, or memory backend** without modifying any other component.
11. **A new model released tomorrow** — adapter added same day, no core changes.
12. **A new memory paradigm invented** — backend added without core changes.
13. **A new protocol (MCP successor, A2A variant) published** — adapter added without core changes.
14. **A new user domain** — skill added in one file, no core changes.
15. **Time-to-add**: from "I have a new adapter idea" to "it's plugged in and working" should be < 30 minutes for someone who's done it before.

### UI criteria

16. **Add a new skill** — it appears in the web UI, TUI, CLI, and phone app on next render, with zero edits to any UI file.
17. **Remove an adapter** — it disappears from the web UI, TUI, CLI, and phone app on next render, with zero edits to any UI file.
18. **No hard-coded individual component names in UI control flow**: `grep -rE '"(calculator|websearch|openai|ollama|postgres|qdrant)' web/ tui/ cli/ phone/` returns zero matches. Capability class names (the 9 sidebar sections) are permitted.

### Local-first criteria

19. **Run fully local** with zero cloud dependencies and zero network calls.
20. **Survive any single adapter disappearing** (provider bankruptcy, model deprecation, API change) without touching the core.

### Observability criteria

21. **Every component emits traces** via the constructor-injected TraceEmitter.
22. **Log drawer renders** all traces with level filtering, component filtering, and search.
23. **The orchestrator surfaces system state** to the user in plain language without requiring them to open the Log drawer.

### Security criteria

24. **External component review**: every externally-sourced component (not authored by user or orchestrator) is reviewed by the Security Guard worker before it runs.
25. **Default-deny for external**: external components do not run until the Security Guard approves or the user explicitly overrides a warning.
26. **Ongoing behavioural audit**: running components are periodically audited for suspicious patterns.

### Code quality criteria

27. **Plain-English docstrings**: every `def` and `async def` has a docstring comprehensible to a non-programmer. Ruff D103 enforced in CI.
28. **Composition root**: one file is the only place that instantiates core components. Every other file receives dependencies via constructor.
29. **Dependency injection only**: no module-level singletons, no `global` keyword, no deferred violations.

### Longevity criteria

30. **The core, after one year of development**, is still readable in a single sitting by a competent reader. (Guideline, not a gate.)
31. **Rust-migratable**: contracts are language-agnostic (manifests, schemas, not Python-specific constructs). A future Rust core could satisfy the same contracts without breaking pluggables.

Criterion 3 (delete any file, system starts) is the most important test of modularity. Criterion 18 (no hard-coded individual component names) is the most important test of capability-driven UI.

---

## Resolved Open Questions

The following open questions from Rev 1 have been resolved by the round table and the user's architecture decisions. They are recorded here for the historical record; future revisions should not re-litigate them.

| Q | Question | Resolution | Source |
|---|---|---|---|
| Q5 | What is the boundary between skill and adapter? | **Adapter** = model-host connector (translates between core protocol and a model provider's API). **Skill** = domain-specific capability that uses (or doesn't use) an adapter's output to produce a result. An MCP server is an adapter if it hosts model calls, a skill if it exposes tools; hybrids must declare both facets in their manifest. A code-execution runtime is a skill. | Round table + user |
| Q6 | Central event bus vs direct calls? | **Event bus with typed channels.** The core provides a lightweight in-process message bus. Direct calls between components are forbidden — all inter-component communication goes through the bus. The bus is NOT an orchestrator; it is transparent infrastructure. If a component dies mid-conversation, the bus detects the timeout and routes the failure notification to the orchestrator. | Round table |
| Q7 | Process isolation between skills? | **Same-process by default, opt-in sandbox per skill.** The user decides the trust level: trusted skills run in-process; untrusted skills run sandboxed (subprocess or WASM). Default trust level for external components is "low" — they start sandboxed until the Security Guard approves and the user explicitly trusts them. | Round table + user (Security Guard) |
| Q10 | What language and runtime? | **Python for v1, Rust-migratable later.** Contracts are language-agnostic (manifests, schemas). A future Rust core could satisfy the same contracts without breaking pluggables. Hot paths are identified and kept tight; Rust-rewrite of those paths is a future Plan N if needed. | User |
| Q11 | What is the smallest possible core? | **LOC budget is a guideline, not a gate.** Target 1,500–3,000 LOC for the core. The hard gates are: fault isolation, independence, acyclic deps, constructor arg cap of 7. Modularity and flexibility trump LOC minimisation. | Round table + user (modularity priority) |
| Q12 | What does "decentralised" mean in practice? | **Question dropped — P8 was redundant.** Modularity (P2, P3) and the lean orchestrator (P7) cover the intent. The orchestrator routes; the event bus is transparent infrastructure; everything else is pluggable. | User |
| Q15 | What is the security model? | **Security Guard worker + default-deny for external.** User/orchestrator-authored components are trusted by default. External components are reviewed by the Security Guard worker before running. The Security Guard's verdict goes to the orchestrator, which informs the user. Sandbox available as an additional layer. | Round table + user |
| Q16 | How do UIs auto-populate without hard-coding component names? | **Capability-class-driven panels.** The 9 sidebar sections are fixed capability class names (hard-coded). Panel contents are populated dynamically from the capability registry — individual component names are never string literals in UI source. | User (9-section sidebar) |
| Q17 | Are UIs truly core, or are they core-hosted? | **UIs are core.** The 9-section sidebar IS the OS shell, which is legitimately core. The sidebar structure is the core UI contract; panel contents are capability-driven. No split between "UI engine" and "UI presentation" — the whole thing is core because it renders the framework's own architecture. | User |
| Q18 | What does a capability look like to a UI? | **Declared by the capability itself in its manifest.** Each skill/adapter/memory backend declares: name, description, icon, TUI shortcut, CLI subcommand, input/output schemas (JSON Schema). The core strips rendering-specific attributes before routing; the UI receives them for rendering. | Round table |

---

## Open Questions for the Round Table (Carried Forward + New)

The following remain open. The round table's job in the next review pass is to resolve or refine these.

### Carried forward from Rev 1

**Q1 — What is the adapter contract?**
Proposed resolution (round table): capability-based discovery via a static manifest (TOML or YAML) declaring capability categories (text, vision, audio, tool-calling, streaming, batching, embeddings) plus a protocol/interface the core routes to. Not duck-typed (too fragile), not a shared base class (drifts across implementations). The manifest is a fixed-format declaration; the interface is a function signature contract enforced by runtime type checking.
**Trade-off**: manifests and runtime contract checks add ceremony — every adapter needs both a manifest file and a conforming implementation.
**Status**: proposed, awaiting round table confirmation.

**Q2 — How are skills discovered and registered?**
Proposed resolution (round table): hybrid — directory scan on startup discovers skill directories, each containing a manifest (same format as Q1). The unit of a skill is a directory (can be a single file, but directory is canonical to allow assets, submodules, config files). A decorator-based API is offered as syntactic sugar that writes the manifest automatically at build time.
**Trade-off**: directory scan means the skill must be "installed" into a known location, adding a step compared to decorator-only.
**Status**: proposed, awaiting round table confirmation.

**Q3 — What is the memory abstraction?**
Proposed resolution (round table): capability-based, not universal interface. A memory backend declares its capabilities (vector, graph, relational, document, episodic, etc.) in its manifest. The core routes queries to backends that declare the relevant capability. Cross-backend queries (vector + graph) are handled by the core as a scatter-gather pattern.
**Trade-off**: scatter-gather for cross-backend queries introduces latency and potential inconsistency if backends return conflicting results.
**Status**: proposed, awaiting round table confirmation.

**Q4 — How does the core route between adapters without knowing them?**
Proposed resolution (round table): capability advertisement via manifests. Each adapter advertises its capabilities and a priority/weight. When a request arrives, the core inspects the request's requirements and routes to the highest-priority adapter that satisfies all requirements. The user can override priority per-request.
**Trade-off**: multi-capability requests (e.g., "describe this image in French") require the core to either find a single adapter that handles both, or compose multiple adapters — composition is not addressed by simple priority routing.
**Status**: proposed, awaiting round table confirmation. Note: under this project's architecture, the orchestrator (not the core) routes; the orchestrator picks a worker, the worker picks an adapter. Q4 may need reframing.

**Q8 — How to handle adapter, skill, and memory versioning?**
Proposed resolution (round table): semantic versioning with capability negotiation. Each component declares a version and its capability set. On startup, the core builds a dependency graph and rejects the system if two components declare incompatible versions. "Latest wins" is the fallback only for cosmetic attributes, never for contracts.
**Trade-off**: strict version checking at startup means a single incompatible component can prevent the system from starting.
**Status**: proposed, awaiting round table confirmation.

**Q9 — How to test a system designed to support "everything"?**
Proposed resolution (round table): all three — conformance suites per capability class, contract tests against the core's public contracts, and property-based tests for invariants (e.g., "deleting any non-core file does not prevent startup"). CI gate requires conformance + contract tests to pass; property-based tests run on schedule.
**Trade-off**: conformance suites are expensive to maintain as capability classes grow.
**Status**: proposed, awaiting round table confirmation.

**Q13 — How does the system learn and improve?**
Proposed resolution (round table): retrospective traces stored as ordered events in the episodic and trace memory backends. The system does not learn autonomously — a learning loop is a skill, not a core capability. A "self-correction" skill reads traces, evaluates outcomes, and produces procedural memory updates.
**Trade-off**: if the user never installs a self-correction skill, the system never learns.
**Status**: proposed, awaiting round table confirmation.

**Q14 — What is the persistence story?**
Proposed resolution (round table): many stores, each owned by a memory backend. No single canonical store. Working memory (volatile, in-process) is owned by the core for the duration of a task. Episodic and trace memory are written by the core but stored in backends. Crash recovery: on restart, the core replays the last incomplete trace from trace memory to reconstruct task state, then prompts the user to resume or discard.
**Trade-off**: distributed state across many backends makes atomic transactions across backends impossible.
**Status**: proposed, awaiting round table confirmation.

### New questions added in Rev 2

**Q19 — Trained expert model lifecycle.**
The user wants workers to use lightweight models specifically trained for narrow tasks. How are these models trained, versioned, acquired, and retired? Does the framework ship a training pipeline, or does it expect pre-trained models? How does a worker declare "I need the marine-weather-expert-v2 model" and how does the system acquire it if missing?

**Q20 — Skill DAG execution model.**
Composite skills are DAGs of atomic skills. When a worker executes a composite skill, what runs the DAG? Is it the worker itself, a shared DAG executor in the core, or a separate "execution engine" component? How are partial failures handled (one node fails — does the whole DAG fail, or does it retry, or does it skip)? How are conditional branches expressed in the DAG?

**Q21 — Cloud relay protocol.**
The phone app connects via a cloud relay. What protocol? Is the relay a custom service, or do we use an existing one (Tailscale, Syncthing's relay, Matrix)? What's the auth model? How does the core advertise itself to the relay without exposing it to the public internet? What happens when the relay is down — can the phone app fall back to local network?

**Q22 — Phone app scope.**
Does the phone app render all 9 sections, or a subset (e.g., chat + tasks + alerts, not the full Skills canvas)? Is the phone app a thin client (renders whatever the core sends) or a thick client (has its own UI logic)? Native app, PWA, or web app wrapped in a native shell?

**Q23 — Loop task persistence.**
Permanent loop tasks must survive restarts. Where are they stored? In trace memory? In a dedicated scheduling backend? What happens if a loop's trigger time arrives while the system is down — does it run on next start, or skip?

**Q24 — Multi-machine core (designed-for-future).**
The architecture must accommodate a future multi-machine core. What does "accommodate" mean concretely? Replicable state? Instance identity? A sync protocol? A discovery protocol for cores to find each other? We don't need to build this in v1, but we need to know what we're not foreclosing.

**Q25 — Worker-to-worker communication.**
Can workers talk to each other directly (via the event bus), or only through the orchestrator? If the Security Guard worker wants to flag a skill mid-execution, does it interrupt the worker running the skill, or does it tell the orchestrator who tells the worker? This affects the orchestrator's "single voice" guarantee.

**Q26 — Composition root bootstrap.**
The composition root instantiates all components. But what instantiates the composition root? Is there a `main()` that boots the composition root? How does the composition root know what to wire (config file? directory scan? hard-coded list)? This is the chicken-and-egg of DI — needs a clean answer.

---

## Closing

This project is a bet that the next decade of AI tooling will not be won by the team that picks the right model, but by the team that builds a core capable of absorbing whatever model comes next. The core must be modular enough to outlive its first generation of adapters, robust enough to run without any of them, and flexible enough that the user never has to ask permission to add a new one.

The round table's job is to find the architecture that makes this real. The job of this document is to make sure every member of the round table argues against the same target.

If the round table returns an architecture that satisfies every principle, passes every success criterion, and answers every open question — build it. If it returns an architecture that satisfies most but not all, name what is missing and send it back. Do not compromise on the principles to ship sooner. The whole point of the project is that the core outlives the rush.

---

## Revision history

- **Rev 1** (2026-06-27): Original vision document. 9 principles, 15 success criteria, 18 open questions. Sent to 6-AI round table.
- **Rev 2** (2026-06-27): Post-round-table revision. Incorporates 4 panel responses + 13 user architecture decisions. P8 dropped. P7 reframed (modularity + flexibility over simplicity). P9 reframed (OS shell, 9 sections). P6 clarified (cloud-relayed). P10 (Observability) added. P11 (Security Guard) added. P12 (DI) added. P13 (Docstrings) added. 15 success criteria → 31 criteria (modularity, flexibility, UI, local-first, observability, security, code quality, longevity). 10 of 18 open questions resolved; 8 carried forward; 8 new questions added (Q19–Q26). Sent to round table for clean-pass check.
