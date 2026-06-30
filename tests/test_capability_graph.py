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
    trace = TraceEmitter()
    graph = CapabilityGraph(trace=trace)
    manifest = ComponentManifest(component_id=ComponentId('TestAdapter'), version='1.0.0', author='test-author', content_hash='sha256:abc123', provides=(CapabilityDeclaration(category=CapabilityCategory.MODEL_INFERENCE, name='text_generation', version='1.0.0', priority=10),), requires=())
    graph.register(manifest)
    providers = graph.find_providers(CapabilityCategory.MODEL_INFERENCE, 'text_generation')
    assert len(providers) == 1
    assert providers[0][0] == ComponentId('TestAdapter')
    assert providers[0][1].name == 'text_generation'

def test_register_multiple_providers_sorted_by_priority() -> None:
    trace = TraceEmitter()
    graph = CapabilityGraph(trace=trace)
    manifest1 = ComponentManifest(component_id=ComponentId('LowPriorityAdapter'), version='1.0.0', author='test-author', content_hash='sha256:abc123', provides=(CapabilityDeclaration(category=CapabilityCategory.MODEL_INFERENCE, name='text_generation', version='1.0.0', priority=5),), requires=())
    manifest2 = ComponentManifest(component_id=ComponentId('HighPriorityAdapter'), version='1.0.0', author='test-author', content_hash='sha256:def456', provides=(CapabilityDeclaration(category=CapabilityCategory.MODEL_INFERENCE, name='text_generation', version='1.0.0', priority=10),), requires=())
    graph.register(manifest1)
    graph.register(manifest2)
    providers = graph.find_providers(CapabilityCategory.MODEL_INFERENCE, 'text_generation')
    assert len(providers) == 2
    assert providers[0][0] == ComponentId('HighPriorityAdapter')
    assert providers[0][1].priority == 10
    assert providers[1][0] == ComponentId('LowPriorityAdapter')
    assert providers[1][1].priority == 5

def test_find_providers_empty_when_no_match() -> None:
    trace = TraceEmitter()
    graph = CapabilityGraph(trace=trace)
    providers = graph.find_providers(CapabilityCategory.TOOL, 'websearch')
    assert providers == ()

def test_list_all_components_returns_all_manifests() -> None:
    trace = TraceEmitter()
    graph = CapabilityGraph(trace=trace)
    manifest1 = ComponentManifest(component_id=ComponentId('Adapter1'), version='1.0.0', author='test-author', content_hash='sha256:abc123', provides=(CapabilityDeclaration(category=CapabilityCategory.MODEL_INFERENCE, name='text_generation', version='1.0.0'),), requires=())
    manifest2 = ComponentManifest(component_id=ComponentId('Adapter2'), version='1.0.0', author='test-author', content_hash='sha256:def456', provides=(CapabilityDeclaration(category=CapabilityCategory.TOOL, name='calculator', version='1.0.0'),), requires=())
    manifest3 = ComponentManifest(component_id=ComponentId('Adapter3'), version='1.0.0', author='test-author', content_hash='sha256:ghi789', provides=(CapabilityDeclaration(category=CapabilityCategory.MEMORY, name='relational', version='1.0.0'),), requires=())
    graph.register(manifest1)
    graph.register(manifest2)
    graph.register(manifest3)
    all_manifests = graph.list_all_components()
    assert len(all_manifests) == 3
    component_ids = {m.component_id for m in all_manifests}
    assert component_ids == {ComponentId('Adapter1'), ComponentId('Adapter2'), ComponentId('Adapter3')}

def test_list_all_components_empty_when_nothing_registered() -> None:
    trace = TraceEmitter()
    graph = CapabilityGraph(trace=trace)
    all_manifests = graph.list_all_components()
    assert all_manifests == ()

def test_protocol_compliance() -> None:
    trace = TraceEmitter()
    graph = CapabilityGraph(trace=trace)
    assert isinstance(graph, ICapabilityIndex)

def test_register_equal_priority_stable_sort() -> None:
    trace = TraceEmitter()
    graph = CapabilityGraph(trace=trace)
    manifest1 = ComponentManifest(component_id=ComponentId('FirstAdapter'), version='1.0.0', author='test-author', content_hash='sha256:abc123', provides=(CapabilityDeclaration(category=CapabilityCategory.MODEL_INFERENCE, name='text_generation', version='1.0.0', priority=5),), requires=())
    manifest2 = ComponentManifest(component_id=ComponentId('SecondAdapter'), version='1.0.0', author='test-author', content_hash='sha256:def456', provides=(CapabilityDeclaration(category=CapabilityCategory.MODEL_INFERENCE, name='text_generation', version='1.0.0', priority=5),), requires=())
    graph.register(manifest1)
    graph.register(manifest2)
    providers = graph.find_providers(CapabilityCategory.MODEL_INFERENCE, 'text_generation')
    assert len(providers) == 2
    assert providers[0][0] == ComponentId('FirstAdapter')
    assert providers[1][0] == ComponentId('SecondAdapter')

def test_register_cleanup_old_capabilities_on_reregistration() -> None:
    trace = TraceEmitter()
    graph = CapabilityGraph(trace=trace)
    manifest_v1 = ComponentManifest(component_id=ComponentId('TestAdapter'), version='1.0.0', author='test-author', content_hash='sha256:abc123', provides=(CapabilityDeclaration(category=CapabilityCategory.MODEL_INFERENCE, name='text_generation', version='1.0.0', priority=10),), requires=())
    graph.register(manifest_v1)
    providers = graph.find_providers(CapabilityCategory.MODEL_INFERENCE, 'text_generation')
    assert len(providers) == 1
    manifest_v2 = ComponentManifest(component_id=ComponentId('TestAdapter'), version='2.0.0', author='test-author', content_hash='sha256:def456', provides=(CapabilityDeclaration(category=CapabilityCategory.TOOL, name='calculator', version='2.0.0', priority=10),), requires=())
    graph.register(manifest_v2)
    providers_old = graph.find_providers(CapabilityCategory.MODEL_INFERENCE, 'text_generation')
    assert len(providers_old) == 0
    providers_new = graph.find_providers(CapabilityCategory.TOOL, 'calculator')
    assert len(providers_new) == 1
