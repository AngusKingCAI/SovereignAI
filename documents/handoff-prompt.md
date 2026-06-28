**Handoff Prompt — AGENTS.md Round Table Rev2 (SovereignAI)**

We are applying accepted Round Table review findings to `AGENTS.md` one fix at a time, the same disciplined way the original AR/OR rules were locked: propose the exact wording change, explain why, check it against `project-vision-Rev5.md`'s principles, and only lock on the user's explicit confirmation ("does this change stick to principles, if so lock").

## Status: 5 of ~12 accepted fixes locked

**Locked so far:**
1. ✅ OR37 — pytest exempted from batch verification chaining (no principle conflict; pure operational consistency fix)
2. ✅ AR9 — Composition Root (`main.py`), tests, and manifests exempted from no-hard-coded-names rule (justified by vision Q26 — "no runtime magic, no auto-discovery" for `main.py` specifically)
3. ✅ AR1 — bypass tightened with four explicit "simple task" criteria (one Worker, one capability, no cross-cutting state, no multi-step dependency chain) + per-delegation (non-standing) clarification (justified by Principle 7, acyclic graph / no invisible coupling)
4. ✅ AR16 — circuit-breaker error *count* clarified as a DI-managed per-Worker object in the container, not module-level state in `shared/`; error-counting *logic* stays in `shared/` (justified by Principle 11, extends the same singleton-via-injection pattern AR4 already uses for Orchestrator/Librarian Registry)
5. 🔄 **AR11 — PROPOSED, AWAITING LOCK CONFIRMATION.** Adds a clarifying sentence: shipped default memory topology assignments live in a user-editable config file (e.g. `config/memory_topology.yaml`), read by the Librarian Registry at startup — never as a dictionary/mapping compiled into source code. Justified by Principle 2/3 — matches the same "delete any file, system gracefully degrades" mechanical test used elsewhere in the vision. **Next step: get the user's lock confirmation on AR11, then apply it to the actual file (it has only been proposed in chat, not yet written to AGENTS.md).**

## Remaining fixes from the adjudication, not yet proposed in chat

These were accepted in the adjudication message but we haven't reached them in the one-at-a-time walkthrough yet:

6. **AR6** — add clarifying sentence that TraceEmitter must not be misused as a context bag (carries only structured trace/observability data, no business-logic parameters).
7. **AR15** — add a sentence specifying in-flight tool call behavior when an adapter fails its health check mid-call (current call completes with graceful error response, then deregisters).
8. **OR4** — add a parenthetical: before applying the `>> Issue: [B` bandit filter, visually confirm the output format still matches; if not, report the format change as a blocker.
9. **OR22** — add an always-on subset checked at every file edit (not a full re-read): OR5, OR6, OR15, OR16, OR34, plus numeric thresholds AR5 (15-arg cap), AR16 (50 errors/10s), AR21 (10-word docstring bar). Also add: full re-read triggered if `AGENTS.md` itself changes mid-session, or session resumes after a STOP/replan boundary.
10. **AR5** — add parenthetical clarifying parameter counting excludes `self`/`cls`; auto-generated dataclass `__init__` is subject to the cap unless it's a pure DTO per AR6.
11. **OR23** — define clearer citation triggers: cite a rule when (a) it directly shapes code structure, (b) it blocks a proposed action, or (c) it's explicitly listed in the plan step.
12. **AR8 numbering gap** — add a one-line note explicitly retiring AR8's number (it was dropped as redundant with AR7); do not renumber AR9–21 down, since that would invalidate cross-references already made in the brief and this review.

## Also tracked (non-blocking, Part 4 action items — not AGENTS.md edits)

- `DEBT.md` doesn't exist yet — needs an entry for the Security Guard deferral (referenced in AGENTS.md's AR10–12 deferral note).
- `LANDMINES.md` content for this project hasn't been reviewed — confirm it exists and L1–L23 inherited entries match the landmine table already in AGENTS.md, before Plan 1 begins.

## Process reminders

- **Working file location**: the locked AGENTS.md is at `/mnt/user-data/outputs/AGENTS.md` from the prior session — confirm it's still there or re-create from this handoff's locked-fixes list before continuing edits. None of fixes 1–4 above have been written into the actual file yet either — only proposed and confirmed in chat. **Before continuing the walkthrough, first apply fixes 1–4 (and 5 once locked) to the actual file with `str_replace`, then proceed to fix 6 onward.**
- **Confirmation phrase**: the user's standard lock signal is "does this change stick to principles, if so lock" (or minor variants). Only write the change to the file after that confirmation — do not pre-emptively edit the file while a fix is still "proposed."
- **Style**: one fix at a time, in the order listed above (6 → 12) unless the user redirects. For each: state the exact wording change, the failure scenario it closes, and an explicit principle/vision citation (not just "this seems fine") before asking for lock.
- **After all fixes are locked**: per the original adjudication, this becomes "AGENTS.md Rev2" — per `AI_HANDOFF.md`, Rev2+ revisions do not need a new Round Table brief; the Round Table reviews the revised file directly. Offer to produce a clean Rev2 `AGENTS.md` and a short changelog of what changed from Rev1, for the user to send back to the Round Table for a fast re-pass confirmation.

## Key documents (all on disk at `/mnt/user-data/uploads/` as of last session)

- `project-vision-Rev5.md` — canonical vision, 14 principles, Core Scope (v1)
- `SovereignAI_Architecture_Decisions.md` — company-metaphor architecture sketch
- `AI_HANDOFF.md` — Architect/Executor/User process guide, Round Table mechanics, GR rules
- `AGENTS.md` — the file being revised (Rev1, fully locked, now undergoing Rev2 fixes)
- `AGENTS-roundtable-brief.md` — the brief sent to the Round Table that prompted this review
- `open.md`, `close.md`, `scan.md`, `verify.md` — Executor workflow files
