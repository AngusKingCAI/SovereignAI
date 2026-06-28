# Round Table Brief — Project Vision Rev 4 Clean-Pass Check #3

**To**: 6-AI Round Table (GPT, Gemini, Llama, Qwen, DeepSeek, Kimi)
**From**: Prompt Creator (GLM)
**Date**: 2026-06-27
**Subject**: Clean-pass check #3 on amended vision (Rev 4)
**Attached**: `project-vision-Rev4.md` (read in full before responding)
**Prior context**: Round table Rev 3 review (4 substantive responses received; all returned REVISE). Rev 4 incorporates panel findings + user resolution of all flagged issues.

---

## Part 1: Your Role and Rules

**Your job is to determine whether Rev 4 has a clean pass.** This is the third clean-pass check. Rev 3 had 2 CRITICAL and 7 HIGH issues; Rev 4 addresses all of them. You are checking whether the amendments actually resolve the problems, and whether they introduce new ones.

**Adversarial framing**: Assume Rev 4 has at least one unresolved issue or one new issue introduced by the amendments. Find it. The author wants you to attack the amendments, not ratify them.

**Proof requirement**: Every issue you raise MUST include (a) a concrete failure scenario, (b) evidence from the Rev 4 document (quote the relevant principle or criterion), and (c) a severity rating per the rubric below. Issues without failure scenarios will be discarded.

**Sign-off (mandatory)**: End your response with a line in the format `**Panelist**: <your name/model>`. Anonymous responses will be flagged but still adjudicated; named responses are preferred for accountability.

**What this is NOT**:
- NOT a re-litigation of resolved questions. Q5, Q6, Q7, Q10, Q11, Q12, Q15, Q16, Q17, Q18, Q19, Q20, Q21, Q22, Q23, Q24, Q25, Q26, Q27, Q28, Q29, Q30 are resolved. Do not re-raise them.
- NOT a fresh architecture design. The architecture direction is set (Python now, Rust-migratable later; lean orchestrator; workers compose skills; Security Guard worker; 9-section UI as separate processes; cloud relay with E2EE + login gate; provenance enforcement). Engage with the new open questions (Q31, Q32), but do not propose alternative architectures.
- NOT a style review. Formatting, tone, and word choice are out of scope.
- NOT a popularity contest. "No issues found" is a valid response.

**Severity rubric** (same as Rev 1/Rev 2/Rev 3):
- **CRITICAL**: A principle is contradictory, internally inconsistent, or would cause data loss / security vulnerability / irreversible system damage if implemented as written.
- **HIGH**: A principle is underspecified in a way that would cause a build failure, test failure, or Devin STOP condition when Plan 1 (Architecture Decision Plan) is drafted.
- **MEDIUM**: A principle is sound but underspecified — degraded functionality, poor UX, or technical debt likely if not clarified before Plan 1.
- **LOW**: Minor clarification, naming preference, or speculative future concern.

---

## Part 2: Context

### What changed in Rev 4

Rev 4 incorporates findings from 4 substantive round table responses to Rev 3, plus the user's resolution of all flagged issues. The major changes:

**Principles**:
- **P9 reframed (again)** — UIs are NOT part of the core. UIs (web/CLI/TUI/phone) are separate processes that consume the core's capability API. Option A from day one (no Option B → A migration). This resolves the C1 contradiction from Rev 3 (P9b "core-hosted" vs criterion 20 "zero core edits").
- **P6 changed** — cloud relay uses a login gate (username + password) instead of QR pairing. User creates login on core during first-run setup; phone app pairs by entering core address + credentials. No physical access required. E2EE still in place.
- **P7 changed** — constructor arg cap raised from 7 to 15. User's call: "give workers the resources they need." The "no context bags" rule (P12) remains the real protection against god-objects.
- **P9 worker→user interrupt schema expanded** — supports boolean, text, choice (select one from list), multi_choice (select multiple), file (file picker). Orchestrator renders generically.
- **P10 (Observability) tightened** — "No silent failures" added. Event bus may isolate faults, but never silently swallows them. All errors logged at ERROR level with full context.
- **P11 (Security Guard) — criterion 27 narrowed** — event bus fault isolation applies to all components except the Security Guard, which is accepted as an in-process risk. If the Security Guard crashes, the core process may crash; recovery on next launch. This is the documented exception.
- **P14 added (Provenance enforcement)** — every external component must carry a signed provenance manifest (author identity, content hash, dependency list). Core verifies signatures on install and update. Unsigned components rejected by default; user can override for local development (override is explicit and logged).

**Core Scope (v1) section added** — concrete list of what's in the core (12 items: composition root, event bus, manifest parser, capability graph, routing engine, lifecycle manager, TraceEmitter, task state machine, DAG validator, auth middleware, relay server, capability API) and what's outside (all adapters, skills, memory backends, workers, UIs, gateways, model loading/unloading, self-correction loops, cross-platform packaging).

**Success criteria**: Expanded from 35 to 37. New: criterion 8 (event bus fault isolation with Security Guard exception), criterion 28 (no silent failures), criterion 32 (provenance enforcement). Constructor arg cap criterion updated to 15.

**Open questions**: Q27 removed (moot under Option A). 2 new questions added (Q31 packaging, Q32 debt register).

**Platform target**: v1 is Windows-only. Cross-platform (macOS, Linux) deferred to a later plan.

**Single developer**: v1 has one developer (the user). Process rules assume solo development — no parallel dev concern.

### Author's reasoning for the major amendments (clearly labeled — attack this, not just the principles)

1. **Why UIs are now separate processes (P9 reframed again)**: Rev 3 panel unanimously flagged that P9b "core-hosted" directly contradicted criterion 20 ("zero core edits for UI presentation changes"). If presentation code is inside the core process, every UI change IS a core edit. The user accepted the panel's recommendation: UIs are separate processes from day one. The web GUI is still built first, but it connects to the core via local socket instead of living inside it. More upfront work (~2-3x for the first UI), but no contradiction, no migration debt, no future refactor. **Author confidence: 95%.**

2. **Why login gate replaces QR pairing (P6)**: Rev 3 panel flagged that QR pairing requires physical access to the core machine, blocking remote phone setup. The user's response: "We will set up a login gate." User creates a login (username + password) on the core during first-run; phone app pairs by entering core address + credentials. No physical access required. E2EE still in place — the relay still can't inspect payloads. **Author confidence: 90%.**

3. **Why constructor arg cap raised to 15 (P7)**: Rev 3 panel flagged that 7 was too restrictive for workers needing many deps (LLM adapter, memory router, trace emitter, skill registry, config, event bus, sandbox manager, approval gate = 8). The user's response: "Why the cap, give workers the resources they need." Raised to 15 — generous, accommodates any realistic case. The "no context bags" rule (P12) remains the real protection against god-objects. If performance issues arise, the cap can be lowered later. **Author confidence: 85%.**

4. **Why criterion 27 is narrowed for Security Guard (P11)**: Rev 3 panel flagged that criterion 27 (event bus fault isolation) is mathematically impossible given P11 (in-process Security Guard). The user's response: narrow criterion 27 to exclude the Security Guard. "Event bus fault isolation applies to all components except the Security Guard, which is accepted as an in-process risk." This is an honest carve-out — documents the exception rather than pretending it doesn't exist. If the Security Guard crashes, the core process may crash; recovery on next launch. **Author confidence: 80%.**

5. **Why provenance enforcement is now a principle (P14)**: Rev 3 panel flagged that provenance is only useful if enforced at load and update time. The user agreed: "Fix seems logical." P14 added: every external component must carry a signed provenance manifest. Core verifies signatures on install and update. Unsigned components rejected by default; user can override for local development (override is explicit and logged). **Author confidence: 90%.**

6. **Why "no silent failures" is now a criterion (criterion 28)**: Rev 3 panel flagged that event bus fault isolation could mask systemic pressure — errors silently swallowed to keep the system "running." The user's response: "No silent failures, Logger will track them." Criterion 28 added: every error is logged at ERROR level with full context. The event bus may isolate faults, but never silently swallows them. **Author confidence: 95%.**

7. **Why v1 is Windows-only**: Rev 3 panel flagged that cross-platform packaging is undefined. The user's response: "Not sure yet, let's just get it working within Windows first and we will look at other platforms after." v1 targets Windows only. Cross-platform deferred. Q31 (packaging format) added as an open question. **Author confidence: 90%.**

8. **Why Core Scope (v1) list was added**: Rev 3 panel flagged that the minimum core boundary was not precise enough. The user accepted the proposed list. Core Scope (v1) section added — concrete list of 12 items in the core, everything else outside. Changes to the list require a core upgrade (round table review). **Author confidence: 95%.**

### Pre-mortem frame (mandatory)

Before listing any issues, open your response with:

> **Pre-mortem**: Assume Rev 4 was implemented and the project failed in 6 months. List the 3–5 most plausible reasons why. Focus on failures introduced by the Rev 4 amendments, not failures that Rev 1/Rev 2/Rev 3 already flagged.

### What to check specifically

The panel should pay special attention to:

1. **Does P9 (UIs as separate processes) actually resolve the P1 vs P9 conflict?** Criterion 21 (UI presentation changes require zero core edits) is the test. Is it now enforceable? Is the capability API (the contract between core and UIs) well-enough specified that a UI can be built without touching core code?

2. **Does the login gate (P6) introduce security issues?** Username + password auth is simpler than QR pairing but potentially weaker. What's the threat model? Can passwords be brute-forced? Is there rate limiting? Is the login session token stored securely on the phone app?

3. **Does the constructor arg cap of 15 (P7) still prevent god-objects?** The "no context bags" rule is the real protection. Is it sufficient? Can a developer still create a god-object by spreading state across 15 individual deps that all happen to be the same underlying service?

4. **Does the Security Guard exception (criterion 27 carve-out) create a footgun?** The user accepts the risk. But if the Security Guard crashes and takes down the core, what's the recovery story? Is the crash logged before the process dies? Can the user tell what happened?

5. **Does P14 (provenance enforcement) create too much friction?** Every external component must be signed. The user can override for local development. Is the override easy enough that it doesn't block experimentation? Is the signing process documented?

6. **Does the Core Scope (v1) list hold up?** Are the 12 items the right 12? Is anything missing (e.g., should the DAG executor be separate from the DAG validator)? Is anything there that shouldn't be (e.g., should the relay server be outside the core)?

7. **Does "no silent failures" (criterion 28) hold up under realistic fault rates?** If a faulty worker emits 1000 errors per second, the Log drawer floods. Is there rate limiting per component, or does the user just see a wall of errors?

8. **Are Q31 (packaging) and Q32 (debt register) the right questions?** What else should be asked given the Rev 4 amendments?

### Anti-sycophancy measures (same as Rev 1/Rev 2/Rev 3)

- Do NOT open with praise. Open with the pre-mortem.
- Do NOT say "this is a strong revision" or "well-amended" or similar.
- "No issues found" is valid if you genuinely find none. Do not invent issues to seem thorough.

---

## Part 3: Answer Format

Your response MUST follow this structure. Section headers are mandatory.

### A. Pre-mortem (mandatory open)
3–5 plausible failure scenarios for the project 6 months after implementing Rev 4. Focus on failures introduced by the Rev 4 amendments. One sentence each.

### B. Amendment check
For each major amendment, state whether it resolves the issue it was meant to resolve, or whether it introduces new problems:
- **P9 reframed (UIs as separate processes)** — [Resolves the P1 vs P9 conflict / Introduces: <issue> — Severity: <X> — Failure scenario: <concrete>]
- **P6 changed (login gate)** — [Resolves the remote pairing problem / Introduces: <issue>]
- **P7 changed (cap raised to 15)** — [Resolves the anti-pattern risk / Introduces: <issue>]
- **P9 worker→user interrupt schema expanded** — [Resolves the interaction bottleneck / Introduces: <issue>]
- **P10 tightened (no silent failures)** — [Resolves the fault-masking risk / Introduces: <issue>]
- **P11 criterion 27 narrowed (Security Guard exception)** — [Resolves the contradiction / Introduces: <issue>]
- **P14 added (provenance enforcement)** — [OK / Introduces: <issue>]
- **Core Scope (v1) list added** — [Resolves the boundary ambiguity / Introduces: <issue>]
- **37 success criteria** — [Cover the principles / Gaps: <which principles lack criteria>]
- **Q31, Q32 new questions** — [Right questions / Missing: <what else should be asked>]

### C. New issues introduced by Rev 4
List any issues that Rev 4 introduces that were not present in Rev 3. For each: [Issue: <description> — Severity: <X> — Failure scenario: <concrete> — Affected principle: <P{n}>]

### D. Unresolved Rev 3 issues
List any issues from Rev 3 that Rev 4 does NOT resolve. For each: [Issue: <description> — Why Rev 4 doesn't resolve it — Severity: <X>]

### E. Open question engagement (Q31, Q32)
For each new question, propose a resolution or explain why the question is malformed:
- **Q31** (packaging and distribution): [Resolved: <proposal> — Trade-off: <one concrete> / Malformed: <why> / Defer: <why>]
- **Q32** (debt register format): [...]

### F. Other concerns
Open field. Anything that didn't fit above.

### G. Bottom-line recommendation
One of:
- **CLEAN PASS — proceed to Plan 1 drafting** (no CRITICAL or HIGH issues remain)
- **CONDITIONAL PASS — proceed with documented accepted risks** (MEDIUM/LOW issues accepted with reasoning)
- **REVISE — specific amendments need rework before Plan 1** (CRITICAL or HIGH issues remain)

Followed by one sentence justifying the recommendation.

### H. Sign-off (mandatory)
End your response with: `**Panelist**: <your name/model>`

---

## Adjudication note (for the user, not the panel)

The Prompt Creator will collect all 6 panel responses and adjudicate per the AI_HANDOFF.md severity rubric. A clean pass requires: (a) no panel member reports a substantiated CRITICAL or HIGH issue that hasn't been addressed, and (b) any remaining MEDIUM/LOW items are documented as accepted/rejected with reasoning.

If clean pass: Prompt Creator drafts `architecture-decision.md` mapping all resolved open questions to decisions, then drafts `plan-1-Rev1.md` (Architecture Decision Plan).

If not clean pass: Prompt Creator applies findings to produce `project-vision-Rev5.md` and re-submits.

---

## End of brief

Read `project-vision-Rev4.md` now. Then respond per the format above. Sign off with your name/model.
