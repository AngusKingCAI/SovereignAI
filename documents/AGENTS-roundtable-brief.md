# AGENTS.md — Round Table Review Brief

**Date**: 2026-06-28
**Document under review**: `AGENTS.md` (SovereignAI, new project — not the inherited sovereign-ai file)
**Status**: All rules locked by the Owner through one-at-a-time questionnaire review. Sent to Round Table for clean-pass check before becoming the Executor's live governance document.

---

## Part 1 — What this document is

`AGENTS.md` is the Executor's always-on rulebook. It is read in full before coding sessions and re-read before every file edit (OR22). It contains two rule families:

- **AR{n} — Architecture Rules (AR1–AR21).** Enforce SovereignAI's company-metaphor architecture (Owner → Orchestrator → Manager → Worker, Librarian-routed memory, Adapter-routed inference, capability-graph discovery). New for this project — derived from `SovereignAI_Architecture_Decisions.md` and checked line-by-line against the 14 principles in `project-vision-Rev5.md`.
- **OR{n} — Operational Rules (OR1–OR37).** Process discipline (git, testing, scope control, output verbosity). Inherited from the predecessor project (sovereign-ai) largely verbatim, since these are process lessons learned from real failures (landmines L1–L17), not architecture-specific. OR38 (decade-based plan-file cleanup) was reviewed and explicitly **dropped** — this project keeps all plan files forever. The gap was filled by OR29–OR31, which were also inherited from sovereign-ai's AGENTS.md (worker circuit-breaker-adjacent operational rules — "no-output-isn't-success," "don't re-run without diagnosing," "STOP and report blockers in a fixed format").

Every AR rule was checked individually against vision Rev 5's Modularity and Flexibility principles before being locked; the Owner's standard confirmation phrase throughout review was "if it aligns with Modularity and Flexibility then lock." No AR rule was locked without that check passing.

---

## Part 2 — Decisions the Round Table should validate

These are the substantive calls made during drafting. Flag any that should be reopened.

1. **AR1 — Orchestrator may bypass Manager for simple tasks.** Resolved via web research on hierarchical multi-agent orchestration: three-tier (Orchestrator → Manager → Worker) is right for context-window management at scale, but a mandatory third hop adds latency-without-value on trivial single-Worker tasks. The bypass is delegation-only.

2. **AR2 — Workers query the Librarian directly, not through their Manager.** Also resolved via research: routing memory through a Manager intermediary is overhead with no benefit; production multi-agent systems converge on direct-to-router access with the router (Librarian) enforcing access control. The Manager is a task coordinator, not a memory gatekeeper.

3. **AR3 — Workers, Managers, and the Orchestrator are themselves models (QLoRA-fine-tuned for Workers).** This forced a design clarification: the Models panel (Panel 6) is not a separate layer from Adapters — it's a filtered view of the Adapters panel. Every model, including a Worker's own fine-tuned weights, is a registered model adapter. This removed the need for any Orchestrator carve-out in AR3.

4. **AR5 — Constructor argument cap is 15, not 5.** A tighter numeric cap (5) was proposed first based on general DI best practice, but rejected once checked against the vision: Rev 5's own revision history shows the Round Table already debated and raised this cap from 7 to 15, and the vision's Composition Root and Routing Engine (sacred Core Scope items) cannot be written under a 5-argument cap. **This is the one place an external "best practice" recommendation was overridden by a prior locked vision decision** — flagging in case the Round Table wants to revisit the 15 figure itself.

5. **AR9 broadened beyond the original UI-only scope.** Originally proposed as "no hard-coded component names in UI layers"; broadened to cover all layers (Managers, Workers, Skills, Adapters) since the narrower version was redundant with AR7 (UI/core separation) and didn't close the gap of a Manager hard-coding a Worker name internally.

6. **AR10–AR12 (original numbering) — Security Guard rules dropped entirely**, not modified. The Owner's call: Security Guard is not pertinent to the core yet; it will be implemented later as a Worker. No placeholder rule was left in its place. A `DEBT.md` entry is owed for this deferral (not yet created — flagging as an action item, see Part 4).

7. **AR12 — The Librarian was split into two layers** (Registry, always-on, no model; Model, demand-loaded, fine-tuned) specifically because Librarian-as-a-single-fine-tuned-model conflicts with the vision's deferred model-loading decision and local-first hardware-efficiency principle. Same logic was applied that produced AR18's Manager split (temporary instance vs. persisted weights).

8. **AR18 — Managers are not fine-tuned by default; Workers always are.** Resolved via research on fine-tuning ROI: gains concentrate on specialist/focused execution (Workers), not coordination (Managers). A promoted permanent Manager may later be fine-tuned, but this isn't the v1 default.

9. **AR21 — Docstring rule was already locked in vision P12** before this exercise; AGENTS.md doesn't re-derive it, just carries it forward as an enforced rule. No independent judgment call here — included in Part 2 only so the Round Table can confirm carry-forward fidelity (jargon-replacement list, ≥10-word/verb-first test, non-coder readability bar).

---

## Part 3 — Condensation: decision made, requesting Round Table confirmation

**The concern**: AGENTS.md is ~4,250 words / ~28,000 characters across 57 rules. The original OR22 directed the Executor to re-read the full document before *every file edit* — at this length, repeated dozens of times per plan, that was the dominant context cost, far larger than any saving available from trimming individual rules' wording.

**Decision taken**: OR22 has been revised. The Executor now reads `AGENTS.md` in full **once per coding session**, at the start (this already matches `/open.md` step 3). It does **not** re-read the full document before each subsequent edit. If a rule's application becomes unclear mid-session, the Executor consults `LANDMINES.md` for the specific rule's diagnostic context — which is already the document's stated escalation path for ambiguity — rather than re-reading everything.

This addresses the dominant cost (read frequency) without touching any rule's wording or trimming any provenance/source citation, so the document's evidentiary value (OR23's audit-trail requirement, the landmine-to-rule graduation record) is unchanged. Rule-prose trimming (the original options (a) and (c) below) remains open if the Round Table wants further reduction, but is no longer the load-bearing fix.

**Still open for Round Table input, if desired:**

(a) **Condense rule prose, keep rule count.** Several rules carry inline justification or provenance narrative that duplicates what's already in `LANDMINES.md`. Could trim to terse imperative + short source pointer, moving "why" entirely to `LANDMINES.md`.

(c) **Tiered loading.** A short "always-on core" of the most frequently violated rules (OR3, OR5, OR15/16, OR18) surfaced prominently, full rule body addressable by number on demand.

(d) **Leave rule prose as-is.** Given the OR22 fix already removes the main cost driver, the Round Table may judge the remaining prose worth keeping for unambiguous enforcement in a single-developer project with no second human reviewer.

**Flag for Round Table attention**: confirm the OR22 revision doesn't create a gap — specifically, whether a single read at session start is sufficient given `/open.md` step 6 instructs running `/verify` after each edit but does not re-trigger a full-document re-read. If the Round Table believes mid-session drift risk (the Executor forgetting a rule deep into a long plan) outweighs the context savings, propose an alternative cadence (e.g., re-read at `/scan` checkpoints, or a condensed rule-index re-read rather than full re-read).

---

## Part 4 — Outstanding action items (not blocking this review)

- `DEBT.md` does not yet exist. It needs an entry: "Security Guard deferred — to be implemented as a Worker in a future plan" (referenced in AGENTS.md's AR10–12 deferral note but not yet recorded).
- `LANDMINES.md` is referenced extensively (L1–L23 inherited from sovereign-ai) but its actual content for this project was not part of this review pass — confirm it exists and matches the landmine table in AGENTS.md before Plan 1 begins.
- GR rules (Architect-facing governance rules) are out of scope for this document by design — they belong in `AI_HANDOFF.md`, not here. Noting only so the Round Table doesn't flag their absence as a gap.

---

## Part 5 — What the Round Table is being asked to do

1. **Confirm clean pass**: does any AR or OR rule conflict with `project-vision-Rev5.md`'s 14 principles or Core Scope (v1) list? Each rule was checked individually during drafting (see Part 2), but a fresh pass from outside the drafting conversation is the point of this review.
2. **Weigh in on Part 3** (condensation) — pick an option, propose a hybrid, or confirm (d) leave as-is with reasoning.
3. **Flag any rule that's ambiguous on its face** — i.e., would a literal-minded Executor know exactly what to do, without needing to consult `LANDMINES.md` for context, for every rule that doesn't explicitly say "see L{n} for context"?

Full `AGENTS.md` is attached/linked alongside this brief.
