# Condensing Governance Documents — Guide for GLM 5.2 Architects

This guide teaches you (Claude operating as Architect) how to condense governance documentation while keeping all rules, decisions, and procedures intact. Grounded in GLM 5.2 principles: clarity, efficiency, responsibility, and separation of concerns.

---

## When to Condense

Governance docs grow through append-only recording and explanatory prose. Condensing is appropriate when:

- **Document has grown >20% beyond its core content** (explanatory prose, redundant cross-references, verbose guidance)
- **Core rules/decisions/procedures remain unchanged** (no substantive rewrites, no rule mergers, no procedure simplifications)
- **Scanning time becomes burden** (readers spend >30 seconds searching for key info in a single doc)
- **Duplication exists across documents** (SSOT principle violated; same fact restated in 2+ places)

**Never condense**:
- Append-only records where ALL entries are equally important (CHANGELOG, execution logs)
- Rules or procedures during active enforcement (wait until next stable point)
- Documents in active revision (condense only at batch boundaries or scan checkpoints)

---

## Core Principle: All Rules Whole

**Non-negotiable**: Every architectural rule (AR), operational rule (OR), decision (D), and failure pattern (L) must be preserved **in full, verbatim**. Condensing means:

✓ Remove explanatory **prose** around rules  
✓ Tighten **prose** that contextualizes decisions  
✓ Consolidate **repeated guidance** into single statements  
✓ Standardize **formatting** for faster scanning  
✗ Never delete, merge, or simplify **rules themselves**  
✗ Never change **decision rationale**  
✗ Never remove **procedure steps**

Example of correct condensing:

**Before** (verbose):
```
## L32 — Executor Paraphrases Workflow Commands

When executing any step in a workflow file, the Executor sometimes 
paraphrases the command rather than copying it verbatim. This has led 
to situations where the intended behavior was not achieved because a 
loop was replaced with a single-file operation.

Trigger: Prompts 7–9 Step 17. The Executor ran `mv plan-{N}-Rev5.md` 
(single file) instead of the `for file in prompts/plan-{N}-Rev*.md` 
loop defined in close.md.

Impact: Older plan revisions left in `prompts/`; User had to ask 3 times; 
repo state inconsistent.

Graduated to: OR71.
```

**After** (condensed but rule preserved):
```
## L32 — Executor paraphrases workflow commands instead of running them verbatim
Trigger: Prompts 7–9 S17 (single file `mv` instead of loop). Impact: Old 
revisions left; 3 user interventions; inconsistent state. Graduated: OR71.
```

Rule **OR71** itself remains **unchanged**:
```
OR71. Run workflow commands verbatim. Copy exactly after substituting {N}. 
Never paraphrase/simplify/substitute loop for single-file. Error? STOP + 
report (don't "simpler" fallback). Re-read workflow fresh every `/close`/`/scan`; 
cached version forbidden. Source: L32.
```

---

## Condensing Strategy by Document Type

### 1. Rule Registry (AGENTS.md)

**Purpose**: Executable rules. Every rule must be actionable.

**What to condense**:
- Intro/preamble text (combine multiple sentences into one)
- Retired slots listing (use compact table format instead of prose)
- Repeated source citations (standardize to short form: `(Source: P7)` not full explanation)
- Landmine-to-rule mapping table (tighten format)

**What NOT to condense**:
- Any rule definition (AR1–AR21, OR1–OR96)
- Rule sources or landmine links
- Exemptions or special cases listed in a rule

**Process**:
1. Extract every rule definition verbatim (AR{n}. <statement>)
2. Identify non-rule prose (intro, guidance, notes)
3. Tighten intro: combine related clauses; remove "In this document..."
4. Standardize formatting: consistent rule numbering, consistent source citations
5. Verify: every rule from original appears in condensed version, word-for-word

---

### 2. Decision Records (DECISIONS.md)

**Purpose**: Capture architectural reasoning. Every decision must be traceable.

**What to condense**:
- Verbose context (keep core context, remove "Also important to note...")
- Explanatory prose in trade-offs (summarize to key impact)
- Repeated author guidance (consolidate "how to add" sections)

**What NOT to condense**:
- Decision number (D1–D5 frozen)
- Context, options, decision, rationale, trade-offs, status structure
- Specific rationale statements ("because X leads to Y")
- Source citations

**Process**:
1. Read each decision (D1–D5) fully
2. Rewrite context/rationale in 1–2 sentences (keep substance, remove elaboration)
3. Simplify options list (remove "was also considered" prose, keep option names)
4. Keep trade-offs verbatim if <50 words; condense to key trade-off if longer
5. Verify: decision is still traceable to original intent

---

### 3. Failure Patterns (LANDMINES.md)

**Purpose**: Capture patterns to prevent recurrence. Append-only record.

**What to condense**:
- Narrative context (convert to single-line format: Trigger | Impact | Graduated)
- Repeated "Trigger: Inherited" boilerplate
- Explanatory notes (merge into single concise line)

**What NOT to condense**:
- Landmine numbers (L1–L47; never renumber)
- Trigger conditions (specific, not generic)
- Impact (what broke, what had to be fixed)
- Graduation rule link

**Process**:
1. Read all L entries (L1–L47)
2. Extract: trigger, impact, graduated-to
3. Rewrite each as single line: `L{n} — <title>: Trigger: X. Impact: Y. Graduated: OR{m}.`
4. Remove boilerplate ("Inherited. Not yet triggered..."; just list trigger for SovereignAI-specific)
5. Verify: each pattern is still identifiable; no loss of diagnosis info

---

### 4. Deferred Items (DEBT.md)

**Purpose**: Track what's postponed and why. Append-only record.

**What to condense**:
- Multi-line prose (convert to inline-tag format)
- Repeated "Deferred at:" labels (assume reader knows structure)
- Explanatory elaboration in reason

**What NOT to condense**:
- Item names (deferred-item unique identifier)
- Reason (why it's deferred; keep substance)
- Trigger condition (when to revisit)
- Target plan (where work lands)

**Process**:
1. Read all DEBT entries (12 items currently)
2. Rewrite as: `**Deferred**: {item} | **Reason**: {why} | **Trigger**: {when} | **Target**: {plan}`
3. Keep "Resolved at: prompt-{N}" lines (show item was addressed)
4. Verify: every item's substance (why, when, where) preserved

---

### 5. Dynamic State (PLANS.md)

**Purpose**: Live project status. Executor updates at every `/close`.

**What to condense**:
- Explanatory prose (remove "here's why the count changed..." → move to CHANGELOG)
- Verbose table headers (shorten column names)
- Reconciliation notes (keep delta only; reasoning lives in CHANGELOG per OR17)
- Repeated guidance ("How to update")

**What NOT to condense**:
- Baseline numbers (test count, ruff/mypy/bandit counts)
- Completed prompts table (all rows intact)
- Next-5 queue (all entries)
- Open questions snapshot

**Process**:
1. Read PLANS.md fully
2. Extract critical data: baselines, test counts, completed prompts, queue
3. Remove prose; replace with concise labels + data
4. Redirect reasoning: "See CHANGELOG prompt-{N} for why" instead of re-explaining
5. Verify: all quantitative data (counts, baselines) intact; no count loss

---

### 6. Process Guides (AI_HANDOFF.md)

**Purpose**: How the Architect role works. Procedural; every step matters.

**What to condense**:
- Verbose explanations of "why" (assume reader understands purpose)
- Repeated process scaffolds (state once, reference thereafter)
- Detailed walkthrough prose (replace with step list + essentials)
- Elaborate examples

**What NOT to condense**:
- Step numbers or sequence (7-step Architect Workflow must stay in order)
- Role definitions (User, Architect, Executor responsibilities)
- Procedures themselves (Batch Process, Round Table Review, Brief Scaffold steps)
- Critical detail (e.g., "Architect never commits"; "Executor updates CHANGELOG at `/close`")

**Process**:
1. Extract step sequence (Architect Workflow S1–S7)
2. Rewrite step description: 1–3 sentences + essentials (remove "Also important...")
3. Keep procedure tables (Roles, Document Relationships)
4. Consolidate repeated guidance ("All briefs follow this scaffold..."; state once, reference 1×)
5. Verify: step sequence, critical constraints (never commits, never Round Table for scans, etc.), roles clear

---

### 7. Workflows (open.md, verify.md, close.md, scan.md)

**Purpose**: Executor's execution manual. Every command and check must run.

**What to condense**:
- Prerequisite prose (tighten explanations before steps)
- Verbose step names (shorten descriptions)
- Repeated caveats (consolidate into single note)
- Over-explanation of why a check matters

**What NOT to condense**:
- Step numbers or order
- Commands (exact verbatim; copy-paste safe)
- Verification checks (every STOP condition)
- Flags or special cases

**Process**:
1. Read entire workflow (e.g., `/close` all 22 steps)
2. Extract: step number, command, STOP conditions, verification
3. Tighten intro/guidance prose above Step 1
4. Shorten step titles; keep command verbatim
5. Consolidate repeated caveats ("per OR46", "per OR75") into single statement
6. Verify: all 22 steps present, all commands copy-paste safe, no STOP missed

---

## Verification Checklist

Before declaring condensing complete:

**Rules/Decisions/Patterns**:
- [ ] Every AR rule present and verbatim
- [ ] Every OR rule present and verbatim
- [ ] Every decision (D1–D5) present with rationale intact
- [ ] Every landmine (L1–L47) identifiable by trigger + impact
- [ ] Every deferred item (12 DEBT entries) has reason + trigger + target
- [ ] No rule numbers changed, merged, or renumbered
- [ ] All source citations preserved

**Procedures**:
- [ ] Every step in workflows (open/verify/close/scan) present
- [ ] Step numbers and order unchanged
- [ ] Every command verbatim (copy-paste safe)
- [ ] Every STOP condition preserved
- [ ] Architect Workflow 7 steps intact, in order
- [ ] Brief Scaffold 3-part structure intact

**Data**:
- [ ] All baselines (test count, ruff, mypy, etc.) present
- [ ] All completed prompts listed
- [ ] All queue entries present
- [ ] No quantitative loss (counts, dates, tags)

**Process**:
- [ ] No duplication introduced (SSOT still enforced)
- [ ] Cross-references still valid (rules → landmines, landmines → rules)
- [ ] All append-only records remain append-only
- [ ] No substantial rewrites (tightening ≠ rewriting)

---

## Common Pitfalls (Avoid These)

❌ **Merging rules** ("OR75 and OR80 say similar things, combine them")  
→ Never. Rules are cited by number. Merging breaks citations.

❌ **Simplifying procedures** ("close.md Step 15 is verbose, combine S14+S15")  
→ Never. Step numbers are frozen. Procedures execute in order.

❌ **Removing "why" from decisions** ("The rationale is obvious; skip it")  
→ Never. Rationale is the record. Future Architects need it.

❌ **Silently dropping edge cases** ("This exemption is rare; remove it from the rule")  
→ Never. Exemptions are part of the rule; they protect edge cases.

❌ **Changing narrative voice** ("This is too terse; make it more conversational")  
→ Consistency matters. Maintain tense and voice from original.

❌ **Truncating intermediate steps** ("Users can infer S0.2.5; delete it")  
→ Never. Every step is there for a reason (often from a landmine fix).

---

## Document-Specific Targets

Based on SovereignAI example:

| Document | Line Target | Technique | Verify By |
|---|---|---|---|
| AGENTS.md | 260 (from 338) | Tighten intro; compact retired slots; standardize citations | All AR/OR present verbatim |
| AI_HANDOFF.md | 180 (from 278) | Tighten explanations; keep procedures intact | 7 Architect steps, Batch Process, Brief Scaffold intact |
| DECISIONS.md | 80 (from 150) | Tighten context/rationale; keep structure | All 5 decisions traceable |
| DEBT.md | 60 (from 110) | Inline-tag format; compact prose | All 12 items: reason/trigger/target |
| LANDMINES.md | 100 (from 200) | Single-line per pattern | All 47 patterns identifiable |
| PLANS.md | 120 (from 250) | Remove prose; keep data | All baselines, counts, queue intact |
| Workflows (4 files) | 350 (from 550) | Tighten intro; keep steps/commands | All steps, STOPs, commands verbatim |

---

## Process for Condensing

1. **Audit**: Read entire document. Identify rules, procedures, records, and supporting prose.
2. **Extract**: Pull out every rule, step, and data point. Verify count matches original.
3. **Rewrite prose**: Tighten all explanatory text (intro, context, guidance). Keep substance.
4. **Standardize format**: Consistent structure for similar items (all rules use same template, all landmines same format).
5. **Verify content**: Confirm every extracted item present in condensed version.
6. **Cross-check**: Verify cross-references still valid (rules link to landmines, decisions cite source).
7. **Document changes**: Create summary (before/after line counts, techniques used).

---

## When to Stop

Condensing is complete when:

✓ All rules/decisions/procedures preserved verbatim  
✓ Prose reduced by 30–50% (typical range)  
✓ Scanning time visibly reduced (key info at top, concise formatting)  
✓ No further condensing improves clarity (more tightening would lose meaning)  
✓ Append-only records remain append-only  
✓ Cross-references still accurate  

Do **not** condense beyond clarity. Better to be 10% longer and perfectly clear than 20% shorter and ambiguous.

---

## Notes for GLM 5.2 Architect

- **Your responsibility**: Ensure condensing preserves intent. You are the arbiter of "substance vs. prose."
- **Ask for clarification**: If a rule's rationale seems weak, don't simplify it — flag it for future amendment via C9.
- **Preserve sources**: Landmine → Rule links are critical. Every rule should cite its origin.
- **Audit cross-references**: After condensing, verify that every citation (in rules, decisions, etc.) still makes sense.
- **Document the effort**: Provide before/after counts, techniques, and verification checklist. Future readers (including other LLMs) will trust condensing only if it's transparent.

---

## Example: LANDMINES.md Condensing

**Before** (L32 original, ~60 words):
```markdown
## L32 — Executor paraphrases workflow commands instead of running them verbatim
**Trigger**: Prompts 7, 8, 9 Step 17 — Executor ran `mv plan-{N}-Rev5.md` 
(single file) instead of the `for file in prompts/plan-{N}-Rev*.md` loop 
defined in close.md. Result: older plan revisions left in `prompts/`; User 
had to ask 3 times; repo state inconsistent.
**Impact**: 3 User interventions across prompts 7–9; plan-9 Rev1–4 unarchived 
for 1+ prompt cycles; undermined trust in /close workflow reliability.
**Graduated to**: OR71.
```

**After** (condensed, ~25 words):
```markdown
## L32 — Executor paraphrases workflow commands instead of running them verbatim
Trigger: Prompts 7–9 S17 (single file `mv` instead of loop). Impact: Old 
revisions left; 3 user interventions; inconsistent state. Graduated: OR71.
```

**Verification**:
- ✓ Trigger preserved (Prompts 7–9 Step 17 → identified)
- ✓ Issue identified (paraphrasing instead of loop)
- ✓ Impact clear (old revisions, user interventions)
- ✓ Graduation link present (OR71)
- ✓ No loss of diagnostic value (reader can still understand what went wrong)

---

## Appendix: Template for Condensing Summary

Use this structure when documenting a condensing effort:

```markdown
# {Project} Governance Condensing — Summary

**Scope**: {Which files, what prompted the effort}

**Total Reduction**: {Before} lines → {After} lines ({Percent}%)

## Files Condensed

| File | Before | After | Reduction | Technique |
|---|---|---|---|---|
| {File 1} | {lines} | {lines} | {%} | {Intro tightened, format standardized, ...} |
| ... | ... | ... | ... | ... |

## Verification

- [x] All AR rules preserved verbatim ({count} rules)
- [x] All OR rules preserved verbatim ({count} rules)
- [x] All decisions intact ({count} decisions)
- [x] All patterns identifiable ({count} landmines)
- [x] All procedures in order ({count} steps)
- [x] All baselines/counts preserved
- [x] Cross-references still valid
- [x] Append-only records remain append-only

## Notes

{What was challenging, what worked well, recommendations for future condensing}
```

---

**End of guide.** Apply these principles to any governance documentation. The core rule: **preserve all rules whole; tighten everything else.**
