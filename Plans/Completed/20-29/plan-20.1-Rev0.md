Depends on: prompt-20
Vision principles: P2, P4, P6, P9, P13

S0 — Opening
- S0.1: Run `/open`
- S0.2: Read `AGENTS.md` in full
- S0.3: Add new rules if governance patch needed; commit before coding

S1 — Fix Scan Infrastructure + Coverage Gap
- S1.1: Revert spec_match.py to original (undo Devin's prompt-20 patch); fix plan format to use "Depends on: prompt-19" instead
- S1.2: Add tests for hardware_probe.py GPU paths — mock nvidia-ml-py/nvmlDeviceGetMemoryInfo, nvmlDeviceGetUtilizationRates, nvmlDeviceGetName to achieve ≥90% coverage
- S1.3: Add regression tests for pynvml→nvidia-ml-py migration and HfApi.list_models() direction param removal
- S1.4: Run `pytest --cov=sovereignai --cov-report=term-missing` — coverage must be ≥90%; run `/verify`

**Files will edit**: `scripts/ar_checks/spec_match.py`, `web/hardware_probe.py`, `tests/test_hardware_probe.py`, `tests/test_hf_database.py`, `tests/test_ar_checks.py`

S2 — Fix Missing Scan Scripts + Small DEBT
- S2.1: Fix scan script paths — update scan protocol to use `scripts/ar_checks/` path; verify check_placeholders.py and check_tracing.py run correctly
- S2.2: Remove TeacherWorker implementation and all tests (completed per user request)
- S2.3: Fix GPU bandwidth lookup — add exact PCI-ID mapping for RTX 3060 Laptop and common GPUs to hardware_probe.py, remove substring matching
- S2.4: Add generate() metadata-only path documentation to llama_cpp_adapter.py docstring

S3 — Mandatory Re-Scan (Plan 20.1)
- S3.1: Run `ruff check .` — record count, must be ≤ Plan 20 count
- S3.2: Run `mypy` on all `.py` files edited — zero errors
- S3.3: Run `bandit -r .` — update baseline if changed
- S3.4: Run `detect-secrets scan --all-files --exclude .venv/` — audit findings
- S3.5: Run `vulture .` — dead code check, must be ≤ Plan 20 findings
- S3.6: Run `pytest --cov=sovereignai --cov-report=term-missing` — coverage ≥90%, do NOT STOP until achieved
- S3.7: Run `python scripts/ar_checks/check_placeholders.py` — zero placeholders
- S3.8: Run `python scripts/ar_checks/check_tracing.py` — universal tracing compliance
- S3.9: Run `python scripts/ar_checks/spec_match.py prompts/plan-20.1-Rev0.md` — mechanical gate, exit≠0 = STOP
- S3.10: Run `/verify`

S4 — Update Documentation + Close
- S4.1: Update `CHANGELOG.md` with Plan 20.1 changes
- S4.2: Update `PLANS.md` baseline (test counts, coverage, bandit count)
- S4.3: Update `DEBT.md` — mark resolved items with "Resolved at: prompt-20.1"
- S4.4: Run `/verify`; run `/close`

---

Brief (≤80 lines)

1. Context: Plan 20 completed but left critical gaps: coverage 83% (below 90% target), scan scripts called from wrong path, spec_match.py patched instead of fixed, TeacherWorker tests still failing, GPU bandwidth placeholder inaccurate, DEBT items unresolved. Plan 20.1 is a cleanup plan to finish what Plan 20 missed.

2. Plans in this batch: Plan 20.1 only — fix scan infrastructure, coverage gap, TeacherWorker tests, small DEBT items.

3. Decisions proposed: DD-20.1.1 — Revert spec_match.py ALLOWLIST patch, use correct "Depends on: prompt-19" format (rejected: keep patched script). DD-20.1.2 — Mock nvidia-ml-py for GPU path tests instead of deferring to hardware testing (rejected: defer to hardware testing plan). DD-20.1.3 — Fix TeacherWorker.curate_dataset() signature now rather than in Education plan (rejected: defer to Education department plan).

4. Decisions carried forward: DD-1 through DD-20.

5. Questions for Round Table: None — cleanup plan, no new architectural decisions.

6. Open questions resolved: None.

7. Risks flagged: L1 (replace_all), L8 (scope creep — limit to small fixes only). Pre-screened: no new landmines introduced.

8. Coverage target: ≥90% at /close. Do NOT STOP until achieved.

9. Round Table protocol: Not required — scan/cleanup plan per handoff rules.

10. Superseded decisions: None.
