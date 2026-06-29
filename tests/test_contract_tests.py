"""Test contract tests."""
from tests.contracts.test_capability_api_contract import TestCapabilityAPIContract


class TestContractTests:
    """Verify contract tests run correctly."""

    def test_capability_api_contract_tests_run(self):
        """Verify contract tests for Capability API run."""
        test_instance = TestCapabilityAPIContract()
        test_instance.test_capability_graph_register_signature()
        test_instance.test_capability_graph_query_signature()
