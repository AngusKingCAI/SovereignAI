Depends on: Plan 35.2
Vision principles: P1 (Core sacred), P11 (Fail-safe), P13 (Strong and robust)
AR rules: AR1, AR8, AR11
OR rules: UOR-1, UOR-2, COR-2
Open questions resolved: DD-35.3.1, DD-35.3.2
**Revision**: Rev1

## Executor Manifest

**Plan**: 35.3
**Phases**: 4 (S1–S4; S0 excluded from count)
**Deliverables**:
| Phase | Deliverable | Verification |
|-------|-------------|--------------|
| S1 | Updated `check_manifest.py` with fail-closed defaults | `pytest .agent/executor/tests/test_manifest_blocking.py -v` passes |
| S2 | `governance_protection.py` and `human_gate.py` scripts | Scripts exist, functions work correctly |
| S3 | Updated `verify_close.py` with complete governance file list | Manual verification: all 10 files checked |
| S4 | Updated `close/SKILL.md` with human confirmation gate | SKILL.md includes Step 13.5 HUMAN GATE |

**Coverage target**: ≥90%
**Forbidden actions**: Do not modify `AI_HANDOFF.md`, `AGENTS.md`, `PRINCIPLES.md`, `OR_RULES.md`, `PLANS.md`, `DEBT.md`.
**Commit message**: `feat(executor): implement fail-closed manifest enforcement and human confirmation gates`

## S0 — Opening

S0.1: Run `/open`
S0.2: Read `AGENTS.md` in full. Read plan header AR rules from `.agent/executor/ARCHITECTURE.md`. Read plan header OR rules from `.agent/executor/OR_RULES.md`.
S0.3: Check `.agent/shared/DEBT.md` for deferred items.

## S1 — Update check_manifest.py

S1.1: Read `.agent/executor/hooks/check_manifest.py`
S1.2: Change line 124 from `sys.exit(0)` (WARN) to `sys.exit(1)` (BLOCK) for out-of-scope files
S1.3: Add `--allow-exploratory` flag to argparse for legitimate out-of-scope write overrides
S1.4: Add governance file protection list: AI_HANDOFF.md, PRINCIPLES.md, OR_RULES.md, ARCHITECTURE.md, LANDMINES.md, PLANS.md, AGENTS.md
S1.5: Governance files always BLOCK unless --allow-exploratory flag is present
S1.6: Add file count limit: if >5 files in single edit operation, require human approval (sys.exit(1))
S1.7: Update warning messages to be explicit about BLOCK vs WARN behavior
S1.8: Test: `pytest .agent/executor/tests/test_manifest_blocking.py -v` — test_block_out_of_scope, test_allow_exploratory_flag, test_governance_file_protection, test_file_count_limit

## S2 — Create Protection Scripts

S2.1: Create `.agent/executor/scripts/governance_protection.py`:
  - `is_governance_file(file_path: str) -> bool` — checks if file is in governance protection list
  - `validate_governance_edit(file_path: str, edit_type: str) -> tuple[bool, str]` — validates if edit is allowed
  - `block_unauthorized_governance_edit(file_path: str) -> None` — blocks edit and logs error
S2.2: Create `.agent/executor/scripts/human_gate.py`:
  - `display_summary(plan_id: str, attestation_status: str, trace_status: str, test_results: str) -> None` — displays execution summary
  - `prompt_for_confirmation() -> bool` — prompts human for CONFIRM, returns True/False
  - `validate_confirmation(user_input: str) -> bool` — validates input is "CONFIRM" (case-sensitive)
S2.3: Add logging to both scripts for audit trail
S2.4: Test: Manual verification of script functions
S2.5: Test: `python .agent/executor/scripts/governance_protection.py --test` must succeed
S2.6: Test: `python .agent/executor/scripts/human_gate.py --test` must succeed

## S3 — Update verify_close.py

S3.1: Read `.agent/executor/scripts/verify_close.py`
S3.2: Remove non-existent DECISIONS.md from governance file list
S3.3: Add missing governance files: OR_RULES.md, ARCHITECTURE.md, AI_HANDOFF.md, ARCHITECT_PATTERNS.md, CHANGELOG.md
S3.4: Verify governance file list has exactly 10 files:
  - AGENTS.md
  - .agent/shared/LANDMINES.md
  - .agent/architect/PRINCIPLES.md
  - .agent/executor/OR_RULES.md
  - .agent/executor/ARCHITECTURE.md
  - .agent/architect/AI_HANDOFF.md
  - .agent/architect/ARCHITECT_PATTERNS.md
  - .agent/shared/CHANGELOG.md
  - .agent/shared/PLANS.md
  - .agent/shared/DEBT.md
S3.5: Add lock file existence check
S3.6: Add attestation existence check for locked plan
S3.7: Add trace completeness check (all manifest phases present)
S3.8: Test: Manual verification of updated check list
S3.9: Test: `python .agent/executor/scripts/verify_close.py --test` must succeed

## S4 — Update close/SKILL.md

S4.1: Read `.devin/skills/close/SKILL.md`
S4.2: Add Step 13.5: HUMAN GATE before git tag
  - Display execution summary: plan being closed, attestation status, trace coverage, test results
  - Prompt human: "Human: Review summary above. Type CONFIRM to proceed with git tag, or STOP to halt."
  - Wait for human input
  - If input != "CONFIRM": STOP execution, do not commit, do not tag
S4.3: Add explicit instruction after Step 10: "If ANY verification fails: STOP. Do not commit. Do not tag."
S4.4: Update Step 14 to reference lock file instead of --plan argument
S4.5: Update Step 12 to reference auto_attest.py for attestation generation
S4.6: Manual verification: Human reviews updated SKILL.md for completeness
S4.7: Test: Manual run of /close with human confirmation gate
