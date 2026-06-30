class TestPropertyTests:

    def test_property_tests_discovered(self):
        from tests.property import test_state_machine_properties
        assert test_state_machine_properties is not None
