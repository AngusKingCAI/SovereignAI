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

1. Read `AGENTS.md` in full.
2. Read `prompts/plan-{N}-Rev{X}.md` in full.
3. Read `CHANGELOG.md`'s most recent `## prompt-{N-1}` entry.

## Pre-execution clarification

4. Identify 1-3 ambiguities in the plan. Check for: (a) undefined terms, (b) conflicting requirements, (c) missing preconditions.
5. Ask user. Wait for answers.
6. Post answers in-session as "Plan {N} clarifications". Do not write to the execution log.
7. If no ambiguities: log "No ambiguities — proceeding with Phase 1".

## Setup

8. Add new rules to `AGENTS.md` and new landmines to `LANDMINES.md`. If either changed: `git add -A && git status -s && git commit -m "docs: add rules and landmines for prompt-{N}"`. Else: log "N/A".
8.5. `git add prompts/*.md` — ensure ALL plan files in prompts/ are added to git (tracked or untracked). This prevents treating untracked plan files as cleanup artifacts per L69.
9. Update `PLANS.md` with new plan entry.
10. Begin Phase 1.

## Incremental verification (after each phase)

11. `CHANGED_PY=$(git diff --name-only HEAD | grep '\.py$')` — if non-empty: `pytest tests/ -k "<phase-keyword>" --no-cov -q` + `ruff check $CHANGED_PY`
12. `CHANGED_JS=$(git diff --name-only HEAD | grep '\.js$')` — if non-empty: `for f in $CHANGED_JS; do node --check "$f"; done`
13. `CHANGED_HTML=$(git diff --name-only HEAD | grep '\.html$')` — if non-empty: `for f in $CHANGED_HTML; do python -c "from html.parser import HTMLParser; HTMLParser().feed(open('$f').read())"; done`
14. `CHANGED_CSS=$(git diff --name-only HEAD | grep '\.css$')` — if non-empty: `for f in $CHANGED_CSS; do python -c "import tinycss2; list(tinycss2.parse_stylesheet(open('$f').read()))"; done`
15. Log: "Phase {N} verified"

STOP on any failure.
