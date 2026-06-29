"""Test property-based tests."""


class TestPropertyTests:
    """Verify property-based tests run correctly."""

    def test_property_tests_discovered(self):
        """Verify property tests are discoverable by pytest."""
        # This test just verifies the module exists and can be imported
        from tests.property import test_state_machine_properties
        assert test_state_machine_properties is not None
