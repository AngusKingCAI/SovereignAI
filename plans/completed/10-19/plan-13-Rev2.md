Depends on: prompt-12 (kept for batch ordering — Plan 13's conformance tests test components registered via the CapabilityGraph, which Plan 12's negotiator may disable. The actual code dependency is on Plan 2's capability graph and Plan 4's CapabilityAPI, both already complete.)

Vision principles: P9 (strong/robust), Q9 (test strategy)
Open questions resolved: Q9 (fully — all three test types implemented)

---

## S0 — Opening

S0.1 — Run `/open`. Verify prompt-12 tag exists on origin. Confirm working copy is clean and on `main`.

S0.2 — Read `AGENTS.md` in full.

S0.3 — Add new rules (revised from Rev1 per Round Table adjudication):
- **OR60**: Every capability class (adapter, skill, memory_backend) MUST have a conformance test suite in `tests/conformance/`. This is the single source of truth — there is no per-component `conformance_test.py` template (Rev1's dual-location approach was rejected per F-26 as a maintenance tax). New components without passing conformance tests cannot be registered in the CapabilityGraph. A dev-mode bypass is available: setting environment variable `SOVEREIGNAI_DEV_MODE=1` skips the conformance gate, logs a WARN trace, and allows registration. This is for the developer's inner loop only — production builds must have `SOVEREIGNAI_DEV_MODE` unset. Source: Plan 13 Rev2 (F-13, F-26).
- **OR61**: Contract tests verify backward compatibility of core public APIs. A contract test failure blocks the build. Source: Plan 13.
- **OR62** (revised): Property-based tests run on every commit (not nightly — Rev1's "nightly" schedule was rejected per F-29 as premature infrastructure with no scheduler). They ARE CI gate blockers. Hypothesis' shrinking keeps them fast (<10s for the current test surface). If a property test finds an invariant violation, STOP. Source: Plan 13 Rev2 (F-29).
- **OR68**: Test dependencies (`hypothesis`, `pytest-cov`) are declared in `pyproject.toml` only — NOT duplicated in `txt/requirements.txt`. The `txt/requirements.txt` file is for runtime dependencies only. Source: Plan 13 Rev2 (F-28).

Commit: `docs: add OR60-OR62, OR68 for prompt-13`

---

## Plan Body

### S1 — Create tests/conformance/ directory structure

```
tests/
  conformance/
    __init__.py
    base.py              # BaseConformanceTest ABC
    test_adapter.py      # Adapter conformance suite (pytest-parametrized)
    test_skill.py        # Skill conformance suite
    test_memory.py       # Memory backend conformance suite (parametrized over backends)
```

**No per-component `conformance_test.py` templates** (per Rev2 F-26 — central-only, single source of truth).

### S2 — Create tests/conformance/base.py

Base class for all conformance tests (per Rev2 F-14 — `run_all()` removed; test methods are regular pytest test methods):

```python
from abc import ABC, abstractmethod
from typing import Any
import pytest

class BaseConformanceTest(ABC):
    """Base class for capability conformance tests.

    Subclasses define pytest test methods (test_*) that take a component
    fixture. The fixture is provided by a parametrized factory in each
    subclass. There is no run_all() method — pytest discovers and runs
    the test_* methods directly.
    """

    @abstractmethod
    def test_required_methods(self, component: Any) -> None:
        """Verify the component implements all required methods for its capability class."""

    @abstractmethod
    def test_method_signatures(self, component: Any) -> None:
        """Verify method signatures match the contract."""

    @abstractmethod
    def test_error_handling(self, component: Any) -> None:
        """Verify the component degrades gracefully on failure."""
```

### S3 — Create tests/conformance/test_adapter.py

```python
import inspect
import pytest
from tests.conformance.base import BaseConformanceTest

class AdapterConformanceTest(BaseConformanceTest):
    """Conformance tests for all components declaring the 'adapter' capability class."""

    def test_required_methods(self, adapter):
        """Verify the adapter implements health_check() and at least one of generate()/chat()."""
        assert hasattr(adapter, 'health_check'), "Missing health_check()"
        assert hasattr(adapter, 'generate') or hasattr(adapter, 'chat'), "Missing generate() or chat()"

    def test_health_check_returns_bool(self, adapter):
        """Verify health_check() returns a boolean, not None or an exception."""
        result = adapter.health_check()
        assert isinstance(result, bool), f"health_check() returned {type(result).__name__}, expected bool"

    def test_error_handling(self, adapter):
        """Verify health_check() never raises — it returns False on failure."""
        try:
            result = adapter.health_check()
            assert isinstance(result, bool)
        except Exception as e:
            pytest.fail(f"health_check() raised {type(e).__name__}: {e} — should return False, not raise")

# Parametrize over all registered adapters (fixture defined in conftest.py)
# Third-party developers run: pytest tests/conformance/test_adapter.py --adapter=path.to.MyAdapter
```

### S4 — Create tests/conformance/test_skill.py

```python
import inspect
import pytest
from tests.conformance.base import BaseConformanceTest

class SkillConformanceTest(BaseConformanceTest):
    """Conformance tests for all components declaring the 'skill' capability class."""

    def test_required_methods(self, skill):
        """Verify the skill implements invoke()."""
        assert hasattr(skill, 'invoke'), "Missing invoke()"

    def test_invoke_signature(self, skill):
        """Verify invoke() accepts a 'payload' parameter."""
        sig = inspect.signature(skill.invoke)
        params = list(sig.parameters.keys())
        assert 'payload' in params, f"invoke() parameters are {params}; missing 'payload'"

    def test_error_handling(self, skill):
        """Verify invoke() with an invalid payload returns an error dict, not raises."""
        # Each skill fixture provides its own invalid payload via the 'invalid_payload' fixture
        # (see conftest.py). This test verifies the skill degrades gracefully.
        try:
            result = skill.invoke(skill.invalid_payload)
            assert isinstance(result, dict), "invoke() should return a dict even on error"
            assert 'error' in result or 'status' in result, "Error dict should contain 'error' or 'status'"
        except Exception as e:
            pytest.fail(f"invoke() raised {type(e).__name__}: {e} — should return error dict, not raise")
```

### S5 — Create tests/conformance/test_memory.py

Per Rev2 F-17, F-27 — the conformance test uses the actual memory backend contract (`store(data, metadata) -> str`, `query(query) -> list`, `delete(id) -> bool`), not a generic key-based interface. The test is parametrized over backend factories so it tests the contract, not one implementation.

```python
import pytest
from tests.conformance.base import BaseConformanceTest

class MemoryConformanceTest(BaseConformanceTest):
    """Conformance tests for all components declaring the 'memory_storage' capability."""

    def test_required_methods(self, backend):
        """Verify the backend implements store(), query(), and delete()."""
        assert hasattr(backend, 'store'), "Missing store()"
        assert hasattr(backend, 'query'), "Missing query()"
        assert hasattr(backend, 'delete'), "Missing delete()"

    def test_store_returns_id(self, backend):
        """Verify store() returns a string id (not a bool — Rev1's signature was wrong)."""
        record_id = backend.store({"test": "data"}, {"meta": "value"})
        assert isinstance(record_id, str), f"store() returned {type(record_id).__name__}, expected str (record id)"
        assert len(record_id) > 0, "store() returned empty id"
        # Cleanup
        backend.delete(record_id)

    def test_round_trip(self, backend):
        """Verify store → query → delete round-trip works with the backend's own query shape.

        Each backend fixture provides its own 'sample_query' (a query dict that will
        match the stored record). This test does NOT assume a generic key-based
        query interface — that was Rev1's bug (F-17).
        """
        record_id = backend.store({"test": "data"}, {"meta": "value"})
        results = backend.query(backend.sample_query)
        assert len(results) >= 1, f"query({backend.sample_query}) returned {len(results)} results, expected >=1"
        found = any(r.get("id") == record_id for r in results)
        assert found, f"Stored record {record_id} not found in query results"
        backend.delete(record_id)
        results = backend.query(backend.sample_query)
        assert not any(r.get("id") == record_id for r in results), "Record still present after delete"

    def test_error_handling(self, backend):
        """Verify delete(nonexistent_id) returns False, not raises."""
        result = backend.delete("nonexistent-id-12345")
        assert isinstance(result, bool), f"delete() returned {type(result).__name__}, expected bool"
        assert result is False, "delete(nonexistent) should return False"
```

**Backend fixtures** (in `tests/conformance/conftest.py`):
```python
import pytest
from sovereignai.memory.episodic_backend import EpisodicMemoryBackend
from sovereignai.memory.procedural_backend import ProceduralMemoryBackend
from sovereignai.memory.working_backend import WorkingMemoryBackend
from sovereignai.memory.trace_backend import TraceMemoryBackend

class _BackendFixture:
    """Wraps a backend instance with a sample_query matching its query interface."""
    def __init__(self, backend, sample_query, invalid_payload=None):
        self._backend = backend
        self.sample_query = sample_query
        self.invalid_payload = invalid_payload
    def __getattr__(self, name):
        return getattr(self._backend, name)

@pytest.fixture
def episodic_memory_fixture(tmp_path):
    """Provide an EpisodicMemoryBackend with a temp db and a matching sample_query."""
    backend = EpisodicMemoryBackend(db_path=str(tmp_path / "test_episodic.db"))
    record_id = backend.store({"test": "data"}, {"meta": "value"})
    sample_query = {"task_id": None, "event_type": None, "time_range": None}  # Match-all query
    return _BackendFixture(backend, sample_query)

# Similar fixtures for procedural, working, trace backends
```

### S6 — Create tests/contracts/ directory

Contract tests verify core API backward compatibility. Per Rev2 F-40 — fixtures are explicitly defined.

```python
# tests/contracts/test_capability_api_contract.py
import pytest
from uuid import uuid4
from sovereignai.shared.capability_api import CapabilityAPI
from sovereignai.shared.container import DIContainer
from sovereignai.shared.trace_emitter import TraceEmitter

@pytest.fixture
def capability_api():
    """Provide a CapabilityAPI instance with a minimal DI container."""
    container = DIContainer()
    trace = TraceEmitter()
    container.register_singleton(TraceEmitter, trace)
    # ... register minimal dependencies ...
    api = CapabilityAPI(
        capability_index=container.retrieve(ICapabilityIndex),
        task_state_query=container.retrieve(ITaskStateQuery),
        state_machine=container.retrieve(TaskStateMachine),
        trace=trace,
    )
    return api

@pytest.fixture
def token():
    """Provide a valid session token for the test."""
    return "test-session-token"

@pytest.fixture
def category():
    return "skill"

@pytest.fixture
def name():
    return "test_capability"

@pytest.fixture
def payload():
    return {"input": "test"}

class TestCapabilityAPIContract:
    def test_query_capabilities_returns_list(self, capability_api, token):
        """Verify query_capabilities() returns a list of capability descriptors."""
        result = capability_api.query_capabilities(token)
        assert isinstance(result, list)

    def test_submit_task_returns_task(self, capability_api, token, category, name, payload):
        """Verify submit_task() returns a task object with task_id and state."""
        task = capability_api.submit_task(token, category, name, payload)
        assert hasattr(task, 'task_id'), "submit_task() result missing 'task_id'"
        assert hasattr(task, 'state'), "submit_task() result missing 'state'"

    def test_get_task_state_returns_task(self, capability_api, token):
        """Verify get_task_state() returns a task object with a state field."""
        # First submit a task to get a valid task_id
        task = capability_api.submit_task(token, "skill", "test_capability", {"input": "test"})
        result = capability_api.get_task_state(token, task.task_id)
        assert hasattr(result, 'state'), "get_task_state() result missing 'state'"
```

### S7 — Add property-based tests with Hypothesis

Per Rev2 F-40 — undefined functions defined explicitly.

```python
# tests/property/test_state_machine_properties.py
from hypothesis import given, strategies as st
from sovereignai.shared.types import TaskState
from sovereignai.shared.task_state_machine import TaskStateMachine, VALID_TRANSITIONS

def can_transition(from_state: TaskState, to_state: TaskState) -> bool:
    """Check whether a transition from from_state to to_state is valid per the state machine."""
    return to_state in VALID_TRANSITIONS.get(from_state, [])

class TestStateMachineProperties:
    @given(st.sampled_from(TaskState), st.sampled_from(TaskState))
    def test_all_transitions_are_valid(self, from_state, to_state):
        """Verify that can_transition() agrees with VALID_TRANSITIONS for all state pairs."""
        expected = to_state in VALID_TRANSITIONS.get(from_state, [])
        assert can_transition(from_state, to_state) == expected

    @given(st.lists(st.sampled_from(TaskState)))
    def test_trace_filtering_never_crashes(self, levels):
        """Verify that filtering arbitrary level combinations never raises."""
        from sovereignai.shared.trace_emitter import TraceEmitter
        trace_emitter = TraceEmitter()
        for level in levels:
            trace_emitter.emit(component="test", level=level, message="test message")
        events = trace_emitter.get_events()
        assert isinstance(events, list)
```

### S8 — Update pyproject.toml for test dependencies

Add to `[project.optional-dependencies] dev`:
```
hypothesis>=6.100.0
pytest-cov>=5.0.0
```

### S9 — txt/requirements.txt

**No change.** Per Rev2 OR68 — test dependencies live in `pyproject.toml` only. The `txt/requirements.txt` file is for runtime dependencies only and must not duplicate test deps. (Rev1's S9 append is removed.)

### S10 — Establish coverage baseline

Per Rev2 F-31 — use `python -m pytest`, not the hardcoded `.venv/Scripts/pytest.exe` path.

Run:
```bash
python -m pytest --cov=sovereignai --cov-report=term-missing tests/
```

Record baseline in PLANS.md:
```
Coverage Baseline (Plan 13): XX%
Target: 90% by Plan 15
```

### S11 — Tests (meta + integration)

Per Rev2 F-49 — add one cross-plan integration test.

- `tests/test_conformance_framework.py`: Test the conformance framework itself — verify that a known-conforming mock component passes, and a known-non-conforming mock component fails.
- `tests/test_contract_tests.py`: Test contract test framework — verify the capability_api fixture works.
- `tests/test_property_tests.py`: Test property-based test framework — verify Hypothesis is installed and runs.
- `tests/test_integration_memory_versioning.py` (new, per F-49): Register a memory backend (episodic), run the version negotiator, confirm the backend is NOT disabled and is queryable via the Librarian. This tests the seam between Plan 11 (memory) and Plan 12 (versioning).

---

## STOP Conditions

- If any conformance test fails against an existing component (Ollama adapter, WebSearch skill, episodic memory backend), STOP — the component is non-conforming. Fix the component, not the test.
- If contract tests fail against existing core APIs, STOP — backward compatibility broken.
- If property-based tests find an invariant violation, STOP — document as new issue in LANDMINES.md.
- If coverage baseline is below 50%, STOP — insufficient test coverage. (50% is a safety net, not a target. The current baseline is 96%; this floor catches catastrophic drops.)

---

## Files WILL Create

- `tests/conformance/__init__.py`
- `tests/conformance/base.py`
- `tests/conformance/test_adapter.py`
- `tests/conformance/test_skill.py`
- `tests/conformance/test_memory.py`
- `tests/conformance/conftest.py` (backend fixtures — new per Rev2 F-27)
- `tests/contracts/__init__.py`
- `tests/contracts/test_capability_api_contract.py`
- `tests/property/__init__.py`
- `tests/property/test_state_machine_properties.py`
- `tests/test_conformance_framework.py`
- `tests/test_contract_tests.py`
- `tests/test_property_tests.py`
- `tests/test_integration_memory_versioning.py` (new per Rev2 F-49)

## Files WILL Edit

- `pyproject.toml` (add dev deps)
- `PLANS.md` (add coverage baseline)
- `sovereignai/shared/capability_graph.py` (add conformance gate to `register()` — see below)

**Conformance gate** (per Rev2 F-13): Add to `CapabilityGraph.register()`:
```python
import os
def register(self, component_id: ComponentId, manifest: Manifest, instance: Any) -> None:
    """Register a component. In production, requires passing conformance tests. In dev mode, skips with WARN."""
    if os.environ.get("SOVEREIGNAI_DEV_MODE") == "1":
        self._trace.emit(component="capability_graph", level=TraceLevel.WARN,
                         message=f"DEV MODE: skipping conformance gate for {component_id}")
    else:
        self._run_conformance_check(component_id, manifest, instance)
    # ... existing registration logic ...
```

This is an edit to `sovereignai/shared/capability_graph.py` (core). Per P1, this requires justification: OR60 (conformance required for registration) is unenforceable without a gate in `register()`. The dev-mode bypass addresses the chicken-and-egg concern (F-13). The `_run_conformance_check` method imports `tests.conformance` lazily (inside the method, not at module level) to avoid a circular dependency.

## Files WILL NOT Edit

- Any source file in `sovereignai/` except `sovereignai/shared/capability_graph.py` (core, justified above)
- `txt/requirements.txt` (per Rev2 OR68 — no test deps here)
- `AGENTS.md` (except S0.3)

---

## Closing

Run `/close`. Tag: `prompt-13`. Update CHANGELOG, PLANS.md.

## Adjudication summary (Rev1 → Rev2)

Findings addressed: F-13 (conformance gate in `register()` + dev-mode bypass), F-14 (`run_all()` removed; pytest-discoverable test methods), F-17 (conformance test uses actual backend contract, not generic key-based interface), F-26 (central-only, no per-component templates), F-27 (parametrized over backend factories, not coupled to one implementation), F-28 (test deps in pyproject.toml only), F-29 (property tests run on every commit, not nightly), F-31 (`python -m pytest`, not hardcoded path), F-40 (fixtures explicitly defined), F-49 (one cross-plan integration test added).

Findings rejected: F-48 (50% coverage floor is a safety net, not a target — current baseline is 96%), F-52 (STOP thresholds are calibrated).
