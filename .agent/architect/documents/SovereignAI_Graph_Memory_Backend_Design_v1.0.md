# SovereignAI -- Graph Memory Backend Design Document v1.0

**Status**: Draft -- approved for implementation  
**Date**: 2026-07-03  
**Author**: Architect  
**Depends on**: `../PRINCIPLES.md`, `../AGENTS.md`, `../DECISIONS.md`, `../AI_HANDOFF.md`, `SovereignAI_Skill_Agent_System_Design_v1.0.md`, `SovereignAI_Cross_Department_Messaging_Design_v1.0.md`

---

## 1. Context

**Gap**: #12 -- Graph Memory Backend  
**Problem**: The Library Department spec describes a graph-based neural map for entity-anchored memory traversal. The existing memory backends (episodic, procedural, working, trace) are SQLite-based. A graph backend is needed for semantic memory (entities, relationships, multi-hop queries).  
**Scope**: How to implement graph memory that composes with existing SQLite infrastructure and the Librarian query router.

---

## 2. Design Decision

**DD-21.12.1**: Graph memory backend (Proposed, P4/P5/AR6/AR19-aligned): SQLite with adjacency tables. Schema: entities (id, type, created_at), entity_attributes (entity_id, name, value_text/value_int/value_real, value_type), relations (source, target, relation_type, created_at). Recursive CTE with cycle detection (path tracking) for traversal. Typed GraphQuery/GraphResult dataclasses conforming to AR19 pluggable backend interface. Hand-roll graph algorithms per-need (~30 lines each), no networkx dependency for v1.

---

## 3. Schema

```sql
CREATE TABLE entities (
    id TEXT PRIMARY KEY,
    type TEXT NOT NULL,
    created_at TEXT NOT NULL  -- ISO 8601 UTC per OR7
);

CREATE TABLE entity_attributes (
    entity_id TEXT NOT NULL,
    name TEXT NOT NULL,
    value_text TEXT,
    value_int INTEGER,
    value_real REAL,
    value_type TEXT NOT NULL CHECK(value_type IN ('text', 'int', 'real', 'bool', 'null')),
    PRIMARY KEY (entity_id, name),
    FOREIGN KEY (entity_id) REFERENCES entities(id) ON DELETE CASCADE
);

CREATE TABLE relations (
    source TEXT NOT NULL,
    target TEXT NOT NULL,
    relation_type TEXT NOT NULL,
    created_at TEXT NOT NULL,
    PRIMARY KEY (source, target, relation_type),
    FOREIGN KEY (source) REFERENCES entities(id) ON DELETE CASCADE,
    FOREIGN KEY (target) REFERENCES entities(id) ON DELETE CASCADE
);

CREATE INDEX idx_relations_source ON relations(source);
CREATE INDEX idx_relations_target ON relations(target);
CREATE INDEX idx_entities_type ON entities(type);
```

**Why EAV (entity-attribute-value) instead of JSON blob**: AR6 compliance. JSON blob in TEXT column = dict[str, Any] at storage layer. Querying "all entities with attribute X = Y" requires Python-side JSON parsing. EAV is typed, indexable, queryable in SQL.

---

## 4. Query Interface

```python
@dataclass(frozen=True)
class GraphQuery:
    entity_id: UUID | None         # starting entity (None = all)
    relation_types: list[str]      # filter by relation type
    depth: int = 2                 # traversal depth
    attribute_filters: dict[str, object] = field(default_factory=dict)

@dataclass(frozen=True)
class GraphResult:
    entities: list[Entity]
    relations: list[Relation]

@dataclass(frozen=True)
class Entity:
    id: UUID
    type: str
    attributes: dict[str, object]

@dataclass(frozen=True)
class Relation:
    source: UUID
    target: UUID
    relation_type: str
```

**Librarian dispatch** (per AR19 pluggable backend):
```python
def query_memory(self, query):
    match query:
        case EpisodicQuery(): return self._episodic_backend.query(query)
        case ProceduralQuery(): return self._procedural_backend.query(query)
        case WorkingQuery(): return self._working_backend.query(query)
        case TraceQuery(): return self._trace_backend.query(query)
        case GraphQuery(): return self._graph_backend.query(query)
```

---

## 5. Traversal Query (Recursive CTE with Cycle Detection)

```sql
WITH RECURSIVE traversal(id, depth, path) AS (
    SELECT ?, 0, ?
    UNION ALL
    SELECT r.target, t.depth + 1, t.path || ',' || r.target
    FROM relations r
    JOIN traversal t ON r.source = t.id
    WHERE t.depth < ?
      AND ',' || t.path || ',' NOT LIKE '%,' || r.target || ',%'
)
SELECT DISTINCT e.* FROM entities e
JOIN traversal t ON e.id = t.id;
```

**Cycle detection**: `path` column tracks visited nodes as comma-separated string. `NOT LIKE` skips already-visited nodes. Standard SQL recursive-CTE pattern.

**Performance**: O(n²) in string operations for large graphs. Acceptable for v1 (thousands of entities). Promote to D (NetworkX cache) when bottlenecked.

---

## 6. Why Not Other Options

### 6.1 A -- NetworkX (In-Memory Only)
- **Why rejected**: Violates persistence requirement. Graph memory must survive process restart -- that's the whole point of the Library Department per the design doc.
- **Consequence**: Data loss on restart. Not a memory backend.

### 6.2 C -- Kuzu (Embedded Graph DB)
- **Why rejected**: "Being archived, risk of abandonment" per research. Adding a soon-to-be-archived dependency to a local-first system is the opposite of P4's durability intent.
- **Consequence**: Dependency abandoned. Forced migration later.

### 6.3 D -- Hybrid (SQLite + NetworkX Cache)
- **Why rejected**: P5 violation. Two systems to maintain. Cache invalidation complexity. Memory duplication.
- **Consequence**: Unnecessary complexity for v1. Promote to D when graph algorithms are actually needed.

---

## 7. Graph Algorithms (Hand-Rolled)

**P5 discipline**: Same as DD-21.10.1 (codebase indexing). Hand-roll per algorithm. No networkx dependency until 3+ algorithms needed AND each is non-trivial.

```python
# BFS/DFS: recursive CTE handles this (see Section 5)

# PageRank (if needed later, ~30 lines):
def pagerank(adjacency: dict[str, set[str]], damping: float = 0.85, iterations: int = 100) -> dict[str, float]:
    nodes = list(adjacency.keys())
    n = len(nodes)
    scores = {node: 1.0 / n for node in nodes}
    for _ in range(iterations):
        new_scores = {}
        for node in nodes:
            incoming = [src for src, targets in adjacency.items() if node in targets]
            rank_sum = sum(scores[src] / len(adjacency[src]) for src in incoming if adjacency[src])
            new_scores[node] = (1 - damping) / n + damping * rank_sum
        scores = new_scores
    return scores
```

---

## 8. Rationale

| Principle | How B Honors It |
|-----------|----------------|
| P4 (local-first) | SQLite is already a dependency. No new server process. |
| P5 (no speculative contracts) | No new dependencies. Schema is 3 tables + 1 CTE. |
| P3 (no provider lock-in) | SQLite is universal. Standard SQL. |
| AR6 (no context bags) | EAV schema is typed. No JSON blobs. |
| AR19 (pluggable backends) | GraphQuery conforms to typed query interface. |
| AR21 (atomic writes) | WAL + transactions. Same discipline as other backends. |

---

## 9. Extension Points

| Extension | Trigger | Interface |
|-----------|---------|-----------|
| NetworkX cache | Graph algorithms needed (PageRank, centrality) | Load subgraph into nx.DiGraph for analysis |
| Kuzu migration | Kuzu successor stabilizes | Export SQLite, import Kuzu |
| Vector search | Semantic similarity on entities | Add embedding column to entities table |
| Temporal queries | Time-travel ("what did user believe on date X?") | Add valid_from/valid_to to relations |

---

## 10. Open Questions

| ID | Question | Status |
|----|----------|--------|
| Q-21.12.1 | Should graph memory support temporal validity (valid_from/valid_to)? | Deferred |
| Q-21.12.2 | Should entities support vector embeddings for semantic similarity? | Deferred to v2+ |
| Q-21.12.3 | Should graph memory support bulk import/export (Turtle, RDF)? | Deferred |

---

## 11. Implementation Plan

**Plan 21.12** (Graph Memory Backend):
- S1: Schema creation (entities, entity_attributes, relations)
- S2: GraphBackend class with CRUD operations
- S3: Recursive CTE traversal with cycle detection
- S4: GraphQuery/GraphResult typed interface
- S5: Librarian integration (match case dispatch)
- S6: Tests for traversal, cycle detection, attribute filtering

**Depends on**: Plan 20.10.1 (Typed Event Foundation) for Librarian event subscription

---

*End of document.*
