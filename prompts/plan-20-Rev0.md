Depends on: prompt-19
Vision principles: P2, P4, P6, P9, P13

WILL edit:
- `sovereignai/shared/hardware_probe.py`
- `databases/hf_database/provider.py`
- `txt/requirements.txt`
- `prompts/plan-20-Rev0.md`
- `PLANS.md`
- `CHANGELOG.md`
- `.gitignore` (pre-existing drift from intermediate commits)
- `bandit/baseline.json` (pre-existing drift from intermediate commits)
- `bandit/report.json` (pre-existing drift from intermediate commits)
- `documents/ollama-scraper-architecture.md` (pre-existing drift from intermediate commits)

WILL NOT edit:
- All other files

S0 — Opening
- S0.1: Run `/open`
- S0.2: Read `AGENTS.md` in full
- S0.3: Add new rules if governance patch needed; commit before coding

S1 — Fix Llama.cpp Adapter Test Failures
- S1.1: Fix `RecursionError` in `test_load_model_no_gpu` — correct mock setup to avoid infinite recursion
- S1.2: Fix `AttributeError` on `llama_cpp` module — correct mock target path to `sovereignai.adapters.external.llama_cpp_adapter.llama_cpp`
- S1.3: Fix `AdapterUnavailableError` message mismatch — ensure "No GGUF files found" matches test expectation
- S1.4: Fix `TypeError` on `open_side_effect()` — add `path` and `mode` positional args to mock function
- S1.5: Run `pytest tests/test_llama_cpp_adapter.py -vvv` — all must pass; run `/verify`

S2 — Fix First-Run Auth + pynvml + Options HF
- S2.1: Fix `AdapterHealth` return type — return typed `AdapterHealth` dataclass, not raw `bool`
- S2.2: Fix auth endpoint 401 vs 200 — ensure `/api/auth/status` returns 200 with valid session
- S2.3: Replace `pynvml` with `nvidia-ml-py` in dependencies, update all imports
- S2.4: Fix `HfApi.list_models()` `direction` parameter — remove deprecated param causing Options panel error
- S2.5: Run `pytest tests/test_first_run_adapter_check.py -vvv` — all must pass; run `/verify`

S3 — Mandatory Scan (Plan 20)
- S3.1: Run `ruff check .` — record count
- S3.2: Run `mypy` on all `.py` files edited — zero errors
- S3.3: Run `bandit -r .` — update baseline if changed
- S3.4: Run `detect-secrets scan --all-files --exclude .venv/` — audit findings
- S3.5: Run `vulture .` — dead code check
- S3.6: Run `pytest --cov=sovereignai --cov-report=term-missing` — coverage ≥90%
- S3.7: Run `python scripts/check_placeholders.py` — zero placeholders in shipped code
- S3.8: Run `python scripts/check_tracing.py` — universal tracing compliance
- S3.9: Run `python scripts/spec_match.py` — mechanical gate, exit≠0 = STOP
- S3.10: Browser smoke test — open http://localhost:8000, verify all 10 panels load without server errors
- S3.11: Screenshot each panel to execution log; run `/verify`

S4 — Update Documentation + Close
- S4.1: Update `CHANGELOG.md` with Plan 20 changes
- S4.2: Update `PLANS.md` baseline (test counts, coverage, bandit count)
- S4.3: Any new landmines found → add to `LANDMINES.md`
- S4.4: Run `/verify`; run `/close`

---

Brief (≤80 lines)

1. Context: Plan 19 completed with 407 passed, 12 skipped, 90% coverage. Critical bugs remain: llama.cpp adapter tests (RecursionError, AttributeError, TypeError, AssertionError), first-run auth (401 vs 200, bool.healthy), pynvml deprecation, HfApi.list_models direction error. UI overhaul deferred to Plans 21-24 per user request.

2. Plans in this batch: Plan 20 only — scan + critical bug fixes.

3. Decisions proposed: DD-20.1 — Remove deprecated HfApi.list_models direction parameter (rejected: pin older hfapi version). DD-20.2 — Replace pynvml with nvidia-ml-py now rather than dedicated plan (rejected: defer to dependency plan).

4. Decisions carried forward: DD-1 through DD-19.

5. Questions for Round Table: Q-20.1 — Should we add regression tests for the llama.cpp mock fixes to prevent recurrence?

6. Open questions resolved: None.

7. Risks flagged: L1 (replace_all), L8 (scope drift — UI fixes deferred per user request). Pre-screened: all blocking landmines addressed.

8. Coverage target: ≥90% at /close.

9. Round Table protocol: Full prompt first pass, diff-summary for re-checks.

10. Superseded decisions: None.
