from sovereignai.shared.capability_graph import CapabilityGraph


class TestCapabilityAPIContract:

    def test_capability_graph_register_signature(self):
        graph = CapabilityGraph(trace=None)
        assert hasattr(graph, 'register')
        assert callable(graph.register)

    def test_capability_graph_query_signature(self):
        graph = CapabilityGraph(trace=None)
        assert hasattr(graph, 'find_providers')
        assert callable(graph.find_providers)
