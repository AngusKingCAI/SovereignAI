"""Test that disabled plugins are removed from both graph and container."""

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
    """Test that disabled plugins are removed from the capability graph."""
    mock_trace = MagicMock()
    graph = CapabilityGraph(trace=mock_trace)

    # Register two incompatible plugins
    plugin1 = ComponentManifest(
        component_id=ComponentId("plugin1"),
        version="1.0.0",
        author="test",
        content_hash="hash1",
        provides=(
            CapabilityDeclaration(
                category=CapabilityCategory.TOOL,
                name="websearch",
                version="1.0.0",
                priority=0,
            ),
        ),
        requires=(),
        core=False,
        _source_path="/external/path/plugin1/manifest.toml",
    )

    plugin2 = ComponentManifest(
        component_id=ComponentId("plugin2"),
        version="2.0.0",
        author="test",
        content_hash="hash2",
        provides=(
            CapabilityDeclaration(
                category=CapabilityCategory.TOOL,
                name="websearch",
                version="2.0.0",
                priority=0,
            ),
        ),
        requires=(),
        core=False,
        _source_path="/external/path/plugin2/manifest.toml",
    )

    graph.register(plugin1)
    graph.register(plugin2)

    # Verify both are registered
    assert len(graph.list_all_components()) == 2

    # Remove one
    graph.remove(ComponentId("plugin1"))

    # Verify only one remains
    assert len(graph.list_all_components()) == 1
    remaining = graph.list_all_components()[0]
    assert remaining.component_id == ComponentId("plugin2")


def test_container_remove_unsubscribes_events() -> None:
    """Test that container.remove() unsubscribes event handlers."""
    mock_trace = MagicMock()
    mock_bus = MagicMock()

    container = DIContainer(event_bus=mock_bus, trace=mock_trace)

    # Register a mock component
    class MockComponent:
        component_id = "test_component"

    instance = MockComponent()
    container.register_singleton(MockComponent, instance)

    # Remove it
    container.remove(MockComponent)

    # Verify unsubscribe_all was called
    mock_bus.unsubscribe_all.assert_called_once_with(subscriber_id="test_component")

    # Verify trace was emitted
    mock_trace.emit.assert_called()
    call_args = mock_trace.emit.call_args
    assert call_args[1]["component"] == "container"
    assert call_args[1]["level"] == TraceLevel.WARN


def test_container_remove_with_id_attribute() -> None:
    """Test container.remove() with component having component_id attribute."""
    mock_trace = MagicMock()
    mock_bus = MagicMock()

    container = DIContainer(event_bus=mock_bus, trace=mock_trace)

    class MockComponent:
        component_id = "test_component"

    instance = MockComponent()
    container.register_singleton(MockComponent, instance)
    container.remove(MockComponent)

    mock_bus.unsubscribe_all.assert_called_once_with(subscriber_id="test_component")


def test_container_remove_with_id_underscore_attribute() -> None:
    """Test container.remove() with component having _component_id attribute."""
    mock_trace = MagicMock()
    mock_bus = MagicMock()

    container = DIContainer(event_bus=mock_bus, trace=mock_trace)

    class MockComponent:
        _component_id = "test_component"

    instance = MockComponent()
    container.register_singleton(MockComponent, instance)
    container.remove(MockComponent)

    mock_bus.unsubscribe_all.assert_called_once_with(subscriber_id="test_component")


def test_container_remove_without_id_attribute() -> None:
    """Test container.remove() with component having no component_id (uses id())."""
    mock_trace = MagicMock()
    mock_bus = MagicMock()

    container = DIContainer(event_bus=mock_bus, trace=mock_trace)

    class MockComponent:
        pass

    instance = MockComponent()
    container.register_singleton(MockComponent, instance)
    container.remove(MockComponent)

    # Should use id(instance) as subscriber_id
    mock_bus.unsubscribe_all.assert_called_once()
    call_args = mock_bus.unsubscribe_all.call_args
    assert call_args[1]["subscriber_id"] == id(instance)


def test_container_remove_nonexistent_no_error() -> None:
    """Test that removing a non-existent component doesn't raise an error."""
    mock_trace = MagicMock()
    mock_bus = MagicMock()

    container = DIContainer(event_bus=mock_bus, trace=mock_trace)

    class MockComponent:
        pass

    # Should not raise
    container.remove(MockComponent)

    # unsubscribe should not be called since instance was None
    mock_bus.unsubscribe_all.assert_not_called()
