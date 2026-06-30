# Round Table Brief — Token Efficiency Audit of AGENTS.md, LANDMINES.md, AI_HANDOFF.md

## What's being reviewed

Audit of 3 governance files for token efficiency. These files are loaded into Devin's context at the start of every plan and on every `/close`. Every token costs context window space. The question: **is each rule, landmine, and section earning its token cost, or is there dead weight?**

## Files

1. `AGENTS-rev11.md` — 73 OR + 17 AR = 90 rules. ~273 lines. Loaded by Devin at `/open` step 5 (OR16).
2. `LANDMINES-rev10.md` — 46 landmines. ~241 lines. Read by Devin on-demand when a rule is ambiguous.
3. `AI_HANDOFF-rev10.md` — process guide for Architect. ~112 lines. Read by Architect (GLM), not Devin — but Devin reads it at S0.2 alongside AGENTS.md.

## The problem

AGENTS.md + LANDMINES.md = ~514 lines = ~6,000 tokens loaded into Devin's context before any code is written. On a 120-line plan (~1,500 tokens), the governance overhead is 4:1. If half the rules are redundant, outdated, or never triggered, that's ~3,000 wasted tokens per plan — context that could be used for actual code comprehension.

## What to evaluate

For each rule/landmine/section, ask:

1. **Does Devin actually need this?** — If it's the Architect's process (round table, plan drafting), it doesn't belong in AGENTS.md.
2. **Is it mechanically enforced?** — If a workflow file (open.md/close.md/scan.md/verify.md) already enforces it via a command, the rule in AGENTS.md is redundant documentation, not enforcement.
3. **Has it ever been triggered?** — If no landmine references it and no execution log shows it being cited, it may be dead code.
4. **Can it be merged?** — If two rules say the same thing in different words, merge them.
5. **Is it an implementation detail?** — If it describes HOW something is stored/configured (not WHAT Devin must do), it belongs in DECISIONS.md or code comments, not AGENTS.md.
6. **Is the landmine still relevant?** — If the failure pattern can't recur (e.g., Windows Git Bash quirk that's now handled by the workflow file), the landmine is historical only and could be archived.

## Decisions locked

1. AGENTS.md is Devin's file only. Architect/User process rules don't belong here.
2. OR52: numbering is permanent going forward (Rev 9 was the one-time reset). No renumbering.
3. 89% coverage floor. 120-line plan cap. P4/P6/P10/P14 deferred.
4. Two-layer spec-match (OR73). Mechanical enforcement > judgment.
5. The goal is frugality — cut anything that doesn't prevent a real failure.

## Severity

- **Critical**: rule/landmine is pure waste — cut it immediately.
- **High**: rule/landmine is redundant with a workflow file or another rule — merge or cut.
- **Medium**: rule/landmine could be shortened by 50%+ without losing meaning.
- **Low**: minor tightening possible.

## Rules

- Cite the specific rule/landmine number and quote its text.
- For each cut/merge suggestion, explain why it's safe to remove.
- If a rule is essential, say "KEEP" — don't cut for the sake of cutting.
- Don't suggest adding new rules. This is a subtraction pass only.
- Don't re-litigate locked decisions.

## Deep context

SovereignAI uses Devin (AI agent) to execute plans. AGENTS.md is loaded into Devin's context at the start of every plan. The 18.x saga showed context rot at 250-300 line plans — the same principle applies to governance docs. Every unnecessary rule in AGENTS.md competes for token space with actual code comprehension.
