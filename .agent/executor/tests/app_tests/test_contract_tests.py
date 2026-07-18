from tests.contracts.test_capability_api_contract import TestCapabilityAPIContract


class TestContractTests:

    def test_capability_api_contract_tests_run(self):
        test_instance = TestCapabilityAPIContract()
        test_instance.test_capability_graph_register_signature()
        test_instance.test_capability_graph_query_signature()
