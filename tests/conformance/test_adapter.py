"""Conformance tests for adapter components."""
from sovereignai.conformance.base import BaseConformanceTest
from sovereignai.conformance.registry import register


@register("adapter")
class AdapterConformanceTest(BaseConformanceTest):
    """Verify adapter components implement the required interface."""

    def test_component_has_required_interface(self, instance) -> None:
        """Verify the adapter has a health_check method."""
        assert hasattr(instance, "health_check"), "Adapter must have health_check method"
        assert callable(instance.health_check), "health_check must be callable"

    def test_adapter_has_manifest(self, instance) -> None:
        """Verify the adapter has a manifest attribute."""
        assert hasattr(instance, "manifest"), "Adapter must have manifest attribute"
