# SovereignAI — Orchestrator: Implementation Specification

**Document Type:** Deep Implementation Spec
**Author:** Angus / Claude (design pass)
**Audience:** GLM (implementing agent) + Round Table review
**Status:** Draft v1 — ready for Round Table review
**Date:** 2026-06-29
**Depends on:** `SovereignAI_Architecture_Decisions.md`, `project-vision-Rev5.md`

---

## 0. Purpose

This document specifies the **Orchestrator** — the CEO of SovereignAI. The Orchestrator is not a department. It has no Manager, no Workers, and produces no deliverables of its own. Its entire job is the boundary between the Owner and every department:

- It is the **only** thing the Owner ever talks to. Departments never surface messages, explanations, or results directly to the Owner (per vision Rev 5, §8).
- It is the **only** thing that talks to department Managers on the Owner's behalf. It does not do coding, research, training, or any domain work itself — it has no workers to delegate to within itself, because it delegates everything, to entire departments.
- It translates: vague human language in one direction, structured department-native requests in the other. And back again with the result.

If a department is a company department with a Manager and Workers, the Orchestrator is the CEO's desk — one person, no direct reports of their own, whose whole function is turning the Owner's intent into instructions departments can act on, and turning department output back into something a human wants to read.

---

## 1. Placement and Boundaries

| Entity | Relationship to the Orchestrator |
|--------|-----------------------------------|
| **Owner (User)** | The only party the Orchestrator converses with. All chat, all approvals-in-conversation, all clarifying questions flow through this single channel. |
| **Department Managers** (Coding Manager, Research Manager, Education Manager, Communication Manager, Security Guard, Operations Manager, etc.) | The only parties the Orchestrator delegates to. The Orchestrator never addresses a Worker, a Reader, a Planner — those are internal to a department and invisible to the Orchestrator. It hands a structured request to a Manager and receives a structured deliverable back. |
| **Core (Task state machine, Event bus, Routing engine)** | The Orchestrator is a consumer of core services, not part of the core itself. It submits tasks via the Capability API, subscribes to task state changes and traces via the event bus, and reads routing/capability data from the capability graph. It does not implement task state, routing, or the event bus — those are sacred-core (vision Rev 5, Core Scope §v1, items 5 and 8). |
| **UIs** | The Orchestrator panel is the chat surface. Other panels (Workers, Tasks, Skills, Memory, Models, Adapters, Hardware, Options) show data, not conversation. Multiple Orchestrator windows may be open at once, each a separate view of the same Orchestrator state (vision Rev 5, §8). |

**What the Orchestrator is not:**
- It is not a department, so it has no Company Metaphor Placement table of Manager/Workers in the way Coding, Research, and Education do. There is exactly one Orchestrator, always running, never task-spawned.
- It does not own the Task state machine (RECEIVED → QUEUED → EXECUTING → COMPLETE/FAILED) — that lives in the core. The Orchestrator submits tasks into it and watches it, but does not define or mutate its states directly outside the documented API.
- It does not perform domain work. It has no terminal skill, no retrieval skill, no training pipeline. If every department were deleted, the Orchestrator would still start and would simply have nothing to route to — it would tell the Owner so, plainly, rather than attempting the work itself.
- It is not the Security Guard, the Librarian, or any other cross-cutting role referenced in department specs. Those are addressed by department Managers directly when needed (e.g., the Coding Manager invoking the Security Guard), not proxied through the Orchestrator.

---

## 2. What the Orchestrator Produces

The Orchestrator produces no deliverables in the department sense — no code, no research dossiers, no models. It produces exactly two kinds of artifact, both ephemeral to a single exchange:

| Artifact | Description |
|----------|--------------|
| **Department Request** | A structured, department-native request built from the Owner's natural-language message: a `CodingTask`, a `ResearchBrief`, a `TrainingJobSpec`, etc. Shape is owned by the receiving department's spec — the Orchestrator's job is producing a request that validates against that department's schema, not defining the schema itself. |
| **Owner Response** | A plain-language reply synthesized from one or more department deliverables, task state events, and/or the Orchestrator's own routing decisions. This is the only thing the Owner ever sees in the chat surface. |

Everything else — Coding Deliverables, Research Deliverables, Expert Models — belongs to the producing department and is merely *referenced* by the Orchestrator when it tells the Owner about it.

---

## 3. Core Responsibilities

### 3.1 Intent Translation (Owner → Department)

The Owner speaks in natural, often underspecified language: "fix the login bug," "find out about X," "make me a Python coding model." The Orchestrator's first job is converting this into a structured request a department can act on.

This involves:
- **Department selection.** Deciding which department(s) the request belongs to. A request may span multiple departments (e.g., "write a blog post about how we fixed the login bug" touches Coding for the technical detail and Communication for the writing).
- **Schema filling.** Populating the receiving department's request schema (its Task/Brief/Spec shape, as defined in that department's own spec) from the Owner's message, including fields the Owner didn't explicitly state but that are inferable from context (e.g., inferring the active project from recent conversation).
- **Gap detection.** Identifying fields the schema requires that cannot be reasonably inferred, and asking the Owner a clarifying question rather than guessing — but only when proceeding would clearly go in the wrong direction. The Orchestrator should prefer making a reasonable assumption and stating it, over blocking on a question, consistent with how the Owner is treated as a capable adult who can correct a wrong assumption faster than they can answer an unnecessary question.
- **Scope discipline.** Not inventing requirements the Owner didn't ask for. A request to "fix the login bug" is a Bug Fix deliverable, not an invitation to refactor the whole auth module.

### 3.2 Routing

The Orchestrator decides which department Manager(s) receive a request, and in what order, when a request spans more than one department.

- **Single-department requests** route directly: the Orchestrator builds the request, submits it to that department's intake endpoint, and waits.
- **Multi-department requests** are sequenced according to the dependency the departments themselves declare in their specs (e.g., Coding issuing a Research Brief before Stage 2, per the Coding spec's Stage 0 — but note that in that case the *Coding Manager* issues the brief directly to Research, not the Orchestrator; the Orchestrator's role is only to recognize, at intake, when the Owner's original request needs Coding at all and to route there. The Orchestrator does not re-implement inter-department handoffs that the departments already own between themselves).
- **Genuinely orchestrator-initiated multi-department requests** — where the Owner's request itself spans departments with no existing department-to-department contract (e.g., "build the feature and then announce it") — are sequenced by the Orchestrator: it routes to Coding first, waits for the Coding Deliverable, then routes a Communication request that includes the Coding Deliverable as context.
- **Important distinction:** the Orchestrator routes *whole requests* to department Managers. It does not route at Worker granularity — it has no visibility into and no opinion about whether a department uses a Reader Worker or a Planner Worker to satisfy the request. That decomposition is entirely internal to the department.
- Per Q4's reframing in the vision doc: the core's routing engine is not what's described here. The core's routing engine matches *capability requests* to *components* at a lower, more general level (vision Rev 5, Core Scope item 5). The Orchestrator's routing described in this section is a higher-level, conversational decision — which department(s) should handle this human request — built on top of, but distinct from, the core's capability routing.

### 3.3 Concurrency and Queuing

- Concurrent Owner submissions from different UIs (web UI and phone app at the same instant) are queued by the Orchestrator in receive order (vision Rev 5, §6). The Orchestrator does not reorder by perceived priority unless the Owner explicitly asks it to deprioritize or expedite something.
- A long-running task started from one UI is visible and controllable from any other UI, because all UIs are views onto the same Orchestrator/core state — the Orchestrator does not maintain per-UI session state for task tracking.
- Multiple Orchestrator chat windows are simply multiple views of the same conversation/task state; the Orchestrator does not treat them as separate conversational contexts requiring separate routing decisions.

### 3.4 Synthesis (Department → Owner)

When a department Manager returns a deliverable, or the core reports a task state change, the Orchestrator converts that into something a human wants to read.

- **Plain-language summary**, not a raw dump of the deliverable's structured fields. The Owner can always drill into the underlying deliverable via the relevant panel (e.g., open the DiffViewer in the Coding sub-panel) — the chat response points them there rather than reproducing it inline.
- **Surfacing system state in plain language** without requiring the Owner to open the Log drawer (vision Rev 5, Observability Criterion 27). If a department degrades gracefully (e.g., Coding produces a deliverable but couldn't commit because no git skill is registered), the Orchestrator says so plainly in the response, not buried in a trace the Owner has to go find.
- **No silent failures.** If a department request fails or a dependency is unavailable, the Orchestrator tells the Owner what failed and why, in the same response — it never simply doesn't respond, and never reports success when a sub-step actually degraded (vision Rev 5, Observability Criterion 28).
- **Pass-through of structured input requests.** When a worker emits a `user_input_request` event (boolean/text/choice/file/multi_choice — vision Rev 5, §8) the Orchestrator is the one that renders this to the Owner in the chat surface and routes the Owner's answer back to the originating department. The Orchestrator does not alter or reinterpret the schema of these requests — it is a faithful relay with a conversational skin.

### 3.5 Conversation Memory and Context

- The Orchestrator maintains the working conversational context for the Owner's current session(s) — what's been discussed, what's in flight, what was recently delivered — so that follow-up messages ("now add tests for that") resolve correctly without the Owner re-stating context.
- This conversational context is distinct from the core's episodic/trace memory (owned by memory backends per the core's persistence model) and distinct from any department's own task registry. The Orchestrator may read from those stores to answer a question ("what did Coding do last Tuesday?") but does not own them.

---

## 4. What the Orchestrator Explicitly Does Not Do

To keep this document from becoming scope creep into the sacred core or into department territory, the following are out of scope for the Orchestrator and called out here so implementers don't accidentally build them into it:

- **Task state machine.** Lives in the core. The Orchestrator submits and observes; it does not define RECEIVED/QUEUED/EXECUTING/COMPLETE/FAILED transitions.
- **Capability routing at the component level** (which adapter, which skill). That's the core's routing engine, operating on capability manifests. The Orchestrator's routing is department-level and conversational, as described in §3.2.
- **Department-internal decomposition.** Stage breakdown, Worker assignment, and intra-department handoffs (e.g., Coding Manager → Research Manager for a Research Brief) are owned entirely by the departments involved. The Orchestrator is not a party to these unless the Owner's original request is what spans the departments (see §3.2's distinction).
- **Approval gating on domain actions.** Whether a git push needs Owner sign-off, or a training run needs explicit approval, is execution policy owned by the relevant department (and ultimately the Security Guard / Options panel approval thresholds). The Orchestrator surfaces these approval requests to the Owner via the input-request relay in §3.4, but does not define the policy of when approval is required.
- **Hardware monitoring.** CPU/GPU/RAM/VRAM, sandbox status, and the download queue are already a first-class sidebar panel (Hardware) reading live system/core state directly. This does not need a department, a Manager, or Workers — it's a panel over data the core/adapters already expose, with no task lifecycle, no deliverable, and no decomposition into stages. No Orchestrator involvement beyond mentioning current hardware state in a synthesized response if the Owner asks ("how much VRAM do I have free right now?").

---

## 5. The Department Request / Response Contract

The Orchestrator's relationship with every department is symmetric, regardless of which department it is. This section defines the shape of that contract so any new department (Communication, Security, Operations, or future ones) can be added without the Orchestrator needing department-specific code paths beyond schema knowledge.

### 5.1 Outbound: Department Request

Every Department Request the Orchestrator builds carries:

| Field | Description |
|-------|--------------|
| `request_id` | Unique ID, used to correlate the eventual deliverable and any task-state events back to this conversational exchange. |
| `department` | Target department identifier (`coding`, `research`, `education`, `communication`, ...). |
| `payload` | The department-native structured request (`CodingTask`, `ResearchBrief`, `TrainingJobSpec`, etc.) — schema owned by the receiving department, validated by the Orchestrator before submission using that department's published schema. |
| `origin_context` | Minimal conversational context the department may need but shouldn't have to ask for again (e.g., the active project, prior turns referenced by "that" or "it"). |
| `owner_priority` | Optional — set only if the Owner explicitly asked to expedite or deprioritize. Absent by default; departments queue in receive order otherwise. |

If the Orchestrator cannot fully populate a required field and cannot reasonably infer it, it does not submit a partially-valid request — it asks the Owner first (§3.1).

### 5.2 Inbound: Deliverable / State Event

The Orchestrator subscribes to two kinds of inbound signal per outstanding request:

- **Task state events** from the core's event bus (RECEIVED/QUEUED/EXECUTING/COMPLETE/FAILED, plus any intermediate progress events a department chooses to emit) — used to keep the Owner informed on long-running work without polling.
- **The final deliverable**, returned by the department Manager once complete — structure owned by the department, read by the Orchestrator only to extract what's needed for synthesis (§3.4), never re-serialized or stored as the Orchestrator's own record of truth (the department's own registry, e.g. the Coding Task registry, remains canonical).

### 5.3 Degradation Contract

Every department is expected (per each department's own spec) to degrade gracefully and report what it could not do, rather than fail silently or pretend success. The Orchestrator's job on receiving a degraded deliverable is purely one of presentation (§3.4) — it does not retry, does not attempt the missing step itself, and does not paper over the gap. It tells the Owner.

---

## 6. UI Behavior

- The **Orchestrator panel is the chat surface** — the only panel in the 9-section sidebar where conversation happens (vision Rev 5, §8). Every other panel shows data about departments, tasks, skills, memory, models, adapters, or hardware — never a conversational thread.
- **Live view of routing decisions.** The Orchestrator panel surfaces, inline or in an expandable trace alongside each response, which department(s) a request was routed to — not as raw logs (that's the Log drawer's job) but as a light, human-readable trace ("Routed to Coding Department" / "Routed to Coding, then Communication"). This satisfies the chat surface also being "the live view of routing decisions" called out in vision Rev 5, §8, without duplicating the Log drawer's role.
- **Structured input requests** (§3.4) render as inline interactive elements in the chat (buttons for boolean/choice, a text field for text, a file picker for file, checkboxes for multi_choice) rather than as plain text the Owner has to parse and answer in prose.
- **Multiple windows.** Each open Orchestrator window subscribes independently to the same underlying conversation/task state; sending a message from one window updates all open windows showing that conversation.
- **No conversational content in other panels.** If the Owner wants to see the actual code diff, research dossier, or training report, the Orchestrator's response in the chat links to or names the relevant panel rather than reproducing the deliverable's full content inline.

---

## 7. Suggested File/Module Layout

```
/backend
  /orchestrator
    intent_translator.py       # §3.1 — natural language → Department Request schema filling
    router.py                  # §3.2 — department selection + sequencing for multi-department asks
    request_builder.py         # §5.1 — validates and constructs the Department Request envelope
    synthesizer.py              # §3.4 — deliverable/state event → plain-language Owner Response
    input_request_relay.py     # §3.4 — relays worker user_input_request events to/from the Owner
    conversation_context.py    # §3.5 — working conversational state per Owner session
    department_registry.py     # known departments + their published request/response schemas
    api.py                      # REST/WebSocket endpoints
      # POST /orchestrator/message        (Owner sends a chat message)
      # GET  /orchestrator/conversation    (current conversation state, for new UI windows)
      # POST /orchestrator/input-response  (Owner answers a structured input request)
      # GET  /orchestrator/routing-trace/<request_id>  (light routing trace for a given exchange)

/frontend
  /components/orchestrator/
    ChatSurface.tsx             # the conversational UI — the only chat surface in the app
    RoutingTrace.tsx            # inline "Routed to X" indicator per response
    InputRequestRenderer.tsx    # renders boolean/text/choice/file/multi_choice inline
    MultiWindowSync.tsx         # keeps multiple open Orchestrator windows in sync
```

---

## 8. Open Questions for Round Table

1. **Schema discovery.** How does the Orchestrator learn each department's Request/Response schema (§5)? Options: each department publishes its schema in its capability manifest (consistent with the core's manifest-driven discovery pattern used for adapters/skills); or department schemas are hand-registered in `department_registry.py` as departments are built. Manifest-driven is more consistent with the rest of the architecture's "no hard-coded individual component names" rule, but department schemas are richer than a typical skill manifest — is the existing manifest format sufficient, or does it need a department-specific extension?

2. **Multi-department sequencing ownership.** §3.2 draws a line between department-to-department handoffs the departments own themselves (e.g., Coding calling Research directly) versus Orchestrator-initiated sequencing for requests with no existing department contract. Is this the right line, or should the Orchestrator always be the one sequencing cross-department work, with departments never calling each other directly? The Coding and Education specs already assume direct Manager-to-Manager calls (Coding → Research, Education → Research) — changing this would require amending those specs.

3. **Clarifying-question budget.** §3.1 says the Orchestrator should prefer inferring and stating an assumption over asking a clarifying question, but department specs (e.g., Coding's Stage 0) describe the Coding Manager documenting assumptions itself when Research is skipped. Should the Orchestrator ever ask a clarifying question on the department's behalf (before the request is even built), or should under-specified requests always be passed through and left to the receiving department to flag? Current draft assumes the Orchestrator only blocks on genuinely required-but-unfillable schema fields; everything else is the department's problem to flag.

4. **Routing trace granularity.** §6 proposes a light "Routed to X" trace distinct from the Log drawer. Is this duplicative of the Log drawer's component-filter view, or does it add enough value (immediate, in-chat, no drawer-opening required) to justify the extra UI surface?

5. **Conversation context retention policy.** §3.5's working conversational context needs a retention/eviction policy — how far back can "that" or "it" resolve before the Orchestrator should ask the Owner to clarify rather than guess? This likely depends on memory backend capacity and is worth deciding alongside the core's episodic memory persistence story (vision Rev 5, Q14), not in isolation here.

6. **Priority and preemption.** `owner_priority` (§5.1) is sketched as optional and explicit-only. Should the Orchestrator ever infer urgency from phrasing ("urgently," "ASAP") without the Owner setting an explicit flag, or is inferred urgency too risky (departments might preempt other in-flight work incorrectly)? Current draft treats it as Owner-set only.

---

## 9. Implementation Order (Suggested)

1. **request_builder.py + department_registry.py** — minimal schema validation against one already-built department (Coding) before anything conversational exists.
2. **intent_translator.py (simple case)** — single-department, fully-specified requests only ("fix the off-by-one error on line 47" — no ambiguity). Validate that a well-formed request reaches Coding correctly before handling ambiguity.
3. **synthesizer.py (simple case)** — plain-language response from a single completed Coding Deliverable. Validate the Owner actually finds the response useful before adding nuance (degradation reporting, multi-deliverable synthesis).
4. **Gap detection + clarifying questions** — extend intent_translator.py to handle under-specified requests, per the resolution of Open Question 3.
5. **Degradation + no-silent-failure reporting** — extend synthesizer.py to surface partial failures plainly, validated against a deliberately-degraded Coding Deliverable (e.g., no git skill registered).
6. **input_request_relay.py** — wire up structured input requests once a department (Coding, during a terminal command requiring confirmation) actually emits one.
7. **router.py multi-department sequencing** — add once a second department (Research) is operational, validated against the Coding→Research pattern that already exists in the Coding spec.
8. **conversation_context.py** — add once single-turn flows are solid; needed for natural follow-up ("now add tests for that").
9. **RoutingTrace.tsx + Log drawer parity check** — add the light in-chat trace once Open Question 4 is resolved.
10. **Remaining departments (Education, Communication, Security, Operations)** — wire each into department_registry.py as they come online; no Orchestrator code changes should be required beyond schema registration, validating Core Principle 2 (everything pluggable) for the Orchestrator's own department-facing side.

---

*End of document.*
