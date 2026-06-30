# Session Context — Plans 16-19 (New Conversation)

## Where we are

- **Repo**: https://github.com/AngusKingCAI/SovereignAI · Branch: `main`
- **Latest commit**: `a27b38b` — "Add execution log for prompt cleanup"
- **Baseline**: `prompt-15.1` (clean core, 62 tests passing, ~91% coverage)
- **What's done**: Devin ran the cleanup prompt (removed docstrings + OR refs from source code). Workflow files need to be committed.

## What needs to happen next

1. **Commit the rev15 workflow files** to the repo (AGENTS, AI_HANDOFF, LANDMINES, open, close, scan, verify, principles.md)
2. **Devin runs the remaining cleanup tasks** from `devin-prompt-cleanup.md` (PLANS.md fixes, DEBT.md fixes, DECISIONS.md D6+D7, CHANGELOG disclaimer, principles.md creation, vision→principles references)
3. **Draft Plans 16-19** using the new 120-line format
4. **Round table** each plan (structured, evidence-based, runs until clean pass)
5. **Execute** each plan sequentially

## Current workflow files (at /home/z/my-project/download/)

- `AGENTS-rev15.md` — 65 OR + 17 AR, flat list, no section headers, authority → principles.md
- `AI_HANDOFF-rev15.md` — 99 lines, trimmed
- `LANDMINES-rev15.md` — 46 landmines L1-L46
- `open-rev15.md` — 41 lines
- `close-rev15.md` — 88 lines, verify-before-commit, mechanical spec-match only
- `scan-rev15.md` — 42 lines, cross-reference check at step 5.5
- `verify-rev15.md` — 21 lines
- `principles.md` — 32 lines, living authority document (replaces 460-line vision)
- `devin-prompt-cleanup.md` — 218 lines, remaining repo-side cleanup tasks

## Key decisions made (this session)

1. **Reverted to prompt-15.1** — 18.x saga was too messy, clean rebuild
2. **Renumbered all rules** — OR1-OR65, AR1-AR17, L1-L46, zero gaps
3. **Purged 47 redundant rules** — implementation details → DECISIONS.md, Architect process → AI_HANDOFF only
4. **AR17 flipped** — docstrings now PROHIBITED (were mandatory). Ruff D103 disabled.
5. **No OR references in source code** — governance is Devin's workflow, not SovereignAI's code
6. **No LLM dependency in governance** — spec_match.py is mechanical-only, no Claude layer
7. **principles.md** replaces project-vision-Rev5.md as authority (32 lines vs 460)
8. **Coverage floor: 90%** (was 89%)
9. **120-line plan cap** — confirmed sufficient, all historical plans would fit
10. **Round table**: runs until clean pass, each rev brings new evidence, no 10-rev loop
11. **P5 fix**: databases/ and services/ will be root-level packages (not inside sovereignai/), core provides registries only
12. **P4 minimum viable local**: 2 adapters (Ollama + llama.cpp). P6/P10/P14 deferred.
13. **Logs as 10th sidebar tab** — user's explicit decision
14. **Models panel**: 4-level dropdown, tok/s computed at runtime from detected hardware, VRAM badges, empty-DB "not populated" state
15. **Options panel**: 3 tabs (Model Services / Model Databases / Authentication), 3-button rows per provider
16. **Hardware panel**: Task Manager style, multi-GPU detection (IGPU + DGPU), live graphs

## Plans 16-19 overview

### Plan 16 — Foundation + Governance Rules + Logs Panel
- Add OR66+ rules to AGENTS.md as needed
- check_tracing.py + check_placeholders.py AR check scripts
- Correlation ID propagation in trace_emitter.py
- Logs panel as 10th sidebar item
- Mechanical enforcement in close.md (grep, spec_match.py)
- No new features beyond Logs panel

### Plan 17 — Provider Framework + HF Database + Ollama Service
- Root-level databases/ and services/ packages (P5 compliant)
- DatabaseRegistry + ServiceRegistry in core
- Three-tab Options (Model Services / Model Databases / Authentication)
- Three-button rows (Download/Update/Uninstall) per provider
- HF database with real scraper (cherry-pick from prompt-18.3)
- Ollama service with pre-flight start check
- All endpoints emit success traces

### Plan 18 — Models Panel + Hardware Panel + Tok/s + VRAM Badges
- 4-level dropdown (DB → file type → Org → Family → Model version → quant variants)
- Sortable columns (default alphabetical)
- HF category badges
- Filters (search, category, VRAM fit, quant level)
- Runtime tok/s from detected hardware (bandwidth ÷ active bytes × 0.65)
- VRAM badges (VRAM / VRAM+RAM / Diskspace / N/A)
- Empty-DB "not populated" state
- Hardware panel: CPU/RAM/GPU/Disk graphs, multi-GPU detection, live SSE sampling

### Plan 19 — llama.cpp Adapter (P4 Minimum Viable Local)
- adapters/external/llama_cpp_adapter/
- Hardware-aware model loading (VRAM detection from Plan 18)
- Routing preference + failover between Ollama and llama.cpp
- First-run experience: functional if either adapter installed
- P4 compliance verification
- Vision compliance scorecard in close report

## Dependency chain

```
Plan 16 (foundation) → Plan 17 (providers) → Plan 18 (UI) → Plan 19 (llama.cpp)
```

Each plan depends on the previous. No parallelism.

## Token budget per plan (new workflow)

- Governance overhead: ~7,400 tokens (AGENTS + AI_HANDOFF + workflow files)
- Plan file: ~1,500 tokens (120 lines)
- Source code: ~30,000 tokens (10 files)
- Test output: ~10,000 tokens
- Devin reasoning: ~20,000 tokens
- **Total per plan: ~69,000 tokens (35% of 200K context)**
- Context rot risk: minimal (starts at 70-80% utilization)

## Old draft plans (at /home/z/my-project/download/)

These were written for the OLD workflow. Use as reference for content, but rewrite in the new 120-line format:
- `plan-16-Rev1.md` — old draft
- `plan-17-Rev1.md` — old draft
- `plan-18-Rev1.md` — old draft
- `plan-19-Rev1.md` — old draft
- `plan-16-19-batch-Rev1-context-brief.md` — old batch brief
- `plan-16-19-batch-Rev1-roundtable-prompt.md` — old roundtable prompt

## Instructions for new conversation

1. Read this document first
2. Read the rev15 workflow files to understand current format
3. Draft Plans 16-19 in the new 120-line format (executable steps only, OR refs by number, no STOP conditions inline, no appendices)
4. Draft a batch context brief (≤80 lines)
5. Draft a roundtable prompt (≤60 lines)
6. User sends to round table (6 AIs, structured output)
7. Architect incorporates findings → Rev2
8. User sends to Devin one plan at a time
