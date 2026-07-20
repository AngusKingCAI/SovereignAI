# Workflow Fix — SovereignAI Compliance System
Date: 2026-07-19
Plan ID: workflow-fix
Repo: https://github.com/AngusKingCAI/SovereignAI
Branch: main (commit 607f097)

## Executor Manifest

You are fixing 9 known issues in the SovereignAI compliance system. All changes must be committed as a single commit with message: `fix(compliance): resolve 9 critical/high/medium issues from architect handoff`.

### Files to Modify
1. `.agent/executor/scripts/verify_execution.py` — Fix malformed quote (Critical #4)
2. `.agent/executor/hooks/append_trace.py` — Add file edit tracing (Critical #5)
3. `.agent/executor/hooks/check_manifest.py` — Clarify/block out-of-scope files (Critical #9)
4. `.devin/skills/verify/SKILL.md` — Add script reference for phase gate check (High #2)
5. `.devin/skills/close/SKILL.md` — Consolidate redundant trace checks (High #3)
6. `.devin/config.json` — Add {plan_id} fallback logic (High #8)
7. `.agent/executor/scripts/organize_logs.py` — Remove hardcoded path (Medium #1)
8. `.agent/executor/scripts/get_current_plan.py` — Remove dead code (Medium #6)
9. `.devin/skills/scan/SKILL.md` — Add log organization step (Medium #7)

### Phases
Phase 1: Critical fixes (Fixes 4, 5, 9)
Phase 2: High priority fixes (Fixes 2, 3, 8)
Phase 3: Medium priority fixes (Fixes 1, 6, 7)

### Coverage Target
N/A (compliance system fixes only)

### Verification Steps
After all fixes:
1. Run syntax check on all modified Python files
2. Run preflight check
3. Run init verification
4. Run final verification
5. Commit with specified message
