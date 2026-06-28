# Round Table Brief — Project Vision Rev 2 Clean-Pass Check

**To**: 6-AI Round Table (Claude, Kimi, DeepSeek, Gemini, ChatGPT, sixth member)
**From**: Prompt Creator (GLM)
**Date**: 2026-06-27
**Subject**: Clean-pass check on amended vision (Rev 2)
**Attached**: `project-vision-Rev2.md` (read in full before responding)
**Prior context**: Round table Rev 1 review (4 responses received). Rev 2 incorporates panel findings + 13 user architecture decisions.

---

## Part 1: Your Role and Rules

**Your job is to determine whether Rev 2 has a clean pass.** This is not a fresh review — Rev 1 already surfaced the issues. Rev 2 is the amended vision responding to those issues. You are checking whether the amendments actually resolve the problems, and whether they introduce new ones.

**Adversarial framing**: Assume Rev 2 has at least one unresolved issue or one new issue introduced by the amendments. Find it. The author wants you to attack the amendments, not ratify them.

**Proof requirement**: Every issue you raise MUST include (a) a concrete failure scenario, (b) evidence from the Rev 2 document (quote the relevant principle or criterion), and (c) a severity rating per the rubric below. Issues without failure scenarios will be discarded.

**What this is NOT**:
- NOT a re-litigation of resolved questions. Q5, Q6, Q7, Q10, Q11, Q12, Q15, Q16, Q17, Q18 are resolved. Do not re-raise them. If you believe a resolution is wrong, you may flag it as a HIGH issue with a concrete failure scenario, but do not re-debate the question itself.
- NOT a fresh architecture design. The architecture direction is set (Python now, Rust-migratable later; lean orchestrator; workers compose skills; Security Guard worker; 9-section UI; cloud relay). Engage with the new open questions (Q19–Q26), but do not propose alternative architectures.
- NOT a style review. Formatting, tone, and word choice are out of scope.
- NOT a popularity contest. "No issues found" is a valid response.

**Severity rubric** (same as Rev 1 review):
- **CRITICAL**: A principle is contradictory, internally inconsistent, or would cause data loss / security vulnerability / irreversible system damage if implemented as written.
- **HIGH**: A principle is underspecified in a way that would cause a build failure, test failure, or Devin STOP condition when Plan 1 (Architecture Decision Plan) is drafted.
- **MEDIUM**: A principle is sound but underspecified — degraded functionality, poor UX, or technical debt likely if not clarified before Plan 1.
- **LOW**: Minor clarification, naming preference, or speculative future concern.

---

## Part 2: Context

### What changed in Rev 2

Rev 2 incorporates findings from 4 round table responses to Rev 1, plus 13 architecture decisions made by the user during a follow-up clarification session. The major changes:

**Principles**:
- P8 (Decentralised by design) — **dropped** as redundant with P2 + P3
- P7 (Strong, robust, modular, simple core) — **reframed** as "Modular and flexible core" — modularity and flexibility prioritised over simplicity. LOC budget becomes a guideline, not a gate. Hard gates: fault isolation, independence, acyclic deps, constructor arg cap of 7.
- P9 (UIs are core) — **reframed** as OS shell with 9 fixed sidebar sections (Orchestrator / Workers / Tasks / Skills / Memory / Models / Adapters / Hardware / Options) + Log drawer. Chat lives in Orchestrator panel only. User only talks to orchestrator. Workers never surface messages directly. Capability-class-driven panels (not individual-component-driven).
- P6 (One user, one system) — **clarified**: cloud-relayed remote UIs now; multi-machine core designed-for-future (not built in v1).
- P10 (Observability by default) — **added**. TraceEmitter + Log drawer.
- P11 (Security via reasoning) — **added**. Security Guard worker reviews external components. Default-deny for external; user/orchestrator-authored trusted by default.
- P12 (Dependency injection, no globals) — **added**. DI for all components. No globals. No deferred violations. Constructor arg cap of 7. Composition root pattern.
- P13 (Plain-English docstrings) — **added**. Every function gets a docstring comprehensible to a non-programmer.
- Original P7's "Strong, robust" — **retained as P13** (renumbered). Fault isolation, graceful degradation.

**Success criteria**: Expanded from 15 to 31. New criteria groups: modularity (1–6), flexibility (7–15), UI (16–18), local-first (19–20), observability (21–23), security (24–26), code quality (27–29), longevity (30–31).

**Open questions**: 10 of 18 resolved (Q5, Q6, Q7, Q10, Q11, Q12, Q15, Q16, Q17, Q18). 8 carried forward with proposed resolutions (Q1, Q2, Q3, Q4, Q8, Q9, Q13, Q14). 8 new questions added (Q19–Q26): trained expert model lifecycle, skill DAG execution, cloud relay protocol, phone app scope, loop task persistence, multi-machine core accommodation, worker-to-worker communication, composition root bootstrap.

### Author's reasoning for the major reframes (clearly labeled — attack this, not just the principles)

1. **Why drop P8 (Decentralised)**: The user's view is that "decentralised" basically means "modular," which is already covered by P2 (pluggable) and P3 (no lock-in). P8 was a slogan, not a principle. The lean orchestrator (P7) and the visible 9-section UI (P9) provide the operational definition that P8 was reaching for.
2. **Why reframe P7 to prioritise modularity + flexibility over simplicity**: The user explicitly stated "Modularity (parts break rather than whole thing) and Flexibility (can add new things easily) — that is what is most important." Simplicity is nice to have, but secondary. The hard gates are fault isolation, independence, acyclic deps, constructor arg cap — not LOC count.
3. **Why reframe P9 as OS shell with fixed 9 sections**: The user wants the UI to be a personal operating system, not a chat interface. The 9 sidebar sections map directly to the framework's own architecture (Orchestrator/Workers/Tasks/Skills/Memory/Models/Adapters/Hardware/Options). The sidebar IS the OS shell, which is legitimately core. Panel contents are capability-driven (auto-populate). User only talks to orchestrator; workers are silent.
4. **Why Security Guard as a worker, not a static permission system**: The user proposed a "Security Guard" worker that checks things for safety. This turns security from a static rule into an active reasoning layer within the existing worker architecture. The Security Guard can be trained on what's safe vs. unsafe, can adapt (retrain rather than rewrite rules), and can explain its reasoning to the orchestrator (which informs the user).
5. **Why Python now, Rust-migratable later**: The user understands Python and not Rust. Python's ML ecosystem is essential for training lightweight expert models (a stated worker capability). Rust's strengths (perf, memory safety) buy less under the user's priorities (modularity + flexibility, not perf). Contracts are kept language-agnostic (manifests, schemas) so a future Rust core could satisfy the same contracts.
6. **Why plain-English docstrings on every function**: The user wants to be able to read every line of their own system despite not knowing Python syntax. This also forces AI-generated code (Devin) to articulate what it's doing in human terms, which improves the code itself.

### Pre-mortem frame (mandatory)

Before listing any issues, open your response with:

> **Pre-mortem**: Assume Rev 2 was implemented and the project failed in 6 months. List the 3–5 most plausible reasons why. Focus on failures introduced by the Rev 2 amendments, not failures that Rev 1 already flagged.

### What to check specifically

The panel should pay special attention to:

1. **Does P9 (OS shell, 9 sections) actually resolve the P1 vs P9 conflict from Rev 1?** The 9 sections are hard-coded capability class names. Is this consistent with criterion 18 (no hard-coded individual component names)? Does "user only talks to orchestrator" hold up when the user is using the Skills canvas to author a composite skill — are they "talking to the orchestrator" or "talking to the Skills panel"?

2. **Does the Security Guard worker introduce a chicken-and-egg?** The Security Guard is a worker. Workers are reviewed by the Security Guard. Who reviews the Security Guard? Is the Security Guard user-authored (trusted by default) or external (reviewed by... itself)?

3. **Does P12 (DI, no globals, composition root) hold up under the bootstrap problem (Q26)?** The composition root instantiates all components. What instantiates the composition root? Is the composition root itself a global? Is `main()` a global?

4. **Does the lean orchestrator (routing + reasoning + user-facing synthesis) actually stay lean?** Reasoning + synthesis is non-trivial. How does the orchestrator reason without becoming a god object? Is the reasoning itself delegated to a worker (a "reasoning worker")?

5. **Do the 31 success criteria actually cover the principles?** Are there principles with no corresponding criterion? Are there criteria that contradict each other?

6. **Are the 8 new open questions (Q19–Q26) the right questions?** Are there architecture-affecting questions the user's decisions have created that Q19–Q26 don't cover?

7. **Does "user only talks to orchestrator" hold up against the Skills canvas?** The Skills canvas is an authoring surface where the user composes atomic skills into composite skills. Is this "talking to the orchestrator"? Or is it a direct interaction with the Skills panel that bypasses the orchestrator? If the latter, does it violate P9's "user only talks to orchestrator"?

8. **Does the cloud relay (P6) introduce a security hole?** The relay routes packets to the core. If the relay is compromised, can an attacker control the core? What's the threat model?

### Anti-sycophancy measures (same as Rev 1 review)

- Do NOT open with praise. Open with the pre-mortem.
- Do NOT say "this is a strong revision" or "well-amended" or similar.
- "No issues found" is valid if you genuinely find none. Do not invent issues to seem thorough.

---

## Part 3: Answer Format

Your response MUST follow this structure. Section headers are mandatory.

### A. Pre-mortem (mandatory open)
3–5 plausible failure scenarios for the project 6 months after implementing Rev 2. Focus on failures introduced by the amendments. One sentence each.

### B. Amendment check
For each major amendment, state whether it resolves the issue it was meant to resolve, or whether it introduces new problems:
- **P8 dropped** — [Resolves the redundancy / Introduces: <issue> — Severity: <X> — Failure scenario: <concrete>]
- **P7 reframed (modularity + flexibility)** — [Resolves the measurability issue / Introduces: <issue>]
- **P9 reframed (OS shell, 9 sections)** — [Resolves the P1 vs P9 conflict / Introduces: <issue>]
- **P6 clarified (cloud relay)** — [Resolves multi-device / Introduces: <issue>]
- **P10 added (Observability)** — [OK / Introduces: <issue>]
- **P11 added (Security Guard worker)** — [OK / Introduces: <issue>]
- **P12 added (DI, no globals)** — [OK / Introduces: <issue>]
- **P13 added (Docstrings)** — [OK / Introduces: <issue>]
- **31 success criteria** — [Cover the principles / Gaps: <which principles lack criteria>]
- **Q19–Q26 new questions** — [Right questions / Missing: <what else should be asked>]

### C. New issues introduced by Rev 2
List any issues that Rev 2 introduces that were not present in Rev 1. For each: [Issue: <description> — Severity: <X> — Failure scenario: <concrete> — Affected principle: <P{n}>]

### D. Unresolved Rev 1 issues
List any issues from Rev 1 that Rev 2 does NOT resolve. For each: [Issue: <description> — Why Rev 2 doesn't resolve it — Severity: <X>]

### E. Open question engagement (Q19–Q26)
For each new question, propose a resolution or explain why the question is malformed:
- **Q19** (trained expert model lifecycle): [Resolved: <proposal> — Trade-off: <one concrete> / Malformed: <why> / Defer: <why>]
- **Q20** (skill DAG execution model): [...]
- **Q21** (cloud relay protocol): [...]
- **Q22** (phone app scope): [...]
- **Q23** (loop task persistence): [...]
- **Q24** (multi-machine core accommodation): [...]
- **Q25** (worker-to-worker communication): [...]
- **Q26** (composition root bootstrap): [...]

### F. Other concerns
Open field. Anything that didn't fit above.

### G. Bottom-line recommendation
One of:
- **CLEAN PASS — proceed to Plan 1 drafting** (no CRITICAL or HIGH issues remain)
- **CONDITIONAL PASS — proceed with documented accepted risks** (MEDIUM/LOW issues accepted with reasoning)
- **REVISE — specific amendments need rework before Plan 1** (CRITICAL or HIGH issues remain)

Followed by one sentence justifying the recommendation.

---

## Adjudication note (for the user, not the panel)

The Prompt Creator will collect all 6 panel responses and adjudicate per the AI_HANDOFF.md severity rubric. A clean pass requires: (a) no panel member reports a substantiated CRITICAL or HIGH issue that hasn't been addressed, and (b) any remaining MEDIUM/LOW items are documented as accepted/rejected with reasoning.

If clean pass: Prompt Creator drafts `architecture-decision.md` mapping all resolved open questions to decisions, then drafts `plan-1-Rev1.md` (Architecture Decision Plan).

If not clean pass: Prompt Creator applies findings to produce `project-vision-Rev3.md` and re-submits.

---

## End of brief

Read `project-vision-Rev2.md` now. Then respond per the format above.
