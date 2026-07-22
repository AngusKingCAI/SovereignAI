Depends on: Plan 35.1, Plan 35.2
Vision principles: P9 (Observability), P13 (Strong and robust)
AR rules: AR8, AR12
OR rules: UOR-1, VOR-1
Open questions resolved: DD-35.4.1, DD-35.4.2, DD-35.4.3
**Revision**: Rev1

## Executor Manifest

**Plan**: 35.4
**Phases**: 4 (S1–S4; S0 excluded from count)
**Deliverables**:
| Phase | Deliverable | Verification |
|-------|-------------|--------------|
| S1 | Enhanced `append_trace.py` with hash chain and error categorization | `pytest .agent/executor/tests/test_trace_enhancement.py -v` passes |
| S2 | `auto_attest.py` script for automated attestation generation | Script generates valid attestation from trace |
| S3 | Updated `ATTESTATION_TEMPLATE.md` with new sections | Template has Error Summary, Token Usage, Performance Summary sections |
| S4 | Updated `verify_execution.py` and `verify_attestation.py` with trace validation | Trace completeness and hash chain verification working |

**Coverage target**: ≥90%
**Forbidden actions**: Do not modify `AI_HANDOFF.md`, `AGENTS.md`, `PRINCIPLES.md`, `OR_RULES.md`, `PLANS.md`, `DEBT.md`.
**Commit message**: `feat(executor): implement trace enhancement with hash chain, error categorization, and automated attestation`

## S0 — Opening

S0.1: Run `/open`
S0.2: Read `AGENTS.md` in full. Read plan header AR rules from `.agent/executor/ARCHITECTURE.md`. Read plan header OR rules from `.agent/executor/OR_RULES.md`.
S0.3: Check `.agent/shared/DEBT.md` for deferred items.

## S1 — Enhance append_trace.py

S1.1: Read `.agent/executor/hooks/append_trace.py`
S1.2: Add manifest_hash field to every trace entry (read from lock file or compute from plan)
S1.3: Add prev_hash field for cryptographic chain: hash of previous entry's entry_hash
S1.4: Add entry_hash field: SHA256 of current entry (excluding entry_hash itself)
S1.5: Add error_state field: OK, ERROR, WARNING
S1.6: Add error_category field: SYNTAX, TYPE, RUNTIME, LINT, IMPORT, TEST_FAILURE, BUILD_FAILURE
S1.7: Add error_message field: error text if error_state != OK
S1.8: Add recovery_action field: action taken to recover from error
S1.9: Add input_tokens field: estimated input tokens for tool call (0 if not available)
S1.10: Add output_tokens field: estimated output tokens for tool call (0 if not available)
S1.11: Add cost_usd field: estimated cost in USD (0 if not available)
S1.12: Add reasoning_step field: step number in reasoning chain
S1.13: Update trace entry format documentation in code comments
S1.14: Test: `pytest .agent/executor/tests/test_trace_enhancement.py -v` — test_manifest_hash_chain, test_error_categorization, test_token_tracking, test_cryptographic_integrity

## S2 — Create auto_attest.py

S2.1: Create `.agent/executor/scripts/auto_attest.py` with functions:
  - `read_trace(trace_path: str) -> list[dict]` — reads and parses trace JSONL file
  - `compute_coverage(trace: list[dict], manifest_phases: list[str]) -> dict` — computes phase coverage percentage
  - `compute_error_summary(trace: list[dict]) -> dict` — groups errors by category, counts total, new, resolved
  - `compute_token_summary(trace: list[dict]) -> dict` — sums input/output tokens, estimates total cost
  - `compute_performance_summary(trace: list[dict]) -> dict` — calculates execution time, slowest phase
  - `generate_attestation(trace: list[dict], template_path: str, output_path: str) -> None` — fills attestation template
  - `sign_attestation(attestation_path: str) -> str` — generates integrity hash for attestation
S2.2: Add error categorization logic: group by error_category, count occurrences
S2.3: Add token estimation logic: use $0.003 per 1K input tokens, $0.015 per 1K output tokens (Devin rates)
S2.4: Add performance metrics: time delta between first and last trace entry
S2.5: Add manifest hash extraction from trace entries
S2.6: Add trace integrity hash: SHA256 of all entry_hash values concatenated
S2.7: Test: Manual verification with sample trace file
S2.8: Test: `python .agent/executor/scripts/auto_attest.py --trace .agent/executor/traces/trace-plan-34.jsonl --template .agent/executor/ATTESTATION_TEMPLATE.md --output logs/test-attestation.md`

## S3 — Update ATTESTATION_TEMPLATE.md

S3.1: Read `.agent/executor/ATTESTATION_TEMPLATE.md`
S3.2: Add Error Summary section:
  - Total errors
  - Errors by category (SYNTAX, TYPE, RUNTIME, LINT, IMPORT, TEST_FAILURE, BUILD_FAILURE)
  - New errors in this plan
  - Resolved errors from previous plans
S3.3: Add Token Usage section:
  - Total input tokens
  - Total output tokens
  - Estimated cost (USD)
  - Cost per phase breakdown
S3.4: Add Performance Summary section:
  - Total execution time
  - Slowest phase
  - Average time per phase
S3.5: Add Manifest Hash section:
  - Manifest hash from lock file
  - Manifest hash from trace (should match)
S3.6: Add Trace Integrity Hash section:
  - Chain integrity hash
  - Number of trace entries
  - Phases covered
S3.7: Update existing sections to reference new auto_attest.py generation
S3.8: Manual verification: Human reviews updated template for completeness
S3.9: Test: Generate test attestation from sample trace

## S4 — Update Verification Scripts

S4.1: Update `.agent/executor/scripts/verify_execution.py`:
  - Add trace completeness validation: check all manifest phases have trace entries
  - Add manifest hash chain verification: verify all entries have same manifest_hash
  - Add trace integrity check: verify entry_hash chain is unbroken
  - Add error summary cross-check: verify error summary in attestation matches trace
  - Add token summary cross-check: verify token summary in attestation matches trace
S4.2: Update `.agent/executor/scripts/verify_attestation.py`:
  - Add data validation: cross-check attestation sections against trace file
  - Add hash verification: verify manifest hash and trace integrity hash
  - Add section completeness check: verify all required sections present
  - Add error summary validation: verify error counts match trace
  - Add token summary validation: verify token counts match trace
S4.3: Add error handling for missing or malformed trace files
S4.4: Add error handling for missing or malformed attestation files
S4.5: Test: `pytest .agent/executor/tests/test_attestation_verification.py -v` — test_data_validation, test_hash_verification, test_section_completeness, test_error_summary_validation, test_token_summary_validation
