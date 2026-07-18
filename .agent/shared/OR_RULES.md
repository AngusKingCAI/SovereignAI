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

## OOR — open Skill Rules

Rules specific to open skill only.

### OOR-1: Architect Suggestion Review
**Rule**: Architect must evaluate all suggestions before creating plan — if suggestions exist, read and evaluate per RULE_LIFECYCLE.md TRIAGE
**Applies to**: open skill
**Trigger**: Before creating plan

## COR — close Skill Rules

Rules specific to close skill only.

### COR-1: Test-Fix Plans Run Full Suite
**Rule**: Plans with "fix" or "test" in title MUST run full test suite via `pytest .agent/executor/tests`, not scoped tests.
**Applies to**: close skill
**Trigger**: Plan title contains "fix" or "test"

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

## Rule Maintenance

- Add new rules to appropriate section with sequential numbering
- Update this file instead of editing skill files directly
- Skills reference by ID, not by embedding full text
- Skills read UOR section + their specific section only
- When creating new rules, update AI_HANDOFF.md references if needed
- When renaming rules, update all references project-wide (CHANGELOG.md, plans, etc.)
