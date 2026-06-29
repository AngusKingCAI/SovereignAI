"""Test the conformance framework itself."""
from unittest.mock import Mock

from sovereignai.conformance.base import BaseConformanceTest
from sovereignai.conformance.registry import get_conformance_tests_for_class, register
from sovereignai.conformance.runner import ConformanceRunner


@register("test_capability")
class MockConformanceTest(BaseConformanceTest):
    """Mock conformance test for testing the framework."""

    def test_component_has_required_interface(self, instance) -> None:
        """Verify the component has a required interface."""
        assert hasattr(instance, "test_method")


class TestConformanceFramework:
    """Test the conformance framework behavior."""

    def test_conforming_mock_passes(self):
        """Verify a conforming mock component passes conformance tests."""
        trace = Mock()
        runner = ConformanceRunner(trace)

        mock_instance = Mock()
        mock_instance.test_method = Mock()

        passed = runner.check(
            component_id="test.component",
            content_hash="abc123",
            capability_class="test_capability",
            instance=mock_instance,
            is_first_party=True,
        )
        assert passed is True

    def test_non_conforming_fails(self):
        """Verify a non-conforming component fails conformance tests."""
        trace = Mock()
        runner = ConformanceRunner(trace)

        mock_instance = Mock()
        # Missing test_method
        del mock_instance.test_method

        passed = runner.check(
            component_id="test.component",
            content_hash="abc123",
            capability_class="test_capability",
            instance=mock_instance,
            is_first_party=True,
        )
        assert passed is False

    def test_fail_open_when_no_tests_for_capability_class(self):
        """Verify fail-open when no tests for capability class (third-party)."""
        trace = Mock()
        runner = ConformanceRunner(trace)

        mock_instance = Mock()

        passed = runner.check(
            component_id="test.component",
            content_hash="abc123",
            capability_class="nonexistent_capability",
            instance=mock_instance,
            is_first_party=False,
        )
        assert passed is True  # fail-open for third-party

    def test_fail_closed_when_no_tests_for_first_party(self):
        """Verify fail-closed for first-party when no tests."""
        trace = Mock()
        runner = ConformanceRunner(trace)

        mock_instance = Mock()

        passed = runner.check(
            component_id="test.component",
            content_hash="abc123",
            capability_class="nonexistent_capability",
            instance=mock_instance,
            is_first_party=True,
        )
        assert passed is False  # fail-closed for first-party

    def test_caching_works(self):
        """Verify conformance results are cached per (component_id, content_hash)."""
        trace = Mock()
        runner = ConformanceRunner(trace)

        mock_instance = Mock()
        mock_instance.test_method = Mock()

        # First call - should run tests
        passed1 = runner.check(
            component_id="test.component",
            content_hash="abc123",
            capability_class="test_capability",
            instance=mock_instance,
            is_first_party=True,
        )
        assert passed1 is True

        # Second call with same key - should use cache
        passed2 = runner.check(
            component_id="test.component",
            content_hash="abc123",
            capability_class="test_capability",
            instance=mock_instance,
            is_first_party=True,
        )
        assert passed2 is True

    def test_entry_point_discovery(self):
        """Verify entry-point discovery returns registered tests."""
        tests = get_conformance_tests_for_class("test_capability")
        assert len(tests) > 0
        assert MockConformanceTest in tests
