Depends on: prompt-12
Vision principles: P9 (strong/robust), Q9 (test strategy)
Open questions resolved: Q9 (fully — all three test types implemented)

---

## S0 — Opening

S0.1 — Run `/open`. Verify prompt-12 tag exists on origin. Confirm working copy is clean and on `main`.

S0.2 — Read `AGENTS.md` in full.

S0.3 — Add new rules:
- **OR60**: Every capability class (adapter, skill, memory_backend) MUST have a conformance test suite in `tests/conformance/`. New components without conformance tests cannot be registered in the CapabilityGraph. Source: Plan 13.
- **OR61**: Contract tests verify backward compatibility of core public APIs. A contract test failure blocks the build. Source: Plan 13.
- **OR62**: Property-based tests run on schedule (nightly), not on every commit. They are not CI gate blockers. Source: Plan 13.

Commit: `docs: add OR60-OR62 for prompt-13`

---

## Plan Body

### S1 — Create tests/conformance/ directory structure

```
tests/
  conformance/
    __init__.py
    base.py              # BaseConformanceTest class
    test_adapter.py      # Adapter conformance suite
    test_skill.py        # Skill conformance suite
    test_memory.py       # Memory backend conformance suite
```

### S2 — Create tests/conformance/base.py

Base class for all conformance tests:

```python
class BaseConformanceTest(ABC):
    """Base class for capability conformance tests.

    Subclasses implement test methods for a specific capability class.
    All test methods raise ConformanceError on failure.
    """

    @abstractmethod
    def test_required_methods(self, component: Any) -> None:
        """Verify component implements all required methods."""

    @abstractmethod
    def test_method_signatures(self, component: Any) -> None:
        """Verify method signatures match the contract."""

    @abstractmethod
    def test_error_handling(self, component: Any) -> None:
        """Verify graceful degradation on failure."""

    def run_all(self, component: Any) -> ConformanceResult:
        """Run all conformance tests against a component."""
```

### S3 — Create tests/conformance/test_adapter.py

Adapter conformance suite:

```python
class AdapterConformanceTest(BaseConformanceTest):
    def test_required_methods(self, adapter):
        assert hasattr(adapter, 'health_check'), "Missing health_check()"
        assert hasattr(adapter, 'generate') or hasattr(adapter, 'chat'), "Missing generate() or chat()"

    def test_health_check_returns_bool(self, adapter):
        result = adapter.health_check()
        assert isinstance(result, bool), f"health_check() returned {type(result)}, expected bool"

    def test_error_handling(self, adapter):
        # Adapter must not raise on health_check failure
        try:
            adapter.health_check()
        except Exception:
            assert False, "health_check() raised exception — should return False"
```

### S4 — Create tests/conformance/test_skill.py

Skill conformance suite:

```python
class SkillConformanceTest(BaseConformanceTest):
    def test_required_methods(self, skill):
        assert hasattr(skill, 'invoke'), "Missing invoke()"

    def test_invoke_signature(self, skill):
        import inspect
        sig = inspect.signature(skill.invoke)
        params = list(sig.parameters.keys())
        assert 'payload' in params, "invoke() missing 'payload' parameter"

    def test_manifest_matches_code(self, skill, manifest):
        # Verify manifest capabilities match implemented methods
        pass
```

### S5 — Create tests/conformance/test_memory.py

Memory backend conformance suite:

```python
class MemoryConformanceTest(BaseConformanceTest):
    def test_required_methods(self, backend):
        assert hasattr(backend, 'store'), "Missing store()"
        assert hasattr(backend, 'query'), "Missing query()"
        assert hasattr(backend, 'delete'), "Missing delete()"

    def test_round_trip(self, backend):
        backend.store("test_key", {"data": "value"}, {})
        results = backend.query({"key": "test_key"})
        assert len(results) == 1
        assert results[0]["data"] == "value"
        backend.delete("test_key")
        results = backend.query({"key": "test_key"})
        assert len(results) == 0
```

### S6 — Create tests/contracts/ directory

Contract tests verify core API backward compatibility:

```python
# tests/contracts/test_capability_api_contract.py
class TestCapabilityAPIContract:
    def test_query_capabilities_returns_list(self, capability_api):
        result = capability_api.query_capabilities(token)
        assert isinstance(result, list)

    def test_submit_task_returns_task(self, capability_api):
        task = capability_api.submit_task(token, category, name, payload)
        assert hasattr(task, 'task_id')
        assert hasattr(task, 'state')

    def test_get_task_state_returns_task(self, capability_api):
        task = capability_api.get_task_state(token, task_id)
        assert hasattr(task, 'state')
```

### S7 — Add property-based tests with Hypothesis

```python
# tests/property/test_state_machine_properties.py
from hypothesis import given, strategies as st

class TestStateMachineProperties:
    @given(st.sampled_from(TaskState), st.sampled_from(TaskState))
    def test_all_transitions_are_valid(self, from_state, to_state):
        # Verify no invalid state transitions exist
        if from_state == TaskState.COMPLETE:
            assert not can_transition(from_state, to_state)

    @given(st.lists(st.sampled_from(TraceLevel)))
    def test_trace_filtering_never_crashes(self, levels):
        # Verify filtering arbitrary level combinations never raises
        trace_emitter = TraceEmitter()
        for level in levels:
            trace_emitter.emit(level, "test", "message")
        events = trace_emitter.get_events()
        assert isinstance(events, list)
```

### S8 — Update pyproject.toml for test dependencies

Add to `[project.optional-dependencies] dev`:
```
hypothesis>=6.100.0
pytest-cov>=5.0.0
```

### S9 — Update txt/requirements.txt

Append:
```
hypothesis>=6.100.0
pytest-cov>=5.0.0
```

### S10 — Establish coverage baseline

Run:
```bash
.venv/Scripts/pytest.exe --cov=sovereignai --cov-report=term-missing tests/
```

Record baseline in PLANS.md:
```
Coverage Baseline (Plan 13): XX%
Target: 90% by Plan 15
```

### S11 — Tests

- `tests/test_conformance_framework.py`: Test the conformance framework itself.
- `tests/test_contract_tests.py`: Test contract test framework.
- `tests/test_property_tests.py`: Test property-based test framework.

---

## STOP Conditions

- If any conformance test fails against an existing component (Ollama adapter, WebSearch skill), STOP — the component is non-conforming.
- If contract tests fail against existing core APIs, STOP — backward compatibility broken.
- If property-based tests find an invariant violation, STOP — document as new issue.
- If coverage baseline is below 50%, STOP — insufficient test coverage.

---

## Files WILL Create

- `tests/conformance/__init__.py`
- `tests/conformance/base.py`
- `tests/conformance/test_adapter.py`
- `tests/conformance/test_skill.py`
- `tests/conformance/test_memory.py`
- `tests/contracts/__init__.py`
- `tests/contracts/test_capability_api_contract.py`
- `tests/property/__init__.py`
- `tests/property/test_state_machine_properties.py`
- `tests/test_conformance_framework.py`
- `tests/test_contract_tests.py`
- `tests/test_property_tests.py`

## Files WILL Edit

- `pyproject.toml` (add dev deps)
- `txt/requirements.txt` (append dev deps)
- `PLANS.md` (add coverage baseline)

## Files WILL NOT Edit

- Any source file in `sovereignai/`
- `AGENTS.md` (except S0.3)

---

## Closing

Run `/close`. Tag: `prompt-13`. Update CHANGELOG, PLANS.md.
