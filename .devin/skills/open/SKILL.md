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

## Pre-flight

1. `taskkill //F //IM bash.exe 2>&1 || true`
2. `git fetch origin && git ls-remote --tags origin | grep "prompt-{N-1}"` — STOP if missing (skip Plan 1).
3. `git status -s | tail -n 10 && git branch --show-current` — STOP if dirty or wrong branch.
4. `if [ ! -d ".venv" ]; then py -3.11 -m venv .venv && .venv/Scripts/pip.exe install -e .[dev]; fi` then `.venv/Scripts/python.exe --version` — STOP if broken.

## Read context

5. Read `AGENTS.md` in full.
6. Read `prompts/plan-{N}-Rev{X}.md` in full.
7. Read `CHANGELOG.md`'s most recent `## prompt-{N-1}` entry.

## Pre-execution clarification

8. Identify 1-3 ambiguities in the plan.
9. Ask user. Wait for answers.
10. Post answers in-session as "Plan {N} clarifications". Do not write to the execution log.
11. If no ambiguities: log "No ambiguities — proceeding with Phase 1".

## Setup

12. Add new rules to `AGENTS.md`. If changed: `git add -A && git status -s && git commit -m "docs: add rules for prompt-{N}"`. Else: log "N/A".
13. Add new landmines to `LANDMINES.md`. If changed: `git add -A && git status -s && git commit -m "docs: add landmines for prompt-{N}"`. Else: log "N/A".
14. Update `PLANS.md` with new plan entry.
15. Begin Phase 1.

## Incremental verification (after each phase)

- `CHANGED_PY=$(git diff --name-only HEAD | grep '\.py$')` — if non-empty: `pytest tests/ -k "<phase-keyword>" --no-cov -q` + `ruff check $CHANGED_PY`
- `CHANGED_JS=$(git diff --name-only HEAD | grep '\.js$')` — if non-empty: `for f in $CHANGED_JS; do node --check "$f"; done`
- `CHANGED_HTML=$(git diff --name-only HEAD | grep '\.html$')` — if non-empty: `for f in $CHANGED_HTML; do python -c "from html.parser import HTMLParser; HTMLParser().feed(open('$f').read())"; done`
- `CHANGED_CSS=$(git diff --name-only HEAD | grep '\.css$')` — if non-empty: `for f in $CHANGED_CSS; do python -c "import tinycss2; list(tinycss2.parse_stylesheet(open('$f').read()))"; done`
- Log: "Phase {N} verified"

STOP on any failure.
