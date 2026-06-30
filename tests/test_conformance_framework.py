from unittest.mock import Mock

from sovereignai.conformance.base import BaseConformanceTest
from sovereignai.conformance.registry import get_conformance_tests_for_class, register
from sovereignai.conformance.runner import ConformanceRunner


@register('test_capability')
class MockConformanceTest(BaseConformanceTest):

    def test_component_has_required_interface(self, instance) -> None:
        assert hasattr(instance, 'test_method')

class TestConformanceFramework:

    def test_conforming_mock_passes(self):
        trace = Mock()
        runner = ConformanceRunner(trace)
        mock_instance = Mock()
        mock_instance.test_method = Mock()
        passed = runner.check(component_id='test.component', content_hash='abc123', capability_class='test_capability', instance=mock_instance, is_first_party=True)
        assert passed is True

    def test_non_conforming_fails(self):
        trace = Mock()
        runner = ConformanceRunner(trace)
        mock_instance = Mock()
        del mock_instance.test_method
        passed = runner.check(component_id='test.component', content_hash='abc123', capability_class='test_capability', instance=mock_instance, is_first_party=True)
        assert passed is False

    def test_fail_open_when_no_tests_for_capability_class(self):
        trace = Mock()
        runner = ConformanceRunner(trace)
        mock_instance = Mock()
        passed = runner.check(component_id='test.component', content_hash='abc123', capability_class='nonexistent_capability', instance=mock_instance, is_first_party=False)
        assert passed is True

    def test_fail_closed_when_no_tests_for_first_party(self):
        trace = Mock()
        runner = ConformanceRunner(trace)
        mock_instance = Mock()
        passed = runner.check(component_id='test.component', content_hash='abc123', capability_class='nonexistent_capability', instance=mock_instance, is_first_party=True)
        assert passed is False

    def test_caching_works(self):
        trace = Mock()
        runner = ConformanceRunner(trace)
        mock_instance = Mock()
        mock_instance.test_method = Mock()
        passed1 = runner.check(component_id='test.component', content_hash='abc123', capability_class='test_capability', instance=mock_instance, is_first_party=True)
        assert passed1 is True
        passed2 = runner.check(component_id='test.component', content_hash='abc123', capability_class='test_capability', instance=mock_instance, is_first_party=True)
        assert passed2 is True

    def test_entry_point_discovery(self):
        tests = get_conformance_tests_for_class('test_capability')
        assert len(tests) > 0
        assert MockConformanceTest in tests
