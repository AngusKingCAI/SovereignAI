Depends on: plan-fix-3-Rev1
Vision principles: P3 (Reliability), P11 (Quality)
Open questions resolved: none

## S0 — Opening

S0.0: Clone latest repo. Verify plan-fix-3-Rev1 completed.
S0.1: Run `/open`
S0.2: Read `AGENTS.md` in full
S0.3: Check `.agent/shared/DEBT.md`
S0.4: Run `grep -r 'suggest_rule' --include='*.md' --include='*.py' .agent/ .devin/` — catalog remaining references

## F1 — Clean Up Remaining suggest_rule.py References

F1.1: Edit `OR_RULES.md` VOR-1: replace "run suggest_rule.py" with "document in execution log for Architect review"
F1.2: Edit `AGENTS.md` line 3: replace "Executor may suggest new rules via suggest_rule.py" with "Architect detects patterns from execution logs"
F1.3: Edit `open/SKILL.md` step 6: replace "run suggest_rule.py" with "document in execution log for Architect review"
F1.4: Run `pytest .agent/executor/tests/test_document_hygiene.py -v` — verify pass

## F2 — Fix AR Rule Cleanup

F2.1: Reconcile `ar_checks/README.md` with `ARCHITECTURE.md` — rewrite as index pointing to ARCHITECTURE.md
F2.2: Fix AR16–AR20 numbering gap in `ARCHITECTURE.md` — add "Reserved. Never assigned."
F2.3: Re-scope AR11 — "Docstrings not required (D-rules disabled in ruff). Self-documenting names preferred."
F2.4: Remove dead `[tool.ruff.lint.pydocstyle]` block from `pyproject.toml`
F2.5: Fix `ARCHITECTURE.md` verification table — remove `no_globals.py` and `constructor_arg_cap.py` from AR11 row
F2.6: Run `pytest .agent/executor/tests/test_document_hygiene.py -v` — verify pass

## F3 — Fix RULE_LIFECYCLE.md File References

F3.1: Update directory structure to reflect actual files (semantic names, not `check_ar{n}.py` pattern)
F3.2: Remove `suggest_rule.py` from tree
F3.3: Run `pytest .agent/executor/tests/test_document_hygiene.py -v` — verify pass

## Closing

Run `/close`
