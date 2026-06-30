from sovereignai.conformance.base import BaseConformanceTest
from sovereignai.conformance.registry import register


@register('memory_storage')
class MemoryStorageConformanceTest(BaseConformanceTest):

    def test_component_has_required_interface(self, instance) -> None:
        assert hasattr(instance, 'store'), 'Memory backend must have store method'
        assert callable(instance.store), 'store must be callable'

    def test_memory_backend_has_retrieve_method(self, instance) -> None:
        assert hasattr(instance, 'retrieve'), 'Memory backend must have retrieve method'
        assert callable(instance.retrieve), 'retrieve must be callable'
