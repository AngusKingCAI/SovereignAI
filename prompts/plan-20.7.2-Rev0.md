# Plan 20.7.2 — sailogs/ Full-Verbosity Logging + Test Mocks

Depends on: prompt-20.7.1
Vision principles: P9 (trust boundary), P14 (audit everything)
Open questions resolved: none

## Best Practices Research (per AI_HANDOFF.md Architect Workflow step 5)

Sources consulted via `z-ai function -n web_search`:

**For sailogs/ (S2-S4)**:
1. https://www.dash0.com/guides/logging-in-python — structured JSON logging, automatic context propagation
2. https://newrelic.com/blog/log/python-structured-logging — structured logging step-by-step
3. https://uptrace.dev/glossary/structured-logging — JSON logging best practices, field schemas
4. https://www.grepr.ai/blog/structured-logging-best-practices — 2026 structured logging guide
5. https://docs.python.org/3/library/logging.handlers.html — TimedRotatingFileHandler (rejected — per-run files simpler)
6. https://medium.com/@ThinkingLoop/7-ways-to-do-python-structured-logging-without-overhead-f7b325a86c3d — low-overhead patterns

Key findings:
- **sailogs/**: JSON Lines (`.jsonl` or `.log`) is the standard for machine-readable logs — one JSON object per line. Structured fields (timestamp, level, component, message, correlation_id) enable filtering without regex. Per-run files (vs rotation) are simpler for local-first single-user apps. Subscriber pattern (vs scattered logging calls) keeps instrumentation centralized — TraceEmitter is already the SSOT per OR61.

## Architect decisions

**DD-20.7.2 (Proposed)**: Add a `FileTraceSubscriber` that subscribes to `TraceEmitter` at startup and writes every event to `sailogs/YYYY-MM-DD_HH-MM-SS.log` as JSON lines. One file per process run, named by start timestamp. No log rotation (each run = fresh file). Full verbosity: all levels (TRACE/DEBUG/INFO/WARN/ERROR), all components, no sampling. Rejected alternative: scatter `logging.info()` calls across all execution layers. Rejected because TraceEmitter already exists (OR61 mandate), already has `subscribe_callback`, and is the SSOT for trace events — duplicating into `logging` would violate SSOT and double the instrumentation surface. Consequence: one new file, one wiring change in `build_container()`, one new directory, one `.gitignore` entry.

## WILL edit
- `AGENTS.md` — add OR76 (sailogs/) (S0.3)
- `LANDMINES.md` — add L59 (sailogs/ not gitignored) (S0.3)
- `sovereignai/shared/file_trace_subscriber.py` — NEW, FileTraceSubscriber class (S3)
- `sovereignai/main.py` — wire FileTraceSubscriber into build_container() (S4)
- `sailogs/.gitkeep` — NEW, create directory (S3)
- `.gitignore` — add `sailogs/*.log` (S3)
- `tests/test_file_trace_subscriber.py` — NEW, tests (S5)
- `pyproject.toml` — add `--timeout=30 --timeout-method=thread` to `[tool.pytest.ini_options] addopts`; verify `pytest-timeout` in dev deps (S6)
- `tests/test_options_panel.py` — mock HFDatabaseProvider.list_models to avoid 501 live API calls (S6)
- `tests/test_models_panel.py` — mock HFDatabaseProvider.list_models to avoid 501 live API calls (S6)
- `CHANGELOG.md` — append prompt-20.7.2 entry per OR73 (S9.3)
- `PLANS.md` — update baseline (S9.4)
- `prompts/plan-20.7.2-Rev0.md` — move to `completed/` (S9.5)
- `logs/execution-log-prompt-20.7.2.md` — NEW, structured S0-S9 summary + `[PASTE DEVIN CHAT HERE]` marker (S9.6)

## WILL NOT edit
- Any existing TraceEmitter code (S2 only adds a subscriber; doesn't modify the emitter)
- Any execution-layer code (no scattering of logging calls — subscriber pattern keeps it centralized)
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
- `__call__(self, event: TraceEvent) -> None`: write JSON line `{timestamp, level, component, message, correlation_id}` + `\n`, flush. Wrap in try/except (subscriber must never crash the emitter — per TraceEmitter's existing callback error handling).
- `close(self) -> None`: close file handle.
- `unsubscribe(self) -> None`: call the unsubscribe function returned by TraceEmitter.subscribe_callback, then close file.
- Use `threading.Lock` for file writes (TraceEmitter calls callbacks under its own lock, but file I/O may block — keep the critical section short).
- JSON serialization: use `json.dumps` with `default=str` (handles UUID, datetime). One line per event.

S3.3: Verify `txt/requirements.txt` needs no new deps (stdlib only: `json`, `pathlib`, `threading`, `datetime`). If any imports fail, add to requirements. `/verify`.

## S4 — Wire into build_container()

S4.1: Edit `sovereignai/main.py` `build_container()`. After TraceEmitter is registered, add: `file_subscriber = FileTraceSubscriber()`, `trace.subscribe_callback(file_subscriber)`, register `file_subscriber` as singleton in container (so it can be cleanly shut down later). Add `from sovereignai.shared.file_trace_subscriber import FileTraceSubscriber` at top.

S4.2: Verify the subscriber receives events: `python -c "from sovereignai.main import build_container; c = build_container(); from sovereignai.shared.trace_emitter import TraceEmitter; from sovereignai.shared.types import TraceLevel; c.retrieve(TraceEmitter).emit('test', TraceLevel.INFO, 'sailogs test'); import time; time.sleep(0.1)"` then check `sailogs/` has a new `.log` file with the event. `/verify`.

S4.3: Manual smoke: `python -m sovereignai.main` — confirm it starts, emits startup traces, and `sailogs/` contains a `.log` file with JSON lines. Kill after 5 seconds. Inspect the log file — should contain startup events from `main`, `capability_graph`, `routing_engine`, etc.

## S5 — Tests

S5.1: Create `tests/test_file_trace_subscriber.py`. Tests:
- `test_subscriber_writes_event`: create subscriber with temp dir, emit one event, read log file, assert JSON line matches.
- `test_subscriber_writes_multiple_events`: emit 3 events, assert 3 lines.
- `test_subscriber_handles_all_levels`: emit one of each TraceLevel, assert all 5 written.
- `test_subscriber_correlation_id`: emit event with explicit correlation_id, assert it's in the JSON.
- `test_subscriber_does_not_crash_on_bad_event`: pass a malformed object (not TraceEvent), assert subscriber catches exception and continues.
- `test_subscriber_filename_format`: assert filename matches `YYYY-MM-DD_HH-MM-SS.log` regex.
- `test_subscriber_creates_dir_if_missing`: point at non-existent dir, assert it's created.

S5.2: `/verify`. Target: 100% pass. All tests must use `tmp_path` fixture — never write to real `sailogs/` in tests.

## S6 — Test timeouts + mock stalling tests (OR79, L62)

S6.1: Edit `pyproject.toml` `[tool.pytest.ini_options]`. Change `addopts = "-vvv"` to `addopts = "-vvv --timeout=30 --timeout-method=thread"`. Verify `pytest-timeout>=2.0` is in `[project.optional-dependencies] dev` list (it was added in P20.4 per log L1283). If missing, add it. Run `pip install -e .[dev]`. Commit: `git add -A && git commit -m "feat: add 30s test timeout per OR79"`.

S6.2 (fix `test_get_databases_authorized` stall): Edit `tests/test_options_panel.py`. The test calls `GET /api/databases`, which calls `HFDatabaseProvider.list_models()` (web/main.py line 514) — same root cause as the models panel stall: 1 list call + 500 per-model `model_info` calls to HuggingFace API. Add a `conftest.py`-style fixture or inline mock at the top of the test file:

```python
import pytest
from databases.hf_database.provider import HFDatabaseProvider
from sovereignai.shared.types import ModelEntry

@pytest.fixture(autouse=True)
def mock_hf_provider(monkeypatch):
    """Avoid 501 live HuggingFace API calls in tests."""
    monkeypatch.setattr(HFDatabaseProvider, "list_models", lambda self: [
        ModelEntry(org="test", family="model-1", version="latest", quant="gguf",
                   file_size_bytes=0, vram_required_mb=0, num_layers=32,
                   category="llm", source_db="huggingface"),
        ModelEntry(org="test", family="model-2", version="latest", quant="gguf",
                   file_size_bytes=0, vram_required_mb=0, num_layers=32,
                   category="llm", source_db="huggingface"),
    ])
```

The `autouse=True` ensures all 4 tests in the file get the mock. `/verify`.

S6.3 (fix `test_models_endpoint_*` stall): Edit `tests/test_models_panel.py`. Same root cause — `GET /api/models` calls `HFDatabaseProvider.list_models()`. Add the same `autouse` fixture (or a shared `tests/conftest.py` fixture if preferred). All 4 tests in the file (including the 3 currently excluded as "HF rate-limit") should now pass instantly. `/verify`.

S6.4: Run `pytest tests/test_options_panel.py tests/test_models_panel.py -vvv --timeout=30` — confirm all tests pass in <5 seconds total (no stalls). `/verify`.

S6.5: Run `pytest tests/ -vvv --timeout=30 --no-cov -q` — confirm no test takes >30s. Any test that times out = FAILED with `Failed: Timeout >30.0s`. Investigate each timeout per OR18 (root cause) — do NOT re-run without fix. Common causes: live network call (mock it), infinite loop (fix the loop), deadlock (fix the lock). Commit: `git add -A && git commit -m "fix: mock HFDatabaseProvider in options/models panel tests per OR79/L62"`.

## S9 — Closing

S9.1: Re-read plan in full.
S9.2: Verify test suite passes: `pytest tests/ -vvv --no-cov -q`. If any test fails, investigate per OR18. Do NOT re-run without fix.
S9.3: Append prompt-20.7.2 entry to `CHANGELOG.md` per OR73. Verbatim text:
```
## prompt-20.7.2 — sailogs/ Full-Verbosity Logging + Test Mocks
**Date**: 2026-07-02
**Plan file**: prompts/plan-20.7.2-Rev0.md
**Tests**: <pytest output from S9.2>
**Coverage**: <coverage output from S9.2>
- Added OR76 (sailogs/ full-verbosity logging) and L59 to LANDMINES.md
- Created FileTraceSubscriber that writes every TraceEmitter event to sailogs/YYYY-MM-DD_HH-MM-SS.log as JSON lines
- Created sailogs/ directory with .gitignore entry
- Wired FileTraceSubscriber into build_container() per DD-20.7.2
- Created test_file_trace_subscriber.py with 7 tests (100% pass)
- Added 30s test timeout to pyproject.toml per OR79 (--timeout=30 --timeout-method=thread)
- Mocked HFDatabaseProvider.list_models in test_options_panel.py and test_models_panel.py to avoid 501 live API calls
- All tests now pass instantly with no stalls per L62
```
Commit: `git add -A && git commit -m "docs: append prompt-20.7.2 entry to CHANGELOG.md per OR73"`.

S9.4: Update `PLANS.md` baseline with new test count and coverage from S9.2.

S9.5: Move plan to completed: `git mv prompts/plan-20.7.2-Rev0.md prompts/completed/plan-20.7.2-Rev0.md`. Commit: `git add -A && git commit -m "docs: move plan-20.7.2-Rev0.md to completed/"`.

S9.6: Create `logs/execution-log-prompt-20.7.2.md` with:
- Header: `# Execution Log: prompt-20.7.2`
- Metadata: `**Plan**: prompts/plan-20.7.2-Rev0.md`, `**Date**: 2026-07-02`, `**Executor**: Devin`
- `## Devin Chat` section with `[PASTE DEVIN CHAT HERE]` marker
- Structured `## S0 — Opening` through `## S9 — Closing` summaries with task counts, deviations, and verbatim CHANGELOG echo per OR73

Commit: `git add -A && git commit -m "docs: create execution-log-prompt-20.7.2.md per OR75"`.

S9.7: Run `/close`. Verify step 17.5 (check_changelog.py 20.7.2), 17.6 (check_dependencies.py) all pass.

S9.8: `git tag prompt-20.7.2` and `git push origin main --tags`. Do NOT force-push (L25/OR42/L55/L64).

---

## Notes for Devin

- **Full verbosity means ALL levels** — TRACE, DEBUG, INFO, WARN, ERROR. Do not filter. The user wants everything.
- **One file per process run** — not rotation. Each `python -m sovereignai.main` creates a new file. The user archives/deletes old files manually.
- **JSON Lines format** — one JSON object per line, not pretty-printed. Easy to `grep`, `jq`, or parse.
- **Subscriber pattern, not scattered logging** — do NOT add `logging.info()` calls across execution layers. TraceEmitter is the SSOT (OR61). The subscriber just persists what TraceEmitter already emits.
- **sailogs/ MUST be gitignored** — L59. Verify `.gitignore` has `sailogs/*.log` before any commit. The `.gitkeep` file is tracked; the `.log` files are not.
- **OR79 is the test-timeout rule** — all tests have a 30s timeout via `--timeout=30 --timeout-method=thread` in pyproject.toml addopts. Stalled tests FAIL instead of hanging. Per-test override via `@pytest.mark.timeout(N)` for tests that legitimately need longer. S6 mocks the two stalling test files (`test_options_panel.py`, `test_models_panel.py`) so they pass instantly — the 30s timeout is a safety net, not the primary fix.
