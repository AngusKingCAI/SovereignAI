Depends on: prompt-20.9.2
Vision principles: 2 (modular memory), 5 (pluggable backends)
Open questions resolved: none

## WILL edit
- `sovereignai/shared/types.py` — add memory query dataclasses
- `sovereignai/memory/episodic_backend.py` — typed queries
- `sovereignai/memory/procedural_backend.py` — typed queries
- `sovereignai/memory/working_backend.py` — typed queries
- `sovereignai/memory/trace_backend.py` — typed queries
- `sovereignai/librarian.py` — typed query dispatch
- `tests/test_memory*.py` — update for typed interfaces
- `DEBT.md` — mark resolved items
- `CHANGELOG.md` — append per OR73
- `PLANS.md` — update baseline
- `prompts/plan-20.9.3-Rev0.md` — move to completed/ at /close

## WILL NOT edit
- TUI panels (handled in 20.9.1), hardware probe (handled in 20.9.2). If scope expands, STOP.

## S0 — Opening

S0.1: Run `/open`. Read `AGENTS.md` in full.
S0.2: Read `DEBT.md`. Identify items this plan resolves.
S0.3: No new rules.
S0.4: Begin Phase 1.

## S1 — Define Typed Memory Queries

S1.1: Add to `sovereignai/shared/types.py`:
```python
@dataclass
class EpisodicQuery:
    session_id: str
    time_range: Optional[Tuple[datetime, datetime]] = None
    tags: Optional[List[str]] = None

@dataclass
class ProceduralQuery:
    skill_name: Optional[str] = None
    capability_type: Optional[str] = None

@dataclass
class WorkingQuery:
    context_id: str
    max_items: int = 10

@dataclass
class TraceQuery:
    correlation_id: Optional[str] = None
    span_type: Optional[str] = None
```

S1.2: Commit: `git add -A && git commit -m "feat: typed memory query dataclasses"`

## S2 — Refactor Memory Backends

S2.1: `episodic_backend.py` — replace `dict` params with `EpisodicQuery`
S2.2: `procedural_backend.py` — replace `dict` params with `ProceduralQuery`
S2.3: `working_backend.py` — replace `dict` params with `WorkingQuery`
S2.4: `trace_backend.py` — replace `dict` params with `TraceQuery`

S2.5: Commit: `git add -A && git commit -m "refactor: memory backends use typed queries per AR6"`

## S3 — Update Librarian

S3.1: `librarian.py` — update `query_memory()` to accept typed queries
S3.2: Add dispatch logic: query type → backend method

S3.3: Commit: `git add -A && git commit -m "refactor: Librarian typed query dispatch"`

## S4 — Update Tests

S4.1: Update all `test_memory*.py` to use typed query constructors
S4.2: Add type validation tests (reject plain dicts)
S4.3: Target ≥90% coverage on memory backends

S4.4: Commit: `git add -A && git commit -m "test: update memory tests for typed queries"`

## S5 — Update DEBT.md

S5.1: Mark resolved:
- AR6 violations - memory backend dict parameters → Resolved at prompt-20.9.3
- Memory abstraction implementation → Resolved at prompt-20.9.3
- Durable persistence backends and crash recovery → Resolved at prompt-20.9.3
- AR6 violations retirement decision → Resolved at prompt-20.9.3

S5.2: Commit: `git add -A && git commit -m "docs: mark memory DEBT items resolved"`

## S6 — /close

S6.1: Run `/close`.
