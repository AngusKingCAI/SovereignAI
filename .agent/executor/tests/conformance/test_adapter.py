from sovereignai.conformance.base import BaseConformanceTest
from sovereignai.conformance.registry import register


@register('adapter')
class AdapterConformanceTest(BaseConformanceTest):

    def test_component_has_required_interface(self, instance) -> None:
        assert hasattr(instance, 'health_check'), 'Adapter must have health_check method'
        assert callable(instance.health_check), 'health_check must be callable'

    def test_adapter_has_manifest(self, instance) -> None:
        assert hasattr(instance, 'manifest'), 'Adapter must have manifest attribute'
