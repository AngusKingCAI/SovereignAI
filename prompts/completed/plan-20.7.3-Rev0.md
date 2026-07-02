# Plan 20.7.3 — 20.6 Rollback + sailogs/ Implementation + Test Mocks

Depends on: prompt-20.7.2
Vision principles: P9 (trust boundary), P14 (audit everything)
Open questions resolved: none

## WILL edit
- `AGENTS.md` — add OR76 (sailogs/) (S0.3)
- `LANDMINES.md` — add L59 (sailogs/ not gitignored) + L64 (quota interrupt without re-read) (S0.3, S8.8)
- `sovereignai/shared/file_trace_subscriber.py` — NEW, FileTraceSubscriber class (S3)
- `sovereignai/main.py` — wire FileTraceSubscriber into build_container() (S4)
- `sailogs/.gitkeep` — NEW, create directory (S3)
- `.gitignore` — add `sailogs/*.log` (S3)
- `tests/test_file_trace_subscriber.py` — NEW, tests (S5)
- `pyproject.toml` — add `--timeout=30 --timeout-method=thread` to `[tool.pytest.ini_options] addopts` (S6)
- `tests/test_options_panel.py` — mock HFDatabaseProvider.list_models (S6)
- `tests/test_models_panel.py` — mock HFDatabaseProvider.list_models (S6)
- `scripts/ar_checks/spec_match.py` — revert self-immunization exclusions added in P20.6 (S8.1)
- `tests/test_ar7_no_core_imports_in_ui.py` — revert TUI_PANELS_ALLOWED_IMPORTS (S8.2)
- `tui/panels/adapters.py` — refactor to consume Capability API only per DD-20.6.1 (S8.2)
- `tests/test_hardware_probe.py` — restore or delete pynvml skip stubs (S8.3)
- `CHANGELOG.md` — correct false prompt-20.6 claims (S8.5); append prompt-20.7.3 entry per OR73 (S9.3)
- `logs/execution-log-prompt-20.6.md` — append `## Post-P20.7.3 /close completion` section (S8.6)
- `PLANS.md` — update baseline (S9.4)
- `prompts/plan-20.7.3-Rev0.md` — move to `completed/` (S9.5)
- `logs/execution-log-prompt-20.7.3.md` — NEW, structured S0-S9 summary + `[PASTE DEVIN CHAT HERE]` marker (S9.6)

## WILL NOT edit
- Any file not listed above. If scope expands, STOP per OR10.

## S0 — Opening

S0.1: Run `/open`. Read `AGENTS.md` in full.
S0.2: Re-read `LANDMINES.md`.
S0.3: Add OR76 (`"OR76. [Mandatory] saillogs/ contains per-run JSONL trace logs named YYYY-MM-DD_HH-MM-SS.log. One file per process run. FileTraceSubscriber writes every TraceEmitter event. sailogs/*.log gitignored. No rotation — user archives/deletes manually."`) to `AGENTS.md`. Add L59 (`"## L59 — sailogs/ not gitignored. Trigger: sailogs/ created without .gitignore entry. Impact: trace logs (may contain sensitive data) committed to repo. Graduated to: OR76."`) to `LANDMINES.md`. Commit: `git add -A && git commit -m "docs: add OR76, L59 (sailogs/ full-verbosity logging)"`.

S0.4: Begin Phase 1.

## S3 — FileTraceSubscriber implementation

S3.1: Create `sailogs/.gitkeep` to track the directory. Add `sailogs/*.log` to `.gitignore`. Commit: `git add -A && git commit -m "feat: create sailogs/ directory with .gitignore per OR76"`.

S3.2: Create `sovereignai/shared/file_trace_subscriber.py`. Class `FileTraceSubscriber`:
- `__init__(self, log_dir: str = "sailogs")`: create directory if missing, generate filename `YYYY-MM-DD_HH-MM-SS.log` using `datetime.now(timezone.utc).strftime("%Y-%m-%d_%H-%M-%S")`. Open file in append mode. Store unsubscribe callback (initially None).
- `__call__(self, event: TraceEvent) -> None`: write JSON line `{timestamp, level, component, message, correlation_id}` + `\n`, flush. Wrap in try/except (subscriber must never crash the emitter).
- `close(self) -> None`: close file handle.
- `unsubscribe(self) -> None`: call the unsubscribe function returned by TraceEmitter.subscribe_callback, then close file.
- Use `threading.Lock` for file writes (TraceEmitter calls callbacks under its own lock, but file I/O may block — keep the critical section short).
- JSON serialization: use `json.dumps` with `default=str` (handles UUID, datetime). One line per event.

S3.3: Verify `txt/requirements.txt` needs no new deps (stdlib only: `json`, `pathlib`, `threading`, `datetime`). If any imports fail, add to requirements. `/verify`.

## S4 — Wire into build_container()

S4.1: Edit `sovereignai/main.py` `build_container()`. After TraceEmitter is registered, add: `file_subscriber = FileTraceSubscriber()`, `trace.subscribe_callback(file_subscriber)`, register `file_subscriber` as singleton in container. Add `from sovereignai.shared.file_trace_subscriber import FileTraceSubscriber` at top.

S4.2: Verify the subscriber receives events: `python -c "from sovereignai.main import build_container; c = build_container(); from sovereignai.shared.trace_emitter import TraceEmitter; from sovereignai.shared.types import TraceLevel; c.retrieve(TraceEmitter).emit('test', TraceLevel.INFO, 'sailogs test'); import time; time.sleep(0.1)"` then check `sailogs/` has a new `.log` file with the event. `/verify`.

S4.3: Manual smoke: `python -m sovereignai.main` — confirm it starts, emits startup traces, and `sailogs/` contains a `.log` file with JSON lines. Kill after 5 seconds.

## S5 — Tests

S5.1: Create `tests/test_file_trace_subscriber.py`. Tests: `test_subscriber_writes_event`, `test_subscriber_writes_multiple_events`, `test_subscriber_handles_all_levels`, `test_subscriber_correlation_id`, `test_subscriber_does_not_crash_on_bad_event`, `test_subscriber_filename_format`, `test_subscriber_creates_dir_if_missing`. All tests must use `tmp_path` fixture — never write to real `sailogs/` in tests.

S5.2: `/verify`. Target: 100% pass.

## S6 — Test timeouts + mock stalling tests (OR79, L62)

S6.1: Edit `pyproject.toml` `[tool.pytest.ini_options]`. Change `addopts = "-vvv"` to `addopts = "-vvv --timeout=30 --timeout-method=thread"`. Verify `pytest-timeout>=2.0` is in `[project.optional-dependencies] dev`. Run `pip install -e .[dev]`. Commit: `git add -A && git commit -m "feat: add 30s test timeout per OR79"`.

S6.2: Edit `tests/test_options_panel.py`. Add `autouse` fixture mocking `HFDatabaseProvider.list_models` to return 2 test `ModelEntry` objects (avoid 501 live API calls). All 4 tests in the file get the mock. `/verify`.

S6.3: Edit `tests/test_models_panel.py`. Add same `autouse` fixture. All 4 tests in the file (including 3 currently excluded as "HF rate-limit") should now pass instantly. `/verify`.

S6.4: Run `pytest tests/test_options_panel.py tests/test_models_panel.py -vvv --timeout=30` — confirm all tests pass in <5 seconds total (no stalls). `/verify`.

S6.5: Run `pytest tests/ -vvv --timeout=30 --no-cov -q` — confirm no test takes >30s. Investigate timeouts per OR18. Commit: `git add -A && git commit -m "fix: mock HFDatabaseProvider in options/models panel tests per OR79/L62"`.

## S8 — 20.6 findings rollback (CRITICAL — MANDATORY, no deferrals)

S8.1: Edit `scripts/ar_checks/spec_match.py`. Remove `and not p.startswith("scripts/ar_checks/")` exclusion (P20.6 L3833) and `and not p.startswith("logs/")` exclusion (P20.6 L3629) and `tui/` addition (P20.6 L3573). If spec_match fails after revert, document failures in DEBT.md with target plan per OR64. Commit: `git add -A && git commit -m "fix: revert spec_match.py self-immunization exclusions per OR39"`.

S8.2: Edit `tests/test_ar7_no_core_imports_in_ui.py`. Remove `TUI_PANELS_ALLOWED_IMPORTS` expansion added in P20.6 S3.6. Run `pytest tests/test_ar7_no_core_imports_in_ui.py -vvv`. If fails, document in DEBT.md with target plan per OR64. Commit: `git add -A && git commit -m "fix: revert TUI_PANELS_ALLOWED_IMPORTS expansion per OR39"`.

S8.2b: Refactor `tui/panels/adapters.py` (and any other TUI panels with direct core imports) to consume Capability API only per DD-20.6.1. If any panel cannot be refactored, document blocker in DEBT.md with target plan per OR64. Commit: `git add -A && git commit -m "refactor: TUI panels consume Capability API only per AR7/DD-20.6.1"`.

S8.3: Edit `tests/test_hardware_probe.py`. Either restore pynvml tests (if pynvml required) or delete skip stubs (if code path gone). Run `pytest tests/test_hardware_probe.py -vvv` after change. Commit: `git add -A && git commit -m "fix: restore or delete pynvml skip stubs per OR15"`.

S8.5: Edit `CHANGELOG.md`. Remove false "Mocked HFDatabaseProvider.list_models" bullets from prompt-20.6 entry (not shipped per P20.6 audit). Correct test count if needed (verify with `pytest tests/ -vvv --no-cov -q`). Commit: `git add -A && git commit -m "docs: correct false prompt-20.6 CHANGELOG claims per OR55"`.

S8.6: Edit `logs/execution-log-prompt-20.6.md`. Append `## Post-P20.7.3 /close completion` section listing S8.1-S8.5 corrections. Commit: `git add -A && git commit -m "docs: append P20.7.3 corrections to execution-log-prompt-20.6.md per OR73"`.

S8.8: Add L64 to `LANDMINES.md`: `"## L64 — Quota interrupt without re-read. Trigger: Devin resumes work after quota interrupt without re-reading plan + AGENTS.md (OR45). Impact: Context lost; rules forgotten; steps skipped. Graduated to: OR45."` Commit: `git add -A && git commit -m "docs: add L64 (quota interrupt without re-read) per OR45"`.

## S9 — Closing

S9.1: Re-read plan in full.
S9.2: Verify test suite passes: `pytest tests/ -vvv --no-cov -q`. If any test fails, investigate per OR18.
S9.3: Append prompt-20.7.3 entry to `CHANGELOG.md` per OR73. Include: OR76/L59, FileTraceSubscriber, sailogs/, test_file_trace_subscriber.py, 30s timeout, HFDatabaseProvider mocks, S8 rollbacks, L64. Commit: `git add -A && git commit -m "docs: append prompt-20.7.3 entry to CHANGELOG.md per OR73"`.

S9.4: Update `PLANS.md` baseline with new test count and coverage from S9.2.

S9.5: Move plan to completed: `git mv prompts/plan-20.7.3-Rev0.md prompts/completed/plan-20.7.3-Rev0.md`. Commit: `git add -A && git commit -m "docs: move plan-20.7.3-Rev0.md to completed/"`.

S9.6: Create `logs/execution-log-prompt-20.7.3.md` with header, metadata, `## Devin Chat` section with `[PASTE DEVIN CHAT HERE]` marker, and structured S0-S9 summaries with verbatim CHANGELOG echo per OR73. Commit: `git add -A && git commit -m "docs: create execution-log-prompt-20.7.3.md per OR75"`.

S9.7: Run `/close`. Verify step 17.5 (check_changelog.py 20.7.3), 17.6 (check_dependencies.py) all pass.

S9.8: `git tag prompt-20.7.3` and `git push origin main --tags`. Do NOT force-push (L25/OR42/L55/L64).

---

## Notes for Devin

- **Full verbosity**: ALL levels (TRACE/DEBUG/INFO/WARN/ERROR). No filtering.
- **One file per process run**: Not rotation. Each `python -m sovereignai.main` creates new file.
- **JSON Lines format**: One JSON object per line, not pretty-printed.
- **Subscriber pattern**: Do NOT add `logging.info()` calls. TraceEmitter is SSOT (OR61).
- **sailogs/ MUST be gitignored**: L59. Verify `.gitignore` has `sailogs/*.log`.
- **OR79**: 30s test timeout via `--timeout=30 --timeout-method=thread` in pyproject.toml.
- **S8 is CRITICAL**: P20.6 audit revealed systematic rule violations. Each item MANDATORY — no deferrals.
