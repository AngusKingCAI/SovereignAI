Depends on: Plan 35
Vision principles: P2 (Pluggable), P9 (Observability), P13 (Strong and robust)
AR rules: AR1, AR8
OR rules: UOR-1, UOR-2
Open questions resolved: DD-35.1.1
**Revision**: Rev1

## Executor Manifest

**Plan**: 35.1
**Phases**: 3 (S1–S3; S0 excluded from count)
**Deliverables**:
| Phase | Deliverable | Verification |
|-------|-------------|--------------|
| S1 | `.devin/hooks.v1.json` with official Devin hook format | File exists, valid JSON, 8 hooks configured |
| S2 | Hook scripts for PreToolUse, PostToolUse, SessionStart, SessionEnd, Stop, PermissionRequest, UserPromptSubmit | All scripts exist, are executable, return correct exit codes |
| S3 | Migrated `.devin/config.json` referencing hooks.v1.json | config.json updated, old hook entries removed |

**Coverage target**: ≥90%
**Forbidden actions**: Do not modify `AI_HANDOFF.md`, `AGENTS.md`, `PRINCIPLES.md`, `OR_RULES.md`, `PLANS.md`, `DEBT.md`.
**Commit message**: `feat(executor): implement Devin Local SWE 1.6 hooks.v1.json configuration`

## S0 — Opening

S0.1: Run `/open`
S0.2: Read `AGENTS.md` in full. Read plan header AR rules from `.agent/executor/ARCHITECTURE.md`. Read plan header OR rules from `.agent/executor/OR_RULES.md`.
S0.3: Check `.agent/shared/DEBT.md` for deferred items.

## S1 — Create hooks.v1.json

S1.1: Create `.devin/hooks.v1.json` with official Devin Local SWE 1.6 format
S1.2: Configure PreToolUse hook: `"PreToolUse": "python .agent/executor/hooks/hard_gate_pretooluse.py"`
S1.3: Configure PostToolUse hook: `"PostToolUse": "python .agent/executor/hooks/append_trace.py"`
S1.4: Configure SessionStart hook: `"SessionStart": "python .agent/executor/hooks/session_start.py"`
S1.5: Configure SessionEnd hook: `"SessionEnd": "python .agent/executor/hooks/session_end.py"`
S1.6: Configure Stop hook: `"Stop": "python .agent/executor/hooks/session_stop.py"`
S1.7: Configure PermissionRequest hook: `"PermissionRequest": "python .agent/executor/hooks/permission_request.py"`
S1.8: Configure UserPromptSubmit hook: `"UserPromptSubmit": "python .agent/executor/hooks/context_injector.py"`
S1.9: Verify hooks.v1.json is valid JSON and all paths are correct
S1.10: Test: `python -m json.tool .devin/hooks.v1.json` must succeed

## S2 — Create Hook Scripts

S2.1: Create `.agent/executor/hooks/hard_gate_pretooluse.py` — PreToolUse handler
  - Reads tool_name, tool_input, session_id from stdin (JSON)
  - Blocks unauthorized writes to governance files (exit code 2)
  - Blocks git commit without verification (exit code 2)
  - Returns {"decision": "approve"} or {"decision": "block", "reason": "..."} to stdout
S2.2: Create `.agent/executor/hooks/session_start.py` — SessionStart handler
  - Reads session_id from stdin (JSON)
  - Validates .plan-lock.json exists and is valid
  - Initializes trace file for session
  - Returns {"hookSpecificOutput": {"additionalContext": "plan locked: {plan_id}"}} to stdout
S2.3: Create `.agent/executor/hooks/session_end.py` — SessionEnd handler
  - Reads session_id from stdin (JSON)
  - Triggers auto_attest.py to generate attestation from trace
  - Archives trace file to completed/
  - Returns {"hookSpecificOutput": {"additionalContext": "attestation generated"}} to stdout
S2.4: Create `.agent/executor/hooks/session_stop.py` — Stop handler
  - Reads session_id from stdin (JSON)
  - Validates all gates passed before allowing stop
  - Blocks stop if attestation missing or verification failed (exit code 2)
  - Returns {"decision": "approve"} or {"decision": "block", "reason": "..."} to stdout
S2.5: Create `.agent/executor/hooks/permission_request.py` — PermissionRequest handler
  - Reads tool_name, tool_input from stdin (JSON)
  - Requires human approval for governance file edits (exit code 2)
  - Returns {"decision": "approve"} or {"decision": "block"} to stdout
S2.6: Create `.agent/executor/hooks/context_injector.py` — UserPromptSubmit handler
  - Reads user_prompt from stdin (JSON)
  - Injects plan context based on current task phase
  - Returns {"hookSpecificOutput": {"additionalContext": "current phase: S{n}"}} to stdout
S2.7: Test: Each hook script must exist and be executable
S2.8: Test: `python .agent/executor/hooks/hard_gate_pretooluse.py --test` must return valid JSON structure

## S3 — Migrate config.json

S3.1: Read existing `.devin/config.json`
S3.2: Remove old hook entries (before_file_write, after_file_write, after_skill_invoke, session_end)
S3.3: Add reference to hooks.v1.json in config.json comments
S3.4: Verify config.json is still valid JSON
S3.5: Test: `python -m json.tool .devin/config.json` must succeed
S3.6: Manual verification: Human confirms config.json migration is correct
