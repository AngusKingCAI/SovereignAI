# AGENTS.md — SovereignAI Rules

**AR{n}** = Architecture Rules · **OR{n}** = Operational Rules · Ambiguous rule → read `LANDMINES.md`.
Authority: `project-vision-Rev5.md` (locked). New rules must be checked against it before being added.
**Rule style**: one to three sentences, actionable content only. No explanatory backstory, no "this applies to all layers" tail-clauses, no repeated framing. Source citations use short form: `(Source: P7)` or `(Source: L24)`.

---

## Architecture Rules

### Chain of command
AR1. Owner ↔ Orchestrator only. Delegation chain: Orchestrator → Manager → Worker. Orchestrator may bypass Manager for tasks that need exactly one Worker, one capability, no shared cross-cutting state, and no multi-step dependency. Bypass is per-delegation, never standing. Workers report to Manager, or to Orchestrator if Manager was bypassed. Manager/Worker may not initiate Owner contact — all Owner-facing output routes through Orchestrator. Exception: Owner-initiated emergency direct control (Owner triggers it, not the component).

AR2. Workers query the Librarian directly for memory — Manager is a task coordinator, not a memory intermediary. Librarian enforces access control. No Worker, Manager, or Orchestrator may query a memory backend directly.

AR3. All model inference routes through the Adapters layer. No component may load model weights, instantiate a model client, or call an inference endpoint directly. The Models panel is a filtered view of Adapters — not a separate layer.

### Core discipline
AR4. No global mutable state. All shared state lives in `shared/container.py` (the DI container). Container is a passive typed registry: no `@inject`, no auto-wiring, no runtime magic. Components declare dependencies as constructor args and receive them via explicit injection from the Composition Root — never self-instantiate. Orchestrator and Librarian are DI singletons. Managers and Workers are factories (per-task, destroyed on completion unless promoted). No module-level mutable variables, class-level mutable defaults, or monkey-patching. `shared/` holds contracts, interfaces, DI container definition, and the singleton container instance only.

AR5. No constructor takes >15 arguments (excluding `self`/`cls`). If exceeded, split the class or introduce a typed config dataclass. Applies to all layers. Auto-generated dataclass `__init__` is exempt only when the dataclass is a pure DTO (no behaviour). Composition Root (`main.py`) is the sole exception. (Source: P7)

AR6. No component may accept a generic context object, untyped dict, or `**kwargs` catch-all across component boundaries. Every parameter must have a declared type and single clear purpose. TraceEmitter is permitted as a constructor arg (single-responsibility typed object) but must carry structured trace/observability data only — never business-logic params, config values, or cross-component state. Adding extra attributes to a TraceEmitter to avoid declaring args is a P11 violation. (Source: P11)

### UI / Panel separation
AR7. UI processes (web, TUI, CLI, phone) consume the Capability API only. No imports from `orchestrator/`, `managers/`, `workers/`, `librarian/`, `adapters/`, or `skills/`. Business logic, routing, and state management live in core/pluggable layers — never in a UI process.

> **AR8 permanently retired** — AR7 already enforces this; do not reuse slot AR8.

AR9. No component references another component by hard-coded name. Component discovery always routes through the capability graph (capability requirement → routing engine → registered component). If a capability is missing at runtime, degrade gracefully and report — no silent failure. **Exemptions**: Composition Root (`main.py`), test files, and skill/adapter manifests may reference component names directly (none are runtime discovery paths).

### Memory & Librarian
AR10. All memory access routes through the Librarian. No component (Worker, Manager, Orchestrator, Skill, UI) may instantiate, import, or query a memory backend directly. Librarian enforces access control, routing, and backend selection per current Memory topology.

AR11. Each data type routes to exactly one primary backend, determined by live topology config — never hardcoded. Librarian reads the live topology at query time. New backend = new adapter, no core changes. Topology assignments live in `config/memory_topology.yaml` (user-editable), read at startup — never as a compiled dict in source. A default that requires a code change to alter violates this rule.

AR12. Librarian has two layers. **Layer 1 (Registry)**: always-on, registers backends at startup, maintains routing topology, resolves structured queries. No model required. **Layer 2 (Model)**: demand-loaded fine-tuned adapter; interprets natural-language queries into structured queries for Layer 1; loaded on demand, unloaded when idle. Layer 2 is pluggable — swapping it requires no Layer 1 changes. All memory queries go to Layer 1; Layer 1 invokes Layer 2 only when needed.

### Skills & Adapters
AR13. Skills consume tools exclusively through the capability graph — no direct adapter imports or calls. Skill declares tool dependencies in its manifest. Exception: Python stdlib (no adapter registration needed). If a capability is unavailable, skill receives a typed error and degrades gracefully.

AR14. All external MCP servers must be wrapped as SovereignAI adapters before any component uses them. Adapter handles auth, error handling, retry, and capability registration. No component calls an MCP server directly. Installed MCP servers are copied locally to `adapters/external/` — remote-only MCP servers are not permitted at runtime.

AR15. At startup every adapter registers each tool it exposes in the capability graph (capability category, interface contract, priority weight). A tool is not callable until registered. If an adapter fails its health check, any in-flight call completes with a graceful typed error; the adapter deregisters after the in-flight call concludes. Subsequent requestors receive a typed error — no silent failure.

### Worker & Manager lifecycle
AR16. Every Worker respects the circuit breaker: >50 errors in 10 seconds triggers automatic unload. Not optional, not overridable per Worker. Error-counting and unload logic lives in `shared/`. The running error tally is a DI-managed object injected at construction (never a module-level variable). On circuit-breaker unload: Orchestrator gets a typed error, Manager is notified, task is marked FAILED. Worker may be reloaded by Orchestrator or Owner after investigation — no automatic restart.

AR18. Managers are temporary runtime instances by default (spawned per task, destroyed on completion). In v1, Managers run on a shared general model. A Manager promoted to permanent status by Orchestrator or Owner persists and may be fine-tuned via QLoRA (weights persist on disk). Workers are always fine-tuned specialist models (weights on disk, instances load on demand, unload when idle or circuit-broken). No Manager or Worker manages its own lifecycle — spawning, promotion, loading, and unloading are handled exclusively by the Lifecycle Manager in `shared/`.

### Telemetry
AR17. All traces, logs, and diagnostics are written to local SSD only via the TraceEmitter. No component may send telemetry, usage data, error reports, or traces to an external server — ever, including anonymised data. TraceEmitter is the sole telemetry surface. Log drawer reads from local trace store only. Sending data externally requires an explicit user-initiated action via a registered adapter — not automatic background telemetry.

### Skill authoring
AR19. Every skill authoring method (Canvas, Code, Template, Conversation, Import) produces identical output: manifest + code + DAG definition. No method may produce a format only it can read or that requires special runtime handling. Manifest format and DAG schema are defined once in `shared/` (SSOT). A new authoring method must produce the same output — new tabs never require changes to skill runtime, manifest parser, or DAG validator.

### Local-first
AR20. All installed external components (MCP servers, external skills, external adapters) are copied to local disk before use. MCP → `adapters/external/`, external skills → `skills/external/`. No component calls a remote-only external service at runtime as a substitute for a local component. Network access during task execution is always an explicit user-initiated action via a registered adapter — never implicit runtime behaviour. If an external component requires network access, that call is the skill's/adapter's explicit responsibility (declared in manifest) — not hidden infrastructure.

### Docstring discipline
AR21. Every `def` and `async def` (including methods) must have a docstring whose first line: starts with a verb, is ≥10 words, and uses no programming jargon (`async`, `await`, `coroutine`, `dispatch`, `yield`, `instantiate` → replace with plain English). A non-coder should understand the function's purpose from the first line alone. Multi-line docstrings may explain inputs/outputs/errors with the same plain-language standard. Enforced via Ruff `D103` + custom CI check (verb-first, ≥10 words, jargon scan). Applies to AI-generated and human-written code equally. (Source: P12)

> **Deferred**: Security Guard rules (originally AR10–AR12 in early drafts) dropped — will be implemented later as a Worker. See `DEBT.md`.

---

## Operational Rules

### Environment
OR1. Git Bash only. Use: `grep`, `cat`, `sed`, `awk`, `head`, `tail`, `touch`, `ls`, `wc`, `xargs`. Avoid: `Select-String`, `Get-Content`, `Set-Content`, `Add-Content`, `Get-ChildItem`, `Measure-Object`, `Where-Object`, `ForEach-Object`.

OR2. File-scoped mypy only. Never `mypy .` except at 5-plan checkpoints (5, 10, 15, 20…).

OR3. Run scan tools (pytest, ruff, mypy, bandit, pip-audit, vulture) ONE AT A TIME. Parallel execution corrupts output streams. (Source: L2)

OR4. When counting bandit findings by ID, filter on `>> Issue: [B` pattern only. Before applying this filter, visually confirm at least one `>> Issue: [B` line exists in raw output — if no matches on a non-trivial file, verify bandit output format hasn't changed (e.g. after upgrade). Zero matches after a format change = blocker, not clean result.

### Edit discipline
OR5. Never use `replace_all`. Edit each occurrence individually or use targeted line-specific replacements. (Source: L1)

OR6. Syntax check after every file edit, BEFORE tests: `python -c "import ast; ast.parse(open('<file>.py').read())"`. If syntax error, STOP.

OR7. Structured-markdown edits (`AGENTS.md`, `AI_HANDOFF.md`, plan files, `CHANGELOG.md`) — Edit tool only with exact `old_str`/`new_str` pairs. Never `sed` or shell redirection (`>`, `>>`) for structured markdown. (Source: L3)

OR8. Diff check after every file edit: `git diff --stat <file>`. Confirm only intended files changed.

### Git discipline
OR9. Tag EVERY prompt. Even docs-only plans must have `git tag prompt-{N}`.

OR10. Tag verification before push: `git tag --list prompt-{N}`. If empty, tag wasn't created.

OR11. Post-push verification (mandatory): `git ls-remote --tags origin | grep "prompt-{N}"`. If empty, push failed.

OR32. Never use `git commit --no-verify`. If a hook fails, fix the issue. Only acceptable exception: hotfix to a broken hook itself — document the bypass in the commit message. (Source: L11)

### CHANGELOG discipline
OR12. Append to END only. Never insert at top. Oldest entry at top, newest at bottom.

OR13. Use temp-file pattern (not here-strings). Append via `cat >>`. After appending, DELETE the temp file. (Source: L4)

OR14. Hard cap: 15 lines per entry — title, changed files, results, test count, ≤3 Notes bullets. Implementation rationale and design trade-offs do NOT belong in CHANGELOG; log them in `DECISIONS.md` and reference the decision ID (`See DECISIONS.md D{n}`) instead of re-explaining. (Amended 2026-06-28, governance review — see DECISIONS.md D5)

### Scope discipline
OR15. Pre-declare scope before editing. List files you WILL edit and files you will NOT edit. Any file outside the "will edit" list requires STOP and Architect authorization.

OR16. HARD STOP on scope expansion. If you discover work outside the plan's scope, STOP and report — do not edit files outside declared scope.

OR17. Baseline reconciliation. If actual count at plan start ≠ plan's expected count, update `PLANS.md` baseline with actual number + reason. (Source: L7)

OR26. Governance-doc edits discovered at `/open` must be a separate commit and tag. If `git status` shows modified/untracked governance docs (`AGENTS.md`, `AI_HANDOFF.md`, `PLANS.md`, `CHANGELOG.md`, `LANDMINES.md`) or plan files, commit them as `docs: cleanup pre-prompt-{N}` and tag as `docs-cleanup-{N}` — do NOT bundle into `prompt-{N}`. CHANGELOG for `prompt-{N}` lists only files edited in the plan body.

### Test discipline
OR18. Tests change with code. Full test suite MUST pass before tagging.

OR19. Test fixture parameters may be required by pytest/middleware/pydantic even if vulture flags them unused. Don't remove without checking decorator context. (Source: L5)

OR25. Test deletion is a scope deviation. If a specified test can't be made to pass, STOP and report. Do NOT delete, comment out, or defer the test. Tests in the plan spec are in scope; removing them is a HARD STOP under OR16.

### Datetime, temp files, always-on
OR20. Never mix naive/aware `datetime`. Use `datetime.now(timezone.utc)` everywhere. Never `datetime.utcnow()`, bare `datetime.now()`, or `default_factory=datetime.utcnow`. (Source: L6)

OR21. Temp files go in a dedicated temp dir (e.g. `C:/SovereignAI/temp/`), NOT repo root. After consuming (e.g. appending to CHANGELOG), DELETE the temp file. Check for stray files before `git add`.

OR22. Read `AGENTS.md` in full once per coding session, before the first file edit. Do not re-read before every subsequent edit. Before every file edit, run a mental check against this always-on subset (no re-read needed): OR5, OR6, OR15, OR16, OR34, AR5, AR16, AR21. Two events require a full mid-session re-read: (a) `AGENTS.md` itself is edited, or (b) session resumes after a STOP or replan boundary. (Source: L8; re-read cadence revised 2026-06-28)

### Verbosity, new implementations, type remediation
OR23. Cite rules by number when applying them in three situations: (a) rule shapes a code-structure decision, (b) rule blocks a proposed action ("Blocked by AR{n}: <name>"), (c) rule is explicitly listed in the current plan step. Format: "Applying AR{n}: <name>" or "Applying OR{n}: <name>".

OR24. Every new implementation (module, class, public function) MUST have a corresponding test file with passing tests covering key paths.

OR27. When fixing type errors requires interface changes that break existing tests, add compatibility shims: delegate to new implementation while accepting old signature, mark deprecated with docstring. This lets type fixes land without modifying out-of-scope tests. (Source: L9)

### Git Bash discipline, hooks, task list
OR28. After each command execution block, close the Git Bash session. For sequential commands, use a single session with `;` separation. At plan close (or every 20 commands), verify no orphaned processes remain.

OR33. Never exclude files from pre-commit hooks to bypass errors. If a hook fails on an out-of-scope file, STOP and report per OR16. Correct responses: (a) fix if in-scope, (b) STOP if out-of-scope, (c) `SKIP="<hook_id>" git commit` for a single commit if the hook itself is broken. Never edit hook config to permanently exclude files. (Source: L12)

OR34. Execute plan steps in strict numerical order (S0 → S1 → … → Sn). Do not start a later step until the current step is complete. Do not mark a task complete based on work done elsewhere. If a step cannot proceed due to an unresolved dependency, STOP and report the dependency conflict — do not jump ahead. (Source: L17)

### Git output discipline
OR35. Use token-efficient git commands:
- `git status -s` not `git status`
- `git diff --stat` not `git diff` (full diff only when line changes are needed)
- `git log --oneline -N` never bare `git log`
- Pipe through `tail -n N` to truncate
- If full output is needed, note why before running

### Git Bash output discipline
OR36. Minimize Git Bash output:
- Pipe through `tail -n N` (default N=5) unless more is needed
- Chain multi-command verifications with `;`; capture only final summary line
- Never run a command producing >20 lines without truncation
- Pre-commit hooks: `2>&1 | tail -n 10`; if hook fails, re-run without truncation for full output
- **pytest**: always full verbose `-vvv`, no `-q`, no `--tb=short`, no piping to `tail` (full output required for hangs/stuck tests/failure details)
- ruff/mypy: `| tail -n 3` (you only need the error count)

### Batch verification
OR37. Batch verification commands to reduce execution blocks:
- Chain syntax, ruff, mypy, detect-secrets, vulture with `;` and capture final summary
- Example: `python -c "import ast; ast.parse(open('file.py').read())" ; ruff check file.py ; mypy file.py --ignore-missing-imports ; echo "---DONE---" 2>&1 | tail -n 5`
- On failure, re-run failing check individually for full output
- **pytest is exempt** — always separate command with full `-vvv` per OR36
- After batching, verify each tool produced output; missing output + exit 0 = success; missing output + non-zero = failure (re-run individually)

> **OR38 permanently retired** — all plan files kept forever; do not reuse slot.

### Worker / batch verification
OR29. Zero output from a command (e.g. empty `git tag --list`) is data, not success. Re-run with a confirmation command that explicitly verifies the expected state exists.

OR30. Never re-run a failing test suite without first identifying the root cause. A second run without a fix is noise, not diagnosis.

OR31. If a plan step is impossible as written (missing dependency, wrong path, wrong API), STOP immediately. Report: `BLOCKED: {step} — {reason} — {what's needed to unblock}`.

### Dependency management
OR39. Runtime dependencies: `txt/requirements.txt` only. Append package + version pin at the plan step that introduces the import. `pyproject.toml` uses `dynamic = ["dependencies"]` reading from `txt/requirements.txt` — do NOT also list runtime deps under `[project.dependencies]`. Dev tools (pytest, ruff, mypy, bandit, vulture, detect-secrets, pre-commit) live in `pyproject.toml [project.optional-dependencies] dev` — never in `txt/requirements.txt`. After any change to `txt/requirements.txt`, run `pip install -e .[dev]` then `pip-audit --strict --requirement txt/requirements.txt`.

OR40. `detect-secrets scan` must exclude vendored/build dirs. Always pass `--exclude`:
```bash
detect-secrets scan --all-files --exclude '.venv,venv,env,build,dist,node_modules,__pycache__,.git,.tox,.eggs,.pytest_cache,.mypy_cache,.ruff_cache,htmlcov,*.egg-info' > txt/.secrets.baseline
```
After generating baseline, run `detect-secrets audit txt/.secrets.baseline` for false-positive review. Do NOT manually edit the baseline JSON — manual edits break its signature. Audit tool is the only sanctioned way to mark false positives. (Source: L26)

OR41. Use the Edit tool to create empty files (`.gitkeep`, `__init__.py`), not `echo "" > path`. Git Bash on Windows handles `echo "" >` unreliably inside `&&` chains. Edit tool with `filepath` and minimal `new_str` is canonical. For directories: `mkdir -p path/to/dir` + separate Edit-tool call for `.gitkeep`. (Source: L24)

OR42. Multi-line git commit messages use multiple `-m` flags, not embedded newlines: `git commit -m "title" -m "body"`. Git Bash on Windows handles `\n` in quoted strings inconsistently. Each `-m` flag becomes a separate paragraph. For bullet lists, use literal newlines within a single `-m` (not `\n` escapes). (Source: L25)

OR43. Shell redirection (`>`, `>>`) for tool output is unreliable in Git Bash on Windows — use `tee` or run without redirection then capture via Edit tool. Applies to any command producing >1KB of output needing file capture. Small outputs (`echo "OK" > flag.txt`) are exempt. (Source: L24)

OR44. Workflow files (`.devin/workflows/*.md`) are structured markdown — OR7 applies. Edits must use the Edit tool with exact `old_str`/`new_str`, never `sed` or shell redirection. If Edit tool fails to match: (a) re-read file to confirm exact content, (b) retry with smaller `old_str`, (c) if still failing, STOP and report — do NOT fall back to `sed`. (Source: L28)

OR45. Project-local venv at `.venv/` is canonical. Create once via `py -3.11 -m venv .venv`, then `.venv/Scripts/pip.exe install -e .[dev]`. System `python`/`pip` on PATH may point to different installations — never assume shared site-packages. Use absolute venv paths per OR46. `.venv/` is gitignored — never commit. (Source: L29)

OR46. Workflow commands use absolute venv paths, not `source activate`. Git Bash on Windows does not reliably persist `source .venv/Scripts/activate`. All workflow files and plan steps must use: `.venv/Scripts/python.exe -m pytest`, `.venv/Scripts/ruff.exe`, `.venv/Scripts/mypy.exe`, `.venv/Scripts/bandit.exe`, `.venv/Scripts/pip-audit.exe`, `.venv/Scripts/vulture.exe`, `.venv/Scripts/detect-secrets.exe`. If `.venv/` is missing, create it per OR45 first. (Source: L30)

OR47. Mypy is invoked on `.py` files only — never markdown, YAML, TOML, or other non-Python files. Filter the file list before passing to mypy. If no `.py` files were edited this plan, mypy is N/A — report "N/A (no Python files edited)" and continue. Canonical invocation: `git diff --name-only HEAD~1 | grep '\.py$' | xargs .venv/Scripts/mypy.exe --ignore-missing-imports`. At scan prompts (5, 10, 15…), `mypy .` scans the whole repo and naturally skips non-Python files. (Source: L31)

OR48. Custom AR static analysis checks (AR4, AR5, AR6, AR9, AR21) are committed scripts in `scripts/ar_checks/`, never re-derived ad hoc at `/close` or `/scan`. If a check has no script yet, write one, commit it with the current plan, and use it from then on. Each script documents which AR rule it enforces via `--help`. Changing a check's behaviour means editing the script (reviewable diff), not silently changing what gets caught. (Source: governance review 2026-06-28 — see DECISIONS.md D5)

OR49. The FastAPI web app runs as a separate process, not embedded in the core runtime. The web server imports from `sovereignai/` only via the public API surface (`CapabilityAPI`, protocols). It does not import core internals directly. Source: Plan 6.

OR50. SSE connections authenticate via standard HTTP session cookie. No query-parameter tokens are used for auth. Source: Plan 6 Rev 2.

OR52. Web-layer DTOs (in `web/schemas.py`) are the canonical HTTP contract. Core domain types are never returned directly from HTTP endpoints. Mapping functions convert between DTOs and core types. Source: Plan 6 Rev 2.

OR54. Every adapter MUST declare a `health_check()` method. The `LifecycleManager` calls this method on adapter registration. If the health check fails, the adapter is registered with `DEGRADED` status in the capability graph — it is NOT skipped. This lets the UI show "Ollama: unavailable" rather than hiding it. Source: Plan 7.

OR55. Skills placed in `skills/user/` are user-authored and trusted by default per P14. They do NOT require a provenance manifest or cryptographic signature. Skills in `skills/external/` DO require provenance manifests. The manifest parser distinguishes by directory path. Source: P14.

OR56. The `MessageDispatcher` (v1) queries the `CapabilityGraph` for registered skills and routes to the first matching capability by priority order. It does NOT perform intent parsing, disambiguation, or structured prompt construction — those are CEO-shaped work deferred to a future plan. Source: Plan 7 Rev 2.

OR71. Run workflow commands verbatim. When executing any step in `.devin/workflows/*.md`, copy the command exactly as written (after substituting `{N}` placeholders for the current plan number). Do not paraphrase, simplify, or substitute a single-file command for a loop. If a command errors, report the error and STOP — do not fall back to a "simpler" version that achieves less. Re-read the workflow file fresh at the start of every `/close` and `/scan` run; do not rely on a cached/remembered version. Source: L32.

OR72. Never edit AR check scripts or tests to make a failure pass. If a script in `scripts/ar_checks/` or a test in `tests/` fails, the failure indicates a real violation in the source code or a real bug in the test. Fix the source code, or fix the test's *logic* (not its assertion). Editing a test to weaken its assertion — excluding imports from a denylist, commenting out a check, raising a threshold — is a STOP condition. The only exception is if the weakening is explicitly documented in the plan's S0.3 with Architect sign-off. Source: L33.

OR73. `/close` is mandatory and atomic. Completing a plan's body (S1–Sn) does not close the plan. The plan is not closed until `/close` runs all 22 steps (or STOPs on a real failure). The Executor must not commit and tag manually as a substitute for `/close`. If `/close` fails partway, the Executor must report the failure to the User rather than falling back to manual commit+tag. Source: L27.

OR74. Workflow files are Architect-authored. `.devin/workflows/*.md` is authored by the Architect per the Document Relationships table in `AI_HANDOFF.md`. The Executor may apply a minimal patch to unblock the current close if a workflow bug is discovered mid-`/close`, but must (a) flag the patch in the execution log (Step 13 C9 mechanism) and (b) note it for the Architect to formally adopt in the next plan's S0.3. The Executor must not make undocumented workflow changes. Source: AI_HANDOFF.md Document Relationships.

OR75. Stage all changes with `git add -A`; verify with `git status` before every commit. Before every `git commit` in `/close` (steps 15 and 18), run `git status -s` to see ALL modified/deleted/new files, then `git add -A` to stage them all (including auto-fixes from ruff `--fix`/detect-secrets AND deletions from `mv` operations). Do not use explicit `git add <file1> <file2> ...` lists — they miss auto-fixed files and `mv` deletions. After `git add -A`, run `git status -s` again to verify the staging area is clean (all changes staged, no unstaged lines). If any unstaged changes remain, STOP. Source: L34, L35.

OR76. Create `git tag prompt-{N}` only after the final code commit is made and verified. Never create a tag pointing at a placeholder or intermediate commit. If a tag was created prematurely, `git tag -d prompt-{N}` locally, complete the work, then create the tag at the final commit. Never `git push origin prompt-{N} --force` to move a tag — if a tag was pushed prematurely, STOP and report to the User; the User decides whether to force-push or accept the stale tag. Source: L36.

OR77. Coverage is measured at every `/close` for plans that touch Python source files. Run `python -m pytest tests/ --cov=. --cov-report=term-missing` as part of Step 1 (or as a new Step 1.5). If coverage dropped >5% from the PLANS.md baseline, STOP. If coverage is "N/A" for a plan that edited `.py` files, STOP. Docs-only plans (no `.py` edits) may report "N/A" with a one-line reason. Update PLANS.md coverage baseline at every `/close` where coverage was measured. Source: L37.

OR78. Update the Bandit baseline in PLANS.md at every `/close` where tests were added or removed. The B101 (assert_used) count grows with test count — this is expected. Record the actual count, not a stale number. If the count changed by >20% from the PLANS.md baseline without a corresponding test count change, STOP and investigate (may indicate a new non-test Low finding). Source: L38.

OR79. If a plan session is interrupted by quota exhaustion, model timeout, or session reset, the Executor MUST re-read the plan file (`prompts/plan-{N}.md`) and `AGENTS.md` in full before continuing. The Executor must also review the TODO list and verify the last completed step. Do not resume from a cached mental model — context may have been lost. If the interrupt happened mid-`/close`, re-read `.devin/workflows/close.md` fresh (per OR71) and verify which step was last completed before resuming. Source: L39.

OR80. `git add -A` is mandatory for EVERY commit, not just `/close` steps 15 and 18. This includes governance patches made during the plan body (S0.3 rule commits, mid-plan fixes, workflow patches, L32-L33 landmine additions). After `git add -A`, run `git status -s` to verify the staging area is clean. Never use `git add <file1> <file2> ...` — explicit lists miss auto-fixes, deletions, and untracked files. OR75 applies to all commits, not just close-workflow commits. Source: OR75 (clarified and broadened).

OR81. The `.secrets.baseline` file is never edited manually. To remove a false positive, run `detect-secrets audit txt/.secrets.baseline` (interactive tool) — never open the JSON in an editor. Manual edits break the baseline's signature and cause false "new secrets detected" results. If `detect-secrets audit` is unavailable or fails, STOP and report — do not fall back to manual editing. Source: L26 (promoted to rule).

OR82. Never use `git mv` — it errors unreliably in Git Bash on Windows. Use plain `mv` to move files, then `git add -A` (per OR75/OR80) to stage both the new paths and the deletions of the old paths. Verify with `git ls-files '<old-path-glob>'` that git no longer tracks the old paths. Source: L34 (clarified).

---

## Landmines → Rules

| Landmine | Rule | Problem |
|---|---|---|
| L1 | OR5 | replace_all corrupts adjacent lines |
| L2 | OR3 | Parallel scan tools corrupt output streams |
| L3 | OR7 | PowerShell -replace corrupts structured markdown |
| L4 | OR13 | Temp files left in repo root get committed |
| L5 | OR19 | Vulture flags unused test fixtures incorrectly |
| L6 | OR20 | Naive/aware datetime mixing |
| L7 | OR17 | Stale baselines propagate through plans |
| L8 | OR16, OR22 | Scope drift: editing files outside declared scope |
| L9 | OR27 | Interface changes break existing tests during type remediation |
| L11 | OR32 | Bypassed pre-commit hooks with --no-verify |
| L12 | OR33 | Hiding type errors by excluding files from hooks |
| L17 | OR34 | Plan steps executed/marked complete out of order |
| L24 | OR41, OR43 | Shell redirection and echo-to-file fail in Git Bash on Windows |
| L25 | OR42 | Multi-line git commit messages fail in Git Bash on Windows |
| L26 | OR40 | detect-secrets --all-files scans .venv/ despite .gitignore |
| L27 | (workflow fix only — /close step 21 + Steps header) | Executor skipped /close steps when expected result was N/A |
| L28 | OR44 | sed used on workflow files after Edit-tool failures |
| L29 | OR45 | python and pip resolve to different interpreters on Windows |
| L30 | OR46 | source .venv/Scripts/activate does not persist in Git Bash on Windows |
| L31 | OR47 | Mypy fails when passed markdown or other non-Python files |

---

## LANDMINES.md — when to read / write

**Read**: Architect Workflow Step 3/4 (before new plans or rule proposals) · Executor (on-demand): if a rule's application is ambiguous.

**Write** (at `/close` step 11) — format:
```markdown
## L{n} — <one-line title>
**Trigger**: <Plan #, step, command/file/context>
**Impact**: <What broke>
```
Concise only — trigger and impact. No narrative, no cross-references, no proposed fixes.

**Graduating a landmine to a rule**:
1. Executor captures L{n} at `/close` step 11
2. Architect reviews at Workflow Step 4, proposes AR{m} or OR{m}
3. Executor adds rule at `/open` step 4 of next plan: `OR{m}. <rule> (Source: L{n})`
4. Rule is live

`LANDMINES.md` is append-only — entries are never edited or removed after capture.
