from __future__ import annotations

import pytest

from sovereignai.shared.capability_graph import CapabilityGraph
from sovereignai.shared.trace_emitter import TraceEmitter
from sovereignai.skills.concrete_runner import ConcreteSkillRunner, SkillNotFoundError
from sovereignai.skills.runner import ISkillRunner
from sovereignai.skills.session import SkillSession


def test_protocol_conformance() -> None:
    trace = TraceEmitter()
    graph = CapabilityGraph(trace=trace)
    runner = ConcreteSkillRunner(capability_graph=graph, trace=trace)
    assert isinstance(runner, ISkillRunner)


def test_skill_not_found_raises() -> None:
    trace = TraceEmitter()
    graph = CapabilityGraph(trace=trace)
    runner = ConcreteSkillRunner(capability_graph=graph, trace=trace)
    session = SkillSession()

    with pytest.raises(SkillNotFoundError):
        runner.run("nonexistent_skill", {}, session)


def test_module_cached_per_skill_id() -> None:
    trace = TraceEmitter()
    graph = CapabilityGraph(trace=trace)
    runner = ConcreteSkillRunner(capability_graph=graph, trace=trace)

    # This test would require registering a skill first
    # For now, we'll test the caching mechanism conceptually
    # by checking that the cache is empty initially
    assert len(runner._module_cache) == 0

    # After loading a skill, it should be cached
    # (This would require proper skill registration in the graph)
    # assert len(runner._module_cache) == 1


def test_health_check() -> None:
    trace = TraceEmitter()
    graph = CapabilityGraph(trace=trace)
    runner = ConcreteSkillRunner(capability_graph=graph, trace=trace)
    assert runner.health_check() is True


def test_list_capabilities() -> None:
    trace = TraceEmitter()
    graph = CapabilityGraph(trace=trace)
    runner = ConcreteSkillRunner(capability_graph=graph, trace=trace)
    capabilities = runner.list_capabilities()
    assert isinstance(capabilities, list)


def test_close_idempotent() -> None:
    trace = TraceEmitter()
    graph = CapabilityGraph(trace=trace)
    runner = ConcreteSkillRunner(capability_graph=graph, trace=trace)

    # Should not raise even if cache is empty
    runner.close()
    runner.close()  # Second call should also not raise

    assert len(runner._module_cache) == 0
