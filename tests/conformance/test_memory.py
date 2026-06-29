"""Conformance tests for memory backend components."""
from sovereignai.conformance.base import BaseConformanceTest
from sovereignai.conformance.registry import register


@register("memory_storage")
class MemoryStorageConformanceTest(BaseConformanceTest):
    """Verify memory storage backends implement the required interface."""

    def test_component_has_required_interface(self, instance) -> None:
        """Verify the memory backend has a store method."""
        assert hasattr(instance, "store"), "Memory backend must have store method"
        assert callable(instance.store), "store must be callable"

    def test_memory_backend_has_retrieve_method(self, instance) -> None:
        """Verify the memory backend has a retrieve method."""
        assert hasattr(instance, "retrieve"), "Memory backend must have retrieve method"
        assert callable(instance.retrieve), "retrieve must be callable"
