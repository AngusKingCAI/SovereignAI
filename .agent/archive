# LANDMINES-ARCHIVE.md — Historical Landmines

Never read routinely. Consult only for audit/investigation.

These landmines graduated to rules that have been removed from AGENTS.md (mechanically enforced by scripts, skills, or plan templates).

---

## L1 — replace_all corrupts adjacent lines
**Trigger**: Edit tool `replace_all=true` on multi-occurrence strings.
**Impact**: Adjacent lines silently modified.
**Graduated to**: OR3 (now mechanically enforced by Edit tool behavior).

## L2 — Parallel scan tools corrupt output streams
**Trigger**: Running pytest/ruff/mypy/bandit simultaneously.
**Impact**: Output streams interleave, counts wrong.
**Graduated to**: OR2 (now mechanically enforced by skill workflow).

## L3 — PowerShell -replace corrupts structured markdown
**Trigger**: PowerShell string replacement on AGENTS.md/plan files.
**Impact**: Markdown structure broken.
**Graduated to**: OR4 (now mechanically enforced by skill workflow).

## L4 — Temp files left in repo root get committed
**Trigger**: `cat >> temp.txt` then forgot to delete before `git add`.
**Impact**: Stray files in commits.
**Graduated to**: OR8 (now covered by git add -A behavior).

## L7 — Stale baselines propagate through plans
**Trigger**: PLANS.md baseline not updated at `/close`.
**Impact**: Future plans start from wrong counts.
**Graduated to**: close.md step 13 (skill-enforced).

## L8 — Scope drift: editing files outside declared scope
**Trigger**: Editing files not in plan's "WILL edit" list.
**Impact**: Scope creep, unplanned changes.
**Graduated to**: OR6 (plan template convention).

## L10 — Bypassed pre-commit hooks with --no-verify
**Trigger**: `git commit --no-verify` to skip failing hook.
**Impact**: Hooks bypassed, broken code committed.
**Graduated to**: OR12 (skill-enforced).

## L11 — Hiding type errors by excluding files from hooks
**Trigger**: Editing hook config to exclude failing files.
**Impact**: Type errors hidden permanently.
**Graduated to**: OR13 (skill-enforced).

## L12 — Plan steps executed/marked complete out of order
**Trigger**: Marking step complete based on work done elsewhere, or jumping ahead.
**Impact**: Dependencies missed, steps skipped.
**Graduated to**: Plan template structure (convention).

## L13 — Shell redirection and echo-to-file fail in Git Bash on Windows
**Trigger**: `echo "" > path` or `> file` redirection in `&&` chains.
**Impact**: Files not created, commands fail silently.
**Graduated to**: Implementation detail (both methods work).

## L14 — Multi-line git commit messages fail in Git Bash on Windows
**Trigger**: `git commit -m "line1\nline2"` with embedded newlines.
**Impact**: Commit message malformed.
**Graduated to**: Implementation detail (both methods work).

## L15 — detect-secrets --all-files scans .venv/ despite .gitignore
**Trigger**: `detect-secrets scan --all-files` without `--exclude`.
**Impact**: .venv/ scanned, false positives.
**Graduated to**: Script configuration (enforced by script).

## L16 — Executor skipped /close steps when expected result was N/A
**Trigger**: Skipping close steps because result would be N/A.
**Impact**: Steps not run, verification incomplete.
**Graduated to**: Skill contract (skill-enforced).

## L17 — sed used on workflow files after Edit-tool failures
**Trigger**: `sed` on `.devin/skills/*/SKILL.md` when Edit tool failed.
**Impact**: Workflow files corrupted.
**Graduated to**: OR4 (skill-enforced).

## L18 — python and pip resolve to different interpreters on Windows
**Trigger**: System `python`/`pip` on PATH pointing to different installs.
**Impact**: Packages installed to wrong interpreter.
**Graduated to**: /open skill step 4 (skill-enforced).

## L19 — source .venv/Scripts/activate does not persist in Git Bash on Windows
**Trigger**: `source .venv/Scripts/activate` in Git Bash.
**Impact**: Activation lost between commands.
**Graduated to**: /open skill step 4 (skill-enforced).

## L20 — Mypy fails when passed markdown or other non-Python files
**Trigger**: `mypy .` passing markdown/YAML/TOML files.
**Impact**: Mypy errors on non-Python files.
**Graduated to**: /close skill step 3 (skill-enforced).

## L21 — Executor paraphrases workflow commands instead of running them verbatim
**Trigger**: Simplifying or substituting workflow commands.
**Impact**: Commands achieve less than specified.
**Graduated to**: /open skill (skill-enforced).

## L23 — mv + git add <new> leaves old path tracked in git
**Trigger**: `mv old new && git add new` without `git add -A`.
**Impact**: Old path still tracked.
**Graduated to**: /close skill step 17 (skill-enforced).

## L24 — ruff --fix / detect-secrets auto-modified files missed by explicit git add lists
**Trigger**: `git add <file1> <file2>` after auto-fixes.
**Impact**: Auto-fixed files not staged.
**Graduated to**: /close skill step 17 (skill-enforced).

## L25 — Premature git tag creation requires force-push to move
**Trigger**: `git tag` before work complete.
**Impact**: Tag points at wrong commit.
**Graduated to**: /close skill step 20 (skill-enforced).

## L26 — Coverage skipped or unmeasured in 8 of 16 prompts
**Trigger**: Coverage not run or reported as N/A.
**Impact**: Coverage rot hidden.
**Graduated to**: /close skill step 1 (skill-enforced).

## L27 — Bandit Low count drifted without baseline reconciliation
**Trigger**: Bandit count not updated in PLANS.md.
**Impact**: Baseline stale, drift undetected.
**Graduated to**: /close skill step 13 (skill-enforced).

## L28 — Quota exhaustion mid-plan causes context loss and skipped steps
**Trigger**: Model quota exhausted during plan execution.
**Impact**: Context lost, steps skipped.
**Graduated to**: Edge case handler (removed as general rule).

## L31 — Command errored without investigation
**Trigger**: Treating "Command errored" as non-blocking.
**Impact**: Real failures ignored.
**Graduated to**: Debugging heuristic (removed as general rule).

## L32 — Command errored in verification step treated as non-blocking
**Trigger**: Verification command errors skipped.
**Impact**: Verification incomplete.
**Graduated to**: OR11 (requires root cause analysis).

## L41 — CHANGELOG claimed unshipped scope
**Trigger**: Commit message claimed features that didn't ship.
**Impact**: User misled.
**Graduated to**: check_changelog.py (script-enforced).

## L44 — Web UI plan lacked browser smoke test
**Trigger**: UI changes shipped without browser verification.
**Impact**: UI broken in browser.
**Graduated to**: /close skill step 15 (skill-enforced).

## L46 — Critical rules dropped from plan spec
**Trigger**: 6 of 12 rules from plan spec not added to AGENTS.md.
**Impact**: Rules that would catch failures absent.
**Graduated to**: spec_match.py (script-enforced).

## L47 — CHANGELOG edited mid-execution or not appended
**Trigger**: Editing CHANGELOG before `/close` step 12, skipping the append, or revising an existing entry after its plan was tagged.
**Impact**: Audit trail broken; CHANGELOG claims unshipped scope; future Architects cannot reconstruct what shipped.
**Graduated to**: check_changelog.py (script-enforced).

## L55 — Force-push of tag post-hoc
**Trigger**: git push --force origin refs/tags/prompt-N (observed in P20.5 L2255).
**Impact**: published tag history rewritten; consumers' git fetch fails.
**Graduated to**: /close skill step 20 (skill-enforced).

## L56 — Execution log stub hidden as full log
**Trigger**: /close with execution-log-prompt-N.md missing the [PASTE DEVIN CHAT HERE] marker when chat content is not yet pasted.
**Impact**: Architect cannot distinguish a stub from a complete log; audit trail ambiguous.
**Graduated to**: /close skill step 23 (skill-enforced).

## L57 — OR19 self-waiver
**Trigger**: Executor says 'I should STOP per OR19' then immediately defers instead (observed in P20.5 L1025 to L1027).
**Impact**: STOP rule defeated by self-granted waiver.
**Graduated to**: OR11 (cultural enforcement, no mechanical fix).

## L58 — Todo counter not updated
**Trigger**: Todo list counter stays at X/Y despite progress (observed in P20.5 L493, L787).
**Impact**: Auditor cannot reconstruct progress; L47 (added same plan) violated.
**Graduated to**: spec_match.py (script-enforced).

## L60 — Missing dependency in requirements.txt
**Trigger**: production code imports a package not in txt/requirements.txt (or dev import not in pyproject.toml).
**Impact**: ImportError at runtime; tests fail; pip-audit can't scan.
**Graduated to**: check_dependencies.py (script-enforced).

## L61 — Plan file mutated mid-execution
**Trigger**: Editing prompts/plan-N-RevM.md during execution to satisfy spec_match or reconcile WILL-edit list (observed in P16, P20.1, P20.4).
**Impact**: Round Table review undermined; post-hoc cover-ups indistinguishable from legitimate fixes.
**Graduated to**: check_plan_immutability.py (script-enforced).

## L62 — Test stalled indefinitely
**Trigger**: Test makes network call (HF API, Ollama, etc.) or infinite loop with no timeout.
**Impact**: Suite hangs; Devin can't proceed; CI blocked.
**Graduated to**: OR25 (testing strategy, kept).

## L63 — Rule too verbose to follow
**Trigger**: AR/OR rule exceeds 600 chars OR uses explanatory context instead of constraint+consequence.
**Impact**: SWE-1.6 ignores long rules; token cost on every re-read.
**Graduated to**: check_rule_conciseness.py (script-enforced).

## L65 — Context7 skipped
**Trigger**: Devin uses library API without querying Context7 first (hallucinated import path, method signature, or version-specific behavior).
**Impact**: Hallucinated APIs shipped (P20.4 ContentSwitcher ImportError).
**Graduated to**: /close skill step 5.5 (skill-enforced).

## L66 — Snyk skipped
**Trigger**: Devin invokes Snyk MCP scan at /close for plans touching txt/requirements.txt or security-sensitive code.
**Impact**: CVEs caught earlier (P20.5 diskcache).
**Graduated to**: /close skill step 5.5 (skill-enforced).

## L64 — Quota interrupt without re-read
**Trigger**: Devin resumes work after quota interrupt without re-reading plan + AGENTS.md.
**Impact**: Context lost; rules forgotten; steps skipped.
**Graduated to**: Edge case handler (removed as general rule).
