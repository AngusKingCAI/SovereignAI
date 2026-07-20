# Plan: Fix Governance Redesign Validation Issues

Depends on: none
Vision principles: P7 (modular), P13 (robust)
Open questions resolved: none

---

## S0 — Opening

1. Run `/open`.
2. Read `AGENTS.md` in full.
3. Read `.agent/executor/ARCHITECTURE.md` in full.
4. Read `.agent/architect/AI_HANDOFF.md` in full.
5. Read `.devin/skills/verify/SKILL.md`, `.devin/skills/close/SKILL.md`, `.devin/skills/scan/SKILL.md` in full.

## S1 — Fix AI_HANDOFF.md Document Relationships table (HIGH-1)

**WILL edit**: `.agent/architect/AI_HANDOFF.md`

**Current** (line ~121):
```
| `AGENTS.md` | Rules (AR + OR) | Executor |
```

**Replace with**:
```
| `AGENTS.md` | Universal Invariants | Executor |
```

**Reason**: AR rules moved to ARCHITECTURE.md. AGENTS.md now contains only universal invariants.

## S2 — Fix AI_HANDOFF.md Plan Template S0.3 (HIGH-2)

**WILL edit**: `.agent/architect/AI_HANDOFF.md`

**Current** (line ~82):
```
- S0.3: Add new rules from this plan's S0 to `AGENTS.md`, commit before coding
```

**Replace with**:
```
- S0.3: Propose new rules from this plan's S0 — add to `.agent/shared/DEBT.md` with target plan, run Round Table, then commit. AR rules → ARCHITECTURE.md, OR rules → edit skill.
```

**Reason**: AGENTS.md is read-only (Invariant 7). New rules go through DEBT.md → Round Table.

## S3 — Fix AI_HANDOFF.md Read order (HIGH-3)

**WILL edit**: `.agent/architect/AI_HANDOFF.md`

**Current** (line ~129):
```
- Architect (new chat): AI_HANDOFF → PRINCIPLES → PLANS → `.agent/shared/LANDMINES.md` → `.agent/shared/DECISIONS.md` → `.agent/shared/DEBT.md`
```

**Replace with**:
```
- Architect (new chat): AI_HANDOFF → PRINCIPLES → `.agent/executor/ARCHITECTURE.md` → PLANS → `.agent/shared/LANDMINES.md` → `.agent/shared/DECISIONS.md` → `.agent/shared/DEBT.md`
```

**Reason**: ARCHITECTURE.md is authority for AR rules. Architects must read it before drafting plans.

## S4 — Add AGENTS.md authority reference to verify skill (HIGH-4)

**WILL edit**: `.devin/skills/verify/SKILL.md`

**Current**: Skill header has no authority reference.

**Insert after line 1** (`---`):
```
authority: AGENTS.md
```

**Reason**: Skills must reference AGENTS.md per SSOT chain.

## S5 — Add AGENTS.md authority reference to close skill (HIGH-4)

**WILL edit**: `.devin/skills/close/SKILL.md`

**Current**: Skill header has no authority reference.

**Insert after line 1** (`---`):
```
authority: AGENTS.md
```

## S6 — Add AGENTS.md authority reference to scan skill (HIGH-4)

**WILL edit**: `.devin/skills/scan/SKILL.md`

**Current**: Skill header has no authority reference.

**Insert after line 1** (`---`):
```
authority: AGENTS.md
```

## S7 — Add self-contained note to scan skill header (MEDIUM-3)

**WILL edit**: `.devin/skills/scan/SKILL.md`

**Current** (line 3):
```
description: Run at scan prompts (5, 10, 15...). Whole-repo scan. No new features. Fixes only. More thorough than /close.
```

**Replace with**:
```
description: Run at scan prompts (5, 10, 15...). Whole-repo scan. No new features. Fixes only. More thorough than /close. Self-contained — does not invoke /close.
```

**Reason**: Clarifies that scan duplicates close steps intentionally; not a bug.

## S8 — Commit and close

1. Run `git status`.
2. Stage modified files:
   - `.agent/architect/AI_HANDOFF.md`
   - `.devin/skills/verify/SKILL.md`
   - `.devin/skills/close/SKILL.md`
   - `.devin/skills/scan/SKILL.md`
3. Commit with message: `fix(governance): resolve validation issues HIGH-1 through HIGH-4, MEDIUM-3`
4. Run `/close`.

---

**Files modified**: 4
**Lines changed**: ~8
**Risk**: Low — all documentation edits, no code changes.
