---
name: open
description: Run at start of every plan. Don't skip steps.
argument-hint: "[plan-number]"
allowed-tools:
  - read
  - grep
  - glob
  - exec
  - edit
  - write
---

Run the /open workflow for the current plan. Follow all steps in order. Don't skip steps.

## Read context

□ Step 1: Read `AGENTS.md` in full.

□ Step 1.5: If plan involves edge cases not covered by AGENTS.md's 30 rules, read `AGENTS_EXTENDED.md` for AR16–AR30 and OR31–OR63.

□ Step 2: Read `prompts/plan-{N}-Rev{X}.md` in full.

□ Step 3: Read `.agent/shared/CHANGELOG.md`'s most recent `## prompt-{N-1}` entry.

## Pre-execution clarification

□ Step 4: Identify 1-3 ambiguities. Check for: undefined terms, conflicting requirements, missing preconditions.

□ Step 5: Ask user. Wait for answers.

□ Step 6: Post answers in-session as "Plan {N} clarifications". Do not write to execution log.

□ Step 7: If no ambiguities: log "No ambiguities — proceeding with Phase 1".

## Setup

□ Step 8: Add new rules to `AGENTS.md` and new landmines to `.agent/shared/LANDMINES.md`. If either changed: `git add -A && git status -s && git commit -m "docs: add rules and landmines for prompt-{N}"`. Else: log "N/A".

□ Step 8.5: `git add prompts/*.md` — ensure ALL plan files in prompts/ are added to git.

□ Step 9: Update `.agent/executor/PLANS.md` with new plan entry.

□ Step 10: Begin Phase 1.

## Incremental verification (after each phase)

□ Step 11: `CHANGED_PY=$(git diff --name-only HEAD | grep '\.py$')` — if non-empty: `pytest tests/ -k "<phase-keyword>" --no-cov -q` + `ruff check $CHANGED_PY`

□ Step 12: `CHANGED_JS=$(git diff --name-only HEAD | grep '\.js$')` — if non-empty: syntax check each.

□ Step 13: `CHANGED_HTML=$(git diff --name-only HEAD | grep '\.html$')` — if non-empty: syntax check each.

□ Step 14: `CHANGED_CSS=$(git diff --name-only HEAD | grep '\.css$')` — if non-empty: syntax check each.

□ Step 15: Log: "Phase {N} verified"

STOP on any failure.
