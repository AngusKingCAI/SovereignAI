# SovereignAI -- Codebase Indexing Design Document v1.0

**Status**: Draft -- approved for implementation  
**Date**: 2026-07-03  
**Author**: Architect  
**Depends on**: `../PRINCIPLES.md`, `../AGENTS.md`, `../DECISIONS.md`, `../AI_HANDOFF.md`, `SovereignAI_Skill_Agent_System_Design_v1.0.md`

---

## 1. Context

**Gap**: #5 / #10 -- Context/Repo Indexing  
**Problem**: The coding agent needs to understand the codebase structure to answer "where is the auth module?" and "what does UserService do?"  
**Scope**: How SovereignAI indexes code for ReAct prompt context construction.

---

## 2. Design Decision

**DD-21.10.1**: Codebase indexing (Proposed, P3/P4/P5/AR6/AR22-aligned): Symbol map (Aider-style) for v1. Tree-sitter extracts symbol definitions and references -> builds directed graph -> PageRank ranks by relevance to currently-edited files -> ranked context string (~1024 tokens) injected into ReAct prompt. No embeddings, no vector store, no ML model.

---

## 3. Architecture

### 3.1 Service Placement

Per AR25: "databases/ and services/ are root-level packages, never nested in sovereignai/."

```
services/
  ollama_service/
    __init__.py
    provider.py
  codebase_index/
    __init__.py
    provider.py              # CodebaseIndex service
    symbol_map.py            # SymbolMap dataclass + builder
    pagerank.py              # hand-rolled PageRank (~30 lines)
    tree_sitter_extractor.py # tree-sitter -> SymbolMap
```

Registered in DI container per D4:
```python
container.register(CodebaseIndex, codebase_index_instance)
```

### 3.2 Interface

```python
class CodebaseIndex:
    def rank_for_task(
        self,
        current_files: list[Path],
        token_budget: int = 1024
    ) -> str:
        ...

    def invalidate(self, paths: list[Path]) -> None:
        ...
```

### 3.3 Data Structures

```python
class SymbolKind(Enum):
    FUNCTION = "function"
    CLASS = "class"
    METHOD = "method"
    VARIABLE = "variable"
    IMPORT = "import"

@dataclass(frozen=True)
class Symbol:
    name: str
    kind: SymbolKind
    file: Path
    line_range: tuple[int, int]

@dataclass(frozen=True)
class SymbolReference:
    symbol: Symbol
    referenced_by: Symbol

@dataclass(frozen=True)
class SymbolMap:
    symbols: dict[str, Symbol]
    references: list[SymbolReference]
    file_index: dict[Path, list[Symbol]]
```

---

## 4. Process

### 4.1 Build Symbol Map

```python
def build_symbol_map(project_root: Path) -> SymbolMap:
    symbols = {}
    references = []
    file_index = defaultdict(list)

    for py_file in project_root.rglob("*.py"):
        tree = parser.parse(py_file.read_bytes())
        root = tree.root_node

        for node in root.children:
            if node.type == "function_definition":
                symbol = _extract_function(node, py_file)
                symbols[symbol.name] = symbol
                file_index[py_file].append(symbol)
            elif node.type == "class_definition":
                symbol = _extract_class(node, py_file)
                symbols[symbol.name] = symbol
                file_index[py_file].append(symbol)

        for node in _walk_tree(root):
            if node.type == "call":
                ref = _extract_call_reference(node, py_file, symbols)
                if ref:
                    references.append(ref)

    return SymbolMap(symbols, references, dict(file_index))
```

### 4.2 PageRank Ranking

```python
def pagerank(
    graph: dict[str, set[str]],
    damping: float = 0.85,
    iterations: int = 100
) -> dict[str, float]:
    nodes = list(graph.keys())
    n = len(nodes)
    if n == 0:
        return {}

    scores = {node: 1.0 / n for node in nodes}
    for _ in range(iterations):
        new_scores = {}
        for node in nodes:
            incoming = [src for src, targets in graph.items() if node in targets]
            rank_sum = sum(
                scores[src] / len(graph[src])
                for src in incoming if graph[src]
            )
            new_scores[node] = (1 - damping) / n + damping * rank_sum
        scores = new_scores
    return scores
```

**Why hand-rolled**: P5. No networkx dependency (5MB library for one algorithm).

### 4.3 Context Construction

```python
def rank_for_task(self, current_files: list[Path], token_budget: int) -> str:
    relevance_graph = self._build_relevance_graph(current_files)
    scores = pagerank(relevance_graph)
    ranked = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    context = self._format_context(ranked, token_budget)
    return context
```

---

## 5. Why Not Semantic Embeddings (A)

- **P3 violation**: Embedding model lock-in.
- **P5 violation**: Vector store before use case arrives. v1 needs structural queries.
- **Complexity**: ~800 lines vs ~200 lines for symbol map.
- **Speed**: ~14x slower than token chunking.

**Semantic search becomes valuable for**: "find all error handling patterns" -- v2+ use case.

---

## 6. Why Not Hybrid with Grep (C)

- **P5 violation**: Two systems.
- **Redundant**: Grep already covered by file_search skill (Plan 21.2).

---

## 7. Why Not File Tree (D)

- Token-inefficient. No structure. Insufficient for non-trivial codebases.

---

## 8. Dependencies

```
tree-sitter>=0.21
tree-sitter-python>=0.21
```

Python grammar for v1. Add grammars per language as needed.

**No networkx**: PageRank hand-rolled (~30 lines).

---

## 9. AR22 Traces

```python
# On map build
self._trace.emit(
    component="codebase_index",
    level=TraceLevel.INFO,
    event="codebase_index.built",
    file_count=len(file_index),
    symbol_count=len(symbols),
    duration_ms=elapsed_ms
)

# On rank query
self._trace.emit(
    component="codebase_index",
    level=TraceLevel.DEBUG,
    event="codebase_index.ranked",
    current_files=[str(f) for f in current_files],
    budget=token_budget,
    returned_symbols=len(ranked),
    duration_ms=elapsed_ms
)

# On rebuild
self._trace.emit(
    component="codebase_index",
    level=TraceLevel.INFO,
    event="codebase_index.rebuilt",
    changed_files=[str(f) for f in changed_paths],
    duration_ms=elapsed_ms
)
```

---

## 10. Cache Strategy

- **In-memory**: SymbolMap cached in memory.
- **Invalidation**: On file change via invalidate(paths).
- **Persistent cache**: Deferred per P5.
- **Rebuild trigger**: File watcher or explicit call from worker after file edit.

---

## 11. Rejected Alternatives

### 11.1 A -- Semantic Embeddings
- **Why rejected**: P3 violation; P5 violation.
- **Consequence**: ~800 lines, vector store dependency, 14x slower.

### 11.2 C -- Hybrid with Grep
- **Why rejected**: P5 violation. Grep already covered by file_search skill.

### 11.3 D -- File Tree
- **Why rejected**: Token-inefficient. No structure.

### 11.4 networkx Dependency
- **Why rejected**: P5 violation. 5MB library for one algorithm.

---

## 12. Rationale

| Principle | How B Honors It |
|-----------|----------------|
| P4 (local-first) | No cloud embeddings. Pure local computation. |
| P5 (no speculative contracts) | No embedding pipeline before use case arrives. |
| P3 (no provider lock-in) | No embedding model dependency. |
| P2 (pluggable) | Grammar packages per language. |
| P9 (observability) | Tree-sitter parsing emits trace events. |

---

## 13. Extension Points

| Extension | Trigger | Interface |
|-----------|---------|-----------|
| Semantic embeddings | v2+ use case arrives | SemanticIndex.query(text, top_k) alongside SymbolMap |
| Multi-language support | JS/TS/Rust codebases | Add grammar packages |
| Persistent cache | Large codebase | SQLite cache with mtime invalidation |
| Incremental updates | File watcher available | invalidate(paths) -> partial rebuild |

---

## 14. Open Questions

| ID | Question | Status |
|----|----------|--------|
| Q-21.10.1 | Should codebase index support incremental updates? | Deferred |
| Q-21.10.2 | When should semantic embeddings be added? | Deferred to v2+ |
| Q-21.10.3 | Should index include docstrings/comments? | Deferred |

---

## 15. Implementation Plan

**Plan 21.10** (Codebase Indexing -- parallel with 21.1-21.3):
- S1: Tree-sitter extractor for Python
- S2: SymbolMap data structures
- S3: Hand-rolled PageRank
- S4: rank_for_task() context construction
- S5: Cache invalidation
- S6: Tests

**No dependency on skill framework** -- this is a service, not a skill.

---

*End of document.*
