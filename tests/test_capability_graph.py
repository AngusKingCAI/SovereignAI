"""Tests for capability graph."""
from __future__ import annotations

from sovereignai.shared.capability_graph import CapabilityGraph, ICapabilityIndex
from sovereignai.shared.trace_emitter import TraceEmitter
from sovereignai.shared.types import (
    CapabilityCategory,
    CapabilityDeclaration,
    ComponentId,
    ComponentManifest,
)


def test_register_single_component_findable() -> None:
    """Register a manifest with one capability and verify find_providers returns it."""
    trace = TraceEmitter()
    graph = CapabilityGraph(trace=trace)
    manifest = ComponentManifest(
        component_id=ComponentId("TestAdapter"),
        version="1.0.0",
        author="test-author",
        content_hash="sha256:abc123",
        provides=(
            CapabilityDeclaration(
                category=CapabilityCategory.MODEL_INFERENCE,
                name="text_generation",
                version="1.0.0",
                priority=10,
            ),
        ),
        requires=(),
    )
    graph.register(manifest)
    providers = graph.find_providers(CapabilityCategory.MODEL_INFERENCE, "text_generation")
    assert len(providers) == 1
    assert providers[0][0] == ComponentId("TestAdapter")
    assert providers[0][1].name == "text_generation"


def test_register_multiple_providers_sorted_by_priority() -> None:
    """Register two providers for the same capability; higher priority returned first."""
    trace = TraceEmitter()
    graph = CapabilityGraph(trace=trace)
    manifest1 = ComponentManifest(
        component_id=ComponentId("LowPriorityAdapter"),
        version="1.0.0",
        author="test-author",
        content_hash="sha256:abc123",
        provides=(
            CapabilityDeclaration(
                category=CapabilityCategory.MODEL_INFERENCE,
                name="text_generation",
                version="1.0.0",
                priority=5,
            ),
        ),
        requires=(),
    )
    manifest2 = ComponentManifest(
        component_id=ComponentId("HighPriorityAdapter"),
        version="1.0.0",
        author="test-author",
        content_hash="sha256:def456",
        provides=(
            CapabilityDeclaration(
                category=CapabilityCategory.MODEL_INFERENCE,
                name="text_generation",
                version="1.0.0",
                priority=10,
            ),
        ),
        requires=(),
    )
    graph.register(manifest1)
    graph.register(manifest2)
    providers = graph.find_providers(CapabilityCategory.MODEL_INFERENCE, "text_generation")
    assert len(providers) == 2
    assert providers[0][0] == ComponentId("HighPriorityAdapter")
    assert providers[0][1].priority == 10
    assert providers[1][0] == ComponentId("LowPriorityAdapter")
    assert providers[1][1].priority == 5


def test_find_providers_empty_when_no_match() -> None:
    """Query for a capability that is not registered; returns empty tuple."""
    trace = TraceEmitter()
    graph = CapabilityGraph(trace=trace)
    providers = graph.find_providers(CapabilityCategory.TOOL, "websearch")
    assert providers == ()


def test_list_all_components_returns_all_manifests() -> None:
    """Register three components and verify list_all_components returns all three."""
    trace = TraceEmitter()
    graph = CapabilityGraph(trace=trace)
    manifest1 = ComponentManifest(
        component_id=ComponentId("Adapter1"),
        version="1.0.0",
        author="test-author",
        content_hash="sha256:abc123",
        provides=(
            CapabilityDeclaration(
                category=CapabilityCategory.MODEL_INFERENCE,
                name="text_generation",
                version="1.0.0",
            ),
        ),
        requires=(),
    )
    manifest2 = ComponentManifest(
        component_id=ComponentId("Adapter2"),
        version="1.0.0",
        author="test-author",
        content_hash="sha256:def456",
        provides=(
            CapabilityDeclaration(
                category=CapabilityCategory.TOOL,
                name="calculator",
                version="1.0.0",
            ),
        ),
        requires=(),
    )
    manifest3 = ComponentManifest(
        component_id=ComponentId("Adapter3"),
        version="1.0.0",
        author="test-author",
        content_hash="sha256:ghi789",
        provides=(
            CapabilityDeclaration(
                category=CapabilityCategory.MEMORY,
                name="relational",
                version="1.0.0",
            ),
        ),
        requires=(),
    )
    graph.register(manifest1)
    graph.register(manifest2)
    graph.register(manifest3)
    all_manifests = graph.list_all_components()
    assert len(all_manifests) == 3
    component_ids = {m.component_id for m in all_manifests}
    assert component_ids == {
        ComponentId("Adapter1"),
        ComponentId("Adapter2"),
        ComponentId("Adapter3"),
    }


def test_list_all_components_empty_when_nothing_registered() -> None:
    """Query a fresh graph with no registrations; returns empty tuple."""
    trace = TraceEmitter()
    graph = CapabilityGraph(trace=trace)
    all_manifests = graph.list_all_components()
    assert all_manifests == ()


def test_protocol_compliance() -> None:
    """Verify CapabilityGraph implements ICapabilityIndex via structural typing."""
    trace = TraceEmitter()
    graph = CapabilityGraph(trace=trace)
    # Protocol structural typing: isinstance returns True if the object
    # has all the required methods with matching signatures
    assert isinstance(graph, ICapabilityIndex)


def test_register_equal_priority_stable_sort() -> None:
    """Register two providers with equal priority; verify stable sort preserves registration order."""
    trace = TraceEmitter()
    graph = CapabilityGraph(trace=trace)
    manifest1 = ComponentManifest(
        component_id=ComponentId("FirstAdapter"),
        version="1.0.0",
        author="test-author",
        content_hash="sha256:abc123",
        provides=(
            CapabilityDeclaration(
                category=CapabilityCategory.MODEL_INFERENCE,
                name="text_generation",
                version="1.0.0",
                priority=5,
            ),
        ),
        requires=(),
    )
    manifest2 = ComponentManifest(
        component_id=ComponentId("SecondAdapter"),
        version="1.0.0",
        author="test-author",
        content_hash="sha256:def456",
        provides=(
            CapabilityDeclaration(
                category=CapabilityCategory.MODEL_INFERENCE,
                name="text_generation",
                version="1.0.0",
                priority=5,
            ),
        ),
        requires=(),
    )
    graph.register(manifest1)
    graph.register(manifest2)
    providers = graph.find_providers(CapabilityCategory.MODEL_INFERENCE, "text_generation")
    assert len(providers) == 2
    # Stable sort: FirstAdapter registered first, should appear first
    assert providers[0][0] == ComponentId("FirstAdapter")
    assert providers[1][0] == ComponentId("SecondAdapter")


def test_register_cleanup_old_capabilities_on_reregistration() -> None:
    """Verify that re-registering a component removes its old capabilities."""
    trace = TraceEmitter()
    graph = CapabilityGraph(trace=trace)
    
    # Initial registration with one capability
    manifest_v1 = ComponentManifest(
        component_id=ComponentId("TestAdapter"),
        version="1.0.0",
        author="test-author",
        content_hash="sha256:abc123",
        provides=(
            CapabilityDeclaration(
                category=CapabilityCategory.MODEL_INFERENCE,
                name="text_generation",
                version="1.0.0",
                priority=10,
            ),
        ),
        requires=(),
    )
    graph.register(manifest_v1)
    providers = graph.find_providers(CapabilityCategory.MODEL_INFERENCE, "text_generation")
    assert len(providers) == 1
    
    # Re-register with different capability
    manifest_v2 = ComponentManifest(
        component_id=ComponentId("TestAdapter"),
        version="2.0.0",
        author="test-author",
        content_hash="sha256:def456",
        provides=(
            CapabilityDeclaration(
                category=CapabilityCategory.TOOL,
                name="calculator",
                version="2.0.0",
                priority=10,
            ),
        ),
        requires=(),
    )
    graph.register(manifest_v2)
    
    # Old capability should be removed
    providers_old = graph.find_providers(CapabilityCategory.MODEL_INFERENCE, "text_generation")
    assert len(providers_old) == 0
    
    # New capability should be present
    providers_new = graph.find_providers(CapabilityCategory.TOOL, "calculator")
    assert len(providers_new) == 1
