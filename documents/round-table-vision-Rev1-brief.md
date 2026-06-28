# Round Table Brief — Project Vision Review

**To**: 6-AI Round Table (Claude, Kimi, DeepSeek, Gemini, ChatGPT, sixth member)
**From**: Prompt Creator (GLM)
**Date**: 2026-06-27
**Subject**: Architecture review for a new local-first AI assistant framework
**Attached**: `project-vision.md` (canonical vision document — read in full before responding)

---

## Part 1: Your Role and Rules

**Your job is to find issues, not rewrite the vision.** You are reviewing a founding vision document for a new software project. The author wants you to attack it, not ratify it.

**Adversarial framing**: Assume this vision is flawed. Assume the architecture that emerges from it will fail in 6 months. Your job is to identify how — concretely, with specific failure scenarios.

**Proof requirement**: Every issue you raise MUST include (a) a concrete failure scenario, (b) evidence from the vision document or general engineering knowledge, and (c) a severity rating per the rubric below. Issues without failure scenarios will be discarded.

**What this is NOT**:
- NOT a request for a complete architecture design. You may propose architectural directions, but only to illustrate how a principle succeeds or fails — not to replace the author's role.
- NOT a style review. Formatting, tone, and word choice are out of scope.
- NOT a feature brainstorm. Do not propose features the vision does not mention.
- NOT a popularity contest. If you find no substantive issues, say "No issues found" — do not pad with false concerns.

**Severity rubric** (use these labels):
- **CRITICAL**: A principle is contradictory, internally inconsistent, or would cause data loss / security vulnerability / irreversible system damage if implemented as written.
- **HIGH**: A principle is underspecified in a way that would cause a build failure, test failure, or Devin STOP condition when Plan 1 (Architecture Decision Plan) is drafted.
- **MEDIUM**: A principle is sound but underspecified — degraded functionality, poor UX, or technical debt likely if not clarified before Plan 1.
- **LOW**: Minor clarification, naming preference, or speculative future concern.

---

## Part 2: Context

### Project summary

The author is building a local-first, single-user AI assistant framework. The premise: models, adapters, skills, and memory paradigms will keep changing over the next decade. The core must absorb whatever comes without rewrites. The project is a fresh start — no code exists yet. The author wants the round table to debate the vision BEFORE any architecture is chosen.

### Predecessor context (read carefully — this is anchoring bait)

The author previously built a similar project ("sovereign-ai") that ran 95 prompts and accumulated known scars. The vision document deliberately does NOT name the predecessor, but you should know: the lessons learned from that project inform this vision. Specifically:
- The predecessor tried Next.js/React/TypeScript for the web UI and abandoned it after 3 failed remediation rounds. The vision's Principle 9 (UIs are core, capability-driven) and the vanilla-JS default are direct responses.
- The predecessor had three overlapping approval gate modules. The vision's emphasis on decentralisation and "no central authority" is a response.
- The predecessor's adapter base class drifted across 12 implementations. The vision's emphasis on contract-based pluggability is a response.

**Anchoring mitigation**: The author's reasoning above is labeled. Attack the reasoning, not the conclusion. If you think the conclusion (e.g., "vanilla JS") is right but the reasoning (e.g., "because sovereign-ai failed at React") is wrong or insufficient, say so. The author wants the strongest justification, not the first one.

### Author's reasoning (clearly labeled — attack this, not just the principles)

The author's reasoning for the vision's shape:

1. **Why "sacred core"**: A small core outlives its first generation of adapters. If the core is large, every adapter change forces core changes, and the system rots from the inside. **Author confidence: 85%.**
2. **Why "decentralised"**: Central orchestrators become bottlenecks — every new capability needs orchestrator changes. Capability-based routing lets the core stay ignorant. **Author confidence: 60%.** The author is unsure whether "no central orchestrator" is achievable in practice or whether it collapses into a hidden orchestrator.
3. **Why "UIs are core, auto-populate"**: A UI that hard-codes a skill name breaks the moment that skill is removed. The only sustainable UI is one that renders whatever the system advertises. **Author confidence: 90%.**
4. **Why "local-first"**: Cloud lock-in kills long-term projects when providers deprecate APIs. Local-first is the only hedge. **Author confidence: 95%.**
5. **Why "wire as you go"**: Unwired capabilities are technical debt that rots. Better to ship with 3 working skills than 30 stub skills. **Author confidence: 80%.**
6. **Why no language/runtime chosen**: The author believes the language choice should follow from the principles, not precede them. Picking Python because it's familiar would violate Principle 7 (simple core) if a smaller core is achievable in another language. **Author confidence: 50%.** The author is genuinely unsure here and wants the panel to argue.

### Named open questions for the panel to engage with

The vision document lists 18 open questions (Q1–Q18) explicitly deferred to the round table. **Engage with each one substantively.** For each:
- Propose a resolution OR explain why the question is malformed and should be reworded.
- If you propose a resolution, name one concrete trade-off it creates.
- If you believe two questions are secretly the same question, say so.

The panel should pay special attention to:
- **Q5** (skill vs adapter boundary) — the author considers this the taxonomy question that will rot if not resolved cleanly.
- **Q10** (language and runtime) — the author has no strong preference and wants the strongest argument, not the safest one.
- **Q11** (smallest possible core) — propose a line-count budget and defend it. The author believes 500–1,000 LOC is achievable; attack this.
- **Q12** (what does "decentralised" mean in practice) — the author's confidence is 60% and explicitly invites attack.
- **Q16** (how do UIs auto-populate) — the author considers this the most architecturally demanding question because it determines whether Principle 9 is achievable.
- **Q17** (are UIs truly core or core-hosted) — the author is unsure whether web/TUI/CLI are three implementations of one contract or three separate core modules.
- **Q18** (what does a capability look like to a UI) — the author believes this question, if answered wrongly, will cause capabilities to drag UI concerns into their domain.

### Pre-mortem frame (mandatory)

Before listing any issues, open your response with:

> **Pre-mortem**: Assume this vision was implemented and the project failed in 6 months. List the 3–5 most plausible reasons why.

This frame is mandatory because it forces you to think about failure modes before defending the vision. Do not skip it.

### Anti-sycophancy measures

Per Anthropic research, LLM reviewers are sycophantic in 9–25% of reviews. To counter this:
- Do NOT open with praise. Open with the pre-mortem.
- Do NOT say "this is a strong vision" or "well-structured" or similar. The author does not want validation.
- If you find yourself wanting to praise, ask: is the praise substantive (with evidence) or social? If social, cut it.
- "No issues found" is a valid response if you genuinely find none. Do not invent issues to seem thorough.

---

## Part 3: Answer Format

Your response MUST follow this structure. Flexibility within sections is fine; the section headers are mandatory.

### A. Pre-mortem (mandatory open)
3–5 plausible failure scenarios for the project 6 months after implementation. One sentence each.

### B. Principle critique
For each of the 9 principles in `project-vision.md`:
- **Principle N — <name>**: [OK as written / Issue: <description> — Severity: <CRITICAL/HIGH/MEDIUM/LOW> — Failure scenario: <concrete>]
- If a principle is missing, propose it.
- If two principles conflict, name the conflict.

### C. Open question resolutions
For each of Q1–Q18:
- **Q{n}**: [Resolved: <proposal> — Trade-off: <one concrete> / Malformed: <why> / Defer: <why>]
- You may skip a question only if you explicitly say "Defer: <reason>".

### D. Architecture direction (optional, illustrative only)
If you want to propose an architectural direction to illustrate how the principles succeed or fail, do so here. Keep it to one paragraph. This is NOT a request for a full design — just enough to make your point. Do not exceed 200 words.

### E. Other concerns
Open field. Anything that didn't fit above. Use this for unexpected issues, cross-cutting concerns, or process suggestions. If empty, write "None."

### F. Bottom-line recommendation
One sentence: **Proceed to Plan 1 drafting** / **Revise vision before Plan 1** / **Specific principles need rework before Plan 1**. Followed by one sentence justifying the recommendation.

---

## Adjudication note (for the user, not the panel)

The Prompt Creator will collect all 6 panel responses and adjudicate per the AI_HANDOFF.md severity rubric. The Prompt Creator commits to adopting the highest-scoring recommendation — even if it contradicts the author's original position. Findings will be summarised in `architecture-decision.md`, which the user reviews before Plan 1 is drafted.

---

## End of brief

Read `project-vision.md` now. Then respond per the format above.
