Depends on: Plan 34 (Persistent Graph Memory)
Vision principles: P1 (Core sacred), P2 (Pluggable), P9 (Observability), P13 (Strong and robust)
AR rules: AR1, AR2, AR8, AR10, AR11, AR12
OR rules: UOR-1, UOR-2, VOR-1, COR-2
Open questions resolved: DD-35.1, DD-35.2, DD-35.3
**Revision**: Rev1

## Executor Manifest

**Plan**: 35
**Phases**: 5 (S1–S5; S0 excluded from count)
**Deliverables**:
| Phase | Deliverable | Verification |
|-------|-------------|--------------|
| S1 | `.devin/hooks.v1.json` with Devin Local SWE 1.6 hook configuration | File exists, valid JSON, all required events configured |
| S2 | `.agent/executor/.plan-lock.json` template and `plan_lock.py` | `pytest .agent/executor/tests/test_plan_lock.py -v` passes |
| S3 | Updated `check_manifest.py` with fail-closed defaults | `pytest .agent/executor/tests/test_manifest_blocking.py -v` passes |
| S4 | Enhanced `append_trace.py` with hash chain and error categorization | `pytest .agent/executor/tests/test_trace_enhancement.py -v` passes |
| S5 | Updated all SKILL.md files with new hook references | Manual verification: all /open, /verify, /close, /scan reference hooks.v1.json |

**Coverage target**: ≥90%
**Forbidden actions**: Do not modify `AI_HANDOFF.md`, `AGENTS.md`, `PRINCIPLES.md`, `OR_RULES.md`, `PLANS.md`, `DEBT.md`.
**Commit message**: `feat(executor): add hard gating infrastructure, plan lock system, and trace enhancement`

## S0 — Opening

S0.1: Run `/open`
S0.2: Read `AGENTS.md` in full. Read plan header AR rules from `.agent/executor/ARCHITECTURE.md`. Read plan header OR rules from `.agent/executor/OR_RULES.md`.
S0.3: Check `.agent/shared/DEBT.md` for deferred items.
S0.4: **Prerequisite check**: verify Devin Local SWE 1.6 is installed and hooks.v1.json format is supported. Programmatic check: `devin --version` and verify hooks documentation exists. Record prerequisite as AGENTS.md trace entry per invariant #12: "S0.4 prerequisite: DEVIN_HOOKS_V1=supported|unsupported". If unsupported → STOP and require human to upgrade Devin.

## S1 — Devin Hook Infrastructure (Foundation)

S1.1: Create `.devin/hooks.v1.json` with official Devin Local SWE 1.6 hook format
S1.2: Configure PreToolUse hook: `python .agent/executor/hooks/hard_gate_pretooluse.py` — blocks unauthorized actions (exit code 2)
S1.3: Configure PostToolUse hook: `python .agent/executor/hooks/append_trace.py` — logs all tool calls to trace
S1.4: Configure SessionStart hook: `python .agent/executor/hooks/session_start.py` — validates plan lock file on session start
S1.5: Configure SessionEnd hook: `python .agent/executor/hooks/session_end.py` — generates attestation on session end
S1.6: Configure Stop hook: `python .agent/executor/hooks/session_stop.py` — validates all gates passed before allowing stop
S1.7: Configure PermissionRequest hook: `python .agent/executor/hooks/permission_request.py` — requires human approval for governance file edits
S1.8: Configure UserPromptSubmit hook: `python .agent/executor/hooks/context_injector.py` — injects plan context based on current task
S1.9: Migrate existing `.devin/config.json` hooks to new format (remove old hook entries, reference hooks.v1.json)
S1.10: Test: Verify hook file exists and is valid JSON; verify each hook script exists and is executable

## S2 — Plan Identity & Lock System

S2.1: Create `.agent/executor/.plan-lock.json` template format with fields: plan_id, plan_file, manifest_hash, session_token, created_by, created_at, expires_at
S2.2: Create `.agent/executor/scripts/plan_lock.py` with functions: generate_lock(), validate_lock(), get_plan_id(), archive_lock()
S2.3: Update `.agent/executor/scripts/get_current_plan.py` to check `.plan-lock.json` FIRST, fall back to PLANS.md only if missing
S2.4: Update `.agent/executor/scripts/verify_execution.py` to REMOVE --plan argument, read from lock file ONLY
S2.5: Update `.agent/executor/scripts/verify_close.py` to add lock file existence, validity, and hash verification
S2.6: Update `.agent/executor/hooks/preflight_check.py` to add lock file validation at session start
S2.7: Test: `pytest .agent/executor/tests/test_plan_lock.py -v` — test_generate_lock, test_validate_lock, test_get_plan_id, test_archive_lock, test_lock_file_fallback, test_verify_execution_reads_lock

## S3 — Hard Gates & Manifest Enforcement

S3.1: Update `.agent/executor/hooks/check_manifest.py` to change default from WARN to BLOCK (sys.exit(1))
S3.2: Add `--allow-exploratory` flag to check_manifest.py for legitimate out-of-scope write overrides
S3.3: Add governance file protection list to check_manifest.py: AI_HANDOFF.md, PRINCIPLES.md, OR_RULES.md, ARCHITECTURE.md, LANDMINES.md, PLANS.md, AGENTS.md — these always BLOCK unless --allow-exploratory
S3.4: Add file count limit to check_manifest.py: >5 files in single edit operation requires human approval
S3.5: Create `.agent/executor/scripts/governance_protection.py` with functions: is_governance_file(), validate_governance_edit(), block_unauthorized_governance_edit()
S3.6: Create `.agent/executor/scripts/human_gate.py` with functions: display_summary(), prompt_for_confirmation(), validate_confirmation()
S3.7: Update `.agent/executor/scripts/verify_close.py` to add all 10 governance files to check list, remove non-existent DECISIONS.md
S3.8: Update `.devin/skills/close/SKILL.md` to add Step 13.5 HUMAN GATE before git tag — display summary, wait for CONFIRM
S3.9: Add explicit instruction to close/SKILL.md: "If ANY verification fails: STOP. Do not commit. Do not tag."
S3.10: Test: `pytest .agent/executor/tests/test_manifest_blocking.py -v` — test_block_out_of_scope, test_allow_exploratory_flag, test_governance_file_protection, test_file_count_limit

## S4 — Trace Enhancement & Attestation Automation

S4.1: Update `.agent/executor/hooks/append_trace.py` to add manifest_hash to every trace entry
S4.2: Add prev_hash field to append_trace.py for cryptographic chain integrity (detect tampering)
S4.3: Add error_state field to append_trace.py: OK, ERROR, WARNING
S4.4: Add error_category field to append_trace.py: SYNTAX, TYPE, RUNTIME, LINT, IMPORT, TEST_FAILURE, BUILD_FAILURE
S4.5: Add error_message and recovery_action fields to append_trace.py
S4.6: Add input_tokens, output_tokens, cost_usd fields to append_trace.py for token tracking
S4.7: Add reasoning_step field to append_trace.py for context tracking
S4.8: Create `.agent/executor/scripts/auto_attest.py` with functions: read_trace(), compute_coverage(), compute_error_summary(), compute_token_summary(), compute_performance_summary(), generate_attestation(), sign_attestation()
S4.9: Update `.agent/executor/ATTESTATION_TEMPLATE.md` to add Error Summary, Token Usage, Performance Summary, Manifest Hash, Trace Integrity Hash sections
S4.10: Update `.agent/executor/scripts/verify_execution.py` to add trace completeness validation, manifest hash chain verification, error summary cross-check
S4.11: Update `.agent/executor/scripts/verify_attestation.py` to add data validation (cross-check against trace), hash verification, section completeness check
S4.12: Test: `pytest .agent/executor/tests/test_trace_enhancement.py -v` — test_manifest_hash_chain, test_error_categorization, test_token_tracking, test_auto_attestation_generation

## S5 — SKILL.md Updates & Integration

S5.1: Update `.devin/skills/open/SKILL.md` to reference hooks.v1.json and plan lock file creation
S5.2: Update `.devin/skills/verify/SKILL.md` to reference enhanced trace format and error categorization
S5.3: Update `.devin/skills/close/SKILL.md` to reference human confirmation gate and attestation automation
S5.4: Update `.devin/skills/scan/SKILL.md` to reference governance file protection and manifest checking
S5.5: Add Devin Local SWE 1.6 invariants to AGENTS.md: hooks are primary enforcement, PreToolUse blocks unauthorized actions, SessionStart validates plan identity, SessionEnd generates attestation
S5.6: Verify all SKILL.md files have consistent hook references
S5.7: Manual verification: Human reviews all updated SKILL.md files for consistency and completeness
