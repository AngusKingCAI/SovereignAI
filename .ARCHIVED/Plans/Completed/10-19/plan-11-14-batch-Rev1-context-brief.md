# Round Table Brief — SovereignAI Plans 11–14 Batch

**Brief type**: Batch context brief covering Plans 11, 12, 13, 14.
**Batch scope**: Memory infrastructure, versioning, testing, and learning — the "deep infrastructure" layer that makes SovereignAI self-improving.
**Scaffold**: Per AI_HANDOFF.md 3-part scaffold.
**Previous batch**: Plans 6–9 (Web UI stack) + Scan 10.

---

## Part 1 — Roles/Rules

- Your job is to find issues, not rewrite the plan.
- Assume this plan will fail — identify how.
- Each issue must include a concrete failure scenario.
- End your response with `**Panelist**: <your name/model>`.
- Anonymous responses will be flagged but still adjudicated; named responses are preferred for accountability.

---

## Part 2 — Context

### What is being reviewed

Plans 11–14 build the deep infrastructure layer on top of the Web UI (Plans 6–9) and core components (Plans 1–4). This batch addresses the remaining open questions from the vision (Q3, Q8, Q9, Q13, Q14) and implements the deferred items from Plans 1–4.

### Cross-plan dependency map

```
Plan 11 (Librarian + Memory Backends)
  │─> Plan 12 (Versioning + Capability Negotiation)
  │     │─> Plan 14 (Education Department + Teacher Worker)
  │           │─> Plan 15 (Scan 15)
  │
Plan 13 (Testing Infrastructure)
  │─> Plan 14 (Learning loop needs tests for self-correction)
```

- Plan 11 MUST complete before Plan 12 — versioning needs memory to store version history.
- Plan 12 MUST complete before Plan 14 — the Teacher worker needs version negotiation to update models safely.
- Plan 13 is independent but feeds into Plan 14's test requirements.

### Plan scope summary

| Plan | Scope | New Files | Runtime Deps Added |
|------|-------|-----------|-------------------|
| **11** | Pluggable memory backends (SQLite episodic, JSON procedural, in-memory working), memory router, crash recovery | `sovereignai/librarian/`, `sovereignai/memory/`, `tests/test_librarian.py`, `tests/test_memory_backends.py` | None (stdlib `sqlite3`, `json`) |
| **12** | Semantic version parser, capability negotiation, dependency graph validation, compatibility matrix | `sovereignai/versioning/`, `tests/test_versioning.py` | None |
| **13** | Conformance test suites, contract test framework, property-based test harness, coverage baseline | `tests/conformance/`, `tests/contracts/`, `tests/property/` | `hypothesis` (dev only) |
| **14** | Education department, Teacher worker (QLoRA model fine-tuning), self-correction skill, retrospective trace analysis | `workers/education/`, `skills/official/self_correction/`, `tests/test_teacher_worker.py` | `peft`, `transformers`, `torch` (optional, graceful degradation) |

### Key dependencies

- Plan 11 builds on: TraceEmitter (Plan 1), EventBus (Plan 1), TaskStateMachine (Plan 3), CapabilityGraph (Plan 2).
- Plan 12 builds on: CapabilityGraph (Plan 2), ManifestParser (Plan 2), Memory backends (Plan 11).
- Plan 13 builds on: All core components (Plans 1–4), all UI components (Plans 6–9), all memory components (Plan 11).
- Plan 14 builds on: Memory backends (Plan 11), Versioning (Plan 12), MessageDispatcher (Plan 7), Ollama adapter (Plan 7).

### Author's reasoning (attack this — don't ratify the conclusion)

**My reasoning for pluggable memory from day one (Plan 11):** The vision (P3) says "Memory is modular. The core does not have a single memory system — it has a memory router that delegates to backends." Building a single SQLite memory store and refactoring later violates P3. The memory router is the architectural piece that matters; the backends are interchangeable. We implement three backends (SQLite for episodic, JSON for procedural, in-memory for working) to prove the plugin architecture works, but the router is the deliverable.

**My reasoning for hybrid versioning (Plan 12):** Core components must be strictly compatible — an incompatible core version is a broken system. But plugins (skills, adapters) should be lenient — an incompatible skill is simply not loaded, with a warning. This is how VS Code and Chrome extensions work. The user sees "Skill X disabled — requires CapabilityAPI >= 2.0" instead of a hard crash.

**My reasoning for conformance tests in both places (Plan 13):** Third-party developers need the conformance suite to validate their adapters/skills. If it's only in the core repo, they can't run it. If it's only per-component, the core can't enforce standards. Both locations: `tests/conformance/` in core for comprehensive suites, and a `conformance_test.py` template in each component directory.

**My reasoning for the Education department (Plan 14):** The user specified that learning should not be a built-in core feature but a worker in a department. The "Education" department houses the "Teacher" worker, which performs model improvement tasks (QLoRA fine-tuning, dataset curation, evaluation). This matches the vision's "learning loop is a skill, not a core capability" while giving it organizational structure. The Teacher worker is a first-class worker, not a special case.

**My reasoning for Windows-only (all plans):** The vision explicitly states v1 targets Windows only. Cross-platform (macOS, Linux) is deferred to a future batch. All hardware detection, packaging, and system calls assume Windows.

### Named open questions for the reviewer

1. **Memory backend lifecycle:** Who owns the SQLite database file? The core? The user? If the user deletes `~/.sovereignai/memory.db`, does the system recreate it or fail? What happens to procedural memory (JSON files) if the user edits them by hand?

2. **Versioning granularity:** Do we version individual capabilities or entire components? If a skill adds a new capability in v1.1, is the entire skill v1.1 or just that capability? The plan versions components, but capability-level granularity might be needed.

3. **Teacher worker dependencies:** QLoRA requires `peft`, `transformers`, `torch`, `bitsandbytes`, `accelerate` — ~2GB of dependencies. If the user doesn't have a GPU, the Teacher worker is useless. Should it be an optional install (`pip install sovereignai[education]`) or always included with graceful degradation?

4. **Self-correction skill vs. Teacher worker:** The self-correction skill analyzes traces and updates procedural memory. The Teacher worker fine-tunes models. Are these the same thing or different? The plan treats them as separate: self-correction is a skill (lightweight, runs frequently), Teacher is a worker (heavyweight, runs on demand).

5. **Crash recovery scope:** Plan 11 implements "replay last incomplete trace from trace memory, prompt user to resume or discard." Does this require UI changes (a "resume task?" dialog), or is it automatic? The plan says "prompt user" — which implies UI involvement, but Plan 11 is a core plan, not a UI plan.

### Architect's confidence by plan

- **Plan 11: 85% confident** — SQLite + JSON + in-memory are well-understood. Risk: memory router scatter-gather complexity.
- **Plan 12: 75% confident** — Versioning is straightforward. Risk: capability-level granularity vs. component-level.
- **Plan 13: 80% confident** — Testing infrastructure is standard. Risk: property-based tests require invariants that may not be documented.
- **Plan 14: 60% confident** — Education department is the most uncertain. Risk: QLoRA dependencies, GPU requirements, model lifecycle management.

### Vision principle compliance

| Plan | Principles Satisfied | Notes |
|------|---------------------|-------|
| 11 | P3 (memory is modular), P9 (no silent data loss), Q14 (persistence) | Pluggable backends prove modularity |
| 12 | P2 (pluggable), P8 (contracts), Q8 (versioning) | Hybrid strict/lenient matches real-world plugin systems |
| 13 | P9 (strong/robust), Q9 (test strategy) | Conformance + contract + property tests cover all three test types |
| 14 | P3 (memory is modular), P13 (learning), Q13 (improvement) | Education department makes learning a first-class organizational concept |

---

## Part 3 — Answer Format

Respond with:
1. **Issues found** (CRITICAL / HIGH / MEDIUM / LOW) — each with a concrete failure scenario.
2. **Other concerns** — anything not covered above.
3. **Clean pass** or **No issues found** — explicitly state if you find nothing.

End with: `**Panelist**: <your name/model>`
