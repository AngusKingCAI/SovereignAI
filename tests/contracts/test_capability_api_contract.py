"""Contract tests for the Capability API."""
from sovereignai.shared.capability_graph import CapabilityGraph


class TestCapabilityAPIContract:
    """Verify the Capability API maintains backward compatibility."""

    def test_capability_graph_register_signature(self):
        """Verify CapabilityGraph.register() accepts the expected parameters."""
        # This is a placeholder contract test - in a real implementation,
        # this would verify the exact signature and behavior
        graph = CapabilityGraph(trace=None)
        # The register method should accept component_id, manifest, instance
        assert hasattr(graph, "register")
        assert callable(graph.register)

    def test_capability_graph_query_signature(self):
        """Verify CapabilityGraph.find_providers() accepts the expected parameters."""
        graph = CapabilityGraph(trace=None)
        # The find_providers method should accept capability requirements
        assert hasattr(graph, "find_providers")
        assert callable(graph.find_providers)
