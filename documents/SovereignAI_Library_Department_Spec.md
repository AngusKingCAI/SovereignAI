# SovereignAI — Library Department: Implementation Specification

**Document Type:** Deep Implementation Spec
**Author:** Angus / Claude (design pass)
**Audience:** GLM (implementing agent) + Round Table review
**Status:** Draft v1 — ready for Round Table review
**Date:** 2026-06-29
**Depends on:** `SovereignAI_Architecture_Decisions.md`, `project-vision-Rev5.md`, `SovereignAI_Orchestrator_Spec.md`

---

## 0. Purpose

This document specifies the **Library Department** — SovereignAI's single, permanent department responsible for **documenting everything that happens, everywhere, at every level**, and for organizing that documentation so it can be found again, traversed, and reasoned about.

Every other department spec written so far (Coding, Research, Education) refers to "the Librarian" as a role that routes memory queries to the correct backend. This document expands that role into its proper scope: the Librarian is not a query router bolted onto each department — it is a department in its own right, one that **observes** every other department's work as it happens and reads for them on request, for everything, all the time.

**The core idea:** nothing in SovereignAI persists by a department walking up to a database and writing to it directly — and a department doesn't even need to walk up to the *Library* and ask it to remember something. A Coding Task's diff, a Research Deliverable, a training job's benchmark scores, a conversation the Owner had with the Orchestrator last Tuesday — all of it is witnessed by the Library as it happens, through the same trace events every component already emits for observability (vision Rev 5, Principle 9). The Library decides what's worth keeping, where it's stored, how it's categorized, what it's connected to, and how it can be found again — without ever asking a department to self-report. The **Memory panel** the Owner sees in the sidebar is not a separate thing with its own logic — it is simply the Library's catalog, made browsable.

---

## 1. Company Metaphor Placement

| Entity | Role in Library Department |
|--------|------------------------------|
| **Owner (User)** | Browses the Library's catalog via the Memory panel; sets retention and privacy policy; can manually annotate, correct, merge, or delete records |
| **Orchestrator (CEO)** | Queries the Library when answering the Owner directly ("what did Coding do last Tuesday?"); never bypasses the Library to read a backend directly |
| **The Librarian** | Permanent department head — and, per current judgment, the **only** worker this department needs. Observes every other department's trace events to build episodic memory, classifies and links what it observes into the neural map, and answers read requests from every other department. See §3 for why a single Librarian is likely sufficient, and §3.4 for the conditions under which a specialised Cataloguer Worker would be split out |
| **Every other department's Manager** (Coding Manager, Research Manager, Education Manager, and future Managers) | Subjects of the Library's observation, not implementers of memory logic and not clients submitting writes. A department never talks to Qdrant, Postgres, or a graph backend directly, and never explicitly tells the Library what to remember — it does its work, emits the same trace events it always would, and the Library documents it unprompted. Departments remain clients of the Library only for **reads** — asking it a question — never for writes |
| **Security Guard** | Audits the Library's provenance chain on demand; enforces retention/consent policy at the point of persistence (the Library checks with the Security Guard before persisting anything tagged as containing personal or sensitive data) |

The Library Department is a **permanent department** (not task-spawned) — there is exactly one, always running, the same way there is exactly one Orchestrator. It maintains the actual data: every memory backend (vector, graph, relational, document) that the core's memory capability class supports is, in practice, written to and read from only by the Library. It surfaces in the Workers panel under a dedicated "Library" section, and its catalog is exposed to the Owner via the existing **Memory** sidebar panel.

---

## 2. Relationship to the Core's Memory Capability

This is the most important boundary in this document, and it must not be blurred.

The core (per vision Rev 5, Core Scope and Capability Surface sections) already:
- Defines memory as a capability class with sub-types: **episodic, semantic, procedural, working, trace**.
- Routes memory operations to whichever backend declares the relevant capability (vector, graph, relational, document), without the core knowing what backends exist.
- **Automatically** persists trace memory via the constructor-injected TraceEmitter — every component emits structured trace events, and this persistence happens without any department or the Library asking for it.
- Owns **working memory** itself, in-process, volatile, for the duration of a task — this is not persisted and the Library has no role here.

**What this means for the Library:**

| Memory type | Who writes it | Library's role |
|---|---|---|
| **Working memory** | Core, in-process, per-task | None. Volatile, never reaches the Library, and there is nothing durable to observe while it's live — see §4.1 on why this is not a gap. |
| **Trace memory** | Core, automatically, via TraceEmitter | The Library does **not** write trace memory — it would be redundant with the core's automatic mechanism, and duplicating it would violate "the core is sacred, everything else is pluggable" by creating two competing persistence paths for the same data. Instead, the Library is a **continuous subscriber** to the live trace stream (the same one the Log drawer renders from) — this is its primary, ongoing input, not an occasional lookup. It also queries persisted trace memory directly (via the core's memory routing contract, the same way any client would) when answering a question that needs history older than what's currently in the live stream (see §9). |
| **Episodic memory** | The Library, built from what it observes on the trace stream | Every Coding Task, Research Job, Training Run, and Owner conversation turn becomes an episodic record, threaded together by the Library from the trace events those components were already emitting (§4) — not written at a department's request, since departments never request anything from the Library. This is the bulk of the Library's processing volume. |
| **Semantic memory** | The Library, derived | The Library distils facts and concepts out of episodic records over time (see §5) — e.g., "this codebase uses snake_case" stops being a one-off observation buried in a task record and becomes a standing semantic fact attached to the project. |
| **Procedural memory** | The Library, on request from a self-correction skill | Learned workflows and automation patterns. The Library stores these but does not generate them autonomously — per the vision doc, learning loops are skills, not core or department capability (Q13). A self-correction skill reads traces and episodic records (via the Library) and writes procedural memory updates back through the Library — this remains a request-response interaction because a skill is explicitly invoked to reason and write, unlike a department's ordinary work, which the Library only observes. |

The Library is therefore **the department-facing front door to memory** — it sits on top of the core's memory routing contract, consuming it the same way any client of the core would, but it adds the layer the core deliberately does not: deciding what's worth keeping, how it's categorized, and how it connects to everything else. The core moves bytes to backends. The Library decides what those bytes mean.

---

## 3. Why One Librarian, Not Many Workers

The other departments (Coding, Research, Education) decompose into multiple Worker types because their work has genuinely distinct phases requiring different skills — reading code is not writing code is not testing code. The Library's job does not have this property in the same way: **every observed event is processed the same way** (thread it, categorize it, store it, connect it to related records) regardless of which department it came from, and **every read is the same operation** (take a query, figure out which backend(s) and which category it touches, retrieve, assemble). The variation is in the *content*, not the *process*.

### 3.1 The case for a single Librarian

- **Consistency of categorization.** If Coding's writes were handled by one Worker and Research's by another, the two might categorize similar content differently (e.g., one tagging a "decision" record under `semantic` and the other under `episodic`). A single Librarian enforces one categorization scheme across the entire system — which is the entire point of having a Library rather than letting each department roll its own memory logic.
- **The neural map needs a single hand on it.** §5 describes a graph-based association layer connecting records across departments. This only stays coherent if one component is responsible for deciding when two records are related — splitting this across Workers risks a fragmented, inconsistent graph where Coding-originated nodes and Research-originated nodes use incompatible relationship semantics.
- **Low branching complexity.** Unlike Coding's six-stage pipeline or Research's multi-tier source waterfall, the Library's operation is fundamentally: classify → store → (optionally) link → (later) retrieve. This does not obviously benefit from parallel specialized workers the way a multi-stage pipeline does.

### 3.2 What the single Librarian actually does, end to end

The Library does **not** wait for departments to decide what's worth telling it. Departments do not author memory, the same way no component in SovereignAI implements its own logging (vision Rev 5, Principle 9) — a department deciding what's "significant enough" to write would be the department grading its own performance, and that self-reporting bias is exactly what an observability-first architecture is designed to avoid. Instead, the Library is a **subscriber to the trace stream**, the same substrate the Log drawer already renders from:

1. **Subscribe** to the event bus's trace stream — every structured event any component emits via its constructor-injected TraceEmitter (vision Rev 5, Principle 9) is visible to the Library, filtered to the components/departments it's responsible for documenting (in practice: all of them).
2. **Classify** each observed event (or, more often, a completed run of related events — see "threading" below) into one or more memory types and categories (§5).
3. **Route** the storage operation to the correct backend(s) via the core's memory routing contract — the Librarian does not talk to Qdrant or Postgres by name, it declares the capability it needs (vector, graph, relational, document) and the core's routing engine resolves the backend, exactly as it would for any other component.
4. **Link** the new record into the neural map — checking for existing related nodes and creating/updating graph edges (§5.3).
5. **Respond** to reads by querying across whichever backends and categories the query touches, assembling a coherent answer (which may require the scatter-gather pattern the core already supports for cross-backend queries).

This means the Library's relationship to every other department is **observer, not client-server**. A department never calls "save this" — it just does its work, emitting the same trace events it would emit anyway for the Log drawer's benefit, and the Library is one more consumer of that stream, alongside the Log drawer. See §4 for exactly what the Library reads off the stream and how it threads events into coherent episodic records.

### 3.3 Concurrency note

Because the Library observes every department's trace events through one subscription point, processing throughput is a legitimate scaling question once multiple departments are active simultaneously (e.g., Coding and Research both completing tasks in the same minute, each emitting their own stream of trace events). This is addressed structurally, not by adding more Librarian instances: the trace stream is consumed by an internal worker pool that drains a queue of unprocessed events — concurrency in the implementation, not multiple decision-making entities. A department's own work is never blocked by the Library's processing, since the Library is a passive subscriber, not something the department calls and waits on (see §8 for the durability and backpressure contract).

The one place this concurrency genuinely needs synchronization, not just a bigger worker pool, is graph-linking (§5.3): two events landing at the same moment that both touch the same Entity node could race on creating or updating edges for that node. This is solved with per-entity locking or transactional graph writes around the link step specifically — it is not a reason to shard the Library by department, which would reintroduce the consistency problem §3.1 exists to avoid (and would actively work against the neural map's purpose, since cross-department links are exactly what should contend briefly on a shared Entity).

### 3.4 When this assumption should be revisited

A single Librarian should remain a single Worker until one of these becomes true:
- Trace volume from departments genuinely exceeds what a single classification/linking pipeline can process without becoming the system's bottleneck (observable via Library-specific traces — see §9). Note this is a *throughput* question, not a *count* question — Coding's many small per-file events and Research's fewer, heavier per-job events stress the pipeline differently (frequency vs. payload size), and whichever shape actually causes queue depth to grow should drive what gets optimized first, not an assumption that one department dominates.
- A new memory type emerges that requires fundamentally different handling logic (e.g., binary/media memory, which might need its own Cataloguer Worker rather than overloading the Librarian's classification logic).
- The neural map (§5) grows complex enough that maintaining it becomes a distinct, schedulable job (e.g., periodic graph consolidation/pruning) better modeled as a background Worker than as part of every event's processing path.

If any of these trigger, the correct move is to add a **Cataloguer Worker** (handles graph maintenance/consolidation as a background job) or a **Retrieval Worker** (handles complex cross-backend reads) — not to fragment the observation path itself, which would reintroduce the consistency problem §3.1 exists to avoid.

---

## 4. What the Library Observes — Trace Events, Threaded into Records

The Library does not define its own submission schema for departments to fill out. It reads the same structured trace events every component already emits via the constructor-injected TraceEmitter (vision Rev 5, Principle 9) — the event bus delivers these to the Log drawer and to the Library identically, as two independent subscribers to the same stream. The Library's job is to take that raw, per-event stream and thread it into something coherent enough to be useful as memory.

### 4.1 What a trace event already carries

Every trace event emitted by a component already includes, per the core's existing observability contract: an originating component identifier, a timestamp, a level (ERROR/WARN/INFO/DEBUG/TRACE), a structured payload (whatever the component chose to report), and — for components operating within a task — the task or job ID they're acting on. The Library adds nothing to this contract; it only reads it. If a department's events are too sparse for the Library to build a useful episodic record (e.g., a component emits only a bare "started" and "finished" with no payload), that is a gap in that department's trace instrumentation to fix at the source, not something the Library should compensate for by inventing content.

### 4.2 Episodic Identity and Concurrency

This is the rule that resolves how concurrent work threads into separate vs. shared history, and it has two parts:

- **Episodic identity is per-Task/Job, not per-event and not per-Worker.** Every trace event carries a task or job ID (per §4.1). All events sharing that ID — regardless of which stage or Worker emitted them — are threaded by the Library into **one** episodic record, ordered by timestamp. For example, Coding Task #47's Reader, Planner, and Writer stages each emit their own trace events, but because all three carry `task_id=47`, the Library threads them into a single episodic conversation for that task, with each stage's events as turns within it — not as three separate, disconnected histories.
- **Different tasks are different episodic records, full stop — even if they run concurrently, and even if they're in the same department.** A Writer Worker on Coding Task #47 and a Synthesis Worker on Research Job #12, running at the same wall-clock moment, produce two independent event streams with two different IDs. The Library threads each into its own record. There is no merging of unrelated task IDs into one history, and no fragmentation of one task ID into several — the task/job ID *is* the episodic boundary.

This means two Workers running concurrently never "collide" at the episodic level — each is its own thread, keyed by the ID it was already carrying for the core's own task-tracking purposes (§2 — the core's task state machine, not the Library, owns this ID). What concurrent Workers *can* legitimately collide on is the **graph**, not the episodic stream: if both task threads turn out to concern the same Entity node (e.g., both reference the same project), the Library's classification step links them via `relates_to` (§5.3) once each thread is processed — and that shared-Entity write is exactly the case §3.3 flags as needing per-entity locking. The histories stay separate; the graph is where they connect.

### 4.3 The internal record shape (after threading)

Once threaded, the Library's internal representation of a completed (or in-progress) episodic record carries:

| Field | Description |
|-------|--------------|
| `record_id` | Unique ID, generated by the Library. |
| `origin_department` | Read from the trace events' component identifiers (`coding`, `research`, `education`, `orchestrator`, ...) — the Library infers this, it is not declared to the Library by the department. |
| `origin_reference` | The task/job/conversation-turn ID the events were threaded on (§4.2) — this is the core's own ID, not one the Library invents. |
| `content` | The assembled narrative built from the threaded events' payloads — what happened, in what order, including intermediate states (a Debug Worker's rejected hypotheses, a Planner's discarded alternatives), not just the final outcome. This is the direct fix for the failure mode of only keeping final deliverables: nothing is discarded just because a stage didn't make it into the final output. |
| `memory_type` | The Library's classification (§5) — `episodic`, contributing to `semantic`/`procedural` distillation over time. There is no "suggested" type from a department to override, since the department was never asked. |
| `entities` | Extracted by the Library during classification (§5) from the threaded content — projects, files, people, models, domains referenced across the events. |
| `sensitivity` | Inferred from the originating component's own trace metadata and the core's existing data-classification signals, then checked against Owner policy (§7) — if a department's trace events don't already carry enough signal to classify sensitivity confidently, that is flagged for Owner review rather than guessed. |
| `timestamp` | Derived from the threaded events' own timestamps (first event = record start, last = completion), not from when the Library happened to process the batch — the Library may process in batches or with some lag, and that lag must never be confused with when the underlying work occurred. |

Because the Library is a passive observer, there is no "acknowledgement" round-trip with a department the way a write-request model would have — a department never waits on the Library, because it never called the Library in the first place. The Library processes the trace stream on its own schedule (§8), bounded only by how far behind real-time its queue is allowed to drift before that becomes an observability concern in its own right (§9).

---

## 5. Categorization: The Neural Map

This is the core design decision of this spec. Rather than treating memory as a flat set of records in separate siloed tables per department, the Library organizes everything into a single, traversable **graph** — the neural map — where every record is a node, and relationships between records (and between records and entities) are edges. This sits on top of the core's existing **graph memory** capability class (Neo4j/Memgraph/DuckDB-graph, per the Capability Surface), which the architecture already lists as a supported backend type — the Library is simply the first component to make full, central use of it.

### 5.1 Why a graph, not just tags or folders

A flat categorization scheme (folders, tags, department-scoped tables) can answer "show me everything from Coding" but struggles with the questions that make a personal AI system actually useful: "what do we know about this library that's relevant across the three different projects that use it?" or "has Research already looked into something that would help the model Education is about to train?" Those are traversal questions — they require walking from one node to related nodes regardless of which department originally wrote them. A graph is the natural structure for this; a set of department-scoped SQL tables is not.

### 5.2 Node types

| Node type | Examples | Typically produced by |
|---|---|---|
| **Event nodes** | A completed Coding Task, a finished Research Job, a Training Run, a single conversation turn | Every department, continuously |
| **Entity nodes** | A project, a file, a person, a domain/topic, a model, a library/package, a source/URL | Extracted from records' `entities` field, or inferred by the Librarian during classification |
| **Fact nodes** (semantic memory) | "Project X uses snake_case," "Library Y has a known CVE," "The Owner prefers terse commit messages" | Distilled by the Librarian from patterns across multiple Event nodes (§5.4) |
| **Workflow nodes** (procedural memory) | A learned multi-step process ("when a dependency upgrade breaks tests, check the changelog before reverting") | Written via a self-correction skill, through the Library, referencing the Event nodes it was derived from |

### 5.3 Edge types

| Edge | Meaning |
|---|---|
| `produced_by` | Event node → originating department/Manager |
| `concerns` | Event or Fact node → Entity node (this task concerned this project; this fact concerns this library) |
| `derived_from` | Fact or Workflow node → the Event node(s) it was distilled from (provenance for semantic/procedural memory — so the Library can always answer "why do we believe this") |
| `relates_to` | Generic association between two Entity nodes, or two Event nodes, when the Librarian's classification step detects a connection (e.g., two Research Jobs that both cite the same source; a Coding Task and a Research Job that both concern the same library) |
| `supersedes` | A newer Fact node that revises or replaces an older one (semantic memory updates rather than duplicates) |
| `referenced_in` | Connects raw source material (a document, a URL, an uploaded file) to the Event nodes that used it as input — distinct from `derived_from`, which is for distilled facts rather than raw inputs |

### 5.4 How facts get distilled (semantic memory generation)

The Librarian does not wait for an explicit instruction to create a Fact node. As part of its classification step (§3.2, step 2), when a new Event node's content overlaps significantly with an existing pattern across prior Event nodes concerning the same Entity, the Librarian proposes a Fact node candidate. Per the project's general stance on learning (vision Rev 5, Q13 — "the system does not learn autonomously"), **fact distillation is a Library function operating on explicit content matching, not an autonomous learning loop** — it is closer to deduplication-with-generalization than to inference. Anything requiring genuine inference across ambiguous evidence is left to a self-correction skill, which can read the Library's data and write back a Workflow or Fact node with its own reasoning attached as provenance, distinct from the Library's own mechanical distillation.

### 5.5 Memory panel as the graph, made browsable

The **Memory** sidebar panel (vision Rev 5, §8 sidebar list) is the Owner-facing rendering of this graph: backends plugged in, recent reads/writes, and a query interface, per its core definition — with the addition that the Library's specific contribution is making that query interface a graph browser, not just a backend-by-backend dump. The Owner can start at any Entity node (a project, a person, a topic) and traverse outward to see everything connected to it, regardless of which department originally wrote each piece.

---

## 6. What Departments Currently Assume That This Spec Changes

The Coding, Research, and Education specs were written describing "the Librarian" as a query-routing role embedded within each department's own pipeline description. This spec does not require changing those departments' behavior — they don't need to add any code to "talk to" the Library on the write side, since they were never going to be asked to. It does clarify and tighten the contract on both sides:

- **Coding §1, §5.1–5.3 (Codebase Index):** previously described as "stored in Qdrant and Postgres," with the Librarian "routing" queries to them. Under this spec, the Coding Manager does not know or care that the Index lives in Qdrant/Postgres, and does not need to explicitly tell the Library about file summaries, symbol index entries, or convention records — the Library builds the Index by observing Coding's own trace events as each stage runs (§4), the same events Coding already emits today for the Log drawer. The only thing Coding does explicitly is issue a `LibraryQuery` when it needs to *read* — e.g., its own memory pre-check stage. No behavior change to Coding's stages; the clarification is that backend selection and write-side bookkeeping are entirely the Library's job, invisible to Coding, not something Coding's stages need to call out to.
- **Research §3.1 (Tier 1 internal memory), §6.1 (memory pre-check):** the "memory hit score" and freshness check described there are now explicitly Library-provided capabilities — the Research Manager issues a `LibraryQuery`, and the Library returns results plus a hit score, using whatever combination of vector similarity and graph traversal it judges appropriate. The 0.85 default threshold remains Research's own configuration, applied to whatever score the Library returns. This read-side contract is unchanged from the original design; only the write side (how Research's own findings became queryable in the first place) is now observation-based rather than an explicit submission Research's spec would otherwise need to implement.
- **Education §6.4 (Memory Panel):** "training data retrieval" is a `LibraryQuery` read like any other department's. "Benchmark storage" no longer needs to be an explicit write Education's spec implements — benchmark results, once Education's own components emit them as trace events (which they need to do regardless, for the Log drawer), are picked up and threaded into episodic memory by the Library the same way any other department's completed work is. No change to what Education does internally, only to the fact that it no longer needs a separate "write to memory panel" step at all.
- **None of the three existing specs need amendment for this to be true on the write side** — if anything, this spec *removes* an implementation burden those specs might otherwise have needed (an explicit memory-write call), since the trace events those departments already emit are sufficient. The read side (`LibraryQuery`) remains exactly as those specs already assumed.

---

## 7. Privacy, Sensitivity, and Consent

The Library is the single chokepoint where personal/sensitive data enters persistent storage, which makes it the natural place to enforce the consent rules other specs already assume:

- A threaded episodic record (§4.3) that the Library's classification step infers as `sensitivity: personal` — based on the originating component's own trace metadata and the core's existing data-classification signals, not a tag a department declared — is checked against the Owner's retention policy (configured in Options) before being persisted. If policy requires explicit consent for a given content type and none has been granted, the Library stores the record in a short-lived holding area (not the permanent graph) and surfaces a consent prompt to the Owner via the Orchestrator, consistent with the Owner-as-only-conversational-party rule. If the Library's classifier cannot confidently infer sensitivity from what it observed, it defaults to the more cautious classification rather than guessing permissive.
- This generalizes the consent mechanism already specified in Research §9.1 (`allow_personal_memory` flag, `memory_scope` field) — rather than being Research-specific, it is the Library's standing policy, applied uniformly to what it observes from every department and to every read.
- **No exfiltration across departments without synthesis.** When one department's `LibraryQuery` would surface another department's raw personal-sensitivity content, the Library returns synthesized/redacted results by default rather than raw records, mirroring Research §9.1's existing rule that other departments receive findings, not raw personal data. The Owner, querying directly via the Memory panel, can see raw records.
- The Security Guard audits the Library's provenance chain on demand (consistent with its role in every other department spec) — the Library stores `derived_from` and `referenced_in` edges (§5.3) precisely so this audit is always possible without reconstruction.

---

## 8. Observation and Read Contracts

### 8.1 Observation (trace stream processing)

- **Async by definition, not by design choice.** There is no submission for a department to wait on — the Library subscribes to the trace stream and processes it on its own schedule. A department's pipeline is structurally incapable of stalling on Library internals, because it never calls the Library to begin with.
- **Durability guarantee.** Once a trace event has been delivered to the Library's subscription, it must not be lost before being threaded, classified, and persisted — a core/Library crash mid-processing must not silently drop events. This leans on the core's existing crash-recovery story via trace memory replay (vision Rev 5, Q14): since trace memory is already durably persisted by the core automatically, the Library can always recover its position by replaying from the last trace event it successfully processed, rather than needing its own separate durability mechanism for the inbound side.
- **Bounded lag, not silent drift.** The Library's processing queue is allowed to lag behind real-time under load (§3.3), but that lag itself must be observable — if the gap between "event emitted" and "event threaded into a record" grows unbounded, that is a Library health signal (§9), not something to hide.
- **No silent drops.** If classification or storage fails for a threaded record, this is logged at ERROR level (per the project's no-silent-failures principle) and surfaced to the Owner via the Orchestrator, the same as any other component's failure — the Library is not exempt from this rule just because it's infrastructure-adjacent.

### 8.2 Read (`LibraryQuery`)

| Field | Description |
|---|---|
| `query_text` or `query_entities` | Free-text query, a specific Entity node to start traversal from, or both. |
| `requesting_department` | Used for sensitivity/consent filtering (§7). |
| `memory_types` | Optional filter (episodic/semantic/procedural) — if omitted, the Library searches across all types relevant to the query. |
| `traversal_depth` | For entity-anchored queries, how many graph hops to include (default: 1 — direct connections only, to avoid runaway breadth). |
| `freshness_requirement` | Optional — for queries like Research's memory pre-check, where stale cache hits should be excluded. |

The Library returns matched records plus, for entity-anchored queries, the relevant subgraph — letting the requesting department (or the Owner via the Memory panel) see not just the answer but what it's connected to.

---

## 9. Observability

- The Library emits traces (via the constructor-injected TraceEmitter, same as every other component) for every batch of trace events it processes, every threading/classification decision made, and every graph edge created — this is what makes §3.4's "is one Librarian still enough" question answerable from real data rather than guesswork. It also emits its own subscription lag (§8.1) as a first-class metric, since that is the earliest warning sign of the Library falling behind the system it's documenting.
- The Library does not need its own separate logging mechanism — it follows the same Log drawer / TraceEmitter contract as everything else (vision Rev 5, Principle 9). Notably, the Library and the Log drawer are *siblings* here, not one built on the other: both are independent subscribers to the same trace stream, one rendering it transiently for the Owner to watch live, the other threading it into durable, traversable memory.

---

## 10. Suggested File/Module Layout

```
/backend
  /library
    librarian.py                # the single Worker — orchestrates subscribe, classify, store, link, retrieve
    trace_subscriber.py          # §4, §8.1 — subscribes to the event bus's trace stream, hands events to the threader
    threader.py                  # §4.2 — groups raw trace events into per-task/job episodic record candidates
    classifier.py                # §5 — assigns memory type, extracts entities, proposes Fact nodes
    graph_writer.py              # §5.2-5.3 — creates/updates nodes and edges via core's graph memory routing
    query_engine.py               # §8.2 — assembles cross-backend, cross-type query responses
    consent_gate.py               # §7 — sensitivity checks, holding area for unconsented personal data
    fact_distillation.py          # §5.4 — pattern matching across Event nodes to propose Fact nodes
    api.py                        # REST/event-bus endpoints — read-only; there is no write/submission endpoint
      # GET  /library/records/<id>
      # POST /library/query               (submit a LibraryQuery)
      # GET  /library/graph/<entity_id>   (subgraph around an entity, for the Memory panel browser)
      # GET  /library/consent-queue       (pending consent prompts for the Owner)
      # POST /library/consent-queue/<id>/decide
      # GET  /library/health               (subscription lag, queue depth — §8.1, §9)

/frontend
  /components/memory-panel/
    GraphBrowser.tsx              # §5.5 — the Memory panel's primary view, entity-anchored graph traversal
    BackendStatusList.tsx        # existing "backends plugged in" view, retained
    QueryBar.tsx                  # free-text + entity search, issues LibraryQuery
    RecentReadsWrites.tsx        # existing "recent reads/writes" view, retained — now populated from the Library's threaded records rather than raw writes
    ConsentPromptModal.tsx        # §7 — surfaces pending consent decisions to the Owner
```

---

## 11. Open Questions for Round Table

1. **Graph backend choice for v1.** The core's Capability Surface lists Neo4j, Memgraph, and DuckDB-graph as examples without prescribing one. Given the "fast browsing, not live scraping" lesson already learned in the Models Panel spec, and that the neural map will be queried interactively from the Memory panel, which graph backend should ship as the v1 default? DuckDB's graph extension keeps the project's general bias toward fewer moving parts (similar reasoning to the Models Panel spec's SQLite recommendation), but Neo4j/Memgraph have more mature traversal query languages (Cypher) that might matter once the graph is large.

2. **Fact distillation thresholds.** §5.4 proposes Fact node candidates based on "significant content overlap" across Event nodes concerning the same Entity. This needs a concrete similarity threshold and a decision on whether distillation candidates are auto-promoted to Fact nodes or queued for Owner confirmation (similar to Research's trust-signal queue in §8.2 of the Research spec). Auto-promotion risks the graph accumulating confidently-wrong "facts"; manual confirmation risks the Owner being asked to review more than they want to.

3. **Cross-department `relates_to` edge creation cost.** Detecting that "this Coding Task and that Research Job both concern the same library" requires comparing newly-threaded records against a potentially large existing graph. Is this comparison done as part of processing each threaded record (every new record checked against everything), which could become the bottleneck flagged in §3.4, or on a scheduled background pass? A scheduled pass means the graph is sometimes stale; per-record comparison means processing latency grows with graph size.

4. **Memory panel performance at scale.** Per the Models Panel spec's own lesson (browsing should feel instant, not live-query), should the Memory panel's GraphBrowser read from a denormalized, UI-optimized snapshot of the graph (refreshed periodically) rather than querying the live graph backend on every click? This mirrors the Models Panel's local-cache-vs-live-scrape decision, applied to graph traversal instead of HTML scraping.

5. **Retention and pruning policy.** The vision doc doesn't currently specify whether episodic memory grows forever or is pruned/archived. Does the Library need a retention policy (e.g., raw Event nodes older than N months get summarized into a Fact node and the raw node is archived/deleted), or is unlimited local storage an acceptable v1 assumption given the project's single-user, local-first scope?

6. **Single Librarian validation.** §3 argues for one Worker on structural grounds, but this is a prediction, not a proven fact. What concrete metric (trace-subscription lag? classification latency? graph query p95?) should trigger the Round Table revisiting §3.4's split conditions, and where should that metric be surfaced — a dedicated Library health indicator in the Workers panel?

---

## 12. Implementation Order (Suggested)

1. **trace_subscriber.py + threader.py** — subscription and per-task/job threading only, no classification yet. Validate that real Coding Task trace events get correctly threaded into single coherent episodic candidates (§4.2) before any graph logic exists.
2. **classifier.py (memory-type assignment only)** — episodic/semantic/procedural classification, no entity extraction or Fact distillation yet. Validate against real Coding Task completions (the most mature existing department) before generalizing.
3. **graph_writer.py (Event and Entity nodes only)** — `produced_by` and `concerns` edges only. Validate the graph is queryable and the Memory panel can render a basic entity-anchored view before adding `relates_to` or `derived_from`.
4. **query_engine.py (single-backend, single-type queries)** — answer Research's existing memory pre-check use case first, since it's the most concretely specified existing consumer (§3.1 of the Research spec).
5. **GraphBrowser.tsx** — wire the Memory panel to real data once steps 1–4 are stable, replacing whatever placeholder "backends plugged in" view currently exists.
6. **consent_gate.py** — add before any department's trace events could plausibly carry `sensitivity: personal` content in production use, generalizing Research's existing `allow_personal_memory` pattern.
7. **fact_distillation.py** — add once enough Event node volume exists for pattern-matching to be meaningful; premature with a small graph.
8. **relates_to edge creation (cross-department linking)** — add once at least two departments (Coding, Research) are both being observed by the Library in production, so cross-department links have real data to connect.
9. **Scheduled graph maintenance / consolidation** — add only if Open Question 3 resolves toward a background-pass approach rather than per-record comparison.
10. **Retention/pruning** — add once Open Question 5 is resolved and there's enough real data volume to make a retention policy meaningful to test.

---

*End of document.*
