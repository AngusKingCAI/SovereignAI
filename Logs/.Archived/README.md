# Archived Log Files

**Source**: These log files were restored from the `main-archive` git branch
**Date Restored**: 2026-07-26
**Purpose**: Historical reference for executor debugging and workflow analysis

## Directory Structure

### `0-9/`
Execution logs for plans 0-9 (prompt-0 through prompt-9)
- `execution-log-prompt-0.md` through `execution-log-prompt-9.md`

### `10-19/`
Execution logs for plans 10-19 including sub-plans
- Main execution logs for plans 10-19
- Sub-plan logs (10.1, 10.2, 10.3, 10.4, 10.5, 15.1, etc.)

### `20-29/`
Execution logs for plans 20-29 including attestation files
- Main execution logs for plans 20-29
- Attestation files for plan-28 and plan-29
- Sub-plan logs (20.1-20.9 series, 25.1, 25.4, 25.5, etc.)

### `30-39/`
Execution logs for plans 30-39
- Main execution logs for plans 30-33
- Attestation files for plans 30-33
- Plan-31-Rev17.md, Plan-32-Rev17.md (latest revisions)

### `Architect/Conversations/`
JSON-formatted conversation logs with timestamps and metadata
- `architecture-decision-final.json`
- `directory-structure-update.json`
- `file-analysis-workflow.json`
- `hook-system-correction.json`
- `phase-0-ide-architecture-rules.json`
- `phase-0-logging-implementation-final.json`
- `phase-0-logging-implementation.json`
- `scope-drift-prevention.json`
- `workflow-gate-integration.json`

### `Architect/Gates/`
Architect gate system logs and state files
- `audit-trail.log` - Gate audit trail
- `phase-0-state.json` - Phase 0 state management

### `Misc/`
Miscellaneous execution logs including fix plans and governance infrastructure
- `execution-log-plan-fix-1-Rev1.md` through `execution-log-plan-fix-7-Rev1.md`
- `execution-log-prompt-0.md` through `execution-log-prompt-0.4.md`
- `execution-log-governance-infrastructure.md`
- Various workflow fix logs

### `executor-traces/`
Detailed executor trace files in JSONL format
- `trace-batch-governance.jsonl`
- `trace-plan-28.jsonl` through `trace-plan-34.jsonl`
- `trace-plan-workflow-fix.jsonl`

### Root Level
- `execution-log-plan-34.md` - Standalone plan 34 execution log

## Usage

These logs are useful for:
1. **Understanding how executor previously worked** - Compare historical execution patterns
2. **Debugging current executor issues** - Identify what changed that broke functionality
3. **Analyzing workflow evolution** - See how governance processes have evolved
4. **Performance benchmarking** - Compare execution times and resource usage

## Note

These files are read-only historical artifacts. Do not modify them as they serve as reference points for current executor debugging.