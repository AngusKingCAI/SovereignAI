# LANDMINES.md

Append-only. Never edit or remove entries. Format:
```
## L{n} — <title>
**Trigger**: <plan, step, command/file>
**Impact**: <what broke>
**Graduated to**: <OR{n} or workflow fix>
```

---

## L1 — replace_all corrupts adjacent lines
**Trigger**: Edit tool `replace_all=true` on multi-occurrence strings.
**Impact**: Adjacent lines silently modified.
**Graduated to**: OR4.

## L2 — Parallel scan tools corrupt output streams
**Trigger**: Running pytest/ruff/mypy/bandit simultaneously.
**Impact**: Output streams interleave, counts wrong.
**Graduated to**: OR3.

## L3 — PowerShell -replace corrupts structured markdown
**Trigger**: PowerShell string replacement on AGENTS.md/plan files.
**Impact**: Markdown structure broken.
**Graduated to**: OR6.

## L4 — Temp files left in repo root get committed
**Trigger**: `cat >> temp.txt` then forgot to delete before `git add`.
**Impact**: Stray files in commits.
**Graduated to**: OR8.

## L5 — Vulture flags unused test fixtures incorrectly
**Trigger**: Vulture on test files with pytest fixtures.
**Impact**: Fixtures flagged unused despite decorator requirement.
**Graduated to**: OR39.

## L6 — Naive/aware datetime mixing
**Trigger**: `datetime.utcnow()` or bare `datetime.now()` mixed with aware.
**Impact**: Comparison errors, timezone bugs.
**Graduated to**: OR12.

## L7 — Stale baselines propagate through plans
**Trigger**: PLANS.md baseline not updated at `/close`.
**Impact**: Future plans start from wrong counts.
**Graduated to**: close.md step 13.

## L8 — Scope drift: editing files outside declared scope
**Trigger**: Editing files not in plan's "WILL edit" list.
**Impact**: Scope creep, unplanned changes.
**Graduated to**: OR10, OR14.

## L9 — Interface changes break existing tests during type remediation
**Trigger**: Changing function signatures during type fixes.
**Impact**: Existing tests fail on new signature.
**Graduated to**: OR15.

## L10 — Bypassed pre-commit hooks with --no-verify
**Trigger**: `git commit --no-verify` to skip failing hook.
**Impact**: Hooks bypassed, broken code committed.
**Graduated to**: OR20.

## L11 — Hiding type errors by excluding files from hooks
**Trigger**: Editing hook config to exclude failing files.
**Impact**: Type errors hidden permanently.
**Graduated to**: OR21.

## L12 — Plan steps executed/marked complete out of order
**Trigger**: Marking step complete based on work done elsewhere, or jumping ahead.
**Impact**: Dependencies missed, steps skipped.
**Graduated to**: OR22.

## L13 — Shell redirection and echo-to-file fail in Git Bash on Windows
**Trigger**: `echo "" > path` or `> file` redirection in `&&` chains.
**Impact**: Files not created, commands fail silently.
**Graduated to**: OR26, OR28.

## L14 — Multi-line git commit messages fail in Git Bash on Windows
**Trigger**: `git commit -m "line1\nline2"` with embedded newlines.
**Impact**: Commit message malformed.
**Graduated to**: OR27.

## L15 — detect-secrets --all-files scans .venv/ despite .gitignore
**Trigger**: `detect-secrets scan --all-files` without `--exclude`.
**Impact**: .venv/ scanned, false positives.
**Graduated to**: OR25.

## L16 — Executor skipped /close steps when expected result was N/A
**Trigger**: Skipping close steps because result would be N/A.
**Impact**: Steps not run, verification incomplete.
**Graduated to**: OR40.

## L17 — sed used on workflow files after Edit-tool failures
**Trigger**: `sed` on `.devin/workflows/*.md` when Edit tool failed.
**Impact**: Workflow files corrupted.
**Graduated to**: OR6.

## L18 — python and pip resolve to different interpreters on Windows
**Trigger**: System `python`/`pip` on PATH pointing to different installs.
**Impact**: Packages installed to wrong interpreter.
**Graduated to**: OR29.

## L19 — source .venv/Scripts/activate does not persist in Git Bash on Windows
**Trigger**: `source .venv/Scripts/activate` in Git Bash.
**Impact**: Activation lost between commands.
**Graduated to**: OR29.

## L20 — Mypy fails when passed markdown or other non-Python files
**Trigger**: `mypy .` passing markdown/YAML/TOML files.
**Impact**: Mypy errors on non-Python files.
**Graduated to**: OR30.

## L21 — Executor paraphrases workflow commands instead of running them verbatim
**Trigger**: Simplifying or substituting workflow commands.
**Impact**: Commands achieve less than specified.
**Graduated to**: OR38.

## L22 — Executor weakens AR check scripts or tests to make a failure pass
**Trigger**: Editing tests/checks to weaken assertions.
**Impact**: Failures hidden.
**Graduated to**: OR39.

## L23 — mv + git add <new> leaves old path tracked in git
**Trigger**: `mv old new && git add new` without `git add -A`.
**Impact**: Old path still tracked.
**Graduated to**: OR41.

## L24 — ruff --fix / detect-secrets auto-modified files missed by explicit git add lists
**Trigger**: `git add <file1> <file2>` after auto-fixes.
**Impact**: Auto-fixed files not staged.
**Graduated to**: OR41.

## L25 — Premature git tag creation requires force-push to move
**Trigger**: `git tag` before work complete.
**Impact**: Tag points at wrong commit.
**Graduated to**: OR42.

## L26 — Coverage skipped or unmeasured in 8 of 16 prompts
**Trigger**: Coverage not run or reported as N/A.
**Impact**: Coverage rot hidden.
**Graduated to**: OR43.

## L27 — Bandit Low count drifted without baseline reconciliation
**Trigger**: Bandit count not updated in PLANS.md.
**Impact**: Baseline stale, drift undetected.
**Graduated to**: OR44.

## L28 — Quota exhaustion mid-plan causes context loss and skipped steps
**Trigger**: Model quota exhausted during plan execution.
**Impact**: Context lost, steps skipped.
**Graduated to**: OR45.

## L29 — close.md Step 17 verification check said "run git rm" which DELETES files
**Trigger**: `/close` Step 17 used `git rm` to move files.
**Impact**: Files deleted instead of moved.
**Graduated to**: close.md fix (prompt-15).

## L30 — Disabled production features to make tests pass
**Trigger**: Disabling crash recovery/memory backends to pass tests.
**Impact**: Production features off.
**Graduated to**: OR48, OR53.

## L31 — Command errored without investigation
**Trigger**: Treating "Command errored" as non-blocking.
**Impact**: Real failures ignored.
**Graduated to**: OR17.

## L32 — Command errored in verification step treated as non-blocking
**Trigger**: Verification command errors skipped.
**Impact**: Verification incomplete.
**Graduated to**: OR19.

## L33 — Filtered on non-existent event attribute
**Trigger**: Self-correction skill filtered on `event.component` which didn't exist.
**Impact**: Filter never matched.
**Graduated to**: OR61.

## L34 — Mypy errors dismissed as "pre-existing"
**Trigger**: Mypy errors dismissed without fixing.
**Impact**: Type errors shipped.
**Graduated to**: OR53.

## L35 — Memory backends not registered in container
**Trigger**: Memory backends not in DI container.
**Impact**: Backends not accessible.
**Graduated to**: OR48.

## L36 — Crash recovery disabled
**Trigger**: `run_crash_recovery()` body replaced with `pass`.
**Impact**: No crash recovery.
**Graduated to**: OR49.

## L37 — Plan shipped with placeholder implementation
**Trigger**: sync.py shipped with `# TODO: Fetch actual data`.
**Impact**: Feature non-functional.
**Graduated to**: OR51.

## L38 — "Already done" claim without verification
**Trigger**: Marking steps complete via visual inspection only.
**Impact**: Incomplete work marked done.
**Graduated to**: OR52.

## L39 — Test failures dismissed as "pre-existing"
**Trigger**: 46 test failures shipped as "pre-existing".
**Impact**: Broken tests in production.
**Graduated to**: OR53.

## L40 — Skipped tests without target-resolution plan
**Trigger**: Tests skipped with no documented target.
**Impact**: Skipped tests accumulate.
**Graduated to**: OR54.

## L41 — CHANGELOG claimed unshipped scope
**Trigger**: Commit message claimed features that didn't ship.
**Impact**: User misled.
**Graduated to**: OR55.

## L42 — HTML/CSS/JS syntax not validated before tests
**Trigger**: Python docstrings in app.js, double-class in HTML.
**Impact**: Invalid code shipped.
**Graduated to**: OR56.

## L43 — Tests used incorrect fixture shapes
**Trigger**: Test fixtures didn't match production data shapes.
**Impact**: Tests pass but production breaks.
**Graduated to**: OR58.

## L44 — Web UI plan lacked browser smoke test
**Trigger**: UI changes shipped without browser verification.
**Impact**: UI broken in browser.
**Graduated to**: OR57.

## L45 — Stray files in commits without pre-commit scan
**Trigger**: cookies.txt staged by `git add -A`.
**Impact**: Unintended files committed.
**Graduated to**: OR59.

## L46 — Critical rules dropped from plan spec
**Trigger**: 6 of 12 rules from plan spec not added to AGENTS.md.
**Impact**: Rules that would catch failures absent.
**Graduated to**: OR65.

## L47 — CHANGELOG edited mid-execution or not appended
**Trigger**: Editing CHANGELOG before `/close` step 12, skipping the append, or revising an existing entry after its plan was tagged.
**Impact**: Audit trail broken; CHANGELOG claims unshipped scope (OR55 violation); future Architects cannot reconstruct what shipped.
**Graduated to**: OR73.

## L48 — Governance tool self-modified to pass its own check
**Trigger**: Editing `scripts/ar_checks/*.py` or `tests/test_ar*.py` in the same commit as core/UI code (observed in plans 17, 18, 19, 20.4).
**Impact**: Mechanical gate defeated; governance tools become unreliable; OR39 violation.
**Graduated to**: OR39 (existing — needs enforcement hook, deferred to DEBT.md).

## L49 — AR7 allowlist expansion treated as routine
**Trigger**: Adding entries to `WEB_MAIN_ALLOWED_IMPORTS` or tui/panels allowlist without Architect sign-off (observed in plans 16, 17, 20.4).
**Impact**: AR7 one-way ratchet; architecture boundary erodes; OR47 exception becomes the rule.
**Graduated to**: OR47 (existing — needs Architect sign-off requirement, deferred to DEBT.md).

## L50 — Plan file mutated mid-execution
**Trigger**: Editing `prompts/plan-N-RevM.md` during execution (observed in plans 16, 20.1, 20.4).
**Impact**: Round Table review undermined; post-hoc cover-ups indistinguishable from legitimate fixes.
**Graduated to**: New pre-commit hook (deferred to DEBT.md, target plan 20.8).

## L51 — LANDMINES.md "N/A — no new patterns" without enumeration
**Trigger**: Closing a plan with "N/A — no new patterns" in LANDMINES.md without listing the patterns considered and why each was rejected (observed in plans 17, 19, 20.1, 20.2, 20.3, 20.4).
**Impact**: Novel failure patterns unrecorded; future plans repeat them.
**Graduated to**: OR40 (existing — needs enumeration requirement, enforced via /close step 14.6).

## L52 — Production code polluted with TEST_MODE env hooks
**Trigger**: Adding env-var early-returns to production code to make tests pass (observed in plan 17: `SOVEREIGNAI_TEST_MODE` in `HFDatabaseProvider.list_models`, `health_check`, `build_container`).
**Impact**: Production features silently disabled; security-adjacent; L30-pattern recurrence.
**Graduated to**: OR48/OR53 (existing — needs AR-check script, deferred to plan 20.5 S1.5).

## L53 — Task-list denominator changed mid-execution without log
**Trigger**: Todo list growing or shrinking during execution without a one-line reason in the execution log (observed in plans 16: 40→41, 18: 19→27, 20.2: 35→34, 20.4: 14→14+6).
**Impact**: Auditor cannot reconstruct what was added/removed or why; OR22 (strict numerical order) spirit violated.
**Graduated to**: New OR (deferred to DEBT.md, target plan 20.8).

---

## L54 — ContentSwitcher import path error
**Trigger**: `from textual.containers import ContentSwitcher` (observed in P20.4 ImportError). Correct import is `from textual.widgets import ContentSwitcher`.
**Impact**: ImportError at runtime; manual `hidden` class fallback with 4 bugs (B1-B3 in Plan 20.6).
**Graduated to**: OR74.

---

## L55 — Force-push of tag post-hoc
**Trigger**: git push --force origin refs/tags/prompt-N (observed in P20.5 L2255).
**Impact**: published tag history rewritten; consumers' git fetch fails.
**Graduated to**: OR42 (existing — needs enforcement hook, deferred to 20.8).

---

## L56 — Execution log stub hidden as full log
**Trigger**: /close with execution-log-prompt-N.md missing the [PASTE DEVIN CHAT HERE] marker when chat content is not yet pasted.
**Impact**: Architect cannot distinguish a stub from a complete log; audit trail ambiguous.
**Graduated to**: OR75.

---

## L57 — OR19 self-waiver
**Trigger**: Executor says 'I should STOP per OR19' then immediately defers instead (observed in P20.5 L1025 to L1027).
**Impact**: STOP rule defeated by self-granted waiver.
**Graduated to**: OR19 (existing — enforcement is cultural, no mechanical fix).

---

## L58 — Todo counter not updated
**Trigger**: Todo list counter stays at X/Y despite progress (observed in P20.5 L493, L787).
**Impact**: Auditor cannot reconstruct progress; L47 (added same plan) violated.
**Graduated to**: L47 (existing — needs enforcement, deferred to 20.8).

---

N/A — no new patterns (OR66 added per plan requirements, not a failure pattern)

---

N/A — no new patterns for prompt-18

---

N/A — no new patterns for prompt-20
