from unittest.mock import MagicMock

from sovereignai.shared.capability_graph import CapabilityGraph
from sovereignai.shared.container import DIContainer
from sovereignai.shared.types import (
    CapabilityCategory,
    CapabilityDeclaration,
    ComponentId,
    ComponentManifest,
    TraceLevel,
)


def test_disabled_plugin_removed_from_graph() -> None:
    mock_trace = MagicMock()
    graph = CapabilityGraph(trace=mock_trace)
    plugin1 = ComponentManifest(component_id=ComponentId('plugin1'), version='1.0.0', author='test', content_hash='hash1', provides=(CapabilityDeclaration(category=CapabilityCategory.TOOL, name='websearch', version='1.0.0', priority=0),), requires=(), core=False, _source_path='/external/path/plugin1/manifest.toml')
    plugin2 = ComponentManifest(component_id=ComponentId('plugin2'), version='2.0.0', author='test', content_hash='hash2', provides=(CapabilityDeclaration(category=CapabilityCategory.TOOL, name='websearch', version='2.0.0', priority=0),), requires=(), core=False, _source_path='/external/path/plugin2/manifest.toml')
    graph.register(plugin1)
    graph.register(plugin2)
    assert len(graph.list_all_components()) == 2
    graph.remove(ComponentId('plugin1'))
    assert len(graph.list_all_components()) == 1
    remaining = graph.list_all_components()[0]
    assert remaining.component_id == ComponentId('plugin2')

def test_container_remove_unsubscribes_events() -> None:
    mock_trace = MagicMock()
    mock_bus = MagicMock()
    container = DIContainer(event_bus=mock_bus, trace=mock_trace)

    class MockComponent:
        component_id = 'test_component'
    instance = MockComponent()
    container.register_singleton(MockComponent, instance)
    container.remove(MockComponent)
    mock_bus.unsubscribe_all.assert_called_once_with(subscriber_id='test_component')
    mock_trace.emit.assert_called()
    call_args = mock_trace.emit.call_args
    assert call_args[1]['component'] == 'container'
    assert call_args[1]['level'] == TraceLevel.WARN

def test_container_remove_with_id_attribute() -> None:
    mock_trace = MagicMock()
    mock_bus = MagicMock()
    container = DIContainer(event_bus=mock_bus, trace=mock_trace)

    class MockComponent:
        component_id = 'test_component'
    instance = MockComponent()
    container.register_singleton(MockComponent, instance)
    container.remove(MockComponent)
    mock_bus.unsubscribe_all.assert_called_once_with(subscriber_id='test_component')

def test_container_remove_with_id_underscore_attribute() -> None:
    mock_trace = MagicMock()
    mock_bus = MagicMock()
    container = DIContainer(event_bus=mock_bus, trace=mock_trace)

    class MockComponent:
        _component_id = 'test_component'
    instance = MockComponent()
    container.register_singleton(MockComponent, instance)
    container.remove(MockComponent)
    mock_bus.unsubscribe_all.assert_called_once_with(subscriber_id='test_component')

def test_container_remove_without_id_attribute() -> None:
    mock_trace = MagicMock()
    mock_bus = MagicMock()
    container = DIContainer(event_bus=mock_bus, trace=mock_trace)

    class MockComponent:
        pass
    instance = MockComponent()
    container.register_singleton(MockComponent, instance)
    container.remove(MockComponent)
    mock_bus.unsubscribe_all.assert_called_once()
    call_args = mock_bus.unsubscribe_all.call_args
    assert call_args[1]['subscriber_id'] == id(instance)

def test_container_remove_nonexistent_no_error() -> None:
    mock_trace = MagicMock()
    mock_bus = MagicMock()
    container = DIContainer(event_bus=mock_bus, trace=mock_trace)

    class MockComponent:
        pass
    container.remove(MockComponent)
    mock_bus.unsubscribe_all.assert_not_called()
