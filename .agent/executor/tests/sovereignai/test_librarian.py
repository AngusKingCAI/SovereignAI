from __future__ import annotations

import pytest
from sovereignai.librarian.librarian import Librarian
from sovereignai.shared.capability_graph import CapabilityGraph
from sovereignai.shared.trace_emitter import TraceEmitter
from sovereignai.shared.types import (
    CapabilityCategory,
    CapabilityDeclaration,
    ComponentId,
    ComponentManifest,
    NoActiveProviderError,
)


def test_librarian_constructor_within_arg_limit() -> None:
    trace = TraceEmitter()
    graph = CapabilityGraph(trace=trace)
    librarian = Librarian(capability_graph=graph, trace=trace)
    assert librarian is not None

def test_librarian_store_no_provider_raises_error() -> None:
    trace = TraceEmitter()
    graph = CapabilityGraph(trace=trace)
    librarian = Librarian(capability_graph=graph, trace=trace)
    with pytest.raises(NoActiveProviderError):
        librarian.store(  # noqa: E501
            memory_type='episodic',
            data={'component': 'test', 'event_type': 'test', 'data': '{}'}
        )

def test_librarian_query_no_provider_raises_error() -> None:
    trace = TraceEmitter()
    graph = CapabilityGraph(trace=trace)
    librarian = Librarian(capability_graph=graph, trace=trace)
    with pytest.raises(NoActiveProviderError):
        librarian.query(memory_type='episodic', query={})

def test_librarian_delete_no_provider_raises_error() -> None:
    trace = TraceEmitter()
    graph = CapabilityGraph(trace=trace)
    librarian = Librarian(capability_graph=graph, trace=trace)
    with pytest.raises(NoActiveProviderError):
        librarian.delete(memory_type='episodic', record_id='test-id')

def test_librarian_route_finds_providers() -> None:
    trace = TraceEmitter()
    graph = CapabilityGraph(trace=trace)
    librarian = Librarian(capability_graph=graph, trace=trace)
    manifest = ComponentManifest(  # noqa: E501
        component_id=ComponentId('episodic_memory'),
        version='0.1.0',
        provides=(
            CapabilityDeclaration(
                category=CapabilityCategory.MEMORY,
                name='episodic',
                version='1.0.0',
                priority=100
            ),
        ),
        requires=(),
        author='system',
        content_hash='sha256:placeholder'
    )
    graph.register(manifest)
    providers = librarian._route('episodic', 'memory_storage')
    assert len(providers) == 1
    assert providers[0] == ComponentId('episodic_memory')

def test_librarian_merge_results_episodic_dedupes_by_id() -> None:
    trace = TraceEmitter()
    graph = CapabilityGraph(trace=trace)
    librarian = Librarian(capability_graph=graph, trace=trace)
    results = [  # noqa: E501
        {'id': '1', 'timestamp': 2.0},
        {'id': '2', 'timestamp': 1.0},
        {'id': '1', 'timestamp': 3.0}
    ]
    merged = librarian._merge_results('episodic', results)
    assert len(merged) == 2
    assert merged[0]['id'] == '2'
    assert merged[1]['id'] == '1'

def test_librarian_merge_results_working_first_backend_wins() -> None:
    trace = TraceEmitter()
    graph = CapabilityGraph(trace=trace)
    librarian = Librarian(capability_graph=graph, trace=trace)
    results = [{'id': '1', 'key': 'a'}, {'id': '2', 'key': 'b'}]
    merged = librarian._merge_results('working', results)
    assert len(merged) == 1
    assert merged == [results[0]]
