# SovereignAI — Coding Department: Implementation Specification

**Document Type:** Deep Implementation Spec
**Author:** Angus / Claude (design pass)
**Audience:** GLM (implementing agent) + Round Table review
**Status:** Draft v1 — ready for Round Table review
**Date:** 2026-06-29
**Depends on:** `SovereignAI_Architecture_Decisions.md`, `project-vision-Rev5.md`, `SovereignAI_Research_Department_Spec.md`

---

## 0. Purpose

This document specifies the **Coding Department** — SovereignAI's internal capability for all software development work. The department writes, reads, modifies, tests, reviews, and reasons about code across any language or framework. It does not own the tools it uses — terminal access, file system operations, git, and test runners are skills and adapters registered in the Skills and Adapters panels. The Coding Department is the brain that directs those tools; the tools themselves are interchangeable.

The department handles the full software development lifecycle from initial task intake through to verified, committed output: understanding requirements, reading existing codebases, planning changes, writing code, running tests, interpreting failures, iterating, and presenting finished work to the Owner for review.

---

## 1. Company Metaphor Placement

| Entity | Role in Coding Department |
|--------|--------------------------|
| **Owner (User)** | Issues coding tasks; reviews and approves output before anything is committed or deployed; can take direct control at any point |
| **Orchestrator (CEO)** | Translates vague requests ("fix the login bug", "add dark mode") into structured Coding Tasks with measurable acceptance criteria |
| **Coding Manager** | Permanent department head. Receives Coding Tasks, reads codebase context, plans the approach, assigns workers, synthesises output, manages the review cycle |
| **Reader Workers** | Parse and index existing codebases; build a working model of structure, dependencies, conventions, and relevant context before any changes are made |
| **Planner Workers** | Break a Coding Task into a concrete change plan — which files to touch, in what order, what each change achieves, what tests need to pass |
| **Writer Workers** | Implement planned changes. Write new code, modify existing code, delete dead code. One Worker per logical change unit (a function, a module, a PR-sized chunk) |
| **Test Workers** | Write test cases, run existing test suites via the terminal skill, interpret results, and report pass/fail with diagnostics |
| **Review Workers** | Read completed changes as a senior developer would — checking correctness, style, security, edge cases, and consistency with the existing codebase |
| **Debug Workers** | Investigate failures: read error output, form hypotheses, apply targeted fixes, re-run until resolved |
| **Research Manager** | Upstream dependency for technical decisions — library selection, API evaluation, security advisories, performance benchmarks. Coding Manager issues a Research Brief before committing to an approach that depends on external knowledge |
| **Librarian** | Routes codebase context queries to the correct memory backend (Qdrant for semantic code search, Postgres for structured records, file system for raw source) |
| **Security Guard** | Audits all skill invocations that touch the file system, terminal, or git. Enforces execution policy. Scans produced code for known vulnerability patterns |

The Coding Department is a **permanent department**. It maintains its own state: a Coding Task registry, a codebase index per project, and a history of completed changes. It surfaces in the Workers panel under a dedicated "Coding" section.

---

## 2. What the Department Produces

Each output is called a **Coding Deliverable**. The deliverable type is declared in the Coding Task and determines how the Coding Manager structures the work:

| Deliverable Type | Description |
|-----------------|-------------|
| **Feature Implementation** | New functionality added to an existing codebase — new files, new functions, new routes, new UI components |
| **Bug Fix** | A targeted change that resolves a specific reported failure, with a regression test added to prevent recurrence |
| **Refactor** | Structural improvement to existing code with no behaviour change — renaming, extracting functions, reducing duplication, improving readability |
| **Test Suite** | A set of tests (unit, integration, or end-to-end) written for existing untested code |
| **Code Review** | A written review of a code change — correctness, style, security, edge cases, suggested improvements. No code written; analysis only |
| **Greenfield Project** | A new codebase created from scratch — directory structure, configuration, boilerplate, initial implementation |
| **Dependency Upgrade** | Updating one or more dependencies, resolving breaking changes, running tests to confirm compatibility |
| **Documentation** | Inline docstrings, README files, API documentation, architecture decision records — generated from reading the codebase |
| **Script** | A standalone script (automation, data processing, deployment, migration) that doesn't belong to a larger project |

All deliverables are written to disk via the file system skill, tracked in the Coding Task registry, and presented to the Owner for review before any git operations are performed.

---

## 3. Tooling and Skills

The Coding Department uses the following skills and adapters. None of these are owned by the department — they are registered externally and consumed as available capabilities. The Coding Manager checks which skills are available at task intake and degrades gracefully if a skill is missing (e.g., no git skill → deliverable is produced but not committed; Owner is notified).

### 3.1 Core Skills

| Skill | Purpose | Notes |
|-------|---------|-------|
| `terminal` | Execute shell commands, capture stdout/stderr, return exit code | The most critical skill. Almost all other coding operations route through this |
| `file_read` | Read file contents from disk | Used by Reader Workers constantly |
| `file_write` | Write or overwrite file contents | Used by Writer Workers for all output |
| `file_delete` | Delete files | Used for cleanup, dead code removal |
| `directory_tree` | List directory structure recursively | Used at task intake to understand project layout |
| `file_search` | Search file contents by regex or string pattern | Used by Reader Workers to locate relevant code |

### 3.2 Version Control Skills

| Skill | Purpose |
|-------|---------|
| `git_status` | Current working tree state |
| `git_diff` | Show changes between commits, branches, or working tree |
| `git_add` | Stage files for commit |
| `git_commit` | Commit staged changes with a message |
| `git_push` | Push to remote (requires Owner approval before invocation) |
| `git_branch` | Create, list, switch branches |
| `git_log` | Read commit history |
| `git_blame` | Identify who last changed each line (useful for Reader Workers understanding intent) |

### 3.3 Language-Specific Skills

| Skill | Purpose |
|-------|---------|
| `python_run` | Execute a Python file or module via `python` / `python3` |
| `python_test` | Run pytest, unittest, or other Python test runners |
| `python_lint` | Run ruff, flake8, mypy, or black — returns violations |
| `node_run` | Execute a Node.js script |
| `node_test` | Run Jest, Mocha, Vitest |
| `node_lint` | Run ESLint, Prettier |
| `shell_run` | Execute a bash/sh script |
| `package_install` | Run pip install, npm install, etc. (Security Guard approval required) |

Language-specific skills are optional — the Coding Manager checks for availability and adjusts the test/lint steps accordingly. New language skills can be added to the Skills panel without touching the department.

### 3.4 Optional / Adapter-Gated Skills

| Skill / Adapter | Purpose |
|----------------|---------|
| `github_pr` | Open a pull request on GitHub (requires GitHub adapter in Adapters panel) |
| `github_issues` | Read and comment on issues |
| `docker_build` | Build a Docker image |
| `docker_run` | Run a container |
| `database_query` | Execute SQL against a configured database (requires database adapter) |

---

## 4. The Coding Pipeline

A Coding Task enters the department and flows through six stages. Not all stages apply to all deliverable types — the Coding Manager selects the appropriate stages based on the task.

```
Stage 0: Research (optional — Research Department)
       ↓  produces: research deliverable (comparison table, fact sheet, etc.)
Stage 1: Task Intake & Codebase Reading
       ↓
Stage 2: Planning
       ↓
Stage 3: Implementation
       ↓
Stage 4: Testing & Validation
       ↓
Stage 5: Review
       ↓
Stage 6: Presentation & Commit
```

### Stage 0: Research (Optional)

**Actor:** Coding Manager → Research Manager (cross-department event bus message)

Stage 0 is **optional but strongly recommended** for tasks that involve a technical decision the department cannot resolve from the existing codebase alone:

- "Which HTTP client library should we use?"
- "Is there a known security vulnerability in version X of this dependency?"
- "What's the idiomatic way to handle async database connections in this framework?"
- "Should we use approach A or approach B for this architecture decision?"

The Coding Manager issues a `ResearchBriefRequest` to the Research Department with `deliverable_type` set to `comparison_table`, `fact_sheet`, or `source_inventory` as appropriate. Research returns its deliverable before the Coding Manager proceeds to Stage 2.

Unlike the Education Department where Stage 0 is a hard blocking dependency, for the Coding Department Stage 0 is **advisory by default**. The Coding Manager proceeds with best-effort judgement if:

- The task is clearly scoped with no ambiguous technical decisions (e.g., "fix the off-by-one error on line 47")
- The Owner has set `skip_research: true` on the task
- Research does not complete within the timeout (default: 10 minutes for `shallow` depth)

When Stage 0 is skipped, the Coding Manager documents the assumptions made in the task record.

### Stage 1: Task Intake & Codebase Reading

**Actor:** Coding Manager + Reader Workers

This is the most important stage for quality. A Coding Worker that writes code without first understanding the existing codebase produces output that doesn't fit — wrong style, wrong patterns, wrong abstractions, broken imports. Reader Workers exist to prevent this.

**Sub-stages:**

**1A: Task parsing.** The Coding Manager reads the Coding Task (produced by the CEO from the Owner's request) and extracts:

- Deliverable type
- Target project / repository (from the task, or inferred from context)
- Scope (which files, modules, or features are in scope)
- Acceptance criteria (what does "done" look like? which tests must pass? which behaviour must change?)
- Constraints (language version, framework, style guide, dependencies not to add)

**1B: Codebase indexing.** Reader Workers traverse the project structure and build a **Codebase Context** — a structured representation of the project that is attached to all subsequent worker prompts:

```python
@dataclass
class CodebaseContext:
    project_root: str
    language: str                   # detected from file extensions + config files
    framework: str | None           # detected from package.json, requirements.txt, pyproject.toml, etc.
    directory_tree: str             # output of directory_tree skill, truncated to relevant subtrees
    relevant_files: list[FileContext]  # files most relevant to the task
    conventions: ConventionSummary  # inferred style, naming, patterns
    dependencies: list[str]         # from requirements.txt, package.json, etc.
    test_framework: str | None      # pytest, jest, unittest, etc.
    existing_tests: list[str]       # paths of existing test files
    entry_points: list[str]         # main.py, index.js, app.py, etc.
    git_branch: str                 # current branch
    recent_commits: list[str]       # last 5 commit messages — reveals recent intent
```

```python
@dataclass
class FileContext:
    path: str
    content: str          # full file content for small files; summary for large ones
    relevance_score: float  # how directly this file relates to the task
    role: str             # "primary target", "dependency", "test file", "config", etc.
```

**1C: Convention inference.** Reader Workers read a sample of existing source files and infer the project's coding conventions:

- Naming style (snake_case, camelCase, PascalCase)
- Import ordering and grouping
- Docstring format (Google, NumPy, reStructuredText, JSDoc)
- Error handling patterns (exceptions vs return codes vs Result types)
- Testing patterns (fixtures, mocks, assertion style)
- Line length and formatting (inferred from existing code if no config file exists)

These conventions are stored in the `CodebaseContext.conventions` field and injected into every Writer Worker's prompt. This is how the department produces code that looks like it was written by the same person who wrote the rest of the project.

**1D: Memory check.** The Coding Manager queries the Librarian for any past Coding Tasks against the same project — completed changes, past bug fixes, architectural decisions recorded in memory. This prevents the department from re-solving problems it has already solved or undoing past work.

### Stage 2: Planning

**Actor:** Planner Workers (one per logical change unit)

Planner Workers produce a **Change Plan** — a structured, ordered list of changes that will achieve the task's acceptance criteria. Planning is separate from implementation because it is cheap (no file writes, no test runs) and catching a bad plan before writing code is far less costly than catching it after.

**A Change Plan contains:**

```toml
[plan]
task_id    = "fix-login-bug-001"
approach   = "The login failure is caused by the session token not being cleared on logout. Fix: call session.clear() in the logout route handler. Add a test that logs in, logs out, and verifies the session is empty."
risk_level = "low"     # low | medium | high — escalates to Owner if high

[[plan.changes]]
id          = "change-001"
file        = "src/auth/routes.py"
type        = "modify"       # modify | create | delete
description = "Add session.clear() call in the logout() route handler, after the existing token invalidation"
depends_on  = []

[[plan.changes]]
id          = "change-002"
file        = "tests/test_auth.py"
type        = "modify"
description = "Add test_logout_clears_session() — log in, call logout endpoint, assert session is empty"
depends_on  = ["change-001"]

[plan.validation]
commands    = ["python -m pytest tests/test_auth.py -v"]
pass_criteria = "All tests in test_auth.py pass, including the new test"
```

**Risk escalation:** If the Planner assesses `risk_level = "high"` (large number of files touched, changes to core infrastructure, deleting significant code, touching authentication or security logic), the Coding Manager pauses and presents the plan to the Owner before any implementation begins. The Owner can approve, modify, or abort.

**Plan review:** For `medium` and `low` risk tasks, the plan is shown to the Owner as a summary (not a hard block) — the Owner can review it while implementation proceeds, and raise concerns before the Review stage.

### Stage 3: Implementation

**Actor:** Writer Workers (one per change in the Change Plan)

Writer Workers execute the Change Plan, one change at a time, in dependency order. Each Writer Worker:

1. Reads the current content of its target file(s) via `file_read`
2. Produces the modified content, informed by the `CodebaseContext` (especially conventions)
3. Writes the result via `file_write`
4. Reports completion to the Coding Manager with a diff summary

**Writer Worker prompt structure:**

Every Writer Worker receives:
- The specific change it is responsible for (from the Change Plan)
- The full current content of its target file(s)
- The `CodebaseContext` (directory tree, conventions, relevant dependencies)
- The content of files its change depends on (so it can match interfaces, types, function signatures)
- A strict instruction: **only make the changes described in the plan**. Do not refactor unrelated code. Do not rename things that aren't in scope. Do not add features not asked for.

The last instruction is critical. Unconstrained Writer Workers tend to "improve" code they weren't asked to touch, which produces diffs that are hard to review, breaks unrelated tests, and erodes Owner trust.

**Parallel vs sequential execution:**

Changes with no dependencies in the Change Plan run in parallel (multiple Writer Workers simultaneously). Changes with dependencies run sequentially — a Writer Worker that depends on `change-001` waits for `change-001` to be written to disk before reading the target file.

**Large file handling:**

For files too large to fit in a Worker's context window, the Writer Worker operates on a targeted excerpt: the Coding Manager provides the surrounding N lines of the specific function or block being changed, plus the file's import section, rather than the full file. After the Worker produces the modified excerpt, the Coding Manager splices it back into the full file using line-number anchors.

### Stage 4: Testing & Validation

**Actor:** Test Workers + Debug Workers

**4A: Run existing tests.** Test Workers execute the project's existing test suite via the appropriate language skill (`python_test`, `node_test`, etc.). The full output (stdout, stderr, exit code) is captured and returned to the Coding Manager.

- **All pass:** proceed to Stage 5.
- **Pre-existing failures** (failures that existed before this task's changes): the Coding Manager checks git diff — if the failing tests were already failing on the base branch, they are noted but do not block the current task. The Owner is informed.
- **New failures** (tests that passed before the changes but now fail): escalate to Debug Workers.

**4B: Run new tests.** If the Change Plan includes new test cases (it almost always should for bug fixes and features), Test Workers run only the new tests first to confirm they pass. If a new test fails, this is a Writer Worker error — Debug Workers investigate.

**4C: Linting.** Lint Workers run the appropriate linter (`python_lint`, `node_lint`) on all modified files and return violations. Minor style violations are auto-fixed if the linter supports it (e.g., `black --fix`, `ruff --fix`). Violations that cannot be auto-fixed are flagged to the Coding Manager.

**4D: Debug loop.** When Test Workers report failures, Debug Workers take over:

```
Debug Worker receives: { failing_test_output, relevant_source_files, change_diff }

1. Read the error message and traceback carefully
2. Form a hypothesis about the root cause
3. Propose a targeted fix (minimal change — not a rewrite)
4. Present the hypothesis and fix to the Coding Manager
5. Coding Manager applies the fix via Writer Worker
6. Test Workers re-run the failing tests
7. Repeat up to max_debug_iterations (default: 5)
```

After `max_debug_iterations` without resolution, the Coding Manager escalates to the Owner with: a summary of what was tried, the current failure output, and a request for guidance (abort / try a different approach / Owner takes over).

The debug loop is bounded deliberately. An unbounded debug loop burns VRAM, produces increasingly speculative fixes, and is worse than an honest escalation.

### Stage 5: Review

**Actor:** Review Workers

Review Workers read all changes produced in Stage 3 as a senior developer would — independently of the workers who wrote them. They are given the full diff (not the individual files) and the original task description. They check:

| Dimension | Questions |
|-----------|-----------|
| **Correctness** | Does this actually solve the stated problem? Are there edge cases not handled? Off-by-one errors? Null/undefined paths? |
| **Security** | Does this introduce SQL injection, XSS, path traversal, hardcoded secrets, insecure deserialization, or other common vulnerabilities? |
| **Style consistency** | Does the new code match the project's existing conventions (naming, formatting, docstrings, import order)? |
| **Test quality** | Do the new tests actually test the right things? Are they testing implementation details rather than behaviour? Would they catch a regression? |
| **Scope discipline** | Did Writer Workers change anything outside the scope of the plan? |
| **Unnecessary complexity** | Is there a simpler way to achieve the same result that would be easier to maintain? |

The Review Worker produces a structured **Review Report:**

```toml
[review]
task_id      = "fix-login-bug-001"
verdict      = "approve"     # approve | approve_with_notes | request_changes

[[review.findings]]
severity     = "info"        # info | warning | blocking
file         = "src/auth/routes.py"
line         = 47
description  = "session.clear() is correct here, but add a comment explaining why this order matters (token invalidation before session clear)"
suggestion   = "# Invalidate token first, then clear session — reversing this order causes a race condition under async load"

[[review.findings]]
severity     = "warning"
file         = "tests/test_auth.py"
line         = 112
description  = "test_logout_clears_session passes but only tests the happy path. Consider adding a test where logout is called without a valid session."
```

**Verdict meanings:**

- `approve` — changes are good, proceed to Stage 6
- `approve_with_notes` — minor issues noted (info/warning severity only), proceed but the Coding Manager applies any auto-fixable suggestions first
- `request_changes` — blocking issues found. Coding Manager sends the Review Report back to Writer Workers as additional context and re-runs the affected changes. Test and Review stages repeat.

**Maximum review cycles:** 3. After 3 cycles without `approve` or `approve_with_notes`, the Coding Manager escalates to the Owner.

### Stage 6: Presentation & Commit

**Actor:** Coding Manager

**6A: Owner presentation.** The Coding Manager prepares a structured summary for the Owner:

```
Coding Task complete: Fix login session bug
─────────────────────────────────────────
Files changed: 2
  src/auth/routes.py  (+3 lines, -1 line)
  tests/test_auth.py  (+18 lines)

Tests: 47 passed, 0 failed (including 2 new tests)
Lint: clean
Review: approved with 1 note (comment added to explain token invalidation order)

Change summary:
  - Added session.clear() after token invalidation in logout() handler
  - Added test_logout_clears_session() and test_logout_without_session()

Actions:
  [Commit]  [View diff]  [Request changes]  [Abort]
```

The Owner must take an explicit action. Nothing is committed without Owner approval. This is a hard rule — not a default.

**6B: Commit.** On Owner approval, the Coding Manager:

1. Stages all changed files via `git_add`
2. Commits with a structured message (Conventional Commits format by default):
   ```
   fix(auth): clear session on logout to prevent stale token reuse

   Added session.clear() after token invalidation in logout() handler.
   Added regression tests: test_logout_clears_session, test_logout_without_session.

   Closes: #47
   Research: N/A
   ```
3. If a `github_pr` skill is available and the Owner approved PR creation, opens a pull request.

**6C: Task record.** The completed task is written to the Coding Task registry with full provenance: which workers ran, what the Change Plan was, what the Review findings were, which files were changed, the commit hash.

---

## 5. Codebase Index

The Coding Department maintains a persistent **Codebase Index** per project. This is distinct from the per-task `CodebaseContext` built in Stage 1 — the Index is a long-lived, incrementally updated representation of a project that persists between tasks and is stored in the memory backends.

### 5.1 What the Index Contains

```
Project Index: SovereignAI
├── Structure snapshot        (directory tree, last updated)
├── File summaries            (one-paragraph summary of each file's purpose)
├── Symbol index              (functions, classes, methods → file + line)
├── Dependency graph          (which files import which)
├── Convention record         (inferred style and patterns)
├── Test coverage map         (which source files have corresponding tests)
├── Past task history         (list of completed Coding Tasks with their diffs)
└── Known issues              (bugs or tech debt noted during past Review stages)
```

### 5.2 Index Maintenance

The Index is built on first contact with a project and updated incrementally after each completed Coding Task:

- **File summaries** are regenerated for any file touched by a task
- **Symbol index** is updated for any file modified
- **Test coverage map** is updated when new tests are added
- **Known issues** are updated based on Review Worker findings

The Index is stored in Qdrant (vector embeddings for semantic search) and Postgres (structured records for exact lookup). The Librarian routes Reader Worker queries to the appropriate backend.

### 5.3 Multi-Project Support

The Coding Department can maintain indexes for multiple projects simultaneously. The Coding Manager selects the correct project index at task intake, inferred from the task description or explicitly specified by the Owner. Projects are registered in the Coding Task registry with a root path and a display name.

---

## 6. Task Types: Specific Behaviour

### 6.1 Bug Fix

The most common task type. Additional behaviour beyond the standard pipeline:

- **Reproduction first:** before writing any fix, Debug Workers attempt to write a failing test that reproduces the bug. If they succeed, this test becomes the primary acceptance criterion — the fix is only "done" when this test passes.
- **Root cause required:** the Change Plan must include a `root_cause` field explaining why the bug occurs, not just what the fix is. This is recorded in the task history and surfaced in the commit message.
- **Regression test mandatory:** a Coding Task of type `bug_fix` cannot reach Stage 6 without at least one new test case.

### 6.2 Greenfield Project

Creates a new codebase from scratch. Additional behaviour:

- **Stage 0 (Research) is recommended** for technology selection — language, framework, testing library, project structure conventions.
- **Scaffolding first:** before writing any business logic, Writer Workers produce the project skeleton — directory structure, config files (`pyproject.toml`, `package.json`, `.gitignore`, `README.md`), and empty entry points. Owner reviews and approves the skeleton before implementation begins.
- **Convention bootstrapping:** since there is no existing codebase to infer conventions from, the Coding Manager asks the Owner for preferences (or uses Research Department findings) and records them explicitly in the project's `conventions.toml`.

### 6.3 Code Review (Analysis Only)

No code is written. Additional behaviour:

- Reader Workers read the diff or the specified files.
- Review Workers run the full review checklist.
- The deliverable is the Review Report only — no file writes, no git operations.
- Useful for reviewing PRs from other sources (Devin output, external contributors, code pasted by the Owner).

### 6.4 Dependency Upgrade

- **Stage 0 (Research) is strongly recommended** — the Research Department checks for known breaking changes, changelogs, and CVEs between the old and new version.
- After upgrading the dependency manifest (`requirements.txt`, `package.json`, etc.) and running the install skill, Test Workers run the full test suite.
- If failures occur, Debug Workers read the changelogs (provided by Research) to identify which API changes caused the failures and produce targeted fixes.

### 6.5 Documentation

No executable code is produced. Additional behaviour:

- Reader Workers read every file in scope thoroughly.
- Writer Workers produce documentation that accurately reflects the code — not generic boilerplate.
- For docstrings: produced inline in the source files. For READMEs and architecture docs: produced as separate files.
- Review Workers check documentation against the actual code — mismatches between docs and implementation are blocking findings.

---

## 7. Integration with Other Departments

### 7.1 Research Department

The Coding Department is a frequent consumer of Research deliverables. Common patterns:

- Before choosing a library: `comparison_table` of candidates
- Before a security-sensitive change: `fact_sheet` on relevant CVEs or security patterns
- Before a dependency upgrade: `source_inventory` of changelogs and breaking changes
- Before architectural decisions: `research_report` on approaches

The Coding Manager issues Research Briefs with `depth = "shallow"` for most queries (fast turnaround, top sources only) and `depth = "standard"` for significant architectural decisions.

### 7.2 Education Department

The Coding Department and Education Department have a bidirectional relationship:

- **Coding → Education:** completed Coding Tasks (change diffs, test results, debug traces) are candidate training data for Expert Models. A "Python Coder" Expert Model trained partly on the system's own successful coding outputs will improve over time.
- **Education → Coding:** once an Expert Model (e.g., Python Coder v1) is registered in the Models panel, the Coding Manager can set it as the default model for Python-specific Writer Workers, replacing or supplementing the general-purpose model. Smaller, faster, domain-specialized.

### 7.3 Communication Department

When a Coding Task produces output that needs to be communicated externally (a release announcement, a changelog, a technical blog post about an implementation decision), the Coding Manager can hand off to the Communication Department with the task record as context. The Communication Manager reads the technical details and produces the appropriate written output.

### 7.4 Operations Department

Long-running or scheduled coding tasks (nightly dependency audits, weekly lint runs, scheduled test suite execution) are registered in the Tasks panel by the Operations Department. The Coding Manager executes the task; the Operations Manager handles the scheduling and recurring trigger logic.

---

## 8. Security Guard Integration

The Security Guard has audit hooks into the Coding Department at the following points:

- **Skill invocation approval:** every call to the `terminal`, `file_write`, `file_delete`, `git_push`, and `package_install` skills requires Security Guard sign-off before execution. The Security Guard checks the command against its policy rules (e.g., `rm -rf /` is never permitted; `pip install` of an unknown package requires Owner confirmation).
- **Code scanning:** after Stage 3 (Implementation), all produced code is scanned for known vulnerability patterns before testing begins. Findings are surfaced as Review Worker findings with `severity = "blocking"` if high-severity.
- **git_push gate:** `git_push` is never invoked without both Owner approval (Stage 6) and Security Guard clearance. It is the highest-privilege git operation and is treated as such.
- **Dependency audit:** when `package_install` is invoked, the Security Guard checks the package name against known malicious package lists and verifies the installed version hash matches the published registry hash (supply chain protection).

---

## 9. Execution Policy

The execution policy governs what the Coding Department is permitted to do autonomously vs what requires Owner approval. It is configured in the Options panel under "Coding Department" and enforced by the Security Guard.

| Action | Default Policy |
|--------|---------------|
| Read any file in project root | Auto-approved |
| Write files in project root | Auto-approved (within task scope) |
| Write files outside project root | Owner approval required |
| Delete files | Owner approval required |
| Run tests | Auto-approved |
| Run linter | Auto-approved |
| Install packages | Owner approval required |
| Git add + commit | Auto-approved (after Owner approves deliverable in Stage 6) |
| Git push | Owner approval required (separate from commit approval) |
| Open pull request | Owner approval required |
| Execute arbitrary shell commands | Owner approval required |
| Network access during execution | Blocked by default; Owner opt-in per task |

The Owner can promote any action to auto-approved or demote it to require explicit approval. Changes are logged by the Security Guard.

---

## 10. Integration with the Models Panel

The Coding Department uses models from the Models panel for all worker inference. The Manager selects models per worker role:

| Worker Role | Default Model Selection Strategy |
|-------------|----------------------------------|
| Reader Workers | Fastest available model with large context window — reading is cheap, context is the constraint |
| Planner Workers | Best available reasoning model — planning quality determines everything downstream |
| Writer Workers | If a domain-specific Expert Model (Education Department) is available for the language, use it. Otherwise, best general-purpose coding model available |
| Test Workers | Fast model — test writing is structured and formulaic |
| Review Workers | Best available model — review requires the broadest knowledge |
| Debug Workers | Best available reasoning model — debugging requires hypothesis formation |

The Coding Manager queries the Models panel catalog at task intake to determine which models are loaded and available, and selects accordingly. The Owner can override model selection per role in the Options panel.

---

## 11. Backend Module Layout

```
/backend
  /coding
    manager.py                  # Coding Manager — orchestrates all stages
    task_store.py               # CRUD for coding tasks (Postgres/SQLite)
    project_registry.py         # registered projects with root paths and index metadata
    codebase_index.py           # build, update, query the persistent Codebase Index
    convention_inferrer.py      # Stage 1C: infer project conventions from source files
    execution_policy.py         # reads policy config, checked before every skill invocation
    /workers
      reader.py                 # Stage 1B: directory traversal, file reading, context building
      planner.py                # Stage 2: change plan generation
      writer.py                 # Stage 3: code generation and file writing
      test_runner.py            # Stage 4A/4B: invoke test skills, parse results
      linter.py                 # Stage 4C: invoke lint skills, parse results
      debugger.py               # Stage 4D: debug loop
      reviewer.py               # Stage 5: review checklist, Review Report generation
    /task_types
      bug_fix.py                # Stage overrides for bug fix tasks
      greenfield.py             # Stage overrides for greenfield projects
      dependency_upgrade.py     # Stage overrides for dependency upgrades
      documentation.py          # Stage overrides for documentation tasks
      code_review.py            # Stage overrides for review-only tasks
    api.py                      # REST endpoints
      # GET  /coding/tasks
      # POST /coding/tasks                (submit Coding Task)
      # GET  /coding/tasks/<id>           (status + stage progress)
      # POST /coding/tasks/<id>/cancel
      # POST /coding/tasks/<id>/approve   (Owner approval at Stage 6)
      # POST /coding/tasks/<id>/reject    (Owner requests changes at Stage 6)
      # GET  /coding/projects             (registered projects)
      # POST /coding/projects             (register new project)
      # GET  /coding/projects/<id>/index  (Codebase Index for a project)

/frontend
  /components/coding/
    CodingPanel.tsx             # main Coding sub-view inside Workers panel
    CodingTaskList.tsx          # list of all tasks with status indicators
    CodingTaskDetail.tsx        # stage progress, live log drawer, current worker activity
    ChangePlanViewer.tsx        # read-only view of the Change Plan before implementation
    DiffViewer.tsx              # syntax-highlighted diff of all changes at Stage 6
    ReviewReportViewer.tsx      # structured Review Report with findings
    ApprovalPanel.tsx           # Owner approve/reject/request-changes at Stage 6
    ProjectList.tsx             # registered projects with index health indicators
    CodebaseIndexViewer.tsx     # browse the Codebase Index for a project
    ExecutionPolicyEditor.tsx   # in Options panel — configure per-action approval policy
```

---

## 12. Open Questions for Round Table

1. **Scope of terminal access:** The `terminal` skill gives workers access to an arbitrary shell. This is extremely powerful and extremely dangerous. Should the terminal skill be sandboxed (e.g., restricted to the project root via a chroot or Docker container), or is the Security Guard's execution policy the sole control? Sandboxing is safer but adds infrastructure complexity and may break some legitimate use cases (e.g., running a development server that binds to a port).

2. **Context window management for large codebases:** A production codebase with hundreds of files cannot fit in any model's context window. The Codebase Index partially addresses this, but Writer Workers still need enough context to write correct code. What is the right strategy for very large files or deeply interconnected codebases — sliding window, chunked summarisation, retrieval-augmented prompting from the index, or something else?

3. **Concurrent tasks against the same project:** If two Coding Tasks run simultaneously against the same project, their Writer Workers will both be reading and writing files, creating potential conflicts. Should the Coding Manager enforce a per-project task queue (only one active task per project at a time), or implement file-level locking, or rely on git branches to isolate concurrent work?

4. **Autonomous commit policy:** Currently, commits require explicit Owner approval at Stage 6. For low-risk, high-confidence tasks (e.g., auto-formatting, lint fixes, documentation updates), should there be an "auto-commit" mode where the Owner pre-approves a class of changes? This would allow unattended operation for maintenance tasks.

5. **Test generation quality:** Test Workers writing tests for untested code face a fundamental problem — they don't know the intended behaviour, only the existing implementation. Tests written this way test the current behaviour, not the correct behaviour, which means they pass even when the implementation is wrong. How should the system handle this? Options: flag auto-generated tests as "implementation tests, not specification tests"; require Owner review of all auto-generated tests; use Research Department to find specification documents before writing tests.

6. **Multi-language projects:** Many real projects mix languages (Python backend, TypeScript frontend, Bash scripts, SQL migrations). The Coding Manager needs to select the right language skills per file. Is the language detected per-file from extension and content, or declared per-project at registration?

7. **External code execution risk:** Running test suites means executing code that the Coding Department itself may have just written. A malicious or subtly broken change could produce code that causes harm when executed. The Security Guard scans produced code before testing, but static scanning is imperfect. Is the sandbox question (Open Question 1) the right mitigation, or are there additional controls needed?

8. **Integration with Devin:** The project currently uses Devin for code implementation. How does the Coding Department relate to Devin? Is Devin replaced by the Coding Department, used alongside it, or used as a fallback for tasks the Coding Department cannot handle? This needs a clear answer before the Coding Department is built, since they occupy overlapping scope.

---

## 13. Implementation Order (Suggested)

1. **task_store.py + project_registry.py** — scaffolding and data model. Register a test project before any workers are written.
2. **reader.py + convention_inferrer.py** — Stage 1 workers. Validate that the Codebase Context produced is accurate and useful for a real project before building anything that depends on it.
3. **execution_policy.py + Security Guard hooks** — establish the safety boundary before any file writes are possible. The policy engine must exist before Writer Workers are introduced.
4. **writer.py (simple case)** — Stage 3, single-file modifications only. Validate with a trivial task ("add a docstring to this function") before tackling multi-file changes.
5. **planner.py** — Stage 2. Once Writer Workers are validated, add the planning layer on top.
6. **test_runner.py + linter.py** — Stage 4A/4C. Wire to Python skills first; validate that test output is correctly parsed and reported.
7. **reviewer.py** — Stage 5. Validate that the Review Report structure is useful and that blocking findings correctly trigger re-implementation.
8. **ApprovalPanel.tsx + DiffViewer.tsx** — Stage 6 UI. The Owner approval flow must exist before git operations are wired.
9. **git skills integration** — git_add + git_commit only. Push deferred until approval flow is proven stable.
10. **debugger.py** — Stage 4D debug loop. Add after the happy path is fully working.
11. **codebase_index.py** — persistent Codebase Index. Add after per-task context has been validated; the Index is an optimisation on top of it.
12. **task_types/** — bug_fix, greenfield, dependency_upgrade, documentation, code_review specialisations. Add one at a time, validating each against real tasks.
13. **Research Department integration (Stage 0)** — add once the core pipeline is stable and Research Department is operational.
14. **Education Department integration** — set Expert Models as Writer Worker defaults once Education Department produces its first Expert Model.
15. **git_push + github_pr** — highest-privilege operations, added last after all other controls are proven.

---

*End of document.*
