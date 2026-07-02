plan-20.8-Rev1.md — AGENTS.md + LANDMINES.md Cleanup and Restructure
Depends on: prompt-20.7.3
Vision principles: 12 (minimal tokens), 5 (wire as you go)
Open questions resolved: Q35 (governance token cost)

## WILL edit
- `AGENTS.md` — remove 38 redundant rules, reclassify 18 OR→AR, remove AR9 (speculative), remove [Mandatory] tags, renumber numerically
- `LANDMINES.md` — purge to 18 active landmines, update rule number references
- `archive/LANDMINES-ARCHIVE.md` — NEW. 35 historical landmines graduated to removed rules
- `CHANGELOG.md` — append prompt-20.8 entry.
- `PLANS.md` — update baseline.
- `prompts/plan-20.8-Rev1.md` — move to completed/ at /close.

## WILL NOT edit
- Any file not listed above. If scope expands, STOP per OR6.

## S0 — Opening

S0.1: Run `/open`. Read `AGENTS.md` in full.
S0.2: Read the proposal at `prompts/proposal-agents-landmines-restructure.md` for context.
S0.3: No new rules for this plan.
S0.4: Begin Phase 1.

## S1 — Remove Redundant Rules from AGENTS.md

S1.1: Remove these 38 rules (mechanically enforced by scripts, skills, or plan templates):
- AR4, AR5, AR6, AR7, AR9 (AR-check script coverage)
- OR1, OR14, OR77, OR78, OR80 (/open skill coverage)
- OR11, OR40, OR42, OR43, OR44, OR55, OR57, OR63, OR65, OR73, OR81 (/close skill coverage)
- OR10, OR19, OR22, OR38, OR41, OR46, OR60, OR75 (plan template conventions)
- OR8, OR23, OR28, OR29, OR30 (cultural/orphan)
- OR5, OR17, OR25, OR26, OR27, OR45, OR74, OR79, OR76 (implementation details)

S1.2: Commit: git add -A && git commit -m "docs: remove 38 redundant rules from AGENTS.md"

## S2 — Reclassify OR Rules to AR Rules

S2.1: Reclassify these 18 OR rules to AR (they are architectural constraints, not operational):
- OR15 → AR13 (FastAPI web app process boundary)
- OR16 → AR14 (SSE auth method)
- OR17 → AR15 (Web-layer DTOs)
- OR18 → AR16 (Adapter health_check interface)
- OR19 → AR17 (Capability conformance tests)
- OR24 → AR20 (Memory backend pluggability)
- OR25 → AR21 (Crash recovery mechanism)
- OR26 → AR22 (Durable backend atomic writes)
- OR34 → AR23 (Universal Tracing Mandate)
- OR35 → AR24 (Correlation ID propagation)
- OR37 → AR25 (Logs panel SSE consumption)
- OR38 → AR26 (databases/ and services/ package structure)
- OR39 → AR27 (ServiceProvider/DatabaseProvider interface contract)
- OR40 → AR28 (Models/Hardware panel capability API)
- OR41 → AR29 (Adapter routing_priority)
- OR42 → AR30 (Diagnostic harness testing strategy)
- OR43 → AR31 (TUI architecture requirement)

S2.2: Renumber all rules numerically (AR1-AR30, OR1-OR25).

S2.3: Commit: git add -A && git commit -m "docs: reclassify 18 OR→AR rules, renumber numerically"

## S3 — Remove Speculative Architecture

S3.1: Remove AR9 ("Managers temporary by default (per-task). Workers always fine-tuned specialists") — violates P5 ("Wire as you go. No speculative contracts").

S3.2: Renumber remaining rules (AR1-AR29, OR1-OR25).

S3.3: Commit: git add -A && git commit -m "docs: remove AR9 speculative architecture rule"

## S4 — Remove [Mandatory] Tags

S4.1: Remove [Mandatory] tags from all rules (redundant noise, all rules are expected to be followed).

S4.2: Commit: git add -A && git commit -m "docs: remove [Mandatory] tags from AGENTS.md"

## S5 — Fix OR5 Specificity

S5.1: Update OR5 to specify it applies to CHANGELOG.md and LANDMINES.md: "CHANGELOG.md and LANDMINES.md append-only. Never insert at top or edit existing entries."

S5.2: Commit: git add -A && git commit -m "docs: specify OR5 applies to CHANGELOG.md and LANDMINES.md"

## S6 — Create LANDMINES-ARCHIVE.md

S6.1: Create `archive/LANDMINES-ARCHIVE.md` with 35 historical landmines graduated to rules that were removed. Copy verbatim from LANDMINES.md.

S6.2: Header: `# LANDMINES-ARCHIVE.md — Historical Landmines\n## Never read routinely. Consult only for audit/investigation.`

S6.3: Update all rule number references in LANDMINES-ARCHIVE.md to match new numbering.

S6.4: Commit: git add -A && git commit -m "docs: create archive/LANDMINES-ARCHIVE.md with historical landmines"

## S7 — Purge LANDMINES.md

S7.1: Remove 35 landmines from LANDMINES.md (graduated to removed rules). Keep 18 active landmines.

S7.2: Update all rule number references in LANDMINES.md to match new numbering.

S7.3: Commit: git add -A && git commit -m "docs: purge LANDMINES.md to 18 active landmines"

## S8 — Verify

S8.1: wc -c AGENTS.md LANDMINES.md archive/LANDMINES-ARCHIVE.md — log counts.

S8.2: Verify AGENTS.md < 10,000 chars.

S8.3: Verify all rules align with principles.md.

S8.4: Verify no rule contradictions.

## S9 — Closing

S9.1: Run /close.
