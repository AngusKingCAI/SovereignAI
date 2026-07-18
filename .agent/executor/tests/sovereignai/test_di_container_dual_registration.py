"""Tests for DIContainer dual-registration (protocol + concrete) (Plan 23 S10)."""

import pytest
from sovereignai.agent.protocols import GraphMemory
from sovereignai.shared.container import DIContainer


class MockGraphMemory:
    """Mock implementation of GraphMemory protocol."""

    def query(self, entity_id: str, depth: int = 2) -> list[dict]:
        return [{"entity": entity_id, "depth": depth}]


def test_protocol_key_registration():
    """Test that protocol class can be used as factory key (S10)."""
    container = DIContainer()
    mock_impl = MockGraphMemory()

    # Register using protocol as key
    container.register_singleton(GraphMemory, mock_impl)

    # Retrieve using protocol key
    retrieved = container.retrieve(GraphMemory)
    assert retrieved is mock_impl


def test_concrete_class_registration():
    """Test that concrete class can be used as factory key (S10)."""
    container = DIContainer()
    mock_impl = MockGraphMemory()

    # Register using concrete class as key
    container.register_singleton(MockGraphMemory, mock_impl)

    # Retrieve using concrete class key
    retrieved = container.retrieve(MockGraphMemory)
    assert retrieved is mock_impl


def test_dual_registration_protocol_and_concrete():
    """Test dual-registration pattern: protocol + concrete both work (DD-23.11.1)."""
    container = DIContainer()
    mock_impl = MockGraphMemory()

    # Register under both protocol and concrete
    container.register_singleton(GraphMemory, mock_impl)
    container.register_singleton(MockGraphMemory, mock_impl)

    # Both keys should work
    retrieved_protocol = container.retrieve(GraphMemory)
    retrieved_concrete = container.retrieve(MockGraphMemory)

    assert retrieved_protocol is mock_impl
    assert retrieved_concrete is mock_impl


def test_protocol_classes_are_hashable():
    """Test that protocol classes are hashable and work as dict keys (P23-E)."""
    # Protocol classes should be hashable
    hash(GraphMemory)  # Should not raise

    # Should work as dict keys
    test_dict = {GraphMemory: "test_value"}
    assert test_dict[GraphMemory] == "test_value"


def test_retrieve_protocol_not_registered_raises():
    """Test that retrieving unregistered protocol raises KeyError."""
    container = DIContainer()

    with pytest.raises(KeyError, match="No singleton or factory registered"):
        container.retrieve(GraphMemory)


def test_factory_registration_with_protocol():
    """Test that factory can be registered with protocol key."""
    container = DIContainer()

    # Register factory with protocol key
    container.register_factory(GraphMemory, lambda: MockGraphMemory())

    # Retrieve should call factory
    retrieved = container.retrieve(GraphMemory)
    assert isinstance(retrieved, MockGraphMemory)

    # Second retrieve should call factory again (not singleton for factories)
    retrieved2 = container.retrieve(GraphMemory)
    assert isinstance(retrieved2, MockGraphMemory)
    # Factories are called each time, so instances will be different


def test_mixed_protocol_and_concrete_different_instances():
    """Test that protocol and concrete can have different instances if desired."""
    container = DIContainer()
    impl1 = MockGraphMemory()
    impl2 = MockGraphMemory()

    # Register different instances under different keys
    container.register_singleton(GraphMemory, impl1)
    container.register_singleton(MockGraphMemory, impl2)

    # Should return different instances
    retrieved_protocol = container.retrieve(GraphMemory)
    retrieved_concrete = container.retrieve(MockGraphMemory)

    assert retrieved_protocol is impl1
    assert retrieved_concrete is impl2
    assert retrieved_protocol is not retrieved_concrete
