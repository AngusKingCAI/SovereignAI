# AGENTS.md — SovereignAI Rules

The Executor's always-on rules. Read before every coding session.

**Rule naming**:
- **AR{n}** = Architecture Rules (AR1–AR21)
- **OR{n}** = Operational Rules (OR1–OR37)

**If a rule's application is unclear or ambiguous**, read `LANDMINES.md` to find the source landmine and understand the diagnostic context behind the rule.

**Canonical authority**: every rule below has been checked against `project-vision-Rev5.md` (locked) for alignment with Modularity and Flexibility. Where a rule cites a Principle (P1–P14) or Core Scope item, that is its justification. New rules proposed in future plans must be checked the same way before being added here.

---

## Architecture Rules

### Chain of command (Owner / Orchestrator / Manager / Worker)

AR1. Only the Orchestrator communicates directly with the Owner. The standard delegation chain is Orchestrator → Manager → Worker. The Orchestrator may bypass the Manager and delegate directly to a Worker, evaluated fresh on each delegation, when the task meets all of the following: it requires exactly one Worker, one capability, no cross-cutting state shared with other in-flight tasks, and no multi-step dependency chain. This bypass is never a standing channel — a Worker that was bypassed for one task is not exempt from Manager coordination on its next task; each delegation is judged independently against these criteria. Managers report results to the Orchestrator, not to the Owner. Workers report to their Manager, or directly to the Orchestrator if the Manager was bypassed. No component at the Manager or Worker level may initiate communication with the Owner — all Owner-facing output routes through the Orchestrator. The only exception is an Owner-initiated bypass (emergency direct control), which the Owner triggers, not the component.

AR2. Workers query the Librarian directly for memory access. The Manager is not a memory intermediary — it is a task coordinator only. The Librarian enforces access control, determining which backends a given Worker or Manager is permitted to read from or write to. No Worker or Manager may instantiate or query a memory backend directly — all memory access routes through the Librarian regardless of whether a Manager is in the delegation chain. The Orchestrator follows the same rule — it queries the Librarian, not backends directly.

AR3. All model inference routes through the Adapters layer. Every model provider (Ollama, Hugging Face, llama.cpp, OpenAI, Anthropic, local fine-tuned weights) is registered as a model adapter. No component — Worker, Manager, Orchestrator, or Skill — may load model weights, instantiate a model client, or call an inference endpoint directly. Workers executing their own fine-tuned inference are loaded and managed by their registered model adapter. The Models panel is a filtered view of the Adapters panel showing model-type adapters only — it is not a separate layer.

### Core discipline

AR4. No global mutable state anywhere in the codebase. All shared state is managed through the `dependency-injector` DI container defined in `shared/container.py` — the single wiring point for the entire application. Components declare their dependencies as constructor arguments and receive them via injection — they never instantiate dependencies themselves or reach into global scope. The Orchestrator and Librarian (Layer 1, the Registry) are registered as DI-managed singletons. Managers and Workers are registered as factories (new instance per task, destroyed when the task completes unless promoted). No module-level mutable variables, no class-level mutable defaults, no monkey-patching. The `shared/` directory holds contracts, interfaces, and the DI container definition only — no runtime state outside the container.

AR5. No constructor in any layer may take more than 15 arguments. If a component requires more, it is a signal the class has too many responsibilities — split the class or introduce a typed config dataclass to group related arguments. This cap applies across all layers: `orchestrator/`, `managers/`, `workers/`, `librarian/`, `adapters/`, `skills/`, `panels/`, `shared/`. When counting arguments, exclude `self` and `cls` — they are not dependencies. Auto-generated dataclass `__init__` methods are subject to the cap unless the dataclass is a pure DTO (a typed data-grouping struct with no behaviour, per AR6) — a pure DTO is exempt because it is the correct pattern for grouping related arguments, not a god-object. The Composition Root (`main.py`) is the sole exception to the cap — it wires all core components explicitly in topological order and is not subject to the limit. (Source: `project-vision-Rev5.md` P7.)

AR6. No component may accept a generic context object, untyped dictionary, or catch-all parameter bag as a substitute for explicit arguments. Every parameter must have a declared type and a single clear purpose. Passing `**kwargs` through component boundaries is forbidden. The TraceEmitter is not a context bag — it is a single-responsibility typed object and is explicitly permitted as a constructor argument. It carries structured trace and observability data only; it must never be used to pass business-logic parameters, configuration values, or cross-component state. Adding extra attributes to a TraceEmitter instance to avoid declaring additional constructor arguments is a P11 violation — the TraceEmitter's permitted status does not make it a vehicle for bypassing the explicit-argument discipline. If a function needs five pieces of data, it declares five typed parameters or receives a typed dataclass grouping related data — it does not receive a dict containing all five. (Source: `project-vision-Rev5.md` P11.)

### UI / Panel separation

AR7. UI processes (web, TUI, CLI, phone) consume the Capability API only. They may not import from `orchestrator/`, `managers/`, `workers/`, `librarian/`, `adapters/`, or `skills/` directly. A UI process that needs data queries the Capability API — it does not reach into core internals. Business logic, routing decisions, and state management live in the core and pluggable layers — never in a UI process.

AR9. No component may reference another component by hard-coded name anywhere in the codebase. Component discovery always routes through the capability graph — a component declares the capability it needs, and the routing engine resolves which registered component satisfies it. This applies across all layers: Managers, Workers, Skills, Adapters, and UI processes. If a capability requirement cannot be satisfied at runtime, the system degrades gracefully and reports the missing capability — it does not fail silently. **The Composition Root (`main.py`) is exempt from this rule** — it explicitly wires concrete components by name, per AR4 and the vision's Q26 ("no runtime magic, no auto-discovery"). Test files and skill/adapter manifests may also reference component names directly, since neither is a runtime discovery path. All runtime call paths — Managers, Workers, Skills, Adapters, UI processes — must still route through the capability graph with no exceptions.

> **Note**: AR8 (UI changes never touch core/) was proposed and dropped — AR7 already enforces this architecturally, since UIs are separate processes that cannot import core internals. Trust the architecture; do not duplicate it as a discipline rule. **AR8's number is permanently retired** — do not reuse this slot for a future rule, as doing so would create a cross-reference conflict with any document that cites the AR8 drop. New rules continue from AR22 onward.

### Memory & Librarian

AR10. All memory access routes through the Librarian. No component — Worker, Manager, Orchestrator, Skill, or UI process — may instantiate, import, or query a memory backend directly. The Librarian enforces access control, determines which backends a component is permitted to read from or write to, and routes queries to the correct backend per the current Memory topology configuration. Memory backends are pluggable — adding or swapping a backend requires no changes to any component that queries memory.

AR11. Each data type is routed to exactly one primary backend at runtime, determined by the user's current Memory topology configuration — not by hardcoded mappings in the codebase. The Librarian resolves the primary backend for each data type by reading the live topology at query time. Adding a new memory backend means registering a new adapter — no core or Librarian code changes required. The user assigns data types to backends via the Memory panel. If no backend is assigned for a data type, the Librarian returns a typed error — it does not fail silently or guess. Default assignments ship with the system but are fully user-configurable. **Shipped default topology assignments live in a user-editable configuration file (e.g. `config/memory_topology.yaml`), read by the Librarian Registry at startup — never as a dictionary or mapping compiled into source code. A default that requires a code change to alter is a hardcoded mapping and violates this rule, regardless of how it is labelled.**

AR12. The Librarian has two distinct layers. **Layer 1 — the Librarian Registry** — is a lightweight always-on core component that registers memory backends at startup via the Composition Root, maintains the routing topology, and resolves structured queries to the correct backend. It requires no model and runs for the lifetime of the application. **Layer 2 — the Librarian Model** — is a demand-loaded fine-tuned model adapter that interprets plain-English memory queries into structured queries for Layer 1. It is loaded when a natural language memory query arrives and unloaded when idle, following the same lifecycle as Workers. Layer 2 is pluggable — swapping it for a better model requires no changes to Layer 1 or any other component. No component interacts with Layer 2 directly — all memory queries go to Layer 1, which invokes Layer 2 only when query interpretation is needed.

### Skills & Adapters

AR13. Skills consume tools exclusively through the capability graph. A skill may not import, instantiate, or call an adapter directly. A skill declares its tool dependencies in its manifest as capability requirements — the routing engine resolves which registered adapter satisfies each requirement at runtime. The only exception is Python standard library functions which are considered native built-ins and do not require adapter registration. If a required capability is unavailable at runtime, the skill receives a typed error and handles degradation gracefully — it does not assume the capability exists.

AR14. All external MCP servers must be wrapped as SovereignAI adapters before any component can use them. The adapter is responsible for authentication, error handling, retry logic, and capability registration. No component may call an MCP server's protocol directly — all calls route through the adapter's registered capability interface. Installed MCP servers are copied locally to `adapters/external/` — remote-only MCP servers are not permitted at runtime. This ensures local-first operation and means MCP server availability does not depend on external network conditions during task execution.

AR15. At startup every adapter calls the capability graph to register each tool it exposes, declaring its capability category, interface contract, and priority weight. A tool is not callable by any component until it appears in the capability graph. Components discover available tools by querying the capability graph with a capability requirement — they never reference adapters or tools by hard-coded name (per AR9). The capability graph is the single source of truth for what the system can do at any given moment. If an adapter fails its health check, any in-flight tool call on that adapter completes with a graceful typed error response — it is not killed mid-execution. The adapter deregisters from the capability graph after the in-flight call concludes, not before. Any subsequent component requesting that capability receives a typed error — it does not fail silently.

### Worker & Manager lifecycle

AR16. Every Worker implementation must respect the circuit breaker threshold — more than 50 errors in 10 seconds triggers automatic unload. The circuit breaker is not optional and cannot be disabled or overridden per Worker. Error counting and unload logic (the rules for what counts as an error and when the threshold is crossed) live in `shared/` as core infrastructure. The error count itself — the running tally for a given Worker's rolling 10-second window — is a DI-managed object registered in the container per Worker, injected at construction. It is never a module-level variable in `shared/`, and no Worker or Manager may read or reset it except through the Lifecycle Manager. A Worker that is unloaded via circuit breaker is reported to the Orchestrator with a typed error, the Manager is notified, and the task is marked FAILED in the task state machine. The Worker may be reloaded by the Orchestrator or Owner after investigation — it does not restart automatically.

AR18. Managers are temporary runtime instances by default — spawned for a task and destroyed on completion. In v1, Managers run on a shared general model and are not fine-tuned individually. A Manager promoted to permanent status by the Orchestrator or Owner persists as a running instance for its department and may be fine-tuned over time via QLoRA — its weights persist on disk independently of its runtime instance. Workers are always fine-tuned specialist models — their weights persist on disk and their runtime instances load on demand and unload when idle or when the circuit breaker triggers. No Manager or Worker may manage its own lifecycle — spawning, promotion, loading, and unloading are handled exclusively by the Lifecycle Manager in `shared/`.

### Telemetry

AR17. All traces, logs, and diagnostic data are written to local SSD only via the TraceEmitter. No component may send telemetry, usage data, error reports, or traces to an external server under any circumstances — not even anonymised. The TraceEmitter is the sole telemetry surface — no component may write logs via any other mechanism. The log drawer (bottom of every panel) reads from the local trace store only. If a future skill or adapter needs to send data externally, that is an explicit user-initiated action via a registered adapter — not automatic background telemetry.

### Skill authoring

AR19. Every skill authoring method — Canvas, Code, Template, Conversation, Import — produces identical output: a manifest plus code plus DAG definition. No authoring method may produce a format that only it can read or that requires special handling by the runtime. The manifest format and DAG schema are defined once in `shared/` and are the SSOT for skill definitions. A skill authored via Canvas must be executable by the same runtime as a skill authored via Code — the authoring method is a UI concern only, invisible to the runtime. If a new authoring method is added in a future plan, it must produce the same output format — adding a new tab never requires changes to the skill runtime, manifest parser, or DAG validator.

### Local-first

AR20. All installed external components — MCP servers, external skills, external adapters — are copied to local disk before use. MCP servers go to `adapters/external/`, external skills go to `skills/external/`. No component may call a remote-only external service at runtime as a substitute for a locally installed component. Network access during task execution is always an explicit user-initiated action via a registered adapter tool — never implicit background behaviour by the runtime. Installing a new external component means downloading and registering it locally — not referencing it remotely. If an external component requires network access to function, that network call is the skill's or adapter's explicit responsibility, declared in its manifest — not hidden infrastructure behaviour.

### Docstring discipline

AR21. Every `def` and `async def` (including methods) must have a docstring whose first line explains, in plain English, what the function does — written so a non-coder could read it and understand the function's purpose without needing to know what code is. The first line must start with a verb and be at least 10 words long. No programming jargon is allowed in the first line — words like `async`, `await`, `coroutine`, `dispatch`, `yield`, or `instantiate` must be replaced with everyday language (`send`, `wait for`, `running task`, `send to`, `produce`, `create`). A useful test: if you read the first line aloud to someone who has never written code, they should understand what the function accomplishes. Multi-line docstrings may explain inputs, outputs, and errors, but should keep the same plain-language standard throughout. Enforced via Ruff `D103` (missing docstring) plus a custom CI check (verb-first, ≥10 words, jargon scan). Applies equally to AI-generated and human-written code. (Source: `project-vision-Rev5.md` P12.)

> **Deferred**: the Security Guard rules originally proposed as AR10–AR12 in early drafts were dropped — the Security Guard is not pertinent to the core yet and will be implemented later as a Worker (see `DEBT.md` for the deferred-item entry once created).

---

## Operational Rules

### Environment
OR1. Git Bash only. Use standard Unix commands: `grep`, `cat`, `sed`, `awk`, `head`, `tail`, `touch`, `ls`, `wc`, `xargs`. Avoid PowerShell-specific commands like `Select-String`, `Get-Content`, `Set-Content`, `Add-Content`, `Get-ChildItem`, `Measure-Object`, `Where-Object`, `ForEach-Object`.

OR2. File-scoped mypy only. Never `mypy .` — except at 5-plan checkpoints (5, 10, 15, 20...) where full-repo mypy is the point.

OR3. Run scan tools (pytest, ruff, mypy, bandit, pip-audit, vulture) ONE AT A TIME. Parallel execution corrupts output streams. (Source: L2)

OR4. When counting bandit findings by ID, filter on `>> Issue: [B` pattern only, not bare ID string (ID appears in multiple line types). Before applying this filter, visually confirm at least one `>> Issue: [B` line appears in the raw output — if no matches are found and the file is non-trivial, verify the bandit output format has not changed (e.g. after a version upgrade). A format change that causes zero matches must be reported as a blocker, not treated as a clean result.

### Edit discipline
OR5. Never use `replace_all`. Edit each occurrence individually or use targeted line-specific replacements. (Source: L1)

OR6. Syntax check after every file edit, BEFORE tests: `python -c "import ast; ast.parse(open('<file>.py').read())"`. If syntax error, STOP.

OR7. Structured-markdown edits (`AGENTS.md`, `AI_HANDOFF.md`, plan files, `CHANGELOG.md`) — Edit tool only with exact `old_str`/`new_str` pairs. NEVER bash `sed`, or shell redirection operators (`>`, `>>`) for structured markdown. (Source: L3)

OR8. Diff check after every file edit: `git diff --stat <file>`. Confirm only intended files changed.

### Git discipline
OR9. Tag EVERY prompt. Even docs-only plans must have `git tag prompt-{N}`.

OR10. Tag verification before push: `git tag --list prompt-{N}`. If empty, tag wasn't created.

OR11. Post-push verification (mandatory): `git ls-remote --tags origin | grep "prompt-{N}"`. If empty, push failed.

OR32. Never use `git commit --no-verify`. Pre-commit hooks are the last gate before commit; bypassing them defeats the purpose of having hooks. If a hook fails, fix the issue — do not bypass the hook. The only acceptable exception is a hotfix to a broken hook itself, and even then, document the bypass in the commit message. (Source: L11)

### CHANGELOG discipline
OR12. Append to END only. Never insert at top. Oldest entry at top, newest at bottom.

OR13. Use temp-file pattern (not here-strings). Append via `cat >>` with proper encoding. After appending, DELETE the temp file. (Source: L4)

OR14. Simplified format: ~10–15 lines per entry. Title, changed files, results, test count. No fluff.

### Scope discipline
OR15. Pre-declare scope before editing. List files you WILL edit and files you will NOT edit. Any file outside the "will edit" list requires STOP and Architect authorization.

OR16. HARD STOP on scope expansion. If you discover work outside the plan's scope, STOP and report it — do not edit files outside the declared scope.

OR17. Baseline reconciliation. If the actual count at the start of a plan ≠ the plan's expected count, update `PLANS.md` baseline with actual number + reason. Don't let stale baselines propagate. (Source: L7)

OR26. Governance-doc edits discovered at `/open` must be a separate commit and tag. If `git status` at the opening step shows modified/untracked governance docs (`AGENTS.md`, `AI_HANDOFF.md`, `PLANS.md`, `CHANGELOG.md`, `LANDMINES.md`) or plan files (`prompts/`), commit them as a standalone `docs: cleanup pre-prompt-{N}` commit and tag as `docs-cleanup-{N}` — do NOT bundle them into the next `prompt-{N}` tag. The CHANGELOG entry for `prompt-{N}` must list only the files actually edited as part of the plan body.

### Test discipline
OR18. Tests change with code. Full test suite MUST pass before tagging.

OR19. Test fixture parameters may be required by pytest/middleware/pydantic even if vulture flags them as unused. Don't remove without checking decorator context. (Source: L5)

OR25. Test deletion is a scope deviation. If a test listed in the plan's test specification cannot be made to pass due to mocking complexity, fixture difficulty, or API mismatch, STOP and report to the user. Do NOT delete the test, comment it out, or replace it with a "deferred to a future plan" note. Tests specified in the plan are part of the plan's scope; removing them is a HARD STOP under OR16.

### Datetime, temp files, always-on
OR20. Never mix naive/aware `datetime`. Use `datetime.now(timezone.utc)` everywhere. Never `datetime.utcnow()` or bare `datetime.now()`. Watch for `default_factory=datetime.utcnow` (use `default_factory=lambda: datetime.now(timezone.utc)` instead). (Source: L6)

OR21. Temp files go in a dedicated temp directory (e.g. `C:/SovereignAI/temp/` or `C:/SovereignAI/scan/logs/`), NOT repo root. After appending to `CHANGELOG.md` (or wherever consumed), DELETE the temp file. Before `git add`, check for stray files.

OR22. Read `AGENTS.md` in full once at the start of each coding session, before the first file edit. Do not re-read it before every subsequent edit — one read per session is sufficient. Before every file edit, run a mental check against this always-on subset (no re-read required): OR5 (no replace-all), OR6 (syntax check before tests), OR15 (scope pre-declared), OR16 (hard stop on scope expansion), OR34 (strict step order), AR5 (≤15 constructor args), AR16 (50 errors/10s circuit breaker), AR21 (≥10-word plain-English docstring first line). If any of these are unclear, consult `LANDMINES.md` for the relevant diagnostic context. Two events require a full re-read of `AGENTS.md` mid-session: (a) `AGENTS.md` itself is edited during the session, or (b) the session resumes after a STOP or replan boundary. The Executor MUST NOT edit files outside the plan's declared scope; if work is discovered outside scope, STOP and report it. (Source: L8; re-read cadence revised 2026-06-28 to reduce repeated full-document re-reads; always-on subset and re-read triggers added after Round Table Rev2 review.)

### Verbosity, new implementations, type remediation
OR23. Cite rules by number when applying them. Citation is required in three situations: (a) the rule directly shapes a code structure decision (e.g. splitting a class because of AR5, routing memory through the Librarian because of AR10), (b) the rule blocks a proposed action (cite it as "Blocked by AR{n}: <rule name>"), or (c) the rule is explicitly listed in the current plan step. When applying a rule, cite it as "Applying AR{n}: <rule name>" or "Applying OR{n}: <rule name>". This creates an audit trail that makes rule compliance explicit and verifiable in the execution log.

OR24. Every new implementation (new module, new class, new public function) MUST have a corresponding test file with tests covering the key paths. No implementation is "complete" until its tests pass.

OR27. When fixing type errors requires interface changes that would break existing tests, add compatibility shims to maintain backward compatibility. The shim should delegate to the new implementation while accepting the old signature. Mark the shim as deprecated with a docstring noting the legacy status. This allows type fixes without test modifications, which are outside scope for type-remediation plans. (Source: L9)

### Git Bash discipline, hooks, task list
OR28. Git Bash session cleanup: After each command execution block, the Executor MUST close the Git Bash session. If executing multiple commands in sequence, use a single session with `;` separation rather than spawning multiple sessions. At plan closing (or every 20 commands, whichever comes first), verify no orphaned processes remain.

OR33. Never exclude files from pre-commit hooks (mypy, ruff, black, etc.) to bypass errors. If a hook fails on a file outside the plan's scope, STOP and report per OR16 — do not edit `.pre-commit-config.yaml` to exclude the file. The correct response is either: (a) fix the error if it's in-scope, (b) STOP and report if it's out-of-scope, or (c) use `SKIP="<hook_id>" git commit` (bash syntax) for a single commit if the hook itself is broken. Never edit hook config to permanently exclude files. (Source: L12)

OR34. Execute plan steps in strict numerical order (S0 → S1 → S2 → ... → Sn). Do not START a later step until the current step is complete. Do not MARK a task complete based on work done in a different section — a task is complete only when its corresponding plan section is fully executed in order. If S0 (opening) edits a governance doc and a later step also edits the same doc, completing S0 does NOT complete that later step, and it must not start until the steps before it are done. If a step cannot proceed because a dependency defined in a later step has not yet been completed, STOP and report the dependency conflict to the Architect — do not implement against an undefined dependency and do not jump ahead in step order. If a step is blocked for any other reason, STOP and report — do not jump ahead to a later step. (Source: L17)

### Git output discipline
OR35. Use token-efficient git commands to reduce context consumption:
- Use `git status -s` (short format) for routine checks, NOT `git status` (full format). Short format returns one line per changed file.
- Use `git diff --stat` for overview, NOT `git diff` (full diff). Only use full `git diff` when you need to see specific line changes.
- Use `git log --oneline -N` (with count limit, e.g., `-5`), NEVER bare `git log`.
- Pipe all git output through `tail -n N` to truncate: `git status -s | tail -n 10`
- If output is needed in full (e.g., diagnosing a specific issue), note why before running the full command.

### Git Bash output discipline
OR36. Minimize Git Bash output to reduce context token consumption:
- Always pipe command output through `tail -n N` (default N=5 unless more is needed).
- For multi-command verification, chain with `;` and capture only the final summary line.
- Never run a command that produces >20 lines of output without truncation.
- For pre-commit hooks: run with `2>&1 | tail -n 10` to capture only pass/fail summary. If a hook fails, re-run that specific hook without truncation to see full output.
- For pytest: run with full verbose output using `-vvv` (no `-q`, no `--tb=short`, no piping to `tail`). Full verbose output is required so hangs, stuck tests, and failure details are all visible. If the user needs truncated output for a specific case, they will request it explicitly.
- For ruff/mypy: pipe through `tail -n 3` — you only need the error count.

### Batch verification
OR37. Batch verification commands to reduce the number of separate command executions and output blocks:
- Instead of running 6 separate verification commands (syntax, ruff, mypy, detect-secrets, vulture, tests), chain them with `;` and capture only the final summary.
- Example: `python -c "import ast; ast.parse(open('file.py').read())" ; ruff check file.py ; mypy file.py --ignore-missing-imports ; echo "---CHECKS DONE---" 2>&1 | tail -n 5`
- If any check fails, the failure will appear in the last 5 lines. Then re-run the failing check individually for full output.
- This reduces 6 Executor actions + 6 output blocks to 1 Executor action + 1 output block.
- **Pytest is exempt from this batching** — it always runs as a separate command with full `-vvv` output per OR36, never piped through `tail`, never chained with other checks.

### Worker / batch verification (Category 12 — gap fill)
OR29. When a step produces no output (e.g., `git tag --list` returns empty, `grep` finds nothing), do not assume success. Zero output is data. Re-run with a confirmation command that explicitly verifies the expected state exists.

OR30. Never re-run a failing test suite without first identifying the root cause. A second run without a fix is noise, not diagnosis.

OR31. When the Executor discovers a plan step is impossible as written (missing dependency, wrong path, wrong API), STOP immediately. Do not attempt a workaround. Report the exact blocker in the format: `BLOCKED: {step} — {reason} — {what's needed to unblock}`.

> **Dropped**: OR38 (decade cleanup / deleting old plan files) was reviewed and explicitly dropped for this project — all plan files are kept forever, no deletion. Do not renumber a future rule into this slot; OR38 is permanently retired.

OR39. Runtime dependencies live in `txt/requirements.txt` only. When a plan introduces a new runtime dependency (a package imported by production code in `sovereignai/`, `web/`, `cli/`, `tui/`, or `phone/`), the Executor appends the package name with version pin (e.g., `pydantic>=2.0`) to `txt/requirements.txt` at the plan step that introduces the import. `pyproject.toml` declares `dynamic = ["dependencies"]` and reads from `txt/requirements.txt` via `[tool.setuptools.dynamic]` — it must NOT also list runtime deps under `[project.dependencies]` (SSOT; duplicate lists drift). Dev-only tools (pytest, ruff, mypy, bandit, vulture, detect-secrets, pre-commit) live in `pyproject.toml`'s `[project.optional-dependencies] dev = [...]` — they never go in `txt/requirements.txt` because they are not installed in a production environment. After any change to `txt/requirements.txt`, run `pip install -e .[dev]` to refresh the local environment, then re-run `pip-audit --strict --requirement txt/requirements.txt` to verify the new runtime dependency has no known CVEs (scans the requirements file only — dev-tool CVEs in the environment are not in scope for this check). (Source: Plan 0 — Architect-proposed.)

OR40. `detect-secrets scan` must exclude vendored and build directories. `detect-secrets` does not honor `.gitignore` by default — it scans every file on disk. When generating or refreshing `txt/.secrets.baseline`, always pass `--exclude` with patterns matching `.gitignore`:

```bash
detect-secrets scan --all-files --exclude '.venv,venv,env,build,dist,node_modules,__pycache__,.git,.tox,.eggs,.pytest_cache,.mypy_cache,.ruff_cache,htmlcov,*.egg-info' > txt/.secrets.baseline
```

After generating the baseline, run `detect-secrets audit txt/.secrets.baseline` interactively to review any remaining false positives. Do NOT manually edit the baseline JSON to remove findings — manual edits break the baseline's signature and cause `detect-secrets scan --baseline` to fail on subsequent runs. The audit tool is the only sanctioned way to mark false positives. (Source: L26 — Plan 0 execution, Executor manually edited JSON instead of using audit tool, required follow-up commit `41b9326` to fix.)

OR41. Use the Edit tool to create empty files (`.gitkeep`, `__init__.py`), not shell `echo "" > path`. Git Bash on Windows does not reliably handle `echo "" > path/to/file` for paths with forward slashes inside `&&` chains — the command errors silently or produces a file at an unexpected location. The Edit tool with `filepath="path/to/file"` and minimal `new_str` content (e.g., a single newline) is the canonical way to create empty files in this repo. For directory creation, `mkdir -p path/to/dir` works reliably; combine with a separate Edit-tool call to create the `.gitkeep` file inside it. (Source: L24 — Plan 0 execution, all 16 `mkdir -p X && echo "" > X/.gitkeep` commands errored; Executor fell back to Edit tool successfully.)

OR42. Multi-line git commit messages use multiple `-m` flags, not embedded newlines. Git Bash on Windows interprets embedded newlines in `git commit -m "title\n\nbody"` quoted strings inconsistently — the command may error or silently produce a single-line message. Use `git commit -m "title" -m "body paragraph 1" -m "body paragraph 2"` instead. Each `-m` flag becomes a separate paragraph in the commit message. For bullet-list bodies, put each bullet on its own line within a single `-m` argument using literal newlines typed in the shell (not `\n` escape sequences). (Source: L25 — Plan 0 execution, multi-line commit message errored; Executor fell back to single-line message, losing the structured body.)

OR43. Shell redirection (`>`, `>>`) for tool output is unreliable in Git Bash on Windows — use `tee` or run without redirection and capture via Edit. When a tool's output needs to be written to a file (e.g., `detect-secrets scan > file.json`), prefer `tool args | tee file.json` (writes to both terminal and file), or run the tool without redirection and use the Edit tool to write the captured output to the target file. This applies to any command producing >1KB of output that needs file capture. Small outputs (e.g., `echo "OK" > flag.txt`) are exempt — `echo` redirection is reliable. (Source: L24 — Plan 0 execution, `detect-secrets scan --all-files > txt/.secrets.baseline` errored; Executor fell back to running without redirect, then Edit.)

---

## Landmines that have graduated to rules

This section maps landmines to their corresponding rules. L1–L23 are inherited from sovereign-ai (the predecessor project); new landmines for SovereignAI start at L24.

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

---

## Reading and writing LANDMINES.md

**When to read LANDMINES.md**:
- Architect Workflow Step 3 / Step 4: re-read landmines before creating new plans or proposing rules
- Executor (on-demand): if an AGENTS.md rule's application is ambiguous, read the source landmine for diagnostic context

**When to write LANDMINES.md** (at `/close` step 11):

Capture new failure patterns using this format:

```markdown
## L{n} — <one-line title of the failure pattern>

**Trigger**: <Plan #, step, specific command/file/context — be concrete>

**Impact**: <What broke as a result>
```

Keep entries concise — trigger and impact only. No narrative, no cross-references to other plans. No proposed fixes or rules — those come from the Architect via `AGENTS.md`.

**Process for graduating a landmine to a rule**:
1. Executor captures L{n} at `/close` step 11
2. Architect reviews at Workflow Step 4 and proposes rule AR{m} or OR{m}
3. Executor adds rule to `AGENTS.md` at `/open` step 4 of the next plan, with source reference: "OR{m}. <rule statement> (Source: L{n})"
4. Rule is live; the Executor complies with it going forward

`LANDMINES.md` is append-only — entries are never edited or removed after capture.
