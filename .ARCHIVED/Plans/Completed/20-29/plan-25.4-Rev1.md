Depends on: Plan 25.3 (baseline: 637 passed, 58 skipped, 0 failures)
Vision principles: P1 (Core sacred), P8 (UIs separate), P9 (Observability), P11 (DI only), P12 (No docstrings), P13 (Strong and robust)
AR rules: AR4, AR8, AR11, AR12, AR15
OR rules: UOR-1, UOR-2, COR-1
Open questions resolved: none

## S0 — Opening

S0.0: Clone latest repo. Verify Plan 25.3 completed (637 passed, 58 skipped).
S0.1: Run `/open`
S0.2: Read `AGENTS.md`, `PRINCIPLES.md`
S0.3: Read AR4, AR8, AR11, AR12, AR15 from `.agent/executor/ARCHITECTURE.md`. Read UOR-1, UOR-2, COR-1 from `.agent/executor/OR_RULES.md`.
S0.4: Read `.agent/shared/DEBT.md` — no debt items triggered.
S0.5: Read `.agent/shared/CHANGELOG.md` latest entry (prompt-25.3-rev1).

## S1 — TraceEmitter SSOT Fix (C1)

S1.1: Read `app/sovereignai/observability/trace_emitter.py` and `app/sovereignai/shared/trace_emitter.py`. Determine canonical (shared/ at 332 lines is authoritative).
S1.2: If `observability/` is stale duplicate: delete it. If re-export wrapper: verify imports from `shared/` and add comment `# Re-export — canonical in shared.trace_emitter`.
S1.3: `grep -r "from sovereignai.observability.trace_emitter" app/` and update all import sites to `sovereignai.shared.trace_emitter`.
S1.4: Run `/verify` on every edited file.

## S2 — Missing AR Check Scripts (C2)

S2.1: Create `.agent/executor/scripts/ar_checks/check_ar7_allowlist.py` — verify UI files in `app/web/` and `app/tui/` only import allowed `sovereignai.*` modules per AR12. Read allowlist from `test_tui_memory_panel_ar7.py`.
S2.2: Create `.agent/executor/scripts/ar_checks/check_component_manifest_kwargs.py` — verify adapter manifests declare `health_check()` in kwargs per AR15. Parse `manifest.toml` files in `app/adapters/`.
S2.3: Create `.agent/executor/scripts/ar_checks/check_rule_crossrefs.py` — verify every AR rule ID in `ARCHITECTURE.md` has corresponding check script OR is marked "Design-time". Exit 0 if consistent, exit 1 if orphaned.
S2.4: Update `ARCHITECTURE.md` verification table to reflect new scripts.
S2.5: Run `/verify` on each new script.

## S3 — print() → TraceEmitter Migration (C3)

S3.1: `grep -rn "print(" app/sovereignai/main.py app/tui/panels/*.py` to enumerate production print sites.
S3.2: Replace each `print()` with `TraceEmitter.emit()` at appropriate `TraceLevel` (ERROR for error handlers, DEBUG for debug/flush).
S3.3: Ensure `TraceEmitter` is imported. If not available via DI, inject via constructor (≤15 args per P11).
S3.4: Run `/verify` on every edited file.

## S4 — Docstring Removal (H1)

S4.1: `grep -rl '"""' app/sovereignai/ .agent/executor/scripts/ .agent/executor/tests/` to find files with triple-quoted strings.
S4.2: For each file, identify function/class/method docstrings (preceded by `def` or `class`). Remove ONLY docstrings; preserve string literals used as values.
S4.3: Skip test data fixtures with intentional string literals — verify before removal.
S4.4: Run `/verify` on every edited file.

## S5 — .gitignore Hardening (H2)

S5.1: Read `.gitignore`.
S5.2: Append if missing: `*.pyc`, `.secrets/`, `*.db`, `*.db-wal`, `*.db-shm`, `__pycache__/`.
S5.3: Run `git check-ignore -v app/sovereignai/__pycache__/test.pyc` to verify.
S5.4: Run `/verify` on `.gitignore`.

## S6 — Plan File Rev Self-Reference (H3)

S6.1: For each active plan in `prompts/` (plan-26-Rev5.md through plan-29-Rev5.md): add `**Revision**: Rev5` to header block.
S6.2: Verify no other Rev numbers appear (grep `Rev\d+`). If mismatched: STOP.
S6.3: Run `/verify` on each edited plan file.

## S7 — Empty __init__.py Audit (H4)

S7.1: `find app/ .agent/ -name "__init__.py" -size 0` to list empty files.
S7.2: For empty files in `app/sovereignai/` subpackages with actual modules: add minimal re-exports (e.g., `from .trace_emitter import TraceEmitter`).
S7.3: For leaf packages with no public API: add comment `# Namespace package marker`.
S7.4: For test `__init__.py` files: leave empty (standard pytest practice).
S7.5: Run `/verify` on every edited file.

## S8 — Adapter Manifest skill.py Backfill (M2)

S8.1: For each adapter in `app/adapters/external/` and `app/adapters/internal/` with `manifest.toml` but no `skill.py`:
  - Create `skill.py` with minimal adapter wrapper class declaring `health_check()` per AR15.
  - Add `dag.json` with `{"nodes": [], "edges": []}` per AR9.
S8.2: Run `/verify` on each new file.

## S9 — Placeholder Code Cleanup (M5)

S9.1: Replace `pass  # placeholder` in `test_ar_checks.py:133` with actual assertion or remove.
S9.2: For each `...` ellipsis in production code (`task_state_machine.py`, `capability_graph.py`): replace with `raise NotImplementedError` if unimplemented, or actual logic if stale.
S9.3: Run `/verify` on every edited file.

## S10 — Execution Log Cleanup (M6)

S10.1: Add `logs/execution-log-*.md` to `.gitignore`.
S10.2: Run `git rm --cached logs/execution-log-*.md` to stop tracking existing logs.
S10.3: Verify `.gitignore` blocks new log files: `git check-ignore -v logs/execution-log-test.md`.

## S11 — Suppression Cleanup (A3-A4, B1-B3, C1, D1-D7, E1-E7)

S11.1: **Stale skips**: In `test_ar7_no_core_imports_in_ui.py`, remove `pytest.skip` at lines 119, 135-138, 163-166 (UI dirs now exist). In `test_ar_checks.py`, update line 174 to match actual structure; remove line 180 if spec_match handles fix plans.
S11.2: **DI Protocol typing**: In `app/sovereignai/di/container.py`, add `TypeVar` bound to `Protocol` for `register_singleton()` and `retrieve()`. Remove `type: ignore[type-abstract]` from `main.py` (11) and `app/web/main.py` (11) as typing resolves. Run `mypy` on both files. STOP on error.
S11.3: **Compatibility matrix**: In `compatibility_matrix.py`, change return types to `str | StatusEnum` where `"unknown"` is returned. Remove 10 `type: ignore[no-any-return]` comments. Run `mypy`. STOP on error.
S11.4: **E501 line breaks**: Run `ruff check . --select E501`. Break all violations to ≤100 chars (parenthesize assertions, trailing comma in collections, wrap imports). Remove `noqa: E501` comments as fixed. Re-run `ruff`. STOP if any remain.
S11.5: **Silent failures**: For each `try/except: pass` in production code (`main.py:182,463`, `types.py:123`, `file_trace_subscriber.py:27`, `hardware_probe.py:35,71`, `event_bus.py:95,169`, `conformance/registry.py:20`, `skills/official/file_search/skill.py:90`): replace `pass` with `TraceEmitter.emit(..., trace_level=TraceLevel.ERROR)` or `logging.getLogger(__name__).error()` fallback.
S11.6: **Broad except narrowing**: For each `except Exception:` in production code (`main.py:476,516`, `file_trace_subscriber.py:41`, `trace_emitter.py:276`, `hardware_probe.py:51`, `event_bus.py:164,204,305,333`, `conformance/registry.py:31,33`, `orchestrator/dispatcher.py:114`): narrow to specific types (`OSError`, `ValueError`, `RuntimeError`, etc.).
S11.7: Run `/verify` on every edited file.

## S12 — AR Checks Integration

S12.1: Update `.agent/executor/scripts/ar_checks/run_all.py` to include new scripts from S2.
S12.2: Run `.agent/executor/scripts/ar_checks/run_all.py`. STOP on any failure.
S12.3: Run `pytest .agent/executor/tests/test_document_hygiene.py -v`.

## Closing

Run `/close`. Use COR-1: this plan has "fix" in title — run full test suite `pytest .agent/executor/tests/`.
