# /close Workflow

Run at the end of every plan. Run straight through — STOP only on failure. Do NOT skip steps because a result would be N/A; observe the N/A result and report it in step 20. Only steps explicitly marked "skip if N/A" below may be skipped.

**Prerequisite**: `.venv/` must exist (verified at `/open` step 3). If missing, STOP and run `/open` first. All commands use absolute venv paths per OR46 — do not rely on `source .venv/Scripts/activate` (L30).

---

**Step 1 — Tests**
```
.venv/Scripts/python.exe -m pytest tests/ -vvv
```
STOP on any failure. STOP if "no tests ran" and the plan was supposed to add tests (silent collection failure).

**Step 2 — Ruff**
```
.venv/Scripts/ruff.exe check . 2>&1 | tail -n 3
```
STOP on errors.

**Step 3 — Mypy** (`.py` files only — never pass markdown/YAML/TOML, per OR47)
- At scan prompts (5, 10, 15…): `.venv/Scripts/mypy.exe . --ignore-missing-imports 2>&1 | tail -n 3`
- At regular prompts:
  ```
  EDITED_PY_FILES=$(git diff --name-only HEAD~1 | grep '\.py$' | tr '\n' ' ')
  if [ -n "$EDITED_PY_FILES" ]; then
    .venv/Scripts/mypy.exe $EDITED_PY_FILES --ignore-missing-imports 2>&1 | tail -n 3
  else
    echo "mypy: N/A (no Python files edited this plan)"
  fi
  ```
STOP on errors on `.py` files.

**Step 4 — Bandit**
```
.venv/Scripts/bandit.exe -r . -ll --exclude .venv,venv,env,.git,node_modules,__pycache__,build,dist,.tox,.eggs,.pytest_cache 2>&1 | tail -n 5
```
STOP on findings.

**Step 5 — pip-audit** (requirements file only per OR39)
```
.venv/Scripts/pip-audit.exe --strict --requirement txt/requirements.txt 2>&1 | tail -n 5
```
STOP on CVEs.

**Step 6 — Vulture**
```
.venv/Scripts/vulture.exe . --min-confidence 80 --exclude .venv,venv,env,.git,node_modules,__pycache__,build,dist,.tox,.eggs,.pytest_cache,.mypy_cache,.ruff_cache,htmlcov 2>&1 | tail -n 5
```
Compare against `txt/vulture-whitelist.txt`. STOP on new findings.

**Step 7 — detect-secrets**
```
.venv/Scripts/detect-secrets.exe scan --baseline txt/.secrets.baseline
```
STOP if exit code != 0. If false positive, run `detect-secrets audit txt/.secrets.baseline` per OR40 — do NOT manually edit the JSON.

**Step 8 — Custom AR static analysis checks**
Run the committed check scripts in `scripts/ar_checks/` (each a separate command — STOP on any violation). Do not re-derive these checks from memory; if a script is missing for a check, write it now, commit it with this plan's changes, and use it from then on (Source: OR48).
```
.venv/Scripts/python.exe scripts/ar_checks/no_globals.py sovereignai/
.venv/Scripts/python.exe scripts/ar_checks/constructor_arg_cap.py sovereignai/ --max-args 15
.venv/Scripts/python.exe scripts/ar_checks/no_context_bags.py sovereignai/
.venv/Scripts/python.exe scripts/ar_checks/docstring_discipline.py sovereignai/
.venv/Scripts/python.exe scripts/ar_checks/no_hardcoded_component_names.py web/ cli/ tui/ phone/
.venv/Scripts/python.exe scripts/ar_checks/ui_does_not_touch_core.py
```
Each script's `--help` documents what it checks and which AR rule it enforces.

**Step 9 — Update `CHANGELOG.md`** (append to END, temp-file pattern per OR13)
```
## prompt-{N} — {Plan title}

**Date**: {YYYY-MM-DD}
**Plan file**: prompts/plan-{N}-Rev{n}.md

**Files changed**:
- {file1}

**Results**:
- Tests: {count} passed, {count} failed
- Ruff: {count} findings
- Mypy: {count} findings
- Bandit: {count} findings
- Vulture: {count} findings
- Detect-secrets: pass/fail

**Notes**:
- {observation, max 3 bullets}
```
Hard cap: 15 lines per entry (OR14). Implementation rationale and design trade-offs do NOT go in Notes — log them in `DECISIONS.md` and write `See DECISIONS.md D{n}` here instead. If Notes needs more than 3 bullets to explain something, that's the signal it belongs in `DECISIONS.md`.

Write to `temp/changelog-entry-{N}.md`, `cat >> CHANGELOG.md`, delete temp.

**Step 10 — Update `PLANS.md`**
- Update Test Baseline using the generated count (`pytest --collect-only -q | tail -n 1`) — do not hand-sum a per-suite breakdown.
- Update Static Analysis Baseline (ruff, mypy, bandit, vulture, detect-secrets, coverage %)
- Add completed prompt row
- Add a one-line Baseline Reconciliation Notes entry if the count changed: `**Plan N**: Baseline → X tests, delta ±Y — see CHANGELOG prompt-N for why.` Full explanation goes in CHANGELOG only, not here.
- Update Active Plan and shift next-5-queue:
  1. Identify the queue slot that matches the just-completed plan (by description or plan number)
  2. Remove that row from the queue
  3. Shift remaining rows up to fill the gap (slot 2→1, 3→2, etc.)
  4. Promote the new slot 1 to Active Plan (format: `**Plan N** — {description}`)
  5. Fill the now-empty slot 5 with "TBD" if no future plan is known
  6. If the completed plan was NOT in the queue (e.g., ad-hoc plan), do NOT shift — leave queue unchanged and set Active Plan to "None — awaiting next plan"
- Do NOT add or edit the Open Questions table — that lives solely in `project-vision-Rev5.md` (see PLANS.md Open Questions section)

**Step 11 — Update `LANDMINES.md`** if a new failure pattern was discovered. Append-only. New landmines start at L32.

**Step 12 — Update `DEBT.md`** if any items deferred this plan. Before appending, check existing entries for the same underlying item (see DEBT.md's "How to add a new deferred item" for the duplicate-check procedure):
```
## Deferred: {item name}
**Deferred at**: prompt-{N}
**Reason**: {why}
**Trigger condition**: {when to address}
**Target plan**: {number or TBD}
```

**Step 13 — C9 rule proposals** — if the Architect spotted a recurring pattern, put the proposal in the execution log.

**Step 14 — Create execution log header** (do NOT commit yet):
```
mkdir -p logs
cat > logs/execution-log-prompt-{N}.md << 'EOF'
# Execution Log — prompt-{N}

**Plan**: {plan title}
**Tag**: prompt-{N}
**Date**: {YYYY-MM-DD}

---

<!-- USER: Paste the full Executor execution log below this line. -->

EOF
```
User pastes content after `/close` completes, then asks Executor to commit and push.

**Step 15 — Commit code changes**
```
git add <files-changed-this-plan>
git commit -m "{plan title} (prompt-{N})" -m "{multi-line description}"
```
Never `--no-verify`. STOP on pre-commit hook failure.

**Step 16 — Tag**
```
git tag prompt-{N}
git tag --list prompt-{N}
```
STOP if tag not listed.

**Step 17 — Archive completed plan files**
```
mkdir -p prompts/completed
mv prompts/plan-{N}*.md prompts/completed/ 2>/dev/null || true
mv prompts/plan-{N}-brief.md prompts/completed/ 2>/dev/null || true
```

**Step 18 — Commit docs** (NOT the execution log — that's committed separately)
```
git add CHANGELOG.md PLANS.md LANDMINES.md DEBT.md prompts/completed/
git commit -m "docs: prompt-{N} governance updates"
```

**Step 19 — Push**
```
git push origin main
git push origin prompt-{N}
```
STOP on failure.

**Step 20 — Verify tag on origin**
```
git ls-remote --tags origin | grep "prompt-{N}"
```
STOP if missing.

**Step 21 — Final summary**
```
=== prompt-{N} COMPLETE ===

Code commit: {hash}
Docs commit: {hash}
Tag: prompt-{N} (verified on origin)

Tests: {count} passed
Ruff: {count} findings
Mypy: {count} findings
Bandit: {count} findings
Vulture: {count} findings
Detect-secrets: pass/fail
Coverage: {%}

New landmines: {count or none}
New deferred items: {count or none}
New rule proposals: {count or none}

=== REMINDER ===
logs/execution-log-prompt-{N}.md created. After this session:
1. Paste full chat log into the file below the comment block
2. Ask Executor to commit and push it
```

**Step 22 — Kill Git Bash sessions. THIS STEP IS MANDATORY — plan is NOT complete until it runs.**
```
taskkill //F //IM bash.exe 2>&1 || true
```
Mandatory for ALL plans including docs-only. N/A results from prior steps do NOT make this step N/A. A second `taskkill` runs at the START of the next `/open` step 1 to clean up any orphans if this step was somehow skipped.
