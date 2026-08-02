# SovereignAI -- Diff-Based Editing Design Document v1.0

**Status**: Draft -- approved for implementation  
**Date**: 2026-07-03  
**Author**: Architect  
**Depends on**: `../PRINCIPLES.md`, `../AGENTS.md`, `../DECISIONS.md`, `../AI_HANDOFF.md`, `SovereignAI_Skill_Agent_System_Design_v1.0.md`

---

## 1. Context

**Gap**: #6 -- Diff-Based Editing  
**Problem**: The `file_edit` skill needs to modify files efficiently without full rewrites. Token efficiency matters for local models with limited context windows.  
**Scope**: How the `file_edit` skill applies changes to files in a multi-step ReAct loop.

---

## 2. Design Decision

**DD-21.9.1**: Diff-based editing (Proposed, P9/P13/P5-aligned): Search/replace blocks (Aider-style) with optional line-range hint. Search text is primary (self-locating, drift-immune). Line-range hint is optional disambiguation. Parser: exact match -> apply; no match -> fuzzy fallback with warning trace; ambiguous -> error with retry. All failures loud. P9/P13 compliant.

---

## 3. Format

```json
{
  "file": "auth.py",
  "search_hint": {"start": 5, "end": 10},
  "search": "def login():\n    print(\"Hello\")\n    return True",
  "replace": "def login():\n    print(\"Goodbye\")\n    return True"
}
```

**Fields**:
- `file` (required): Relative path to target file
- `search_hint` (optional): `{start: int, end: int}` line range to search within
- `search` (required): Exact text to find (including whitespace)
- `replace` (required): Replacement text

---

## 4. Parser Logic

```python
class DiffParser:
    def apply(self, edit: FileEdit, project_root: Path) -> EditResult:
        file_path = project_root / edit.file
        content = file_path.read_text()

        # Step 1: Try search_hint if provided
        if edit.search_hint:
            hint_content = self._extract_lines(content, edit.search_hint)
            if edit.search in hint_content:
                return self._apply_in_range(content, edit, edit.search_hint)
            self._trace.emit(level=WARN, message="search_hint missed, falling back")

        # Step 2: Full-file exact match
        matches = self._find_all(content, edit.search)
        if len(matches) == 1:
            return self._apply_at(content, edit, matches[0])

        # Step 3: Fuzzy fallback
        if len(matches) == 0:
            fuzzy_match = self._fuzzy_find(content, edit.search)
            if fuzzy_match and fuzzy_match.confidence > 0.9:
                self._trace.emit(level=WARN, message="fuzzy match applied")
                return self._apply_at(content, edit, fuzzy_match.position)
            raise EditError("search_not_found", "No match found. Retry with exact text.")

        # Step 4: Ambiguous
        if len(matches) > 1:
            raise EditError(
                "ambiguous_match",
                f"Found {len(matches)} matches. Provide search_hint or add context lines."
            )
```

---

## 5. Why Not Line-Range Only (E)

**Fatal flaw**: Multi-step ReAct line drift.

```
Turn 1: Model reads auth.py (50 lines). Observation includes content.
Turn 2: Model emits edit: "replace lines 5-7". Applied. File now 52 lines.
Turn 3: Model emits another edit: "replace lines 10-12".
        -- BUT lines 10-12 have shifted +2 due to Turn 2's edit.
        -- Model is using stale line numbers from Turn 1's observation.
        -- Edit applies to the WRONG lines. Silently.
```

**Failure mode comparison**:

| Failure | E (line-range) | A+ (search/replace) |
|---------|---------------|---------------------|
| Line numbers off by 1 | Silent corruption | Loud: "not found" |
| Line drift | Silent corruption | Loud: "not found" |
| Range exceeds file | Loud (IndexError) | N/A |
| Valid syntax, wrong location | Silent corruption | N/A |

E has **two silent failure modes** -- P9 violation. A+ has **zero**.

---

## 6. Token Efficiency Reality

For a 3-line edit in a 300-line file, 5-edit ReAct loop:

| Option | Tokens per edit | Re-read needed? | Total for 5 edits |
|--------|----------------|-----------------|-------------------|
| A+ (search/replace + hint) | ~80 | No | ~400 |
| E (line-range) | ~60 | Yes (full file each turn) | ~15,060 |
| B (whole-file rewrite) | ~3,000 | No | ~15,000 |

E's per-edit advantage is wiped out by the re-read requirement. A+ is **37x more token-efficient** in a 5-edit ReAct loop.

---

## 7. Enhancements Over Naive Search/Replace

### 7.1 Whitespace Normalization
```python
def _normalize(text: str) -> str:
    return text.rstrip().replace("\t", "    ")
```

### 7.2 Context Lines
Search block includes 2-3 lines before/after the change for disambiguation:
```python
"search": "# User authentication\ndef login():\n    print(\"Hello\")\n    return True\n# End login"
```

### 7.3 Fuzzy Matching
```python
def _fuzzy_find(self, content: str, search: str) -> FuzzyMatch | None:
    # Edit distance threshold: 90% similarity
    # Reject if multiple matches above threshold
```

### 7.4 Retry with Error Feedback
Same pattern as DD-21.3.1:
```
Your search block was not found. Closest match at line 47 with 2 character differences.
Please retry with the exact text from the file.
```

---

## 8. Rejected Alternatives

### 8.1 B -- Whole-File Rewrite
- **Why rejected**: Token-expensive. "Lost in the middle" risk on large files.
- **Consequence**: 15,000 tokens for 5-edit loop on 300-line file.

### 8.2 C -- Script Generation (sed/ripgrep)
- **Why rejected**: P4 violation (Windows shell differences). Security risk.
- **Consequence**: Platform-dependent, requires sandbox.

### 8.3 D -- Adaptive (Choose Format Per Edit)
- **Why rejected**: P5 violation. Decision model = speculative contract. Two parsers.
- **Consequence**: Runtime complexity. Wrong decision = wrong format.

### 8.4 E -- Line-Range Only
- **Why rejected**: P9 violation (silent corruption). ReAct-hostile (line drift).
- **Consequence**: Wrong-line edits undetected. Model continues with corrupted file.

---

## 9. Rationale

| Principle | How A+ Honors It |
|-----------|-----------------|
| P9 (no silent failures) | All failure modes loud. No silent corruption. |
| P13 (strong and robust) | Retry with error feedback. Typed errors. |
| P5 (no speculative contracts) | One parser. One format. No decision model. |
| P4 (local-first) | Pure Python. No shell dependency. |

---

## 10. Data Structures

```python
@dataclass(frozen=True)
class FileEdit:
    file: str
    search: str
    replace: str
    search_hint: LineRange | None = None

@dataclass(frozen=True)
class LineRange:
    start: int
    end: int

@dataclass(frozen=True)
class EditResult:
    success: bool
    bytes_changed: int
    new_size: int
    error: EditError | None = None

@dataclass(frozen=True)
class EditError:
    error_type: str  # "search_not_found" | "ambiguous_match" | "file_not_found"
    message: str
    suggestion: str | None = None
```

---

## 11. Extension Points

| Extension | Trigger | Interface |
|-----------|---------|-----------|
| Multi-file edits | Single response edits multiple files | `list[FileEdit]` |
| Hunk-based diffs | Git-style patch application | `apply_patch(diff_text)` |
| AST-aware editing | Structural code changes | `ast_edit(node_path, replacement)` |

---

## 12. Open Questions

| ID | Question | Status |
|----|----------|--------|
| Q-21.9.1 | Should diff-based editing support multi-file edits in single response? | Deferred |
| Q-21.9.2 | Should hunk-based git diffs be supported as alternative format? | Deferred |
| Q-21.9.3 | Should AST-aware structural editing be added for Python? | Deferred to v2+ |

---

## 13. Implementation Plan

**Plan 21.9** (Diff-Based Editing):
- S1: DiffParser class with search/replace logic
- S2: Whitespace normalization + fuzzy matching
- S3: search_hint support
- S4: Retry integration with ReAct loop
- S5: Tests for all failure modes (not found, ambiguous, drift)

---

*End of document.*
