# Plan 0 — Prompt-0 Remediation (Bootstrap Fix-Up)

**Special plan**: Pre-Plan 1 cleanup. Fixes the incomplete prompt-0 bootstrap state so Plans 1–4 can proceed cleanly.

Depends on: none
Vision principles: none (bootstrap governance scaffolding — no architectural impact)
Open questions resolved: Q32 (partial — DEBT.md scaffold created; full format/trigger definitions deferred to Plan 1)

---

## Adjudication Log (Rev2 → Rev3)

Per GR4. Rev3 does not get a new context brief — the Round Table reviews this revised file directly. 6 panelist responses were received (gpt-5.4-mini, Gemini-3.5-Flash, meta/llama4, qwen3.7-plus, moonshot/kimi-k2.7-code, DeepSeek v3.2). 10 unique findings were accepted; the rest were rejected as duplicates, factual errors, or speculative. The Round Table should focus on any *remaining* issues, not re-litigate these.

### Finding 1 — pip-audit invocation ambiguity (Qwen M1 / Kimi H1 — convergent)
**Severity**: HIGH (upgraded from MEDIUM)
**Reasoning**: OR39 said `pip-audit --strict` (scans environment) but Closing section said "0 CVEs expected (txt/requirements.txt is empty)." After `pip install -e .[dev]`, the environment contains dev tools that may have CVEs → `/close` step 5 says "If CVEs, STOP" → bootstrap blocks.
**Action**: ACCEPTED. OR39 text updated to `pip-audit --strict --requirement txt/requirements.txt` (scans requirements file only). Closing section's pip-audit expected result updated to reflect requirements-file scan.

### Finding 2 — LANDMINES.md header claims L1–L23 but only 12 entries documented (Qwen M2 / Kimi M1 / DeepSeek M5 — convergent)
**Severity**: MEDIUM
**Reasoning**: AGENTS.md's landmine-to-rule table references L1–L9, L11, L12, L17 only (12 entries). Header said "L1–L23 inherited" — inaccurate.
**Action**: ACCEPTED. Header changed to "Selected landmines (L1–L9, L11, L12, L17) inherited from sovereign-ai predecessor. New landmines for SovereignAI start at L24."

### Finding 3 — S6 and S8 both edit PLANS.md with unclear separation (Qwen L1)
**Severity**: LOW
**Reasoning**: S6 says "verify prompt-0 row present and accurate"; S8 says "mark prompt-0 as complete." Ambiguous whether they overlap.
**Action**: ACCEPTED. S6 clarified as verification-only + date update. S8 clarified as the substantive state change (active plan update). Both happen before S7's commit (see Finding 9).

### Finding 4 — detect-secrets baseline will contain false positives (Qwen L2)
**Severity**: LOW
**Reasoning**: `detect-secrets scan --all-files` scans governance docs which contain strings like "MIT" license text, example API keys in landmine descriptions.
**Action**: ACCEPTED. S3.5 updated to include a `detect-secrets audit txt/.secrets.baseline` step after the scan, with explicit guidance on reviewing false positives.

### Finding 5 — txt/requirements.txt format may be non-standard (Qwen L3)
**Severity**: LOW
**Reasoning**: File content had no explicit trailing newline. POSIX text file standards require a trailing newline.
**Action**: ACCEPTED. Trailing newline added to file content. Comment block in file also fixed ("sovereignignai/" typo → "sovereignai/").

### Finding 6 — Missing README.md blocks the build (Kimi H1)
**Severity**: HIGH
**Reasoning**: `pyproject.toml` declares `readme = "README.md"` but no README.md exists in the repo or in Rev2's "Files WILL Create" list. `pip install -e .[dev]` would error with "readme file not found: README.md" at S3.5.
**Action**: ACCEPTED. Minimal README.md added to S4 (new S4.1 step). File listed in "Files WILL Create".

### Finding 7 — S5 instruction to rewrite "What changed since Rev 3" paragraph risks editing locked content (Kimi M2)
**Severity**: MEDIUM
**Reasoning**: S5's vague instruction to "change 'Rev 4' prefix references to 'Rev 5' where they describe what's locked" could lead the Executor to mutate substantive content in the locked vision document.
**Action**: ACCEPTED. S5 restricted to three metadata-only edits: (a) H1 title change, (b) status block update (append-only), (c) append-only Rev 5 history entry. The "What changed since Rev 3" paragraph is NOT edited.

### Finding 8 — Bandit pre-commit hook not explicitly wired to its config (Kimi M3)
**Severity**: MEDIUM
**Reasoning**: `.pre-commit-config.yaml` had `args: ["-r", ".", "-ll"]` for bandit with no explicit `-c pyproject.toml`. Bandit's auto-discovery of pyproject.toml config is version-dependent. Hook may scan `.venv/`, `.git/`, etc.
**Action**: ACCEPTED. Bandit hook args updated to include explicit exclusions: `args: ["-r", ".", "-ll", "-x", ".venv,venv,env,.git,node_modules,__pycache__,build,dist,.tox,.eggs,.pytest_cache,.mypy_cache,.ruff_cache"]`.

### Finding 9 — prompt-0 tag pushed before final PLANS.md update (Kimi M4 / DeepSeek CRITICAL — convergent)
**Severity**: CRITICAL (per DeepSeek) / MEDIUM (per Kimi) — treated as HIGH
**Reasoning**: S7 committed, tagged, and pushed; S8 only then updated PLANS.md to mark prompt-0 complete and set Plan 1 active. Anyone checking out the `prompt-0` tag saw PLANS.md still showing prompt-0 as active.
**Action**: ACCEPTED. Step order reorganized: S6 (verify state) and S8 (update active plan) are now performed before S7's commit. Both PLANS.md edits land in the tagged commit.

### Finding 10 — No .gitignore (Kimi M5)
**Severity**: MEDIUM
**Reasoning**: `pip install -e .[dev]` creates `sovereignai.egg-info/`, possibly `.venv/`. `git add -A` would stage these. `detect-secrets scan --all-files` may include them in the baseline.
**Action**: ACCEPTED. `.gitignore` added to S4. Covers: `.venv/`, `*.egg-info/`, `build/`, `dist/`, `.pytest_cache/`, `.mypy_cache/`, `.ruff_cache/`, `htmlcov/`, `__pycache__/`.

### Rejected findings (notable)

- **Gemini HIGH** ("[tool.setuptools.dynamic] missing"): Block IS in S3.1 pyproject.toml. Gemini missed it on reading.
- **Gemini MEDIUM** ("txt/ directory missing from S5"): Directory created implicitly when files written into it.
- **Llama4 CRITICAL/HIGH/MEDIUM findings**: All speculative, no concrete failure scenarios.
- **DeepSeek HIGH #2** ("no pip install step"): S3.5 already contains `pip install -e .[dev]`. DeepSeek appears to have read Rev1, not Rev2.
- **DeepSeek HIGH #3** ("dynamic deps untested for wheel builds"): Partially accepted as a note in S3.1 — no real deps exist at bootstrap to verify. Plan 1's first runtime dep should include a `python -m build --wheel` verification step.
- **DeepSeek M5** ("inherited landmine placeholders"): Dup of Finding 2. Alternative proposal (delete L1–L23) breaks AGENTS.md cross-references.
- **DeepSeek "orphaned Rev1 files in prompts/"**: Misreads the handoff workflow. Rev3 lives in /home/z/my-project/download/. User copies it to C:/SovereignAI/prompts/plan-0.md per AI_HANDOFF.md instructions. Rev1 preserved in git history.

### Verdict

Per clean-pass definition: no substantiated CRITICAL or HIGH issue remains unaddressed after Rev3. The one CRITICAL (DeepSeek, also Kimi M4) is fixed by step reordering. All other HIGHs are either accepted and fixed or factually wrong.

---

## Adjudication Log (Rev1 → Rev2)

Per GR4. Rev2 does not get a new context brief — the Round Table reviews this revised file directly. The following issues were identified in Rev1 by the Architect during pre-review alignment check against `project-vision-Rev5.md`, `AI_HANDOFF.md`, and `AGENTS.md`. The Round Table should focus on any *remaining* issues, not re-litigate these.

### Self-identified Issue 1 — S1 (.devin → .windsurf move) is stale
**Severity**: CRITICAL
**Reasoning**: The user manually fixed the path discrepancy in commit `2905452` by editing `AI_HANDOFF.md` and `PLANS.md` to reference `.devin/workflows/` (the actual directory name on disk). Executing S1 as written would move the directory back to `.windsurf/`, recreating the original discrepancy and undoing the user's fix.
**Action**: ACCEPTED. S1 removed entirely. All subsequent `.windsurf/` path references in the plan corrected to `.devin/`.

### Self-identified Issue 2 — S2 cites wrong file paths
**Severity**: HIGH
**Reasoning**: S2 said to edit `.windsurf/workflows/open.md` and `.windsurf/workflows/close.md`. Files live at `.devin/workflows/`.
**Action**: ACCEPTED. All paths corrected to `.devin/workflows/`.

### Self-identified Issue 3 — S2 incorrectly claims close.md needs master→main fix
**Severity**: HIGH
**Reasoning**: Verified via `git show origin/main:.devin/workflows/close.md | grep -nE 'master|main'` — line 143 already says `git push origin main`. Only `open.md` lines 14 and 19 need the fix.
**Action**: ACCEPTED. S2 scope reduced to `open.md` only.

### Self-identified Issue 4 — S0.1 and Closing section cite wrong workflow paths
**Severity**: HIGH
**Reasoning**: Both said `.windsurf/workflows/open.md` / `.windsurf/workflows/close.md`.
**Action**: ACCEPTED. Corrected to `.devin/workflows/`.

### Self-identified Issue 5 — S3.2 LANDMINES.md content is fabricated
**Severity**: HIGH
**Reasoning**: Rev1 populated L1–L12 + L17 with concrete fabricated triggers ("Trigger: Plan 1, S2, using `replace_all` on `AGENTS.md`..."). None of these events have happened in SovereignAI — they're inherited from the sovereign-ai predecessor. AGENTS.md says: "Keep entries concise — trigger and impact only. No narrative." Inherited landmines should clearly state they are inherited, with SovereignAI-specific trigger TBD.
**Action**: ACCEPTED. S2.2 LANDMINES.md content rewritten as inherited-pattern placeholders with honest "Inherited from sovereign-ai predecessor. SovereignAI-specific trigger TBD." language.

### Self-identified Issue 6 — S3.3 DECISIONS.md invents D2 (dependency-injector)
**Severity**: HIGH
**Reasoning**: D1 (Python) and D3 (Windows-only) are locked in the vision (Q10, P4) — defensible as ADR records. D2 (dependency-injector) is named in AR4 but the options/rationale were never separately debated in a Round Table or user decision session. Recording it as a full ADR with fabricated "Options considered" is dishonest.
**Action**: PARTIALLY ACCEPTED. D2 retained but reframed: it points to AR4 as the source of the choice, with an explicit note that options/rationale weren't separately debated and the entry should be expanded if Plan 1+ implementation reveals issues.

### Self-identified Issue 7 — Vision principles claim is a stretch
**Severity**: MEDIUM
**Reasoning**: Rev1 header said `Vision principles: 1 (sacred core), 2 (pluggable), 5 (wire as you go), 7 (modular core)`. Plan 0 is mechanical governance scaffolding — it doesn't *satisfy* any principle, it creates conditions for future plans to satisfy them. Claiming principle satisfaction for a docs-only plan inflates the plan's architectural weight.
**Action**: ACCEPTED. Header changed to `Vision principles: none (bootstrap governance scaffolding — no architectural impact)`.

### Self-identified Issue 8 — Q32 resolution is premature
**Severity**: MEDIUM
**Reasoning**: Rev1 said `Open questions resolved: Q32 (debt register format — DEBT.md scaffold)`. Plan 0 creates the DEBT.md file but doesn't define maintenance responsibilities, trigger conditions, or full format — those are deferred.
**Action**: ACCEPTED. Header changed to `Open questions resolved: Q32 (partial — DEBT.md scaffold created; full format/trigger definitions deferred to Plan 1)`.

### Self-identified Issue 9 — P1/P8 violation in S5 directory structure
**Severity**: CRITICAL
**Reasoning**: S5 nested UI code inside the core package: `sovereignai/web/`, `sovereignai/cli/`, `sovereignai/tui/`, `sovereignai/phone/`. P1 + Core Scope (v1) explicitly list UIs as **outside** the core. P8: "UIs are separate processes... The web UI, TUI, CLI, and phone app each run as independent processes that connect to the core via a local socket." AR7 reinforces: "UI processes may not import from `orchestrator/`, `managers/`, `workers/`, etc. directly." S5 also created `sovereignai/panels/` — "panels" is a UI concept (Panel 1–9), not a core concept. The 12-item Core Scope list has no `panels/` entry.
**Action**: ACCEPTED. S4 directory structure reorganized: UIs (`web/`, `cli/`, `tui/`, `phone/`) moved to top-level peer directories. `sovereignai/panels/` removed entirely. `adapters/external/`, `skills/user/`, `skills/external/` added (required by AR20 and Q30 provenance directory split).

### Self-identified Issue 10 — P5 (wire as you go) partial violation in S4
**Severity**: MEDIUM
**Reasoning**: S4 created `pyproject.toml` with full `[tool.ruff]`, `[tool.mypy]`, `[tool.bandit]`, `[tool.vulture]` config before any Python code exists. P5 says "no speculative contracts for hypothetical future modalities." Tool config is a contract with the codebase — line-length 100, ruff rule set, mypy strictness — these are guesses. S4.3 also fabricated `txt/vulture-whitelist.txt` with entry `fixture_param` — no such fixture exists.
**Action**: PARTIALLY ACCEPTED. Tool config retained (the workflow files reference these tools, so the config must exist for `/close` to run), but explicitly marked "TENTATIVE — will be tuned as code emerges in Plans 1+". Vulture whitelist emptied (header comment only, no fabricated entries). Ruff D100/D104 exclusions documented with reason.

### Self-identified Issue 11 — Rev5 byte-identical to Rev4 (item 4 from previous review)
**Severity**: MEDIUM
**Reasoning**: `md5sum` confirms `documents/project-vision-Rev5.md` is byte-identical to `documents/project-vision-Rev4.md`. The H1 title still says "Rev 4" and the revision history stops at Rev 4. The Rev4 brief said: "If clean pass: draft plan-1. If not clean pass: produce Rev5 and re-submit." Either Rev4 got a clean pass (in which case Rev5 shouldn't exist as a separate file) or Rev5 was supposed to incorporate feedback but the changes weren't applied.
**Action**: ACCEPTED. New S5 added to fix Rev5's H1 title and append a Rev5 revision-history entry noting it's the locked canonical version (no content changes from Rev4 — Rev4 received clean-pass #3 from the Round Table).

### Self-identified Issue 12 — `.secrets.baseline` creation underspecified
**Severity**: LOW
**Reasoning**: Rev1 said "create a minimal baseline file" without specifying JSON shape. Hand-written JSON might not match the installed detect-secrets version's format.
**Action**: ACCEPTED. S3.5 now says: install dev deps first (`pip install -e .[dev]`), then generate baseline via `detect-secrets scan --all-files > txt/.secrets.baseline`. No hand-written JSON.

### User-directed addition — `txt/requirements.txt` + OR39
**Severity**: N/A (user request, not a finding)
**Reasoning**: User asked: "Do we need a requirements.txt that will live in txt/? This will be updated by Devin when we add new functionality. Probably worth creating a OR for this." Architect proposed OR39 (runtime deps in `txt/requirements.txt` only, `pyproject.toml` reads via `dynamic = ["dependencies"]`, dev deps stay in `pyproject.toml`). User confirmed direction.
**Action**: ACCEPTED. S0.3 changed from "No new rules" to "Add OR39". New file `txt/requirements.txt` added to S3. `pyproject.toml` updated to use `dynamic = ["dependencies"]` instead of `[project.dependencies]`.

---

## S0 — Opening

**S0.1** — Run `/open` workflow from `.devin/workflows/open.md`. Skip previous tag verification (Plan 0 has no predecessor).

**S0.2** — Read `AGENTS.md` in full. Note that OR22's always-on subset (OR5, OR6, OR15, OR16, OR34, AR5, AR16, AR21) applies to every edit in this plan.

**S0.3** — Add OR39 to `AGENTS.md`. Commit before any other step:

Append the following rule to the Operational Rules section of `AGENTS.md`, after OR37 and before the "Landmines that have graduated to rules" section:

> OR39. Runtime dependencies live in `txt/requirements.txt` only. When a plan introduces a new runtime dependency (a package imported by production code in `sovereignai/`, `web/`, `cli/`, `tui/`, or `phone/`), the Executor appends the package name with version pin (e.g., `pydantic>=2.0`) to `txt/requirements.txt` at the plan step that introduces the import. `pyproject.toml` declares `dynamic = ["dependencies"]` and reads from `txt/requirements.txt` via `[tool.setuptools.dynamic]` — it must NOT also list runtime deps under `[project.dependencies]` (SSOT; duplicate lists drift). Dev-only tools (pytest, ruff, mypy, bandit, vulture, detect-secrets, pre-commit) live in `pyproject.toml`'s `[project.optional-dependencies] dev = [...]` — they never go in `txt/requirements.txt` because they are not installed in a production environment. After any change to `txt/requirements.txt`, run `pip install -e .[dev]` to refresh the local environment, then re-run `pip-audit --strict --requirement txt/requirements.txt` to verify the new runtime dependency has no known CVEs (scans the requirements file only — dev-tool CVEs in the environment are not in scope for this check). (Source: Plan 0 — Architect-proposed.)

Do **not** add an entry to the landmine-to-rule table at the bottom of `AGENTS.md` — OR39 is preventive, not graduated from a landmine.

Commit:
```
git add AGENTS.md
git commit -m "docs: add OR39 (runtime deps in txt/requirements.txt) for prompt-0"
```

After edit, run `/verify`.

---

## S1 — Fix Branch Name: `master` → `main`

**Problem**: `.devin/workflows/open.md` references `master` branch on lines 14 and 19, but the actual default branch is `main`.

**Fix** (use Edit tool only — OR7):
- In `.devin/workflows/open.md` line 14: change "Confirm working copy is clean and on master:" to "Confirm working copy is clean and on main:"
- In `.devin/workflows/open.md` line 19: change "If dirty (excluding governance docs/plan files) or not on master, STOP." to "If dirty (excluding governance docs/plan files) or not on main, STOP."

**Note**: `.devin/workflows/close.md` line 143 already says `git push origin main` — no change needed. Do not edit `close.md`.

After each edit, run `/verify`.

---

## S2 — Create Missing Governance Documents

Create 4 files at repo root. Content for each is provided below. Use the Edit tool with empty `old_str` to create new files (per OR7 — Edit tool only for structured markdown).

### S2.1 — `CHANGELOG.md`

```markdown
# CHANGELOG — SovereignAI

Chronological change log. Append-only. Oldest entry at top, newest at bottom.

---

## prompt-0 — Bootstrap: Governance docs and infrastructure

**Date**: 2026-06-28
**Plan file**: prompts/plan-0-Rev3.md

**Files changed**:
- AGENTS.md (added OR39)
- .devin/workflows/open.md (fixed master -> main)
- documents/project-vision-Rev5.md (fixed title + revision history — metadata only)
- PLANS.md (state update: prompt-0 complete, Plan 1 active)
- README.md (new, minimal)
- .gitignore (new)
- CHANGELOG.md (new)
- LANDMINES.md (new)
- DECISIONS.md (new)
- DEBT.md (new)
- pyproject.toml (new)
- txt/requirements.txt (new, empty with header comment)
- .pre-commit-config.yaml (new)
- txt/vulture-whitelist.txt (new, empty)
- txt/.secrets.baseline (new, generated)
- Directory structure: sovereignai/ + UI peers + adapters/external + skills/user + skills/external

**Results**:
- Tests: N/A (no code)
- Ruff: N/A (no Python code yet)
- Mypy: N/A (no Python code yet)
- Bandit: N/A (no Python code yet)
- pip-audit: 0 CVEs (scanned txt/requirements.txt only — empty file, no runtime deps)
- Vulture: N/A (no Python code yet)
- Detect-secrets: pass (baseline established and audited)

**Notes**:
- Bootstrap commit establishing 12-document governance set + infrastructure scaffolding.
- No code, no tests. Architecture and process documentation only.
- AR4's `dependency-injector` reference recorded in DECISIONS.md D2 as pending separate debate.
- Rev5 title fixed (was byte-identical to Rev4).
```

### S2.2 — `LANDMINES.md`

```markdown
# LANDMINES.md — SovereignAI Failure Patterns

Append-only. Selected landmines (L1–L9, L11, L12, L17) inherited from sovereign-ai (predecessor project) — these are the entries referenced in `AGENTS.md`'s landmine-to-rule table. L10, L13–L16, L18–L23 were not graduated to rules in SovereignAI and are not carried forward. New landmines for SovereignAI start at L24.

Entries below are placeholder records for the inherited landmines referenced in `AGENTS.md`'s landmine-to-rule table. Each entry records the inherited trigger pattern and impact; SovereignAI-specific triggers will be appended as they occur. Per AGENTS.md: "Keep entries concise — trigger and impact only. No narrative."

---

## L1 — replace_all corrupts adjacent lines
**Trigger**: Inherited from sovereign-ai predecessor. Specific SovereignAI trigger TBD.
**Impact**: `AGENTS.md` or other structured markdown becomes structurally invalid. Requires manual restoration from git.
**Graduated to**: OR5.

## L2 — Parallel scan tools corrupt output streams
**Trigger**: Inherited from sovereign-ai predecessor. Specific SovereignAI trigger TBD.
**Impact**: Output streams from pytest/ruff/mypy/bandit/pip-audit/vulture interleave when run in parallel, producing unreadable output. Requires re-running all tools sequentially.
**Graduated to**: OR3.

## L3 — PowerShell -replace corrupts structured markdown
**Trigger**: Inherited from sovereign-ai predecessor. Specific SovereignAI trigger TBD (SovereignAI uses Git Bash per OR1, so this should not recur — retained for diagnostic context).
**Impact**: Markdown table formatting destroyed when edited with PowerShell `Set-Content` + `-replace`.
**Graduated to**: OR7.

## L4 — Temp files left in repo root get committed
**Trigger**: Inherited from sovereign-ai predecessor. Specific SovereignAI trigger TBD.
**Impact**: Temp file committed to repo. Requires follow-up commit to remove.
**Graduated to**: OR13, OR21.

## L5 — Vulture flags unused test fixtures incorrectly
**Trigger**: Inherited from sovereign-ai predecessor. Specific SovereignAI trigger TBD.
**Impact**: False positive. Parameter was required by pytest's parametrize decorator.
**Graduated to**: OR19.

## L6 — Naive/aware datetime mixing
**Trigger**: Inherited from sovereign-ai predecessor. Specific SovereignAI trigger TBD.
**Impact**: Type error when comparing `datetime.utcnow()` with `datetime.now(timezone.utc)`. Mypy flagged the mismatch.
**Graduated to**: OR20.

## L7 — Stale baselines propagate through plans
**Trigger**: Inherited from sovereign-ai predecessor. Specific SovereignAI trigger TBD.
**Impact**: Baseline drift. Subsequent plan starts with wrong expected test count, causing false STOP.
**Graduated to**: OR17.

## L8 — Scope drift: editing files outside declared scope
**Trigger**: Inherited from sovereign-ai predecessor. Specific SovereignAI trigger TBD.
**Impact**: Unplanned changes in commit. Difficult to trace which plan produced which change.
**Graduated to**: OR16, OR22.

## L9 — Interface changes break existing tests during type remediation
**Trigger**: Inherited from sovereign-ai predecessor. Specific SovereignAI trigger TBD.
**Impact**: Tests failed. Required either test updates (out of scope) or compatibility shim.
**Graduated to**: OR27.

## L11 — Bypassed pre-commit hooks with --no-verify
**Trigger**: Inherited from sovereign-ai predecessor. Specific SovereignAI trigger TBD.
**Impact**: Committed code with known style violation. Required follow-up fix.
**Graduated to**: OR32.

## L12 — Hiding type errors by excluding files from hooks
**Trigger**: Inherited from sovereign-ai predecessor. Specific SovereignAI trigger TBD.
**Impact**: Type error hidden permanently. File never type-checked again.
**Graduated to**: OR33.

## L17 — Plan steps executed/marked complete out of order
**Trigger**: Inherited from sovereign-ai predecessor. Specific SovereignAI trigger TBD.
**Impact**: Step marked complete based on work done in a different section. Required replan.
**Graduated to**: OR34.

---

## Process for capturing new landmines (L24+)

At `/close` step 11, if a new failure pattern was discovered during the plan, append an entry in this format:

```markdown
## L{n} — <one-line title of the failure pattern>

**Trigger**: <Plan #, step, specific command/file/context — be concrete>
**Impact**: <What broke as a result>
```

Keep entries concise — trigger and impact only. No narrative, no cross-references to other plans. No proposed fixes or rules — those come from the Architect via `AGENTS.md`.
```

### S2.3 — `DECISIONS.md`

```markdown
# DECISIONS.md — SovereignAI Architectural Decisions Record

Append-only. Each entry: context, options considered, decision, rationale, trade-offs, status.

---

## D1 — Python for v1, Rust migration deferred

**Context**: Language choice for initial implementation (vision open question Q10).
**Options considered**: A) Python for v1, migrate to Rust later; B) Rust from day one; C) Hybrid — core in Rust, adapters in Python.
**Decision**: Option A — Python for v1.
**Rationale**: Speed of iteration for a single developer. Python's ecosystem (pydantic, pytest, ruff, mypy) provides mature tooling. Contracts are language-agnostic; future Rust rewrite is not precluded.
**Trade-offs**: Slower runtime, higher memory usage, GIL limits parallelism. Acceptable for v1 single-user local-first target.
**Status**: Active. Revisit after Plan 20+.
**Source**: `project-vision-Rev5.md` Q10 (resolved).

---

## D2 — `dependency-injector` as the DI container library

**Context**: AR4 requires a DI container and names `dependency-injector` specifically.
**Options considered**: Not separately debated. The choice was made during AR4 drafting and encoded directly in the rule text.
**Decision**: `dependency-injector` (per AR4).
**Rationale**: AR4 asserts this library meets the DI-managed singleton (Orchestrator, Librarian Registry) and factory (Managers, Workers) requirements. Full options/rationale not separately debated — this ADR records that gap.
**Trade-offs**: External dependency. If abandoned, manual DI is the fallback. If Plan 1+ implementation reveals issues, this entry should be expanded with the options/rationale and re-submitted to the Round Table.
**Status**: Active, pending separate debate. Revisit at Plan 1 if implementation surfaces friction.
**Source**: `AGENTS.md` AR4.

---

## D3 — Windows-only for v1

**Context**: Platform target (vision principle P4).
**Options considered**: A) Windows-only v1, cross-platform later; B) Cross-platform from day one.
**Decision**: Option A — Windows-only for v1.
**Rationale**: Single developer on Windows. Reduces complexity. Architecture must not foreclose cross-platform support.
**Trade-offs**: Linux/macOS users cannot run v1. Path handling uses forward slashes (Windows accepts both).
**Status**: Active. Revisit for packaging plan (Q31).
**Source**: `project-vision-Rev5.md` P4, Q31 (open).

---

## How to add a new decision

At `/close` step (when a decision is codified), append an entry in the format above. Do not edit or remove existing entries — DECISIONS.md is append-only.
```

### S2.4 — `DEBT.md`

```markdown
# DEBT.md — SovereignAI Deferred Items Register

Append-only. Each entry: deferred at, reason, trigger condition, target plan.

---

## Deferred: Security Guard implementation

**Deferred at**: prompt-0 (bootstrap)
**Reason**: Security Guard is not pertinent to the core yet. It will be implemented as a Worker later, not as core infrastructure. Per AGENTS.md AR10–12 deferral note.
**Trigger condition**: When Worker lifecycle and skill authoring are stable (post Plan 4).
**Target plan**: TBD (post Plan 4).

---

## Deferred: Cross-platform packaging

**Deferred at**: prompt-0 (bootstrap)
**Reason**: v1 is Windows-only per P4. Cross-platform packaging adds complexity not needed for initial validation.
**Trigger condition**: When core is stable and Windows packaging is working.
**Target plan**: Q31 (post Plan 4).

---

## Deferred: Model loading/unloading based on hardware

**Deferred at**: prompt-0 (bootstrap)
**Reason**: VRAM management, GPU detection, and dynamic model loading are advanced features. Core needs to exist first. Per `project-vision-Rev5.md` Models section: "Model loading/unloading based on system hardware is a planned feature for a later plan, not Plan 1."
**Trigger condition**: When local model adapters (Ollama, llama.cpp) are wired and working.
**Target plan**: TBD (post Plan 4).

---

## Deferred: Self-correction / learning loops

**Deferred at**: prompt-0 (bootstrap)
**Reason**: Learning and improvement (Q13) is a skill-level concern, not core. The retrospective trace skill will be built once the skill framework exists.
**Trigger condition**: When skill framework (Plan 2+) is stable.
**Target plan**: TBD (post Plan 4).

---

## Deferred: Relay server E2EE implementation

**Deferred at**: prompt-0 (bootstrap, per Plan 1–4 scope adjudication A4)
**Reason**: Plan 4 ships a local-only relay placeholder that returns a structured error and does not accept connections. Full E2EE implementation deferred to a dedicated plan post-batch.
**Trigger condition**: When Plan 4's placeholder is merged and the local UI stack is functional.
**Target plan**: TBD (post Plan 4, dedicated plan).

---

## Deferred: Durable persistence backends and crash recovery

**Deferred at**: prompt-0 (bootstrap, per Plan 1–4 scope adjudication A7)
**Reason**: Plan 3 implements the event-store interface and in-memory replay only. Durable backends and full crash recovery are too much for Plan 3 alongside four other components.
**Trigger condition**: When Plan 3's in-memory event store is stable.
**Target plan**: TBD (post Plan 3).

---

## Deferred: Full Q8 versioning / capability negotiation

**Deferred at**: prompt-0 (bootstrap, per Plan 1–4 scope adjudication)
**Reason**: Plan 2 ships Q8 MVP only. Full versioning/capability negotiation deferred.
**Trigger condition**: When Plan 2's manifest schema is stable and a second adapter version is needed.
**Target plan**: TBD (post Plan 2).

---

## How to add a new deferred item

At `/close` step 12, if an item is deferred, append an entry in the format above. When a deferred item is addressed, do not remove the entry — add a "Resolved at: prompt-{N}" line below it. DEBT.md is append-only.
```

After creating each file, run `/verify`.

---

## S3 — Create Infrastructure Files

### S3.1 — `pyproject.toml`

```toml
[build-system]
requires = ["setuptools>=61.0", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "sovereignai"
version = "0.1.0"
description = "Local-first, modular AI assistant framework"
readme = "README.md"
requires-python = ">=3.11"
license = {text = "MIT"}
authors = [{name = "AngusKingCAI"}]
# Runtime deps live in txt/requirements.txt (SSOT per OR39).
# Do NOT add [project.dependencies] — that would duplicate and drift.
dynamic = ["dependencies"]

[tool.setuptools.dynamic]
dependencies = {file = ["txt/requirements.txt"]}

[tool.setuptools.packages.find]
# Only sovereignai/ is an installable package.
# UIs (web/, cli/, tui/, phone/) are separate processes — NOT installable as part of the core.
include = ["sovereignai*"]
exclude = ["tests*", "web*", "cli*", "tui*", "phone*", "documents*", "prompts*", "logs*", "txt*"]

[project.optional-dependencies]
# Dev-only tools — never installed in production. Per OR39.
dev = [
    "pytest>=7.0",
    "pytest-cov>=4.0",
    "ruff>=0.4.0",
    "mypy>=1.0",
    "bandit>=1.7",
    "pip-audit>=2.0",
    "vulture>=2.0",
    "detect-secrets>=1.0",
    "pre-commit>=3.0",
]

# ============================================================================
# Tool configuration below is TENTATIVE per P5 (wire as you go).
# These settings are best-effort guesses for an empty codebase. They WILL be
# tuned as Python code emerges in Plans 1+. Any /close that produces the first
# real Python file should revisit these settings.
# ============================================================================

[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py", "*_test.py"]
python_classes = ["Test*"]
python_functions = ["test_*"]
addopts = "-vvv"

[tool.ruff]
line-length = 100
target-version = "py311"

[tool.ruff.lint]
select = ["E", "F", "W", "D", "I", "N", "UP", "B", "C4", "SIM"]
# D100 (missing module docstring) and D104 (missing package docstring) are
# excluded because empty __init__.py files in the scaffold don't need
# docstrings yet. AR21 covers def/async def docstrings (D103) — that's the
# enforced rule. Revisit at Plan 1 when __init__.py files get content.
ignore = ["D100", "D104"]

[tool.ruff.pydocstyle]
convention = "google"

[tool.mypy]
python_version = "3.11"
warn_return_any = true
warn_unused_configs = true
disallow_untyped_defs = true
ignore_missing_imports = true

[tool.bandit]
exclude_dirs = [".venv", "venv", "env", ".git", "node_modules", "__pycache__", "build", "dist", ".tox", ".eggs", ".pytest_cache"]

[tool.vulture]
min_confidence = 80
exclude = [".venv", "venv", "env", ".git", "node_modules", "__pycache__", "build", "dist", ".tox", ".eggs", ".pytest_cache", ".mypy_cache", ".ruff_cache", "htmlcov"]
```

### S3.2 — `txt/requirements.txt`

```
# SovereignAI runtime dependencies
#
# This file is the SSOT for runtime deps (per AGENTS.md OR39).
# pyproject.toml reads it via dynamic = ["dependencies"].
#
# Append package>=version when adding a new import to production code in
# sovereignai/, web/, cli/, tui/, or phone/.
#
# Dev-only tools (pytest, ruff, mypy, etc.) go in pyproject.toml's
# [project.optional-dependencies] dev = [...] — NOT here.
#
# After any change, run: pip install -e .[dev] && pip-audit --strict --requirement txt/requirements.txt

```

(File starts empty — no runtime deps yet. Trailing newline included per POSIX text file standard. First entry will be added in Plan 1 when the first import lands.)

### S3.3 — `.pre-commit-config.yaml`

```yaml
repos:
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.4.0
    hooks:
      - id: ruff
        args: [--fix]
      - id: ruff-format

  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.10.0
    hooks:
      - id: mypy
        additional_dependencies: [types-all]

  - repo: https://github.com/PyCQA/bandit
    rev: 1.7.8
    hooks:
      - id: bandit
        # Explicit exclusions rather than relying on [tool.bandit] auto-discovery
        # (version-dependent). Per Kimi M3 Round Table finding.
        args: ["-r", ".", "-ll", "-x", ".venv,venv,env,.git,node_modules,__pycache__,build,dist,.tox,.eggs,.pytest_cache,.mypy_cache,.ruff_cache,htmlcov"]

  - repo: https://github.com/Yelp/detect-secrets
    rev: v1.5.0
    hooks:
      - id: detect-secrets
        args: ['--baseline', 'txt/.secrets.baseline']
```

### S3.4 — `txt/vulture-whitelist.txt`

```
# Vulture whitelist — SovereignAI
#
# Add symbols here that vulture falsely flags as unused.
# Format: symbol_name  # reason
#
# Per OR19: pytest fixture parameters flagged by vulture may be required by
# the parametrize decorator — verify before removing.
#
# File starts empty. First entry will be added when vulture reports its first
# false positive in Plan 1+.
```

After creating each file in S3.1–S3.4, run `/verify`.

---

## S4 — Create Directory Structure and Root Files

### S4.1 — `README.md`

Create a minimal README at repo root. Required because `pyproject.toml` declares `readme = "README.md"` — `pip install -e .[dev]` will fail without it (per Kimi H1 Round Table finding).

```markdown
# SovereignAI

Local-first, modular AI assistant framework. Built for a single user. Designed to absorb whatever models, adapters, skills, and memory paradigms arrive over the next decade without forcing rewrites.

## Status

Pre-Plan 1 (bootstrap). No code yet — governance docs and infrastructure only.

## Documentation

- `AI_HANDOFF.md` — Architect process guide
- `AGENTS.md` — Executor always-on rules
- `PLANS.md` — current project state
- `documents/project-vision-Rev5.md` — canonical vision (locked)
- `documents/SovereignAI_Architecture_Decisions.md` — architecture sketch

## License

MIT
```

### S4.2 — `.gitignore`

Create `.gitignore` at repo root. Required because `pip install -e .[dev]` and `detect-secrets scan --all-files` would otherwise pick up editable-install artifacts and caches (per Kimi M5 Round Table finding).

```gitignore
# Python
__pycache__/
*.py[cod]
*$py.class
*.so

# Virtual environments
.venv/
venv/
env/

# Build artifacts
*.egg-info/
*.egg
build/
dist/
.eggs/

# Test / lint caches
.pytest_cache/
.mypy_cache/
.ruff_cache/
htmlcov/
.coverage
.coverage.*
.tox/

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Secrets (never commit real secrets — detect-secrets enforces this)
.env
.env.local
```

### S4.3 — Directory structure

Create empty directories with `.gitkeep` files. Do **not** create `__init__.py` files yet — Plan 1 will add them when the first Python module lands in each package.

**Core package (`sovereignai/`) — per Core Scope (v1) in `project-vision-Rev5.md`:**
```
sovereignai/.gitkeep
sovereignai/orchestrator/.gitkeep
sovereignai/managers/.gitkeep
sovereignai/workers/.gitkeep
sovereignai/librarian/.gitkeep
sovereignai/adapters/.gitkeep
sovereignai/adapters/external/.gitkeep          # per AR20, Q30
sovereignai/skills/.gitkeep
sovereignai/skills/user/.gitkeep                # per Q30 (user-authored, trusted by default)
sovereignai/skills/external/.gitkeep            # per AR20, Q30 (signed provenance required)
sovereignai/shared/.gitkeep                     # AR4: shared/container.py lives here in Plan 1
```

**UI processes (top-level peers, NOT under sovereignai/ — per P8):**
```
web/.gitkeep
cli/.gitkeep
tui/.gitkeep
phone/.gitkeep
```

**Project infrastructure:**
```
logs/.gitkeep
tests/.gitkeep
```

**Note**: `prompts/` and `txt/` already exist (this plan and S3 add files there). Do not add `.gitkeep` to non-empty directories.

**Note on `sovereignai/panels/`**: this directory is **not** created. "Panels" is a UI concept (Panel 1–9 in the architecture decisions doc), not a core concept. The 12-item Core Scope list has no `panels/` entry. UI panel code lives under `web/`, `cli/`, `tui/`, `phone/` respectively.

After creating each `.gitkeep`, run `/verify` (markdown skip per `/verify` step 1 — `.gitkeep` has no syntax to check, but the workflow still requires the report step).

### S4.4 — `txt/.secrets.baseline`

**Prerequisite**: S3.1 (`pyproject.toml`) and S4.1 (`README.md`) must be complete — `pip install -e .[dev]` requires both. S4.2 (`.gitignore`) must also be complete so editable-install artifacts are not scanned.

**Install dev dependencies** (this is the install step — pip-audit, detect-secrets, etc. all come from here):

```bash
pip install -e .[dev]
```

If install fails (e.g., setuptools < 61.0.0 — `pyproject.toml` requires `setuptools>=61.0` per `[build-system]`), STOP and report.

**Generate the baseline** (hand-written JSON is forbidden — use the tool):

```bash
detect-secrets scan --all-files > txt/.secrets.baseline
```

**Audit the baseline for false positives** (per Qwen L2 Round Table finding — `--all-files` will flag strings in governance docs like "MIT" license text, example API keys in landmine descriptions, "AngusKingCAI" author name):

```bash
detect-secrets audit txt/.secrets.baseline
```

This opens an interactive audit. For each finding:
- If it's a real secret: STOP, remove the secret from source, re-scan.
- If it's a false positive: mark it as `is_secret: false` in the audit tool.

Document the audit decisions in the execution log (e.g., "Baseline audit: 12 findings, 0 real secrets, 12 false positives suppressed — list: 'MIT' in pyproject.toml license field, 'AngusKingCAI' in author field, etc.").

**Verify the file is valid JSON**:

```bash
python -c "import json; json.load(open('txt/.secrets.baseline'))" && echo "OK"
```

If `detect-secrets` is not installed or the scan fails, STOP and report.

After completing S4.4, run `/verify`.

---

## S5 — Fix `project-vision-Rev5.md` Title and Revision History (metadata only)

**Problem**: `documents/project-vision-Rev5.md` is byte-identical to `documents/project-vision-Rev4.md` (md5sum confirmed: `6832d5f7ecba94bfd648f2268123288b` for both). The H1 still says "Rev 4" and the revision history stops at Rev 4. Per AI_HANDOFF.md, Rev5 is the locked canonical vision all architecture must comply with — the title must reflect that.

**Scope restriction** (per Kimi M2 Round Table finding): This step is **metadata-only**. The lock on Rev5's content is preserved — no principles, criteria, or open questions are edited. Only three metadata edits are made: H1 title, status block append, revision history append.

**Fix** (use Edit tool only — OR7). Three edits, in order:

1. **H1 title change** (line 1):
   - Old: `# Founding Vision — The Unnamed Project (Rev 4)`
   - New: `# Founding Vision — The Unnamed Project (Rev 5)`

2. **Status block append** (the `> **Status**:` line near the top):
   - Append to the existing status line (do not replace): ` Locked canonical revision.`
   - Result: `> **Status**: Pre-architecture, post-third-round-table, locked canonical revision. This revision incorporates findings from the third 6-AI round table review (4 substantive responses received) and the user's resolution of all flagged issues.`

3. **Revision history append** (at the bottom of the file, after the last Rev 4 entry — append-only, do not edit existing entries):
   ```
   - **Rev 5** (2026-06-28): Locked canonical revision. No content changes from Rev 4 — Rev 4 received clean-pass #3 from the Round Table. This file's H1 title and revision history are corrected to reflect Rev 5 status. All architecture must comply with this revision per `AI_HANDOFF.md`.
   ```

**Do NOT edit**:
- The "What changed since Rev 3" paragraph (substantive content describing the Rev 4 amendments — editing it risks mutating locked history per Kimi M2).
- Any principle text, success criteria, open questions, or resolved questions table.
- The Preamble, Premise, Capability Surface, Non-Goals, or Closing sections.

After all three edits, run `/verify`.

---

## S6 — Update PLANS.md (date + verification only)

**Fix** (use Edit tool only — OR7):

1. Update the "Last updated" line at the top to today's date.
2. **Verify** (read-only — do not edit) that the `prompt-0` row in "Completed Prompts" table is present and accurate. It should already be there from the initial bootstrap commit. If it's missing or inaccurate, STOP and report.
3. **Verify** (read-only — do not edit) that Plan 1 is marked "🔜 Ready to draft" in the Next-5-Prompt Queue. It should already be. If not, STOP and report.

**Note**: S6 makes only ONE substantive edit (the date). The state verification is read-only. The substantive state change (marking prompt-0 complete, setting Plan 1 active) happens in S7.

After edit, run `/verify`.

---

## S7 — Update PLANS.md Active Plan (substantive state change)

**Fix** (use Edit tool only — OR7). This is the substantive PLANS.md state change — do this BEFORE S8's commit so the tagged commit includes the final active-plan state (per Kimi M4 / DeepSeek CRITICAL Round Table finding).

1. In the "Active Plan" section: change "None — awaiting Plan 1 execution." to "Plan 1 — awaiting execution." (or whatever the canonical active-plan format is per the existing PLANS.md structure).
2. If the existing PLANS.md has a "Next-5-Prompt Queue" with Plan 1 in slot 1, mark Plan 1's status as "▶️ Active" (or the equivalent status indicator). Do not remove Plan 1 from the queue — it stays in slot 1 with active status.
3. If there's a "Plan 1 file" reference (e.g., `prompts/plan-1-Rev1.md (to be created by Architect, copied by User)`), leave it as-is — Plan 1's file is created in a later session by the Architect.

After edit, run `/verify`.

---

## S8 — Commit and Tag Prompt-0

**STOP condition**: If any `/verify` step failed, STOP and report before committing.

1. Stage all changes (note: AGENTS.md was already committed at S0.3, so it won't be in this commit):
   ```
   git add -A
   git status -s | tail -n 20
   ```
   Verify the staged files match the "Files WILL Create" and "Files WILL Edit" lists below. If anything unexpected is staged (e.g., `.venv/`, `*.egg-info/` — `.gitignore` should prevent these, but verify), STOP.

2. Commit:
   ```
   git commit -m "prompt-0: Bootstrap governance docs and infrastructure

   - Fix master -> main branch reference in .devin/workflows/open.md
   - Add missing governance docs: CHANGELOG.md, LANDMINES.md, DECISIONS.md, DEBT.md
   - Add README.md (minimal — required by pyproject.toml readme field)
   - Add .gitignore (prevents editable-install artifacts from being committed)
   - Add pyproject.toml (dynamic deps via txt/requirements.txt per OR39)
   - Add txt/requirements.txt (empty with header), txt/vulture-whitelist.txt (empty)
   - Add txt/.secrets.baseline (generated via detect-secrets scan + audited)
   - Add .pre-commit-config.yaml
   - Create directory structure: sovereignai/ core package + UI peers (web/cli/tui/phone) + adapters/external + skills/user + skills/external
   - Fix project-vision-Rev5.md H1 title + revision history (metadata only — was byte-identical to Rev4)
   - Update PLANS.md: prompt-0 complete, Plan 1 active"
   ```

3. Tag:
   ```
   git tag prompt-0
   git tag --list prompt-0
   ```
   If empty, STOP.

4. Push:
   ```
   git push origin main
   git push origin prompt-0
   ```

5. Verify tag on origin:
   ```
   git ls-remote --tags origin | grep "prompt-0"
   ```
   If empty, STOP.

---

## Closing

Run `/close` workflow from `.devin/workflows/close.md`.

Since this is a docs-only plan with no Python code, several steps will report N/A:

**Expected results**:
- Tests: N/A (no code, no `tests/test_*.py` files yet)
- Ruff: N/A (no Python code yet — `pyproject.toml` config exists but no `.py` files to lint)
- Mypy: N/A (no Python code yet)
- Bandit: N/A (no Python code yet)
- pip-audit: 0 CVEs expected (scanned `txt/requirements.txt` only per OR39 — file is empty, no runtime deps. Dev-tool CVEs in the environment are out of scope for this check.)
- Vulture: N/A (no Python code yet)
- Detect-secrets: pass (baseline established and audited at S3.5)
- Custom AR checks: N/A (no `core/` directory — note: the AR check in `/close` step 8 references `core/`; the actual core package is `sovereignai/`. This is a known naming mismatch between the workflow file and the actual package name. The Executor should report this as a finding for Plan 1's S0 to address — the workflow files reference `core/` but the package is `sovereignai/`.)

**Custom AR check note**: `/close` step 8 includes "No globals in `core/`", "Constructor arg cap (15) in `core/`", "No context bags in `core/`", "UI changes don't touch `core/` (check `git diff --name-only HEAD~1`)". Since there is no `core/` directory (the package is `sovereignai/`), these checks will trivially pass (no files to check). The workflow file should be updated in a future plan to reference `sovereignai/` instead of `core/`. **Do not edit the workflow files in this plan** — out of scope per OR15/OR16. Report this as a finding in the execution log for the Architect to address in Plan 1.

After `/close` completes, create `logs/execution-log-prompt-0.md` with header template (per `/close` step 14). User will paste execution log content.

---

## Files WILL Create

- `README.md` (S4.1 — minimal, required by pyproject.toml readme field)
- `.gitignore` (S4.2 — prevents editable-install artifacts)
- `CHANGELOG.md` (S2.1)
- `LANDMINES.md` (S2.2)
- `DECISIONS.md` (S2.3)
- `DEBT.md` (S2.4)
- `pyproject.toml` (S3.1)
- `txt/requirements.txt` (S3.2)
- `.pre-commit-config.yaml` (S3.3)
- `txt/vulture-whitelist.txt` (S3.4)
- `txt/.secrets.baseline` (S4.4 — generated)
- `logs/.gitkeep` (S4.3)
- `tests/.gitkeep` (S4.3)
- `sovereignai/.gitkeep` (S4.3)
- `sovereignai/orchestrator/.gitkeep` (S4.3)
- `sovereignai/managers/.gitkeep` (S4.3)
- `sovereignai/workers/.gitkeep` (S4.3)
- `sovereignai/librarian/.gitkeep` (S4.3)
- `sovereignai/adapters/.gitkeep` (S4.3)
- `sovereignai/adapters/external/.gitkeep` (S4.3)
- `sovereignai/skills/.gitkeep` (S4.3)
- `sovereignai/skills/user/.gitkeep` (S4.3)
- `sovereignai/skills/external/.gitkeep` (S4.3)
- `sovereignai/shared/.gitkeep` (S4.3)
- `web/.gitkeep` (S4.3)
- `cli/.gitkeep` (S4.3)
- `tui/.gitkeep` (S4.3)
- `phone/.gitkeep` (S4.3)

## Files WILL Edit

- `AGENTS.md` (add OR39 at S0.3 — committed separately as `docs: add OR39 for prompt-0`)
- `.devin/workflows/open.md` (fix `master` → `main` on lines 14, 19 at S1)
- `documents/project-vision-Rev5.md` (fix H1 title + status block append + revision history append at S5 — metadata only)
- `PLANS.md` (update date at S6; update Active Plan at S7 — both before S8's commit)

## Files WILL NOT Edit

- `AI_HANDOFF.md` (already manually fixed by user in commit `2905452` — `.devin/` path is canonical)
- `AGENTS.md` (beyond S0.3 OR39 addition — no other edits)
- `.devin/workflows/close.md` (already correct — `main` not `master`)
- `.devin/workflows/verify.md` (no issues found)
- `.devin/workflows/scan.md` (no issues found)
- `documents/project-vision-Rev1.md` through `Rev4.md` (archived history — do not touch)
- `documents/SovereignAI_Architecture_Decisions.md` (archived — DECISIONS.md at root is the live ADR)
- `documents/plan-1-4-scope-*.md` (archived — Plan 1–4 scope split is locked)
- `documents/round-table-vision-Rev*-brief.md` (archived — vision review is complete)
- `documents/handoff-prompt.md` (archived — AGENTS.md Rev2 fixes are locked)
- `documents/AGENTS-roundtable-brief.md` (archived)
- `prompts/plan-0.md` (Rev1 — will be overwritten when user copies Rev3 to C:/SovereignAI/prompts/plan-0.md per AI_HANDOFF.md; Rev1 content preserved in git history)
- `prompts/plan-0-brief.md` (Rev1 brief — Rev3 reviews directly per Rev2+ process)

---

*Plan 0 — Prompt-0 Remediation. Rev3. Architect draft. Round Table reviews this file directly per AI_HANDOFF.md Rev2+ process.*
