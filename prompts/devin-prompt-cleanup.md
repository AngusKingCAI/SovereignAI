# Devin Prompt — Source Code Cleanup: Strip Docstrings + OR References

## Task

Remove all docstrings and all OR{n} governance references from SovereignAI source code, tests, and manifests. These are token overhead with no functional value.

## Rules

1. **AR17 (new):** No docstrings in Python source. Use clear function/class/variable names instead. Code must be self-documenting.

2. **No OR references in source code:** OR rules are governance for Devin's workflow, not SovereignAI's code. Remove every `(per OR{n})`, `Per OR{n}:`, `# Per OR{n}` comment from Python files, test files, TOML manifests, and pyproject.toml. If the comment explains behavior, keep the behavior explanation but remove the OR number.

## Files to modify

### Python source (strip docstrings + OR references)

1. `sovereignai/workers/education/teacher_worker.py` — strip docstrings, remove `OR70` ref
2. `sovereignai/orchestrator/dispatcher.py` — strip docstrings, remove `OR56` ref
3. `sovereignai/librarian/librarian.py` — strip docstrings, remove `OR86` refs (×2)
4. `sovereignai/skills/official/self_correction/skill.py` — strip docstrings, remove `OR69` ref
5. `sovereignai/memory/episodic_backend.py` — strip docstrings, remove `OR87` refs (×3)
6. `sovereignai/memory/trace_backend.py` — strip docstrings, remove `OR87` refs (×3)
7. `sovereignai/memory/procedural_backend.py` — strip docstrings, remove `OR87`, `OR89` refs (×5)
8. `sovereignai/memory/working_backend.py` — strip docstrings, remove `OR87` refs (×2)
9. `sovereignai/memory/__init__.py` — strip docstrings, remove `OR87` ref
10. `sovereignai/versioning/negotiator.py` — strip docstrings, remove `OR57`, `OR67` refs (×4)
11. `sovereignai/versioning/compatibility_matrix.py` — strip docstrings, remove `OR59` refs (×4)
12. `sovereignai/shared/types.py` — strip docstrings, remove `OR20`, `OR57` refs (×7)
13. `web/main.py` — strip docstrings, remove `OR49`, `OR50`, `OR52` refs (×4)
14. All other `.py` files in `sovereignai/` and `web/` — strip docstrings only

### Tests (strip docstrings + OR references)

15. `tests/test_self_correction_skill.py` — strip docstrings, remove `OR69` refs (×2)
16. `tests/test_teacher_worker.py` — strip docstrings, remove `OR70` ref
17. `tests/test_web_server.py` — strip docstrings, remove `OR24` ref
18. `tests/test_fatal_error_noninteractive.py` — strip docstrings, remove `OR67` ref
19. All other test files — strip docstrings only

### Manifests + config (remove OR references only, no docstrings to strip)

20. `sovereignai/workers/education/manifest.toml` — remove `OR48` ref
21. `sovereignai/skills/official/self_correction/manifest.toml` — remove `OR48` ref
22. `pyproject.toml` — remove `OR39` refs (×2), disable Ruff D103 rule

### AR check scripts

23. `scripts/ar_checks/docstring_discipline.py` — DELETE this file (AR17 now prohibits docstrings, so the checker is obsolete)
24. `.devin/workflows/close.md` — remove `docstring_discipline.py` from step 8 AR checks list
25. `.pre-commit-config.yaml` — remove docstring enforcement if present

## Examples

**Before:**
```python
def store_episodic_memory(self, data: dict) -> str:
    """Store an episodic memory record in the SQLite database with WAL mode.
    
    Per OR87: Stores episodic memory in ~/.sovereignai/episodic.db
    Per OR89: Uses atomic writes with WAL mode and busy_timeout=5000.
    """
    conn = self._get_connection()
    ...
```

**After:**
```python
def store_episodic_memory(self, data: dict) -> str:
    conn = self._get_connection()
    ...
```

**Before:**
```python
# Per OR20: UTC, timezone-aware (naive/aware datetime mixing caused L6)
timestamp: datetime
```

**After:**
```python
timestamp: datetime  # UTC, timezone-aware
```

**Before:**
```toml
content_hash = "<computed at /close per OR48>"
```

**After:**
```toml
content_hash = "<computed at /close>"
```

**Before:**
```toml
# Runtime deps live in txt/requirements.txt (SSOT per OR39).
```

**After:**
```toml
# Runtime deps live in txt/requirements.txt (SSOT).
```

## What NOT to remove

- **Comments that explain non-obvious behavior** — keep the explanation, just remove the OR number. Example: `# UTC, timezone-aware` stays; `# Per OR20: UTC, timezone-aware` becomes `# UTC, timezone-aware`.
- **Type annotations** — these are code, not documentation.
- **Inline comments explaining complex logic** — keep these, they're not docstrings.

## Verification

After all changes:
1. `python -m pytest tests/ -vvv` — all tests must pass
2. `ruff check .` — no errors (D103 disabled in pyproject.toml)
3. `grep -rn "OR[0-9]" sovereignai/ web/ tests/ --include="*.py" --include="*.toml"` — must return ZERO results
4. `grep -rn '"""' sovereignai/ web/ tests/ --include="*.py"` — must return ZERO results (no docstrings remain)

## Commit

`git add -A && git commit -m "Remove docstrings and OR references from source code (AR17)"`

Tag: not needed — this is a cleanup commit, not a plan close.

## Additional repo-side fixes (PLANS.md, DEBT.md, DECISIONS.md)

These files reference the OLD numbering scheme (pre-Rev 9 renumber). Fix them:

### PLANS.md
- Find: "Numbering policy (per OR84)" → Replace with: "Numbering policy (per OR46)"
- Find: "New rules continue from OR85" → Replace with: "New rules continue from OR66"
- Find: "new landmines from L40" → Replace with: "new landmines from L47"
- Find: "Coverage measured at every /close per OR77" → Replace with: "Coverage measured at every /close per OR43"
- Find any other references to OR66-OR120 or AR18-AR21 → update to current numbering or remove
- **Historical rows exemption**: The "Completed Prompts" table (rows like "prompt-10.1 ... OR75" and "prompt-10.2 ... OR76-OR82") contains historical references to old rule numbers. These are historical records, not live citations. Add a disclaimer above the Completed Prompts table: `> **Note**: Rule numbers in historical rows refer to the numbering scheme active at that time.`

### DEBT.md
- Find the AR21 deferred item (docstring discipline) → Mark as RESOLVED with note: "AR21 retired in workflow rev 12. Docstrings now prohibited per AR17. Reversed by design — see DECISIONS.md D6."
- Find any references to OR66-OR120 or AR18-AR21 → update to current numbering or remove

### DECISIONS.md
- Add new decision entry:
  ```
  ## D6 — AR17 reversal: docstrings prohibited (was AR21 mandated)
  
  **Context**: AR21 (old numbering) mandated docstrings on every function — verb-first, ≥10 words, no jargon. This was enforced via Ruff D103 + custom check script.
  
  **Decision**: Reversed. AR17 (new numbering) now PROHIBITS docstrings. Ruff D103 disabled. `scripts/ar_checks/docstring_discipline.py` deleted.
  
  **Rationale**: Token efficiency. Docstrings cost ~500-600 output tokens per plan + ~30% context inflation per file read. LLMs understand code by reading implementation, not plain-English summaries. The sole code author is Devin (AI agent), not a human reader.
  
  **Trade-off**: Future human contributors will find code harder to onboard to. Revisit if human contributors join.
  
  **Date**: Workflow rev 12 (post-18.3 audit)
  ```

- Add second decision entry:
  ```
  ## D7 — OR65 spec-match: mechanical-only, LLM layer removed
  
  **Context**: OR65 originally had two layers — Layer 1 (mechanical `spec_match.py`) and Layer 2 (Claude semantic review if available). Layer 2 was the primary defense against L46 (rules dropped from plan spec).
  
  **Decision**: Layer 2 removed. `spec_match.py` is the sole gate. No LLM dependency in governance files.
  
  **Rationale**: Governance files should not reference external tools (Claude) by name. The mechanical gate catches rule-ID diffs, placeholder markers, artifact existence, and scope contraction. Semantic gaps that the mechanical gate misses are caught by the Round Table review process (pre-execution) and OR52 (logged verification per "already done" claim).
  
  **Trade-off**: A mechanical script cannot detect prose-level spec drift (e.g., "plan said implement feature X, code implements feature Y"). This is accepted — the Round Table catches spec issues before execution, and the close report + execution log provide human reviewable artifacts post-execution.
  
  **Date**: Workflow rev 14
  ```

### Verification after repo-side fixes
- `grep -rn "OR8[0-9]\|OR9[0-9]\|OR1[0-2][0-9]" PLANS.md DEBT.md` — must return ZERO results (no old OR numbers ≥80)
- `grep -rn "AR1[89]\|AR2[01]" PLANS.md DEBT.md` — must return ZERO results (no old AR numbers ≥18)
- `grep -rn "AR21" DEBT.md` — must return ZERO results (or only in RESOLVED state)

### CHANGELOG.md
Add this disclaimer as the FIRST line of CHANGELOG.md (before any entries):
```
> **Note**: Rule numbers (OR{n}/AR{n}) in older entries refer to the numbering scheme active at that time and may not match current AGENTS.md. Current rules: OR1-OR65, AR1-AR17.
```
