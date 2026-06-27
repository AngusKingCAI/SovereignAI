# Founding Vision — The Unnamed Project

> **Status**: Pre-architecture. This document exists to give the round table a single target to argue against. It does **not** prescribe modules, file layouts, frameworks, languages, or protocols. It states what the project is trying to become. The round table decides how.

> **Reading time**: ~8 minutes.

---

## Preamble

This project has no name yet. That is deliberate — names constrain thinking. "Sovereign AI", "Jarvis", "Assistant", "Agent" all carry baggage. The round table may name it; for now it is **the project**.

This document is not a specification. It is a charter. Every architectural decision the round table debates must be tested against the principles below. If a proposal violates a principle, the principle wins. If a proposal satisfies every principle but the round table still rejects it, the principle is incomplete and must be amended before the next round.

---

## The Premise

Software is being rebuilt around models that did not exist three years ago and will be obsolete in three more. Most teams building these systems pick one provider, one memory store, one orchestration pattern, and ship. When the next model lands — different context window, different modality, different pricing, different protocol — they rewrite.

This project rejects that approach.

The aim is a **solid core that can adapt to all new things that come out**. The core is small, stable, and deliberately ignorant of what attaches to it. Memory, adapters, skills, and models are not part of the core — they are equal citizens plugged into it. A new memory paradigm invented next year means adding a backend, not editing the core. A new model provider launching tomorrow means adding an adapter, not editing the core. A new skill needed means adding a file, not editing the core.

The system must be **fundamentally decentralised and modular**. No central authority decides which adapter is canonical. No central registry picks the "right" memory backend. No orchestrator hard-codes a skill. Every capability is optional, replaceable, and reachable through a uniform contract that the core does not own.

This is not a framework. Frameworks impose structure on others. This is a personal system built for one user, designed to absorb whatever the next decade throws at it without forcing a rewrite.

---

## Core Principles

### 1. The core is sacred.

The core grows reluctantly. Every line added must justify itself against the cost of every future adapter, skill, and memory backend having to live with it. If a feature can live outside the core, it must. If it cannot, the burden of proof is on adding it, not on leaving it out.

### 2. Everything else is pluggable.

Adapters, skills, memory backends, model hosts, gateways — all are equal. None is more privileged than another. The system runs with any subset. A user with one local adapter and one skill has a working system. A user with twelve adapters, fifty skills, and four memory backends has the same core.

### 3. No provider lock-in.

Swap any component without touching the core or any other component. If removing one piece breaks another, the architecture has failed. The test is mechanical: delete any adapter file, any skill file, any memory backend file. The system must continue to start and serve the remaining capabilities.

### 4. Local-first by default, cloud by choice.

The system runs fully offline with zero cloud dependencies and zero network calls. Cloud is an escalation, not a foundation. A user who never wants to touch a cloud API key still gets a working system. A user who wants to escalate a hard task to a frontier model can — but the cloud is a guest, not a host.

### 5. Wire as you go.

No new horizontal capability until the existing stack is reachable and demonstrably improving outputs. A skill that is not wired is a skill that does not exist. An adapter that is not invoked is an adapter that does not exist. The system ships with what it uses, not with what it might someday use.

### 6. One user, one system.

Built for a single individual's context — their files, their tools, their domains, their habits. Not multi-tenant. Not enterprise. Not general-purpose. The user is the operator and the only operator.

### 7. Strong, robust, modular, simple core.

**Strong**: it does what it claims, without caveat. **Robust**: it fails gracefully, isolates faults, and recovers without manual intervention. **Modular**: components come and go without ceremony. **Simple**: a new reader can hold the core in their head in a single sitting. If the core cannot be held in a head, it has grown too large.

### 8. Decentralised by design.

No central orchestrator owns the flow. No central registry owns discovery. No central authority owns truth. Components advertise capabilities; the core routes; backends fulfil. The shape of the system emerges from what is plugged in, not from what the core decrees.

### 9. UIs are core. Capabilities auto-populate.

The web UI, TUI, CLI, and any other interface surface are **part of the core**, not pluggable components. They are the lens through which the user sees the system — and they must reflect, in real time, every adapter, skill, memory backend, and model that is plugged in. Adding a new skill must cause that skill to appear in every UI without editing any UI file. Removing an adapter must cause it to disappear from every UI without editing any UI file. UIs are capability-driven, not feature-driven: they render whatever the system advertises, and they render nothing the system does not advertise. A UI that hard-codes a skill name, an adapter name, or a memory backend name has violated this principle. The contract is one-way: components declare what they are; UIs discover and render; UIs never assume what exists.

---

## The Capability Surface

The core must **support** the following capability classes without prescribing their implementation. This is what the system must accept — not what it must contain at v1. v1 may ship with one example of each class; the architecture must allow dozens more to be added later without friction.

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

The contract must allow any of these to be added without the core knowing they exist. The core routes memory operations; backends fulfil them. A backend that can only do vector search is a valid backend. A backend that can do vector + relational is also valid. The core must not assume any specific backend's capabilities.

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

A new skill must be addable in a single file. The core must never hard-code a skill's name. Skills must be discoverable, invocable, and replaceable without touching the core.

### Models — all deployment modes, treated as interchangeable

- **Local models** — running on user hardware, fully offline.
- **Cloud models** — running on provider infrastructure, on-demand.
- **Hybrid models** — local for routing/triage, cloud for heavy lifting.
- **Federated models** — composed across multiple providers in a single request (e.g. local summariser + cloud reasoner + local verifier).

The core must not assume any specific model is present. It must tolerate a world where the only model available is a 7B local, and a world where every frontier model is one call away. Model tier routing — if it exists — is a strategy, not a core feature.

### Gateways — interface surfaces

Interface surfaces split into two classes:

**Core UIs** (part of the core, capability-driven, auto-populating):
- **Web** — browser-based UI, served locally. Renders every plugged-in capability.
- **TUI** — full-screen terminal interface for interactive use. Renders every plugged-in capability.
- **CLI** — terminal interface for scripting. Every skill, adapter, and memory backend is reachable as a subcommand without manual registration.

**Pluggable gateways** (external, optional, route messages into the core):
- **Voice** — speech in, speech out, hands-free operation.
- **IM** — chat-based access (Telegram, Signal, future).
- **API** — programmatic access for other agents and external systems.
- **Future gateways** — added without touching the core.

The distinction matters: a UI is the user's window into the system and must reflect its current shape. A gateway is a pipe that delivers input and collects output; it does not need to render capabilities. UIs are core; gateways are pluggable. Both can coexist and run simultaneously. A user might use any combination, simultaneously. The core must serve them all from the same state. A message arriving via voice and a message arriving via the web UI must be handled by the same pipeline.

---

## Non-Goals

This project is explicitly **NOT**:

- **A SaaS.** No hosting, no multi-tenant, no subscription tier, no usage metering.
- **A chatbot.** Conversation is one gateway among many, not the product.
- **Cloud-locked.** Any architecture that requires a specific cloud service to function is rejected.
- **Enterprise software.** No RBAC, no org charts, no compliance certifications, no audit trails for auditors.
- **A framework for others.** Built for one user. If others find it useful, fine. If not, also fine. The architecture does not bend to accommodate hypothetical second users.
- **Feature-complete at v1.** Capabilities are wired as the user needs them. An unwired capability is not a bug — it is a future plan.
- **Opinionated about which adapter, skill, or memory backend is "best."** All are welcome. None is privileged. The system does not pick winners.
- **A single-LLM wrapper.** A system that only works with one provider has already failed its premise.
- **A rewrite of any existing project.** The architecture will be informed by prior art but designed from scratch. Patterns may be borrowed; code will not be.
- **A research project.** The system must be usable daily. Elegance is welcome; theoretical purity is not a substitute for working software.
- **Built for scale.** One user, one machine (or a small personal cluster). Architectures optimised for thousands of concurrent users are explicitly out of scope.

---

## Success Criteria

The core is solid if and only if all of the following are true. If any becomes false, the architecture has drifted and must be corrected before further capability work.

1. **Add a new adapter** in a single file, under 100 lines of code, without touching the core.
2. **Add a new skill** in a single file, under 100 lines of code, without touching the core.
3. **Add a new memory backend** in a single file, without touching the core.
4. **Swap any adapter, skill, or memory backend** without modifying any other component.
5. **Run fully local** with zero cloud dependencies and zero network calls.
6. **Survive any single adapter disappearing** (provider bankruptcy, model deprecation, API change) without touching the core.
7. **A new model released tomorrow** — adapter added same day, no core changes.
8. **A new memory paradigm invented** — backend added without core changes.
9. **A new protocol (MCP successor, A2A variant) published** — adapter added without core changes.
10. **A new user domain** — skill added in one file, no core changes.
11. **The core, after one year of development**, is still readable in a single sitting by a competent reader.
12. **Delete any single non-core file** — the system starts and serves the remaining capabilities without error.
13. **Add a new skill** — it appears in the web UI, TUI, and CLI on next start, with zero edits to any UI file.
14. **Remove an adapter** — it disappears from the web UI, TUI, and CLI on next start, with zero edits to any UI file.
15. **A UI never hard-codes a component name.** Grep the UI source for any adapter, skill, or memory backend's name — there must be zero matches.

Criterion 15 is the strictest test of capability-driven UI. If it fails, the UI has silently become feature-driven and the principle is broken.

Criterion 12 is the most important test of modularity. Criterion 15 is the most important test of capability-driven UI.

---

## Open Questions for the Round Table

The following decisions are explicitly deferred to the round table. This document does not pre-judge them. The round table's job is to debate them, propose architectures that resolve them, and stress-test those architectures against the principles above.

1. **What is the adapter contract?** Protocol, abstract base class, duck-typed interface, or capability-based discovery? How does a new adapter announce what it can do (text, vision, audio, tool-calling, streaming, batching, embeddings) without the core knowing the full list?

2. **How are skills discovered and registered?** Decorator, manifest file, entry point, directory scan, or hybrid? What is the unit of a skill — a function, a class, a module, a package?

3. **What is the memory abstraction?** A universal interface all backends implement, or capability-based (a backend declares what it can do — vector, graph, relational, document — and the core routes accordingly)? How does the system handle a query that needs both vector search and graph traversal?

4. **How does the core route between adapters without knowing them?** Capability negotiation, capability advertisement, registry, marketplace pattern, or something else? Who decides which adapter handles a given request — the core, the request, or the user?

5. **What is the boundary between skill and adapter?** Is an MCP server a skill or an adapter? Is a tool-calling model an adapter or a skill host? Is a code-execution runtime a skill or an adapter? The taxonomy must be clean or it will rot.

6. **Central event bus vs direct calls?** Does the core mediate all communication between components, or do components talk to each other directly? What is the failure model if a component dies mid-conversation?

7. **Process isolation between skills?** Same process, subprocess, container, WebAssembly sandbox, or all of the above as a per-skill choice? What is the trust boundary — does a skill have access to the user's full filesystem, a sandbox, or nothing by default?

8. **How to handle adapter, skill, and memory versioning?** Semantic versioning, capability negotiation, or "the latest wins"? What happens when two skills depend on incompatible versions of a third skill?

9. **How to test a system designed to support "everything"?** Conformance suites per capability class, contract tests against the core's contracts, property-based tests, or all three? What does the CI gate look like?

10. **What language and runtime?** Python, Rust, Go, TypeScript, or something else? The choice must be justified against the modularity and adaptivity goals — not against familiarity. Python has ecosystem; Rust has safety and performance; Go has deployment simplicity. What serves the principles?

11. **What is the smallest possible core?** Can the core be expressed in 500 lines? 1,000? 5,000? The smaller the better, but it must still be useful. Propose a core size budget and defend it.

12. **What does "decentralised" mean in practice?** No central registry? No central orchestrator? No central authority? All three? If there is no orchestrator, who decides what runs next?

13. **How does the system learn and improve?** Self-correction loops, evaluation harnesses, debate pools, retrospective traces — all are mentioned in the capability surface. How do they fit into a decentralised architecture without becoming a hidden core?

14. **What is the persistence story?** Where does state live? Is there one canonical store, or many? How does the system recover from a crash mid-task?

15. **What is the security model?** Local-first means the user owns everything — but skills can execute code, adapters can make network calls, memory can store secrets. What is the default trust level, and how does the user override it?

16. **How do UIs auto-populate without hard-coding component names?** When a new skill is dropped into the system, the web UI, TUI, and CLI must each render it on next start. What is the discovery protocol — capability manifest, runtime introspection, event emission, directory scan? What is the rendering contract — does each UI receive a list of capabilities and render them generically, or does each capability ship its own UI fragment that the core UI hosts? Both approaches have tradeoffs: pure generic rendering keeps UIs small but loses skill-specific affordances; fragment-hosting preserves richness but risks the UI becoming a patchwork of foreign code. The round table must pick one (or propose a hybrid with a clear rule for when each applies) and defend it.

17. **Are UIs truly core, or are they core-hosted?** Principle 9 says UIs are core. But the web UI, TUI, and CLI have very different rendering models — HTML/CSS/JS, terminal escape codes, argparse. Are they three implementations of one core UI contract, or three separate core modules that happen to share a discovery protocol? If the former, what is the abstract UI contract? If the latter, how do we keep them in sync when the capability surface changes?

18. **What does a capability look like to a UI?** A skill needs a name, a description, an icon (for web), a shortcut (for TUI), and a subcommand (for CLI). An adapter needs a name, a status indicator, and a configuration surface. A memory backend needs a name, a type, and a query interface. Are these attributes part of the capability itself (declared by the component) or part of a separate presentation layer (declared alongside the component)? If the former, how do we keep capabilities from dragging UI concerns into their domain? If the latter, who maintains the presentation layer when capabilities are added?

---

## Closing

This project is a bet that the next decade of AI tooling will not be won by the team that picks the right model, but by the team that builds a core capable of absorbing whatever model comes next. The core must be small enough to outlive its first generation of adapters, robust enough to run without any of them, and modular enough that the user never has to ask permission to add a new one.

The round table's job is to find the architecture that makes this real. The job of this document is to make sure every member of the round table argues against the same target.

If the round table returns an architecture that satisfies every principle, passes every success criterion, and answers every open question — build it. If it returns an architecture that satisfies most but not all, name what is missing and send it back. Do not compromise on the principles to ship sooner. The whole point of the project is that the core outlives the rush.
