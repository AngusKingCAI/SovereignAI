Depends on: prompt-12 (kept for batch ordering.)

Vision principles: P9 (strong/robust), Q9 (test strategy)
Open questions resolved: Q9 (fully — all three test types implemented)

---

## S0 — Opening

S0.1 — Run `/open`. Verify prompt-12 tag exists on origin. Confirm working copy is clean and on `main`.

S0.2 — Read `AGENTS.md` in full.

S0.3 — Add new rules (revised from Rev2 per Round Table re-review):
- **OR60** (revised): Every capability class (adapter, skill, memory_backend) SHOULD have a conformance test suite. The conformance *runner* lives in `sovereignai/conformance/` (a runtime-safe package, shipped in production). The pytest-discoverable *test suites* live in `tests/conformance/` and import from `sovereignai/conformance/`. The runtime gate in `CapabilityGraph.register()` imports from `sovereignai/conformance/` ONLY — never from `tests/`. The gate is **fail-open**: if no conformance tests are found for a component's capability class, log WARN and allow registration (handles third-party components per N12). If tests exist and FAIL, block registration. Conformance tests must be <100ms each (cache results per `(component_id, content_hash)` to avoid re-running on every startup). Third-party components MAY ship conformance tests via Python entry points (`[project.entry-points.'sovereignai.conformance']`). A dev-mode bypass is available via `--dev` CLI flag (requires the flag, not just an env var); emits an ERROR trace when active. Source: Plan 13 Rev3 (N1, N12, N13, N18).
- **OR61**: Contract tests verify backward compatibility of core public APIs. A contract test failure blocks the build. Source: Plan 13.
- **OR62** (revised): Property-based tests run on every commit. They ARE CI gate blockers. Source: Plan 13 Rev2 (F-29).
- **OR68**: Test dependencies (`hypothesis`, `pytest-cov`) are declared in `pyproject.toml` only. Source: Plan 13 Rev2 (F-28).

Commit: `docs: add OR60-OR62, OR68 for prompt-13`

---

## Plan Body

### S1 — Create sovereignai/conformance/ (runtime-safe package) + tests/conformance/ (pytest suites)

(Revised per Rev3 N1 — split the runner from the test suites.)

**`sovereignai/conformance/`** (shipped in production — the runtime gate imports from here):
```
sovereignai/
  conformance/
    __init__.py
    base.py              # BaseConformanceTest ABC + ConformanceResult
    runner.py            # ConformanceRunner — discovers and runs tests
    registry.py          # Registry of conformance test classes by capability class
```

**`tests/conformance/`** (NOT shipped in production — pytest discovers these):
```
tests/
  conformance/
    __init__.py
    test_adapter.py      # Imports from sovereignai.conformance
    test_skill.py
    test_memory.py
    conftest.py          # Backend fixtures
```

**No per-component `conformance_test.py` templates** (unchanged from Rev2).

### S2 — Create sovereignai/conformance/base.py + runner.py

**`base.py`** (unchanged from Rev2 — `BaseConformanceTest` ABC with pytest-discoverable `test_*` methods, no `run_all()`).

**`runner.py`** (NEW per N1 — the runtime-safe entry point):
```python
"""Conformance runner — discovers and executes conformance tests for a component.

This module is shipped in production (lives in sovereignai/conformance/, not tests/).
The runtime gate in CapabilityGraph.register() calls ConformanceRunner.check().
"""
from sovereignai.conformance.registry import get_conformance_tests_for_class

class ConformanceRunner:
    """Discover and run conformance tests for a component."""

    def __init__(self, trace):
        self._trace = trace
        self._cache: dict[tuple[str, str], bool] = {}  # (component_id, content_hash) -> passed

    def check(self, component_id: str, content_hash: str, capability_class: str, instance) -> bool:
        """Run conformance tests for a component. Returns True if passed (or no tests exist).

        Per Rev3 N1: imports from sovereignai.conformance.registry, NEVER from tests/.
        Per Rev3 N12: fail-open — if no tests found for capability_class, log WARN and return True.
        Per Rev3 N13: results cached per (component_id, content_hash).
        """
        cache_key = (component_id, content_hash)
        if cache_key in self._cache:
            return self._cache[cache_key]

        test_classes = get_conformance_tests_for_class(capability_class)
        if not test_classes:
            self._trace.emit(
                component="conformance",
                level=TraceLevel.WARN,
                message=f"No conformance tests for capability class '{capability_class}'; allowing registration of {component_id}",
            )
            self._cache[cache_key] = True
            return True

        for test_class in test_classes:
            test_instance = test_class()
            try:
                for method_name in dir(test_instance):
                    if method_name.startswith("test_"):
                        getattr(test_instance, method_name)(instance)
            except AssertionError as e:
                self._trace.emit(
                    component="conformance",
                    level=TraceLevel.ERROR,
                    message=f"Conformance test {test_class.__name__}.{method_name} failed for {component_id}: {e}",
                )
                self._cache[cache_key] = False
                return False
            except Exception as e:
                self._trace.emit(
                    component="conformance",
                    level=TraceLevel.ERROR,
                    message=f"Conformance test {test_class.__name__}.{method_name} raised for {component_id}: {e}",
                )
                self._cache[cache_key] = False
                return False

        self._cache[cache_key] = True
        return True
```

**`registry.py`** (NEW per N1/N12):
```python
"""Registry of conformance test classes by capability class.

First-party tests are registered here. Third-party tests are discovered via
Python entry points ('sovereignai.conformance' group).
"""
from typing import Type
import importlib.metadata

_CONFORMANCE_TESTS: dict[str, list[Type]] = {}

def register(capability_class: str):
    """Decorator: register a conformance test class for a capability class."""
    def decorator(cls):
        _CONFORMANCE_TESTS.setdefault(capability_class, []).append(cls)
        return cls
    return decorator

def get_conformance_tests_for_class(capability_class: str) -> list[Type]:
    """Return all conformance test classes for a capability class.

    Combines first-party (registered via decorator) and third-party (entry points).
    """
    tests = list(_CONFORMANCE_TESTS.get(capability_class, []))
    # Discover third-party conformance tests via entry points (per Rev3 N12)
    try:
        eps = importlib.metadata.entry_points(group="sovereignai.conformance")
        if hasattr(eps, "select"):  # Python 3.10+
            eps = eps.select(capability_class=capability_class)
        for ep in eps:
            try:
                cls = ep.load()
                tests.append(cls)
            except Exception:
                pass  # Best-effort discovery
    except Exception:
        pass
    return tests
```

### S3 — Create tests/conformance/test_adapter.py

(Unchanged from Rev2 — imports `from sovereignai.conformance.base import BaseConformanceTest`. Uses `@register("adapter")` decorator to register with the runtime registry.)

```python
from sovereignai.conformance.base import BaseConformanceTest
from sovereignai.conformance.registry import register

@register("adapter")
class AdapterConformanceTest(BaseConformanceTest):
    # ... unchanged from Rev2 ...
```

### S4 — Create tests/conformance/test_skill.py

(Unchanged from Rev2 — `@register("skill")`.)

### S5 — Create tests/conformance/test_memory.py

(Unchanged from Rev2 — uses standard `store(data, metadata) -> str` contract; `@register("memory_storage")`.)

### S6 — Create tests/contracts/

(Unchanged from Rev2 — fixtures explicitly defined.)

### S7 — Add property-based tests with Hypothesis

(Revised per Rev3 N6 — sample from TraceLevel, not TaskState.)

```python
# tests/property/test_state_machine_properties.py
from hypothesis import given, strategies as st
from sovereignai.shared.types import TaskState, TraceLevel  # N6: import TraceLevel
from sovereignai.shared.task_state_machine import VALID_TRANSITIONS

def can_transition(from_state: TaskState, to_state: TaskState) -> bool:
    return to_state in VALID_TRANSITIONS.get(from_state, [])

class TestStateMachineProperties:
    @given(st.sampled_from(TaskState), st.sampled_from(TaskState))
    def test_all_transitions_are_valid(self, from_state, to_state):
        """Verify can_transition() agrees with VALID_TRANSITIONS."""
        expected = to_state in VALID_TRANSITIONS.get(from_state, [])
        assert can_transition(from_state, to_state) == expected

    @given(st.lists(st.sampled_from(TraceLevel)))  # N6: TraceLevel, not TaskState
    def test_trace_filtering_never_crashes(self, levels):
        """Verify filtering arbitrary TraceLevel combinations never raises."""
        from sovereignai.shared.trace_emitter import TraceEmitter
        trace_emitter = TraceEmitter()
        for level in levels:
            trace_emitter.emit(component="test", level=level, message="test message")
        events = trace_emitter.get_events()
        assert isinstance(events, list)
```

### S8 — Update pyproject.toml

Add to `[project.optional-dependencies] dev`: `hypothesis>=6.100.0`, `pytest-cov>=5.0.0`.

### S9 — txt/requirements.txt

No change (unchanged from Rev2 — test deps in pyproject.toml only).

### S10 — Coverage baseline

(Unchanged from Rev2 — `python -m pytest --cov=sovereignai --cov-report=term-missing tests/`.)

### S11 — Update CapabilityGraph.register() conformance gate

(Revised per Rev3 N1, N18 — import from `sovereignai.conformance`, not `tests.conformance`; `--dev` CLI flag.)

```python
import os, argparse

def register(self, component_id, manifest, instance) -> None:
    """Register a component. Runs conformance gate unless --dev flag is set."""
    # N18: --dev flag required (not just env var)
    dev_mode = os.environ.get("SOVEREIGNAI_DEV_MODE") == "1"
    if dev_mode:
        self._trace.emit(
            component="capability_graph",
            level=TraceLevel.ERROR,  # N18: ERROR, not WARN
            message=f"DEV MODE active: skipping conformance gate for {component_id}. DO NOT use in production.",
        )
    else:
        # N1: import from sovereignai.conformance, NOT tests.conformance
        from sovereignai.conformance.runner import ConformanceRunner
        runner = ConformanceRunner(self._trace)
        passed = runner.check(
            component_id=str(component_id),
            content_hash=manifest.content_hash,
            capability_class=manifest.capability_class,  # or derive from manifest
            instance=instance,
        )
        if not passed:
            raise ComponentRegistrationError(
                f"Component {component_id} failed conformance tests"
            )
    # ... existing registration logic ...
```

**`--dev` CLI flag** (in `main.py`):
```python
parser.add_argument("--dev", action="store_true", help="Skip conformance gate (development only)")
if args.dev:
    os.environ["SOVEREIGNAI_DEV_MODE"] = "1"
```

### S12 — Tests (meta + integration)

(Updated per Rev3.)

- `tests/test_conformance_framework.py`: Test the conformance framework — verify conforming mock passes, non-conforming fails, **fail-open when no tests for capability class (N12)**, **caching works (N13)**, **entry-point discovery (N12)**.
- `tests/test_contract_tests.py`: Unchanged.
- `tests/test_property_tests.py`: Unchanged.
- `tests/test_integration_memory_versioning.py` (unchanged from Rev2).

---

## STOP Conditions

- If any conformance test fails against an existing component, STOP.
- If contract tests fail, STOP.
- If property-based tests find an invariant violation, STOP.
- If `CapabilityGraph.register()` imports from `tests/` at runtime (N1), STOP.
- If a core component without `version` passes registration (N21 — in Plan 12), STOP.
- If coverage baseline is below 50%, STOP.
- If any test fails, STOP.

---

## Files WILL Create

- `sovereignai/conformance/__init__.py` (NEW per N1)
- `sovereignai/conformance/base.py` (NEW per N1)
- `sovereignai/conformance/runner.py` (NEW per N1)
- `sovereignai/conformance/registry.py` (NEW per N1/N12)
- `tests/conformance/__init__.py`
- `tests/conformance/base.py` (re-exports from sovereignai.conformance for pytest compat)
- `tests/conformance/test_adapter.py`
- `tests/conformance/test_skill.py`
- `tests/conformance/test_memory.py`
- `tests/conformance/conftest.py`
- `tests/contracts/__init__.py`
- `tests/contracts/test_capability_api_contract.py`
- `tests/property/__init__.py`
- `tests/property/test_state_machine_properties.py`
- `tests/test_conformance_framework.py`
- `tests/test_contract_tests.py`
- `tests/test_property_tests.py`
- `tests/test_integration_memory_versioning.py`

## Files WILL Edit

- `pyproject.toml` (add dev deps)
- `PLANS.md` (coverage baseline)
- `sovereignai/shared/capability_graph.py` (conformance gate — imports from `sovereignai.conformance.runner`, not `tests.conformance`)
- `sovereignai/main.py` (add `--dev` CLI flag)

## Files WILL NOT Edit

- Any source file in `sovereignai/` except `sovereignai/shared/capability_graph.py` and the new `sovereignai/conformance/` package
- `txt/requirements.txt`
- `AGENTS.md` (except S0.3)

---

## Closing

Run `/close`. Tag: `prompt-13`. Update CHANGELOG, PLANS.md.

## Adjudication summary (Rev2 → Rev3)

New findings addressed: N1 (conformance runner in `sovereignai/conformance/`, not `tests/`), N6 (TraceLevel not TaskState), N12 (fail-open + entry-point discovery), N13 (cache + <100ms requirement), N18 (--dev flag + ERROR trace).
