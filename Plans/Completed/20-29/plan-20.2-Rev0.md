# Plan 20.2 — Fix Post-20.1 Test & Type Failures

```
Depends on: prompt-20.1
Vision principles: P2 (modularity), P4 (testability), P6 (local-first), P9 (observability), P13 (quality gates)

Open questions resolved: none
```

---

## S0 — Opening
- **S0.1**: Run `/open`
- **S0.2**: Read `AGENTS.md` in full
- **S0.3**: Add new rules if governance patch needed; commit before coding

---

## S1 — Fix `test_procedural_backend_lock_timeout` Failure
**Evidence**: Log 20.1 L2516 — `Failed: DID NOT RAISE ProceduralMemoryLockTimeoutError`. Test patches `time.monotonic` to return `9999999999`, but `_acquire_lock()` returns `True` in in-memory mode (`_path=None`). The test uses `tempfile.NamedTemporaryFile` but the backend may not be entering file-based lock logic.

**Root cause analysis**: The test creates a backend with `file_path=tmp_path`, but `_acquire_lock()` checks `if not self._path: return True`. If `_path` is set correctly, the deadline = `9999999999 + 5.0`, and `time.monotonic()` returns `9999999999` on first call, which is `< deadline`, so it enters the loop. The `os.O_CREAT | os.O_EXCL` should succeed on first iteration since the lock file doesn't exist yet — so it returns `True`, not `False`. The test expects the lock to timeout, but with a fresh temp file, there's no contention.

**Fix**: The test must simulate lock contention — create the `.lock` file before calling `store()`, or patch `_acquire_lock` to return `False` directly (which matches the pattern in `tests/test_procedural_backend.py` line 42).

- **S1.1**: Read `sovereignai/memory/procedural_backend.py` lines 38-51 to confirm `_acquire_lock` logic
- **S1.2**: Fix the test to create lock file contention or patch `_acquire_lock` return value; verify test raises `ProceduralMemoryLockTimeoutError`
- **S1.3**: Run `pytest tests/test_hardware_probe.py::test_procedural_backend_lock_timeout -v`

**Files will edit**: `tests/test_hardware_probe.py`

---

## S2 — Fix Mypy Type Errors (7 errors in 2 files)
**Evidence**: Log 20.1 L4223-4234.

| File | Line | Error | Fix |
|------|------|-------|-----|
| `conformance/base.py` | 14 | Missing type annotation for `instance` param | Already has `instance: Any` — check if method signature is complete; add return type `-> None` if missing |
| `llama_cpp_adapter/adapter.py` | 86 | `Path` assigned to `TextIOWrapper` | Variable shadowing: `f` is file handle, then `gguf_path` reassigned from `model_dir / model_info["filename"]` — check line 86 context |
| `llama_cpp_adapter/adapter.py` | 87 | `TextIOWrapper` has no attribute `stem` | Same shadowing issue — `gguf_path` typed as `Path | None` but assigned file handle |
| `llama_cpp_adapter/adapter.py` | 88 | `TextIOWrapper` assigned to `Path | None` | Same root cause |
| `llama_cpp_adapter/adapter.py` | 94 | `BufferedReader` assigned to `TextIOWrapper` | `gguf_path.open("rb")` returns `BufferedReader`, but variable may have been shadowed |
| `llama_cpp_adapter/adapter.py` | 105 | `int.from_bytes()` gets `str` | `buf[4:8]` is `bytes`, but mypy thinks it's `str` — likely because `buf` was reassigned from a file read |
| `llama_cpp_adapter/adapter.py` | 168 | Returning `Any` from function declared `str` | `create_completion` returns `Any`, need explicit `str()` cast or `# type: ignore` with justification |

- **S2.1**: Read `adapters/external/llama_cpp_adapter/adapter.py` lines 80-110 to identify variable shadowing
- **S2.2**: Fix variable names to prevent shadowing (`model_info_file` vs `gguf_path`, separate `buf` variable)
- **S2.3**: Add explicit `str()` return or type ignore with comment for line 168
- **S2.4**: Verify `conformance/base.py` line 14 has complete annotations
- **S2.5**: Run `mypy sovereignai/conformance/base.py adapters/external/llama_cpp_adapter/adapter.py` — must be zero errors

**Files will edit**: `sovereignai/conformance/base.py`, `adapters/external/llama_cpp_adapter/adapter.py`

---

## S3 — Fix detect-secrets CLI Flag
**Evidence**: Log 20.1 L4571 — `ambiguous option: --exclude could match --exclude-lines, --exclude-files, --exclude-secrets`

- **S3.1**: Find scan script or workflow using `--exclude` (should be `--exclude-files`)
- **S3.2**: Update to `--exclude-files` explicitly
- **S3.3**: Run `detect-secrets scan --all-files --exclude-files .venv/` — must pass

**Files will edit**: Scan script in `scripts/` or `.devin/workflows/`

---

## S4 — Address Ruff Errors (273 findings)
**Evidence**: Log 20.1 — "Ruff found 273 errors (mostly line length issues in test files). Continuing with mypy scan." The Executor continued despite errors. Per OR38/AGENTS.md, lint errors must be ≤ baseline or fixed.

- **S4.1**: Run `ruff check .` — record count and categories
- **S4.2**: Fix line-length issues in test files (E501) — use `# noqa: E501` for long strings where splitting hurts readability, or split lines
- **S4.3**: Fix any non-E501 ruff errors
- **S4.4**: Re-run `ruff check .` — must be ≤ Plan 20 baseline or zero

**Files will edit**: Test files with E501 violations

---

## S5 — Verify TeacherWorker Cleanup Completeness
**Evidence**: Log 20.1 L1067 — grep_search tool failed twice with invalid JSON. Executor deleted files but couldn't verify remaining references.

- **S5.1**: Run `grep -r "TeacherWorker" --include="*.py" .` (excluding `documents/`, `.venv/`)
- **S5.2**: Remove any remaining references in code files
- **S5.3**: Run tests to confirm no import errors

**Files will edit**: Any files with remaining `TeacherWorker` references

---

## S6 — Mandatory Re-Scan (Plan 20.2)
- **S6.1**: Run `pytest --cov=sovereignai --cov-report=term-missing` — must be ≥90%, no failures
- **S6.2**: Run `mypy` on all `.py` files edited — zero errors
- **S6.3**: Run `ruff check .` — record count, must be ≤ Plan 20 baseline
- **S6.4**: Run `bandit -r .` — update baseline if changed
- **S6.5**: Run `detect-secrets scan --all-files --exclude-files .venv/` — audit findings
- **S6.6**: Run `vulture .` — dead code check
- **S6.7**: Run `python scripts/ar_checks/check_placeholders.py` — zero placeholders
- **S6.8**: Run `python scripts/ar_checks/check_tracing.py` — universal tracing compliance
- **S6.9**: Run `python scripts/ar_checks/spec_match.py prompts/plan-20.2-Rev0.md` — mechanical gate, exit≠0 = STOP
- **S6.10**: Run `/verify`

---

## S7 — Update Documentation + Close
- **S7.1**: Update `CHANGELOG.md` with Plan 20.2 changes
- **S7.2**: Update `PLANS.md` baseline (test counts, coverage, ruff count)
- **S7.3**: Update `DEBT.md` — mark resolved items
- **S7.4**: Run `/verify`; run `/close`
