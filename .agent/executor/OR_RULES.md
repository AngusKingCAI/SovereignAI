# OR_RULES.md — Operational Rules

Single source of truth for operational rules. Skills reference by ID or section.

## UOR — Universal Operational Rules (All Skills)

These rules apply to all skills universally. Skills MUST read UOR section first.

### UOR-1: Deliverables Ship in Full
**Rule**: Deliverables ship in full or defer — no partial implementations
**Applies to**: All skills
**Trigger**: Partial delivery attempt

### UOR-2: Test/Static Analysis Failures
**Rule**: Test/mypy/static-analysis failures: no "pre-existing" exemption
**Applies to**: All skills
**Trigger**: Test failure or static analysis error

### UOR-3: diskcache CVE Monitoring
**Rule**: diskcache CVE monitoring — check DEBT.md for CVE status before close
**Applies to**: close skill primarily
**Trigger**: Before committing changes

### UOR-4: Executor Manifest Compliance
**Rule**: Every plan execution MUST read the Executor Manifest from the plan file at `/open`. The manifest defines phases, deliverables, gates, coverage target, and forbidden actions. Execution that deviates from the manifest = STOP. The executor runs `verify_execution.py --init` at `/open` and `--final` at `/close` to validate compliance automatically.
**Applies to**: All skills
**Trigger**: Plan execution start and end

### UOR-5: Governance File Protection
**Rule**: Governance files (ARCHITECTURE.md, OR_RULES.md, PRINCIPLES.md, AI_HANDOFF.md, LANDMINES.md) MUST NOT be modified during plan execution. The executor runs `check_manifest.py` before every file write to block unauthorized modifications. Any attempt to modify governance files = STOP.
**Applies to**: All skills
**Trigger**: Any file write operation

### UOR-6: Execution Trace Requirement
**Rule**: Every action (file edit, command run, skill invocation) MUST be appended to `.agent/executor/traces/trace-plan-{N}.jsonl`. The trace is the immutable record of execution. Missing trace entries indicate skipped steps or undetected drift. The executor runs `append_trace.py` after every skill invocation to ensure complete logging.
**Applies to**: All skills
**Trigger**: Every action during execution

## VOR — verify Skill Rules

Rules specific to verify skill only.

### VOR-1: Error Pattern Detection
**Rule**: If same error appears 2+ times in execution, document in execution log for Architect review. Define "same error" as: same error message substring OR same script failure OR same command syntax error.
**Applies to**: verify skill
**Trigger**: Repeated error patterns during verification

### VOR-2: Long-Running Commands
**Rule**: Test suites and build commands MUST use background execution mode with timeout=300000 on first invocation. Never restart command; poll existing process identifier with output retrieval. If output truncated, read overflow file.
**Applies to**: verify skill
**Trigger**: Running pytest, mypy, ruff, or other long-running commands

## COR — close Skill Rules

Rules specific to close skill only.

### COR-1: Test-Fix Plans Run Full Suite
**Rule**: Plans with "fix" or "test" in title MUST run full test suite via `pytest .agent/executor/tests`, not scoped tests.
**Applies to**: close skill
**Trigger**: Plan title contains "fix" or "test"

### COR-2: Iterative Testing for Developer Efficiency
**Rule**: Use `run_failing_tests.py` for iterative test execution to reduce iteration time:
- First run: `run_failing_tests.py <test_path> --full` to establish baseline and cache failures
- On retry: `run_failing_tests.py <test_path>` to run only failing tests from cache
- Final verification: `run_failing_tests.py <test_path> --full` when all specific tests pass
**Applies to**: close skill, verify skill
**Trigger**: Test failure requiring fix

### COR-3: Execution Attestation Required
**Rule**: Before `/close` completes, the executor MUST produce `logs/execution-attestation-plan-{N}.md` using the template at `.agent/executor/ATTESTATION_TEMPLATE.md`. The attestation is verified by running `verify_execution.py --final --plan {N}`. If verification FAILs, do not commit, do not tag, do not push. The attestation is the executor's proof of compliance with the plan manifest.
**Applies to**: close skill
**Trigger**: Before session end

## SOR — scan Skill Rules

Rules specific to scan skill only.

## Retired Rules

Legacy OR IDs that have been retired or replaced with new naming scheme.

| Legacy ID | New ID | Status | Notes |
|-----------|--------|--------|-------|
| OR17 | UOR-1 | Replaced | Deliverables Ship in Full |
| OR19 | UOR-2 | Replaced | Test/Static Analysis Failures |
| OR29 | COR-1 | Replaced | Test-Fix Plans Run Full Suite |
| OR48 | - | Retired | No equivalent found |
| OR61 | - | Retired | No equivalent found |
| OR63 | UOR-3 | Replaced | diskcache CVE Monitoring |
| OR65 | - | Retired | No equivalent found |
| OOR-1 | - | Retired | Architect Suggestion Review - removed in governance reorganization |

## Rule Maintenance

- Add new rules to appropriate section with sequential numbering
- Update this file instead of editing skill files directly
- Skills reference by ID, not by embedding full text
- Skills read UOR section + their specific section only
- When creating new rules, update AI_HANDOFF.md references if needed (Architect drafts, Executor writes)
- When renaming rules, update all references project-wide (CHANGELOG.md, plans, etc.)
