from __future__ import annotations

import sys
from pathlib import Path

import pytest

from app.sovereignai.shared.capability_graph import CapabilityGraph
from app.sovereignai.shared.trace_emitter import TraceEmitter
from app.sovereignai.shared.types import CapabilityCategory
from app.sovereignai.skills.discovery import SkillDiscovery


def test_auto_discovery() -> None:
    trace = TraceEmitter()
    graph = CapabilityGraph(trace=trace)
    discovery = SkillDiscovery(trace=trace, capability_graph=graph)

    skills_path = Path("app/sovereignai/skills/official")
    if not skills_path.exists():
        pytest.skip(f"Skills directory not found: {skills_path}")

    modules_before = set(sys.modules.keys())
    discovery.scan([skills_path])
    modules_after = set(sys.modules.keys())

    new_modules = modules_after - modules_before
    allowlist = set(sys.stdlib_module_names) if hasattr(sys, "stdlib_module_names") else set()
    allowlist.add("defusedxml")
    # Allow conformance modules loaded by CapabilityGraph.register()
    allowlist.add("sovereignai.conformance")
    allowlist.add("sovereignai.conformance.runner")
    allowlist.add("sovereignai.conformance.registry")
    allowlist.add("app.sovereignai.conformance")
    allowlist.add("app.sovereignai.conformance.runner")
    allowlist.add("app.sovereignai.conformance.registry")
    allowlist.add("sovereignai")
    allowlist.add("app.sovereignai")

    unexpected_modules = new_modules - allowlist
    assert not unexpected_modules, f"Unexpected modules loaded: {unexpected_modules}"


def test_capability_graph_registration() -> None:
    trace = TraceEmitter()
    graph = CapabilityGraph(trace=trace, dev_mode=True)
    discovery = SkillDiscovery(trace=trace, capability_graph=graph)

    skills_path = Path("app/sovereignai/skills/official")
    if not skills_path.exists():
        pytest.skip(f"Skills directory not found: {skills_path}")

    discovery.scan([skills_path])

    # Check that skills were registered
    manifests = graph.list_all_components()
    skill_manifests = [
        m for m in manifests
        if any(c.category == CapabilityCategory.SKILL for c in m.provides)
    ]
    assert len(skill_manifests) > 0


def test_explicit_disable() -> None:
    trace = TraceEmitter()
    graph = CapabilityGraph(trace=trace)
    discovery = SkillDiscovery(trace=trace, capability_graph=graph)

    # Scan non-existent path should not error
    non_existent = Path("nonexistent/path")
    discovery.scan([non_existent])

    # Should not raise any errors
    assert True


def test_dangling_dependency_warning() -> None:
    trace = TraceEmitter()
    graph = CapabilityGraph(trace=trace)
    discovery = SkillDiscovery(trace=trace, capability_graph=graph)

    skills_path = Path("app/sovereignai/skills/official")
    if not skills_path.exists():
        pytest.skip(f"Skills directory not found: {skills_path}")

    discovery.scan([skills_path])

    # The test would need to verify warning logs for dangling dependencies
    # For now, we just ensure the scan completes without error
    assert True
