# Plan 20.5 — Governance Cleanup: CHANGELOG Discipline + Issue Review Fixes

Depends on: prompt-20.4
Vision principles: P4 (Modular core), P9 (Trust boundary), P14 (Audit everything)
Open questions resolved: none

**Note on length**: This plan exceeds the 120-line guideline because it addresses 29 findings from the Architect's logs-16+ issue review (3 CRITICAL, 11 HIGH, 11 MEDIUM, 4 LOW; H11 was withdrawn — see H11 WITHDRAWN note in issue review). Per OR19, splitting into 20.5/20.6/20.7 is an option if the User prefers strict compliance; this single-plan form is delivered per User request.

**Correction note**: Original draft had S2.10 (H11 — Plan 18 rev mismatch). H11 was withdrawn after Architect verified `prompts/completed/plan-18-Rev9.md` exists. The residual (stale log header line 4) is now L5 — handled in S4.5.

## WILL edit
- `AGENTS.md` — add OR73 (S0.3)
- `LANDMINES.md` — backfill L47-L53 (S0.3)
- `.devin/workflows/close.md` — add step 17.5 for `check_changelog.py` (S2.11)
- `scripts/ar_checks/check_changelog.py` — NEW, OR73 enforcement (S2.11)
- `scripts/ar_checks/check_test_mode_hooks.py` — NEW, L52 enforcement (S1.5)
- `scripts/ar_checks/spec_match.py` — revert P19 self-exemption (S1.2)
- `scripts/ar_checks/ui_does_not_touch_core.py` — remove `CORE_EXCEPTION` (S1.3)
- `scripts/ar_checks/no_context_bags.py` — fix AR5→AR6 mislabel (S4.2)
- `adapters/external/llama_cpp_adapter/manifest.toml` — replace placeholder hash (S1.1)
- `databases/hf_database/provider.py` — remove `SOVEREIGNAI_TEST_MODE` (S1.4)
- `sovereignai/main.py` — remove `SOVEREIGNAI_TEST_MODE` from `build_container` (S1.4)
- `tests/test_ar7_no_core_imports_in_ui.py` — revert P20.4 tui/panels allowlist (S2.2)
- `tests/test_spec_match_missing_in_diff.py` — revert P18 weakening (S2.2)
- `tests/test_hf_database.py` — restore P18 deleted assertion (S2.2)
- `web/main.py` — revert `WEB_MAIN_ALLOWED_IMPORTS` expansion (S2.2)
- `bandit-baseline.json`, `bandit/baseline.json` — REMOVE (S2.6)
- `=0.20.0` — REMOVE stray file (S3.1)
- `.gitignore` — add `=0.20.0` (S3.1)
- `documents/SovereignAI_UI_Specification_v1.1.md` — verify scope, `git rm` if out-of-scope (S3.2)
- `web/hardware_probe.py` — pynvml strategy decision (S3.5); add GPU path tests (S2.9)
- `tests/test_hardware_stream_endpoint_sse` — investigate IndexError (S3.3)
- `adapters/external/llama_cpp_adapter/` — add conformance tests (S3.7)
- `sovereignai/conformance/registry.py` — classify llama_cpp_adapter as first-party (S3.7)
- `txt/vulture-whitelist.txt` — audit + comment P20.2 additions (S3.8)
- `CHANGELOG.md` — prepend prompt-20.5 entry per OR73 (S5.3); fix prompt-20.4 entry 456→455 (S3.9)
- `PLANS.md` — update baseline + fix prompt-20.4 line (S3.9, S5.4)
- `DEBT.md` — add deferred items with target plans (S5.5)
- `prompts/plan-20.5-Rev0.md` — move to `completed/` at close (S5.6)
- `logs/execution-log-prompt-20.5.md` — NEW, full session log (S5.7)
- `logs/execution-log-prompt-20.3.md` — backfill actual content (S2.11)
- `logs/execution-log-prompt-18.md` — fix stale header line 4 (S4.5, was H11 → L5)
- `.gitattributes` — NEW, enforce LF (S4.1)

## WILL NOT edit
- Any file not listed above. If scope expands, STOP per OR10.

## S0 — Opening

S0.1: Run `/open`.
S0.2: Read `AGENTS.md` in full.
S0.2.5: This plan adds OR73 and backfills L47-L53 — re-read `AGENTS.md` and `LANDMINES.md` after S0.3.
S0.3: Add OR73 to `AGENTS.md` (verbatim text in `/home/z/my-project/download/AGENTS-OR73-patch.md` — copy verbatim). Add L47-L53 to `LANDMINES.md` (verbatim text in same patch file). Commit before any coding: `git add -A && git commit -m "docs: add OR73 and L47-L53 for governance cleanup"`. Per OR45, if quota interrupts after this commit, re-read plan + AGENTS.md before continuing.

## S1 — CRITICAL fixes

S1.1 (C1 — placeholder hash): Edit `adapters/external/llama_cpp_adapter/manifest.toml`. Replace `content_hash = "sha256:placeholder-external-adapter"` with the real SHA-256 of the adapter directory. Compute via: `python -c "import hashlib, pathlib; print('sha256:' + hashlib.sha256(b''.join(p.read_bytes() for p in sorted(pathlib.Path('adapters/external/llama_cpp_adapter').rglob('*.py')))).hexdigest())"`. `/verify`.

S1.2 (C2a — spec_match self-exemption): Edit `scripts/ar_checks/spec_match.py`. Remove the lines `and not p.startswith("scripts/ar_checks/")` and `and not p.startswith("logs/")` added in Plan 19. The script will now correctly flag its own presence in diffs — that is expected. The fix for AR-check scripts appearing in diffs is to commit them in a separate commit, not to exempt them. `/verify`.

S1.3 (C2b — CORE_EXCEPTION): Edit `scripts/ar_checks/ui_does_not_touch_core.py`. Remove the `CORE_EXCEPTION = "sovereignai/main.py"` line and any logic referencing it, added in Plan 20.4. If `sovereignai/main.py` legitimately needs to be in UI commits, the plan must split commits — not weaken the check. `/verify`.

S1.4 (C3 — SOVEREIGNAI_TEST_MODE): Edit `databases/hf_database/provider.py`. Remove the `SOVEREIGNAI_TEST_MODE` env-var early-returns from `list_models` (was `return []`) and `health_check` (was `return DatabaseStatus(available=True, version="test-mode")`). Edit `sovereignai/main.py`. Remove the `SOVEREIGNAI_TEST_MODE` branch from `build_container`. Fix the root cause: the web TestClient needs a properly-seeded test container, not a production escape hatch. If `test_options_panel` 500s after revert, fix the test fixture to seed a real container. `/verify`.

S1.5 (L52 enforcement): Create `scripts/ar_checks/check_test_mode_hooks.py`. Scan production code (`sovereignai/`, `databases/`, `services/`, `adapters/`, `web/`) for env-var branching patterns: `os.environ.get(...TEST_MODE...)`, `if os.getenv(...TEST...)`, `if _test_mode`, etc. Exit≠0 if found in any non-test file. `/verify`.

## S2 — HIGH fixes

S2.1 (H1 — spec_match defeat): After S1.2 reverts the self-exemption, `spec_match.py` will fail across plans 16-20.4 diffs. This is EXPECTED — the failures indicate real scope drift accumulated over 7 plans. Do NOT re-introduce the exemption. At `/close` step 16, run spec_match; document the failure in DEBT.md with target plan 20.6 (spec_match redesign + scope drift cleanup). Get User authorization per OR53 at S5.2.

S2.2 (H2, H3 — AR7 allowlist + AR-test weakening): Revert the following in this exact order, running `/verify` after each:
- `tests/test_ar7_no_core_imports_in_ui.py` — revert P20.4 tui/panels allowlist exception for `sovereignai.shared` (the `+10/-1` edit at P20.4 L1208).
- `tests/test_spec_match_missing_in_diff.py` — revert P18 weakening: restore `assert "Missing in diff" in result.stdout` without the `or "Unexpected in diff"` clause.
- `tests/test_hf_database.py` — restore P18 deleted assertion `assert call_args.kwargs["local_dir_use_symlinks"] is False`.
- `web/main.py` — revert `WEB_MAIN_ALLOWED_IMPORTS` expansion from P17 (remove `database_registry`, `service_registry` from the allowlist).
- If reverting any of these causes the underlying code to fail, FIX THE CODE, not the test. If the code fix is non-trivial, STOP per OR19 and request an Architect-issued Rev.

S2.3 (H4 — OR57 browser smoke): Manually run browser smoke tests for Plan 16 (Logs panel) and Plan 17 (Options panel) UI surfaces. Start the web app: `python -m web.main`. Open `http://localhost:8000` in a browser. Take screenshots of: Logs panel with SSE streaming, Options panel with database/service status. Save to `logs/screenshots/prompt-20.5-smoke-{logs,options}.png`. Attach to `logs/execution-log-prompt-20.5.md`. If UI is broken, fix in this plan (add the broken file to WILL edit list, `/verify`).

S2.4 (H5 — LANDMINES backfill): Already done in S0.3 (L47-L53 added). Verify LANDMINES.md append-only: `git diff LANDMINES.md` should show only additions.

S2.5 (H6 — 156 mypy errors): Document in DEBT.md with target plan 20.7 (type remediation). Entry: `**Deferred at**: prompt-20.5 | **Reason**: 156 mypy errors across 29 files accumulated since plans 16-20.4 (per Plan 20.2 log L5414). Per OR53, no "pre-existing" exemption. | **Trigger condition**: When type remediation plan is scheduled. | **Target plan**: 20.7`. Do NOT attempt to fix in this plan — out of scope. Get User authorization at S5.2.

S2.6 (H7 — bandit baselines): `rm bandit-baseline.json` (root). `rm -r bandit/` (directory). Check `.gitignore` for `bandit/` entry — if present, leave it; if not, do not add. Re-run bandit without baseline: `bandit -r . -ll --exclude .venv/,tests/`. Triage findings: fix, `# nosec BXXX  # <reason>` with comment, or DEBT-document with target plan. `/verify`.

S2.7 (H8 — plan file immutability): Defer full pre-commit hook to plan 20.8. For this plan, document intent in DEBT.md: `**Deferred at**: prompt-20.5 | **Reason**: Plan file immutability hook (block edits to prompts/plan-*.md during execution) needs pre-commit infrastructure. | **Target plan**: 20.8`. Do NOT implement the hook in this plan.

S2.8 (H9 — Plan 20 S1 verification): Re-run `pytest tests/test_llama_cpp_adapter.py tests/test_first_run_adapter_check.py -vvv`. Confirm 6 + 4 = 10 tests pass. If failures, the headline task of Plan 20 was NOT actually resolved — fix in this plan. `/verify`.

S2.9 (H10 — coverage): Add tests for `web/hardware_probe.py` GPU paths (mock strategy: mock `subprocess.run` for `nvidia-smi`, mock `pynvml`/`nvidia-ml-py` imports). Target ≥90% coverage on `hardware_probe.py`. Run `pytest tests/test_hardware_probe.py --cov=web/hardware_probe --cov-report=term-missing`. If mocking strategy can't reach 90%, document in DEBT.md with target plan 20.9 (GPU testing infrastructure). `/verify`.

S2.10 (H12 — P20.3 execution log stub): The in-repo `logs/execution-log-prompt-20.3.md` is a 26-token stub (per P20.3 log L1254-1256). If the original session log is available (check executor's local terminal scrollback or `/tmp/` artifacts), write the actual content to the file. If unavailable, document in DEBT.md: `**Deferred at**: prompt-20.5 | **Reason**: Original P20.3 execution log content unrecoverable. In-repo file is a 26-token stub. | **Target plan**: N/A (irreversible)`.

S2.11 (H1 meta — check_changelog): Create `scripts/ar_checks/check_changelog.py` per the spec in `/home/z/my-project/download/AGENTS-OR73-patch.md`. Test: `python scripts/ar_checks/check_changelog.py 20.4` should pass (prompt-20.4 entry is at top of CHANGELOG). `python scripts/ar_checks/check_changelog.py 99` should fail (no such entry). Edit `.devin/workflows/close.md` to add step 17.5 between current step 17 and 18: `17.5. Run python scripts/ar_checks/check_changelog.py <plan_number>. Exit≠0 = STOP per OR73.` `/verify`.

> **Withdrawn**: S2.10 (originally H11 — Plan 18 rev mismatch) was removed after Architect verified `prompts/completed/plan-18-Rev9.md` exists. Residual stale header line is L5, handled in S4.5. Subsequent S2 task numbers shifted down by 1 (H12 became S2.10, H1-meta became S2.11).

## S3 — MEDIUM fixes

S3.1 (M1): `rm =0.20.0`. Add `=0.20.0` to `.gitignore`. `/verify`.
S3.2 (M2): Inspect `documents/SovereignAI_UI_Specification_v1.1.md`. Check if it was in P20.2's declared scope (read `prompts/completed/plan-20.2-Rev0.md` WILL edit list). If out of scope, `git rm documents/SovereignAI_UI_Specification_v1.1.md`. If in scope, leave with a note in CHANGELOG.
S3.3 (M3): Investigate `PytestUnhandledThreadExceptionWarning: IndexError: pop from empty list` in `tests/test_web_ui_panels.py::test_hardware_stream_endpoint_sse` (per P20.2 log L5280, L6493). Likely thread-safety issue in the SSE infinite-loop generator. Read `web/main.py` `/api/hardware/stream` endpoint and `capability_api.stream_hardware()`. Fix: either bound the generator or use `client.stream()` in the test. If fix is non-trivial, DEBT-document with target plan 20.10. `/verify`.
S3.4 (M4): For each pip-audit CVE in DEBT.md (setuptools ×5 from P18, diskcache ×1 from P20.1): confirm transitive dep status via `pip show <pkg>` and `pip-audit -r txt/requirements.txt`. Edit DEBT.md entries to replace `TBD` with explicit target plan: `20.11` (dependency upgrade plan). `/verify`.
S3.5 (M5): Edit `web/hardware_probe.py`. Decide pynvml strategy: (a) drop pynvml fallback entirely — commit to `nvidia-ml-py` only; OR (b) keep dual-import with a deprecation timeline comment. Architect recommends (a) per P14 (audit everything — dual-import is harder to audit). Remove the `FutureWarning` source. `/verify`.
S3.6 (M6): Out of scope (Architect decision). Document in DEBT.md: `**Deferred at**: prompt-20.5 | **Reason**: AR6 violations 5+ plans old (deferred since prompt-15.1; 14-15 violations across memory backends, routing_engine, librarian, conformance/). Needs Architect decision: refactor (major memory system plan) or retire AR6. | **Target plan**: Architect next session`. Do NOT attempt to fix.
S3.7 (M7): Add conformance tests for `adapters/external/llama_cpp_adapter/` in `tests/conformance/test_adapter.py` (or new `test_llama_cpp_conformance.py`). Update `sovereignai/conformance/registry.py` to classify `llama_cpp_adapter` as first-party (fail-closed per OR35, not fail-open per F2). The P19 log L4517 warning `[warn] conformance: Third-party component llama_cpp_adapter has no conformance tests ... allowing registration (fail-open per F2)` must not recur. `/verify`.
S3.8 (M8): Audit `txt/vulture-whitelist.txt` additions from P20.2 (+76 entries, per P20.2 log L6298). For each entry: add a trailing comment explaining why the flagged code is intentionally retained (`# <file>:<line> <reason>`). Remove entries that are legitimate dead code (fix the code instead). `/verify`.
S3.9 (M9): Edit `CHANGELOG.md` prompt-20.4 entry. Change `**Tests**: 456 passed, 5 skipped` to `**Tests**: 455 passed, 1 deselected (spec_match — see Plan 20.5 H1), 5 skipped`. Edit `PLANS.md` prompt-20.4 line similarly. Per OR55, CHANGELOG must not claim unshipped scope. `/verify`.
S3.10 (M10): Reconcile bandit headline vs metrics. The `-ll` flag filters everything below Low severity, but the metrics block still enumerates them. Document bandit invocation convention in `.devin/workflows/close.md` step 4: `bandit -r . -ll --exclude .venv/,tests/ -f json -o bandit-report.json || true; bandit -r . -ll --exclude .venv/,tests/`. The first run captures metrics; the second prints headline. `/verify`.
S3.11 (M11): Re-run each AR-check script independently: `python scripts/ar_checks/no_globals.py`, `python scripts/ar_checks/constructor_arg_cap.py`, `python scripts/ar_checks/no_context_bags.py`, `python scripts/ar_checks/check_tracing.py`, `python scripts/ar_checks/check_placeholders.py`, `python scripts/ar_checks/check_p4_compliance.py`, `python scripts/ar_checks/spec_match.py 20.5`. Confirm output differs between scripts. If outputs are byte-identical (per P20.4 log L3964-3999), investigate caching/piping — likely a subprocess stdout capture bug. Fix or DEBT-document with target plan 20.12. `/verify`.

## S4 — LOW fixes

S4.1 (L1): Create `.gitattributes` with content: `* text=auto eol=lf` and `*.png binary` and `*.db binary`. Commit.
S4.2 (L2): Edit `scripts/ar_checks/no_context_bags.py`. Fix the output label from `AR5: no constructors exceed 15 args.` to `AR6: no context bags violations.` (per P20.4 log L3959).
S4.3 (L3): Edit `.devin/workflows/close.md`. Add a note in step 17 (move plan to completed): `If git mv fails with "bad source", use plain mv then git add -A. Per L23, mv + git add -A is safe (git add -A catches the rename).`
S4.4 (L4): Document L53 (already added in S0.3) as the landmine. Defer the OR to plan 20.8 (hook infrastructure). For this plan, just be disciplined: any task-list denominator change gets a one-line reason in the execution log.

S4.5 (L5 — was H11): Edit `logs/execution-log-prompt-18.md` line 4. Change `**Plan**: prompts/plan-18-Rev4.md` to `**Plan**: prompts/completed/plan-18-Rev9.md`. This is a cosmetic header fix; the plan was correctly executed against Rev9 (the latest). Originally flagged as H11 (HIGH) but downgraded to L5 after Architect verified Rev9 exists in `prompts/completed/`. `/verify`.

## S5 — Closing

S5.1: Run full scan suite ONE AT A TIME per OR3 (no parallel):
- pytest: `.venv/Scripts/pytest.exe tests/ -vvv --cov=. --cov-report=term-missing`. Expected failures from S2 reverts (spec_match, possibly AR7 if allowlist revert breaks code). Document each per OR53.
- ruff: `.venv/Scripts/ruff.exe check .`
- mypy: file-scoped only per OR2, on each edited file
- bandit: `bandit -r . -ll --exclude .venv/,tests/` (WITHOUT baseline, per S2.6)
- pip-audit: `pip-audit -r txt/requirements.txt`
- vulture: `vulture . --min-confidence 80 --exclude .venv/`
- detect-secrets: `detect-secrets scan --exclude-files .venv/ --baseline txt/.secrets.baseline`
- AR checks: run each in `scripts/ar_checks/` (including NEW `check_changelog.py 20.5` and `check_test_mode_hooks.py`)

S5.2: Per OR53, get User authorization for any unfixed failures. Expected: spec_match (per S2.1, target plan 20.6), mypy 156 errors (per S2.5, target plan 20.7). Any others = STOP per OR19.

S5.3: Prepend CHANGELOG entry per OR73. Entry must include: `## prompt-20.5 — Governance Cleanup`, `**Date**:`, `**Plan file**:`, `**Tests**:`, `**Coverage**:`, and ≥1 bullet of shipped scope. Echo verbatim entry text in `logs/execution-log-prompt-20.5.md` (NOT just `+N` line count — this is the OR73 enforcement point).

S5.4: Update `PLANS.md` baseline: `**Current**: <N> tests (Plan 20.5 /close)`. Update Plan 20.5 line: `**Plan 20.5**: Baseline → <N> tests. Delta: <+/-N> — see CHANGELOG prompt-20.5.`

S5.5: Update `DEBT.md` with all deferred items from S2/S3. Each entry must have explicit target plan (not `TBD`): 20.6 (spec_match redesign), 20.7 (mypy remediation), 20.8 (pre-commit hooks), 20.9 (GPU tests), 20.10 (SSE thread safety), 20.11 (CVE dependency upgrades), 20.12 (AR-check output caching investigation). For S2.10 (Plan 18 rev mismatch) and S3.6 (AR6 retirement decision): target = "Architect next session".

S5.6: `git mv prompts/plan-20.5-Rev0.md prompts/completed/` (if `git mv` fails, use `mv` + `git add -A` per L4.3).

S5.7: Write `logs/execution-log-prompt-20.5.md` with full session log. Echo verbatim CHANGELOG entry per OR73. Include screenshots from S2.3 if applicable.

S5.8: Run `/close`. Verify step 17.5 (NEW `check_changelog.py 20.5`) passes per OR73. If step 17.5 fails, STOP — do not tag.

S5.9: After `/close` passes, `git tag prompt-20.5` and `git push origin main --tags`. Verify tag on remote: `git ls-remote --tags origin | grep prompt-20.5`.
