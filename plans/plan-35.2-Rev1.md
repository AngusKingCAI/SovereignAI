Depends on: Plan 35.1
Vision principles: P1 (Core sacred), P2 (Pluggable), P13 (Strong and robust)
AR rules: AR1, AR2
OR rules: UOR-1, VOR-1
Open questions resolved: DD-35.2.1, DD-35.2.2
**Revision**: Rev1

## Executor Manifest

**Plan**: 35.2
**Phases**: 4 (S1–S4; S0 excluded from count)
**Deliverables**:
| Phase | Deliverable | Verification |
|-------|-------------|--------------|
| S1 | `.agent/executor/.plan-lock.json` template format | Template file exists with all required fields |
| S2 | `.agent/executor/scripts/plan_lock.py` with lock management functions | `pytest .agent/executor/tests/test_plan_lock.py -v` passes |
| S3 | Updated `get_current_plan.py` to check lock file first | Manual verification: lock file checked before PLANS.md |
| S4 | Updated `verify_execution.py` and `verify_close.py` to use lock file | `pytest .agent/executor/tests/test_lock_verification.py -v` passes |

**Coverage target**: ≥90%
**Forbidden actions**: Do not modify `AI_HANDOFF.md`, `AGENTS.md`, `PRINCIPLES.md`, `OR_RULES.md`, `PLANS.md`, `DEBT.md`.
**Commit message**: `feat(executor): implement immutable plan identity lock system`

## S0 — Opening

S0.1: Run `/open`
S0.2: Read `AGENTS.md` in full. Read plan header AR rules from `.agent/executor/ARCHITECTURE.md`. Read plan header OR rules from `.agent/executor/OR_RULES.md`.
S0.3: Check `.agent/shared/DEBT.md` for deferred items.

## S1 — Create Lock File Template

S1.1: Create `.agent/executor/.plan-lock.json.template` with format:
  ```json
  {
    "plan_id": "{plan_id}",
    "plan_file": "plans/plan-{plan_id}-Rev{N}.md",
    "manifest_hash": "{sha256_of_manifest_section}",
    "session_token": "{human-generated-secret-32char}",
    "created_by": "human",
    "created_at": "{ISO8601_timestamp}",
    "expires_at": "{ISO8601_timestamp_7days_later}"
  }
  ```
S1.2: Document lock file creation process in AI_HANDOFF.md Section 8 (Devin Local Configuration)
S1.3: Verify template file exists and is valid JSON
S1.4: Test: `python -m json.tool .agent/executor/.plan-lock.json.template` must succeed

## S2 — Create plan_lock.py

S2.1: Create `.agent/executor/scripts/plan_lock.py` with functions:
  - `generate_lock(plan_id: str, plan_file: str, session_token: str) -> dict` — generates lock file content
  - `validate_lock(lock_path: str) -> tuple[bool, str]` — validates lock file exists, is valid JSON, not expired
  - `get_plan_id(lock_path: str) -> str` — extracts plan_id from lock file
  - `archive_lock(lock_path: str) -> str` — moves lock file to .agent/executor/archived-locks/
S2.2: Add manifest hash computation: `compute_manifest_hash(plan_file: str) -> str` using hashlib.sha256
S2.3: Add session token validation: 32-character alphanumeric string
S2.4: Add expiration check: expires_at must be within 7 days of created_at
S2.5: Test: `pytest .agent/executor/tests/test_plan_lock.py -v` — test_generate_lock, test_validate_lock, test_get_plan_id, test_archive_lock, test_manifest_hash_computation, test_session_token_validation, test_expiration_check

## S3 — Update get_current_plan.py

S3.1: Read `.agent/executor/scripts/get_current_plan.py`
S3.2: Add lock file check at function start: check `.agent/executor/.plan-lock.json` exists
S3.3: If lock file exists and is valid: return plan_id from lock file
S3.4: If lock file missing or invalid: fall back to PLANS.md (current behavior)
S3.5: Add logging: log when lock file is used vs fallback to PLANS.md
S3.6: Test: Manual verification with lock file present and absent
S3.7: Test: Verify lock file takes precedence over PLANS.md

## S4 — Update Verification Scripts

S4.1: Update `.agent/executor/scripts/verify_execution.py`:
  - REMOVE --plan argument from argparse
  - Read plan_id from `.agent/executor/.plan-lock.json` ONLY
  - If lock file missing or invalid: sys.exit(1) with error message
  - Add manifest hash chain verification: read trace file, verify all entries have same manifest_hash
  - Add lock file existence check to verification steps
S4.2: Update `.agent/executor/scripts/verify_close.py`:
  - Add lock file existence check
  - Add lock file validity check (not expired, valid JSON)
  - Add manifest hash verification against lock file
  - Add attestation existence check for locked plan
S4.3: Update `.agent/executor/hooks/preflight_check.py`:
  - Add lock file validation at session start
  - If lock file missing or invalid: warn but allow execution (for backward compatibility)
  - Log lock file status to trace
S4.4: Test: `pytest .agent/executor/tests/test_lock_verification.py -v` — test_verify_execution_reads_lock, test_verify_close_checks_lock, test_preflight_validates_lock
